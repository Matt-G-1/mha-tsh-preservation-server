from __future__ import annotations

from dataclasses import dataclass


SECRET_AREA_STAGE_SOURCE = (
    "phone_dump/apk_extract/assets/0QIU/e64de4e82ab94375, "
    "./script/setting/language/en/secret_area_cfg_new.lua, parsed 2026-06-24"
)
SECRET_AREA_GROUPS = (
    {"group_id": 11001, "group_name": "Town Nightraid"},
    {"group_id": 11002, "group_name": "Abandoned Chemical Plant"},
    {"group_id": 11003, "group_name": "Forest Training"},
)
SECRET_AREA_STAGE_IDS = (
    100101,
    100201,
    100301,
    100401,
    100501,
    100601,
    101101,
    101201,
    101301,
    101401,
    101501,
    101601,
    100102,
    100202,
    100302,
    100402,
    100502,
    100602,
    101102,
    101202,
    101302,
    101402,
    101502,
    101602,
    100103,
    100203,
    100303,
    100403,
    100503,
    100603,
    101103,
    101203,
    101303,
    101403,
    101503,
    101603,
    100104,
    100204,
    100304,
    100404,
    100504,
    100604,
    101104,
    101204,
    101304,
    101404,
    101504,
    101604,
    100105,
    100205,
    100305,
    100405,
    100505,
    100605,
    101105,
    101205,
    101305,
    101405,
    101505,
    101605,
    100106,
    100206,
    100306,
    100406,
    100506,
    100606,
    101106,
    101206,
    101306,
    101406,
    101506,
    101606,
    100107,
    100207,
    100307,
    100407,
    100507,
    100607,
    101107,
    101207,
    101307,
    101407,
    101507,
    101607,
    100508,
    100608,
    101508,
    101608,
)


@dataclass(frozen=True, slots=True)
class SecretAreaStageDefinition:
    stage_id: int
    level_range_id: int
    floor: int
    group_id: int = 11001
    group_name: str = "Secret Area"

    @property
    def label(self) -> str:
        return f"{self.group_name} {self.level_range_id} Floor {self.floor}"

    @property
    def key_id(self) -> int:
        return self.stage_id

    def as_history(
        self, *, waste_time: int = 0, reward_item_id: int = 1001
    ) -> dict[str, object]:
        return {
            "Time": int(waste_time),
            "StageGroupId": self.group_id,
            "StageLevel": self.level_range_id,
            "StageHierarchy": self.floor,
            "RewardList": [{"ItemId": reward_item_id, "Amount": 1}],
        }


SECRET_AREA_STAGES = tuple(
    SecretAreaStageDefinition(
        stage_id=stage_id,
        level_range_id=stage_id // 100,
        floor=stage_id % 100,
        group_name="Town Nightraid",
    )
    for stage_id in SECRET_AREA_STAGE_IDS
)
SECRET_AREA_STAGE_BY_ID = {stage.stage_id: stage for stage in SECRET_AREA_STAGES}
DEFAULT_SECRET_AREA_STAGE = SECRET_AREA_STAGES[0]
