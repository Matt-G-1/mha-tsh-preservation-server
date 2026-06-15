from __future__ import annotations

from dataclasses import dataclass


TASK_STATUS_AVAILABLE = 1
TASK_STATUS_ACCEPTED = 2
TASK_STATUS_FINISHED = 3
STARTER_GUIDE_ID = 1301
STARTER_GUIDE_STEP = 10011


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
        )


class TaskState:
    def __init__(self) -> None:
        self.tasks: dict[int, TaskRecord] = {STARTER_TASK.id: STARTER_TASK.clone()}
        self.finished: set[int] = set()

    def task_info(self, task_type: int | None = None) -> dict[str, object]:
        tasks = [
            task.to_protocol()
            for task in sorted(self.tasks.values(), key=lambda item: item.id)
            if task_type in (None, 0, task.type)
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

    def sync_info(
        self, task_id: int, sync_type: str, params: list[str]
    ) -> dict[str, object]:
        return {
            "TaskId": task_id,
            "Type": sync_type,
            "ParamList": params,
        }

    def enter_stage(self, is_enter: int) -> dict[str, object]:
        return {"IsEnter": is_enter}

    def task_update(self, task: TaskRecord, action_type: int) -> dict[str, object]:
        return {
            "action_type": action_type,
            "task_info": task.to_protocol(),
            "Reward": [],
            "RewardRate": 0,
        }

    def _task(self, task_id: int) -> TaskRecord:
        task = self.tasks.get(task_id)
        if task is None:
            task = TaskRecord(id=task_id, type=0, status=TASK_STATUS_AVAILABLE)
            self.tasks[task_id] = task
        return task

    def _finish(self, task: TaskRecord) -> None:
        task.status = TASK_STATUS_FINISHED
        self.finished.add(task.id)


STARTER_TASK = TaskRecord(
    id=STARTER_GUIDE_ID,
    type=1,
    status=TASK_STATUS_AVAILABLE,
    conditions=(
        TaskCondition(
            id=1,
            completed_count=0,
            params=(STARTER_GUIDE_ID, STARTER_GUIDE_STEP),
        ),
    ),
)
