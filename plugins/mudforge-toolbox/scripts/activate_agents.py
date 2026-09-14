#!/usr/bin/env python3
"""Explicitly copy bundled agents into one project's .codex/agents directory."""

import argparse
import json
import os
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]


def activate(project, dry_run=False, root=ROOT):
    project = Path(project).expanduser().absolute()
    if not project.is_dir():
        raise ValueError("project must be an existing directory")
    destination = project / ".codex/agents"
    if any(p.is_symlink() for p in (destination, *destination.parents)):
        raise ValueError("destination may not traverse symlinks")
    if any(p.exists() and not p.is_dir() for p in (project / ".codex", destination)):
        raise ValueError("destination parent is not a directory")
    planned = []
    sources = sorted((root / "agents").glob("*.toml"))
    if len(sources) != 3:
        raise ValueError("expected three bundled agents")
    for source in sources:
        if source.is_symlink():
            raise ValueError("agent source may not be a symlink")
        data = source.read_bytes()
        agent = tomllib.loads(data.decode("utf-8"))
        if agent.get("name") != source.stem:
            raise ValueError("agent name must match its filename")
        for key in ("name", "description", "developer_instructions"):
            if not isinstance(agent.get(key), str) or not agent[key].strip():
                raise ValueError("invalid agent definition")
        target = destination / source.name
        if target.is_symlink() or (target.exists() and not target.is_file()):
            raise ValueError("agent destination is not a regular file")
        if target.exists() and target.read_bytes() != data:
            raise ValueError("conflicting agent exists; no files were overwritten")
        planned.append((target, data, target.exists()))
    result = {"dry_run": dry_run, "agents": [
        {"name": p.stem, "action": "unchanged" if exists else "create"}
        for p, _, exists in planned]}
    if dry_run or all(exists for _, _, exists in planned):
        return result
    made_dirs = []
    created = []
    try:
        for directory in (project / ".codex", destination):
            if not directory.exists():
                directory.mkdir()
                made_dirs.append(directory)
        for target, data, exists in planned:
            if exists:
                continue
            # Exclusive creation protects existing files even if preflight races.
            with target.open("xb") as handle:
                owned = os.fstat(handle.fileno())
                created.append((target, owned.st_dev, owned.st_ino))
                handle.write(data)
    except OSError:
        for target, device, inode in reversed(created):
            try:
                current = target.lstat()
                if current.st_dev == device and current.st_ino == inode and not target.is_symlink():
                    target.unlink()
            except FileNotFoundError:
                pass
        for directory in reversed(made_dirs):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise ValueError("activation failed; existing agents were not overwritten") from None
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(activate(args.project, args.dry_run), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, f"activation failed: {error}\n")
