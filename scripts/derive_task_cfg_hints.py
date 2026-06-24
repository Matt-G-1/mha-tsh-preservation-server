from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_TASK_CFG_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "decoded_cfg"
    / "task_cfg.luac"
)
TASK_CFG_SOURCE = (
    "analysis/mediafire_20260620/decoded_cfg/task_cfg.luac, "
    "./script/setting/task_cfg.lua, parsed 2026-06-24"
)

AREA_EVENT_RE = re.compile(r"^区域事件\|(?P<event_id>\d+)\|(?P<step>\d+)$")
DRAMA_REF_RE = re.compile(
    r"^(?:cp|zx|fzx|xht|act|stage|area|sj|txbw|beach|bus|huodong|tc)[A-Za-z0-9_|\\.-]*$",
    re.IGNORECASE,
)
DIALOG_TEXT_TERMS = (
    "\u8c08\u8bdd",
    "\u62dc\u8bbf",
    "\u6c47\u62a5",
    "\u544a\u77e5",
    "\u8be2\u95ee",
    "\u4e86\u89e3\u60c5\u51b5",
)
CONTROL_STRINGS = {
    "API",
    "AccCond",
    "AccDramaDesc",
    "AccNpc",
    "AreaId",
    "AutoAcc",
    "AutoAdd",
    "AutoSub",
    "Cond",
    "Count",
    "CreateNpc",
    "DeleteNpc",
    "Desc",
    "DialogAcc",
    "DialogBehavior",
    "DialogSub",
    "DialogTask",
    "DramaName",
    "Exp",
    "FailTall",
    "FcName",
    "Goto",
    "HideSceneTargetIcon",
    "ID",
    "Id",
    "IsHideAutoBtn",
    "IsHideTask",
    "IsShowItemType",
    "Label",
    "Level",
    "Name",
    "NeedCount",
    "Next",
    "NotTrace",
    "NpcAction",
    "NpcDrama",
    "NpcDramaSub",
    "NpcId",
    "ParamList",
    "Pre",
    "Rewards",
    "SceneId",
    "ScenceId",
    "ShowTotalProg",
    "SubDramaDesc",
    "SubNpc",
    "SuccTall",
    "TargetDesc",
    "TaskIcon",
    "TaskImg",
    "TaskTrigger",
    "TaskType",
    "TraceTrigger",
    "Type",
    "TypeDescribe",
    "Value1",
    "Values",
}


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _has_cjk(value: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in value)


def _is_drama_ref(value: str) -> bool:
    return bool(DRAMA_REF_RE.match(value)) or bool(AREA_EVENT_RE.match(value))


def _is_narrative_text(value: str) -> bool:
    if not value or value in CONTROL_STRINGS or _is_drama_ref(value):
        return False
    if value.isdigit() or "|" in value and not _has_cjk(value):
        return False
    if "系统_" in value or value.startswith("地图系统_"):
        return False
    return _has_cjk(value)


def _is_dialog_text(value: str) -> bool:
    return any(term in value for term in DIALOG_TEXT_TERMS)


def _is_task_or_stage_id(value: int | None) -> bool:
    return value is not None and 1000 <= value <= 999999 and not _is_npc_id(value)


def _is_stage_id(value: int | None) -> bool:
    return value is not None and 100000 <= value <= 999999


def _is_npc_id(value: int | None) -> bool:
    return value is not None and 5000 <= value <= 6999


def _nearest_task_id(constants: list[object], index: int) -> int:
    candidates: list[int] = []
    for cursor in range(index - 1, max(-1, index - 10), -1):
        number = _as_int(constants[cursor])
        if _is_task_or_stage_id(number):
            candidates.append(int(number))
    for number in candidates:
        if number >= 100000:
            return number
    if candidates:
        return candidates[0]
    return 0


def _nearby_numbers(
    constants: list[object],
    index: int,
    predicate,
    *,
    radius: int = 10,
) -> tuple[int, ...]:
    output: list[int] = []
    for value in constants[max(0, index - radius) : min(len(constants), index + radius + 1)]:
        number = _as_int(value)
        if predicate(number) and int(number) not in output:
            output.append(int(number))
    return tuple(output)


def _nearby_drama_refs(
    constants: list[object],
    index: int,
    *,
    radius: int = 10,
) -> tuple[str, ...]:
    output: list[str] = []
    for value in constants[max(0, index - radius) : min(len(constants), index + radius + 1)]:
        if isinstance(value, str) and _is_drama_ref(value) and value not in output:
            output.append(value)
    return tuple(output)


