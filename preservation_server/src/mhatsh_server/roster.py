from __future__ import annotations

from dataclasses import dataclass

from .characters import PlayableCharacter, playable_card


@dataclass(frozen=True, slots=True)
class RosterCard:
    card_uid: int
    character: PlayableCharacter

    @property
    def hero_id(self) -> int:
        if self.character.hero_id is None:
            raise ValueError(f"{self.character.model_asset_id} has no verified HeroId")
        return self.character.hero_id

    @property
    def shape_id(self) -> int:
        if self.character.shape_id is None:
            raise ValueError(f"{self.character.model_asset_id} has no verified ShapeId")
        return self.character.shape_id


class RosterState:
    def __init__(
        self,
        characters: tuple[PlayableCharacter, ...],
        *,
        first_card_uid: int,
        hero_level: int = 1,
    ) -> None:
        self.cards = {
            first_card_uid + index: RosterCard(first_card_uid + index, character)
            for index, character in enumerate(characters)
            if character.is_protocol_verified
        }
        if not self.cards:
            raise ValueError("roster requires at least one verified playable character")
        self.active_card_uid = min(self.cards)
        self.active_show = 1
        self.hero_level = max(1, int(hero_level))

    @property
    def active_card(self) -> RosterCard:
        return self.cards[self.active_card_uid]

    @property
    def active_hero_id(self) -> int:
        return self.active_card.hero_id

    @property
    def active_shape_id(self) -> int:
        return self.active_card.shape_id

    def card_info(self) -> list[dict[str, object]]:
        return [
            self._card_to_protocol(card)
            for card in sorted(self.cards.values(), key=lambda item: item.card_uid)
        ]

    def hero_set(self, requested_ids: list[int] | tuple[int, ...]) -> list[int]:
        owned = {card.hero_id for card in self.cards.values()}
        requested = [int(hero_id) for hero_id in requested_ids if int(hero_id) in owned]
        if requested:
            return sorted(set(requested))
        return sorted(owned)

    def select_card(self, card_uid: int, is_show: int = 1) -> RosterCard:
        card = self.cards.get(card_uid)
        if card is None:
            raise KeyError(card_uid)
        self.active_card_uid = card_uid
        self.active_show = is_show
        return card

    def select_hero(self, hero_id: int) -> RosterCard:
        for card in self.cards.values():
            if card.hero_id == hero_id:
                self.active_card_uid = card.card_uid
                return card
        raise KeyError(hero_id)

    def card_fight_response(self, card_uid: int, is_show: int) -> dict[str, object]:
        card = self.select_card(card_uid, is_show)
        return {"CardUid": card.card_uid, "IsShow": is_show}

    def team_hero_response(self, user_uid: int, hero_id: int) -> dict[str, object]:
        card = self.select_hero(hero_id)
        return {
            "UserUId": user_uid,
            "HeroId": card.hero_id,
            "Fighting": 1,
            "Vitality": 100,
            "ShapeId": card.shape_id,
            "MLv": self.hero_level,
        }

    def scene_hero_change(self, user_uid: int) -> dict[str, object]:
        return {
            "Uid": user_uid,
            "ShowHeroId": self.active_hero_id,
            "ShapeCacheId": 0,
        }

    def area_event_switch_response(self, hero_uid: int) -> dict[str, object]:
        card = self.select_card(hero_uid, 1)
        return {"ControlId": card.card_uid}

    def team_play_response(
        self, play_id: int, extra_values: list[int]
    ) -> dict[str, object]:
        return {
            "PlayId": play_id,
            "Extra": [
                {"Key": str(index + 1), "Val": int(value)}
                for index, value in enumerate(extra_values)
            ],
        }

    def _card_to_protocol(self, card: RosterCard) -> dict[str, object]:
        values = playable_card(
            card.character,
            card.card_uid,
            level=self.hero_level,
        )
        values["Fighting"] = int(card.card_uid == self.active_card_uid)
        return values
