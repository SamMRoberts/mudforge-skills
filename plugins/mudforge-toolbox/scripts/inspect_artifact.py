#!/usr/bin/env python3
"""Inspect documented MudForge containers without extracting or executing content."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile
import zlib

MAX_ARCHIVE = 64 * 1024 * 1024
MAX_MEMBER = 32 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_MEMBERS = 4096
MAX_RATIO = 200


class InspectionError(ValueError):
    """A safe, fixed diagnostic suitable for a public report."""


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InspectionError("duplicate JSON keys")
        result[key] = value
    return result


def parse_json(data):
    def invalid_constant(_value):
        raise InspectionError("non-finite JSON number")
    try:
        return json.loads(data, object_pairs_hook=object_pairs,
                          parse_constant=invalid_constant)
    except (ValueError, UnicodeError, RecursionError):
        raise InspectionError("invalid or excessively nested JSON") from None


def check_member(info):
    name = info.orig_filename
    parts = name.rstrip("/").split("/")
    if (not name or "\\" in name or any(ord(c) < 32 for c in name)
            or PurePosixPath(name).is_absolute()
            or any(p in ("", ".", "..") for p in parts)
            or any(":" in p for p in parts)):
        raise InspectionError("unsafe archive member path")
    mode = info.external_attr >> 16
    if stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
        raise InspectionError("archive contains a link or special file")
    if info.flag_bits & 1:
        raise InspectionError("encrypted archive members are unsupported")
    if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        raise InspectionError("unsupported compression method")
    if info.file_size > MAX_MEMBER:
        raise InspectionError("archive member exceeds size limit")
    if info.file_size / max(1, info.compress_size) > MAX_RATIO:
        raise InspectionError("archive compression ratio exceeds limit")
    return name.rstrip("/").casefold()


def inspect(path):
    """Return redacted envelope evidence, never a claim of native import validity."""
    path = Path(path)
    report = {"status": "rejected", "format": "unknown", "issues": []}
    try:
        if path.is_symlink():
            raise InspectionError("source symlinks are unsupported")
        # Resolve parent aliases such as macOS /var and /tmp for read-only access.
        path = path.resolve()
        if not path.is_file():
            raise InspectionError("source is not a regular file")
        if path.stat().st_size > MAX_ARCHIVE:
            raise InspectionError("artifact exceeds size limit")
        # One bounded read provides a consistent snapshot and its checksum.
        with path.open("rb") as source:
            data = source.read(MAX_ARCHIVE + 1)
        if len(data) > MAX_ARCHIVE:
            raise InspectionError("artifact exceeds size limit")
        report["sha256"] = hashlib.sha256(data).hexdigest()
        if path.name.lower().endswith(".mfw.json"):
            report["format"] = "legacy-world-json"
            if not isinstance(parse_json(data), dict):
                raise InspectionError("legacy JSON root must be an object")
            report.update(status="unsupported", issues=[
                "legacy JSON parsed; full legacy schema is not publicly specified"])
            return report
        extension = path.suffix.lower()
        if extension not in (".mfw", ".mfp"):
            report.update(status="unsupported", issues=["unsupported artifact extension"])
            return report
        report["format"] = "world-zip" if extension == ".mfw" else "package-zip"
        import io
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > MAX_MEMBERS:
                raise InspectionError("too many archive members")
            names = set()
            files = set()
            total = 0
            categories = Counter()
            controls = {}
            for info in members:
                normalized = check_member(info)
                if normalized in names:
                    raise InspectionError("duplicate or case-colliding archive paths")
                names.add(normalized)
                total += info.file_size
                if total > MAX_TOTAL:
                    raise InspectionError("archive exceeds expanded size limit")
                if extension == ".mfp" and PurePosixPath(normalized).name == "world.json":
                    raise InspectionError("package contains forbidden world.json")
                if not info.is_dir():
                    files.add(normalized)
            for name in names:
                if any(p.as_posix() in files for p in PurePosixPath(name).parents
                       if p.as_posix() != "."):
                    raise InspectionError("archive file/directory path collision")
            for info in members:
                if info.is_dir():
                    continue
                name = info.filename
                extension_key = PurePosixPath(name).suffix.lower()
                category = {".lua": "lua", ".json": "json", ".png": "images",
                            ".jpg": "images", ".webp": "images", ".sqlite": "databases",
                            ".db": "databases"}.get(extension_key, "other")
                categories[category] += 1
                # Fully drain every stream to check CRC, without executing anything.
                chunks = [] if extension_key == ".json" else None
                expanded = 0
                with archive.open(info) as member:
                    while chunk := member.read(65536):
                        expanded += len(chunk)
                        if expanded > MAX_MEMBER:
                            raise InspectionError("expanded member exceeds limit")
                        if chunks is not None:
                            chunks.append(chunk)
                if chunks is not None:
                    parsed = parse_json(b"".join(chunks))
                    if name in ("world.json", "package.json"):
                        controls[name] = parsed
            report["inventory"] = {"files": len(files), "expanded_bytes": total,
                                   "categories": dict(sorted(categories.items()))}
            required = "world.json" if extension == ".mfw" else "package.json"
            if required not in controls:
                report.update(status="unsupported", issues=["unrecognized container envelope"])
            elif not isinstance(controls[required], dict) or not controls[required]:
                raise InspectionError("container control JSON must be a nonempty object")
            else:
                report.update(status="envelope_checked", issues=[
                    "full content schema, permissions, and native import are unverified"])
    except InspectionError as error:
        report.update(status="rejected", issues=[str(error)])
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError, ValueError, zlib.error):
        # Never echo exceptions containing private paths, archive names, or data.
        report.update(status="rejected", issues=["unreadable or malformed artifact"])
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path)
    args = parser.parse_args()
    result = inspect(args.artifact)
    print(json.dumps(result, indent=2, sort_keys=True))
    return {"envelope_checked": 0, "rejected": 1, "unsupported": 2}[result["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
