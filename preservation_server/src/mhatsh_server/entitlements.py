from __future__ import annotations

from dataclasses import dataclass, field

from .characters import SUPPORT_CARD_ITEM_IDS
from .stages import (
    LOCAL_STAGE_FIRST_REWARD_ITEM_ID,
    LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
    LOCAL_STAGE_PASS_REWARD_ITEM_ID,
    LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
)


PRESERVATION_CURRENCY_AMOUNT = 999_999_999
PRESERVATION_PERMANENT_END_TIME = 4_102_444_800
PRESERVATION_RECHARGE_VALUE = 999_999

PRESERVATION_SHOP_ITEMS = (
    LOCAL_STAGE_PASS_REWARD_ITEM_ID,
    LOCAL_STAGE_FIRST_REWARD_ITEM_ID,
    LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
    LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
)
PRESERVATION_SHOP_ITEM_AMOUNT = 99_999
PRESERVATION_WELFARE_SIGN_DAYS = tuple(range(1, 32))
PRESERVATION_TOTAL_LOGIN_REWARDS = tuple(range(1, 31))
PRESERVATION_STRENGTH_SUPPLIES = (1, 2, 3)
PRESERVATION_LEVEL_REWARDS = tuple(range(1, 71))
PRESERVATION_RECHARGE_REWARD_IDS = tuple(range(1, 21))


def preservation_seed_items() -> tuple[tuple[int, int], ...]:
    item_ids = sorted(
        {
            *PRESERVATION_SHOP_ITEMS,
            *SUPPORT_CARD_ITEM_IDS,
        }
    )
    return tuple(
        (item_id, PRESERVATION_SHOP_ITEM_AMOUNT)
        for item_id in item_ids
    )


