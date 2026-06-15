from __future__ import annotations

from dataclasses import dataclass


TASK_STATUS_AVAILABLE = 1
TASK_STATUS_ACCEPTED = 2
TASK_STATUS_FINISHED = 3


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


class TaskState:
    def __init__(self) -> None:
        self.tasks: dict[int, TaskRecord] = {
            STARTER_TASK.id: TaskRecord(
                id=STARTER_TASK.id,
                type=STARTER_TASK.type,
                status=STARTER_TASK.status,
                loop_times=STARTER_TASK.loop_times,
                conditions=STARTER_TASK.conditions,
            )
        }
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
        task.status = TASK_STATUS_FINISHED
        self.finished.add(task.id)
        return self.task_update(task, action_type=2)

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


STARTER_TASK = TaskRecord(
    id=100001,
    type=1,
    status=TASK_STATUS_AVAILABLE,
    conditions=(TaskCondition(id=1, completed_count=0),),
)
