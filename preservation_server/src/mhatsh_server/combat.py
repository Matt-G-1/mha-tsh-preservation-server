from __future__ import annotations

from dataclasses import dataclass, replace

from .characters import PlayableCharacter
from .combat_action_hints import RECOVERED_HERO_ACTION_HINTS_BY_MODEL
from .combat_internal_action_hints import RECOVERED_INTERNAL_ACTION_HINTS_BY_MODEL


COMBAT_CATALOG_SOURCE = (
    "local skill-description strings, OBB battle audio names, and verified "
    "hero_cfg roster rows, 2026-06-23"
)


@dataclass(frozen=True, slots=True)
class FightMove:
    slot: int
    command: str
    name: str
    role: str
    damage_type: str
    range_type: str
    tags: tuple[str, ...] = ()

    def to_skill_level(self, level: int) -> dict[str, object]:
        return {"SkillId": self.slot, "SkillLevel": max(1, int(level))}


@dataclass(frozen=True, slots=True)
class HeroCombatMetadata:
    config_row: int
    shape_id: int
    skill_group_id: int
    q_shape_id: int
    passive_skill_active: int
    skill_ids: tuple[int, ...] = ()
    preload_effects: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class HeroSkillVideoEvidence:
    prefix: str
    count: int
    categories: tuple[str, ...]

    def categories_for_command(self, command: str) -> tuple[str, ...]:
        wanted = SKILL_VIDEO_CATEGORIES_BY_COMMAND.get(command, ())
        return tuple(category for category in wanted if category in self.categories)


@dataclass(frozen=True, slots=True)
class HeroSkillInfoEvidence:
    terms_by_command: tuple[tuple[str, tuple[str, ...]], ...]

    def terms_for_command(self, command: str) -> tuple[str, ...]:
        for evidence_command, terms in self.terms_by_command:
            if evidence_command == command:
                return terms
        return ()

    def all_terms(self) -> tuple[str, ...]:
        return tuple(
            term
            for _, terms in self.terms_by_command
            for term in terms
        )


@dataclass(frozen=True, slots=True)
class HeroSupportSkillEvidence:
    terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MoveCombatResult:
    slot: int
    command: str
    name: str
    count: int
    estimated_hits: int
    estimated_damage: int
    control_score: int
    resource_delta: int
    mobility_score: int
    defense_score: int
    damage_type: str
    range_type: str
    role: str
    video_categories: tuple[str, ...] = ()
    skill_info_terms: tuple[str, ...] = ()
    skill_slot_labels: tuple[str, ...] = ()
    action_hints: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "Slot": self.slot,
            "Command": self.command,
            "Name": self.name,
            "Count": self.count,
            "EstimatedHits": self.estimated_hits,
            "EstimatedDamage": self.estimated_damage,
            "ControlScore": self.control_score,
            "ResourceDelta": self.resource_delta,
            "MobilityScore": self.mobility_score,
            "DefenseScore": self.defense_score,
            "DamageType": self.damage_type,
            "RangeType": self.range_type,
            "Role": self.role,
            "VideoCategories": list(self.video_categories),
            "SkillInfoTerms": list(self.skill_info_terms),
            "SkillSlotLabels": list(self.skill_slot_labels),
            "ActionHints": list(self.action_hints),
        }


@dataclass(frozen=True, slots=True)
class CombatResolution:
    hero_id: int
    style_name: str
    hero_level: int
    reported_damage: int
    estimated_damage: int
    target_count: int
    defeated_targets: int
    control_score: int
    resource_delta: int
    mobility_score: int
    defense_score: int
    pressure_score: int
    move_results: tuple[MoveCombatResult, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "HeroId": self.hero_id,
            "StyleName": self.style_name,
            "HeroLevel": self.hero_level,
            "ReportedDamage": self.reported_damage,
            "EstimatedDamage": self.estimated_damage,
            "TargetCount": self.target_count,
            "DefeatedTargets": self.defeated_targets,
            "ControlScore": self.control_score,
            "ResourceDelta": self.resource_delta,
            "MobilityScore": self.mobility_score,
            "DefenseScore": self.defense_score,
            "PressureScore": self.pressure_score,
            "MoveResults": [result.as_dict() for result in self.move_results],
        }