def _text_role(value: str) -> str:
    if "#r" in value or "#n" in value or "【x/y】" in value:
        return "objective"
    if len(value) <= 14 and not any(mark in value for mark in "，。！？：；"):
        return "name"
    return "description"


def _text_before(constants: list[object], index: int) -> str:
    for cursor in range(index - 1, max(-1, index - 8), -1):
        value = constants[cursor]
        if isinstance(value, str) and _is_narrative_text(value):
            return value
    return ""


def _text_after(constants: list[object], index: int) -> str:
    for cursor in range(index + 1, min(len(constants), index + 8)):
        value = constants[cursor]
        if isinstance(value, str) and _is_narrative_text(value):
            return value
    return ""


def _task_type_from_task_id(task_id: int) -> int:
    if task_id >= 100000:
        return task_id // 100000
    if task_id >= 1000:
        return task_id // 1000
    return 0


def collect_task_cfg_hints(
    task_cfg_asset: Path = DEFAULT_TASK_CFG_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(task_cfg_asset.read_bytes()).root_constants()

    text_hints: list[dict[str, object]] = []
    for index, value in enumerate(constants):
        if not isinstance(value, str) or not _is_narrative_text(value):
            continue
        text_hints.append(
            {
                "constant_index": index,
                "task_id": _nearest_task_id(constants, index),
                "role": _text_role(value),
                "text": value,
                "nearby_stage_ids": list(_nearby_numbers(constants, index, _is_stage_id)),
                "nearby_npc_ids": list(_nearby_numbers(constants, index, _is_npc_id)),
                "drama_refs": list(_nearby_drama_refs(constants, index)),
            }
        )

    area_events: list[dict[str, object]] = []
    for index, value in enumerate(constants):
        if not isinstance(value, str):
            continue
        match = AREA_EVENT_RE.match(value)
        if not match:
            continue
        event_id = int(match.group("event_id"))
        area_events.append(
            {
                "constant_index": index,
                "event_id": event_id,
                "step": int(match.group("step")),
                "task_type": event_id // 10000,
                "condition_id": int(match.group("step")),
                "task_id": _nearest_task_id(constants, index),
                "description": _text_before(constants, index),
                "name": _text_after(constants, index),
                "nearby_stage_ids": list(_nearby_numbers(constants, index, _is_stage_id)),
                "nearby_npc_ids": list(_nearby_numbers(constants, index, _is_npc_id)),
                "drama_refs": list(_nearby_drama_refs(constants, index)),
            }
        )

    act_markers: list[dict[str, object]] = []
    for index, value in enumerate(constants):
        if isinstance(value, str) and value.startswith("act"):
            task_id = _nearest_task_id(constants, index)
            act_markers.append(
                {
                    "constant_index": index,
                    "marker": value,
                    "task_id": task_id,
                    "task_type": _task_type_from_task_id(task_id),
                    "previous_text": _text_before(constants, index),
                    "next_text": _text_after(constants, index),
                    "nearby_stage_ids": list(
                        _nearby_numbers(constants, index, _is_stage_id)
                    ),
                    "nearby_npc_ids": list(
                        _nearby_numbers(constants, index, _is_npc_id)
                    ),
                    "drama_refs": list(_nearby_drama_refs(constants, index)),
                }
            )

    act_tasks: list[dict[str, object]] = []
    seen_act_task_ids: set[int] = set()
    for item in act_markers:
        task_id = int(item["task_id"])
        marker = str(item["marker"])
        if task_id <= 0 or marker.startswith("act_event"):
            continue
        if task_id in seen_act_task_ids:
            continue
        seen_act_task_ids.add(task_id)
        act_tasks.append(
            {
                "constant_index": int(item["constant_index"]),
                "marker": marker,
                "task_id": task_id,
                "task_type": int(item["task_type"]),
                "label": str(item["previous_text"]),
                "objective": str(item["next_text"]),
                "nearby_stage_ids": list(item["nearby_stage_ids"]),
                "nearby_npc_ids": list(item["nearby_npc_ids"]),
                "drama_refs": list(item["drama_refs"]),
            }
        )

    quest_chain: list[dict[str, object]] = []
    for item in act_tasks:
        quest_chain.append(
            {
                "constant_index": int(item["constant_index"]),
                "kind": "act",
                "task_id": int(item["task_id"]),
                "task_type": int(item["task_type"]),
                "marker": str(item["marker"]),
                "label": str(item["label"]),
                "objective": str(item["objective"]),
                "nearby_stage_ids": list(item["nearby_stage_ids"]),
                "nearby_npc_ids": list(item["nearby_npc_ids"]),
                "drama_refs": list(item["drama_refs"]),
            }
        )
    for item in area_events:
        quest_chain.append(
            {
                "constant_index": int(item["constant_index"]),
                "kind": "area_event",
                "task_id": int(item["task_id"]),
                "task_type": int(item["task_type"]),
                "event_id": int(item["event_id"]),
                "condition_id": int(item["condition_id"]),
                "label": str(item["name"]),
                "objective": str(item["description"]),
                "nearby_stage_ids": list(item["nearby_stage_ids"]),
                "nearby_npc_ids": list(item["nearby_npc_ids"]),
                "drama_refs": list(item["drama_refs"]),
            }
        )
    quest_chain.sort(key=lambda item: int(item["constant_index"]))
    for order, item in enumerate(quest_chain, start=1):
        item["order"] = order
    for index, item in enumerate(quest_chain):
        previous_item = quest_chain[index - 1] if index > 0 else None
        next_item = quest_chain[index + 1] if index + 1 < len(quest_chain) else None
        item["previous_task_id"] = (
            int(previous_item["task_id"]) if previous_item is not None else 0
        )
        item["next_task_id"] = (
            int(next_item["task_id"]) if next_item is not None else 0
        )

    quest_chain_by_task_id = {
        int(item["task_id"]): item
        for item in quest_chain
        if int(item["task_id"]) > 0
    }
    quest_dialog_references: list[dict[str, object]] = []
    for item in text_hints:
        task_id = int(item["task_id"])
        chain_item = quest_chain_by_task_id.get(task_id)
        if chain_item is None:
            continue
        if not item["nearby_npc_ids"] or not _is_dialog_text(str(item["text"])):
            continue
        quest_dialog_references.append(
            {
                "constant_index": int(item["constant_index"]),
                "task_id": task_id,
                "quest_order": int(chain_item["order"]),
                "text": str(item["text"]),
                "nearby_stage_ids": list(item["nearby_stage_ids"]),
                "nearby_npc_ids": list(item["nearby_npc_ids"]),
                "drama_refs": list(item["drama_refs"]),
            }
        )

    return {
        "source": TASK_CFG_SOURCE,
        "constant_count": len(constants),
        "text_hint_count": len(text_hints),
        "area_event_count": len(area_events),
        "act_marker_count": len(act_markers),
        "act_task_count": len(act_tasks),
        "quest_chain_count": len(quest_chain),
        "quest_dialog_reference_count": len(quest_dialog_references),
        "text_hints": text_hints,
        "area_events": area_events,
        "act_markers": act_markers,
        "act_tasks": act_tasks,
        "quest_chain": quest_chain,
        "quest_dialog_references": quest_dialog_references,
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    text_hints = payload["text_hints"]
    area_events = payload["area_events"]
    act_markers = payload["act_markers"]
    act_tasks = payload["act_tasks"]
    quest_chain = payload["quest_chain"]
    quest_dialog_references = payload["quest_dialog_references"]
    return (
        "from __future__ import annotations\n\n"
        "TASK_CFG_HINT_SOURCE = "
        + repr(str(payload["source"]))
        + "\n"
        "TASK_CFG_CONSTANT_COUNT = "
        + repr(int(payload["constant_count"]))
        + "\n\n"
        "RECOVERED_TASK_TEXT_HINTS = "
        + pformat(text_hints, width=96, sort_dicts=False)
        + "\n\n"
        "RECOVERED_AREA_EVENT_TASKS = "
        + pformat(area_events, width=96, sort_dicts=False)
        + "\n\n"
        "RECOVERED_ACT_MARKERS = "
        + pformat(act_markers, width=96, sort_dicts=False)
        + "\n\n"
        "RECOVERED_ACT_TASKS = "
        + pformat(act_tasks, width=96, sort_dicts=False)
        + "\n\n"
        "RECOVERED_QUEST_CHAIN = "
        + pformat(quest_chain, width=96, sort_dicts=False)
        + "\n\n"
        "RECOVERED_QUEST_DIALOG_REFERENCES = "
        + pformat(quest_dialog_references, width=96, sort_dicts=False)
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover conservative quest/task ordering hints from task_cfg.lua."
    )
    parser.add_argument("task_cfg_asset", nargs="?", type=Path, default=DEFAULT_TASK_CFG_ASSET)
    parser.add_argument("--emit-python", action="store_true")
    args = parser.parse_args()

    payload = collect_task_cfg_hints(args.task_cfg_asset)
    if args.emit_python:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
