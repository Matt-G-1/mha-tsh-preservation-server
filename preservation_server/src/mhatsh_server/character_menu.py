from __future__ import annotations

from dataclasses import dataclass, field

from .roster import RosterState


@dataclass(slots=True)
class CharacterMenuState:
    opened_show_ids: list[int] = field(default_factory=list)
    requested_area_lineups: list[tuple[int, tuple[int, ...]]] = field(
        default_factory=list
    )

    def card_show_info(self) -> dict[str, object]:
        return {"ActiveAttachedCardIdList": []}

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
                {"HeroUid": card.card_uid, "SkillLevelInfo": []} for card in cards
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
                {"HeroId": card.hero_id, "SlotInfo": []}
                for card in sorted(
                    roster.cards.values(), key=lambda item: item.card_uid
                )
            ]
        }

    def attached_card_book(self) -> dict[str, object]:
        return {"Page": 0, "Book": []}

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

    def training_hero_info(self, roster: RosterState) -> dict[str, object]:
        active = roster.active_card
        return {
            "TrainingData": {
                "HeroId": active.hero_id,
                "ShapeId": active.shape_id,
                "FashionId": 0,
                "CardUid": active.card_uid,
                "infos": [],
                "ChooseHero": [],
                "CardSkillLevel": [],
                "CardSpecLevel": [],
                "RuneSpecList": [],
                "Buffs": [],
                "EquipHideAttr": [],
                "AttachedCardBuff": [],
                "ActiveCards": [],
                "SupportSkill": [],
            }
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