@dataclass(frozen=True, slots=True)
class FightStyle:
    model_asset_id: str
    hero_id: int
    style_name: str
    archetype: str
    resource: str
    moves: tuple[FightMove, ...]
    recovered_action_hints: tuple[str, ...] = ()
    hero_cfg: HeroCombatMetadata | None = None
    source: str = COMBAT_CATALOG_SOURCE

    def skill_levels(self, level: int) -> list[dict[str, object]]:
        return [move.to_skill_level(level) for move in self.moves]

    def move_names(self) -> tuple[str, ...]:
        return tuple(move.name for move in self.moves)

    def action_hints(self) -> tuple[str, ...]:
        return self.recovered_action_hints

    def action_hints_for_command(self, command: str) -> tuple[str, ...]:
        return tuple(
            action
            for action in self.recovered_action_hints
            if _action_hint_command_for_model(self.model_asset_id, action) == command
        )

    def action_hint_counts_by_command(self) -> dict[str, int]:
        return {
            command: len(self.action_hints_for_command(command))
            for command in REPORT_BUTTON_COMMANDS.values()
        }

    def missing_action_hint_commands(self) -> tuple[str, ...]:
        return tuple(
            command
            for command, count in self.action_hint_counts_by_command().items()
            if count == 0
        )

    def hero_cfg_skill_ids(self) -> tuple[int, ...]:
        if self.hero_cfg is None:
            return ()
        return self.hero_cfg.skill_ids

    def hero_cfg_preload_effects(self) -> tuple[int, ...]:
        if self.hero_cfg is None:
            return ()
        return self.hero_cfg.preload_effects

    def recovered_ai_name(self) -> str:
        return HERO_CFG_AI_NAMES_BY_MODEL.get(self.model_asset_id, "")

    def recovered_action_map(self) -> tuple[tuple[str, str], ...]:
        return HERO_CFG_ACTION_MAP_BY_MODEL.get(self.model_asset_id, ())

    def recovered_skill_video_evidence(self) -> HeroSkillVideoEvidence | None:
        return HERO_SKILL_VIDEO_EVIDENCE_BY_MODEL.get(self.model_asset_id)

    def recovered_skill_info_evidence(self) -> HeroSkillInfoEvidence | None:
        return HERO_SKILL_INFO_EVIDENCE_BY_MODEL.get(self.model_asset_id)

    def recovered_support_skill_evidence(self) -> HeroSupportSkillEvidence | None:
        return HERO_SUPPORT_SKILL_EVIDENCE_BY_MODEL.get(self.model_asset_id)

    def move_usage(
        self, button_counts: tuple[tuple[str, int], ...]
    ) -> list[dict[str, object]]:
        counts = {str(command): max(0, int(count)) for command, count in button_counts}
        move_by_command = {move.command: move for move in self.moves}
        usage = []
        for report_key, command in REPORT_BUTTON_COMMANDS.items():
            move = move_by_command.get(command)
            if move is None:
                continue
            usage.append(
                {
                    "Slot": move.slot,
                    "Command": move.command,
                    "Name": move.name,
                    "Count": counts.get(report_key, 0),
                    "DamageType": move.damage_type,
                    "RangeType": move.range_type,
                }
            )
        return usage

    def resolve_usage(
        self,
        button_counts: tuple[tuple[str, int], ...],
        *,
        hero_level: int = 1,
        reported_damage: int = 0,
        target_count: int = 1,
        target_hp_values: tuple[int, ...] = (),
    ) -> CombatResolution:
        counts = {str(command): max(0, int(count)) for command, count in button_counts}
        move_by_command = {move.command: move for move in self.moves}
        raw_results = []
        level_scale = 1.0 + max(0, int(hero_level) - 1) * 0.03
        video_evidence = self.recovered_skill_video_evidence()
        skill_info_evidence = self.recovered_skill_info_evidence()
        for report_key, command in REPORT_BUTTON_COMMANDS.items():
            move = move_by_command.get(command)
            if move is None:
                continue
            count = counts.get(report_key, 0)
            raw_damage = round(count * _move_power(move) * level_scale)
            raw_results.append((move, count, raw_damage))

        raw_total = sum(damage for _, _, damage in raw_results)
        reported = max(0, int(reported_damage))
        scale = (reported / raw_total) if reported and raw_total else 1.0
        result_list = [
            MoveCombatResult(
                slot=move.slot,
                command=move.command,
                name=move.name,
                count=count,
                estimated_hits=count * _move_hit_count(move),
                estimated_damage=round(raw_damage * scale),
                control_score=count * _move_control_score(move),
                resource_delta=count * _move_resource_delta(move),
                mobility_score=count * _move_mobility_score(move),
                defense_score=count * _move_defense_score(move),
                damage_type=move.damage_type,
                range_type=move.range_type,
                role=move.role,
                video_categories=(
                    video_evidence.categories_for_command(move.command)
                    if video_evidence is not None
                    else ()
                ),
                skill_info_terms=(
                    skill_info_evidence.terms_for_command(move.command)
                    if skill_info_evidence is not None
                    else ()
                ),
                skill_slot_labels=skill_slot_labels_for_command(move.command),
                action_hints=self.action_hints_for_command(move.command),
            )
            for move, count, raw_damage in raw_results
        ]
        estimated_total = sum(result.estimated_damage for result in result_list)
        if reported and result_list and estimated_total != reported:
            for index, result in enumerate(result_list):
                if result.count or result.estimated_damage:
                    result_list[index] = replace(
                        result,
                        estimated_damage=max(
                            0,
                            result.estimated_damage + reported - estimated_total,
                        ),
                    )
                    break
        move_results = tuple(result_list)
        estimated_total = sum(result.estimated_damage for result in move_results)
        control_score = sum(result.control_score for result in move_results)
        resource_delta = sum(result.resource_delta for result in move_results)
        mobility_score = sum(result.mobility_score for result in move_results)
        defense_score = sum(result.defense_score for result in move_results)
        pressure_score = max(
            0,
            (estimated_total // 100)
            + control_score
            + mobility_score // 2
            - defense_score // 3,
        )
        target_hps = tuple(max(1, int(value)) for value in target_hp_values)
        target_total = len(target_hps) if target_hps else max(0, int(target_count))
        defeated = _defeated_target_count(
            estimated_total,
            target_hps
            or (max(750, round(1600 + max(1, int(hero_level)) * 45)),)
            * target_total,
        )
        return CombatResolution(
            hero_id=self.hero_id,
            style_name=self.style_name,
            hero_level=max(1, int(hero_level)),
            reported_damage=reported,
            estimated_damage=estimated_total,
            target_count=target_total,
            defeated_targets=defeated,
            control_score=control_score,
            resource_delta=resource_delta,
            mobility_score=mobility_score,
            defense_score=defense_score,
            pressure_score=pressure_score,
            move_results=move_results,
        )


def _move(
    slot: int,
    command: str,
    name: str,
    role: str,
    damage_type: str,
    range_type: str,
    *tags: str,
) -> FightMove:
    return FightMove(slot, command, name, role, damage_type, range_type, tags)


def _style(
    model_asset_id: str,
    hero_id: int,
    style_name: str,
    archetype: str,
    resource: str,
    moves: tuple[FightMove, ...],
    recovered_action_hints: tuple[str, ...] = (),
    hero_cfg: HeroCombatMetadata | None = None,
) -> FightStyle:
    action_hints = _combined_action_hints(model_asset_id, recovered_action_hints)
    return FightStyle(
        model_asset_id,
        hero_id,
        style_name,
        archetype,
        resource,
        moves,
        action_hints,
        hero_cfg or HERO_CFG_COMBAT_METADATA_BY_MODEL.get(model_asset_id),
    )


DEFAULT_MOVES = (
    _move(1, "ATK", "Normal Combo", "basic combo", "physical", "melee"),
    _move(2, "Q", "Quirk Skill Q", "starter skill", "quirk", "mid"),
    _move(3, "W", "Quirk Skill W", "secondary skill", "quirk", "mid"),
    _move(4, "E", "Quirk Skill E", "launcher skill", "quirk", "mid"),
    _move(5, "R", "Ultimate", "ultimate", "quirk", "area"),
    _move(6, "DODGE", "Perfect Dodge", "defensive counter", "utility", "self"),
    _move(7, "PASSIVE", "Core Passive", "passive mechanic", "utility", "self"),
)


HERO_ACTION_HINTS_BY_MODEL = {
    **RECOVERED_HERO_ACTION_HINTS_BY_MODEL,
    **RECOVERED_INTERNAL_ACTION_HINTS_BY_MODEL,
    "h1004": RECOVERED_HERO_ACTION_HINTS_BY_MODEL["h1003"],
    "h1024": RECOVERED_HERO_ACTION_HINTS_BY_MODEL["h1001"],
    "h1998": RECOVERED_HERO_ACTION_HINTS_BY_MODEL["h1003"],
}


HERO_ACTION_COMMAND_OVERRIDES_BY_MODEL = {
    "h1009": (
        ("wskill_create", "Q"),
    ),
    "h1029": (
        ("1029_askill", "ATK"),
        ("1029_skill0", "Q"),
        ("1029_skill1", "W"),
        ("1029_skill2", "E"),
        ("1029_skill3", "R"),
    ),
}


def _combined_action_hints(
    model_asset_id: str, recovered_action_hints: tuple[str, ...]
) -> tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            (
                *recovered_action_hints,
                *HERO_ACTION_HINTS_BY_MODEL.get(model_asset_id, ()),
            )
        )
    )


REPORT_BUTTON_COMMANDS = {
    "ATK": "ATK",
    "1": "Q",
    "2": "W",
    "3": "E",
    "4": "R",
    "5": "DODGE",
    "6": "PASSIVE",
}


SKILL_VIDEO_CATEGORIES_BY_COMMAND = {
    "ATK": ("ATK", "BREAK", "RUSH"),
    "Q": ("Q",),
    "W": ("W",),
    "E": ("E",),
    "R": ("R", "QTE"),
    "DODGE": ("DASH",),
    "PASSIVE": ("ABI", "PRE"),
}


SKILL_SLOT_LABELS_BY_COMMAND = {
    "ATK": ("BaseSkill", "ASkill", "DashAtk", "RushSkill", "Normal ATK Combo"),
    "Q": ("FirstSkill", "Special Skill"),
    "W": ("SecondSkill", "Special Skill"),
    "E": ("ThirdSkill", "Special Skill"),
    "R": ("FinalSkill",),
    "DODGE": ("RollSkill",),
    "PASSIVE": ("PassiveSkill",),
    "QTE": ("QteBtnSkill",),
}


def skill_slot_labels_for_command(command: str) -> tuple[str, ...]:
    return SKILL_SLOT_LABELS_BY_COMMAND.get(command, ())


def _action_hint_command_for_model(model_asset_id: str, action: str) -> str | None:
    leaf = action.lower().rsplit("/", 1)[-1]
    for prefix, command in HERO_ACTION_COMMAND_OVERRIDES_BY_MODEL.get(
        model_asset_id, ()
    ):
        if leaf.startswith(prefix):
            return command
    return _action_hint_command(action)


