from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .beginner_quest import (
    STARTER_GUIDE_STEP,
    STARTER_TASK_CONDITION_ID,
    STARTER_TASK_ID,
    STARTER_TASK_TYPE,
)
from .area_event_stages import AREA_EVENT_STAGES
from .task_cfg_hints import (
    RECOVERED_ACT_TASKS,
    RECOVERED_AREA_EVENT_TASKS,
    RECOVERED_QUEST_CHAIN,
    RECOVERED_QUEST_DIALOG_REFERENCES as RECOVERED_QUEST_DIALOG_HINTS,
)
from .npc_cfg_hints import RECOVERED_NPC_NAME_HINTS
from .characters import MAP_CHARACTERS


TASK_STATUS_AVAILABLE = 1
TASK_STATUS_ACCEPTED = 2
TASK_STATUS_FINISHED = 3
STARTER_GUIDE_ID = STARTER_TASK_ID


@dataclass(slots=True)
class TaskCondition:
    id: int
    completed_count: int = 0
    params: tuple[int, ...] = ()

    def to_protocol(self) -> dict[str, object]:
        return {
            "Id": self.id,
            "CompCount": self.completed_count,
            "ParamList": list(self.params),
        }

    def clone(self) -> "TaskCondition":
        return TaskCondition(
            id=self.id,
            completed_count=self.completed_count,
            params=self.params,
        )


@dataclass(slots=True)
class TaskRecord:
    id: int
    type: int
    status: int = TASK_STATUS_AVAILABLE
    loop_times: int = 0
    conditions: tuple[TaskCondition, ...] = ()
    label: str = ""
    objective: str = ""
    source_event_id: int = 0
    source_stage_id: int = 0
    source_relate_stage_id: int = 0
    source_marker: str = ""
    source_kind: str = ""
    quest_order: int = 0
    previous_task_id: int = 0
    next_task_id: int = 0
    nearby_stage_ids: tuple[int, ...] = ()
    nearby_npc_ids: tuple[int, ...] = ()
    drama_refs: tuple[str, ...] = ()

    def to_protocol(self) -> dict[str, object]:
        return {
            "Id": self.id,
            "Type": self.type,
            "Status": self.status,
            "LoopTimes": self.loop_times,
            "Cond": [condition.to_protocol() for condition in self.conditions],
        }

    def clone(self) -> "TaskRecord":
        return TaskRecord(
            id=self.id,
            type=self.type,
            status=self.status,
            loop_times=self.loop_times,
            conditions=tuple(condition.clone() for condition in self.conditions),
            label=self.label,
            objective=self.objective,
            source_event_id=self.source_event_id,
            source_stage_id=self.source_stage_id,
            source_relate_stage_id=self.source_relate_stage_id,
            source_marker=self.source_marker,
            source_kind=self.source_kind,
            quest_order=self.quest_order,
            previous_task_id=self.previous_task_id,
            next_task_id=self.next_task_id,
            nearby_stage_ids=self.nearby_stage_ids,
            nearby_npc_ids=self.nearby_npc_ids,
            drama_refs=self.drama_refs,
        )


@dataclass(frozen=True, slots=True)
class QuestNpcReference:
    npc_id: int
    task_id: int
    quest_order: int
    label: str
    objective: str
    drama_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class QuestDialogReference:
    npc_id: int
    task_id: int
    quest_order: int
    text: str
    resolved_npc_ids: tuple[int, ...] = ()
    resolved_npc_names: tuple[str, ...] = ()
    nearby_stage_ids: tuple[int, ...] = ()
    drama_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class QuestContactCandidate:
    task_id: int
    quest_order: int
    text: str
    raw_npc_ids: tuple[int, ...]
    resolved_npc_ids: tuple[int, ...]
    resolved_npc_names: tuple[str, ...]
    scene_npc_ids: tuple[int, ...] = ()
    placement_verified: bool = False
    nearby_stage_ids: tuple[int, ...] = ()
    drama_refs: tuple[str, ...] = ()

    @property
    def has_scene_npc_rows(self) -> bool:
        return bool(self.scene_npc_ids)

    @property
    def can_spawn_on_map(self) -> bool:
        return self.has_scene_npc_rows and self.placement_verified


