from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_CFG_DIR = Path("analysis") / "mediafire_20260620" / "decoded_cfg"
WORLD_CONFIG_SOURCE = (
    "analysis/mediafire_20260620/decoded_cfg/city_level_cfg.luac, "
    "user_info_cfg.luac, funcopen_cfg.luac, parsed 2026-06-24"
)
OFFICE_LEVEL_RE = re.compile(r"(?:事务所等级达到|通关)(?P<level>\d+)级")


def _constants(path: Path) -> list[object]:
    return _RootConstantReader(path.read_bytes()).root_constants()


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _max_consecutive_level(constants: list[object], *, limit: int) -> int:
    numbers = {
        number
        for value in constants
        if (number := _as_int(value)) is not None and 1 <= number <= limit
    }
    level = 0
    while level + 1 in numbers:
        level += 1
    return level


def _max_office_level(constants: list[object]) -> int:
    levels: list[int] = []
    for value in constants:
        if not isinstance(value, str):
            continue
        for match in OFFICE_LEVEL_RE.finditer(value):
            levels.append(int(match.group("level")))
    return max(levels)


def collect_world_config_hints(cfg_dir: Path = DEFAULT_CFG_DIR) -> dict[str, object]:
    city_constants = _constants(cfg_dir / "city_level_cfg.luac")
    user_info_constants = _constants(cfg_dir / "user_info_cfg.luac")
    funcopen_constants = _constants(cfg_dir / "funcopen_cfg.luac")
    function_ids = sorted(
        {
            number
            for value in funcopen_constants
            if (number := _as_int(value)) is not None and 1 <= number <= 240
        }
    )
    return {
        "source": WORLD_CONFIG_SOURCE,
        "city_level_cap": _max_consecutive_level(city_constants, limit=120),
        "player_level_cap": _max_office_level(user_info_constants),
        "function_open_ids": function_ids,
        "city_level_constant_count": len(city_constants),
        "user_info_constant_count": len(user_info_constants),
        "funcopen_constant_count": len(funcopen_constants),
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    return (
        "from __future__ import annotations\n\n"
        "WORLD_CONFIG_HINT_SOURCE = "
        + repr(str(payload["source"]))
        + "\n"
        "CITY_LEVEL_CAP = "
        + repr(int(payload["city_level_cap"]))
        + "\n"
        "PLAYER_LEVEL_CAP = "
        + repr(int(payload["player_level_cap"]))
        + "\n"
        "FUNCTION_OPEN_IDS = tuple("
        + pformat(payload["function_open_ids"], width=88, sort_dicts=False)
        + ")\n"
        "WORLD_CONFIG_CONSTANT_COUNTS = "
        + pformat(
            {
                "city_level_cfg": int(payload["city_level_constant_count"]),
                "user_info_cfg": int(payload["user_info_constant_count"]),
                "funcopen_cfg": int(payload["funcopen_constant_count"]),
            },
            width=88,
            sort_dicts=False,
        )
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover broad world/player config caps from packed cfg chunks."
    )
    parser.add_argument("cfg_dir", nargs="?", type=Path, default=DEFAULT_CFG_DIR)
    parser.add_argument("--emit-python", action="store_true")
    args = parser.parse_args()

    payload = collect_world_config_hints(args.cfg_dir)
    if args.emit_python:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