def _action_hint_command(action: str) -> str | None:
    normalized = action.lower()
    leaf = normalized.rsplit("/", 1)[-1]
    if (
        "/commonatk/" in normalized
        or "/connomatk/" in normalized
        or "/atk/" in normalized
        or "commonatk" in normalized
        or "breakatk" in normalized
        or "break_atk" in normalized
        or "dashatk" in normalized
        or "dash_atk" in normalized
        or leaf.startswith("atk")
        or "_atk" in leaf
    ):
        return "ATK"
    if "qskill" in normalized:
        return "Q"
    if "wskill" in normalized:
        return "W"
    if "eskill" in normalized:
        return "E"
    if "rskill" in normalized:
        return "R"
    if "skillex" in leaf or "skill_ex" in leaf:
        return "R"
    if "dodge" in normalized:
        return "DODGE"
    if "dash" in leaf:
        return "DODGE"
    if (
        "/ability/" in normalized
        or "/ability" in normalized
        or "nengli" in leaf
        or "gexing" in leaf
    ):
        return "PASSIVE"
    generic_number = _generic_skill_number(leaf)
    if generic_number in {0, 1, 11}:
        return "Q"
    if generic_number in {2, 21}:
        return "W"
    if generic_number in {3, 31}:
        return "E"
    if generic_number in {4, 7, 41}:
        return "R"
    return None


def _generic_skill_number(leaf: str) -> int | None:
    for prefix in ("skill", "pve_skill", "pvp_skill"):
        index = leaf.find(prefix)
        if index < 0:
            continue
        suffix = leaf[index + len(prefix) :]
        while suffix.startswith("_"):
            suffix = suffix[1:]
        digits = ""
        for char in suffix:
            if not char.isdigit():
                break
            digits += char
        if digits:
            return int(digits)
    return None


MOVE_BASE_POWER = {
    "ATK": 80,
    "Q": 260,
    "W": 240,
    "E": 280,
    "R": 950,
    "DODGE": 120,
    "PASSIVE": 0,
}


def _move_power(move: FightMove) -> int:
    power = MOVE_BASE_POWER.get(move.command, 100)
    if move.range_type == "area":
        power += 45
    elif move.range_type == "ranged":
        power += 20
    if "ultimate" in move.role:
        power += 160
    if "buff" in move.role or "passive" in move.role:
        power = max(0, power - 80)
    return power


def _move_hit_count(move: FightMove) -> int:
    if move.command == "ATK":
        return 3
    if move.range_type == "area":
        return 2
    return 1


def _defeated_target_count(total_damage: int, target_hp_values: tuple[int, ...]) -> int:
    remaining_damage = max(0, int(total_damage))
    defeated = 0
    for target_hp in target_hp_values:
        if remaining_damage >= target_hp:
            defeated += 1
            remaining_damage -= target_hp
        else:
            break
    return defeated


def _move_control_score(move: FightMove) -> int:
    text = f"{move.role} {' '.join(move.tags)}".lower()
    score = 0
    if any(
        token in text
        for token in (
            "bind",
            "control",
            "counter",
            "field",
            "guard",
            "interrupt",
            "knock",
            "launcher",
            "pull",
            "root",
            "slow",
            "stagger",
            "trap",
            "wall",
        )
    ):
        score += 2
    if move.range_type == "area":
        score += 1
    return score


def _move_resource_delta(move: FightMove) -> int:
    text = f"{move.role} {' '.join(move.tags)}".lower()
    if move.command == "R":
        return -3
    if any(token in text for token in ("ramp", "refresh", "stockpile", "charge")):
        return 2
    if any(token in text for token in ("buff", "stance", "form")):
        return 1
    return 0


def _move_mobility_score(move: FightMove) -> int:
    text = move.role.lower()
    if any(token in text for token in ("dash", "gap closer", "leap", "reposition")):
        return 2
    if move.command == "DODGE":
        return 3
    return 0


def _move_defense_score(move: FightMove) -> int:
    text = move.role.lower()
    if any(
        token in text
        for token in ("counter", "defense", "defensive", "guard", "shield", "survival")
    ):
        return 2
    if move.command == "DODGE":
        return 2
    return 0


HERO_CFG_COMBAT_METADATA_BY_MODEL = {
    "h1001": HeroCombatMetadata(101, 1001, 10007, 11001, 0, (1001, 1002), (100101,)),
    "h1002": HeroCombatMetadata(102, 1002, 10008, 11002, 0, (), (100201,)),
    "h1003": HeroCombatMetadata(104, 1003, 10010, 11003, 0),
    "h1004": HeroCombatMetadata(103, 1004, 10016, 11001, 0),
    "h1006": HeroCombatMetadata(106, 1006, 10020, 11006, 0),
    "h1007": HeroCombatMetadata(107, 1007, 10015, 11007, 0),
    "h1008": HeroCombatMetadata(108, 1008, 10019, 11008, 0),
    "h1009": HeroCombatMetadata(
        109,
        1009,
        10014,
        11009,
        0,
        (),
        (1174, 1175, 1181, 1182, 1192),
    ),
    "h1010": HeroCombatMetadata(110, 1010, 10009, 11010, 0),
    "h1012": HeroCombatMetadata(112, 1012, 10007, 11012, 0, (), (100101,)),
    "h1013": HeroCombatMetadata(113, 1013, 10007, 11013, 0, (1001, 1002), (100101,)),
    "h1014": HeroCombatMetadata(114, 1014, 10007, 11014, 0, (1001, 1002), (100101,)),
    "h1015": HeroCombatMetadata(115, 1015, 10007, 11015, 0, (1001, 1002), (100101,)),
    "h1016": HeroCombatMetadata(116, 1016, 10007, 11016, 0, (1001, 1002), (100101,)),
    "h1017": HeroCombatMetadata(117, 1017, 10007, 11017, 0, (1001, 1002), (100101,)),
    "h1018": HeroCombatMetadata(118, 1018, 10009, 11018, 0),
    "h1019": HeroCombatMetadata(119, 1019, 10009, 11019, 0),
    "h1020": HeroCombatMetadata(120, 1020, 10009, 11020, 0),
    "h1021": HeroCombatMetadata(121, 1021, 10009, 11021, 0),
    "h1022": HeroCombatMetadata(122, 1022, 10009, 11022, 0),
    "h1024": HeroCombatMetadata(124, 1024, 10007, 11001, 0, (1001, 1002), (100101,)),
    "h1026": HeroCombatMetadata(126, 1026, 10007, 11026, 0, (1001, 1002), (100101,)),
    "h1027": HeroCombatMetadata(127, 1027, 10007, 11027, 0, (1001, 1002), (100101,)),
    "h1028": HeroCombatMetadata(128, 1028, 10008, 11028, 0, (), (100201,)),
    "h1029": HeroCombatMetadata(129, 1029, 10019, 11029, 0),
    "h1030": HeroCombatMetadata(130, 1030, 10008, 11030, 0, (), (100201,)),
    "h1031": HeroCombatMetadata(131, 1031, 10008, 11031, 0, (), (100201,)),
    "h1032": HeroCombatMetadata(
        132,
        1032,
        10008,
        11032,
        0,
        (),
        (2600201, 2600202, 2600203),
    ),
    "h1110": HeroCombatMetadata(111, 1011, 10009, 11011, 0),
    "h1998": HeroCombatMetadata(198, 9051, 10010, 11001, 1),
}


