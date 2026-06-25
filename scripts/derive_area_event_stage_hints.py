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
DEFAULT_DRAMA_INDEX = Path("analysis") / "intro_qte_asset_index.txt"
AREA_EVENT_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/0QIU/7b71e951b327b200, "
    "./script/setting/stage/areaevent_cfg.lua, parsed 2026-06-23"
)

AREA_STAGE_NAME_RE = re.compile(r"^(?P<chapter>\d+)-(?P<step>\d+)")
AREA_SCRIPT_RE = re.compile(r"^area[\w-]+(?:_start)?$")
DRAMA_INDEX_SCRIPT_RE = re.compile(r"\./script/setting/dramas/([^\s'\"\]]+)\.lua")
AREA_INDEX_SCRIPT_RE = re.compile(r"^area[`_-]?(?P<chapter>\d+)[_-](?P<step>\d+)")


def _resolve_related_path(anchor: Path, related: Path) -> Path:
    if related.is_absolute() or related.exists():
        return related
    for parent in (anchor.resolve().parent, *anchor.resolve().parents):
        candidate = parent / related
        if candidate.exists():
            return candidate
    return related


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


def _natural_script_key(value: str) -> tuple[object, ...]:
    return tuple(
        int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)
    )


def _area_script_flow_key(value: str) -> tuple[object, ...]:
    lower = value.lower()
    if "start" in lower:
        phase = 1
    elif "boss" in lower:
        phase = 3
    elif "end" in lower:
        phase = 4
    else:
        phase = 2
    return (phase, *_natural_script_key(value))


def _sorted_area_scripts(
    key: tuple[int, int],
    scripts: list[str],
) -> tuple[str, ...]:
    chapter, step = key
    base_names = {
        f"area{chapter}_{step}",
        f"area{chapter}-{step}",
        f"area_{chapter}_{step}",
        f"area`_{chapter}_{step}",
    }

    def sort_key(value: str) -> tuple[object, ...]:
        if value in base_names:
            return (0, *_natural_script_key(value))
        return (1, *_area_script_flow_key(value))

    return tuple(sorted(scripts, key=sort_key))


def _area_event_scripts_by_chapter_step(
    drama_index: Path = DEFAULT_DRAMA_INDEX,
) -> dict[tuple[int, int], tuple[str, ...]]:
    if not drama_index.exists():
        return {}
    text = drama_index.read_text(encoding="utf-8", errors="ignore")
    groups: dict[tuple[int, int], list[str]] = {}
    for match in DRAMA_INDEX_SCRIPT_RE.finditer(text):
        script = match.group(1)
        area_match = AREA_INDEX_SCRIPT_RE.match(script)
        if area_match is None:
            continue
        chapter = int(area_match.group("chapter"))
        step = int(area_match.group("step"))
        group = groups.setdefault((chapter, step), [])
        if script not in group:
            group.append(script)
    return {
        key: _sorted_area_scripts(key, scripts)
        for key, scripts in sorted(groups.items())
    }


def collect_area_event_stage_hints(
    area_event_asset: Path = DEFAULT_AREA_EVENT_ASSET,
    drama_index: Path = DEFAULT_DRAMA_INDEX,
) -> dict[str, object]:
    drama_index = _resolve_related_path(area_event_asset, drama_index)
    constants = _RootConstantReader(area_event_asset.read_bytes()).root_constants()
    script_groups = _area_event_scripts_by_chapter_step(drama_index)
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
        scripts = script_groups.get((chapter, step), ())
        if open_drama and open_drama not in scripts:
            scripts = (open_drama, *scripts)
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
                "scripts": scripts,
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
                "scripts",
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
        "    scripts: tuple[str, ...]\n"
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
        "            'Scripts': self.scripts,\n"
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Recover area-event stage progression from areaevent_cfg."
    )
    parser.add_argument("--area-event", type=Path, default=DEFAULT_AREA_EVENT_ASSET)
    parser.add_argument("--drama-index", type=Path, default=DEFAULT_DRAMA_INDEX)
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()

    payload = collect_area_event_stage_hints(args.area_event, args.drama_index)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