class TaskState:
    def __init__(self) -> None:
        self.tasks: dict[int, TaskRecord] = {
            STARTER_TASK.id: STARTER_TASK.clone(),
            **{
                task.id: task.clone()
                for task in RECOVERED_AREA_EVENT_TASKS_BY_ID.values()
            },
            **{task.id: task.clone() for task in RECOVERED_ACT_TASKS_BY_ID.values()},
        }
        self.finished: set[int] = set()
        self.spawned_task_npcs: set[int] = set()
        self.spawned_contact_task_npcs: set[int] = set()

    def task_info(self, task_type: int | None = None) -> dict[str, object]:
        tasks = [
            task.to_protocol()
            for task in sorted(self.tasks.values(), key=_task_sort_key)
            if task_type in (None, 0, task.type) and self._is_visible(task)
        ]
        return {
            "tasks": tasks,
            "finishs": sorted(self.finished),
            "IsStart": 1,
            "IsEnd": 1,
        }

    def accept(self, task_id: int) -> dict[str, object]:
        task = self._task(task_id)
        task.status = TASK_STATUS_ACCEPTED
        return self.task_update(task, action_type=1)

    def submit(self, task_id: int) -> dict[str, object]:
        task = self._task(task_id)
        self._finish(task)
        return self.task_update(task, action_type=2)

    def complete_guide(self, guide_id: int) -> dict[str, object] | None:
        if guide_id != STARTER_GUIDE_ID:
            return None
        task = self._task(STARTER_TASK.id)
        if task.id in self.finished:
            return None
        for condition in task.conditions:
            if guide_id in condition.params:
                condition.completed_count = max(condition.completed_count, 1)
        self._finish(task)
        return self.task_update(task, action_type=2)

    def observe_client_stat(self, stat: dict[str, object]) -> dict[str, object] | None:
        nums = list(stat.get("NumData") or [])
        if len(nums) < 3:
            return None
        flag, guide_id, step = (int(nums[0]), int(nums[1]), int(nums[2]))
        if flag != 1 or guide_id != STARTER_GUIDE_ID or step != STARTER_GUIDE_STEP:
            return None
        return self.complete_guide(guide_id)

    def complete_area_event_stage(self, stage_id: int) -> dict[str, object] | None:
        task = RECOVERED_AREA_EVENT_TASK_BY_STAGE_TOKEN.get(int(stage_id))
        if task is None:
            return None
        live_task = self._task(task.id)
        if live_task.id in self.finished:
            return None
        for condition in live_task.conditions:
            condition.completed_count = max(condition.completed_count, 1)
        self._finish(live_task)
        return self.task_update(live_task, action_type=2)

    def seed_completed_area_event_stages(
        self, stage_ids: Iterable[int]
    ) -> None:
        for stage_id in stage_ids:
            task = RECOVERED_AREA_EVENT_TASK_BY_STAGE_TOKEN.get(int(stage_id))
            if task is None:
                continue
            live_task = self._task(task.id)
            for condition in live_task.conditions:
                condition.completed_count = max(condition.completed_count, 1)
            self._finish(live_task)

    def seed_finished_tasks(self, task_ids: Iterable[int]) -> None:
        for task_id in task_ids:
            task = self._task(int(task_id))
            for condition in task.conditions:
                condition.completed_count = max(condition.completed_count, 1)
            self._finish(task)

    def should_spawn_beginner_npc(self, task_id: int) -> bool:
        if task_id != STARTER_TASK.id:
            return False
        if task_id in self.finished or task_id in self.spawned_task_npcs:
            return False
        self.spawned_task_npcs.add(task_id)
        return True

    def skip_starter_quest(self) -> None:
        task = self._task(STARTER_TASK.id)
        for condition in task.conditions:
            condition.completed_count = max(condition.completed_count, 1)
        self._finish(task)

    def sync_info(
        self, task_id: int, sync_type: str, params: list[str]
    ) -> dict[str, object]:
        return {
            "TaskId": task_id,
            "Type": sync_type,
            "ParamList": params,
        }

    def complete_active_quest_contact(self, task_id: int) -> dict[str, object] | None:
        task = self.tasks.get(int(task_id))
        if task is None or task.id in self.finished:
            return None
        if task.quest_order <= 0 or not self._is_visible(task):
            return None
        if task.id not in RECOVERED_QUEST_CONTACT_CANDIDATES_BY_TASK_ID:
            return None
        self._finish(task)
        return self.task_update(task, action_type=2)

    def complete_active_quest_contact_from_sync(
        self, task_id: int, params: Iterable[object]
    ) -> dict[str, object] | None:
        update = self.complete_active_quest_contact(task_id)
        if update is not None:
            return update
        npc_ids = _safe_int_set(params)
        if not npc_ids:
            return None
        for candidate in self.active_quest_contact_candidates():
            candidate_ids = (
                set(candidate.raw_npc_ids)
                | set(candidate.resolved_npc_ids)
                | set(candidate.scene_npc_ids)
            )
            if not (candidate_ids & npc_ids):
                continue
            task = self.tasks.get(candidate.task_id)
            if task is None or task.id in self.finished:
                continue
            self._finish(task)
            return self.task_update(task, action_type=2)
        return None

    def area_event_stage_id_for_task(self, task_id: int) -> int:
        task = self.tasks.get(int(task_id))
        if task is None or task.source_kind != "area_event":
            return 0
        return int(task.source_stage_id)

    def canonical_area_event_stage_id(self, stage_id: int) -> int:
        task = RECOVERED_AREA_EVENT_TASK_BY_STAGE_TOKEN.get(int(stage_id))
        if task is None:
            return int(stage_id)
        return int(task.source_stage_id)

    def area_event_id_for_stage(self, stage_id: int) -> int:
        task = RECOVERED_AREA_EVENT_TASK_BY_STAGE_TOKEN.get(int(stage_id))
        if task is None:
            return 0
        return int(task.source_event_id)

    def complete_active_base_station_task(self) -> dict[str, object] | None:
        task = self._active_base_station_task()
        if task is None:
            return None
        self._finish(task)
        return self.task_update(task, action_type=2)

    def complete_active_act_task(self, task_id: int) -> dict[str, object] | None:
        task = self.tasks.get(int(task_id))
        if task is None or task.id in self.finished:
            return None
        if task.source_kind != "act" or task.quest_order <= 0:
            return None
        if not self._is_visible(task):
            return None
        self._finish(task)
        return self.task_update(task, action_type=2)

    def complete_auto_act_gates(self) -> list[dict[str, object]]:
        updates: list[dict[str, object]] = []
        while True:
            task = self._active_auto_act_gate()
            if task is None:
                break
            self._finish(task)
            updates.append(self.task_update(task, action_type=2))
        return updates

    def enter_stage(self, is_enter: int) -> dict[str, object]:
        return {"IsEnter": is_enter}

    def task_update(self, task: TaskRecord, action_type: int) -> dict[str, object]:
        return {
            "action_type": action_type,
            "task_info": task.to_protocol(),
            "Reward": [],
            "RewardRate": 0,
        }

    def should_refresh_progression_list(self, task_id: int) -> bool:
        task = self.tasks.get(int(task_id))
        return task is not None and (
            task.id == STARTER_TASK.id or task.quest_order > 0
        )

    def active_quest_dialog_references(
        self,
    ) -> tuple[QuestDialogReference, ...]:
        active_task_ids = {
            task.id
            for task in self.tasks.values()
            if task.id not in self.finished
            and task.quest_order > 0
            and self._is_visible(task)
        }
        return tuple(
            reference
            for reference in RECOVERED_QUEST_DIALOG_REFERENCES
            if reference.task_id in active_task_ids
        )

    def active_quest_contact_candidates(
        self,
    ) -> tuple[QuestContactCandidate, ...]:
        active_task_ids = {
            task.id
            for task in self.tasks.values()
            if task.id not in self.finished
            and task.quest_order > 0
            and self._is_visible(task)
        }
        return tuple(
            candidate
            for candidate in RECOVERED_QUEST_CONTACT_CANDIDATES
            if candidate.task_id in active_task_ids
        )

    def claim_active_quest_contact_spawn_candidates(
        self,
    ) -> tuple[QuestContactCandidate, ...]:
        candidates = tuple(
            candidate
            for candidate in self.active_quest_contact_candidates()
            if candidate.scene_npc_ids
            and candidate.task_id not in self.spawned_contact_task_npcs
        )
        self.spawned_contact_task_npcs.update(
            candidate.task_id for candidate in candidates
        )
        return candidates

    def _task(self, task_id: int) -> TaskRecord:
        task = self.tasks.get(task_id)
        if task is None:
            task = TaskRecord(id=task_id, type=0, status=TASK_STATUS_AVAILABLE)
            self.tasks[task_id] = task
        return task

    def _finish(self, task: TaskRecord) -> None:
        for predecessor in self._unfinished_chain_predecessors(task):
            self._finish_one(predecessor)
        self._finish_one(task)

    def _finish_one(self, task: TaskRecord) -> None:
        for condition in task.conditions:
            condition.completed_count = max(condition.completed_count, 1)
        task.status = TASK_STATUS_FINISHED
        self.finished.add(task.id)

    def _unfinished_chain_predecessors(
        self, task: TaskRecord
    ) -> tuple[TaskRecord, ...]:
        predecessors: list[TaskRecord] = []
        seen = {task.id}
        previous_id = task.previous_task_id
        while previous_id:
            if previous_id in seen or previous_id in self.finished:
                break
            seen.add(previous_id)
            previous = self.tasks.get(previous_id)
            if previous is None:
                break
            predecessors.append(previous)
            previous_id = previous.previous_task_id
        return tuple(reversed(predecessors))

    def _is_visible(self, task: TaskRecord) -> bool:
        if task.id == STARTER_TASK.id or task.id in self.finished:
            return True
        if task.quest_order <= 0:
            return True
        if STARTER_TASK.id not in self.finished:
            return False
        return task.previous_task_id == 0 or task.previous_task_id in self.finished

    def _active_base_station_task(self) -> TaskRecord | None:
        candidates = sorted(
            (
                task
                for task in self.tasks.values()
                if task.id not in self.finished
                and task.source_kind == "act"
                and task.quest_order > 0
                and self._is_visible(task)
                and (
                    "\u57fa\u7ad9" in task.objective
                    or "\u8ba4\u8bc1" in task.objective
                )
            ),
            key=lambda task: (task.quest_order, task.id),
        )
        return candidates[0] if candidates else None

    def _active_auto_act_gate(self) -> TaskRecord | None:
        candidates = sorted(
            (
                task
                for task in self.tasks.values()
                if task.id not in self.finished
                and task.source_kind == "act"
                and task.quest_order > 0
                and not task.objective.strip()
                and self._is_visible(task)
            ),
            key=lambda task: (task.quest_order, task.id),
        )
        return candidates[0] if candidates else None