HERO_CFG_AI_NAMES_BY_MODEL = {
    "h1001": "bot_lvgu",
    "h1002": "bot_baohao",
    "h1003": "bot_ouermaite",
    "h1004": "bot_ouermaite",
    "h1006": "bot_fantian",
    "h1007": "bot_yuchazi",
    "h1008": "bot_hong",
    "h1009": "bot_babaiwan",
    "h1010": "bot_dianqi",
    "h1012": "bot_tupi",
    "h1013": "bot_qiedao",
    "h1014": "bot_wachui",
    "h1015": "bot_xiangze",
    "h1016": "bot_weibai",
    "h1017": "bot_sannai",
    "h1018": "bot_dianqi",
    "h1019": "bot_sibingmu",
    "h1020": "bot_putao",
    "h1021": "bot_andewa",
    "h1022": "bot_changan",
    "h1024": "bot_lvgu",
    "h1026": "bot_huokesi",
    "h1027": "bot_lvguwhm",
    "h1028": "bot_baohaowhm",
    "h1029": "bot_hongwhm",
    "h1030": "bot_bodong",
    "h1031": "bot_tiancanhuan",
    "h1032": "bot_tongxingbaiwan",
    "h1110": "bot_sitanyin",
    "h1998": "bot_common",
}


HERO_CFG_ACTION_MAP_BY_MODEL = {
    "h1002": (("arder_biliqi", "arder_biliqi02"), ("arder_yaling", "arder_yaling02")),
    "h1003": (("arder_yaling", "arder_yaling03"),),
    "h1008": (("arder_biliqi", "arder_biliqi11"),),
    "h1009": (("arder_biliqi", "arder_biliqi11"),),
    "h1010": (("arder_yaling", "arder_yaling10"),),
    "h1012": (("arder_biliqi", "arder_biliqi11"),),
    "h1015": (("arder_biliqi", "arder_biliqi115"), ("arder_yaling", "arder_yaling115")),
    "h1016": (
        ("arder_biliqi", "arder_biliqi116"),
        ("arder_tiaosheng", "arder_tiaosheng116"),
    ),
    "h1019": (("arder_yaling", "arder_yaling10"),),
    "h1021": (("arder_yaling", "arder_yaling121"),),
    "h1022": (("arder_biliqi", "arder_biliqi11"), ("arder_yaling", "arder_yaling11")),
    "h1028": (("arder_biliqi", "arder_biliqi02"), ("arder_yaling", "arder_yaling02")),
    "h1029": (("arder_biliqi", "arder_biliqi11"),),
    "h1030": (("arder_biliqi", "arder_biliqi02"), ("arder_yaling", "arder_yaling02")),
    "h1031": (("arder_biliqi", "arder_biliqi02"), ("arder_yaling", "arder_yaling02")),
    "h1032": (("arder_biliqi", "arder_biliqi02"), ("arder_yaling", "arder_yaling02")),
    "h1110": (("arder_biliqi", "arder_biliqi11"), ("arder_yaling", "arder_yaling11")),
}


