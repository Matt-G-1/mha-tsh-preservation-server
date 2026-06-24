from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_HEROCHIP_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "4YOU"
    / "7e1da27f95a28f95"
)
HEROCHIP_STAGE_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/4YOU/7e1da27f95a28f95, "
    "./script/setting/herochip_stage_cfg.lua, parsed 2026-06-24"
)

DIGIT_STRING_RE = re.compile(r"^\d+$")


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_herochip_stage_id(value: int | None) -> bool:
    return value is not None and 370100 <= value <= 370199


def _first_string(values: list[object], predicate) -> str:
    for value in values:
        if isinstance(value, str) and predicate(value):
            return value
    return ""


def _last_string(values: list[object], predicate) -> str:
    for value in reversed(values):
        if isinstance(value, str) and predicate(value):
            return value
    return ""


def _last_int(values: list[object], predicate) -> int:
    for value in reversed(values):
        number = _as_int(value)
        if predicate(number):
            return int(number)
    return 0


def _hero_class_id(values: list[object]) -> int:
    for value in values:
        if isinstance(value, str) and DIGIT_STRING_RE.match(value):
            return int(value)
    return 0


def collect_herochip_stage_hints(
    herochip_stage_asset: Path = DEFAULT_HEROCHIP_STAGE_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(herochip_stage_asset.read_bytes()).root_constants()
    positions: list[tuple[int, int]] = []
    for index, value in enumerate(constants):
        stage_id = _as_int(value)
        if _is_herochip_stage_id(stage_id):
            positions.append((index, int(stage_id)))

    stages: list[dict[str, object]] = []
    for order, (index, stage_id) in enumerate(positions):
        previous_index = positions[order - 1][0] if order else 0
        next_index = positions[order + 1][0] if order + 1 < len(positions) else len(constants)
        before = constants[previous_index:index]
        after = constants[index + 1 : next_index]
        title = _first_string(
            after,
            lambda value: not value.startswith("碎片本_关卡图_")
            and value
            not in {"StageImage", "Title", "Type", "Values", "class", "subTitle"},
        )
        stages.append(
            {
                "stage_id": stage_id,
                "display_order": order + 1,
                "title": title,
                "stage_desc": _last_string(
                    before, lambda value: value.startswith("进行关卡挑战")
                ),
                "unlock_desc": _last_string(
                    before, lambda value: value.startswith("通关治安事件")
                ),
                "stage_image": _first_string(
                    after, lambda value: value.startswith("碎片本_关卡图_")
                ),
                "hero_class_id": _hero_class_id(after),
                "reward_item_id": _last_int(
                    before, lambda value: value is not None and 1012000 <= value <= 1012999
                ),
                "unlock_stage_id": _last_int(
                    after, lambda value: value is not None and 280000 <= value <= 280999
                ),
                "constant_index": index,
            }
        )

    return {
        "source": HEROCHIP_STAGE_SOURCE,
        "constant_count": len(constants),
        "stage_count": len(stages),
        "stages": stages,
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    stages = [
        {
            key: stage[key]
            for key in (
                "stage_id",
                "display_order",
                "title",
                "stage_desc",
                "unlock_desc",
                "stage_image",
                "hero_class_id",
                "reward_item_id",
                "unlock_stage_id",
                "constant_index",
            )
        }
        for stage in payload["stages"]
        if isinstance(stage, dict)
    ]
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n\n\n"
        "HEROCHIP_STAGE_SOURCE = "
        + repr(str(payload["source"]))
        + "\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class HerochipStageDefinition:\n"
        "    stage_id: int\n"
        "    display_order: int\n"
        "    title: str\n"
        "    stage_desc: str\n"
        "    unlock_desc: str\n"
        "    stage_image: str\n"
        "    hero_class_id: int\n"
        "    reward_item_id: int\n"
        "    unlock_stage_id: int\n"
        "    constant_index: int\n\n"
        "    @property\n"
        "    def label(self) -> str:\n"
        "        return self.title or f'Hero chip stage {self.stage_id}'\n\n"
        "    def as_dict(self) -> dict[str, object]:\n"
        "        return {\n"
        "            'StageId': self.stage_id,\n"
        "            'DisplayOrder': self.display_order,\n"
        "            'Title': self.title,\n"
        "            'StageDesc': self.stage_desc,\n"
        "            'UnlockDesc': self.unlock_desc,\n"
        "            'StageImage': self.stage_image,\n"
        "            'HeroClassId': self.hero_class_id,\n"
        "            'RewardItemId': self.reward_item_id,\n"
        "            'UnlockStageId': self.unlock_stage_id,\n"
        "            'Source': HEROCHIP_STAGE_SOURCE,\n"
        "        }\n\n\n"
        "HEROCHIP_STAGES = tuple(\n"
        "    HerochipStageDefinition(**item)\n"
        "    for item in "
        + pformat(stages, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "HEROCHIP_STAGE_BY_ID = {stage.stage_id: stage for stage in HEROCHIP_STAGES}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover hero chip trial stages from herochip_stage_cfg."
    )
    parser.add_argument(
        "--herochip-stage",
        type=Path,
        default=DEFAULT_HEROCHIP_STAGE_ASSET,
    )
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()

    payload = collect_herochip_stage_hints(args.herochip_stage)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
