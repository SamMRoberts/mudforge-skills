#!/usr/bin/env python3
"""Read MudForge bundle metadata and storage presence; never inspect world values."""

import argparse
import json
from pathlib import Path
import platform
import plistlib
import struct


def architectures(executable):
    try:
        with executable.open("rb") as handle:
            header = handle.read(4096)
        if header[:4] == b"\xcf\xfa\xed\xfe":
            cpus = [struct.unpack_from("<I", header, 4)[0]]
        elif header[:4] in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
            count = struct.unpack_from(">I", header, 4)[0]
            width = 32 if header[3] == 0xBF else 20
            if count > 16:
                return ["unknown"]
            cpus = [struct.unpack_from(">I", header, 8 + width*i)[0] for i in range(count)]
        else:
            return ["unknown"]
        return sorted({{0x1000007: "x86_64", 0x100000C: "arm64"}.get(cpu, "unknown")
                       for cpu in cpus})
    except (OSError, struct.error):
        return ["unknown"]


def diagnose(app=None, home=None):
    home = Path(home) if home else Path.home()
    candidates = [Path(app).expanduser()] if app else [
        Path("/Applications/MudForge.app"), home / "Applications/MudForge.app"]
    found = []
    for candidate in candidates:
        info_path = candidate / "Contents/Info.plist"
        if not info_path.is_file():
            continue
        try:
            with info_path.open("rb") as handle:
                info = plistlib.load(handle)
            bundle = info.get("CFBundleIdentifier", "")
            executable = info.get("CFBundleExecutable", "")
            if (not isinstance(bundle, str) or not bundle or "/" in bundle or "\\" in bundle
                    or bundle in (".", "..") or not isinstance(executable, str)
                    or Path(executable).name != executable or executable in ("", ".", "..")):
                raise ValueError("invalid bundle metadata")
            roots = [home / "Library/Application Support" / bundle,
                     home / "Library/WebKit" / bundle, home / "MudForge"]
            found.append({"app": str(candidate), "bundle_id": bundle,
                          "version": info.get("CFBundleShortVersionString"),
                          "architectures": architectures(candidate / "Contents/MacOS" / executable),
                          "storage": [{"path": str(p), "exists": p.exists()} for p in roots]})
        except (OSError, ValueError, plistlib.InvalidFileException):
            found.append({"app": str(candidate), "error": "unreadable bundle metadata"})
    return {"platform": platform.system(), "host_architecture": platform.machine(),
            "installations": found, "native_runtime_tested": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path)
    args = parser.parse_args()
    print(json.dumps(diagnose(args.app), indent=2))
