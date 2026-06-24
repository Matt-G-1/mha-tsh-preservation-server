from __future__ import annotations

from dataclasses import dataclass

from .stages import (
    LOCAL_STAGE_FIRST_REWARD_ITEM_ID,
    LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
    LOCAL_STAGE_PASS_REWARD_ITEM_ID,
    LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
)


LOTTERY_EVIDENCE_SOURCE = (
    "allproto_readable.lua: c_lottery_load, s_lottery_draw, "
    "c_lottery_draw, s_lottery_choose_up, c_lottery_choose_up"
)

DEFAULT_DRAW_ID = 1
DEFAULT_UP_RATIO_ID = 0


@dataclass(slots=True)
class LotteryBanner:
    draw_id: int
    up_ratio_id: int = DEFAULT_UP_RATIO_ID
    have_draw: int = 1
    last_free_time: int = 0
    one_times: int = 0
    ten_times: int = 0

    def to_load_protocol(self) -> dict[str, int]:
        return {
            "DrawId": self.draw_id,
            "HaveDraw": self.have_draw,
            "LastFreeTime": self.last_free_time,
            "UpRatioId": self.up_ratio_id,
        }


class LotteryState:
    def __init__(self) -> None:
        self.banners = {DEFAULT_DRAW_ID: LotteryBanner(DEFAULT_DRAW_ID)}
        self.guarantee_progress: dict[int, int] = {}

    def load(self) -> dict[str, object]:
        return {
            "DrawInfo": [
                banner.to_load_protocol()
                for banner in sorted(
                    self.banners.values(), key=lambda item: item.draw_id
                )
            ],
            "GuaranteesInfo": self._guarantees_info(),
        }

    def choose_up(self, draw_id: int, up_ratio_id: int) -> dict[str, int]:
        banner = self._banner(draw_id)
        banner.up_ratio_id = max(0, int(up_ratio_id))
        return {"DrawId": banner.draw_id, "UpRatioId": banner.up_ratio_id}

    def draw(self, draw_id: int, times: int) -> dict[str, object]:
        banner = self._banner(draw_id)
        normalized_times = self._normalized_times(times)
        if normalized_times == 1:
            banner.one_times += 1
        elif normalized_times == 10:
            banner.ten_times += 1

        rewards = self._draw_rewards(banner.draw_id, normalized_times)
        for reward in rewards:
            important_id = int(reward["ItemId"])
            self.guarantee_progress[important_id] = (
                self.guarantee_progress.get(important_id, 0) + 1
            )

        return {
            "DrawId": banner.draw_id,
            "Times": normalized_times,
            "OneTimes": banner.one_times,
            "TenTimes": banner.ten_times,
            "RewardList": [
                {"AddLog": [reward], "IsImportant": int(index == 0)}
                for index, reward in enumerate(rewards)
            ],
            "GuaranteesInfo": self._guarantees_info(),
        }

    def _banner(self, draw_id: int) -> LotteryBanner:
        normalized_draw_id = int(draw_id) if int(draw_id) > 0 else DEFAULT_DRAW_ID
        return self.banners.setdefault(
            normalized_draw_id, LotteryBanner(normalized_draw_id)
        )

    @staticmethod
    def _normalized_times(times: int) -> int:
        return 10 if int(times) >= 10 else 1

    @staticmethod
    def _draw_rewards(draw_id: int, times: int) -> list[dict[str, object]]:
        reward_cycle = (
            LOCAL_STAGE_PASS_REWARD_ITEM_ID,
            LOCAL_STAGE_FIRST_REWARD_ITEM_ID,
            LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
            LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
        )
        return [
            {
                "ItemId": reward_cycle[(draw_id + index - 1) % len(reward_cycle)],
                "count": 1,
                "extra": [],
            }
            for index in range(times)
        ]

    def _guarantees_info(self) -> list[dict[str, object]]:
        return [
            {
                "GuaranteesType": 1,
                "ProcessInfo": [
                    {
                        "ImportantId": important_id,
                        "AccumulationTimes": times,
                    }
                    for important_id, times in sorted(
                        self.guarantee_progress.items()
                    )
                ],
            }
        ]
