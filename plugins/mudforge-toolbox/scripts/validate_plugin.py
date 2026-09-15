#!/usr/bin/env python3
"""Validate this bundle's manifest, skills, custom agents, and local references."""

import argparse
import json
from pathlib import Path
import re
import tomllib
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = {"mudforge-macos", "mudforge-lua-scripting", "mudforge-plugin-development",
          "mudforge-widgets", "mudforge-events-protocols", "mudforge-mapper",
          "mudforge-worlds-migration", "mudforge-testing"}
AGENTS = {"mudforge-developer", "mudforge-diagnostics", "mudforge-qa"}
SUFFIXES = {".md", ".json", ".yaml", ".toml", ".py", ".lua"}


def ignored(path):
    return (path.name == ".DS_Store" or "__pycache__" in path.parts
            or path.suffix == ".pyc")


def bundle_files(root):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError("symlinks are not distributable")
        if ignored(relative) or path.is_dir():
            continue
        if (relative.parts[0] not in {".codex-plugin", "skills", "agents", "scripts", "references", "README.md"}
                or path.suffix not in SUFFIXES):
            raise ValueError("unexpected file in distributable: " + relative.as_posix())
        yield path


def validate(root=ROOT):
    root = Path(root).resolve()
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    try:
        files = list(bundle_files(root))
        manifest = json.loads((root / ".codex-plugin/plugin.json").read_text())
        allowed = {"name", "version", "description", "author", "repository", "homepage",
                   "license", "keywords", "skills", "interface"}
        check(not set(manifest) - allowed, "unsupported manifest fields")
        check(manifest.get("name") == "mudforge-toolbox", "incorrect plugin name")
        check(bool(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", manifest.get("version", ""))),
              "version must be semver")
        check(manifest.get("skills") == "./skills/", "skills path must be ./skills/")
        check(bool(manifest.get("description")), "missing description")
        check(bool(manifest.get("author", {}).get("name")), "missing author")
        interface = manifest.get("interface", {})
        for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
            check(isinstance(interface.get(key), str) and bool(interface[key].strip()), "missing interface " + key)
        prompts = interface.get("defaultPrompt")
        check(isinstance(prompts, list) and 1 <= len(prompts) <= 3
              and all(isinstance(p, str) and 0 < len(p) <= 128 for p in prompts), "invalid starter prompts")
        capabilities = interface.get("capabilities")
        check(isinstance(capabilities, list) and all(isinstance(c, str) for c in capabilities), "invalid capabilities")
        actual_skills = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
        check(actual_skills == SKILLS, "expected exactly eight skills")
        for name in sorted(SKILLS):
            folder = root / "skills" / name
            text = (folder / "SKILL.md").read_text()
            match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
            if not match:
                errors.append(name + ": missing frontmatter")
                continue
            front = yaml.safe_load(match[1])
            check(isinstance(front, dict) and front.get("name") == name and bool(front.get("description")),
                  name + ": invalid frontmatter")
            metadata = yaml.safe_load((folder / "agents/openai.yaml").read_text())
            ui = metadata.get("interface", {})
            check(bool(ui.get("display_name")), name + ": missing display name")
            check(25 <= len(ui.get("short_description", "")) <= 64, name + ": short description length")
            check("$" + name in ui.get("default_prompt", ""), name + ": missing skill invocation")
            check(metadata.get("policy", {}).get("allow_implicit_invocation", True) is True,
                  name + ": implicit discovery should remain enabled")
        actual_agents = {p.stem for p in (root / "agents").glob("*.toml")}
        check(actual_agents == AGENTS, "expected exactly three custom agents")
        for name in sorted(AGENTS):
            agent = tomllib.loads((root / "agents" / (name + ".toml")).read_text())
            for key in ("name", "description", "developer_instructions"):
                check(isinstance(agent.get(key), str) and bool(agent[key].strip()), name + ": missing " + key)
            check(agent.get("name") == name, name + ": name mismatch")
            check(not {"model", "model_reasoning_effort"} & agent.keys(), name + ": model should be inherited")
        check(tomllib.loads((root / "agents/mudforge-diagnostics.toml").read_text()).get("sandbox_mode") == "read-only",
              "diagnostics must default to read-only")
        for path in files:
            text = path.read_text(encoding="utf-8")
            if path.suffix != ".py":
                check("[TODO:" not in text, "unfinished scaffold: " + path.relative_to(root).as_posix())
            if path.suffix != ".md":
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", text):
                url = urlsplit(target)
                if url.scheme or target.startswith("#"):
                    continue
                resolved = (path.parent / unquote(url.path)).resolve()
                check(resolved.is_relative_to(root) and resolved.is_file(),
                      "missing or escaping reference in " + path.relative_to(root).as_posix() + ": " + target)
        for required in ("README.md", "scripts/activate_agents.py", "scripts/inspect_artifact.py",
                         "scripts/diagnose_macos.py", "scripts/build_plugin.py"):
            check((root / required).is_file(), "missing " + required)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, yaml.YAMLError) as error:
        errors.append("validation could not complete: " + str(error))
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plugin", nargs="?", default=ROOT, type=Path)
    args = parser.parse_args()
    problems = validate(args.plugin)
    print(json.dumps({"ok": not problems, "errors": problems}, indent=2))
    raise SystemExit(bool(problems))
