from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_ACT_DAILY_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "3BAO"
    / "7633aad8b4929bd2"
)
ACT_DAILY_STAGE_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/3BAO/7633aad8b4929bd2, "
    "./script/setting/act/act_daily_stage_cfg.lua, parsed 2026-06-23"
)

DAILY_STAGE_RANGES = (
    (860001, 860007, "daily_stage"),
    (860011, 860017, "daily_stage_extra"),
    (880001, 880007, "named_daily_challenge"),
    (882001, 882008, "snowman_daily_challenge"),
    (890001, 890005, "awake_daily_challenge"),
)


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if value.is_integer():
            return int(value)
        integer = int(value)
        if 850000 <= integer <= 899999 and abs(value - integer) < 0.25:
            return integer
    return None


def _stage_section(stage_id: int) -> str:
    for start, end, section in DAILY_STAGE_RANGES:
        if start <= stage_id <= end:
            return section
    return ""


def _is_daily_stage_id(value: int | None) -> bool:
    return value is not None and bool(_stage_section(value))


def _is_member_id(value: int | None) -> bool:
    return value is not None and 1000 <= value <= 1999


def _is_member_shape_id(value: int | None) -> bool:
    return value is not None and 36000 <= value <= 37999


def _is_monster_model_id(value: int | None) -> bool:
    return value is not None and 2000 <= value <= 3999


def _total_limit(constants: list[object]) -> int:
    try:
        index = constants.index("TotalLimit")
    except ValueError:
        return 0
    if index + 1 >= len(constants):
        return 0
    return _as_int(constants[index + 1]) or 0


def _stage_name(constants: list[object], index: int) -> str:
    previous = constants[index - 1] if index else ""
    if isinstance(previous, str) and previous not in {"Name", "StageId"}:
        return previous
    return ""


def _sub_id_after(constants: list[object], index: int) -> int:
    if index + 1 >= len(constants):
        return 0
    sub_id = _as_int(constants[index + 1])
    if sub_id is None or _is_daily_stage_id(sub_id):
        return 0
    return sub_id


def _member_values(values: list[object]) -> tuple[int, ...]:
    output: list[int] = []
    for value in values:
        number = _as_int(value)
        if _is_member_id(number) and number not in output:
            output.append(number)
    return tuple(output)


def _member_shape_values(values: list[object]) -> tuple[int, ...]:
    output: list[int] = []
    for value in values:
        number = _as_int(value)
        if _is_member_shape_id(number) and number not in output:
            output.append(number)
    return tuple(output)


def _collect_monsters(constants: list[object]) -> tuple[dict[str, object], ...]:
    try:
        start = constants.index("MonsterCfg")
    except ValueError:
        return ()
    end = constants.index("__maketime") if "__maketime" in constants else len(constants)
    monsters: list[dict[str, object]] = []
    seen: set[int] = set()
    for index in range(start, end):
        monster_id = _as_int(constants[index])
        if not _is_monster_model_id(monster_id) or monster_id in seen:
            continue
        seen.add(monster_id)
        display_name = ""
        if index + 1 < end and isinstance(constants[index + 1], str):
            candidate = constants[index + 1]
            if candidate not in {"idle", "idle1", "op1", "op2", "op_moni", "ground2"}:
                display_name = candidate
        monsters.append(
            {
                "monster_id": monster_id,
                "display_name": display_name,
                "constant_index": index,
            }
        )
    return tuple(monsters)


def collect_act_daily_stage_hints(
    act_daily_stage_asset: Path = DEFAULT_ACT_DAILY_STAGE_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(act_daily_stage_asset.read_bytes()).root_constants()
    stage_positions: list[tuple[int, int]] = []
    for index, value in enumerate(constants):
        stage_id = _as_int(value)
        if _is_daily_stage_id(stage_id):
            stage_positions.append((index, int(stage_id)))

    stages: list[dict[str, object]] = []
    for order, (index, stage_id) in enumerate(stage_positions):
        next_index = (
            stage_positions[order + 1][0]
            if order + 1 < len(stage_positions)
            else len(constants)
        )
        window = constants[index + 1 : next_index]
        section = _stage_section(stage_id)
        stages.append(
            {
                "stage_id": stage_id,
                "section": section,
                "display_order": order + 1,
                "sub_id": _sub_id_after(constants, index),
                "name": _stage_name(constants, index),
                "member_ids": _member_values(window),
                "member_shape_ids": _member_shape_values(window),
                "constant_index": index,
            }
        )

    return {
        "source": ACT_DAILY_STAGE_SOURCE,
        "constant_count": len(constants),
        "total_limit": _total_limit(constants),
        "stage_count": len(stages),
        "stages": stages,
        "monsters": list(_collect_monsters(constants)),
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    stages = [
        {
            key: stage[key]
            for key in (
                "stage_id",
                "section",
                "display_order",
                "sub_id",
                "name",
                "member_ids",
                "member_shape_ids",
                "constant_index",
            )
        }
        for stage in payload["stages"]
        if isinstance(stage, dict)
    ]
    monsters = [
        {
            key: monster[key]
            for key in ("monster_id", "display_name", "constant_index")
        }
        for monster in payload["monsters"]
        if isinstance(monster, dict)
    ]
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n\n\n"
        "ACT_DAILY_STAGE_SOURCE = "
        + repr(str(payload["source"]))
        + "\n"
        "ACT_DAILY_TOTAL_LIMIT = "
        + repr(int(payload["total_limit"]))
        + "\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class ActDailyStageDefinition:\n"
        "    stage_id: int\n"
        "    section: str\n"
        "    display_order: int\n"
        "    sub_id: int\n"
        "    name: str\n"
        "    member_ids: tuple[int, ...]\n"
        "    member_shape_ids: tuple[int, ...]\n"
        "    constant_index: int\n\n"
        "    @property\n"
        "    def label(self) -> str:\n"
        "        if self.name:\n"
        "            return self.name\n"
        "        return f'{self.section} {self.stage_id}'\n\n"
        "    def as_dict(self) -> dict[str, object]:\n"
        "        return {\n"
        "            'StageId': self.stage_id,\n"
        "            'Section': self.section,\n"
        "            'DisplayOrder': self.display_order,\n"
        "            'SubId': self.sub_id,\n"
        "            'Name': self.name,\n"
        "            'MemberIds': list(self.member_ids),\n"
        "            'MemberShapeIds': list(self.member_shape_ids),\n"
        "            'TotalLimit': ACT_DAILY_TOTAL_LIMIT,\n"
        "            'Source': ACT_DAILY_STAGE_SOURCE,\n"
        "        }\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class ActDailyMonsterDefinition:\n"
        "    monster_id: int\n"
        "    display_name: str\n"
        "    constant_index: int\n\n\n"
        "ACT_DAILY_STAGES = tuple(\n"
        "    ActDailyStageDefinition(**item)\n"
        "    for item in "
        + pformat(stages, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "ACT_DAILY_STAGE_BY_ID = {stage.stage_id: stage for stage in ACT_DAILY_STAGES}\n\n"
        "ACT_DAILY_MONSTERS = tuple(\n"
        "    ActDailyMonsterDefinition(**item)\n"
        "    for item in "
        + pformat(monsters, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "ACT_DAILY_MONSTER_IDS = tuple(monster.monster_id for monster in ACT_DAILY_MONSTERS)\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover daily activity stage IDs from act_daily_stage_cfg."
    )
    parser.add_argument(
        "--act-daily-stage",
        type=Path,
        default=DEFAULT_ACT_DAILY_STAGE_ASSET,
    )
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()

    payload = collect_act_daily_stage_hints(args.act_daily_stage)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
