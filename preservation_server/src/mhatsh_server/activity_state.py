from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ActivityState:
    requested_activity_types: list[int] = field(default_factory=list)
    requested_group_maps: int = 0
    entrust_list_version: int = 1

    def stage_activity_info(self) -> dict[str, object]:
        return {"ProgressInfo": []}

    def activity_shop_info(self, act_type: int) -> dict[str, object]:
        if act_type not in self.requested_activity_types:
            self.requested_activity_types.append(act_type)
        return {"BuyInfo": []}

    def entrust_task_list(self) -> dict[str, object]:
        return {"Version": self.entrust_list_version, "EntrustTaskData": []}

    def secret_area_task(self) -> dict[str, object]:
        return {"TaskList": []}

    def usj_task(self) -> dict[str, object]:
        return {"TaskList": []}

    def offlinepvp_task(self) -> dict[str, object]:
        return {"TaskList": []}

    def battlefield_task_info(self) -> dict[str, object]:
        return {
            "IsFightOver": 0,
            "IsGetDayReward": 0,
            "IsGetWeekReward": 0,
            "ReplaceTimes": 0,
            "FreshenTime": 0,
            "Tasks": [],
        }

    def group_open_map(self) -> dict[str, object]:
        self.requested_group_maps += 1
        return {"MapAttackArea": []}