HERO_SKILL_VIDEO_EVIDENCE_BY_MODEL = {
    "h1001": HeroSkillVideoEvidence(
        "lvgu",
        10,
        ("ABI", "ATK", "BREAK", "DASH", "E", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1002": HeroSkillVideoEvidence(
        "baohao",
        11,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "QTE", "R", "RUSH", "W"),
    ),
    "h1003": HeroSkillVideoEvidence(
        "ouermaite",
        10,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1004": HeroSkillVideoEvidence(
        "ouermaite",
        10,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1006": HeroSkillVideoEvidence(
        "fantian",
        9,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "W"),
    ),
    "h1007": HeroSkillVideoEvidence(
        "yuchazi",
        15,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1008": HeroSkillVideoEvidence(
        "hong",
        14,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1009": HeroSkillVideoEvidence(
        "babaiwan",
        12,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1010": HeroSkillVideoEvidence(
        "shangming",
        11,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1012": HeroSkillVideoEvidence(
        "tupi",
        11,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1013": HeroSkillVideoEvidence(
        "xqiedao",
        10,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1014": HeroSkillVideoEvidence(
        "wachui",
        10,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1015": HeroSkillVideoEvidence(
        "xiangze",
        14,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1016": HeroSkillVideoEvidence(
        "weibai",
        13,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1017": HeroSkillVideoEvidence(
        "sannai",
        12,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1019": HeroSkillVideoEvidence(
        "sibingmu",
        13,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1021": HeroSkillVideoEvidence(
        "andewa",
        13,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1022": HeroSkillVideoEvidence(
        "changan",
        12,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1024": HeroSkillVideoEvidence(
        "xlvgu",
        10,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1026": HeroSkillVideoEvidence(
        "huokesi",
        12,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1027": HeroSkillVideoEvidence(
        "lvguwhm",
        11,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1028": HeroSkillVideoEvidence(
        "baohaowhm",
        15,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1029": HeroSkillVideoEvidence(
        "hongwhm",
        14,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1030": HeroSkillVideoEvidence(
        "bodong",
        10,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1031": HeroSkillVideoEvidence(
        "tiancanhuan",
        12,
        ("ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1032": HeroSkillVideoEvidence(
        "tongxingbaiwan",
        14,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
    "h1110": HeroSkillVideoEvidence(
        "sitanyin",
        11,
        ("ABI", "ATK", "BREAK", "DASH", "E", "PRE", "Q", "QTE", "R", "RUSH", "W"),
    ),
}


HERO_SKILL_INFO_EVIDENCE_BY_MODEL = {
    "h1001": HeroSkillInfoEvidence(
        (
            ("Q", ("Smash", "Detroit Smash")),
            ("R", ("One For All",)),
        )
    ),
    "h1002": HeroSkillInfoEvidence(
        (
            ("Q", ("Extra Explosion",)),
            ("PASSIVE", ("Bakugo",)),
        )
    ),
    "h1003": HeroSkillInfoEvidence((("E", ("I Am Here!",)),)),
    "h1006": HeroSkillInfoEvidence((("Q", ("Recipro Extend",)),)),
    "h1007": HeroSkillInfoEvidence(
        (
            ("Q", ("Gravel Strike", "Meteor Storm")),
            ("W", ("失重冲击",)),
            ("E", ("个性无重力",)),
            ("R", ("御茶子必杀技",)),
            ("DODGE", ("御茶子极限闪避QTE",)),
        )
    ),
    "h1008": HeroSkillInfoEvidence(
        (
            ("Q", ("Half-Cold Half-Hot",)),
            ("W", ("Charge Ice Spear",)),
        )
    ),
    "h1009": HeroSkillInfoEvidence(
        (
            ("Q", ("Meteor Storm",)),
            ("W", ("Q - Weapon Creation",)),
            ("PASSIVE", ("Yaoyorozu",)),
        )
    ),
    "h1010": HeroSkillInfoEvidence((("R", ("Lightning Bolt",)),)),
    "h1012": HeroSkillInfoEvidence(
        (
            ("ATK", ("Dabi普攻1",)),
            ("Q", ("DabiQ",)),
            ("W", ("DabiQ变身",)),
            ("E", ("Dabi Assist Skill E",)),
            ("R", ("Dabi大招（PVE)",)),
            ("PASSIVE", ("Dabi ability fire",)),
        )
    ),
    "h1013": HeroSkillInfoEvidence(
        (
            (
                "Q",
                (
                    "Kirishima Defense counter Q 2 tap",
                    "Kirishima Q change 2 tap",
                    "Kirishima Q change return",
                ),
            ),
            (
                "W",
                (
                    "Kirishima W change Aeration 4",
                    "Kirishima W Talent 10 cooldown",
                ),
            ),
            ("PASSIVE", ("Talent Aeration 4",)),
        )
    ),
    "h1014": HeroSkillInfoEvidence((("Q", ("Tongue Swipe",)),)),
    "h1015": HeroSkillInfoEvidence(
        (
            ("ATK", ("正常普攻1",)),
            ("Q", ("相泽Q1",)),
            ("W", ("相泽W陷阱",)),
            ("E", ("相泽E远程",)),
            ("R", ("相泽大招",)),
            ("DODGE", ("相泽闪避",)),
            ("PASSIVE", ("相泽能力",)),
        )
    ),
    "h1016": HeroSkillInfoEvidence(
        (
            ("ATK", ("尾白普攻1",)),
            ("Q", ("尾白Q", "尾巴强化Q")),
            ("W", ("尾白W", "尾白强化W")),
            ("E", ("尾白E", "尾白强化E")),
            ("R", ("尾白大招",)),
            ("DODGE", ("尾白闪避攻击",)),
            ("PASSIVE", ("尾白能力",)),
        )
    ),
    "h1017": HeroSkillInfoEvidence(
        (
            ("Q", ("Mina Q", "Mina Enhanced Q", "Mina Q acid")),
            ("W", ("Mina W slip", "Mina W end")),
            ("E", ("Mina E ready to spin", "Mina E upper cut")),
            ("R", ("Mina R",)),
            (
                "DODGE",
                (
                    "Mina Perfect Dodge slow",
                    "Mina Perfect Dodge effect",
                    "Mina Perfect Dodge QTE",
                ),
            ),
        )
    ),
    "h1019": HeroSkillInfoEvidence((("ATK", ("Vicious Contact",)),)),
    "h1020": HeroSkillInfoEvidence(
        (
            ("Q", ("Firing Mode", "Exit Firing Mode")),
            ("W", ("Mineta-Bounce", "Dimensional Bounce")),
            ("E", ("Grape Rain",)),
            ("DODGE", ("Dodge 2",)),
        )
    ),
    "h1021": HeroSkillInfoEvidence(
        (
            ("R", ("Exploding Lance",)),
            ("PASSIVE", ("Endeavor",)),
        )
    ),
    "h1022": HeroSkillInfoEvidence(
        (
            ("Q", ("Abyssal Claw",)),
            ("W", ("Shadow Zone",)),
            ("R", ("Abyssal Talons",)),
        )
    ),
    "h1024": HeroSkillInfoEvidence((("Q", ("Smash!",)),)),
    "h1026": HeroSkillInfoEvidence(
        (
            ("ATK", ("Hawks Normal ATK 1",)),
            ("Q", ("Hawks Q open",)),
            ("W", ("Hawks W",)),
            ("E", ("Hawks E",)),
            ("R", ("Hawks ult",)),
            ("PASSIVE", ("Hawks passive",)),
        )
    ),
    "h1027": HeroSkillInfoEvidence(
        (
            ("ATK", ("WHM绿谷普攻1", "Midoriya black whip")),
            ("Q", ("Midoriya Q", "Midoriya Q skill down kick")),
            ("W", ("Midoriya W",)),
            ("E", ("Midoriya E", "Midoriya E skill charge")),
            ("R", ("whm绿谷R",)),
        )
    ),
    "h1028": HeroSkillInfoEvidence(
        (
            ("ATK", ("Normal ATK 6 (Fly)", "Bakugo DEF Break attack")),
            ("Q", ("Q Ground charge", "Q Ground machine gun", "Q Air 1")),
            ("W", ("W Wuhu takeoff", "W Air move")),
            ("E", ("E Fire tornado", "E Drill flame")),
            ("R", ("R Movie Ult (PVE)",)),
            ("PASSIVE", ("whm爆豪被动1",)),
        )
    ),
    "h1029": HeroSkillInfoEvidence(
        (
            ("Q", ("whm轰Q1", "whm轰Q2")),
            ("W", ("whm轰W1", "冰枪1段")),
            ("E", ("whm轰E", "火焰喷射")),
            ("R", ("whm轰R",)),
            ("PASSIVE", ("whm轰被动1",)),
        )
    ),
    "h1030": HeroSkillInfoEvidence(
        (
            ("ATK", ("测试波动普攻1",)),
            ("Q", ("波动Q1", "Wave Blast")),
            ("W", ("波动W",)),
            ("E", ("波动E1", "波动E2")),
            ("R", ("波动R",)),
        )
    ),
    "h1031": HeroSkillInfoEvidence(
        (
            ("ATK", ("天喰环普攻1",)),
            ("Q", ("天喰环Q1", "Tentacles Grasp")),
            ("W", ("天喰环W",)),
            ("E", ("天喰环E1", "天喰环E2")),
            ("R", ("天喰环R",)),
        )
    ),
    "h1032": HeroSkillInfoEvidence(
        (
            ("ATK", ("通行百万普攻1",)),
            ("Q", ("通行百万Q3", "通行百万Q4")),
            ("W", ("Mirio TogataW",)),
            ("E", ("Mirio TogataE",)),
            ("R", ("通行百万R",)),
        )
    ),
    "h1110": HeroSkillInfoEvidence(
        (
            ("Q", ("Aura of Fear",)),
            ("W", ("Dagger Throw",)),
            ("E", ("Permeate Uppercut",)),
            ("DODGE", ("Shadowy Surprise",)),
            ("PASSIVE", ("Vigor", "Stain")),
        )
    ),
}


HERO_SUPPORT_SKILL_EVIDENCE_BY_MODEL = {
    "h1019": HeroSupportSkillEvidence(("Vicious Contact",)),
    "h1021": HeroSupportSkillEvidence(("Exploding Lance",)),
    "h1024": HeroSupportSkillEvidence(("Smash!",)),
    "h1026": HeroSupportSkillEvidence(("Downfall",)),
    "h1027": HeroSupportSkillEvidence(("WHM Shoot Style",)),
    "h1028": HeroSupportSkillEvidence(("Turbo Twister",)),
    "h1029": HeroSupportSkillEvidence(("Icicle Storm",)),
    "h1030": HeroSupportSkillEvidence(("Wave Blast",)),
    "h1031": HeroSupportSkillEvidence(("Tentacles Grasp",)),
}


FIGHT_STYLES_BY_MODEL = {
    "h1001": _style(
        "h1001",
        1011,
        "One For All Rookie",
        "mobile striker",
        "One For All charge",
        (
            _move(1, "ATK", "Shoot Style Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Detroit Smash", "knockback burst", "wind", "mid", "tornado"),
            _move(3, "W", "Delaware Smash", "ranged poke", "wind", "ranged"),
            _move(4, "E", "Full Cowl Rush", "gap closer", "physical", "melee"),
            _move(5, "R", "One For All Burst", "ultimate", "wind", "area"),
            _move(6, "DODGE", "Perfect Dodge Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Full Cowl", "buff ramp", "utility", "self"),
        ),
        (
            "BATTLE/HERO/lvgu/VO/One_For_All",
            "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01",
            "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01S",
            "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk03",
        ),
    ),
    "h1002": _style(
        "h1002",
        1021,
        "Explosion Brawler",
        "burst brawler",
        "Nitro Sweat",
        (
            _move(1, "ATK", "Explosion Combo", "basic combo", "explosion", "melee"),
            _move(2, "Q", "AP Shot", "line blast", "explosion", "ranged"),
            _move(3, "W", "Blast Rush", "gap closer", "explosion", "melee"),
            _move(4, "E", "Stun Grenade", "area control", "explosion", "area"),
            _move(5, "R", "Howitzer Impact", "ultimate", "explosion", "area"),
            _move(6, "DODGE", "Rush Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Nitro Stockpile", "resource ramp", "utility", "self"),
        ),
        (
            "BATTLE/HERO/baohao/commonATK/commonATK02",
            "BATTLE/HERO/baohao/commonATK/commonATK03_1",
            "BATTLE/HERO/baohao/commonATK/commonATK03_2",
            "BATTLE/HERO/baohao/commonATK/commonATK05",
            "BATTLE/HERO/baohao/skills/Qskill_EX",
            "BATTLE/HERO/baohao/skills/Qskill_EX_start",
        ),
    ),
    "h1003": _style(
        "h1003",
        1041,
        "Symbol of Peace",
        "power bruiser",
        "One For All stacks",
        (
            _move(1, "ATK", "Heavy Strike", "charged combo", "physical", "melee", "charge"),
            _move(2, "Q", "Detroit Smash", "air current", "wind", "mid"),
            _move(3, "W", "New Hampshire Smash", "dash punch", "wind", "melee"),
            _move(4, "E", "I Am Here", "slam engage", "physical", "area"),
            _move(5, "R", "United States of Smash", "ultimate", "wind", "area"),
            _move(6, "DODGE", "Expert Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Transferred Might", "attack ramp", "utility", "self"),
        ),
        (
            "BATTLE/HERO/allmight/VO/DIE",
            "BATTLE/HERO/allmight/VO/OP",
            "BATTLE/HERO/allmight/VO/Rskill_VO_01",
            "BATTLE/HERO/allmight/VO/Rskill_VO_02",
            "BATTLE/HERO/allmight/VO/Rskill_VO_03",
            "BATTLE/HERO/allmight/ability/ability",
            "BATTLE/HERO/allmight/commonATK/breakATK",
            "BATTLE/HERO/allmight/commonATK/commonATK_01",
            "BATTLE/HERO/allmight/commonATK/commonATK_01_01",
            "BATTLE/HERO/allmight/commonATK/commonATK_01_02",
            "BATTLE/HERO/allmight/commonATK/commonATK_02",
            "BATTLE/HERO/allmight/commonATK/commonATK_02_01",
            "BATTLE/HERO/allmight/commonATK/commonATK_02_02",
            "BATTLE/HERO/allmight/commonATK/commonATK_03_01",
            "BATTLE/HERO/allmight/commonATK/commonATK_03_02",
            "BATTLE/HERO/allmight/commonATK/commonATK_OVER_TIME",
            "BATTLE/HERO/allmight/commonATK/commonATK_dash",
            "BATTLE/HERO/allmight/commonATK/commonatk_atk4",
            "BATTLE/HERO/allmight/skills/Eskill_01",
            "BATTLE/HERO/allmight/skills/Eskill_02",
            "BATTLE/HERO/allmight/skills/Qskill_01",
            "BATTLE/HERO/allmight/skills/Qskill_02",
            "BATTLE/HERO/allmight/skills/Qskill_EX_01",
            "BATTLE/HERO/allmight/skills/Qskill_EX_02",
            "BATTLE/HERO/allmight/skills/Rskill",
            "BATTLE/HERO/allmight/skills/Wskill",
            "BATTLE/HERO/allmight/skills/dodge_skill",
        ),
    ),
    "h1004": _style(
        "h1004",
        1031,
        "Deflated Symbol",
        "support bruiser",
        "heroic resolve",
        (
            _move(1, "ATK", "Skinny Smash Combo", "measured combo", "physical", "melee"),
            _move(2, "Q", "Heroic Jab", "interrupt poke", "physical", "melee"),
            _move(3, "W", "Defensive Sidestep", "reposition", "utility", "self"),
            _move(4, "E", "Last-Second Uppercut", "launcher", "physical", "melee"),
            _move(5, "R", "Symbolic Rally", "ultimate support", "physical", "area"),
            _move(6, "DODGE", "Thin Dodge", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Heroic Resolve", "survival ramp", "utility", "self"),
        ),
    ),
    "h1006": _style(
        "h1006",
        1061,
        "Recipro Burst",
        "speed striker",
        "engine boost",
        (
            _move(1, "ATK", "Engine Kick Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Recipro Kick", "burst kick", "physical", "melee"),
            _move(3, "W", "Engine Dash", "gap closer", "physical", "dash"),
            _move(4, "E", "Spiral Kick", "launcher", "physical", "area"),
            _move(5, "R", "Recipro Burst", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Speed Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Engine Overdrive", "speed ramp", "utility", "self"),
        ),
    ),
    "h1007": _style(
        "h1007",
        1071,
        "Zero Gravity",
        "control skirmisher",
        "gravity marks",
        (
            _move(1, "ATK", "Gravity Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Meteor Storm", "projectile drop", "physical", "area"),
            _move(3, "W", "Weightless Pull", "crowd control", "gravity", "mid"),
            _move(4, "E", "Float Rush", "launcher", "gravity", "melee"),
            _move(5, "R", "Zero Gravity Field", "ultimate", "gravity", "area"),
            _move(6, "DODGE", "Float Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Weightless", "control ramp", "utility", "self"),
        ),
        (
            "BATTLE/HERO/yuchazi/VO/DIE",
            "BATTLE/HERO/yuchazi/ability/ability_run",
            "BATTLE/HERO/yuchazi/ability/ability_start",
            "BATTLE/HERO/yuchazi/ability/ability_static",
            "BATTLE/HERO/yuchazi/commonATK/ability_commonATK01",
            "BATTLE/HERO/yuchazi/commonATK/ability_commonATK02",
            "BATTLE/HERO/yuchazi/commonATK/breakATK_01",
            "BATTLE/HERO/yuchazi/commonATK/commonATK02",
            "BATTLE/HERO/yuchazi/commonATK/commonATK03",
            "BATTLE/HERO/yuchazi/commonATK/commonATK04",
            "BATTLE/HERO/yuchazi/commonATK/commonATK_dash_01",
            "BATTLE/HERO/yuchazi/skills/Eskill",
            "BATTLE/HERO/yuchazi/skills/Qskill",
            "BATTLE/HERO/yuchazi/skills/Wskill",
        ),
    ),
    "h1008": _style(
        "h1008",
        1081,
        "Half-Cold Half-Hot",
        "stance caster",
        "heat and cold",
        (
            _move(1, "ATK", "Ice Flame Combo", "basic combo", "mixed", "mid"),
            _move(2, "Q", "Flashfreeze Heatwave", "stance swap", "mixed", "area"),
            _move(3, "W", "Ice Wall Rush", "control dash", "ice", "mid"),
            _move(4, "E", "Flame Stream", "channeled damage", "fire", "area"),
            _move(5, "R", "Heaven-Piercing Ice Wall", "ultimate", "mixed", "area"),
            _move(6, "DODGE", "Frost Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Thermal Balance", "resource ramp", "utility", "self"),
        ),
    ),
    "h1009": _style(
        "h1009",
        1091,
        "Creation Arsenal",
        "weapon specialist",
        "creation charge",
        (
            _move(1, "ATK", "Bo Staff Combo", "weapon combo", "physical", "melee"),
            _move(2, "Q", "Created Cannon", "line blast", "physical", "ranged"),
            _move(3, "W", "Flash Grenade", "area control", "physical", "area"),
            _move(4, "E", "Shield Bash", "guard launcher", "physical", "melee"),
            _move(5, "R", "Arsenal Barrage", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Tactical Roll", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Creation Charge", "resource ramp", "utility", "self"),
        ),
    ),
    "h1010": _style(
        "h1010",
        1101,
        "Electrification",
        "area caster",
        "electric charge",
        (
            _move(1, "ATK", "Spark Combo", "basic combo", "electric", "mid"),
            _move(2, "Q", "Indiscriminate Shock", "area pulse", "electric", "area"),
            _move(3, "W", "Stun Disc", "ranged stun", "electric", "ranged"),
            _move(4, "E", "Lightning Dash", "gap closer", "electric", "melee"),
            _move(5, "R", "Million Volt Discharge", "ultimate", "electric", "area"),
            _move(6, "DODGE", "Static Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Charge Overload", "resource ramp", "utility", "self"),
        ),
    ),
    "h1012": _style(
        "h1012",
        1121,
        "Blue Flame",
        "burn caster",
        "Enflamed",
        (
            _move(1, "ATK", "Blue Flame Combo", "basic combo", "fire", "mid"),
            _move(2, "Q", "Scorched Earth", "burn field", "fire", "area"),
            _move(3, "W", "Flame Knockback", "control blast", "fire", "mid"),
            _move(4, "E", "Pillar of Flame", "burn stack", "fire", "area"),
            _move(5, "R", "Cremation", "ultimate", "fire", "area"),
            _move(6, "DODGE", "Blue Flame Dodge", "counter", "utility", "self"),
            _move(7, "PASSIVE", "Charcoaled", "burn ramp", "utility", "self"),
        ),
    ),
    "h1013": _style(
        "h1013",
        1131,
        "Hardening",
        "tank brawler",
        "hardening",
        (
            _move(1, "ATK", "Hardened Knuckle Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Red Counter", "guard counter", "physical", "melee"),
            _move(3, "W", "Shoulder Charge", "gap closer", "physical", "melee"),
            _move(4, "E", "Unbreakable Slam", "area stagger", "physical", "area"),
            _move(5, "R", "Red Riot Unbreakable", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Hardened Guard", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Hardening", "damage reduction ramp", "utility", "self"),
        ),
    ),
    "h1014": _style(
        "h1014",
        1141,
        "Frog Style",
        "agile control",
        "frog agility",
        (
            _move(1, "ATK", "Frog-Fu Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Tongue Snatch", "pull control", "physical", "ranged"),
            _move(3, "W", "Camouflage Leap", "reposition strike", "physical", "melee"),
            _move(4, "E", "Air Kick", "launcher", "physical", "melee"),
            _move(5, "R", "Froppy Ambush", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Wall-Hop Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Frog Agility", "mobility ramp", "utility", "self"),
        ),
    ),
    "h1015": _style(
        "h1015",
        1151,
        "Erasure Weapon",
        "technical controller",
        "combat stance",
        (
            _move(1, "ATK", "Assault Combo", "knife-cloth combo", "physical", "melee"),
            _move(2, "Q", "Battle Tactics", "stance switch", "utility", "self"),
            _move(3, "W", "Caltrops/Taijutsu", "range-adaptive", "physical", "mid"),
            _move(4, "E", "Remote Capture", "bind launcher", "physical", "ranged"),
            _move(5, "R", "Onslaught", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Flaw Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Erasure", "survival window", "utility", "self"),
        ),
    ),
    "h1016": _style(
        "h1016",
        1161,
        "Tail Martial Arts",
        "melee duelist",
        "tail momentum",
        (
            _move(1, "ATK", "Tail Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Tail Sweep", "knockdown", "physical", "area"),
            _move(3, "W", "Martial Dash", "gap closer", "physical", "melee"),
            _move(4, "E", "Rising Tail", "launcher", "physical", "melee"),
            _move(5, "R", "Spinning Tail Assault", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Tail Parry", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Tail Momentum", "combo ramp", "utility", "self"),
        ),
    ),
    "h1017": _style(
        "h1017",
        1171,
        "Acid Dance",
        "area skirmisher",
        "acid",
        (
            _move(1, "ATK", "Acid Kick Combo", "basic combo", "acid", "melee"),
            _move(2, "Q", "Acid Veil", "field hazard", "acid", "area"),
            _move(3, "W", "Slippery Slide", "gap closer", "acid", "melee"),
            _move(4, "E", "Acid Splash", "area burst", "acid", "area"),
            _move(5, "R", "Acidman Rush", "ultimate", "acid", "area"),
            _move(6, "DODGE", "Corrosive Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Acid Armor", "defense ramp", "utility", "self"),
        ),
    ),
    "h1018": _style(
        "h1018",
        1181,
        "Earphone Jack",
        "ranged controller",
        "sound waves",
        (
            _move(1, "ATK", "Jack Combo", "basic combo", "sound", "mid"),
            _move(2, "Q", "Heartbeat Wall", "wave blast", "sound", "ranged"),
            _move(3, "W", "Sonic Trap", "area control", "sound", "area"),
            _move(4, "E", "Amped Strike", "launcher", "sound", "mid"),
            _move(5, "R", "Heartbeat Surround", "ultimate", "sound", "area"),
            _move(6, "DODGE", "Sonic Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Sound Check", "control ramp", "utility", "self"),
        ),
    ),
    "h1019": _style(
        "h1019",
        1191,
        "Decay and Nomu Control",
        "summoner controller",
        "Spite",
        (
            _move(1, "ATK", "Decay Combo", "basic combo", "decay", "melee"),
            _move(2, "Q", "Nomu Smash", "summon strike", "decay", "area"),
            _move(3, "W", "Warp Gate Assault", "gap closer", "decay", "mid"),
            _move(4, "E", "Decay Grab", "throw control", "decay", "melee"),
            _move(5, "R", "Concretized Hatred", "ultimate", "decay", "area"),
            _move(6, "DODGE", "Deadly Gift", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Control Nomu", "summon mode", "utility", "self"),
        ),
    ),
    "h1020": _style(
        "h1020",
        1201,
        "Pop Off",
        "trap controller",
        "sticky balls",
        (
            _move(1, "ATK", "Sticky Toss Combo", "basic combo", "physical", "ranged"),
            _move(2, "Q", "Grape Trap", "root field", "physical", "area"),
            _move(3, "W", "Bounce Launch", "reposition", "physical", "melee"),
            _move(4, "E", "Sticky Barrage", "ranged burst", "physical", "ranged"),
            _move(5, "R", "Pop Off Rush", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Sticky Escape", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Sticky Setup", "trap ramp", "utility", "self"),
        ),
    ),
    "h1021": _style(
        "h1021",
        1211,
        "Hellflame Lance",
        "stance bruiser",
        "Temperature",
        (
            _move(1, "ATK", "Flaming Fists", "basic combo", "fire", "melee"),
            _move(2, "Q", "Fire Lance", "form swap", "fire", "mid"),
            _move(3, "W", "Prominence Rush", "defense ramp", "fire", "area"),
            _move(4, "E", "Pillar Sweep", "launcher", "fire", "area"),
            _move(5, "R", "Prominence Burn", "ultimate", "fire", "area"),
            _move(6, "DODGE", "Scorching Counter", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Temperature Shield", "resource shield", "utility", "self"),
        ),
    ),
    "h1022": _style(
        "h1022",
        1221,
        "Dark Shadow",
        "summoner brawler",
        "shadow",
        (
            _move(1, "ATK", "Shadow Talon Combo", "basic combo", "shadow", "mid"),
            _move(2, "Q", "Dark Shadow Lunge", "summon strike", "shadow", "melee"),
            _move(3, "W", "Shadow Guard", "defensive field", "shadow", "area"),
            _move(4, "E", "Black Abyss", "launcher", "shadow", "area"),
            _move(5, "R", "Ragnarok", "ultimate", "shadow", "area"),
            _move(6, "DODGE", "Shadow Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Dark Shadow", "summon ramp", "utility", "self"),
        ),
    ),
    "h1024": _style(
        "h1024",
        1241,
        "Alternate One For All",
        "mobile striker",
        "One For All charge",
        (
            _move(1, "ATK", "Full Cowl Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Air Force Shot", "ranged poke", "wind", "ranged"),
            _move(3, "W", "One For All Dash", "gap closer", "physical", "melee"),
            _move(4, "E", "Shoot Style Breaker", "launcher", "physical", "melee"),
            _move(5, "R", "Full Cowl Burst", "ultimate", "wind", "area"),
            _move(6, "DODGE", "Cowl Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Charge Control", "resource ramp", "utility", "self"),
        ),
    ),
    "h1026": _style(
        "h1026",
        1261,
        "Fierce Wings",
        "ranged stance striker",
        "Feathers",
        (
            _move(1, "ATK", "Feather Combo", "basic combo", "physical", "ranged"),
            _move(2, "Q", "Feather Guard", "auto attack field", "physical", "area"),
            _move(3, "W", "Marked Feather", "mark target", "physical", "ranged"),
            _move(4, "E", "Feather Rain", "area attack", "physical", "area"),
            _move(5, "R", "Hawks on High", "ultimate stance", "physical", "area"),
            _move(6, "DODGE", "Perfect Dodge", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Feather Control", "resource refresh", "utility", "self"),
        ),
    ),
    "h1027": _style(
        "h1027",
        1271,
        "WHM Fullpower",
        "agile striker",
        "Fullpower status",
        (
            _move(1, "ATK", "WHM Shoot Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Blackwhip Snare", "pull control", "physical", "ranged"),
            _move(3, "W", "Fullpower Rush", "gap closer", "physical", "melee"),
            _move(4, "E", "Aerial Smash", "launcher", "wind", "area"),
            _move(5, "R", "World Heroes Smash", "ultimate", "wind", "area"),
            _move(6, "DODGE", "Fullpower Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Fullpower Status", "buff ramp", "utility", "self"),
        ),
    ),
    "h1028": _style(
        "h1028",
        1281,
        "WHM Air Strike",
        "aerial blaster",
        "Sweat",
        (
            _move(1, "ATK", "Aerial Explosion Combo", "basic combo", "explosion", "mid"),
            _move(2, "Q", "Cluster Shot", "ranged blast", "explosion", "ranged"),
            _move(3, "W", "Boost Burst", "gap closer", "explosion", "melee"),
            _move(4, "E", "Air Mine", "area control", "explosion", "area"),
            _move(5, "R", "WHM Howitzer", "ultimate", "explosion", "area"),
            _move(6, "DODGE", "Blast Drift", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Sweat Reserve", "resource ramp", "utility", "self"),
        ),
    ),
    "h1029": _style(
        "h1029",
        1291,
        "WHM Frost Blaze",
        "stance caster",
        "heat and cold",
        (
            _move(1, "ATK", "WHM Icefire Combo", "basic combo", "mixed", "mid"),
            _move(2, "Q", "Ice Rampart", "control wall", "ice", "area"),
            _move(3, "W", "Flashfreeze Chase", "gap closer", "ice", "mid"),
            _move(4, "E", "Flame Burst", "area burst", "fire", "area"),
            _move(5, "R", "WHM Flashfreeze Heatwave", "ultimate", "mixed", "area"),
            _move(6, "DODGE", "Thermal Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Heat-Cold Balance", "stance ramp", "utility", "self"),
        ),
    ),
    "h1030": _style(
        "h1030",
        1301,
        "Wave Motion",
        "vitality caster",
        "Vitality",
        (
            _move(1, "ATK", "Wave Beam Combo", "basic combo", "energy", "ranged"),
            _move(2, "Q", "Spiral Wave", "ranged burst", "energy", "ranged"),
            _move(3, "W", "Vitality Float", "reposition", "utility", "self"),
            _move(4, "E", "Wave Ring", "area control", "energy", "area"),
            _move(5, "R", "Full Wave Motion", "ultimate", "energy", "area"),
            _move(6, "DODGE", "Wave Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Vitality Charge", "resource ramp", "utility", "self"),
        ),
    ),
    "h1031": _style(
        "h1031",
        1311,
        "Manifest",
        "form switcher",
        "Proficiency",
        (
            _move(1, "ATK", "Manifest Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Tentacle Strike", "pull control", "physical", "ranged"),
            _move(3, "W", "Clam Guard", "defensive stance", "utility", "self"),
            _move(4, "E", "Chimera Rush", "gap closer", "physical", "melee"),
            _move(5, "R", "Vast Hybrid Manifest", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Manifest Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Proficiency", "form ramp", "utility", "self"),
        ),
    ),
    "h1032": _style(
        "h1032",
        1321,
        "Permeation",
        "stance striker",
        "Charge",
        (
            _move(1, "ATK", "Phantom Combo", "basic combo", "physical", "melee"),
            _move(2, "Q", "Phantom Menace", "phase strike", "physical", "melee"),
            _move(3, "W", "Permeation Step", "reposition", "utility", "self"),
            _move(4, "E", "Surprise Uppercut", "launcher", "physical", "melee"),
            _move(5, "R", "Power!", "ultimate", "physical", "area"),
            _move(6, "DODGE", "Phase Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Permeation Charge", "resource ramp", "utility", "self"),
        ),
    ),
    "h1110": _style(
        "h1110",
        1111,
        "Bloodcurdle",
        "bleed duelist",
        "Vigor",
        (
            _move(1, "ATK", "Cull", "combo finisher", "physical", "melee"),
            _move(2, "Q", "Aura of Fear", "area pressure", "physical", "area"),
            _move(3, "W", "Dagger Strike", "fan projectile", "physical", "ranged"),
            _move(4, "E", "Blade Dance", "air combo", "physical", "melee"),
            _move(5, "R", "Verdict", "ultimate line", "physical", "ranged"),
            _move(6, "DODGE", "Shadowy Surprise", "slow counter", "utility", "self"),
            _move(7, "PASSIVE", "Bloodcurdle", "hit recovery control", "utility", "self"),
        ),
    ),
    "h1998": _style(
        "h1998",
        1981,
        "All Might Variant",
        "power bruiser",
        "test energy",
        (
            _move(1, "ATK", "Variant Smash Combo", "heavy combo", "physical", "melee"),
            _move(2, "Q", "Variant Detroit Smash", "air current", "wind", "mid"),
            _move(3, "W", "Variant Rush", "dash punch", "physical", "melee"),
            _move(4, "E", "Variant Shockwave", "area stagger", "wind", "area"),
            _move(5, "R", "Variant United Smash", "ultimate", "wind", "area"),
            _move(6, "DODGE", "Variant Counter", "defensive counter", "utility", "self"),
            _move(7, "PASSIVE", "Test Energy", "attack ramp", "utility", "self"),
        ),
    ),
}


FIGHT_STYLES_BY_HERO_ID = {
    style.hero_id: style for style in FIGHT_STYLES_BY_MODEL.values()
}


def fight_style_for_character(character: PlayableCharacter) -> FightStyle:
    if character.hero_id is None:
        raise ValueError(f"{character.model_asset_id} has no verified HeroId")
    try:
        return FIGHT_STYLES_BY_HERO_ID[character.hero_id]
    except KeyError:
        return FightStyle(
            model_asset_id=character.model_asset_id,
            hero_id=character.hero_id,
            style_name=character.name,
            archetype="unclassified fighter",
            resource="unknown",
            moves=DEFAULT_MOVES,
        )


def fight_style_for_hero_id(hero_id: int) -> FightStyle:
    return FIGHT_STYLES_BY_HERO_ID[int(hero_id)]