@dataclass(slots=True)
class EntitlementState:
    shop_buys: dict[tuple[int, int], int] = field(default_factory=dict)
    activity_shop_buys: dict[tuple[int, int], int] = field(default_factory=dict)
    signed_types: set[int] = field(default_factory=set)
    claimed_total_login: set[int] = field(default_factory=set)
    claimed_strength_supply: set[int] = field(default_factory=set)
    claimed_recharge_totals: set[int] = field(default_factory=set)
    claimed_recharge_firsts: set[tuple[int, int]] = field(default_factory=set)

    def user_currency(self) -> dict[str, int]:
        return {
            "Gold": PRESERVATION_CURRENCY_AMOUNT,
            "BindGold": PRESERVATION_CURRENCY_AMOUNT,
        }

    def shop_info(self, shop_ids: list[int]) -> dict[str, object]:
        requested = [int(shop_id) for shop_id in shop_ids if int(shop_id) > 0]
        if not requested:
            requested = [1]
        return {
            "shopinfo": [
                {
                    "ShopId": shop_id,
                    "RefreshTime": 0,
                    "RefreshCount": 0,
                    "Goods": [
                        {
                            "GoodsId": self._goods_id(shop_id, index),
                            "ItemId": item_id,
                            "Amount": PRESERVATION_SHOP_ITEM_AMOUNT,
                            "Price": [0],
                            "PriceType": 0,
                            "Discount": [100],
                            "BuyTimes": self.shop_buys.get(
                                (shop_id, self._goods_id(shop_id, index)), 0
                            ),
                            "NumberList": [1, 10, 100],
                        }
                        for index, item_id in enumerate(
                            PRESERVATION_SHOP_ITEMS, start=1
                        )
                    ],
                }
                for shop_id in requested
            ]
        }

    def shop_buy(self, shop_id: int, goods_id: int, amount: int) -> dict[str, object]:
        normalized_shop_id = int(shop_id)
        normalized_goods_id = int(goods_id)
        count = max(1, int(amount))
        key = (normalized_shop_id, normalized_goods_id)
        self.shop_buys[key] = self.shop_buys.get(key, 0) + count
        return {
            "IsReturn": 1,
            "ItemInfo": [
                {
                    "ItemId": self._item_id_for_goods(normalized_shop_id, normalized_goods_id),
                    "Amount": count * PRESERVATION_SHOP_ITEM_AMOUNT,
                    "Uid": 0,
                }
            ],
            "ShopId": normalized_shop_id,
            "GoodsId": normalized_goods_id,
            "BuyTimes": self.shop_buys[key],
        }

    def activity_shop_info(self, act_type: int) -> dict[str, object]:
        numeric_act_type = int(act_type)
        return {
            "BuyInfo": [
                {
                    "GoodsId": self._goods_id(numeric_act_type or 1, index),
                    "BuyTimes": self.activity_shop_buys.get(
                        (numeric_act_type, self._goods_id(numeric_act_type or 1, index)),
                        0,
                    ),
                }
                for index, _item_id in enumerate(PRESERVATION_SHOP_ITEMS, start=1)
            ]
        }

    def welfare_info(self) -> dict[str, object]:
        return {
            "Exchange": PRESERVATION_CURRENCY_AMOUNT,
            "FixDay": 31,
            "SignList": list(PRESERVATION_WELFARE_SIGN_DAYS),
            "TotalLogin": list(PRESERVATION_TOTAL_LOGIN_REWARDS),
            "Strength": list(PRESERVATION_STRENGTH_SUPPLIES),
            "LevelRewards": list(PRESERVATION_LEVEL_REWARDS),
        }

    def welfare_sign(self, sign_type: int) -> dict[str, object]:
        numeric_sign_type = int(sign_type)
        self.signed_types.add(numeric_sign_type)
        return {
            "SignType": numeric_sign_type,
            "FixDay": 31,
            "SignList": list(PRESERVATION_WELFARE_SIGN_DAYS),
        }

    def welfare_total_login(self, reward_id: int) -> dict[str, object]:
        numeric_reward_id = int(reward_id)
        if numeric_reward_id > 0:
            self.claimed_total_login.add(numeric_reward_id)
        return {
            "Id": numeric_reward_id,
            "TotalLogin": sorted(
                self.claimed_total_login | set(PRESERVATION_TOTAL_LOGIN_REWARDS)
            ),
        }

    def welfare_strength_supply(self, reward_id: int) -> dict[str, object]:
        numeric_reward_id = int(reward_id)
        if numeric_reward_id > 0:
            self.claimed_strength_supply.add(numeric_reward_id)
        return {
            "Id": numeric_reward_id,
            "List": sorted(
                self.claimed_strength_supply | set(PRESERVATION_STRENGTH_SUPPLIES)
            ),
        }

    def welfare_exchange_money(self, exchange_type: int, times: int) -> dict[str, int]:
        return {
            "Type": int(exchange_type),
            "Count": max(1, int(times)),
            "Exchange": PRESERVATION_CURRENCY_AMOUNT,
            "TypeCount": PRESERVATION_CURRENCY_AMOUNT,
            "BoneCount": PRESERVATION_CURRENCY_AMOUNT,
        }

    def recharge_info(self) -> dict[str, int]:
        return {
            "RechargeCount": PRESERVATION_RECHARGE_VALUE,
            "RechargeValue": PRESERVATION_RECHARGE_VALUE,
            "RechargeGold": PRESERVATION_CURRENCY_AMOUNT,
        }

    def recharge_reward_info(self) -> dict[str, object]:
        return {
            "Once": [
                {"Id": reward_id, "State": 1}
                for reward_id in PRESERVATION_RECHARGE_REWARD_IDS
            ],
            "Total": [
                {"Id": reward_id, "State": 1}
                for reward_id in PRESERVATION_RECHARGE_REWARD_IDS
            ],
        }

    def recharge_reward_total_get(self, reward_id: int) -> dict[str, object]:
        numeric_reward_id = int(reward_id)
        if numeric_reward_id > 0:
            self.claimed_recharge_totals.add(numeric_reward_id)
        return {
            "List": [
                {"Id": reward_id, "State": 2}
                for reward_id in sorted(
                    self.claimed_recharge_totals | {numeric_reward_id}
                )
                if reward_id > 0
            ]
        }

    def recharge_reward_first_info(self) -> dict[str, object]:
        return {
            "Round": [
                {
                    "State": [2, 2, 2, 2, 2, 2, 2],
                    "GetTime": PRESERVATION_PERMANENT_END_TIME,
                }
            ]
        }

    @staticmethod
    def _goods_id(shop_id: int, index: int) -> int:
        return int(shop_id) * 1000 + int(index)

    @staticmethod
    def _item_id_for_goods(shop_id: int, goods_id: int) -> int:
        index = (int(goods_id) - int(shop_id) * 1000) - 1
        if 0 <= index < len(PRESERVATION_SHOP_ITEMS):
            return PRESERVATION_SHOP_ITEMS[index]
        return PRESERVATION_SHOP_ITEMS[0]
