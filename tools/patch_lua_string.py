from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path


def patch_lua_string(
    data: bytes, old: bytes, new: bytes, expected_offset: int | None = None
) -> bytes:
    matches = []
    start = 0
    while True:
        offset = data.find(old, start)
        if offset < 0:
            break
        matches.append(offset)
        start = offset + len(old)
    if expected_offset is not None:
        matches = [offset for offset in matches if offset == expected_offset]
    if len(matches) != 1:
        raise ValueError(f"Expected one match for {old!r}, found {len(matches)}")

    offset = matches[0]
    if offset < 5 or data[offset - 5] != 4:
        raise ValueError(f"String at {offset} is not a Lua string constant")
    stored_length = struct.unpack_from("<I", data, offset - 4)[0]
    if stored_length != len(old) + 1 or data[offset + len(old)] != 0:
        raise ValueError(
            f"String length mismatch at {offset}: stored={stored_length}, "
            f"expected={len(old) + 1}"
        )

    return (
        data[: offset - 4]
        + struct.pack("<I", len(new) + 1)
        + new
        + b"\x00"
        + data[offset + len(old) + 1 :]
    )


def update_md5_manifest(manifest: Path, relative_path: str, asset: Path) -> None:
    digest = hashlib.md5(asset.read_bytes()).hexdigest()
    compact_digest = digest[8:24]
    lines = manifest.read_text(encoding="ascii").splitlines()
    suffix = f",{relative_path},"
    matches = [index for index, line in enumerate(lines) if suffix in line]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one manifest entry for {relative_path}, found {len(matches)}"
        )
    index = matches[0]
    columns = lines[index].split(",")
    columns[0] = compact_digest
    lines[index] = ",".join(columns)
    manifest.write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch a Lua 5.1 string constant")
    parser.add_argument("asset", type=Path)
    parser.add_argument("old")
    parser.add_argument("new")
    parser.add_argument("--offset", type=int)
    parser.add_argument("--md5-manifest", type=Path)
    parser.add_argument("--relative-path")
    args = parser.parse_args()

    data = args.asset.read_bytes()
    patched = patch_lua_string(
        data, args.old.encode(), args.new.encode(), args.offset
    )
    args.asset.write_bytes(patched)

    if args.md5_manifest:
        if not args.relative_path:
            parser.error("--relative-path is required with --md5-manifest")
        update_md5_manifest(args.md5_manifest, args.relative_path, args.asset)


if __name__ == "__main__":
    main()