def _int_tuple(value: object) -> tuple[int, ...]:
    return tuple(int(item) for item in list(value or []))


def _safe_int_set(value: Iterable[object]) -> set[int]:
    result: set[int] = set()
    for item in value:
        try:
            result.add(int(item))
        except (TypeError, ValueError):
            continue
    return result


def _str_tuple(value: object) -> tuple[str, ...]:
    return tuple(str(item) for item in list(value or []))


def _clean_npc_hint_text(value: str) -> str:
    text = value.strip()
    for prefix in (
        "\u5730\u56fe\u7cfb\u7edf_",
        "\u4e3b\u7ebf\u4efb\u52a1-",
        "\u4e3b\u7ebf\u590d\u7528-",
        "\u5267\u60c5\u590d\u7528-",
        "\u5267\u60c5\u590d\u7528_",
        "\u652f\u7ebf\u4e34\u65f6_",
        "\u652f\u7ebf_",
        "NPC-",
    ):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    text = text.split("\uff08", 1)[0]
    text = text.split("(", 1)[0]
    return text.strip()


def _clean_dialog_target_text(value: str) -> str:
    text = value.strip()
    for prefix in ("\u627e", "\u4e0e", "\u62dc\u8bbf"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    for suffix in ("\u8c08\u8bdd", "\u5427"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text.strip()


def _npc_hint_score(
    raw_hint_text: str,
    hint_text: str,
    target_text: str,
    dialog_text: str,
) -> int:
    if not hint_text:
        return 999
    if hint_text == target_text:
        score = 0
    elif hint_text in dialog_text:
        score = 2
    else:
        return 999
    if any(
        marker in raw_hint_text
        for marker in (
            "\u6536\u85cf\u7269",
            "\u85cf\u54c1",
            "\u652f\u7ebf",
            "\u4e34\u65f6",
            "\u63a2\u6d4b",
        )
    ):
        score += 5
    return score


def _resolve_dialog_npc_ids(text: str, raw_npc_ids: tuple[int, ...]) -> tuple[int, ...]:
    target_text = _clean_dialog_target_text(text)
    scored_candidates: list[tuple[int, tuple[int, ...]]] = []
    for hint in RECOVERED_NPC_NAME_HINTS:
        raw_hint_text = str(hint["text"])
        hint_text = _clean_npc_hint_text(raw_hint_text)
        if len(hint_text) < 2:
            continue
        score = _npc_hint_score(raw_hint_text, hint_text, target_text, text)
        if score >= 999:
            continue
        scored_candidates.append((score, _int_tuple(hint.get("nearest_npc_ids"))))
    if not scored_candidates:
        return raw_npc_ids
    best_score = min(score for score, _ in scored_candidates)
    candidates: list[int] = []
    for score, npc_ids in scored_candidates:
        if score != best_score:
            continue
        for npc_id in npc_ids:
            if npc_id not in candidates:
                candidates.append(npc_id)
    raw_matches = tuple(npc_id for npc_id in candidates if npc_id in raw_npc_ids)
    if raw_matches:
        return raw_matches
    if candidates:
        return tuple(candidates)
    return raw_npc_ids


def _resolve_dialog_npc_names(
    text: str,
    resolved_npc_ids: tuple[int, ...],
) -> tuple[str, ...]:
    if not resolved_npc_ids:
        return ()
    target_text = _clean_dialog_target_text(text)
    scored_names: list[tuple[int, str]] = []
    for hint in RECOVERED_NPC_NAME_HINTS:
        nearest_ids = _int_tuple(hint.get("nearest_npc_ids"))
        if not any(npc_id in resolved_npc_ids for npc_id in nearest_ids):
            continue
        raw_hint_text = str(hint["text"])
        hint_text = _clean_npc_hint_text(raw_hint_text)
        if len(hint_text) < 2:
            continue
        score = _npc_hint_score(raw_hint_text, hint_text, target_text, text)
        if score >= 999:
            continue
        scored_names.append((score, hint_text))
    if not scored_names:
        return ()
    best_score = min(score for score, _ in scored_names)
    output: list[str] = []
    for score, name in scored_names:
        if score == best_score and name not in output:
            output.append(name)
    return tuple(output)


def _scene_npc_ids_for_resolved_ids(
    resolved_npc_ids: tuple[int, ...],
) -> tuple[int, ...]:
    output: list[int] = []
    for npc_id in resolved_npc_ids:
        character = MAP_CHARACTERS.get(npc_id)
        if character is None or not character.is_spawn_verified:
            continue
        if character.npc_id is not None and character.npc_id not in output:
            output.append(character.npc_id)
    return tuple(output)


STARTER_TASK = TaskRecord(
    id=STARTER_GUIDE_ID,
    type=STARTER_TASK_TYPE,
    status=TASK_STATUS_AVAILABLE,
    conditions=(
        TaskCondition(
            id=STARTER_TASK_CONDITION_ID,
            completed_count=0,
            params=(STARTER_GUIDE_ID, STARTER_GUIDE_STEP),
        ),
    ),
)


QUEST_CHAIN_ORDER_BY_ACT_MARKER = {
    str(item["marker"]): int(item["order"])
    for item in RECOVERED_QUEST_CHAIN
    if item.get("kind") == "act"
}
QUEST_CHAIN_ORDER_BY_AREA_EVENT_ID = {
    int(item["event_id"]): int(item["order"])
    for item in RECOVERED_QUEST_CHAIN
    if item.get("kind") == "area_event"
}
QUEST_CHAIN_BY_ACT_MARKER = {
    str(item["marker"]): item
    for item in RECOVERED_QUEST_CHAIN
    if item.get("kind") == "act"
}
QUEST_CHAIN_BY_AREA_EVENT_ID = {
    int(item["event_id"]): item
    for item in RECOVERED_QUEST_CHAIN
    if item.get("kind") == "area_event"
}


def _recovered_area_event_task_records() -> tuple[TaskRecord, ...]:
    records: list[TaskRecord] = []
    for task_hint, stage in zip(RECOVERED_AREA_EVENT_TASKS, AREA_EVENT_STAGES):
        task_id = int(task_hint["task_id"] or task_hint["event_id"])
        event_id = int(task_hint["event_id"])
        relate_stage = int(stage.relate_stage)
        chain_item = QUEST_CHAIN_BY_AREA_EVENT_ID.get(event_id, {})
        params = tuple(
            value
            for value in (int(stage.stage_id), event_id, relate_stage)
            if value
        )
        records.append(
            TaskRecord(
                id=task_id,
                type=int(task_hint["task_type"]),
                status=TASK_STATUS_AVAILABLE,
                conditions=(
                    TaskCondition(
                        id=int(task_hint["condition_id"]),
                        completed_count=0,
                        params=params,
                    ),
                ),
                label=str(task_hint["name"]),
                objective=str(task_hint["description"]),
                source_event_id=event_id,
                source_stage_id=int(stage.stage_id),
                source_relate_stage_id=relate_stage,
                source_kind="area_event",
                quest_order=int(chain_item.get("order") or 0),
                previous_task_id=int(chain_item.get("previous_task_id") or 0),
                next_task_id=int(chain_item.get("next_task_id") or 0),
                nearby_stage_ids=_int_tuple(task_hint.get("nearby_stage_ids")),
                nearby_npc_ids=_int_tuple(task_hint.get("nearby_npc_ids")),
                drama_refs=_str_tuple(task_hint.get("drama_refs")),
            )
        )
    return tuple(records)


RECOVERED_AREA_EVENT_TASK_RECORDS = _recovered_area_event_task_records()
RECOVERED_AREA_EVENT_TASK_TYPE = (
    RECOVERED_AREA_EVENT_TASK_RECORDS[0].type
    if RECOVERED_AREA_EVENT_TASK_RECORDS
    else 0
)
RECOVERED_AREA_EVENT_TASKS_BY_ID = {
    task.id: task for task in RECOVERED_AREA_EVENT_TASK_RECORDS
}
RECOVERED_AREA_EVENT_TASK_BY_STAGE_ID = {
    stage.stage_id: task
    for task, stage in zip(RECOVERED_AREA_EVENT_TASK_RECORDS, AREA_EVENT_STAGES)
}
RECOVERED_AREA_EVENT_TASK_BY_STAGE_TOKEN = {
    token: task
    for task in RECOVERED_AREA_EVENT_TASK_RECORDS
    for condition in task.conditions
    for token in condition.params
}
RECOVERED_AREA_EVENT_TASK_ORDER = {
    task.id: index for index, task in enumerate(RECOVERED_AREA_EVENT_TASK_RECORDS)
}


def _recovered_act_task_records() -> tuple[TaskRecord, ...]:
    records: list[TaskRecord] = []
    for task_hint in RECOVERED_ACT_TASKS:
        marker = str(task_hint["marker"])
        chain_item = QUEST_CHAIN_BY_ACT_MARKER.get(marker, {})
        records.append(
            TaskRecord(
                id=int(task_hint["task_id"]),
                type=int(task_hint["task_type"]),
                status=TASK_STATUS_AVAILABLE,
                conditions=(),
                label=str(task_hint["label"]),
                objective=str(task_hint["objective"]),
                source_marker=marker,
                source_kind="act",
                quest_order=int(chain_item.get("order") or 0),
                previous_task_id=int(chain_item.get("previous_task_id") or 0),
                next_task_id=int(chain_item.get("next_task_id") or 0),
                nearby_stage_ids=_int_tuple(task_hint.get("nearby_stage_ids")),
                nearby_npc_ids=_int_tuple(task_hint.get("nearby_npc_ids")),
                drama_refs=_str_tuple(task_hint.get("drama_refs")),
            )
        )
    return tuple(records)


RECOVERED_ACT_TASK_RECORDS = _recovered_act_task_records()
RECOVERED_ACT_TASKS_BY_ID = {task.id: task for task in RECOVERED_ACT_TASK_RECORDS}
RECOVERED_ACT_TASK_ORDER = {
    task.id: index for index, task in enumerate(RECOVERED_ACT_TASK_RECORDS)
}


def _recovered_quest_npc_references() -> tuple[QuestNpcReference, ...]:
    references: list[QuestNpcReference] = []
    tasks = sorted(
        (*RECOVERED_ACT_TASK_RECORDS, *RECOVERED_AREA_EVENT_TASK_RECORDS),
        key=lambda task: (task.quest_order or 999999, task.id),
    )
    for task in tasks:
        if task.quest_order <= 0:
            continue
        for npc_id in task.nearby_npc_ids:
            references.append(
                QuestNpcReference(
                    npc_id=int(npc_id),
                    task_id=task.id,
                    quest_order=task.quest_order,
                    label=task.label,
                    objective=task.objective,
                    drama_refs=task.drama_refs,
                )
            )
    return tuple(references)


RECOVERED_QUEST_NPC_REFERENCES = _recovered_quest_npc_references()
RECOVERED_QUEST_NPC_REFERENCES_BY_NPC_ID: dict[int, tuple[QuestNpcReference, ...]] = {
    npc_id: tuple(
        reference
        for reference in RECOVERED_QUEST_NPC_REFERENCES
        if reference.npc_id == npc_id
    )
    for npc_id in sorted({reference.npc_id for reference in RECOVERED_QUEST_NPC_REFERENCES})
}


def _recovered_quest_dialog_references() -> tuple[QuestDialogReference, ...]:
    references: list[QuestDialogReference] = []
    for item in RECOVERED_QUEST_DIALOG_HINTS:
        text = str(item["text"])
        raw_npc_ids = _int_tuple(item.get("nearby_npc_ids"))
        resolved_npc_ids = _resolve_dialog_npc_ids(text, raw_npc_ids)
        for npc_id in _int_tuple(item.get("nearby_npc_ids")):
            references.append(
                QuestDialogReference(
                    npc_id=npc_id,
                    task_id=int(item["task_id"]),
                    quest_order=int(item["quest_order"]),
                    text=text,
                    resolved_npc_ids=resolved_npc_ids,
                    resolved_npc_names=_resolve_dialog_npc_names(
                        text,
                        resolved_npc_ids,
                    ),
                    nearby_stage_ids=_int_tuple(item.get("nearby_stage_ids")),
                    drama_refs=_str_tuple(item.get("drama_refs")),
                )
            )
    return tuple(references)


RECOVERED_QUEST_DIALOG_REFERENCES = _recovered_quest_dialog_references()
RECOVERED_QUEST_DIALOG_REFERENCES_BY_NPC_ID: dict[
    int, tuple[QuestDialogReference, ...]
] = {
    npc_id: tuple(
        reference
        for reference in RECOVERED_QUEST_DIALOG_REFERENCES
        if reference.npc_id == npc_id
    )
    for npc_id in sorted(
        {reference.npc_id for reference in RECOVERED_QUEST_DIALOG_REFERENCES}
    )
}
RECOVERED_QUEST_DIALOG_REFERENCES_BY_TASK_ID: dict[
    int, tuple[QuestDialogReference, ...]
] = {
    task_id: tuple(
        reference
        for reference in RECOVERED_QUEST_DIALOG_REFERENCES
        if reference.task_id == task_id
    )
    for task_id in sorted(
        {reference.task_id for reference in RECOVERED_QUEST_DIALOG_REFERENCES}
    )
}
RECOVERED_QUEST_DIALOG_REFERENCES_BY_RESOLVED_NPC_ID: dict[
    int, tuple[QuestDialogReference, ...]
] = {
    npc_id: tuple(
        reference
        for reference in RECOVERED_QUEST_DIALOG_REFERENCES
        if npc_id in reference.resolved_npc_ids
    )
    for npc_id in sorted(
        {
            npc_id
            for reference in RECOVERED_QUEST_DIALOG_REFERENCES
            for npc_id in reference.resolved_npc_ids
        }
    )
}


def _recovered_quest_contact_candidates() -> tuple[QuestContactCandidate, ...]:
    candidates: list[QuestContactCandidate] = []
    seen: set[tuple[int, str]] = set()
    for reference in RECOVERED_QUEST_DIALOG_REFERENCES:
        key = (reference.task_id, reference.text)
        if key in seen:
            continue
        seen.add(key)
        raw_npc_ids = tuple(
            item.npc_id
            for item in RECOVERED_QUEST_DIALOG_REFERENCES
            if item.task_id == reference.task_id and item.text == reference.text
        )
        candidates.append(
            QuestContactCandidate(
                task_id=reference.task_id,
                quest_order=reference.quest_order,
                text=reference.text,
                raw_npc_ids=raw_npc_ids,
                resolved_npc_ids=reference.resolved_npc_ids,
                resolved_npc_names=reference.resolved_npc_names,
                scene_npc_ids=_scene_npc_ids_for_resolved_ids(
                    reference.resolved_npc_ids,
                ),
                placement_verified=False,
                nearby_stage_ids=reference.nearby_stage_ids,
                drama_refs=reference.drama_refs,
            )
        )
    return tuple(candidates)


RECOVERED_QUEST_CONTACT_CANDIDATES = _recovered_quest_contact_candidates()
RECOVERED_QUEST_CONTACT_CANDIDATES_BY_TASK_ID: dict[
    int, tuple[QuestContactCandidate, ...]
] = {
    task_id: tuple(
        candidate
        for candidate in RECOVERED_QUEST_CONTACT_CANDIDATES
        if candidate.task_id == task_id
    )
    for task_id in sorted(
        {candidate.task_id for candidate in RECOVERED_QUEST_CONTACT_CANDIDATES}
    )
}


def _task_sort_key(task: TaskRecord) -> tuple[int, int]:
    if task.id == STARTER_TASK.id:
        return (0, task.id)
    if task.quest_order > 0:
        return (1, task.quest_order)
    act_task_order = RECOVERED_ACT_TASK_ORDER.get(task.id)
    if act_task_order is not None:
        return (2, act_task_order)
    area_event_order = RECOVERED_AREA_EVENT_TASK_ORDER.get(task.id)
    if area_event_order is not None:
        return (3, area_event_order)
    return (4, task.id)
