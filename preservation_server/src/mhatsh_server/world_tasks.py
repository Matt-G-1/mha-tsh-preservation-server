from __future__ import annotations

from dataclasses import dataclass, field

from .beginner_quest import (
    BEGINNER_QUEST_CITY_EXP,
    BEGINNER_QUEST_CITY_LEVEL,
    STARTER_TASK_ID,
    STARTER_WORLD_AREA_ID,
    STARTER_WORLD_MAP_ID,
)

STARTER_CITY_LEVEL = 1


@dataclass(slots=True)
class WorldTaskState:
    open_world_maps: set[int] = field(
        default_factory=lambda: {STARTER_WORLD_MAP_ID}
    )
    city_level: int = STARTER_CITY_LEVEL
    city_exp: int = 0
    clicked_city_levels: set[int] = field(default_factory=set)
    reward_rate: int = 0
    ignore_auto_finish_tips: int = 0
    auto_finished_tasks: set[int] = field(default_factory=set)
    completed_beginner_quest: bool = False
    recovered_finished_tasks: set[int] = field(default_factory=set)

    def seed_unlocked(self, city_level: int) -> None:
        self.city_level = max(STARTER_CITY_LEVEL, int(city_level))
        self.city_exp = 0
        self.completed_beginner_quest = True

    def seed_recovered_finished_tasks(self, task_ids: set[int]) -> None:
        self.recovered_finished_tasks.update(
            int(task_id) for task_id in task_ids if int(task_id) > 0
        )
        if STARTER_TASK_ID in self.recovered_finished_tasks:
            self.completed_beginner_quest = True

    def city_level_info(self) -> dict[str, object]:
        return {
            "Level": self.city_level,
            "ClickList": sorted(self.clicked_city_levels),
        }

    def world_task_info(self) -> dict[str, object]:
        finished_task_ids = set(self.recovered_finished_tasks)
        if self.completed_beginner_quest:
            finished_task_ids.add(STARTER_TASK_ID)
        sorted_finished_task_ids = sorted(
            finished_task_ids,
            key=lambda task_id: (task_id != STARTER_TASK_ID, task_id),
        )[:0xFF]
        return {
            "FinishList": [
                {
                    "Map": STARTER_WORLD_MAP_ID,
                    "Area": STARTER_WORLD_AREA_ID,
                    "TaskId": task_id,
                }
                for task_id in sorted_finished_task_ids
            ]
            if finished_task_ids
            else [],
            "OpenWorldMap": [
                {"MapId": map_id} for map_id in sorted(self.open_world_maps)
            ],
            "PrestigeMap": 0,
            "PrestigeTaskStatus": 0,
            "IsFirstRewardSign": 0,
            "RewardBase": 0,
            "ExtraReward": [],
            "IgnoreAutoFinishTips": self.ignore_auto_finish_tips,
        }

    def city_level_click(self, level: int) -> dict[str, object]:
        if level > 0:
            self.clicked_city_levels.add(level)
        return {"Level": level}

    def complete_beginner_quest(self) -> list[tuple[str, dict[str, object]]]:
        if self.completed_beginner_quest:
            return []
        self.completed_beginner_quest = True
        self.city_exp += BEGINNER_QUEST_CITY_EXP
        if self.city_level < BEGINNER_QUEST_CITY_LEVEL:
            self.city_level = BEGINNER_QUEST_CITY_LEVEL
            return [
                ("c_city_level_add_exp", {"Exp": self.city_exp}),
                ("c_city_level_up", {"Level": self.city_level}),
                ("c_city_level_info", self.city_level_info()),
                ("c_world_task_info", self.world_task_info()),
            ]
        return [
            ("c_city_level_add_exp", {"Exp": self.city_exp}),
            ("c_city_level_info", self.city_level_info()),
            ("c_world_task_info", self.world_task_info()),
        ]

    def world_task_reward_rate(self, rate: int) -> dict[str, object]:
        self.reward_rate = max(0, rate)
        return {"Rate": self.reward_rate}

    def ignore_auto_finish_tips_response(self, flag: int) -> dict[str, object]:
        self.ignore_auto_finish_tips = 1 if flag else 0
        return {"Flag": self.ignore_auto_finish_tips}

    def auto_finish_response(self, task_id: int) -> dict[str, object]:
        if task_id > 0:
            self.auto_finished_tasks.add(task_id)
        return {"IsSuccess": 1}

    def pick_prestige_response(self) -> dict[str, object]:
        return {
            "IsSuccess": 1,
            "FixedReward": [],
            "RandomReward": [],
            "RandomItem": 0,
        }
