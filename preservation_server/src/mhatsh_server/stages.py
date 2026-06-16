from __future__ import annotations

from dataclasses import dataclass, field


STARTER_INTRO_STAGE_ID = 299301
STARTER_INTRO_STAGE_UID = 2993010001
STARTER_INTRO_STAGE_LEVEL = 1
STARTER_INTRO_STAGE_TIME = 300
STARTER_INTRO_STAGE_DRAMA = 1


@dataclass(slots=True)
class StageState:
    current_stage_id: int = 0
    current_stage_uid: int = 0
    finished_loading_count: int = 0
    reports: list[dict[str, object]] = field(default_factory=list)

    def enter_stage(
        self,
        stage_id: int = STARTER_INTRO_STAGE_ID,
        *,
        stage_uid: int = STARTER_INTRO_STAGE_UID,
        level: int = STARTER_INTRO_STAGE_LEVEL,
        time_limit: int = STARTER_INTRO_STAGE_TIME,
        drama: int = STARTER_INTRO_STAGE_DRAMA,
    ) -> dict[str, object]:
        self.current_stage_id = stage_id
        self.current_stage_uid = stage_uid
        return {
            "StageId": stage_id,
            "StageUid": stage_uid,
            "Level": level,
            "Time": time_limit,
            "Drama": drama,
            "IsReconnect": 0,
            "NeedLagLog": 0,
            "IsRecord": 0,
            "Extra": [],
        }

    def finish_loading(self, uid: int) -> dict[str, object]:
        self.finished_loading_count += 1
        return {"Uid": uid}

    def record_report(self, values: dict[str, object]) -> None:
        self.reports.append(dict(values))

    def empty_drop(self) -> dict[str, object]:
        return {
            "Monster": [],
            "Boss": [],
            "StagePassDrop": [],
            "Card": [],
            "VipCard": [],
            "FirstReward": [],
        }

    def result(self, result: int = 1) -> dict[str, object]:
        stage_id = self.current_stage_id or STARTER_INTRO_STAGE_ID
        return {
            "StageId": stage_id,
            "Result": result,
            "Time": 0,
            "RewardList": [],
            "StageInfo": [
                {
                    "Id": stage_id,
                    "Status": result,
                    "StarList": [],
                    "FullStarTime": 0,
                }
            ],
        }

    def end_gm(self, result: int = 1) -> dict[str, object]:
        return {"Result": result}
