from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_NPC_CFG_ASSET = Path("analysis") / "npc_cfg.normalized.luac"
NPC_CFG_SOURCE = "analysis/npc_cfg.normalized.luac, ./script/setting/npc_cfg.lua"


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _has_cjk(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)


def _is_npc_id(value: int | None) -> bool:
    return value is not None and 5000 <= value <= 6999


def _nearby_npc_ids(
    constants: list[object],
    index: int,
    *,
    radius: int = 4,
) -> tuple[int, ...]:
    candidates: list[tuple[int, int]] = []
    for cursor in range(max(0, index - radius), min(len(constants), index + radius + 1)):
        npc_id = _as_int(constants[cursor])
        if _is_npc_id(npc_id):
            candidates.append((abs(cursor - index), int(npc_id)))
    if not candidates:
        return ()
    nearest_distance = min(distance for distance, _ in candidates)
    output: list[int] = []
    for distance, npc_id in candidates:
        if distance == nearest_distance and npc_id not in output:
            output.append(npc_id)
    return tuple(output)


def collect_npc_cfg_hints(
    npc_cfg_asset: Path = DEFAULT_NPC_CFG_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(npc_cfg_asset.read_bytes()).root_constants()
    name_hints: list[dict[str, object]] = []
    for index, value in enumerate(constants):
        if not isinstance(value, str) or not _has_cjk(value):
            continue
        npc_ids = _nearby_npc_ids(constants, index)
        if not npc_ids:
            continue
        name_hints.append(
            {
                "constant_index": index,
                "text": value,
                "nearest_npc_ids": list(npc_ids),
            }
        )
    return {
        "source": NPC_CFG_SOURCE,
        "constant_count": len(constants),
        "name_hint_count": len(name_hints),
        "name_hints": name_hints,
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    name_hints = payload["name_hints"]
    return (
        "from __future__ import annotations\n\n"
        "NPC_CFG_HINT_SOURCE = "
        + repr(str(payload["source"]))
        + "\n"
        "NPC_CFG_CONSTANT_COUNT = "
        + repr(int(payload["constant_count"]))
        + "\n\n"
        "RECOVERED_NPC_NAME_HINTS = "
        + pformat(name_hints, width=96, sort_dicts=False)
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover conservative NPC name-to-row hints from npc_cfg.lua."
    )
    parser.add_argument("npc_cfg_asset", nargs="?", type=Path, default=DEFAULT_NPC_CFG_ASSET)
    parser.add_argument("--emit-python", action="store_true")
    args = parser.parse_args()

    payload = collect_npc_cfg_hints(args.npc_cfg_asset)
    if args.emit_python:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
