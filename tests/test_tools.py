import hashlib
import json
from pathlib import Path
import plistlib
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/mudforge-toolbox"
sys.path.insert(0, str(PLUGIN / "scripts"))
import activate_agents
import build_plugin
import diagnose_macos
import inspect_artifact
import validate_plugin


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def archive(self, entries, suffix=".mfw", compression=zipfile.ZIP_STORED):
        path = self.root / ("fixture" + suffix)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(path, "w", compression=compression) as archive:
                for name, data in entries:
                    archive.writestr(name, data)
        return path

    def test_world_envelope_no_mutation_or_saved_value_disclosure(self):
        path = self.archive([("world.json", '{"password":"SECRET","host":"PRIVATE"}'),
                             ("private-person.lua", 'error("DO NOT EXECUTE")')])
        before = path.read_bytes()
        result = inspect_artifact.inspect(path)
        self.assertEqual(result["status"], "envelope_checked")
        self.assertEqual(result["inventory"]["files"], 2)
        self.assertEqual(result["sha256"], hashlib.sha256(before).hexdigest())
        for secret in ("SECRET", "PRIVATE", "private-person", "DO NOT EXECUTE"):
            self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(before, path.read_bytes())
        self.assertEqual(list(self.root.iterdir()), [path])

    def test_package_and_forbidden_world(self):
        path = self.archive([("package.json", '{"name":"demo","version":"1.0.0"}')], ".mfp")
        self.assertEqual(inspect_artifact.inspect(path)["status"], "envelope_checked")
        for name in ("world.json", "nested/WORLD.JSON"):
            path = self.archive([("package.json", '{"name":"demo"}'), (name, '{}')], ".mfp")
            self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")

    def test_legacy_and_unknown(self):
        path = self.root / "world.mfw.json"
        path.write_text('{"private-field":"PRIVATE"}')
        self.assertEqual(inspect_artifact.inspect(path)["status"], "unsupported")
        path.write_text('[]')
        self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")
        path = self.archive([("unknown.json", '{}')])
        self.assertEqual(inspect_artifact.inspect(path)["status"], "unsupported")
        unknown = self.root / "unrecognized.bin"
        unknown.write_bytes(b"anything")
        self.assertEqual(inspect_artifact.inspect(unknown)["status"], "unsupported")

    def test_malformed_json_zip_and_empty_controls(self):
        for value in ('{', '[]', '{}', '{"a":1,"a":2}', '{"value":NaN}', '['*2000):
            with self.subTest(value=value[:30]):
                path = self.archive([("world.json", value)])
                self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")
        path.write_bytes(b"not a zip")
        self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")

    def test_unsafe_paths(self):
        for name in ("../secret", "/secret", "C:/secret", "a\\b", "a/../b", "a//b", "a/./b", "a\x00b"):
            with self.subTest(name=name):
                if "\x00" in name:
                    info = zipfile.ZipInfo("safe")
                    info.orig_filename = name
                    with self.assertRaises(inspect_artifact.InspectionError):
                        inspect_artifact.check_member(info)
                    continue
                self.assertEqual(inspect_artifact.inspect(self.archive([(name, "x")]))["status"], "rejected")

    def test_duplicates_and_path_collisions(self):
        for entries in ([('a', 'x'), ('a', 'y')], [('a', 'x'), ('A', 'y')],
                        [('a', 'x'), ('a/b', 'y')], [('a/', ''), ('a', 'x')]):
            self.assertEqual(inspect_artifact.inspect(self.archive(entries))["status"], "rejected")

    def test_links(self):
        info = zipfile.ZipInfo("link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.assertEqual(inspect_artifact.inspect(self.archive([(info, '/private')]))["status"], "rejected")
        path = self.root / "source.mfw"
        path.symlink_to(self.root / "fixture.mfw")
        self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")

    def test_parent_path_alias_is_safe_for_readonly_inspection(self):
        path = self.archive([('world.json', '{"name":"demo"}')])
        alias = self.root/'alias'
        alias.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(inspect_artifact.inspect(alias/path.name)['status'], 'envelope_checked')

    def test_limits(self):
        path = self.archive([('world.json', '{"name":"demo"}'), ('a.lua', 'a'*100)])
        for constant, value in (("MAX_ARCHIVE", 10), ("MAX_MEMBER", 10), ("MAX_TOTAL", 20), ("MAX_MEMBERS", 1)):
            with self.subTest(constant=constant), patch.object(inspect_artifact, constant, value):
                self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")
        path = self.archive([('a', 'a'*100000)], compression=zipfile.ZIP_DEFLATED)
        self.assertEqual(inspect_artifact.inspect(path)["status"], "rejected")

    def test_bad_crc_and_private_error_names(self):
        path = self.archive([('world.json', '{"name":"demo"}'), ('PRIVATE.lua', 'SECRET')])
        data = bytearray(path.read_bytes())
        data[data.index(b'SECRET')] ^= 1
        path.write_bytes(data)
        result = inspect_artifact.inspect(path)
        self.assertEqual(result["status"], "rejected")
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn('SECRET', json.dumps(result))

    def test_inspection_cli_exit_codes(self):
        for suffix, content, expected in ((".mfw.json", '{}', 2), (".mfw", 'bad', 1)):
            path = self.root / ('fixture' + suffix)
            path.write_text(content)
            result = subprocess.run([sys.executable, str(PLUGIN/'scripts/inspect_artifact.py'), str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, expected)
            json.loads(result.stdout)


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name).resolve()

    def test_dry_run_then_idempotent_activation(self):
        plan = activate_agents.activate(self.project, True)
        self.assertEqual(len(plan['agents']), 3)
        self.assertFalse((self.project/'.codex').exists())
        activate_agents.activate(self.project)
        result = activate_agents.activate(self.project)
        self.assertTrue(all(a['action'] == 'unchanged' for a in result['agents']))
        self.assertFalse((self.project/'.codex/config.toml').exists())

    def test_conflict_preflight_preserves_unrelated_files(self):
        destination = self.project/'.codex/agents'
        destination.mkdir(parents=True)
        (destination/'mudforge-qa.toml').write_text('user content')
        (destination/'unrelated.toml').write_text('other')
        before = {p.name:p.read_bytes() for p in destination.iterdir()}
        with self.assertRaises(ValueError):
            activate_agents.activate(self.project)
        self.assertEqual(before, {p.name:p.read_bytes() for p in destination.iterdir()})

    def test_refuses_symlink_destination(self):
        (self.project/'.codex').symlink_to(self.project, target_is_directory=True)
        with self.assertRaises(ValueError):
            activate_agents.activate(self.project)

    def test_failed_activation_removes_its_new_files(self):
        real_open = Path.open
        def fail_second(path, mode='r', *args, **kwargs):
            if mode == 'xb' and path.name == 'mudforge-diagnostics.toml':
                raise OSError('simulated write failure')
            return real_open(path, mode, *args, **kwargs)
        with patch.object(Path, 'open', fail_second), self.assertRaises(ValueError):
            activate_agents.activate(self.project)
        self.assertFalse((self.project/'.codex').exists())


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def test_validation(self):
        self.assertEqual(validate_plugin.validate(PLUGIN), [])

    def test_build_reproducible_relocatable_and_complete(self):
        first, second = self.root/'one.zip', self.root/'two.zip'
        build_plugin.build(first)
        build_plugin.build(second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(hashlib.sha256(first.read_bytes()).hexdigest(), first.with_suffix('.zip.sha256').read_text().split()[0])
        extracted = self.root/'relocated/mudforge-toolbox'
        with zipfile.ZipFile(first) as archive:
            self.assertIn('.codex-plugin/plugin.json', archive.namelist())
            self.assertEqual(sum(n.endswith('/SKILL.md') for n in archive.namelist()), 8)
            self.assertEqual(sum(n.startswith('agents/') for n in archive.namelist()), 3)
            self.assertFalse(any(n.startswith(('research/', 'tests/')) for n in archive.namelist()))
            archive.extractall(extracted)  # Only our generated, trusted archive.
        run = subprocess.run([sys.executable, str(extracted/'scripts/validate_plugin.py')], cwd=self.root,
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        project = self.root/'new-project'
        project.mkdir()
        run = subprocess.run([sys.executable, str(extracted/'scripts/activate_agents.py'), '--project', str(project)],
                             cwd=self.root, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        self.assertEqual(len(list((project/'.codex/agents').glob('*.toml'))), 3)
        run = subprocess.run([sys.executable, str(extracted/'scripts/diagnose_macos.py'), '--app', str(self.root/'absent.app')],
                             cwd=self.root, capture_output=True, text=True)
        self.assertEqual(json.loads(run.stdout)['installations'], [])

    def test_metadata_filters_and_symlink_rejection(self):
        copied = self.root/'mudforge-toolbox'
        shutil.copytree(PLUGIN, copied, ignore=shutil.ignore_patterns('__pycache__'))
        for p in (copied/'.DS_Store', copied/'skills/.DS_Store', copied/'scripts/cache.pyc'):
            p.write_text('finder metadata')
        output = self.root/'clean.zip'
        build_plugin.build(output, copied)
        with zipfile.ZipFile(output) as archive:
            self.assertFalse(any('.DS_Store' in n or n.endswith('.pyc') for n in archive.namelist()))
        (copied/'scripts/private.py').symlink_to(PLUGIN/'scripts/activate_agents.py')
        with self.assertRaises(ValueError):
            build_plugin.build(output, copied)

    def test_missing_reference_fails(self):
        copied = self.root/'mudforge-toolbox'
        shutil.copytree(PLUGIN, copied, ignore=shutil.ignore_patterns('__pycache__'))
        (copied/'references/compatibility.md').unlink()
        self.assertTrue(any('missing or escaping reference' in e for e in validate_plugin.validate(copied)))

    def test_diagnosis_reads_only_metadata(self):
        app = self.root/'MudForge.app'
        (app/'Contents/MacOS').mkdir(parents=True)
        with (app/'Contents/Info.plist').open('wb') as f:
            plistlib.dump({'CFBundleIdentifier':'com.mudforge.app','CFBundleExecutable':'mudforge',
                          'CFBundleShortVersionString':'1.2.2394'}, f)
        (app/'Contents/MacOS/mudforge').write_bytes(b'\xcf\xfa\xed\xfe\x0c\x00\x00\x01')
        result = diagnose_macos.diagnose(app, self.root)
        self.assertEqual(result['installations'][0]['architectures'], ['arm64'])
        self.assertFalse(result['native_runtime_tested'])


if __name__ == '__main__':
    unittest.main()
