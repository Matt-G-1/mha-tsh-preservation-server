from __future__ import annotations

from dataclasses import dataclass, field

from .characters import SUPPORT_CARD_ITEM_IDS, support_card_book_entries
from .combat import fight_style_for_character
from .roster import RosterState


@dataclass(slots=True)
class CharacterMenuState:
    opened_show_ids: list[int] = field(default_factory=list)
    requested_area_lineups: list[tuple[int, tuple[int, ...]]] = field(
        default_factory=list
    )
    attached_card_slots: dict[int, dict[int, int]] = field(default_factory=dict)
    support_skill_slots: dict[int, dict[int, int]] = field(default_factory=dict)

    def card_show_info(self) -> dict[str, object]:
        active_cards = {
            attached_card_uid
            for slots in self.attached_card_slots.values()
            for attached_card_uid in slots.values()
            if attached_card_uid > 0
        }
        return {"ActiveAttachedCardIdList": sorted(active_cards)}

    def card_show_oper(self, card_id: int) -> dict[str, object]:
        if card_id not in self.opened_show_ids:
            self.opened_show_ids.append(card_id)
        return {"Id": card_id}

    def card_seeinfo(self, user_uid: int, roster: RosterState) -> dict[str, object]:
        return {"Uid": user_uid, "CardInfo": roster.card_info()}

    def card_hero_bio_info(self, roster: RosterState) -> dict[str, object]:
        return {
            "HeroBiographyList": [
                {"CardUid": card.card_uid, "BiographyIdList": []}
                for card in sorted(
                    roster.cards.values(), key=lambda item: item.card_uid
                )
            ]
        }

    def skill_level_list(
        self, requested_card_uids: list[int], roster: RosterState
    ) -> dict[str, object]:
        cards = self._requested_cards(requested_card_uids, roster)
        return {
            "SkillInfoList": [
                {
                    "HeroUid": card.card_uid,
                    "SkillLevelInfo": fight_style_for_character(
                        card.character
                    ).protocol_skill_levels(roster.hero_level),
                }
                for card in cards
            ]
        }

    def spec_level_list(
        self, requested_card_uids: list[int], roster: RosterState
    ) -> dict[str, object]:
        cards = self._requested_cards(requested_card_uids, roster)
        return {
            "SpecInfoList": [
                {"HeroUid": card.card_uid, "SpecLevelInfo": []} for card in cards
            ]
        }

    def skill_level(self, card_uid: int, roster: RosterState) -> dict[str, object]:
        card = roster.cards.get(card_uid)
        if card is None:
            return {"SkillInfo": {"HeroUid": card_uid, "SkillLevelInfo": []}}
        return {
            "SkillInfo": {
                "HeroUid": card_uid,
                "SkillLevelInfo": fight_style_for_character(
                    card.character
                ).protocol_skill_levels(roster.hero_level),
            }
        }

    def spec_level(self, card_uid: int) -> dict[str, object]:
        return {"SpecInfo": {"HeroUid": card_uid, "SpecLevelInfo": []}}

    def gem_list(self, hero_ids: list[int]) -> dict[str, object]:
        return {
            "Total": 0,
            "HeroGemData": [
                {"HeroCId": int(hero_id), "GemData": []}
                for hero_id in hero_ids
            ],
        }

    def toplist_pages(
        self,
        list_id: int,
        sub_name: int,
        page_numbers: list[int],
        self_uid: int,
        is_cross: int,
    ) -> dict[str, object]:
        return {
            "ID": list_id,
            "SubName": sub_name,
            "PageNums": page_numbers,
            "MaxPageNum": 0,
            "SelfUid": self_uid,
            "Pages": [],
            "SelfRankInfo": {"Rank": 0, "Number": [], "String": []},
            "IsCross": is_cross,
        }

    def hero_rank_info(self, roster: RosterState) -> dict[str, object]:
        return {
            "TotalStar": 0,
            "HeroStar": [
                {"Cid": card.hero_id, "Star": 0}
                for card in sorted(
                    roster.cards.values(), key=lambda item: item.card_uid
                )
            ],
            "TaskList": [],
            "LastStarId": 0,
            "LastStarState": 0,
            "BuffList": [],
        }

    def hero_class_info(self) -> dict[str, object]:
        return {"Idx": 0, "Id": 0, "Value": 0, "State": 0, "SkipCount": 0}

    def attached_card_info(self, roster: RosterState) -> dict[str, object]:
        return {
            "AttachedCardInfo": [
                {
                    "HeroId": card.hero_id,
                    "SlotInfo": [
                        {"Index": index, "ACardUid": attached_card_uid}
                        for index, attached_card_uid in sorted(
                            self.attached_card_slots.get(card.hero_id, {}).items()
                        )
                    ],
                }
                for card in sorted(
                    roster.cards.values(), key=lambda item: item.card_uid
                )
            ]
        }

    def attached_card_book(self) -> dict[str, object]:
        return {"Page": 0, "Book": support_card_book_entries()}

    def attached_card_oper(
        self,
        *,
        hero_id: int,
        index: int,
        oper: int,
        attached_card_uid: int,
        roster: RosterState,
    ) -> dict[str, object]:
        hero_id = int(hero_id)
        index = int(index)
        attached_card_uid = int(attached_card_uid)
        if index > 0:
            slots = self.attached_card_slots.setdefault(hero_id, {})
            if oper == 0 and attached_card_uid in SUPPORT_CARD_ITEM_IDS:
                slots[index] = attached_card_uid
            else:
                slots.pop(index, None)
            if not slots:
                self.attached_card_slots.pop(hero_id, None)
        return self.attached_card_info(roster)

    def card_support_skill(
        self,
        *,
        hero_cid: int,
        index: int,
        support_hero_cid: int,
        roster: RosterState,
    ) -> dict[str, object]:
        hero_cid = int(hero_cid)
        index = int(index)
        support_hero_cid = int(support_hero_cid)
        owned_hero_ids = {card.hero_id for card in roster.cards.values()}
        if hero_cid in owned_hero_ids and index > 0:
            slots = self.support_skill_slots.setdefault(hero_cid, {})
            if support_hero_cid in owned_hero_ids:
                slots[index] = support_hero_cid
            else:
                slots.pop(index, None)
            if not slots:
                self.support_skill_slots.pop(hero_cid, None)
        return self.card_support_skill_info()

    def card_support_skill_info(self) -> dict[str, object]:
        return {
            "Supports": [
                {
                    "HeroCId": hero_cid,
                    "Index": index,
                    "SupportHeroCId": support_hero_cid,
                    "IsAuto": 0,
                }
                for hero_cid, slots in sorted(self.support_skill_slots.items())
                for index, support_hero_cid in sorted(slots.items())
            ]
        }

    def equip_list(self) -> dict[str, object]:
        return {"UidList": []}

    def equip_attr(self, equip_uid: int = 0) -> dict[str, object]:
        return {
            "EquipAttrList": {
                "Uid": equip_uid,
                "ExtraAttr": [],
                "HideAttr": [],
            }
        }

    def area_event_hero_list(
        self, list_type: int, lineup: list[int], roster: RosterState
    ) -> dict[str, object]:
        normalized_lineup = tuple(int(item) for item in lineup)
        self.requested_area_lineups.append((list_type, normalized_lineup))
        fallback = [card.card_uid for card in roster.cards.values()]
        selected = [
            card_uid for card_uid in normalized_lineup if card_uid in roster.cards
        ]
        return {
            "Type": list_type,
            "NormalLineup": selected or fallback,
            "ActLineup": [],
        }

    def league_pvp_self_hero_list(self, roster: RosterState) -> dict[str, object]:
        return {
            "HeroList": [
                {
                    "HeroCId": card.hero_id,
                    "Hp": 100,
                    "BuffLayer": 0,
                    "CdTime": 0,
                }
                for card in sorted(
                    roster.cards.values(), key=lambda item: item.card_uid
                )
            ]
        }

    def training_hero_info(
        self, roster: RosterState, hero_id: int = 0
    ) -> dict[str, object]:
        active = roster.active_card
        if hero_id:
            for card in roster.cards.values():
                if card.hero_id == int(hero_id):
                    active = card
                    break
        active_skill_level = fight_style_for_character(
            active.character
        ).protocol_skill_levels(roster.hero_level)
        return {
            "TrainingData": {
                "HeroId": active.hero_id,
                "ShapeId": active.shape_id,
                "FashionId": 0,
                "CardUid": active.card_uid,
                "infos": [],
                "ChooseHero": [],
                "CardSkillLevel": [
                    {
                        "HeroUid": active.card_uid,
                        "SkillLevel": active_skill_level,
                    }
                ],
                "CardSpecLevel": [],
                "RuneSpecList": [],
                "Buffs": [],
                "EquipHideAttr": [],
                "AttachedCardBuff": [],
                "ActiveCards": [],
                "SupportSkill": self.training_support_skills(active.hero_id, roster),
            }
        }

    def training_info(self, roster: RosterState) -> dict[str, object]:
        return {
            "HeroData": [
                {
                    "HeroCId": card.hero_id,
                    "FinishList": [],
                    "GetList": [],
                }
                for card in sorted(
                    roster.cards.values(), key=lambda item: item.card_uid
                )
            ]
        }

    def card_lock(self, card_uid: int, is_lock: int) -> dict[str, object]:
        return {"Uid": card_uid, "IsLock": is_lock}

    def card_lock_skill(
        self, hero_cid: int, index: int, is_lock: int
    ) -> dict[str, object]:
        return {"HeroCId": hero_cid, "Index": index, "IsLock": is_lock}

    def _requested_cards(self, card_uids: list[int], roster: RosterState):
        requested = [roster.cards[uid] for uid in card_uids if uid in roster.cards]
        if requested:
            return requested
        return [
            card
            for card in sorted(roster.cards.values(), key=lambda item: item.card_uid)
        ]

    def training_support_skills(
        self, hero_cid: int, roster: RosterState
    ) -> list[dict[str, object]]:
        cards_by_hero_id = {card.hero_id: card for card in roster.cards.values()}
        entries: list[dict[str, object]] = []
        for index, support_hero_cid in sorted(
            self.support_skill_slots.get(hero_cid, {}).items()
        ):
            support_card = cards_by_hero_id.get(support_hero_cid)
            if support_card is None:
                continue
            entries.append(
                {
                    "Index": index,
                    "HeroId": support_card.hero_id,
                    "ShapeId": support_card.shape_id,
                    "FashionId": 0,
                }
            )
        return entries
