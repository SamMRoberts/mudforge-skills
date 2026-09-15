#!/usr/bin/env python3
"""Build a reproducible Codex ZIP and SHA-256 checksum from this plugin."""

import argparse
import hashlib
from pathlib import Path
import tempfile
import zipfile

from validate_plugin import ROOT, bundle_files, validate


def build(output, root=ROOT):
    root = Path(root).resolve()
    output = Path(output).absolute()
    if output.is_symlink() or output.resolve().is_relative_to(root):
        raise ValueError("output must be outside the plugin source tree and not a symlink")
    problems = validate(root)
    if problems:
        raise ValueError("invalid plugin: " + "; ".join(problems))
    output.parent.mkdir(parents=True, exist_ok=True)
    checksum = output.with_suffix(output.suffix + ".sha256")
    if checksum.is_symlink():
        raise ValueError("checksum destination may not be a symlink")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".zip", delete=False) as handle:
            temporary = Path(handle.name)
        # Stored ZIP avoids compression-version differences; normalized metadata
        # and sorted entries make identical sources produce identical bytes.
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED) as archive:
            for path in bundle_files(root):
                info = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        temporary.replace(output)
        checksum.write_text(digest + "  " + output.name + "\n")
        return {"archive": str(output), "sha256": digest}
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        import json
        print(json.dumps(build(args.output), indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f"build failed: {error}\n")
