from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_AREA_EVENT_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "0QIU"
    / "7b71e951b327b200"
)
AREA_EVENT_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/0QIU/7b71e951b327b200, "
    "./script/setting/stage/areaevent_cfg.lua, parsed 2026-06-23"
)

AREA_STAGE_NAME_RE = re.compile(r"^(?P<chapter>\d+)-(?P<step>\d+)")
AREA_SCRIPT_RE = re.compile(r"^area[\w-]+(?:_start)?$")


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_area_stage_id(value: int) -> bool:
    return 21000 <= value <= 21999 or 211000 <= value <= 211999


def _last_int(
    values: list[object],
    predicate,
) -> int | None:
    for value in reversed(values):
        number = _as_int(value)
        if number is not None and predicate(number):
            return number
    return None


def _last_string(
    values: list[object],
    predicate,
) -> str:
    for value in reversed(values):
        if isinstance(value, str) and predicate(value):
            return value
    return ""


def _description_before_name(values: list[object], stage_map: str) -> str:
    if stage_map and stage_map in values:
        values = values[: values.index(stage_map)]
    return _last_string(
        values,
        lambda value: len(value) > 18
        and not value.startswith("区域事件H_"),
    )


def _area_name_before_stage(values: list[object], area_image: str) -> str:
    if not area_image or area_image not in values:
        return ""
    cursor = values.index(area_image) + 1
    while cursor < len(values):
        value = values[cursor]
        if (
            isinstance(value, str)
            and value not in {"AEName", "BOSSImage", "BOSSName"}
            and not value.startswith("区域事件H_")
        ):
            return value
        cursor += 1
    return ""


def collect_area_event_stage_hints(
    area_event_asset: Path = DEFAULT_AREA_EVENT_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(area_event_asset.read_bytes()).root_constants()
    name_positions: list[tuple[int, str, int, int]] = []
    for index, value in enumerate(constants):
        if not isinstance(value, str):
            continue
        match = AREA_STAGE_NAME_RE.match(value)
        if match is None:
            continue
        name_positions.append(
            (
                index,
                value,
                int(match.group("chapter")),
                int(match.group("step")),
            )
        )

    stages: list[dict[str, object]] = []
    for order, (index, name, chapter, step) in enumerate(name_positions):
        start = name_positions[order - 1][0] + 1 if order else 0
        window = constants[max(start, index - 96) : index]
        stage_id = _last_int(
            window,
            lambda value: _is_area_stage_id(value) and value % 10 == 1,
        )
        if stage_id is None:
            continue
        stage_map = _last_string(
            window, lambda value: value.startswith("区域事件H_关卡底图_stage")
        )
        area_image = _last_string(
            window, lambda value: value.startswith("区域事件H_区域图片_area")
        )
        open_drama = _last_string(window, lambda value: AREA_SCRIPT_RE.match(value))
        stages.append(
            {
                "stage_id": stage_id,
                "chapter": chapter,
                "step": step,
                "display_order": order + 1,
                "name": name,
                "description": _description_before_name(window, stage_map),
                "stage_map": stage_map,
                "area_image": area_image,
                "area_name": _area_name_before_stage(window, area_image),
                "open_drama": open_drama,
                "relate_stage": _last_int(
                    window, lambda value: 290000 <= value <= 299999
                )
                or 0,
                "reward_show_id": _last_int(
                    window, lambda value: _is_area_stage_id(value) and value % 10 == 6
                )
                or 0,
                "reward_tips_item_id": _last_int(
                    window, lambda value: 1013000 <= value <= 1013999
                )
                or 0,
                "constant_index": index,
            }
        )

    for previous, current, following in zip(
        [None, *stages[:-1]],
        stages,
        [*stages[1:], None],
    ):
        current["previous_stage_id"] = previous["stage_id"] if previous else 0
        current["next_stage_id"] = following["stage_id"] if following else 0

    return {
        "source": AREA_EVENT_SOURCE,
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
                "chapter",
                "step",
                "display_order",
                "name",
                "description",
                "stage_map",
                "area_image",
                "area_name",
                "open_drama",
                "relate_stage",
                "reward_show_id",
                "reward_tips_item_id",
                "constant_index",
                "previous_stage_id",
                "next_stage_id",
            )
        }
        for stage in payload["stages"]
        if isinstance(stage, dict)
    ]
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n\n\n"
        "AREA_EVENT_STAGE_SOURCE = "
        + repr(str(payload["source"]))
        + "\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class AreaEventStageDefinition:\n"
        "    stage_id: int\n"
        "    chapter: int\n"
        "    step: int\n"
        "    display_order: int\n"
        "    name: str\n"
        "    description: str\n"
        "    stage_map: str\n"
        "    area_image: str\n"
        "    area_name: str\n"
        "    open_drama: str\n"
        "    relate_stage: int\n"
        "    reward_show_id: int\n"
        "    reward_tips_item_id: int\n"
        "    constant_index: int\n"
        "    previous_stage_id: int\n"
        "    next_stage_id: int\n\n"
        "    def as_dict(self) -> dict[str, object]:\n"
        "        return {\n"
        "            'StageId': self.stage_id,\n"
        "            'Chapter': self.chapter,\n"
        "            'Step': self.step,\n"
        "            'DisplayOrder': self.display_order,\n"
        "            'Name': self.name,\n"
        "            'Description': self.description,\n"
        "            'StageMap': self.stage_map,\n"
        "            'AreaImage': self.area_image,\n"
        "            'AreaName': self.area_name,\n"
        "            'OpenDrama': self.open_drama,\n"
        "            'RelateStage': self.relate_stage,\n"
        "            'RewardShowId': self.reward_show_id,\n"
        "            'RewardTipsItemId': self.reward_tips_item_id,\n"
        "            'PreviousStageId': self.previous_stage_id,\n"
        "            'NextStageId': self.next_stage_id,\n"
        "            'Source': AREA_EVENT_STAGE_SOURCE,\n"
        "        }\n\n\n"
        "AREA_EVENT_STAGES = tuple(\n"
        "    AreaEventStageDefinition(**item)\n"
        "    for item in "
        + pformat(stages, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "AREA_EVENT_STAGE_BY_ID = {stage.stage_id: stage for stage in AREA_EVENT_STAGES}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover area-event stage progression from areaevent_cfg."
    )
    parser.add_argument("--area-event", type=Path, default=DEFAULT_AREA_EVENT_ASSET)
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()

    payload = collect_area_event_stage_hints(args.area_event)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
