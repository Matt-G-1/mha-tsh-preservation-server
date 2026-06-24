from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_CAMPAIGN_ID = 1


@dataclass(slots=True)
class CampaignTask:
    task_id: int
    status: int = 1
    comp_count: int = 0

    def to_protocol(self) -> dict[str, object]:
        return {
            "Id": self.task_id,
            "Status": self.status,
            "Cond": [{"CompCount": self.comp_count}],
        }


@dataclass(slots=True)
class CampaignState:
    campaign_id: int = DEFAULT_CAMPAIGN_ID
    entered: bool = False
    has_cache: bool = False
    control_uid: int = 0
    scene_id: int = 1000
    position: list[int] = field(default_factory=lambda: [4221, 19931, 0])
    detected_triggers: dict[int, set[int]] = field(default_factory=dict)
    seen_triggers: dict[int, set[int]] = field(default_factory=dict)
    finished_triggers: dict[int, set[int]] = field(default_factory=dict)
    tasks: dict[int, CampaignTask] = field(default_factory=dict)
    finished_tasks: set[int] = field(default_factory=set)
    selected_buffs: list[int] = field(default_factory=list)
    buffs: list[int] = field(default_factory=list)
    drama_indices: set[int] = field(default_factory=set)
    shop_buys: dict[tuple[int, int], int] = field(default_factory=dict)

    def data_list(self) -> dict[str, object]:
        return {
            "Data": [
                {
                    "CampaignId": self.campaign_id,
                    "Cache": 1 if self.has_cache else 0,
                    "FinishTrigger": self._finish_trigger_protocol(),
                    "FinishTask": sorted(self.finished_tasks),
                    "EnterFlag": 1,
                }
            ]
        }

    def enter(self, campaign_id: int) -> dict[str, object]:
        if campaign_id > 0:
            self.campaign_id = campaign_id
        self.entered = True
        self.has_cache = True
        return self.internal_status()

    def leave(self) -> None:
        self.entered = False

    def clear_cache(self) -> dict[str, object]:
        self.has_cache = False
        return {
            "CampaignId": self.campaign_id,
            "HasCache": 0,
        }

    def update_control(self, control_uid: int) -> dict[str, object]:
        self.control_uid = max(0, int(control_uid))
        return self.internal_status()

    def update_position(self, user_pos: dict[str, object]) -> None:
        self.scene_id = int(user_pos.get("SceneId") or self.scene_id)
        raw_pos = list(user_pos.get("Pos") or self.position)
        self.position = [int(item) for item in raw_pos[:3]]
        while len(self.position) < 3:
            self.position.append(0)

    def mark_trigger_on(self, field_id: int, area_id: int) -> dict[str, int]:
        self._trigger_set(self.detected_triggers, field_id).add(area_id)
        return {"FieldId": int(field_id), "AreaId": int(area_id)}

    def mark_trigger_seen(self, field_id: int, area_id: int) -> None:
        self._trigger_set(self.detected_triggers, field_id).add(area_id)
        self._trigger_set(self.seen_triggers, field_id).add(area_id)

    def mark_trigger_finished(self, field_id: int, area_id: int) -> dict[str, int]:
        self._trigger_set(self.detected_triggers, field_id).add(area_id)
        self._trigger_set(self.seen_triggers, field_id).add(area_id)
        self._trigger_set(self.finished_triggers, field_id).add(area_id)
        return {"FieldId": int(field_id), "AreaId": int(area_id)}

    def accept_task(self, task_id: int) -> dict[str, object]:
        task = self.tasks.setdefault(int(task_id), CampaignTask(int(task_id)))
        task.status = max(task.status, 1)
        return {"TaskInfo": task.to_protocol()}

    def update_task(self, task_id: int) -> dict[str, object]:
        task = self.tasks.setdefault(int(task_id), CampaignTask(int(task_id)))
        task.comp_count = max(task.comp_count, 1)
        task.status = max(task.status, 1)
        return {"TaskInfo": task.to_protocol()}

    def finish_task(self, task_id: int) -> dict[str, object]:
        task = self.tasks.setdefault(int(task_id), CampaignTask(int(task_id)))
        task.comp_count = max(task.comp_count, 1)
        task.status = 2
        self.finished_tasks.add(task.task_id)
        return {"Id": task.task_id, "Reward": []}

    def shop_info(self, shop_id: int) -> dict[str, object]:
        buys = [
            count
            for (saved_shop_id, _pos), count in sorted(self.shop_buys.items())
            if saved_shop_id == int(shop_id)
        ]
        return {
            "ShopId": int(shop_id),
            "Buff": [
                {"Pos": index + 1, "BuffId": buff_id}
                for index, buff_id in enumerate(self.buffs[:3])
            ],
            "BuyCount": buys,
        }

    def buy(self, shop_id: int, pos: int, count: int) -> dict[str, int]:
        key = (int(shop_id), int(pos))
        self.shop_buys[key] = self.shop_buys.get(key, 0) + max(1, int(count))
        return {
            "ShopId": int(shop_id),
            "Pos": int(pos),
            "Count": self.shop_buys[key],
        }

    def select_buff(self, index: int) -> dict[str, object]:
        normalized = int(index)
        if normalized not in self.selected_buffs:
            self.selected_buffs.append(normalized)
        return {"SelectBuff": list(self.selected_buffs)}

    def add_drama_index(self, drama_index: int) -> dict[str, object]:
        if drama_index > 0:
            self.drama_indices.add(int(drama_index))
        return self.internal_status()

    def internal_status(self) -> dict[str, object]:
        return {
            "CampaignId": self.campaign_id,
            "ControlUid": self.control_uid,
            "UserPos": {
                "SceneId": self.scene_id,
                "Pos": list(self.position),
            },
            "TriggerOnMap": self._trigger_on_map_protocol(),
            "HeroInfo": [],
            "Buff": list(self.buffs),
            "Property": [],
            "FinishTriggerList": self._finish_trigger_protocol(),
            "SelectBuff": list(self.selected_buffs),
            "TaskList": [
                task.to_protocol()
                for task in sorted(self.tasks.values(), key=lambda item: item.task_id)
            ],
            "FinishTask": sorted(self.finished_tasks),
            "DramaIndex": sorted(self.drama_indices),
        }

    @staticmethod
    def _trigger_set(groups: dict[int, set[int]], field_id: int) -> set[int]:
        return groups.setdefault(int(field_id), set())

    def _finish_trigger_protocol(self) -> list[dict[str, object]]:
        return [
            {
                "FieldId": field_id,
                "TriggerList": sorted(area_ids),
            }
            for field_id, area_ids in sorted(self.finished_triggers.items())
        ]

    def _trigger_on_map_protocol(self) -> list[dict[str, object]]:
        fields = set(self.detected_triggers) | set(self.seen_triggers)
        entries: list[dict[str, object]] = []
        for field_id in sorted(fields):
            area_ids = self.detected_triggers.get(field_id, set()) | self.seen_triggers.get(
                field_id, set()
            )
            entries.append(
                {
                    "FieldId": field_id,
                    "TriggerList": [
                        {
                            "AreaId": area_id,
                            "Detected": 1 if area_id in self.detected_triggers.get(field_id, set()) else 0,
                            "See": 1 if area_id in self.seen_triggers.get(field_id, set()) else 0,
                        }
                        for area_id in sorted(area_ids)
                    ],
                }
            )
        return entries
