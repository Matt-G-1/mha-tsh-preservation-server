from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_asset_drama_stage_hints import DEFAULT_ASSET_ROOT, collect_drama_stage_hints


DEFAULT_STAGE_CFG_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "4YOU"
    / "16eeb8bc82c44019"
)

LUA_HEADER = b"\x1bLua"
STRING_TAGS = {4, 0x37}
STAGE_REF_RE = re.compile(r"^stage(\d{3,6})(?:[a-z]|_\d+|_[a-z]+)?$")


class _RootConstantReader:
    def __init__(self, data: bytes) -> None:
        header_offset = data.find(LUA_HEADER)
        if header_offset < 0:
            encoded_header_offset = data.find(b"LuaQ")
            if encoded_header_offset < 0:
                raise ValueError("Lua header not found")
            data = b"\x1b" + data[encoded_header_offset:]
        else:
            data = data[header_offset:]
        self.data = data
        self.offset = 12

    def read(self, size: int) -> bytes:
        end = self.offset + size
        if end > len(self.data):
            raise ValueError("unexpected end while reading Lua chunk")
        value = self.data[self.offset:end]
        self.offset = end
        return value

    def u8(self) -> int:
        return self.read(1)[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.read(4))[0]

    def count(self, minimum_item_size: int = 1) -> int:
        encoded_count = self.u32()
        remaining = len(self.data) - self.offset
        if encoded_count * minimum_item_size > remaining:
            return encoded_count & 0xFF
        return encoded_count

    def lua_string(self) -> str:
        encoded_size = self.u32()
        size = encoded_size & 0xFFFF
        if not size:
            return ""
        raw = self.read(size)
        if raw.endswith(b"\x00"):
            raw = raw[:-1]
        return raw.decode("utf-8", "replace")

    def root_constants(self) -> list[object]:
        self.lua_string()
        self.read(12)
        self.read(self.count(4) * 4)
        constants: list[object] = []
        for _ in range(self.count()):
            tag = self.u8()
            if tag == 0:
                constants.append(None)
            elif tag == 1:
                constants.append(bool(self.u8()))
            elif tag == 3:
                constants.append(struct.unpack("<d", self.read(8))[0])
            elif tag in STRING_TAGS:
                constants.append(self.lua_string())
            else:
                raise ValueError(f"unsupported constant tag {tag:#x}")
        return constants


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_stage_id(value: int | None) -> bool:
    return value is not None and 100000 <= value <= 999999


def _candidate_score(
    candidate: int, constants: list[object], start: int, end: int
) -> int:
    prefix = str(candidate)
    score = 0
    for value in constants[start:end]:
        number = _as_int(value)
        if number is not None and str(number).startswith(prefix) and number != candidate:
            score += 3
        elif isinstance(value, str) and value.startswith(prefix):
            score += 2
    return score


def _route_for_script(script: str, index: int, constants: list[object]) -> dict[str, object]:
    embedded = STAGE_REF_RE.match(script)
    if embedded:
        return {
            "route_stage_id": int(embedded.group(1)),
            "confidence": "embedded",
            "constant_index": index,
        }

    start = max(0, index - 12)
    end = min(len(constants), index + 8)
    candidates: list[tuple[int, int, int]] = []
    for position in range(start, index + 1):
        value = _as_int(constants[position])
        if not _is_stage_id(value):
            continue
        score = _candidate_score(value, constants, position, end)
        candidates.append((score, -abs(index - position), value))
    if not candidates:
        return {"route_stage_id": None, "confidence": "none", "constant_index": index}
    score, _, stage_id = max(candidates)
    return {
        "route_stage_id": stage_id,
        "confidence": "prefix-neighborhood" if score else "nearby",
        "constant_index": index,
    }


def collect_stage_cfg_route_hints(
    stage_cfg_asset: Path = DEFAULT_STAGE_CFG_ASSET,
    asset_root: Path = DEFAULT_ASSET_ROOT,
) -> dict[str, object]:
    constants = _RootConstantReader(stage_cfg_asset.read_bytes()).root_constants()
    drama_scripts = {
        item["script"]
        for item in collect_drama_stage_hints(asset_root)["scripts"]
        if isinstance(item.get("script"), str)
    }
    routes: dict[str, dict[str, object]] = {}
    for index, value in enumerate(constants):
        if not isinstance(value, str) or value not in drama_scripts:
            continue
        routes[value] = _route_for_script(value, index, constants)
    return {
        "constant_count": len(constants),
        "script_route_count": len(routes),
        "routes": routes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover stage_cfg drama-script route hints from Lua constants."
    )
    parser.add_argument("--stage-cfg", type=Path, default=DEFAULT_STAGE_CFG_ASSET)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_stage_cfg_route_hints(args.stage_cfg, args.asset_root),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
