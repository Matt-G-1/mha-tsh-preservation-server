from __future__ import annotations

import argparse
from pathlib import Path

from patch_lua_string import update_md5_manifest


def parse_hex(value: str) -> bytes:
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Replace one fixed-width instruction in a Lua bytecode asset"
    )
    parser.add_argument("asset", type=Path)
    parser.add_argument("offset", type=int)
    parser.add_argument("expected", type=parse_hex)
    parser.add_argument("replacement", type=parse_hex)
    parser.add_argument("--md5-manifest", type=Path)
    parser.add_argument("--relative-path")
    args = parser.parse_args()

    if len(args.expected) != len(args.replacement):
        parser.error("expected and replacement instructions must have equal length")

    data = args.asset.read_bytes()
    end = args.offset + len(args.expected)
    actual = data[args.offset:end]
    if actual != args.expected:
        raise ValueError(
            f"Instruction mismatch at {args.offset}: "
            f"expected {args.expected.hex()}, found {actual.hex()}"
        )

    args.asset.write_bytes(data[: args.offset] + args.replacement + data[end:])

    if args.md5_manifest:
        if not args.relative_path:
            parser.error("--relative-path is required with --md5-manifest")
        update_md5_manifest(args.md5_manifest, args.relative_path, args.asset)


if __name__ == "__main__":
    main()
