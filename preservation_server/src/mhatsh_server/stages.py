from __future__ import annotations

from dataclasses import dataclass, field

from .allsvr_stages import (
    ALLSVR_BOSS_STAGE_BY_BOSS_AND_DIFFICULTY,
    ALLSVR_BOSS_STAGE_BY_ID,
    ALLSVR_BOSS_STAGES,
    ALLSVR_COND_IDS,
    ALLSVR_STAGE_BY_ID,
    ALLSVR_STAGE_SOURCE,
    ALLSVR_STAGES,
    DEFAULT_ALLSVR_BOSS_STAGE,
    DEFAULT_ALLSVR_STAGE,
)
from .area_event_stages import (
    AREA_EVENT_STAGE_BY_ID,
    AREA_EVENT_STAGES,
    AREA_EVENT_STAGE_SOURCE,
)
from .act_daily_stages import (
    ACT_DAILY_MONSTER_IDS,
    ACT_DAILY_STAGE_SOURCE,
    ACT_DAILY_STAGES,
)
from .combat import CombatResolution, FightStyle
from .empty_shop_stages import (
    DEFAULT_EMPTY_SHOP_STAGE,
    EMPTY_SHOP_STAGE_BY_CHALLENGE_INDEX,
    EMPTY_SHOP_STAGE_BY_INDEX,
    EMPTY_SHOP_STAGE_SOURCE,
    EMPTY_SHOP_STAGES,
)
from .herochip_stages import HEROCHIP_STAGE_SOURCE, HEROCHIP_STAGES
from .relax_stages import RELAX_STAGE_BY_ID, RELAX_STAGE_SOURCE, RELAX_STAGES
from .roguelike_stages import ROGUELIKE_STAGE_SOURCE, ROGUELIKE_STAGES
from .secret_area_stages import (
    DEFAULT_SECRET_AREA_STAGE,
    SECRET_AREA_STAGE_BY_ID,
    SECRET_AREA_STAGE_SOURCE,
    SECRET_AREA_STAGES,
)
from .usj_stages import USJ_POINT_BY_ID, USJ_POINTS, USJ_STAGE_SOURCE, USJ_STAGES


STARTER_INTRO_STAGE_ID = 299301
STARTER_INTRO_STAGE_UID = 2993010001
STARTER_INTRO_STAGE_LEVEL = 1
STARTER_INTRO_STAGE_TIME = 300
STARTER_INTRO_STAGE_DRAMA = 1
STAGE_CATALOG_SOURCE = (
    "analysis/intro_qte_asset_index.txt and "
    "analysis/battle_stage_candidate_catalog.json, 2026-06-23"
)
LOCAL_STAGE_PASS_REWARD_ITEM_ID = 1001
LOCAL_STAGE_FIRST_REWARD_ITEM_ID = 1002
LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID = 1003
LOCAL_STAGE_STYLE_REWARD_ITEM_ID = 1004
NIGHT_FIGHT_DEFAULT_STAGE_IDS = (160001, 299301, 502601)


@dataclass(frozen=True, slots=True)
class EnemyAIProfile:
    key: str
    bt_name: str
    behavior: str
    attack_range: int
    leash_radius: int
    skill_rotation: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MonsterCfgEvidence:
    monster_id: int
    preferred_name: str
    display_names: tuple[str, ...] = ()
    animation_keys: tuple[str, ...] = ()
    source: str = (
        "analysis/mediafire_20260620/apk_extract/assets/1FO/fee3a47c0b4a95e9, "
        "parsed by scripts/derive_monster_cfg_hints.py, 2026-06-23"
    )


@dataclass(frozen=True, slots=True)
class StageEnemySpawn:
    label: str
    enemy_id: int
    shape_id: int
    uid: int
    x: int
    y: int
    z: int = 0
    face: int = 0
    level: int = 1
    group_id: int = 0
    ai_profile_key: str = "melee_chaser"

    @property
    def ai_profile(self) -> EnemyAIProfile:
        return ENEMY_AI_PROFILES[self.ai_profile_key]

    @property
    def monster_cfg_evidence(self) -> MonsterCfgEvidence | None:
        return MONSTER_CFG_EVIDENCE_BY_ID.get(self.enemy_id)

    @property
    def display_name(self) -> str:
        evidence = self.monster_cfg_evidence
        return evidence.preferred_name if evidence is not None else self.label

    @property
    def placement_source(self) -> str:
        if self.label.startswith("stage_cfg_authored_"):
            return "stage_cfg_authored"
        if self.label.startswith("stage_cfg_"):
            return "stage_cfg_generated"
        if self.label.startswith("generated_stage_"):
            return "generated_fallback"
        return "explicit"

    @property
    def is_authored_placement(self) -> bool:
        return self.placement_source in {"explicit", "stage_cfg_authored"}

    @property
    def combat_hp(self) -> int:
        base_hp = 1600 + max(1, int(self.level)) * 45
        if self.ai_profile_key in {
            "sludge_boss",
            "boss_brute",
            "nomu_brute",
            "mechanical_boss",
        }:
            base_hp += 1800
        return base_hp

    def to_scene_npc(self) -> dict[str, object]:
        return {
            "Uid": self.uid,
            "Id": self.enemy_id,
            "X": self.x,
            "Y": self.y,
            "Z": self.z,
            "Face": self.face,
            "Version": 1,
            "ShapeId": self.shape_id,
            "Attach": [],
            "HideStatus": 0,
            "AreaId": 0,
            "StartAnim": "",
            "BTName": self.ai_profile.bt_name,
            "ForceShow": 1,
        }

    def to_monster_frame_seed(self) -> dict[str, object]:
        return {
            "Uid": self.uid,
            "Type": 1,
            "X": self.x,
            "Y": self.y,
            "BoxFullMode": 0,
            "OwnerUid": 0,
            "CurFrame": 0,
            "CurAni": "idle",
            "CurAniTime": 0,
            "CurAnimationIdx": 0,
            "State": 0,
            "BodyBlock": 0,
            "ReplaceRunAni": "",
            "Camp": 1,
            "RotationY": self.face,
            "SkillId": 0,
            "Info": {
                "Id": self.enemy_id,
                "Face": self.face,
                "ShapeVer": 1,
                "MissionLv": self.level,
                "StartAnim": "",
                "DropList": [],
                "MoneyList": [],
                "Alias": self.display_name,
                "GroupId": self.group_id,
                "BallId": 0,
                "AreaId": 0,
                "WallNormal": [],
                "Level": self.level,
                "BTParam": list(self.ai_profile.skill_rotation),
                "bNotAsync": 0,
            },
        }

    def to_ai_directive(self) -> dict[str, object]:
        profile = self.ai_profile
        return {
            "Uid": self.uid,
            "EnemyId": self.enemy_id,
            "Alias": self.display_name,
            "Profile": profile.key,
            "Behavior": profile.behavior,
            "BTName": profile.bt_name,
            "Home": {"X": self.x, "Y": self.y, "Z": self.z, "Face": self.face},
            "AttackRange": profile.attack_range,
            "LeashRadius": profile.leash_radius,
            "SkillRotation": list(profile.skill_rotation),
            "CombatHp": self.combat_hp,
            "PlacementSource": self.placement_source,
            "AuthoredPlacement": int(self.is_authored_placement),
        }


@dataclass(frozen=True, slots=True)
class StageEnemyCombatResult:
    uid: int
    enemy_id: int
    label: str
    display_name: str
    ai_profile_key: str
    placement_source: str
    authored_placement: bool
    max_hp: int
    damage_taken: int
    defeated: bool
    last_skill: str
    threat_score: int
    action_hint: str

    def as_dict(self) -> dict[str, object]:
        return {
            "Uid": self.uid,
            "EnemyId": self.enemy_id,
            "Label": self.label,
            "DisplayName": self.display_name,
            "AIProfile": self.ai_profile_key,
            "PlacementSource": self.placement_source,
            "AuthoredPlacement": int(self.authored_placement),
            "MaxHP": self.max_hp,
            "DamageTaken": self.damage_taken,
            "Defeated": int(self.defeated),
            "LastSkill": self.last_skill,
            "ThreatScore": self.threat_score,
            "ActionHint": self.action_hint,
        }


@dataclass(frozen=True, slots=True)
class StageCompletion:
    stage_id: int
    status: int = 0
    stars: tuple[int, ...] = ()
    full_star_time: int = 0
    best_time: int = 0
    pass_count: int = 0

    def to_stage_info(self) -> dict[str, object]:
        return {
            "Id": self.stage_id,
            "Status": self.status,
            "StarList": list(self.stars),
            "FullStarTime": self.full_star_time,
        }

    def to_profile(self) -> dict[str, int | list[int]]:
        return {
            "status": self.status,
            "stars": list(self.stars),
            "full_star_time": self.full_star_time,
            "best_time": self.best_time,
            "pass_count": self.pass_count,
        }

    @classmethod
    def from_profile(
        cls, stage_id: int, values: dict[str, object]
    ) -> "StageCompletion":
        return cls(
            stage_id=stage_id,
            status=_as_int(values.get("status")),
            stars=tuple(_as_int(item) for item in list(values.get("stars") or [])),
            full_star_time=_as_int(values.get("full_star_time")),
            best_time=_as_int(values.get("best_time")),
            pass_count=_as_int(values.get("pass_count")),
        )


@dataclass(frozen=True, slots=True)
class BattleStageDefinition:
    key: str
    label: str
    stage_id: int | None
    stage_uid: int | None = None
    level: int = STARTER_INTRO_STAGE_LEVEL
    time_limit: int = STARTER_INTRO_STAGE_TIME
    drama: int = STARTER_INTRO_STAGE_DRAMA
    scripts: tuple[str, ...] = ()
    audio_events: tuple[str, ...] = ()
    actor_sets: tuple[str, ...] = ()
    video_assets: tuple[str, ...] = ()
    character_refs: tuple[str, ...] = ()
    enemy_group_ids: tuple[int, ...] = ()
    enemy_spawns: tuple[StageEnemySpawn, ...] = ()
    source: str = STAGE_CATALOG_SOURCE

    @property
    def can_enter_by_stage_id(self) -> bool:
        return self.stage_id is not None

    @property
    def resolved_stage_uid(self) -> int:
        if self.stage_uid is not None:
            return self.stage_uid
        if self.stage_id is None:
            raise ValueError(f"{self.key} has no numeric stage id")
        return self.stage_id * 10000 + 1

    @property
    def encounter_spawns(self) -> tuple[StageEnemySpawn, ...]:
        if self.enemy_spawns:
            return self.enemy_spawns
        stage_cfg_spawns = stage_cfg_enemy_spawns(self.stage_id, self.combat_enemy_ids)
        if stage_cfg_spawns:
            return stage_cfg_spawns
        return generated_stage_spawns(self.stage_id)

    @property
    def combat_enemy_ids(self) -> tuple[int, ...]:
        if self.enemy_spawns:
            return tuple(spawn.enemy_id for spawn in self.enemy_spawns)
        if self.stage_id is None:
            return ()
        return STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE.get(int(self.stage_id), ())

    @property
    def encounter_target_count(self) -> int:
        return len(self.encounter_spawns)


MONSTER_CFG_EVIDENCE_BY_ID = {
    2005: MonsterCfgEvidence(
        monster_id=2005,
        preferred_name="Giant Villain",
        display_names=("Giant Villain", "Gigantification", "Scavenger", "Thug"),
        animation_keys=(
            "2005_b1_01",
            "2005_b2_01",
            "2005_b2_02",
            "2005_b2_03",
            "2005_b2_04",
            "2005_b2_05",
            "2005_b3_01",
            "2005_b3_02",
            "2005_b4_01",
            "2005_d7_01",
        ),
    ),
    2202: MonsterCfgEvidence(
        monster_id=2202,
        preferred_name="Monstrous Lizard",
        display_names=("Monstrous Lizard", "Sharp Blade"),
        animation_keys=(
            "2202_a1_01",
            "2202_b1_01",
            "2202_c2_01",
            "2202_c2_02",
            "2202_c2_03",
            "2202_c2_04",
            "2202_d1_01",
            "2202_d1_02",
            "2202_d1_03",
            "2202_kong",
        ),
    ),
    2470: MonsterCfgEvidence(
        monster_id=2470,
        preferred_name="Twice",
        display_names=("Twice",),
        animation_keys=("2470_a1_01",),
    ),
    2471: MonsterCfgEvidence(
        monster_id=2471,
        preferred_name="Twice",
        display_names=("Twice",),
        animation_keys=("2471_a1_01",),
    ),
    2472: MonsterCfgEvidence(
        monster_id=2472,
        preferred_name="Twice",
        display_names=("Twice",),
        animation_keys=("2472_a1_01", "2472_a1_02", "2472_a1_03"),
    ),
    3005: MonsterCfgEvidence(
        monster_id=3005,
        preferred_name="Faux Villain",
        display_names=("Faux Villain",),
        animation_keys=("3005_d1_01",),
    ),
    3006: MonsterCfgEvidence(
        monster_id=3006,
        preferred_name="Hanzo Suiden",
        display_names=("Hanzo Suiden", "Water", "Cyclone", "Shark"),
        animation_keys=(
            "3006_30",
            "3006_40",
            "3006_40_1",
            "3006_c3_01",
            "3006_c4_01",
            "3006_d3_01",
        ),
    ),
    3007: MonsterCfgEvidence(
        monster_id=3007,
        preferred_name="Nomu",
        display_names=("Nomu", "Gigantification", "Scavenger"),
        animation_keys=(
            "3007_60_11",
            "3007_b2_01",
            "3007_b2_02",
            "3007_b2_03",
            "3007_b2_04",
            "3007_b2_05",
            "3007_b2_06",
            "3007_c6_04",
            "3007_d1_01",
            "3007_d5_01",
            "3007_d5_02",
            "3007_heroplay",
        ),
    ),
    3016: MonsterCfgEvidence(
        monster_id=3016,
        preferred_name="Muscular",
        display_names=("Muscular",),
        animation_keys=("3016_c2_01",),
    ),
}


ENEMY_AI_PROFILES = {
    "melee_chaser": EnemyAIProfile(
        key="melee_chaser",
        bt_name="bt_preservation_melee_chaser",
        behavior="close distance, use basic attacks, reset when far from spawn",
        attack_range=220,
        leash_radius=1800,
        skill_rotation=("common_atk_01", "common_atk_02"),
    ),
    "sludge_boss": EnemyAIProfile(
        key="sludge_boss",
        bt_name="bt_preservation_sludge_boss",
        behavior="slow boss pressure with short melee strings and QTE-friendly pauses",
        attack_range=360,
        leash_radius=2200,
        skill_rotation=("sludge_grab", "sludge_slam", "sludge_recover"),
    ),
    "training_enemy": EnemyAIProfile(
        key="training_enemy",
        bt_name="bt_preservation_training_enemy",
        behavior="low-aggression tutorial target used for move validation",
        attack_range=180,
        leash_radius=1200,
        skill_rotation=("idle_guard", "common_atk_01"),
    ),
    "elite_chaser": EnemyAIProfile(
        key="elite_chaser",
        bt_name="bt_preservation_elite_chaser",
        behavior="aggressive elite melee enemy with faster pursuit and combo pressure",
        attack_range=280,
        leash_radius=2200,
        skill_rotation=("elite_dash", "elite_combo", "heavy_followup"),
    ),
    "boss_brute": EnemyAIProfile(
        key="boss_brute",
        bt_name="bt_preservation_boss_brute",
        behavior="large enemy pressure pattern for Nomu/mech style candidates",
        attack_range=420,
        leash_radius=2600,
        skill_rotation=("heavy_swing", "ground_slam", "reposition"),
    ),
    "nomu_brute": EnemyAIProfile(
        key="nomu_brute",
        bt_name="bt_preservation_nomu_brute",
        behavior="armored brawler with slow pursuit and interrupt-heavy swings",
        attack_range=440,
        leash_radius=2600,
        skill_rotation=("nomu_charge", "nomu_swing", "nomu_roar"),
    ),
    "mechanical_boss": EnemyAIProfile(
        key="mechanical_boss",
        bt_name="bt_preservation_mechanical_boss",
        behavior="large mechanical boss probe with telegraphed area attacks",
        attack_range=500,
        leash_radius=2800,
        skill_rotation=("mech_stomp", "mech_sweep", "mech_missile"),
    ),
    "mechanical_patrol": EnemyAIProfile(
        key="mechanical_patrol",
        bt_name="bt_preservation_mechanical_patrol",
        behavior="mechanical small enemy with patrol-style pursuit and burst attacks",
        attack_range=360,
        leash_radius=2200,
        skill_rotation=("mech_patrol", "mech_burst", "mech_reposition"),
    ),
    "ranged_pressure": EnemyAIProfile(
        key="ranged_pressure",
        bt_name="bt_preservation_ranged_pressure",
        behavior="keeps distance and fires intermittent ranged attacks",
        attack_range=620,
        leash_radius=2100,
        skill_rotation=("ranged_shot", "strafe", "ranged_burst"),
    ),
}


STARTER_STAGE_ENEMIES = (
    StageEnemySpawn(
        label="starter_sludge_villain_probe",
        enemy_id=3002,
        shape_id=3002,
        uid=3003001,
        x=4560,
        y=19980,
        face=180,
        level=1,
        group_id=3003001,
        ai_profile_key="sludge_boss",
    ),
    StageEnemySpawn(
        label="starter_training_enemy_probe",
        enemy_id=2005,
        shape_id=2005,
        uid=3003002,
        x=4800,
        y=20120,
        face=180,
        level=1,
        group_id=3003002,
        ai_profile_key="training_enemy",
    ),
)


def generated_stage_spawns(stage_id: int | None) -> tuple[StageEnemySpawn, ...]:
    if stage_id is None:
        return ()
    stage = int(stage_id)
    if stage == 500:
        enemy_ids = (2005,)
    elif stage >= 560000:
        enemy_ids = (2202, 2472, 3007)
    elif stage >= 500000:
        enemy_ids = (3002, 3007)
    elif stage >= 420000:
        enemy_ids = (2470, 2202, 3005)
    elif stage >= 400000:
        enemy_ids = (2202, 2005, 2202)
    elif stage >= 200000:
        enemy_ids = (2005, 2202)
    else:
        enemy_ids = (2005,)

    base_x = ((stage % 11) - 5) * 120
    base_y = ((stage // 10 % 11) - 5) * 120
    return tuple(
        StageEnemySpawn(
            label=f"generated_stage_{stage}_enemy_{index + 1}",
            enemy_id=enemy_id,
            shape_id=enemy_id,
            uid=stage * 100 + index + 1,
            x=base_x + index * 180,
            y=base_y + index * 140,
            level=1 + (stage % 4),
            group_id=stage,
            ai_profile_key=generated_enemy_profile_key(enemy_id),
        )
        for index, enemy_id in enumerate(enemy_ids)
    )


def stage_cfg_enemy_spawns(
    stage_id: int | None,
    combat_enemy_ids: tuple[int, ...],
) -> tuple[StageEnemySpawn, ...]:
    if stage_id is None or not combat_enemy_ids:
        return ()

    stage = int(stage_id)
    enemy_ids = combat_enemy_ids
    authored_spawns = {
        spawn.enemy_id: spawn
        for spawn in STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE.get(stage, ())
    }
    base_x = ((stage % 13) - 6) * 150
    base_y = ((stage // 10 % 13) - 6) * 150
    spawns: list[StageEnemySpawn] = []
    for index, enemy_id in enumerate(enemy_ids):
        authored_spawn = authored_spawns.get(enemy_id)
        if authored_spawn is not None:
            spawns.append(authored_spawn)
            continue
        spawns.append(
            StageEnemySpawn(
                label=f"stage_cfg_{stage}_enemy_{enemy_id}",
                enemy_id=enemy_id,
                shape_id=enemy_id,
                uid=enemy_id,
                x=base_x + index * 160,
                y=base_y + index * 120,
                level=1 + (stage % 5),
                group_id=stage,
                ai_profile_key=generated_enemy_profile_key(enemy_id),
            )
        )
    return tuple(spawns)


def generated_enemy_profile_key(enemy_id: int) -> str:
    override = STAGE_CFG_AI_PROFILE_OVERRIDES_BY_ENEMY_ID.get(enemy_id)
    if override is not None:
        return override
    if enemy_id == 3002:
        return "sludge_boss"
    if enemy_id in {2470, 2471, 3007, 31040301}:
        return "nomu_brute"
    if enemy_id == 3005:
        return "mechanical_boss"
    if enemy_id in {2472, 5008, 5015, 56390302}:
        return "ranged_pressure"
    if enemy_id == 2005:
        return "training_enemy"
    return "melee_chaser"


STAGE_CFG_AI_PROFILE_OVERRIDES_BY_ENEMY_ID: dict[int, str] = {
    16000101: "boss_brute",
    30040104: "elite_chaser",
    30040108: "boss_brute",
    30040109: "elite_chaser",
    31040301: "nomu_brute",
    40011512: "elite_chaser",
    40011513: "elite_chaser",
    40011514: "boss_brute",
    40011801: "nomu_brute",
    40510301: "mechanical_patrol",
    40510304: "mechanical_patrol",
    40525201: "mechanical_patrol",
    40525202: "mechanical_patrol",
    40525203: "mechanical_patrol",
    40525204: "mechanical_patrol",
    40525251: "mechanical_patrol",
    40525272: "mechanical_patrol",
    40620504: "elite_chaser",
    40650202: "elite_chaser",
    40650205: "ranged_pressure",
    40650504: "elite_chaser",
    40650603: "boss_brute",
    56111503: "mechanical_patrol",
    56111505: "mechanical_patrol",
    56120303: "elite_chaser",
    56121103: "boss_brute",
    56130412: "ranged_pressure",
    56240652: "elite_chaser",
    56240751: "elite_chaser",
    56250410: "elite_chaser",
    56261004: "elite_chaser",
    56370101: "elite_chaser",
    56370103: "elite_chaser",
    56390302: "ranged_pressure",
    56390303: "elite_chaser",
}


EXPLICIT_RECOVERED_STAGE_IDS = {
    STARTER_INTRO_STAGE_ID,
    500,
    160001,
    200508,
    200509,
    404103,
    404105,
    404201,
    404204,
    404205,
    404402,
    404405,
    406405,
    406502,
    406505,
    406506,
    420001,
    501201,
    502601,
    561203,
}


ZX_NUMERIC_STAGE_SCRIPT_GROUPS: dict[int, tuple[str, ...]] = {
    50206: ("zx_50206_1", "zx_50206_2"),
    101002: ("zx_101002_1",),
    101101: ("zx_101101_1",),
    102003: ("zx_102003_1",),
    103006: ("zx_103006_1",),
    201006: (
        "zx_201006_1",
        "zx_201006_2",
        "zx_201006_3",
        "zx_201006_4",
        "zx_201006_5",
    ),
    201008: ("zx_201008_1", "zx_201008_2"),
    201009: ("zx_201009_2", "zx_201009_3", "zx_201009_4"),
    201101: ("zx_201101_1", "zx_201101_2", "zx_201101_3"),
    201103: (
        "zx_201103_1",
        "zx_201103_2",
        "zx_201103_3",
        "zx_201103_5",
    ),
    201104: ("zx_201104_1",),
    201105: ("zx_201105_1",),
    201107: ("zx_201107",),
    202102: ("zx_202102_1",),
    202105: ("zx_202105_2",),
    301201: ("zx_301201_1",),
    301202: ("zx_301202_2",),
    301203: ("zx_301203_3",),
    301204: ("zx_301204_3",),
    402009: ("zx_402009_1",),
    402010: ("zx_402010_1",),
    404001: (
        "zx_404001_1",
        "zx_404001_2",
        "zx_404001_21",
        "zx_404001_22",
        "zx_404001_23",
        "zx_404001_3",
    ),
    404002: ("zx_404002_1", "zx_404002_2"),
    404003: ("zx_404003_1", "zx_404003_2"),
    404004: ("zx_404004_1",),
    404005: ("zx_404005_1",),
    404006: (
        "zx_404006_1",
        "zx_404006_11",
        "zx_404006_12",
        "zx_404006_13",
        "zx_404006_21",
        "zx_404006_22",
        "zx_404006_31",
        "zx_404006_32",
        "zx_404006_33",
    ),
    501007: ("zx_501007_1",),
    501101: ("zx_501101_1_copy", "zx_501101_2", "zx_501101_3"),
    501103: ("zx_501103_1", "zx_501103_2", "zx_501103_3"),
    501104: ("zx_501104_1",),
    502104: ("zx_502104_1",),
    502105: ("zx_502105_1",),
    502106: ("zx_502106_1",),
    502107: ("zx_502107_1", "zx_502107_2", "zx_502107_3"),
    502108: ("zx_502108_1",),
    561004: ("zx_561004",),
    561201: ("zx_561201_1", "zx_561201_2", "zx_561201_3"),
    561221: ("zx_561221_1", "zx_561221_2", "zx_561221_3", "zx_561221_4"),
    561222: ("zx_561222_1", "zx_561222_2", "zx_561222_3"),
    561224: ("zx_561224_2",),
    562402: ("zx_562402_1",),
    562403: ("zx_562403_1",),
    562406: ("zx_562406_1", "zx_562406_2", "zx_562406_3"),
    562407: ("zx_562407_1", "zx_562407_2"),
    562504: ("zx_562504_1",),
    562606: ("zx_562606_1",),
    602007: ("zx_602007_1",),
    801201: ("zx_801201_1", "zx_801201_3", "zx_801201_5", "zx_801201_6", "zx_801201_7"),
    801202: ("zx_801202_1",),
    801204: ("zx_801204_1",),
    801205: ("zx_801205_1", "zx_801205_2"),
    801206: ("zx_801206_1",),
}


ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS: dict[int, tuple[str, ...]] = {
    101201: ("101201_1", "101201_2"),
    101203: ("101203_1",),
    200503: ("200503",),
    200504: ("200504",),
    200505: ("200505_1",),
    200506: ("200506",),
    200507: ("200507_1",),
    300406: ("300406",),
    300503: ("300503_01", "300503_02"),
    350010: ("350010", "350010_end"),
    360401: ("360401", "360401_1"),
    360402: ("360402_1",),
    360403: ("360403_1",),
    400006: ("400006_boss",),
    400301: ("400301_1", "400301_2", "400301_3"),
    400302: ("400302", "400302_1", "400302_2", "400302_3"),
    400303: ("400303", "400303_1", "400303_2", "400303_3"),
    400304: ("400304", "400304_1", "400304_2", "400304_3"),
    400305: ("400305", "400305_1", "400305_2", "400305_3"),
    400306: ("400306_1", "400306_2", "400306_3"),
    403301: ("403301",),
    403302: ("403302",),
    403304: ("403304",),
    403352: ("403352", "403352_2"),
    403361: ("403361",),
    404101: ("404101",),
    404102: ("404102",),
    404202: ("404202",),
    404301: ("404301",),
    404303: ("404303_1",),
    404305: ("404305",),
    404306: ("404306",),
    404401: ("404401",),
    405401: ("405401",),
    405402: ("405402", "405402_1"),
    405403: ("405403",),
    405404: ("405404",),
    405405: ("405405",),
    405406: ("405406",),
    405501: ("405501",),
    405506: ("405506",),
    406401: ("406401",),
    406403: ("406403",),
    406406: ("406406", "406406_1"),
    406451: ("406451", "406451_1"),
    406452: ("406452",),
    411351: ("411351",),
    501301: ("501301-1", "501301-2", "501301-3", "501301-4"),
    501403: ("501403",),
    510003: ("510003",),
    511001: ("511001",),
    511002: ("511002",),
    511003: ("511003",),
    511004: ("511004",),
    511005: ("511005",),
    511006: ("511006", "511006_1"),
    511007: ("511007",),
    511008: ("511008",),
    520001: ("520001",),
    520002: ("520002",),
    520003: ("520003",),
    520004: ("520004",),
    520005: ("520005",),
    520006: ("520006",),
    520007: ("520007",),
    520015: ("520015",),
    520016: ("520016",),
    520017: ("520017",),
    520018: ("520018",),
    520019: ("520019",),
    520020: ("520020",),
    520021: ("520021",),
    530001: ("530001",),
    530002: ("530002",),
    530003: ("530003",),
    530004: ("530004",),
    530005: ("530005",),
    530006: ("530006",),
    530007: ("530007",),
    561002: ("561002", "561002_1"),
    561223: ("561223",),
    561225: (
        "561225",
        "561225_1",
        "561225_2",
        "561225_3",
        "561225_4",
        "561225_5",
    ),
    561304: ("561304", "561304_1"),
    561310: ("561310",),
    606001: ("606001",),
    901003: ("901003",),
    901004: ("901004",),
    901005: ("901005",),
    901006: ("901006",),
    901007: ("901007",),
    901008: ("901008",),
}


STAGE_CFG_SCRIPT_ROUTE_GROUPS: dict[int, tuple[str, ...]] = {
    160001: ("stage160001_lose", "stage160001_start", "stage160001_win"),
    201005: ("act_signal",),
    201006: ("chase_end",),
    300301: ("zx_touqiu",),
    300401: ("zx_usj_002",),
    300502: ("zx_tyj03",),
    300505: ("zx_tyj05",),
    310403: ("zx_usj_03002",),
    400115: ("tyj_400116", "tyj_400117"),
    400118: ("tyj_400118",),
    404105: ("stage404105",),
    404201: ("stage404201",),
    404205: ("stage404205_1",),
    405103: ("area5_1_3",),
    405252: ("area6_2end",),
    405302: ("area5_3_2_1", "area5_3_2_2"),
    406205: ("area6_2_6", "area6_2_6_2"),
    406305: ("area6_3_6", "area6_3_6_2"),
    406502: ("stage406502",),
    406505: ("stage406505",),
    406506: ("stage406506",),
    561002: ("561002",),
    561112: ("ZX-3-1-3-2",),
    561113: ("ZX-3-1-5-1",),
    561115: ("zx_501101_1",),
    561203: ("stage561203",),
    561211: ("zx_561221_1", "zx_561222_1"),
    561223: ("zx_201103_3",),
    561224: ("zx_201104_1", "zx_561224_2"),
    561304: ("561304", "561304_1"),
    562406: ("zx_562406_1", "zx_562406_3"),
    562407: ("zx_562407_1",),
    562504: ("zx_562504_1",),
    562610: ("act_70110901try",),
    563701: ("act_70110204", "act_70110204try"),
    563901: ("901003", "9010031"),
    563903: ("901008",),
    571101: ("101201_1",),
}


STAGE_CFG_ROUTE_LABELS: dict[int, str] = {
    160001: "All Might's guidance",
    201005: "检查信号塔",
    201006: "调查信号源",
    300301: "Quirk Mastery Test",
    300401: "聚集的敌人",
    300502: "It's a Robo Inferno!",
    300505: "Become the best cavalry there is!",
    310403: "Respective Battleground 01",
    400115: "Boss Stage 1",
    400118: "Boss Stage 3",
    404105: "研究所袭击事件上5",
    404201: "研究所袭击事件下",
    404205: "区域事件4-2-幕后黑手",
    405103: "突出重围3（现6-1）",
    405252: "区域事件5-2Boss",
    405302: "夜间突袭2",
    406205: "区域事件5-2-幕后黑手",
    406305: "脑无",
    406502: "区域事件6-5修复电力",
    406505: "突出重围5",
    406506: "突出重围6",
    561002: "支线任务2",
    561112: "yyk-李季田等院战斗3",
    561113: "yyk-李季田等院战斗4",
    561115: "training signal tower 5 branch battle 1",
    561203: "世界任务复制2-3（临时）",
    561211: "yhc-信号塔2支线抓狗关卡1",
    561223: "限时救援",
    561224: "昊程塔2-1支线1-烈火克星后续",
    561304: "李季塔3-4",
    562406: "雄英塔4-2级-子弹追踪-战斗1",
    562407: "雄英塔4-2级-子弹追踪-战斗2",
    562504: "sr-塔5—1支线4-沙滩救狗",
    562610: "芷晴塔1-1级-独立支线1-战斗",
    563701: "芷晴塔2-1级-独立支线3-战斗",
    563901: "新城区9塔1级-独立支线1-战斗",
    563903: "新城区9塔1级-独立支线2-战斗",
    571101: "本英町",
}


STAGE_CFG_ENCOUNTER_GROUPS: dict[int, tuple[int, ...]] = {
    160001: (16000101,),
    201005: (20100502,),
    201006: (20100602, 20100603, 20100606, 20100607, 20100608),
    300401: (
        30040101,
        30040102,
        30040103,
        30040104,
        30040105,
        30040106,
        30040107,
        30040108,
        30040109,
    ),
    300502: (30050201, 30050202, 30050204, 30050205),
    310403: (31040301,),
    400115: (40011512, 40011513, 40011514),
    400118: (40011801,),
    404201: (40420102, 40420103),
    405103: (40510301, 40510304, 40510371, 40510372, 40510373, 40510374),
    405252: (
        40525201,
        40525202,
        40525203,
        40525204,
        40525251,
        40525271,
        40525272,
    ),
    405302: (40530201, 40530202),
    406205: (40620502, 40620503, 40620504, 40620505, 40620506),
    406305: (40630501, 40630503, 40630505, 40630506),
    406502: (40650201, 40650202, 40650203, 40650204, 40650205),
    406505: (40650501, 40650502, 40650503, 40650504, 40650505),
    406506: (40650603,),
    561112: (56111203, 56111204, 56111205),
    561113: (56111302, 56111303, 56111304),
    561115: (56111501, 56111502, 56111503, 56111505),
    561203: (56120302, 56120303),
    561211: (56121101, 56121102, 56121103),
    561223: (
        56122302,
        56122303,
        56122304,
        56122305,
        56122306,
        56122331,
        56122332,
        56122333,
        56122335,
        56122339,
        56122341,
        56122343,
    ),
    561224: (56122401, 56122402, 56122403, 56122404, 56122405, 56122406),
    561304: (56130411, 56130412, 56130413, 56130414, 56130415),
    562406: (
        56240604,
        56240605,
        56240606,
        56240607,
        56240608,
        56240652,
        56240671,
        56240681,
    ),
    562407: (56240702, 56240751, 56240771, 56240773, 56240775),
    562504: (56250406, 56250407, 56250408, 56250409, 56250410),
    562610: (56261001, 56261002, 56261003, 56261004),
    563701: (56370101, 56370102, 56370103),
    563901: (56390101, 56390102, 56390104),
    563903: (56390301, 56390302, 56390303, 56390304, 56390305, 56390306),
    571101: (57110101, 57110102, 57110104),
}


STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE: dict[int, tuple[int, ...]] = {
    160001: (16000101,),
    201006: (20100603,),
    300401: (
        30040101,
        30040102,
        30040103,
        30040104,
        30040105,
        30040106,
        30040107,
        30040108,
        30040109,
    ),
    310403: (31040301,),
    400115: (40011512, 40011513, 40011514),
    400118: (40011801,),
    404201: (40420102, 40420103),
    405103: (40510301, 40510304),
    405252: (40525201, 40525202, 40525203, 40525204, 40525251, 40525272),
    405302: (40530201, 40530202),
    406205: (40620502, 40620503, 40620504),
    406305: (40630501, 40630503, 40630506),
    406502: (40650202, 40650204, 40650205),
    406505: (40650501, 40650503, 40650504),
    406506: (40650603,),
    561113: (56111303, 56111304),
    561115: (56111503, 56111505),
    561203: (56120302, 56120303),
    561211: (56121101, 56121102, 56121103),
    561304: (56130411, 56130412, 56130414),
    562406: (56240652,),
    562407: (56240702, 56240751, 56240771),
    562504: (56250407, 56250408, 56250409, 56250410),
    562610: (56261001, 56261002, 56261003, 56261004),
    563701: (56370101, 56370102, 56370103),
    563901: (56390101, 56390102),
    563903: (56390301, 56390302, 56390303),
    571101: (57110101, 57110102),
}


STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE: dict[int, tuple[StageEnemySpawn, ...]] = {
    300401: (
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040101",
            enemy_id=30040101,
            shape_id=30040101,
            uid=30040101,
            x=13493,
            y=19529,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040101),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040102",
            enemy_id=30040102,
            shape_id=30040102,
            uid=30040102,
            x=13908,
            y=19515,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040102),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040103",
            enemy_id=30040103,
            shape_id=30040103,
            uid=30040103,
            x=13053,
            y=19328,
            face=337,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040103),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040104",
            enemy_id=30040104,
            shape_id=30040104,
            uid=30040104,
            x=14852,
            y=18674,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040104),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040105",
            enemy_id=30040105,
            shape_id=30040105,
            uid=30040105,
            x=14863,
            y=17882,
            face=90,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040105),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040106",
            enemy_id=30040106,
            shape_id=30040106,
            uid=30040106,
            x=12627,
            y=17570,
            face=270,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040106),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040107",
            enemy_id=30040107,
            shape_id=30040107,
            uid=30040107,
            x=12337,
            y=18408,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040107),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040108",
            enemy_id=30040108,
            shape_id=30040108,
            uid=30040108,
            x=13503,
            y=20148,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040108),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_300401_enemy_30040109",
            enemy_id=30040109,
            shape_id=30040109,
            uid=30040109,
            x=13472,
            y=17177,
            face=180,
            group_id=300401,
            ai_profile_key=generated_enemy_profile_key(30040109),
        ),
    ),
    404201: (
        StageEnemySpawn(
            label="stage_cfg_authored_404201_enemy_40420102",
            enemy_id=40420102,
            shape_id=40420102,
            uid=40420102,
            x=11294,
            y=12209,
            z=195,
            group_id=404201,
            ai_profile_key=generated_enemy_profile_key(40420102),
        ),
    ),
    405252: (
        StageEnemySpawn(
            label="stage_cfg_authored_405252_enemy_40525202",
            enemy_id=40525202,
            shape_id=40525202,
            uid=40525202,
            x=22942,
            y=17316,
            face=157,
            group_id=405252,
            ai_profile_key=generated_enemy_profile_key(40525202),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_405252_enemy_40525272",
            enemy_id=40525272,
            shape_id=40525272,
            uid=40525272,
            x=21361,
            y=17640,
            group_id=405252,
            ai_profile_key=generated_enemy_profile_key(40525272),
        ),
    ),
    406305: (
        StageEnemySpawn(
            label="stage_cfg_authored_406305_enemy_40630501",
            enemy_id=40630501,
            shape_id=40630501,
            uid=40630501,
            x=12128,
            y=3047,
            group_id=406305,
            ai_profile_key=generated_enemy_profile_key(40630501),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_406305_enemy_40630506",
            enemy_id=40630506,
            shape_id=40630506,
            uid=40630506,
            x=11282,
            y=2785,
            z=1225,
            group_id=406305,
            ai_profile_key=generated_enemy_profile_key(40630506),
        ),
    ),
    406502: (
        StageEnemySpawn(
            label="stage_cfg_authored_406502_enemy_40650202",
            enemy_id=40650202,
            shape_id=40650202,
            uid=40650202,
            x=4802,
            y=16698,
            face=270,
            group_id=406502,
            ai_profile_key=generated_enemy_profile_key(40650202),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_406502_enemy_40650204",
            enemy_id=40650204,
            shape_id=40650204,
            uid=40650204,
            x=5005,
            y=13341,
            group_id=406502,
            ai_profile_key=generated_enemy_profile_key(40650204),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_406502_enemy_40650205",
            enemy_id=40650205,
            shape_id=40650205,
            uid=40650205,
            x=7542,
            y=11969,
            group_id=406502,
            ai_profile_key=generated_enemy_profile_key(40650205),
        ),
    ),
    406505: (
        StageEnemySpawn(
            label="stage_cfg_authored_406505_enemy_40650503",
            enemy_id=40650503,
            shape_id=40650503,
            uid=40650503,
            x=2765,
            y=3122,
            z=616,
            group_id=406505,
            ai_profile_key=generated_enemy_profile_key(40650503),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_406505_enemy_40650504",
            enemy_id=40650504,
            shape_id=40650504,
            uid=40650504,
            x=2764,
            y=3196,
            group_id=406505,
            ai_profile_key=generated_enemy_profile_key(40650504),
        ),
    ),
    561113: (
        StageEnemySpawn(
            label="stage_cfg_authored_561113_enemy_56111304",
            enemy_id=56111304,
            shape_id=56111304,
            uid=56111304,
            x=26315,
            y=23088,
            group_id=561113,
            ai_profile_key=generated_enemy_profile_key(56111304),
        ),
    ),
    561203: (
        StageEnemySpawn(
            label="stage_cfg_authored_561203_enemy_56120302",
            enemy_id=56120302,
            shape_id=56120302,
            uid=56120302,
            x=8637,
            y=1122,
            z=5069,
            face=119,
            group_id=561203,
            ai_profile_key=generated_enemy_profile_key(56120302),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_561203_enemy_56120303",
            enemy_id=56120303,
            shape_id=56120303,
            uid=56120303,
            x=8081,
            y=5945,
            group_id=561203,
            ai_profile_key=generated_enemy_profile_key(56120303),
        ),
    ),
    561304: (
        StageEnemySpawn(
            label="stage_cfg_authored_561304_enemy_56130412",
            enemy_id=56130412,
            shape_id=56130412,
            uid=56130412,
            x=25731,
            y=4541,
            z=2033,
            group_id=561304,
            ai_profile_key=generated_enemy_profile_key(56130412),
        ),
    ),
    563701: (
        StageEnemySpawn(
            label="stage_cfg_authored_563701_enemy_56370101",
            enemy_id=56370101,
            shape_id=56370101,
            uid=56370101,
            x=30655,
            y=23585,
            face=180,
            group_id=563701,
            ai_profile_key=generated_enemy_profile_key(56370101),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_563701_enemy_56370102",
            enemy_id=56370102,
            shape_id=56370102,
            uid=56370102,
            x=30917,
            y=23188,
            group_id=563701,
            ai_profile_key=generated_enemy_profile_key(56370102),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_563701_enemy_56370103",
            enemy_id=56370103,
            shape_id=56370103,
            uid=56370103,
            x=30747,
            y=24369,
            z=982,
            group_id=563701,
            ai_profile_key=generated_enemy_profile_key(56370103),
        ),
    ),
    563901: (
        StageEnemySpawn(
            label="stage_cfg_authored_563901_enemy_56390102",
            enemy_id=56390102,
            shape_id=56390102,
            uid=56390102,
            x=15498,
            y=13956,
            face=230,
            group_id=563901,
            ai_profile_key=generated_enemy_profile_key(56390102),
        ),
    ),
    571101: (
        StageEnemySpawn(
            label="stage_cfg_authored_571101_enemy_57110101",
            enemy_id=57110101,
            shape_id=57110101,
            uid=57110101,
            x=10144,
            y=2366,
            z=27144,
            face=90,
            group_id=571101,
            ai_profile_key=generated_enemy_profile_key(57110101),
        ),
        StageEnemySpawn(
            label="stage_cfg_authored_571101_enemy_57110102",
            enemy_id=57110102,
            shape_id=57110102,
            uid=57110102,
            x=10333,
            y=2240,
            z=27160,
            face=-8,
            group_id=571101,
            ai_profile_key=generated_enemy_profile_key(57110102),
        ),
    ),
}

STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE.update(
    {
        400115: (
            StageEnemySpawn(
                label="stage_cfg_authored_400115_enemy_40011512",
                enemy_id=40011512,
                shape_id=40011512,
                uid=40011512,
                x=8175,
                y=4683,
                face=180,
                group_id=400115,
                ai_profile_key=generated_enemy_profile_key(40011512),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_400115_enemy_40011513",
                enemy_id=40011513,
                shape_id=40011513,
                uid=40011513,
                x=8085,
                y=3424,
                group_id=400115,
                ai_profile_key=generated_enemy_profile_key(40011513),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_400115_enemy_40011514",
                enemy_id=40011514,
                shape_id=40011514,
                uid=40011514,
                x=8053,
                y=1659,
                group_id=400115,
                ai_profile_key=generated_enemy_profile_key(40011514),
            ),
        ),
        404201: (
            StageEnemySpawn(
                label="stage_cfg_authored_404201_enemy_40420102",
                enemy_id=40420102,
                shape_id=40420102,
                uid=40420102,
                x=11294,
                y=12209,
                z=195,
                face=60,
                group_id=404201,
                ai_profile_key=generated_enemy_profile_key(40420102),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_404201_enemy_40420103",
                enemy_id=40420103,
                shape_id=40420103,
                uid=40420103,
                x=9676,
                y=12727,
                group_id=404201,
                ai_profile_key=generated_enemy_profile_key(40420103),
            ),
        ),
        405103: (
            StageEnemySpawn(
                label="stage_cfg_authored_405103_enemy_40510304",
                enemy_id=40510304,
                shape_id=40510304,
                uid=40510304,
                x=13564,
                y=18845,
                group_id=405103,
                ai_profile_key=generated_enemy_profile_key(40510304),
            ),
        ),
        405302: (
            StageEnemySpawn(
                label="stage_cfg_authored_405302_enemy_40530201",
                enemy_id=40530201,
                shape_id=40530201,
                uid=40530201,
                x=21866,
                y=27279,
                z=4232,
                face=180,
                group_id=405302,
                ai_profile_key=generated_enemy_profile_key(40530201),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405302_enemy_40530202",
                enemy_id=40530202,
                shape_id=40530202,
                uid=40530202,
                x=21655,
                y=26938,
                group_id=405302,
                ai_profile_key=generated_enemy_profile_key(40530202),
            ),
        ),
        561211: (
            StageEnemySpawn(
                label="stage_cfg_authored_561211_enemy_56121101",
                enemy_id=56121101,
                shape_id=56121101,
                uid=56121101,
                x=15617,
                y=15248,
                group_id=561211,
                ai_profile_key=generated_enemy_profile_key(56121101),
            ),
        ),
        561304: (
            StageEnemySpawn(
                label="stage_cfg_authored_561304_enemy_56130411",
                enemy_id=56130411,
                shape_id=56130411,
                uid=56130411,
                x=25761,
                y=3003,
                z=2049,
                face=210,
                group_id=561304,
                ai_profile_key=generated_enemy_profile_key(56130411),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_561304_enemy_56130412",
                enemy_id=56130412,
                shape_id=56130412,
                uid=56130412,
                x=25731,
                y=4541,
                z=2033,
                group_id=561304,
                ai_profile_key=generated_enemy_profile_key(56130412),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_561304_enemy_56130414",
                enemy_id=56130414,
                shape_id=56130414,
                uid=56130414,
                x=25928,
                y=2418,
                group_id=561304,
                ai_profile_key=generated_enemy_profile_key(56130414),
            ),
        ),
        562504: (
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250407",
                enemy_id=56250407,
                shape_id=56250407,
                uid=56250407,
                x=9186,
                y=16550,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250407),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250408",
                enemy_id=56250408,
                shape_id=56250408,
                uid=56250408,
                x=10667,
                y=16780,
                face=260,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250408),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250410",
                enemy_id=56250410,
                shape_id=56250410,
                uid=56250410,
                x=12125,
                y=16808,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250410),
            ),
        ),
        562610: (
            StageEnemySpawn(
                label="stage_cfg_authored_562610_enemy_56261001",
                enemy_id=56261001,
                shape_id=56261001,
                uid=56261001,
                x=14679,
                y=14883,
                z=670,
                group_id=562610,
                ai_profile_key=generated_enemy_profile_key(56261001),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562610_enemy_56261002",
                enemy_id=56261002,
                shape_id=56261002,
                uid=56261002,
                x=14877,
                y=13745,
                group_id=562610,
                ai_profile_key=generated_enemy_profile_key(56261002),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562610_enemy_56261003",
                enemy_id=56261003,
                shape_id=56261003,
                uid=56261003,
                x=14797,
                y=12399,
                z=661,
                face=180,
                group_id=562610,
                ai_profile_key=generated_enemy_profile_key(56261003),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562610_enemy_56261004",
                enemy_id=56261004,
                shape_id=56261004,
                uid=56261004,
                x=14183,
                y=12526,
                group_id=562610,
                ai_profile_key=generated_enemy_profile_key(56261004),
            ),
        ),
        563903: (
            StageEnemySpawn(
                label="stage_cfg_authored_563903_enemy_56390301",
                enemy_id=56390301,
                shape_id=56390301,
                uid=56390301,
                x=7821,
                y=21904,
                z=944,
                face=90,
                group_id=563903,
                ai_profile_key=generated_enemy_profile_key(56390301),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_563903_enemy_56390302",
                enemy_id=56390302,
                shape_id=56390302,
                uid=56390302,
                x=6220,
                y=21612,
                group_id=563903,
                ai_profile_key=generated_enemy_profile_key(56390302),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_563903_enemy_56390303",
                enemy_id=56390303,
                shape_id=56390303,
                uid=56390303,
                x=6536,
                y=21355,
                group_id=563903,
                ai_profile_key=generated_enemy_profile_key(56390303),
            ),
        ),
    }
)

STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE.update(
    {
        405103: (
            StageEnemySpawn(
                label="stage_cfg_authored_405103_enemy_40510301",
                enemy_id=40510301,
                shape_id=40510301,
                uid=40510301,
                x=12207,
                y=3850,
                face=270,
                group_id=405103,
                ai_profile_key=generated_enemy_profile_key(40510301),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405103_enemy_40510304",
                enemy_id=40510304,
                shape_id=40510304,
                uid=40510304,
                x=13564,
                y=18845,
                group_id=405103,
                ai_profile_key=generated_enemy_profile_key(40510304),
            ),
        ),
        405252: (
            StageEnemySpawn(
                label="stage_cfg_authored_405252_enemy_40525201",
                enemy_id=40525201,
                shape_id=40525201,
                uid=40525201,
                x=22330,
                y=16891,
                z=164,
                face=90,
                group_id=405252,
                ai_profile_key=generated_enemy_profile_key(40525201),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405252_enemy_40525202",
                enemy_id=40525202,
                shape_id=40525202,
                uid=40525202,
                x=22942,
                y=17316,
                face=157,
                group_id=405252,
                ai_profile_key=generated_enemy_profile_key(40525202),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405252_enemy_40525203",
                enemy_id=40525203,
                shape_id=40525203,
                uid=40525203,
                x=21633,
                y=16617,
                face=230,
                group_id=405252,
                ai_profile_key=generated_enemy_profile_key(40525203),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405252_enemy_40525204",
                enemy_id=40525204,
                shape_id=40525204,
                uid=40525204,
                x=23411,
                y=17080,
                group_id=405252,
                ai_profile_key=generated_enemy_profile_key(40525204),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405252_enemy_40525251",
                enemy_id=40525251,
                shape_id=40525251,
                uid=40525251,
                x=22002,
                y=17132,
                face=270,
                group_id=405252,
                ai_profile_key=generated_enemy_profile_key(40525251),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_405252_enemy_40525272",
                enemy_id=40525272,
                shape_id=40525272,
                uid=40525272,
                x=21361,
                y=17640,
                group_id=405252,
                ai_profile_key=generated_enemy_profile_key(40525272),
            ),
        ),
        406305: (
            StageEnemySpawn(
                label="stage_cfg_authored_406305_enemy_40630501",
                enemy_id=40630501,
                shape_id=40630501,
                uid=40630501,
                x=12128,
                y=3047,
                group_id=406305,
                ai_profile_key=generated_enemy_profile_key(40630501),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_406305_enemy_40630503",
                enemy_id=40630503,
                shape_id=40630503,
                uid=40630503,
                x=3343,
                y=1214,
                group_id=406305,
                ai_profile_key=generated_enemy_profile_key(40630503),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_406305_enemy_40630506",
                enemy_id=40630506,
                shape_id=40630506,
                uid=40630506,
                x=11282,
                y=2785,
                z=1225,
                group_id=406305,
                ai_profile_key=generated_enemy_profile_key(40630506),
            ),
        ),
        406205: (
            StageEnemySpawn(
                label="stage_cfg_authored_406205_enemy_40620502",
                enemy_id=40620502,
                shape_id=40620502,
                uid=40620502,
                x=11350,
                y=3476,
                face=43,
                group_id=406205,
                ai_profile_key=generated_enemy_profile_key(40620502),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_406205_enemy_40620503",
                enemy_id=40620503,
                shape_id=40620503,
                uid=40620503,
                x=11117,
                y=3820,
                face=160,
                group_id=406205,
                ai_profile_key=generated_enemy_profile_key(40620503),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_406205_enemy_40620504",
                enemy_id=40620504,
                shape_id=40620504,
                uid=40620504,
                x=11639,
                y=2918,
                group_id=406205,
                ai_profile_key=generated_enemy_profile_key(40620504),
            ),
        ),
        406505: (
            StageEnemySpawn(
                label="stage_cfg_authored_406505_enemy_40650501",
                enemy_id=40650501,
                shape_id=40650501,
                uid=40650501,
                x=2418,
                y=3747,
                group_id=406505,
                ai_profile_key=generated_enemy_profile_key(40650501),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_406505_enemy_40650503",
                enemy_id=40650503,
                shape_id=40650503,
                uid=40650503,
                x=2765,
                y=3122,
                z=616,
                group_id=406505,
                ai_profile_key=generated_enemy_profile_key(40650503),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_406505_enemy_40650504",
                enemy_id=40650504,
                shape_id=40650504,
                uid=40650504,
                x=2764,
                y=3196,
                group_id=406505,
                ai_profile_key=generated_enemy_profile_key(40650504),
            ),
        ),
        562407: (
            StageEnemySpawn(
                label="stage_cfg_authored_562407_enemy_56240702",
                enemy_id=56240702,
                shape_id=56240702,
                uid=56240702,
                x=12482,
                y=21152,
                face=120,
                group_id=562407,
                ai_profile_key=generated_enemy_profile_key(56240702),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562407_enemy_56240751",
                enemy_id=56240751,
                shape_id=56240751,
                uid=56240751,
                x=12304,
                y=20264,
                group_id=562407,
                ai_profile_key=generated_enemy_profile_key(56240751),
            ),
        ),
        562504: (
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250407",
                enemy_id=56250407,
                shape_id=56250407,
                uid=56250407,
                x=9186,
                y=16550,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250407),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250408",
                enemy_id=56250408,
                shape_id=56250408,
                uid=56250408,
                x=10667,
                y=16780,
                face=260,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250408),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250409",
                enemy_id=56250409,
                shape_id=56250409,
                uid=56250409,
                x=11021,
                y=16431,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250409),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_562504_enemy_56250410",
                enemy_id=56250410,
                shape_id=56250410,
                uid=56250410,
                x=12125,
                y=16808,
                group_id=562504,
                ai_profile_key=generated_enemy_profile_key(56250410),
            ),
        ),
        563901: (
            StageEnemySpawn(
                label="stage_cfg_authored_563901_enemy_56390101",
                enemy_id=56390101,
                shape_id=56390101,
                uid=56390101,
                x=83072,
                y=14714,
                face=240,
                group_id=563901,
                ai_profile_key=generated_enemy_profile_key(56390101),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_563901_enemy_56390102",
                enemy_id=56390102,
                shape_id=56390102,
                uid=56390102,
                x=15498,
                y=13956,
                face=230,
                group_id=563901,
                ai_profile_key=generated_enemy_profile_key(56390102),
            ),
        ),
    }
)

STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE.update(
    {
        160001: (
            StageEnemySpawn(
                label="stage_cfg_authored_160001_enemy_16000101",
                enemy_id=16000101,
                shape_id=16000101,
                uid=16000101,
                x=5193,
                y=23257,
                z=526,
                group_id=160001,
                ai_profile_key=generated_enemy_profile_key(16000101),
            ),
        ),
        201006: (
            StageEnemySpawn(
                label="stage_cfg_authored_201006_enemy_20100603",
                enemy_id=20100603,
                shape_id=20100603,
                uid=20100603,
                x=10290,
                y=28269,
                z=2033,
                face=300,
                group_id=201006,
                ai_profile_key=generated_enemy_profile_key(20100603),
            ),
        ),
        310403: (
            StageEnemySpawn(
                label="stage_cfg_authored_310403_enemy_31040301",
                enemy_id=31040301,
                shape_id=31040301,
                uid=31040301,
                x=13952,
                y=19206,
                group_id=310403,
                ai_profile_key=generated_enemy_profile_key(31040301),
            ),
        ),
        400118: (
            StageEnemySpawn(
                label="stage_cfg_authored_400118_enemy_40011801",
                enemy_id=40011801,
                shape_id=40011801,
                uid=40011801,
                x=18484,
                y=10491,
                z=186,
                face=90,
                group_id=400118,
                ai_profile_key=generated_enemy_profile_key(40011801),
            ),
        ),
        406506: (
            StageEnemySpawn(
                label="stage_cfg_authored_406506_enemy_40650603",
                enemy_id=40650603,
                shape_id=40650603,
                uid=40650603,
                x=10636,
                y=4708,
                face=180,
                group_id=406506,
                ai_profile_key=generated_enemy_profile_key(40650603),
            ),
        ),
        561113: (
            StageEnemySpawn(
                label="stage_cfg_authored_561113_enemy_56111303",
                enemy_id=56111303,
                shape_id=56111303,
                uid=56111303,
                x=26375,
                y=23089,
                face=180,
                group_id=561113,
                ai_profile_key=generated_enemy_profile_key(56111303),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_561113_enemy_56111304",
                enemy_id=56111304,
                shape_id=56111304,
                uid=56111304,
                x=26315,
                y=23088,
                group_id=561113,
                ai_profile_key=generated_enemy_profile_key(56111304),
            ),
        ),
        561115: (
            StageEnemySpawn(
                label="stage_cfg_authored_561115_enemy_56111505",
                enemy_id=56111505,
                shape_id=56111505,
                uid=56111505,
                x=31319,
                y=25275,
                group_id=561115,
                ai_profile_key=generated_enemy_profile_key(56111505),
            ),
        ),
        561211: (
            StageEnemySpawn(
                label="stage_cfg_authored_561211_enemy_56121101",
                enemy_id=56121101,
                shape_id=56121101,
                uid=56121101,
                x=15186,
                y=14578,
                z=2034,
                group_id=561211,
                ai_profile_key=generated_enemy_profile_key(56121101),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_561211_enemy_56121102",
                enemy_id=56121102,
                shape_id=56121102,
                uid=56121102,
                x=15186,
                y=14578,
                z=2034,
                group_id=561211,
                ai_profile_key=generated_enemy_profile_key(56121102),
            ),
            StageEnemySpawn(
                label="stage_cfg_authored_561211_enemy_56121103",
                enemy_id=56121103,
                shape_id=56121103,
                uid=56121103,
                x=15186,
                y=14578,
                z=2034,
                group_id=561211,
                ai_profile_key=generated_enemy_profile_key(56121103),
            ),
        ),
    }
)


def _zx_numeric_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    return tuple(
        BattleStageDefinition(
            key=f"zx_stage_{stage_id}",
            label=f"recovered numeric zx stage script cluster {stage_id}",
            stage_id=stage_id,
            scripts=scripts,
            source="parsed from zx numeric drama script names, 2026-06-23",
        )
        for stage_id, scripts in sorted(ZX_NUMERIC_STAGE_SCRIPT_GROUPS.items())
        if stage_id not in EXPLICIT_RECOVERED_STAGE_IDS
    )


def _asset_numeric_drama_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | {stage.stage_id for stage in RELAX_STAGES}
        | {stage.stage_id for stage in ALLSVR_STAGES}
        | {stage.stage_id for stage in ALLSVR_BOSS_STAGES}
        | {stage.stage_id for stage in EMPTY_SHOP_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"asset_drama_stage_{stage_id}",
            label=f"asset-header numeric drama stage {stage_id}",
            stage_id=stage_id,
            scripts=scripts,
            source="parsed from packed Lua drama chunk headers, 2026-06-23",
        )
        for stage_id, scripts in sorted(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS.items())
        if stage_id not in occupied_ids
    )


def _stage_cfg_script_route_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
    )
    return tuple(
        BattleStageDefinition(
            key=f"stage_cfg_route_{stage_id}",
            label=STAGE_CFG_ROUTE_LABELS.get(
                stage_id,
                f"stage_cfg routed drama stage {stage_id}",
            ),
            stage_id=stage_id,
            scripts=scripts,
            enemy_group_ids=STAGE_CFG_ENCOUNTER_GROUPS.get(stage_id, ()),
            source="parsed from packed stage_cfg constant routes, 2026-06-23",
        )
        for stage_id, scripts in sorted(STAGE_CFG_SCRIPT_ROUTE_GROUPS.items())
        if stage_id not in occupied_ids
    )


def _area_event_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
    )
    return tuple(
        BattleStageDefinition(
            key=f"area_event_stage_{stage.stage_id}",
            label=stage.name,
            stage_id=stage.stage_id,
            scripts=(stage.open_drama,) if stage.open_drama else (),
            source=AREA_EVENT_STAGE_SOURCE,
        )
        for stage in AREA_EVENT_STAGES
        if stage.stage_id not in occupied_ids
    )


def _act_daily_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"act_daily_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            enemy_group_ids=ACT_DAILY_MONSTER_IDS,
            source=ACT_DAILY_STAGE_SOURCE,
        )
        for stage in ACT_DAILY_STAGES
        if stage.stage_id not in occupied_ids
    )


def _usj_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
        | {stage.stage_id for stage in ACT_DAILY_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"usj_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=USJ_STAGE_SOURCE,
        )
        for stage in USJ_STAGES
        if stage.stage_id not in occupied_ids
    )


def _herochip_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
        | {stage.stage_id for stage in ACT_DAILY_STAGES}
        | {stage.stage_id for stage in USJ_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"herochip_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=HEROCHIP_STAGE_SOURCE,
        )
        for stage in HEROCHIP_STAGES
        if stage.stage_id not in occupied_ids
    )


def _roguelike_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
        | {stage.stage_id for stage in ACT_DAILY_STAGES}
        | {stage.stage_id for stage in USJ_STAGES}
        | {stage.stage_id for stage in HEROCHIP_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"roguelike_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=ROGUELIKE_STAGE_SOURCE,
        )
        for stage in ROGUELIKE_STAGES
        if stage.stage_id not in occupied_ids
    )


def _relax_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    return tuple(
        BattleStageDefinition(
            key=f"relax_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=RELAX_STAGE_SOURCE,
        )
        for stage in RELAX_STAGES
    )


def _secret_area_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
        | {stage.stage_id for stage in ACT_DAILY_STAGES}
        | {stage.stage_id for stage in USJ_STAGES}
        | {stage.stage_id for stage in HEROCHIP_STAGES}
        | {stage.stage_id for stage in ROGUELIKE_STAGES}
        | {stage.stage_id for stage in RELAX_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"secret_area_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=SECRET_AREA_STAGE_SOURCE,
        )
        for stage in SECRET_AREA_STAGES
        if stage.stage_id not in occupied_ids
    )


def _allsvr_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
        | {stage.stage_id for stage in ACT_DAILY_STAGES}
        | {stage.stage_id for stage in USJ_STAGES}
        | {stage.stage_id for stage in HEROCHIP_STAGES}
        | {stage.stage_id for stage in ROGUELIKE_STAGES}
        | {stage.stage_id for stage in RELAX_STAGES}
        | {stage.stage_id for stage in SECRET_AREA_STAGES}
    )
    regular = tuple(
        BattleStageDefinition(
            key=f"allsvr_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=ALLSVR_STAGE_SOURCE,
        )
        for stage in ALLSVR_STAGES
        if stage.stage_id not in occupied_ids
    )
    occupied_ids = occupied_ids | {stage.stage_id for stage in ALLSVR_STAGES}
    bosses = tuple(
        BattleStageDefinition(
            key=f"allsvr_boss_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=ALLSVR_STAGE_SOURCE,
        )
        for stage in ALLSVR_BOSS_STAGES
        if stage.stage_id not in occupied_ids
    )
    return regular + bosses


def _empty_shop_stage_definitions() -> tuple[BattleStageDefinition, ...]:
    occupied_ids = (
        EXPLICIT_RECOVERED_STAGE_IDS
        | set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS)
        | set(ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS)
        | set(STAGE_CFG_SCRIPT_ROUTE_GROUPS)
        | {stage.stage_id for stage in AREA_EVENT_STAGES}
        | {stage.stage_id for stage in ACT_DAILY_STAGES}
        | {stage.stage_id for stage in USJ_STAGES}
        | {stage.stage_id for stage in HEROCHIP_STAGES}
        | {stage.stage_id for stage in ROGUELIKE_STAGES}
        | {stage.stage_id for stage in RELAX_STAGES}
        | {stage.stage_id for stage in SECRET_AREA_STAGES}
        | {stage.stage_id for stage in ALLSVR_STAGES}
        | {stage.stage_id for stage in ALLSVR_BOSS_STAGES}
    )
    return tuple(
        BattleStageDefinition(
            key=f"empty_shop_stage_{stage.stage_id}",
            label=stage.label,
            stage_id=stage.stage_id,
            source=EMPTY_SHOP_STAGE_SOURCE,
        )
        for stage in EMPTY_SHOP_STAGES
        if stage.stage_id not in occupied_ids
    )


RECOVERED_BATTLE_STAGES = (
    BattleStageDefinition(
        key="starter_intro_299301",
        label="starter intro battle cluster",
        stage_id=STARTER_INTRO_STAGE_ID,
        stage_uid=STARTER_INTRO_STAGE_UID,
        scripts=(
            "zx_battle01",
            "zx_battle02",
            "zx_battle02_1",
            "zx_battle03",
            "zx_battle03_1",
            "zx_battle03_2",
            "zx_battle04",
            "zx_battle05",
            "zx_battle06",
            "zx_battle07",
            "zx_lvb_001",
            "zx_lvb_002",
            "zx_lvb_003",
            "zx_lvb_004",
            "zx_lvbzero",
        ),
        audio_events=(
            "PLOT_zx_battle01_01",
            "PLOT_zx_battle04_08",
            "PLOT_zx_battle07_01",
            "PLOT_zx_battle07_02",
            "PLOT_zx_battle07_03",
            "PLOT_zx_battle07_04",
            "PLOT_zx_battle07_04+05",
            "PLOT_zx_battle07_05",
        ),
        actor_sets=(
            "zx_lvb001",
            "zx_lvb002",
            "zx_lvb002_1",
            "zx_lvb003",
            "zx_lvb003_1",
            "zx_lvb004",
            "zx_lvb005",
            "zx_lvb006",
        ),
        video_assets=(
            "video/zx/chapter2/lvb01.flv",
            "video/zx/chapter2/lvb02.flv",
            "video/zx/chapter2/lvb03.flv",
            "video/zx/chapter2/lvb04.flv",
        ),
        character_refs=("h1001", "h1002", "h1007", "h1024"),
        enemy_group_ids=(
            2001,
            3002,
            3003,
            3004,
            8003,
            20021,
            20022,
            20023,
            20031,
            20032,
            20033,
            20041,
            3003001,
            3003002,
            3003003,
            3003004,
            3003005,
            3003006,
            3003007,
            3003008,
            3003009,
            3003010,
            3003011,
            3003012,
            3003013,
            3003014,
            3003015,
            3003016,
        ),
        enemy_spawns=STARTER_STAGE_ENEMIES,
    ),
    BattleStageDefinition(
        key="all_might_stage_502601",
        label="All Might related drama stage cluster",
        stage_id=502601,
        scripts=("stage502601", "stage502601a", "stage502601b", "stage502601c"),
        audio_events=(
            "BATTLE_HERO_allmight_allmight_VO_01",
            "BATTLE_HERO_allmight_allmight_VO_02",
            "BATTLE_HERO_allmight_allmight_VO_03",
            "BATTLE/HERO/allmight/skills/Eskill_01",
            "BATTLE/HERO/allmight/commonATK/commonATK_01",
        ),
        actor_sets=("stage502601a", "stage502601b"),
        character_refs=("h1003",),
        enemy_spawns=(
            StageEnemySpawn(
                label="all_might_stage_brute_probe",
                enemy_id=3002,
                shape_id=3002,
                uid=50260101,
                x=0,
                y=0,
                level=1,
                group_id=502601,
                ai_profile_key="sludge_boss",
            ),
        ),
    ),
    BattleStageDefinition(
        key="main_stage_160001",
        label="generic main-stage drama cluster",
        stage_id=160001,
        scripts=(
            "stage160001",
            "stage160001_start",
            "stage160001_win",
            "stage160001_lose",
            "stage160001_end",
        ),
        enemy_group_ids=STAGE_CFG_ENCOUNTER_GROUPS[160001],
        enemy_spawns=(
            StageEnemySpawn(
                label="main_stage_training_enemy",
                enemy_id=2005,
                shape_id=2005,
                uid=16000101,
                x=0,
                y=0,
                group_id=160001,
                ai_profile_key="training_enemy",
            ),
        ),
    ),
    BattleStageDefinition(
        key="stage_500",
        label="recovered numeric drama stage 500",
        stage_id=500,
        scripts=("stage500",),
    ),
    BattleStageDefinition(
        key="stage_200508",
        label="recovered numeric drama stage 200508",
        stage_id=200508,
        scripts=("stage200508",),
    ),
    BattleStageDefinition(
        key="stage_200509",
        label="recovered numeric drama stage 200509",
        stage_id=200509,
        scripts=("stage200509_1", "stage200509_2"),
    ),
    BattleStageDefinition(
        key="stage_404103",
        label="recovered numeric drama stage 404103",
        stage_id=404103,
        scripts=("stage404103_1",),
    ),
    BattleStageDefinition(
        key="stage_404105",
        label="recovered numeric drama stage 404105",
        stage_id=404105,
        scripts=("stage404105",),
    ),
    BattleStageDefinition(
        key="stage_404201",
        label="recovered numeric drama stage 404201",
        stage_id=404201,
        scripts=("stage404201",),
    ),
    BattleStageDefinition(
        key="stage_404204",
        label="recovered numeric drama stage 404204",
        stage_id=404204,
        scripts=("stage404204",),
    ),
    BattleStageDefinition(
        key="stage_404205",
        label="recovered numeric drama stage 404205",
        stage_id=404205,
        scripts=("stage404205_1",),
    ),
    BattleStageDefinition(
        key="stage_404402",
        label="recovered numeric drama stage 404402",
        stage_id=404402,
        scripts=("stage404402",),
    ),
    BattleStageDefinition(
        key="stage_404405",
        label="recovered numeric drama stage 404405",
        stage_id=404405,
        scripts=("stage404405",),
    ),
    BattleStageDefinition(
        key="stage_406405",
        label="recovered numeric drama stage 406405",
        stage_id=406405,
        scripts=("stage406405",),
    ),
    BattleStageDefinition(
        key="stage_406502",
        label="recovered numeric drama stage 406502",
        stage_id=406502,
        scripts=("stage406502",),
    ),
    BattleStageDefinition(
        key="stage_406505",
        label="recovered numeric drama stage 406505",
        stage_id=406505,
        scripts=("stage406505", "stage406505_1"),
    ),
    BattleStageDefinition(
        key="stage_406506",
        label="recovered numeric drama stage 406506",
        stage_id=406506,
        scripts=("stage406506",),
    ),
    BattleStageDefinition(
        key="stage_420001",
        label="recovered numeric drama stage 420001",
        stage_id=420001,
        scripts=("stage420001",),
    ),
    BattleStageDefinition(
        key="stage_501201",
        label="recovered numeric drama stage 501201",
        stage_id=501201,
        scripts=("stage501201a", "stage501201b"),
    ),
    BattleStageDefinition(
        key="stage_561203",
        label="recovered numeric drama stage 561203",
        stage_id=561203,
        scripts=("stage561203", "stage561203_1", "stage561203_2"),
    ),
    *_asset_numeric_drama_stage_definitions(),
    *_stage_cfg_script_route_definitions(),
    *_area_event_stage_definitions(),
    *_act_daily_stage_definitions(),
    *_usj_stage_definitions(),
    *_herochip_stage_definitions(),
    *_roguelike_stage_definitions(),
    *_zx_numeric_stage_definitions(),
    *_relax_stage_definitions(),
    *_secret_area_stage_definitions(),
    *_allsvr_stage_definitions(),
    *_empty_shop_stage_definitions(),
    BattleStageDefinition(
        key="battle_drama_zx_only",
        label="battle drama scripts without recovered numeric stage id",
        stage_id=None,
        scripts=(
            "zx_battle01",
            "zx_battle02",
            "zx_battle02_1",
            "zx_battle03",
            "zx_battle03_1",
            "zx_battle03_2",
            "zx_battle04",
            "zx_battle05",
            "zx_battle06",
            "zx_battle07",
        ),
        audio_events=(
            "PLOT_zx_battle01_01",
            "PLOT_zx_battle04_08",
            "PLOT_zx_battle07_01",
            "PLOT_zx_battle07_02",
            "PLOT_zx_battle07_03",
            "PLOT_zx_battle07_04",
            "PLOT_zx_battle07_05",
        ),
    ),
    BattleStageDefinition(
        key="ruxue_intro_drama_scripts",
        label="U.A. enrollment intro drama script cluster",
        stage_id=None,
        scripts=(
            "zx_ruxue01",
            "zx_ruxue02",
            "zx_ruxue03",
            "zx_ruxue03_1",
            "zx_ruxue03_2",
            "zx_ruxue03_2_1",
            "zx_ruxue04",
            "zx_ruxue05",
            "zx_ruxue_new2",
            "zx_ruxue_new2_1",
            "zx_ruxue_new3",
        ),
        audio_events=(
            "PLOT_copyright_zx_ruxue02_01",
            "PLOT_copyright_zx_ruxue02_02",
            "PLOT_copyright_zx_ruxue02_03",
            "PLOT_zx_ruxue03_1_01",
            "PLOT_zx_ruxue03_2_09",
        ),
        video_assets=("video/zx/chapter2/ruxue_1.flv",),
    ),
    BattleStageDefinition(
        key="usj_drama_scripts",
        label="USJ drama and combat script cluster",
        stage_id=None,
        scripts=(
            "zx_usj001",
            "zx_usj002",
            "zx_usj_001",
            "zx_usj_001001",
            "zx_usj_002",
            "zx_usj_003",
            "zx_usj_003001",
            "zx_usj_004",
            "zx_usj_005",
            "zx_usj_006",
            "zx_usj_007",
            "zx_usj_03001",
            "zx_usj_03002",
        ),
        enemy_group_ids=(3007, 3125),
    ),
    BattleStageDefinition(
        key="beach_event_scripts",
        label="beach event drama and carry script cluster",
        stage_id=None,
        scripts=(
            "zx_beach",
            "zx_beach01",
            "zx_beach03",
            "zx_beach04",
            "zx_beach_1",
            "zx_beach_carry",
            "zx_beach_carry1_1",
            "zx_beach_carry1_2",
            "zx_beach_carry1_3",
            "zx_beach_carry1_4",
            "zx_beach_carry1_5",
            "zx_beach_carry2",
            "zx_beach_carry_fail1",
            "zx_beach_carry_fail2",
            "zx_beach_carry_fail3",
            "zx_beach_carry_fail4",
            "zx_beach_carry_fail5",
            "zx_beach_carry_suc1",
            "zx_beach_carry_suc2",
            "zx_beach_carry_suc3",
            "zx_beach_carry_suc4",
            "zx_beach_carry_suc5",
            "zx_beach_g1",
            "zx_beach_suc",
        ),
        video_assets=("video/zx/chapter2/beach_01.flv",),
    ),
    BattleStageDefinition(
        key="commercial_street_scripts",
        label="commercial street intro/exploration script cluster",
        stage_id=None,
        scripts=(
            "zx_shangyejie0",
            "zx_shangyejie01",
            "zx_shangyejie02",
            "zx_shangyejie03",
            "zx_shangyejie1",
            "zx_shangyejie2",
            "zx_shangyejie3",
            "zx_shangyejie4",
            "zx_shangyejie_end",
            "zx_shangyejie_qte",
            "zx_shangyejie_start",
            "zx_shangyejie_test",
        ),
    ),
    BattleStageDefinition(
        key="training_yard_scripts",
        label="training-yard drama and hazard script cluster",
        stage_id=None,
        scripts=(
            "zx_tyj01",
            "zx_tyj02",
            "zx_tyj02_1",
            "zx_tyj03",
            "zx_tyj04",
            "zx_tyj04_1",
            "zx_tyj05",
            "zx_tyj06",
            "zx_touqiu",
            "zx_tyj_dilei01",
            "zx_tyj_dilei02",
        ),
        video_assets=("video/zx/chapter2/touqiu.flv",),
    ),
    BattleStageDefinition(
        key="stage_cfg_chapter1_zx_evidence",
        label="stage_cfg chapter 1 zx/video evidence without proven stage route",
        stage_id=None,
        scripts=("zx_2_2_1", "zx_2_2_2", "zx_2_6_1", "zx_2_7"),
        video_assets=(
            "video/zx/chapter1/judahua.flv",
            "video/zx/chapter1/yuniguai_1.flv",
        ),
        source="parsed from packed stage_cfg strings, 2026-06-23",
    ),
)


RECOVERED_BATTLE_STAGE_BY_KEY = {
    stage.key: stage for stage in RECOVERED_BATTLE_STAGES
}
RECOVERED_BATTLE_STAGE_BY_ID = {
    stage.stage_id: stage
    for stage in RECOVERED_BATTLE_STAGES
    if stage.stage_id is not None
}


def stage_candidate_by_key(key: str) -> BattleStageDefinition:
    return RECOVERED_BATTLE_STAGE_BY_KEY[key]


def stage_candidate_by_id(stage_id: int) -> BattleStageDefinition:
    return RECOVERED_BATTLE_STAGE_BY_ID[stage_id]


def stage_candidate_or_generated(stage_id: int) -> BattleStageDefinition:
    stage = RECOVERED_BATTLE_STAGE_BY_ID.get(int(stage_id))
    if stage is not None:
        return stage
    return BattleStageDefinition(
        key=f"generated_stage_{int(stage_id)}",
        label=f"generated playable combat stage {int(stage_id)}",
        stage_id=int(stage_id),
        scripts=(),
        source="generated from requested stage id, 2026-06-23",
    )


def _as_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _dict_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [dict(item) for item in value if isinstance(item, dict)]


@dataclass(frozen=True, slots=True)
class StageCombatSummary:
    stage_id: int
    result: int
    time: int
    max_combo: int
    combo_damage: int
    all_damage: int
    on_hit_num: int
    solo_boss_num: int
    monster_kills: tuple[tuple[int, int], ...] = ()
    item_rewards: tuple[tuple[int, int], ...] = ()
    skill_levels: tuple[tuple[int, int], ...] = ()
    button_counts: tuple[tuple[str, int], ...] = ()
    move_total: int = 0
    damage_members: tuple[tuple[int, int], ...] = ()
    mvp_uid: int = 0
    reborn: int = 0
    combat_resolution: CombatResolution | None = None
    enemy_results: tuple[StageEnemyCombatResult, ...] = ()
    stage_time_limit: int = STARTER_INTRO_STAGE_TIME

    @property
    def passed(self) -> bool:
        return self.result == 1

    @property
    def stars(self) -> list[int]:
        if not self.passed:
            return []
        stars = [1]
        target_count = (
            self.combat_resolution.target_count
            if self.combat_resolution is not None
            else 0
        )
        if not target_count or self.estimated_defeats >= target_count:
            stars.append(2)
        clean_clear = self.reborn == 0
        fast_clear = not self.time or self.time <= max(1, int(self.stage_time_limit * 0.8))
        if 2 in stars and clean_clear and fast_clear:
            stars.append(3)
        return stars

    @property
    def rewards(self) -> list[dict[str, object]]:
        return [
            {"ItemId": item_id, "count": count, "extra": []}
            for item_id, count in self.item_rewards
            if item_id and count
        ]

    @property
    def generated_rewards(self) -> list[dict[str, object]]:
        rewards = [
            {
                "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                "count": max(1, self.estimated_defeats or 1),
                "extra": [],
            }
        ]
        stars = self.stars
        if 2 in stars:
            rewards.append(
                {
                    "ItemId": LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
                    "count": len(stars),
                    "extra": [],
                }
            )
        if (
            self.combat_resolution is not None
            and self.combat_resolution.pressure_score >= 75
        ):
            rewards.append(
                {
                    "ItemId": LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
                    "count": max(1, self.combat_resolution.pressure_score // 75),
                    "extra": [],
                }
            )
        return rewards

    @property
    def result_rewards(self) -> list[dict[str, object]]:
        return self.rewards or self.generated_rewards

    @property
    def move_results(self) -> list[dict[str, object]]:
        if self.combat_resolution is None:
            return []
        return [
            result.as_dict()
            for result in self.combat_resolution.move_results
            if result.count or result.estimated_damage
        ]

    @property
    def estimated_defeats(self) -> int:
        if self.enemy_results:
            return sum(1 for result in self.enemy_results if result.defeated)
        if self.combat_resolution is not None:
            return self.combat_resolution.defeated_targets
        return 0

    @property
    def enemy_result_list(self) -> list[dict[str, object]]:
        return [result.as_dict() for result in self.enemy_results]

    @property
    def combat_effects(self) -> dict[str, object]:
        if self.combat_resolution is None:
            return {
                "HeroId": 0,
                "StyleName": "",
                "Damage": 0,
                "ControlScore": 0,
                "ResourceDelta": 0,
                "MobilityScore": 0,
                "DefenseScore": 0,
                "PressureScore": 0,
                "DefeatedTargets": 0,
            }
        resolution = self.combat_resolution
        return {
            "HeroId": resolution.hero_id,
            "StyleName": resolution.style_name,
            "Damage": resolution.estimated_damage,
            "ControlScore": resolution.control_score,
            "ResourceDelta": resolution.resource_delta,
            "MobilityScore": resolution.mobility_score,
            "DefenseScore": resolution.defense_score,
            "PressureScore": resolution.pressure_score,
            "DefeatedTargets": resolution.defeated_targets,
        }


@dataclass(slots=True)
class StageState:
    current_stage_id: int = 0
    current_stage_uid: int = 0
    current_stage_key: str | None = None
    finished_loading_count: int = 0
    reports: list[dict[str, object]] = field(default_factory=list)
    damage_reports: list[dict[str, object]] = field(default_factory=list)
    encounter_frames: list[dict[str, object]] = field(default_factory=list)
    ai_directives: list[dict[str, object]] = field(default_factory=list)
    monster_frames: list[dict[str, object]] = field(default_factory=list)
    play_sync_reports: list[dict[str, object]] = field(default_factory=list)
    frame_report_count: int = 0
    quick_reborn_count: int = 0
    leave_requests: list[int] = field(default_factory=list)
    is_back_checks: list[int] = field(default_factory=list)
    pressure_scores: dict[int, int] = field(default_factory=dict)
    daily_stage_counts: dict[int, int] = field(default_factory=dict)
    allsvr_level_counts: dict[int, int] = field(default_factory=dict)
    allsvr_boss_scores: dict[int, int] = field(default_factory=dict)
    empty_shop_max_pass_stage: int = 0
    night_fight_statuses: dict[int, int] = field(default_factory=dict)
    night_fight_hero_tired: dict[int, int] = field(default_factory=dict)
    theater_unlocked_stage_ids: set[int] = field(default_factory=set)
    theater_bonus_claims: dict[str, int] = field(default_factory=dict)
    completions: dict[int, StageCompletion] = field(default_factory=dict)
    current_usj_point_id: int = 0

    def enter_stage(
        self,
        stage_id: int = STARTER_INTRO_STAGE_ID,
        *,
        stage_uid: int = STARTER_INTRO_STAGE_UID,
        level: int = STARTER_INTRO_STAGE_LEVEL,
        time_limit: int = STARTER_INTRO_STAGE_TIME,
        drama: int = STARTER_INTRO_STAGE_DRAMA,
        stage_key: str | None = None,
    ) -> dict[str, object]:
        self.current_stage_id = stage_id
        self.current_stage_uid = stage_uid
        self.current_stage_key = stage_key
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

    def enter_recovered_stage(
        self, stage: BattleStageDefinition
    ) -> dict[str, object]:
        if stage.stage_id is None:
            raise ValueError(f"{stage.key} has no numeric stage id")
        payload = self.enter_stage(
            stage.stage_id,
            stage_uid=stage.resolved_stage_uid,
            level=stage.level,
            time_limit=stage.time_limit,
            drama=stage.drama,
            stage_key=stage.key,
        )
        self.seed_encounter(stage)
        return payload

    def seed_encounter(
        self, stage: BattleStageDefinition
    ) -> list[dict[str, object]]:
        spawns = stage.encounter_spawns
        frames = [spawn.to_monster_frame_seed() for spawn in spawns]
        self.encounter_frames = frames
        self.ai_directives = [spawn.to_ai_directive() for spawn in spawns]
        return frames

    def finish_loading(self, uid: int) -> dict[str, object]:
        self.finished_loading_count += 1
        return {"Uid": uid}

    def record_report(self, values: dict[str, object]) -> None:
        self.reports.append(dict(values))

    def record_damage_info(self, values: dict[str, object]) -> None:
        self.damage_reports.append(dict(values))

    def record_monster_frame_data(
        self, values: dict[str, object]
    ) -> list[dict[str, object]]:
        frames = [dict(item) for item in list(values.get("monster_data") or [])]
        self.monster_frames.extend(frames)
        return frames

    def record_play_sync(
        self, uid: int, sync_data: list[dict[str, object]]
    ) -> dict[str, object]:
        normalized = [
            {"Key": str(item.get("Key") or ""), "Val": _as_int(item.get("Val"))}
            for item in sync_data
            if isinstance(item, dict)
        ]
        payload = {"UUid": int(uid), "SyncData": normalized}
        self.play_sync_reports.append(payload)
        return payload

    def record_frame_report(self) -> dict[str, object]:
        self.frame_report_count += 1
        return {}

    def record_quick_reborn(self, reborn_count: int) -> None:
        self.quick_reborn_count += max(0, int(reborn_count))

    def leave_stage(self, stage_id: int | None = None) -> dict[str, object]:
        resolved_stage_id = int(stage_id or self.current_stage_id or 0)
        self.leave_requests.append(resolved_stage_id)
        return {"StageId": resolved_stage_id}

    def stage_is_back(self, stage_id: int | None = None) -> dict[str, object]:
        resolved_stage_id = int(stage_id or self.current_stage_id or 0)
        self.is_back_checks.append(resolved_stage_id)
        return {"StageId": resolved_stage_id}

    def night_fight_stage_ids(
        self, extra_stage_id: int | None = None
    ) -> tuple[int, ...]:
        stage_ids = set(NIGHT_FIGHT_DEFAULT_STAGE_IDS)
        stage_ids.update(
            stage_id
            for stage_id, completion in self.completions.items()
            if completion.status == 1
        )
        stage_ids.update(self.night_fight_statuses)
        if extra_stage_id:
            stage_ids.add(int(extra_stage_id))
        return tuple(sorted(stage_ids))

    def night_fight_info(self) -> dict[str, object]:
        return {
            "StageInfo": [
                {
                    "NightFightId": stage_id,
                    "Progress": self.night_fight_statuses.get(
                        stage_id,
                        1 if self.completions.get(stage_id, None)
                        and self.completions[stage_id].status == 1
                        else 0,
                    ),
                    "IsPass": (
                        1
                        if self.night_fight_statuses.get(stage_id, 0) >= 1
                        or (
                            self.completions.get(stage_id, None) is not None
                            and self.completions[stage_id].status == 1
                        )
                        else 0
                    ),
                }
                for stage_id in self.night_fight_stage_ids()
            ]
        }

    @staticmethod
    def night_fight_hero_lineup(hero_uids: list[int]) -> dict[str, object]:
        return {"HeroLineup": [int(hero_uid) for hero_uid in hero_uids]}

    def night_fight_sync_status(
        self, stage_id: int | None = None, hero_uids: list[int] | None = None
    ) -> dict[str, object]:
        resolved_stage_id = int(stage_id or self.current_stage_id or 0)
        return {
            "StageId": resolved_stage_id,
            "StageList": [
                {
                    "StageId": known_stage_id,
                    "StageType": max(1, known_stage_id // 100000),
                    "StageStatus": self.night_fight_statuses.get(
                        known_stage_id,
                        1 if self.completions.get(known_stage_id, None)
                        and self.completions[known_stage_id].status == 1
                        else 0,
                    ),
                    "HasExtraReward": (
                        1 if self.night_fight_statuses.get(known_stage_id, 0) >= 1 else 0
                    ),
                }
                for known_stage_id in self.night_fight_stage_ids(resolved_stage_id)
            ],
            "HeroStatus": [
                {
                    "HeroUid": int(hero_uid),
                    "TiredValue": self.night_fight_hero_tired.get(int(hero_uid), 0),
                }
                for hero_uid in (hero_uids or [])
            ],
        }

    def night_fight_fight_over(
        self, stage_id: int, hero_uid: int, is_win: int
    ) -> dict[str, object]:
        resolved_stage_id = int(stage_id or self.current_stage_id or 0)
        result = 1 if int(is_win) else 0
        if result:
            self.night_fight_statuses[resolved_stage_id] = 1
            self.night_fight_hero_tired[int(hero_uid)] = (
                self.night_fight_hero_tired.get(int(hero_uid), 0) + 5
            )
            existing = self.completions.get(resolved_stage_id)
            self.completions[resolved_stage_id] = StageCompletion(
                stage_id=resolved_stage_id,
                status=1,
                stars=(
                    tuple(sorted(set(existing.stars).union({1, 2, 3})))
                    if existing is not None
                    else (1, 2, 3)
                ),
                full_star_time=existing.full_star_time if existing is not None else 0,
                best_time=existing.best_time if existing is not None else 0,
                pass_count=(existing.pass_count if existing is not None else 0) + 1,
            )
        else:
            self.night_fight_statuses.setdefault(resolved_stage_id, 0)
        return {"StageId": resolved_stage_id, "IsWin": result}

    @staticmethod
    def night_fight_reward(is_win: int) -> dict[str, object]:
        rewards = (
            [{"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "count": 1, "extra": []}]
            if int(is_win)
            else []
        )
        return {"FixedReward": rewards, "ExtraReward": [], "SpecialReward": []}

    def hero_rank_stage_info(self) -> dict[str, object]:
        return {
            "StageList": [
                {"Id": stage_id, "Star": list(completion.stars)}
                for stage_id, completion in sorted(self.completions.items())
                if completion.status == 1
            ]
        }

    def hero_rank_stage_update(
        self, stage_id: int, stars: list[int]
    ) -> dict[str, object]:
        resolved_stage_id = int(stage_id or self.current_stage_id or 0)
        normalized_stars = tuple(sorted({_as_int(star) for star in stars if _as_int(star) > 0}))
        existing = self.completions.get(resolved_stage_id)
        self.completions[resolved_stage_id] = StageCompletion(
            stage_id=resolved_stage_id,
            status=1,
            stars=(
                tuple(sorted(set(existing.stars).union(normalized_stars)))
                if existing is not None
                else normalized_stars
            ),
            full_star_time=existing.full_star_time if existing is not None else 0,
            best_time=existing.best_time if existing is not None else 0,
            pass_count=(existing.pass_count if existing is not None else 0) + 1,
        )
        return {
            "Id": resolved_stage_id,
            "Star": list(self.completions[resolved_stage_id].stars),
        }

    def stage_bonus(self, values: dict[str, object]) -> dict[str, object]:
        stage_id = _as_int(values.get("StageId"), self.current_stage_id)
        result = _as_int(values.get("Result"), 1)
        stars = tuple(
            sorted({_as_int(star) for star in list(values.get("StarList") or []) if _as_int(star) > 0})
        )
        existing = self.completions.get(stage_id)
        if result == 1:
            self.completions[stage_id] = StageCompletion(
                stage_id=stage_id,
                status=1,
                stars=(
                    tuple(sorted(set(existing.stars).union(stars)))
                    if existing is not None
                    else stars
                ),
                full_star_time=_as_int(values.get("TotalTime"))
                if len(stars) >= 3
                else (existing.full_star_time if existing is not None else 0),
                best_time=existing.best_time if existing is not None else 0,
                pass_count=(existing.pass_count if existing is not None else 0) + 1,
            )
        rewards = [
            {
                "ItemId": LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
                "count": max(1, len(stars) or 1),
                "extra": [],
            }
        ] if result == 1 else []
        return {"RewardList": rewards}

    @staticmethod
    def stage_extra_reward(uid: int) -> dict[str, object]:
        return {
            "UserUid": int(uid),
            "DrawItems": [
                {
                    "ItemId": LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
                    "Num": 1,
                }
            ],
        }

    def resource_stage_info(self, hero_uid: int) -> dict[str, object]:
        completed_stage_ids = sorted(
            stage_id
            for stage_id, completion in self.completions.items()
            if completion.status == 1
        )
        progress_by_type: dict[int, int] = {}
        for stage_id in completed_stage_ids:
            resource_type = max(1, int(stage_id) // 100000)
            progress_by_type[resource_type] = max(
                progress_by_type.get(resource_type, 0),
                len(self.completions[stage_id].stars),
            )
        return {
            "Progress": [
                {"Type": resource_type, "Level": level}
                for resource_type, level in sorted(progress_by_type.items())
            ],
            "HeroUid": int(hero_uid),
            "PassStage": completed_stage_ids,
            "Chances": [
                {"Type": resource_type, "Chances": 3}
                for resource_type in range(1, 4)
            ],
        }

    def area_event_stage_data(self, stage_id: int) -> dict[str, object]:
        numeric_stage_id = int(stage_id)
        completion = self.completions.get(numeric_stage_id)
        return {
            "StageId": numeric_stage_id,
            "PassedTimes": completion.pass_count if completion else 0,
            "DropCountTimes": 0,
            "Star": len(completion.stars) if completion else 0,
        }

    def area_event_info(self, stage_id: int) -> dict[str, object]:
        return {"StageData": self.area_event_stage_data(stage_id)}

    def area_event_stage_times(self) -> list[dict[str, object]]:
        return [
            self.area_event_stage_times_for(stage.stage_id)
            for stage in AREA_EVENT_STAGES
        ]

    def area_event_stage_times_for(self, stage_id: int) -> dict[str, object]:
        completion = self.completions.get(int(stage_id))
        return {
            "StageId": int(stage_id),
            "FightTimes": completion.pass_count if completion else 0,
            "ResetTimes": 0,
        }

    def relax_stage_sync_times(self) -> dict[str, object]:
        box_times = sum(
            self.completions.get(stage.stage_id, StageCompletion(stage.stage_id)).pass_count
            for stage in RELAX_STAGES
        )
        reward_times = len(
            [
                stage
                for stage in RELAX_STAGES
                if self.completions.get(stage.stage_id) is not None
                and self.completions[stage.stage_id].status == 1
            ]
        )
        return {
            "DailyBoxTimes": min(1, box_times),
            "TotalBoxTimes": box_times,
            "DailyRewardTimes": min(1, reward_times),
            "TotalRewardTimes": reward_times,
        }

    def relax_stage_sync_data(self) -> dict[str, object]:
        times = self.relax_stage_sync_times()
        round_data = [
            stage.as_round_data(
                status=(
                    self.completions[stage.stage_id].status
                    if stage.stage_id in self.completions
                    else 0
                ),
                reward=(
                    1
                    if stage.stage_id in self.completions
                    and self.completions[stage.stage_id].status == 1
                    else 0
                ),
            )
            for stage in RELAX_STAGES
        ]
        return {**times, "RoundData": round_data, "StepsData": []}

    def relax_stage_sync_cond(self, cond_type: int, cond_id: int) -> dict[str, object]:
        stage = RELAX_STAGE_BY_ID.get(int(cond_id))
        completion = self.completions.get(int(cond_id))
        status = completion.status if completion is not None else 0
        reward = 1 if completion is not None and completion.status == 1 else 0
        return {
            "NewData": [
                {
                    "Type": int(cond_type),
                    "Id": stage.stage_id if stage is not None else int(cond_id),
                    "Status": status,
                    "Reward": reward,
                }
            ]
        }

    def relax_stage_boxinfo(self, uid: int) -> dict[str, object]:
        times = self.relax_stage_sync_times()
        return {
            "BoxInfo": [
                {
                    "Uid": int(uid),
                    "BoxList": [],
                    **times,
                }
            ]
        }

    def secret_area_stage(self, stage_id: int | None = None):
        resolved_stage_id = int(stage_id or self.current_stage_id or 0)
        return SECRET_AREA_STAGE_BY_ID.get(resolved_stage_id, DEFAULT_SECRET_AREA_STAGE)

    def secret_area_key(self, stage_id: int | None = None) -> dict[str, object]:
        stage = self.secret_area_stage(stage_id)
        return {
            "Status": 1,
            "KeyId": stage.key_id,
            "StageId": stage.stage_id,
            "LevelRangeId": stage.level_range_id,
        }

    def secret_area_cycle(self) -> dict[str, object]:
        return {
            "CycleTypeId": 1,
            "SeasonId": 1,
            "CycleId": 1,
            "PersonalityGroupId": 1,
            "EndTime": 4102444800,
        }

    def secret_area_times(self) -> dict[str, object]:
        completed = [
            stage_id
            for stage_id, completion in self.completions.items()
            if stage_id in SECRET_AREA_STAGE_BY_ID and completion.status == 1
        ]
        return {
            "DayIncomeTimes": min(3, len(completed)),
            "CycleIncomeTimes": len(completed),
        }

    def secret_area_history(self) -> dict[str, object]:
        history = [
            SECRET_AREA_STAGE_BY_ID[stage_id].as_history(
                waste_time=completion.best_time,
                reward_item_id=LOCAL_STAGE_PASS_REWARD_ITEM_ID,
            )
            for stage_id, completion in sorted(self.completions.items())
            if stage_id in SECRET_AREA_STAGE_BY_ID and completion.status == 1
        ]
        return {"HistoryList": history}

    def secret_area_cycle_record(self, uid: int, hero_id: int) -> dict[str, object]:
        records = []
        for stage_id, completion in sorted(self.completions.items()):
            stage = SECRET_AREA_STAGE_BY_ID.get(stage_id)
            if stage is None or completion.status != 1:
                continue
            records.append(
                {
                    "WasteTime": completion.best_time,
                    "KeyId": stage.key_id,
                    "LevelRangeId": stage.level_range_id,
                    "StageId": stage.stage_id,
                    "StageLevel": stage.floor,
                    "TeamMembers": [
                        {
                            "Uid": int(uid),
                            "AvatarId": 0,
                            "AvatarFrameId": 0,
                            "HeroId": int(hero_id),
                            "Level": 1,
                            "Name": "Local Hero",
                        }
                    ],
                }
            )
        return {"PreviousRecord": [], "HaveRecord": int(bool(records)), "CurrentRecord": records}

    def secret_area_all_hero(self, hero_ids: list[int]) -> dict[str, object]:
        return {
            "AllHero": [
                {
                    "ClassId": int(hero_id),
                    "Strength": 100,
                    "ReturnTime": 0,
                }
                for hero_id in hero_ids
            ]
        }

    def secret_area_players(
        self,
        *,
        uid: int,
        hero_id: int,
        level: int,
        fighting: int,
    ) -> dict[str, object]:
        return {
            "PlayerList": [
                {
                    "UserUid": int(uid),
                    "HeroId": int(hero_id),
                    "Fighting": int(fighting),
                    "Lv": int(level),
                    "EquipRune": [],
                }
            ]
        }

    def secret_area_stage_finish(
        self,
        uid: int,
        values: dict[str, object],
    ) -> dict[str, object]:
        stage = self.secret_area_stage()
        members = []
        for member in _dict_list(values.get("Members")):
            hurt_sum = _as_int(member.get("HurtSum"))
            members.append(
                {
                    "UserUid": _as_int(member.get("UserUid"), uid),
                    "DrawItems": [
                        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Num": 1}
                    ],
                    "FakeItems": [],
                    "ExtraItems": [],
                    "LeagueItems": [],
                    "HurtSum": hurt_sum,
                    "MaxCombo": 0,
                    "Reborn": 0,
                    "LeagueDraw": 0,
                }
            )
        if not members:
            members.append(
                {
                    "UserUid": int(uid),
                    "DrawItems": [
                        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Num": 1}
                    ],
                    "FakeItems": [],
                    "ExtraItems": [],
                    "LeagueItems": [],
                    "HurtSum": 0,
                    "MaxCombo": 0,
                    "Reborn": 0,
                    "LeagueDraw": 0,
                }
            )
        completion = self.complete_stage(
            StageCombatSummary(
                stage_id=stage.stage_id,
                result=1,
                time=60,
                max_combo=0,
                combo_damage=0,
                all_damage=sum(_as_int(member.get("HurtSum")) for member in members),
                on_hit_num=0,
                solo_boss_num=0,
                monster_kills=(),
                item_rewards=((LOCAL_STAGE_PASS_REWARD_ITEM_ID, len(members)),),
                skill_levels=(),
                button_counts=(),
                move_total=0,
                damage_members=(),
                mvp_uid=_as_int(values.get("MvpUserUid"), uid),
                reborn=0,
                combat_resolution=None,
                enemy_results=(),
                stage_time_limit=STARTER_INTRO_STAGE_TIME,
            )
        )
        return {
            "Members": members,
            "MvpUserUid": _as_int(values.get("MvpUserUid"), uid),
            "ScoreLevel": 1,
            "HierarchyUp": min(stage.floor + completion.pass_count, 40),
            "WasteTime": completion.best_time or 60,
            "KeyId": stage.key_id,
            "StageLevel": stage.floor,
        }

    def secret_area_stage_fail(
        self,
        uid: int,
        values: dict[str, object],
    ) -> dict[str, object]:
        stage = self.secret_area_stage()
        members = [
            {
                "UserUid": _as_int(member.get("UserUid"), uid),
                "HurtSum": _as_int(member.get("HurtSum")),
                "Reborn": 0,
            }
            for member in _dict_list(values.get("Members"))
        ] or [{"UserUid": int(uid), "HurtSum": 0, "Reborn": 0}]
        return {"Members": members, "KeyId": stage.key_id}

    def secret_area_history_add(self) -> dict[str, object]:
        stage = self.secret_area_stage()
        completion = self.completions.get(stage.stage_id)
        return {
            "History": stage.as_history(
                waste_time=completion.best_time if completion else 0,
                reward_item_id=LOCAL_STAGE_PASS_REWARD_ITEM_ID,
            )
        }

    def secret_area_drop_card(self, uid: int, card_pos: int) -> dict[str, object]:
        return {"UserUid": int(uid), "CardPos": int(card_pos)}

    def act_secret_info(self, act_id: int = 0) -> dict[str, object]:
        return {
            "ActId": int(act_id),
            "CurScore": len(self.secret_area_history()["HistoryList"]),
            "RewardTakeList": [],
            "LevelRangeId": self.secret_area_stage().level_range_id,
        }

    def act_secret_record_list(self, act_id: int = 0) -> dict[str, object]:
        records = [
            {
                "NameList": ["Local Hero"],
                "StageGroupId": SECRET_AREA_STAGE_BY_ID[stage_id].group_id,
                "Floor": SECRET_AREA_STAGE_BY_ID[stage_id].floor,
                "Score": len(completion.stars) or 1,
                "Time": completion.best_time or 60,
                "StageLevel": SECRET_AREA_STAGE_BY_ID[stage_id].floor,
            }
            for stage_id, completion in sorted(self.completions.items())
            if stage_id in SECRET_AREA_STAGE_BY_ID and completion.status == 1
        ]
        return {"ActId": int(act_id), "RecordList": records}

    def area_event_login_data(
        self,
        *,
        normal_lineup: list[int],
        act_lineup: list[int] | None = None,
        diff_lineup: list[int] | None = None,
    ) -> dict[str, object]:
        stage_data = [
            self.area_event_stage_data(stage.stage_id)
            for stage in AREA_EVENT_STAGES
        ]
        stage_times = self.area_event_stage_times()
        return {
            "StageData": stage_data,
            "DiffStageData": [],
            "CacheStageId": AREA_EVENT_STAGES[0].stage_id if AREA_EVENT_STAGES else 0,
            "DifficultCacheStageId": 0,
            "NormalLineup": list(normal_lineup),
            "ActLineup": list(act_lineup or []),
            "DiffLineup": list(diff_lineup or []),
            "StageFightTimes": stage_times,
            "DiffStageFightTimes": [],
        }

    def area_event_stage_pass(self, stage_id: int) -> dict[str, object]:
        completion = self.completions.get(int(stage_id))
        stars = list(completion.stars) if completion is not None else []
        return {
            "Star": stars,
            "FirstPass": int(completion.pass_count == 1) if completion else 0,
            "FirstPassPrize": [],
            "ImportantPrize": [],
        }

    def area_event_stage_metadata(self, stage_id: int) -> dict[str, object]:
        stage = AREA_EVENT_STAGE_BY_ID.get(int(stage_id))
        return stage.as_dict() if stage is not None else {}

    def record_area_event_fight_over(
        self,
        *,
        stage_id: int,
        is_win: int,
        use_time: int,
    ) -> dict[str, object]:
        summary = StageCombatSummary(
            stage_id=int(stage_id),
            result=1 if int(is_win) else 0,
            time=max(0, int(use_time)),
            max_combo=0,
            combo_damage=0,
            all_damage=0,
            on_hit_num=0,
            solo_boss_num=0,
        )
        if summary.passed:
            self.complete_stage(summary)
        else:
            existing = self.completions.get(summary.stage_id)
            self.completions[summary.stage_id] = StageCompletion(
                stage_id=summary.stage_id,
                status=0,
                stars=existing.stars if existing else (),
                full_star_time=existing.full_star_time if existing else 0,
                best_time=existing.best_time if existing else 0,
                pass_count=existing.pass_count if existing else 0,
            )
        return self.area_event_stage_pass(summary.stage_id)

    def pressure_stage_detail(
        self,
        stage_id: int,
        *,
        hero_list: list[dict[str, int]],
    ) -> dict[str, object]:
        numeric_stage_id = int(stage_id or self.current_stage_id or 0)
        stage_score = self.pressure_scores.get(numeric_stage_id, 0)
        total_score = sum(self.pressure_scores.values())
        return {
            "TotalScore": total_score,
            "TotalRank": 0,
            "StageId": numeric_stage_id,
            "StageScore": stage_score,
            "StageRank": 0,
            "TopList": (
                [
                    {
                        "Rank": 1,
                        "Number": [stage_score],
                        "String": ["Local Hero"],
                    }
                ]
                if stage_score
                else []
            ),
            "Count": 3,
            "HeroList": hero_list,
            "StageLevel": 1,
        }

    def record_pressure_stage_finish(self, values: dict[str, object]) -> None:
        stage_id = _as_int(values.get("StageId"), self.current_stage_id)
        score = _as_int(values.get("Score"))
        if stage_id:
            self.pressure_scores[stage_id] = max(
                score,
                self.pressure_scores.get(stage_id, 0),
            )

    def herochip_stage_sync_data(self) -> dict[str, object]:
        return {
            "DailyTimes": [
                {
                    "Id": stage.stage_id,
                    "Times": self.completions.get(
                        stage.stage_id, StageCompletion(stage.stage_id)
                    ).pass_count,
                }
                for stage in HEROCHIP_STAGES
            ],
            "PassStage": [
                stage.stage_id
                for stage in HEROCHIP_STAGES
                if self.completions.get(
                    stage.stage_id, StageCompletion(stage.stage_id)
                ).status
            ],
        }

    def herochip_red_info(self) -> dict[str, object]:
        return {
            "List": [
                stage.stage_id
                for stage in HEROCHIP_STAGES
                if not self.completions.get(
                    stage.stage_id, StageCompletion(stage.stage_id)
                ).status
            ]
        }

    def act_daily_stage_info(self, act_id: int = 0) -> dict[str, object]:
        return {
            "ActId": int(act_id),
            "Count": [
                {
                    "Id": stage.stage_id,
                    "Count": self.daily_stage_counts.get(stage.stage_id, 0),
                    "Extra": {
                        "NumList": [
                            stage.stage_id,
                            stage.sub_id,
                            stage.display_order,
                        ],
                        "StrList": [stage.section, stage.name],
                    },
                }
                for stage in ACT_DAILY_STAGES
            ],
        }

    def empty_shop_stage(self, stage_index: int | None = None):
        numeric_index = int(stage_index or 0)
        return (
            EMPTY_SHOP_STAGE_BY_INDEX.get(numeric_index)
            or EMPTY_SHOP_STAGE_BY_CHALLENGE_INDEX.get(numeric_index)
            or DEFAULT_EMPTY_SHOP_STAGE
        )

    def empty_shop_stage_update(
        self, act_id: int = 0, stage_index: int = 0
    ) -> dict[str, object]:
        stage = self.empty_shop_stage(stage_index)
        pass_stage = max(0, stage.challenge_index)
        self.empty_shop_max_pass_stage = max(self.empty_shop_max_pass_stage, pass_stage)
        return self.empty_shop_info(act_id)

    def empty_shop_info(self, act_id: int = 0) -> dict[str, object]:
        return {
            "ActId": int(act_id),
            "MaxPassStage": int(self.empty_shop_max_pass_stage),
        }

    def allsvr_stage(self, level_id: int | None = None):
        return ALLSVR_STAGE_BY_ID.get(int(level_id or 0), DEFAULT_ALLSVR_STAGE)

    def allsvr_boss_stage(self, boss_id: int = 0, difficulty: int = 0):
        return ALLSVR_BOSS_STAGE_BY_BOSS_AND_DIFFICULTY.get(
            (int(boss_id or 0), int(difficulty or 0)),
            DEFAULT_ALLSVR_BOSS_STAGE,
        )

    def allsvr_total_score(self) -> int:
        return sum(self.allsvr_level_counts.values()) * 100 + sum(
            self.allsvr_boss_scores.values()
        )

    def allsvr_cond_list(self) -> list[dict[str, object]]:
        score = self.allsvr_total_score()
        return [
            {"Id": cond_id, "State": int(score >= cond_id * 100)}
            for cond_id in ALLSVR_COND_IDS
        ]

    def allsvr_stage_info(self, act_id: int = 0) -> dict[str, object]:
        boss_stage = DEFAULT_ALLSVR_BOSS_STAGE
        return {
            "ActId": int(act_id),
            "AreaInfo": {
                "Id": DEFAULT_ALLSVR_STAGE.area_id,
                "Difficult": DEFAULT_ALLSVR_STAGE.difficulty,
                "LevelList": [{"Id": stage.stage_id} for stage in ALLSVR_STAGES],
            },
            "AllSvrScore": self.allsvr_total_score(),
            "AllSvrCond": self.allsvr_cond_list(),
            "BossInfo": {
                "Id": boss_stage.boss_id,
                "Count": self.allsvr_boss_scores.get(boss_stage.stage_id, 0),
                "BestScore": self.allsvr_boss_scores.get(boss_stage.stage_id, 0),
                "TodayScore": self.allsvr_boss_scores.get(boss_stage.stage_id, 0),
            },
        }

    def allsvr_stage_update_level(
        self,
        act_id: int = 0,
        level_id: int = 0,
    ) -> dict[str, object]:
        stage = self.allsvr_stage(level_id)
        self.allsvr_level_counts[stage.stage_id] = (
            self.allsvr_level_counts.get(stage.stage_id, 0) + 1
        )
        return {
            "ActId": int(act_id),
            "AreaInfo": {
                "Id": stage.area_id,
                "RewardList": [
                    {
                        "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                        "count": 1,
                        "extra": [],
                    }
                ],
                "LevelList": [
                    {
                        "Id": candidate.stage_id,
                        "Count": self.allsvr_level_counts.get(candidate.stage_id, 0),
                    }
                    for candidate in ALLSVR_STAGES
                    if candidate.area_id == stage.area_id
                ],
            },
        }

    def allsvr_stage_update_boss(
        self,
        act_id: int = 0,
        boss_id: int = 0,
        difficulty: int = 0,
    ) -> dict[str, object]:
        stage = self.allsvr_boss_stage(boss_id, difficulty)
        score = self.allsvr_boss_scores.get(stage.stage_id, 0) + 100
        self.allsvr_boss_scores[stage.stage_id] = score
        return {
            "ActId": int(act_id),
            "BossInfo": {
                "Id": stage.boss_id,
                "Count": 1,
                "Score": score,
                "BestScore": score,
                "TodayScore": score,
            },
        }

    def allsvr_stage_reward(self, act_id: int = 0) -> dict[str, object]:
        return {
            "ActId": int(act_id),
            "AllSvrScore": self.allsvr_total_score(),
            "AllSvrCond": self.allsvr_cond_list(),
        }

    def theater_open(self) -> dict[str, object]:
        area_ids = sorted({stage.area_id for stage in ALLSVR_STAGES})
        return {
            "ChapterInfo": [
                {
                    "Id": area_id,
                    "Status": 1,
                    "BonusInfo": [],
                }
                for area_id in area_ids
            ],
            "StageInfo": [
                {
                    "Id": stage.stage_id,
                    "Status": int(
                        stage.stage_id in self.theater_unlocked_stage_ids
                        or stage.stage_id == DEFAULT_ALLSVR_STAGE.stage_id
                        or self.allsvr_level_counts.get(stage.stage_id, 0) > 0
                    ),
                    "StarList": (
                        [1, 2, 3]
                        if self.allsvr_level_counts.get(stage.stage_id, 0) > 0
                        else []
                    ),
                    "FullStarTime": 0,
                    "DramaFinish": [],
                    "ViewTimes": self.allsvr_level_counts.get(stage.stage_id, 0),
                }
                for stage in ALLSVR_STAGES
            ],
            "BonusInfo": [
                {"Idx": int(key.split(":", 1)[1]), "BonusTime": value}
                for key, value in sorted(self.theater_bonus_claims.items())
                if key.startswith("bonus:")
            ],
            "GlobalBonusInfo": [],
            "UserContri": self.allsvr_total_score(),
            "GlobalContri": self.allsvr_total_score(),
        }

    def theater_unlock(self, stage_id: int = 0) -> dict[str, object]:
        resolved_stage_id = int(stage_id or DEFAULT_ALLSVR_STAGE.stage_id)
        self.theater_unlocked_stage_ids.add(resolved_stage_id)
        return {"StageId": resolved_stage_id, "Status": 1}

    def theater_bonus(self, cfg_type: int = 0, bonus_idx: int = 0) -> dict[str, object]:
        claim_key = f"bonus:{int(bonus_idx)}"
        self.theater_bonus_claims[claim_key] = self.theater_bonus_claims.get(
            claim_key,
            0,
        ) + 1
        return {
            "CfgType": int(cfg_type),
            "BonusIdx": int(bonus_idx),
            "Reward": [{"Id": LOCAL_STAGE_STYLE_REWARD_ITEM_ID, "Amount": 1}],
        }

    def theater_chapter_bonus(
        self,
        chapter_id: int = 0,
        star_idx: int = 0,
    ) -> dict[str, object]:
        claim_key = f"chapter:{int(chapter_id)}:{int(star_idx)}"
        self.theater_bonus_claims[claim_key] = self.theater_bonus_claims.get(
            claim_key,
            0,
        ) + 1
        return {"chapterid": int(chapter_id), "starIdx": int(star_idx)}

    def theater_finish(self, values: dict[str, object]) -> dict[str, object]:
        stage_id = int(values.get("StageId") or self.current_stage_id or 0)
        result = int(values.get("Result") or 0)
        if stage_id:
            self.theater_unlocked_stage_ids.add(stage_id)
            if result:
                self.allsvr_level_counts[stage_id] = max(
                    1,
                    self.allsvr_level_counts.get(stage_id, 0),
                )
        stage = ALLSVR_STAGE_BY_ID.get(stage_id, DEFAULT_ALLSVR_STAGE)
        return {
            "newChapterInfo": [{"Id": stage.area_id, "Status": 1}],
            "newStageInfo": [{"Id": stage.stage_id, "Status": int(bool(result))}],
        }

    def usj_cycle_id(self) -> dict[str, object]:
        return {"CycleId": 1}

    def usj_zone_id_for_point(self, point_id: int) -> int:
        if not point_id:
            return USJ_POINTS[0].point_id // 100 if USJ_POINTS else 0
        return int(point_id) // 100

    def usj_first_stage_for_point(self, point_id: int) -> int:
        point = USJ_POINT_BY_ID.get(int(point_id))
        if point is not None and point.stage_ids:
            return point.stage_ids[0]
        return USJ_STAGES[0].stage_id if USJ_STAGES else STARTER_INTRO_STAGE_ID

    def usj_load(
        self,
        *,
        hero_uids: list[int],
        current_hero_uid: int,
    ) -> dict[str, object]:
        zones: dict[int, list[int]] = {}
        for point in USJ_POINTS:
            zones.setdefault(self.usj_zone_id_for_point(point.point_id), []).append(
                point.point_id
            )

        current_point = self.current_usj_point_id or (
            USJ_POINTS[0].point_id if USJ_POINTS else 0
        )
        current_zone = self.usj_zone_id_for_point(current_point)
        return {
            "ServerTotalScore": sum(self.pressure_scores.values()),
            "UserTotalScore": sum(self.pressure_scores.values()),
            "HeroList": [
                {"HeroUid": int(hero_uid), "HpPercent": 100, "DeathTime": 0}
                for hero_uid in hero_uids
            ],
            "ZoneList": [
                {
                    "ZoneId": zone_id,
                    "AccessedPath": point_ids,
                    "ZoneRewards": [
                        {"RewardType": reward_type, "RewardState": 0}
                        for reward_type in (1, 2, 3)
                    ],
                    "PointRewards": [
                        {
                            "PointId": point_id,
                            "RewardState": int(
                                self.pressure_scores.get(point_id, 0) > 0
                            ),
                        }
                        for point_id in point_ids
                    ],
                    "ScoreList": [
                        {
                            "PointId": point_id,
                            "Score": self.pressure_scores.get(point_id, 0),
                        }
                        for point_id in point_ids
                    ],
                }
                for zone_id, point_ids in sorted(zones.items())
            ],
            "OpenZone": [
                {"ZoneId": zone_id, "Reason": 0}
                for zone_id in sorted(zones)
            ],
            "LevelRangeId": 1,
            "CurrentZoneId": current_zone,
            "CurrentPointId": current_point,
            "CurrentHeroUid": int(current_hero_uid),
            "RankReward": 0,
            "HaveShowEndReward": 0,
            "IsFirstTime": int(not self.pressure_scores),
            "ThemeId": 1,
            "NextThemeId": 0,
            "ScoreReward": [
                {"Id": reward_id, "State": 0}
                for reward_id in (1, 2, 3)
            ],
        }

    def usj_enter_stage(
        self,
        *,
        zone_id: int,
        point_id: int,
        hero_uid: int,
    ) -> dict[str, object]:
        self.current_usj_point_id = int(point_id)
        return {
            "ZoneId": int(zone_id or self.usj_zone_id_for_point(point_id)),
            "PointId": int(point_id),
            "HeroUid": int(hero_uid),
        }

    def usj_enter_next_zone(self, zone_id: int) -> dict[str, object]:
        zone_points = [
            point.point_id
            for point in USJ_POINTS
            if self.usj_zone_id_for_point(point.point_id) == int(zone_id)
        ]
        point_id = (
            zone_points[0]
            if zone_points
            else (USJ_POINTS[0].point_id if USJ_POINTS else 0)
        )
        return {"CurrentZoneId": int(zone_id), "CurrentPointId": point_id}

    def usj_point_reward(self, zone_id: int, point_ids: list[int]) -> dict[str, object]:
        return {
            "ZoneId": int(zone_id),
            "RewardList": [
                {
                    "PointId": int(point_id),
                    "Reward": [
                        {
                            "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                            "count": max(
                                1,
                                self.pressure_scores.get(int(point_id), 0) // 100,
                            ),
                            "extra": [],
                        }
                    ],
                }
                for point_id in point_ids
            ],
        }

    def usj_score_reward(self, reward_id: int) -> dict[str, object]:
        return {
            "List": [
                {"Id": int(reward_id), "State": 1},
            ]
        }

    def usj_zone_reward(self, zone_id: int, reward_type: int) -> dict[str, object]:
        return {"ZoneId": int(zone_id), "RewardType": int(reward_type)}

    def usj_stage_record(
        self,
        *,
        point_id: int,
        uid: int,
        user_level: int,
        hero_id: int,
        fighting: int,
    ) -> dict[str, object]:
        score = self.pressure_scores.get(int(point_id), 0)
        return {
            "StageRecords": (
                [
                    {
                        "PointId": int(point_id),
                        "UserUid": int(uid),
                        "UserName": "Local Hero",
                        "UserLevel": int(user_level),
                        "HeroId": int(hero_id),
                        "Fighting": int(fighting),
                        "Score": score,
                    }
                ]
                if score
                else []
            )
        }

    def usj_end_stage(
        self,
        values: dict[str, object],
        *,
        hero_uid: int,
    ) -> dict[str, object]:
        hurt_sum = _as_int(values.get("HurtSum"))
        hp_percent = _as_int(values.get("HpPercent"), 100)
        use_time = max(0, STARTER_INTRO_STAGE_TIME - hp_percent)
        base_score = max(0, hurt_sum // 100)
        time_score = max(0, hp_percent)
        score = base_score + time_score
        point_id = (
            self.current_usj_point_id
            or self.current_stage_id
            or STARTER_INTRO_STAGE_ID
        )
        self.pressure_scores[point_id] = max(
            score,
            self.pressure_scores.get(point_id, 0),
        )
        return {
            "CurrentZoneId": 0,
            "CurrentPointId": point_id,
            "CurrentHeroUid": int(hero_uid),
            "UserTotalScore": sum(self.pressure_scores.values()),
            "PointReward": [{"PointId": point_id, "RewardState": 1}],
            "UseTime": use_time,
            "HurtSum": hurt_sum,
            "Score": score,
            "HightestScore": self.pressure_scores[point_id],
            "Reason": _as_int(values.get("Reason")),
            "HpPercent": hp_percent,
            "BaseScore": base_score,
            "TimeScore": time_score,
        }

    def act_daily_stage_result(self, values: dict[str, object]) -> dict[str, object]:
        act_id = _as_int(values.get("ActId"))
        count = _as_int(values.get("Count"))
        result = _as_int(values.get("Result"))
        self.daily_stage_counts[act_id] = self.daily_stage_counts.get(act_id, 0) + 1
        reward = (
            [
                {
                    "AddLog": [
                        {
                            "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                            "count": max(1, count),
                            "extra": [],
                        }
                    ]
                }
            ]
            if result
            else []
        )
        return {
            "ActId": act_id,
            "Count": {
                "Id": act_id,
                "Count": self.daily_stage_counts[act_id],
                "Extra": {"NumList": [count], "StrList": []},
            },
            "RewardList": reward,
        }

    def empty_drop(self) -> dict[str, object]:
        return {
            "Monster": [],
            "Boss": [],
            "StagePassDrop": [],
            "Card": [],
            "VipCard": [],
            "FirstReward": [],
        }

    def stage_drop(
        self,
        *,
        fight_style: FightStyle | None = None,
        hero_level: int = 1,
        stage: BattleStageDefinition | None = None,
    ) -> dict[str, object]:
        summary = self.combat_summary(
            fight_style=fight_style,
            hero_level=hero_level,
            stage=stage,
        )
        completion = self.completions.get(
            summary.stage_id, StageCompletion(summary.stage_id)
        )
        pass_count = completion.pass_count
        pass_reward = max(1, summary.estimated_defeats or len(summary.monster_kills) or 1)
        return {
            "Monster": [
                {
                    "idx": index + 1,
                    "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                    "Count": 1,
                }
                for index in range(max(0, summary.estimated_defeats))
            ],
            "Boss": [],
            "StagePassDrop": [
                {
                    "idx": 1,
                    "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                    "Count": pass_reward,
                }
            ],
            "Card": [],
            "VipCard": [],
            "FirstReward": (
                [
                    {
                        "idx": 1,
                        "ItemId": LOCAL_STAGE_FIRST_REWARD_ITEM_ID,
                        "Count": 1,
                    }
                ]
                if summary.passed and pass_count == 0
                else []
            ),
        }

    def load_completions(
        self, values: dict[str, dict[str, int | list[int]]]
    ) -> None:
        self.completions = {}
        for stage_id, progress in values.items():
            try:
                numeric_stage_id = int(stage_id)
            except (TypeError, ValueError):
                continue
            self.completions[numeric_stage_id] = StageCompletion.from_profile(
                numeric_stage_id, dict(progress)
            )

    def load_family_progress(
        self, values: dict[str, dict[str, int]]
    ) -> None:
        self.pressure_scores = self._int_section(
            values.get("pressure_scores", {})
        )
        self.daily_stage_counts = self._int_section(
            values.get("daily_stage_counts", {})
        )
        self.allsvr_level_counts = self._int_section(
            values.get("allsvr_level_counts", {})
        )
        self.allsvr_boss_scores = self._int_section(
            values.get("allsvr_boss_scores", {})
        )
        self.night_fight_statuses = self._int_section(
            values.get("night_fight_statuses", {})
        )
        self.night_fight_hero_tired = self._int_section(
            values.get("night_fight_hero_tired", {})
        )
        empty_shop_progress = self._int_section(
            values.get("empty_shop_max_pass_stage", {})
        )
        self.empty_shop_max_pass_stage = max(empty_shop_progress.values(), default=0)
        self.theater_unlocked_stage_ids = set(
            self._int_section(values.get("theater_unlocked_stage_ids", {}))
        )
        self.theater_bonus_claims = {}
        bonus_claims = values.get("theater_bonus_claims", {})
        if isinstance(bonus_claims, dict):
            for key, value in bonus_claims.items():
                try:
                    numeric_value = int(value)
                except (TypeError, ValueError):
                    continue
                if isinstance(key, str) and numeric_value >= 0:
                    self.theater_bonus_claims[key] = numeric_value

    def export_completions(self) -> dict[int, dict[str, int | list[int]]]:
        return {
            stage_id: completion.to_profile()
            for stage_id, completion in sorted(self.completions.items())
        }

    def export_family_progress(self) -> dict[str, dict[int, int]]:
        return {
            "pressure_scores": dict(sorted(self.pressure_scores.items())),
            "daily_stage_counts": dict(sorted(self.daily_stage_counts.items())),
            "allsvr_level_counts": dict(sorted(self.allsvr_level_counts.items())),
            "allsvr_boss_scores": dict(sorted(self.allsvr_boss_scores.items())),
            "night_fight_statuses": dict(sorted(self.night_fight_statuses.items())),
            "night_fight_hero_tired": dict(sorted(self.night_fight_hero_tired.items())),
            "empty_shop_max_pass_stage": {1: int(self.empty_shop_max_pass_stage)},
            "theater_unlocked_stage_ids": {
                stage_id: 1 for stage_id in sorted(self.theater_unlocked_stage_ids)
            },
            "theater_bonus_claims": dict(sorted(self.theater_bonus_claims.items())),
        }

    @staticmethod
    def _int_section(values: dict[str, int]) -> dict[int, int]:
        output: dict[int, int] = {}
        if not isinstance(values, dict):
            return output
        for key, value in values.items():
            try:
                numeric_key = int(key)
                numeric_value = int(value)
            except (TypeError, ValueError):
                continue
            if numeric_key > 0 and numeric_value >= 0:
                output[numeric_key] = numeric_value
        return output

    def complete_stage(self, summary: StageCombatSummary) -> StageCompletion:
        existing = self.completions.get(summary.stage_id)
        if not summary.passed:
            completion = StageCompletion(
                stage_id=summary.stage_id,
                status=0,
                stars=existing.stars if existing else (),
                full_star_time=existing.full_star_time if existing else 0,
                best_time=existing.best_time if existing else 0,
                pass_count=existing.pass_count if existing else 0,
            )
            self.completions[summary.stage_id] = completion
            return completion

        previous_stars = set(existing.stars if existing else ())
        stars = tuple(sorted(previous_stars.union(summary.stars)))
        previous_best = existing.best_time if existing else 0
        best_time = (
            summary.time
            if summary.time and (not previous_best or summary.time < previous_best)
            else previous_best
        )
        full_star_time = (
            summary.time
            if len(stars) >= 3 and summary.time
            else (existing.full_star_time if existing else 0)
        )
        completion = StageCompletion(
            stage_id=summary.stage_id,
            status=1,
            stars=stars,
            full_star_time=full_star_time,
            best_time=best_time,
            pass_count=(existing.pass_count if existing else 0) + 1,
        )
        self.completions[summary.stage_id] = completion
        return completion

    def combat_summary(
        self,
        *,
        fight_style: FightStyle | None = None,
        hero_level: int = 1,
        stage: BattleStageDefinition | None = None,
    ) -> StageCombatSummary:
        report = self.reports[-1] if self.reports else {}
        end_report = report.get("EndReport")
        end = dict(end_report) if isinstance(end_report, dict) else {}
        damage_report = self.damage_reports[-1] if self.damage_reports else {}

        result_value = report.get("Result")
        result = 1 if result_value is None else _as_int(result_value, 1)
        stage_id = _as_int(
            report.get("Id"),
            self.current_stage_id or STARTER_INTRO_STAGE_ID,
        )
        time = _as_int(end.get("RoundTimeUse"), 0)
        max_combo = max(
            _as_int(report.get("MaxCombo")),
            _as_int(end.get("RoundFighterComboMax")),
            _as_int(damage_report.get("MaxCombo")),
        )
        all_damage = max(
            _as_int(report.get("AllDmg")),
            _as_int(end.get("RoundFighterDpsTotal")),
            _as_int(end.get("RoundFighterAtkTotal")),
        )
        monster_kills = tuple(
            (
                _as_int(item.get("MonsterId")),
                _as_int(item.get("Amount")),
            )
            for item in _dict_list(report.get("MonsterNum"))
        )
        item_rewards = tuple(
            (
                _as_int(item.get("ItemId")),
                _as_int(item.get("Amount")),
            )
            for item in _dict_list(report.get("ItemNum"))
        )
        skill_levels = tuple(
            (
                _as_int(item.get("SkillId")),
                _as_int(item.get("SkillLevel")),
            )
            for item in _dict_list(end.get("SkillLevel"))
        )
        button_counts = [
            ("ATK", _as_int(end.get("RoundFighterButtonClickCountATK"))),
        ]
        button_counts.extend(
            (
                str(index),
                _as_int(end.get(f"RoundFighterButtonClickCount{index}")),
            )
            for index in range(1, 11)
        )
        damage_members = tuple(
            (
                _as_int(item.get("UserUid")),
                _as_int(item.get("HurtSum")),
            )
            for item in _dict_list(damage_report.get("Members"))
        )
        target_count = (
            stage.encounter_target_count
            if stage is not None
            else max(1, len(monster_kills), len(self.monster_frames))
        )
        combat_resolution = (
            fight_style.resolve_usage(
                tuple(button_counts),
                hero_level=hero_level,
                reported_damage=all_damage,
                target_count=target_count,
                target_hp_values=(
                    tuple(spawn.combat_hp for spawn in stage.encounter_spawns)
                    if stage is not None
                    else ()
                ),
            )
            if fight_style is not None
            else None
        )
        enemy_results = (
            _resolve_enemy_results(stage.encounter_spawns, combat_resolution)
            if stage is not None and combat_resolution is not None
            else ()
        )
        return StageCombatSummary(
            stage_id=stage_id,
            result=result,
            time=time,
            max_combo=max_combo,
            combo_damage=_as_int(report.get("ComboDmg")),
            all_damage=all_damage,
            on_hit_num=_as_int(report.get("OnHitNum")),
            solo_boss_num=_as_int(report.get("SoloBossNum")),
            monster_kills=monster_kills,
            item_rewards=item_rewards,
            skill_levels=skill_levels,
            button_counts=tuple(button_counts),
            move_total=_as_int(end.get("RoundFighterMoveTotal")),
            damage_members=damage_members,
            mvp_uid=_as_int(damage_report.get("MvpUserUid")),
            reborn=_as_int(damage_report.get("Reborn")),
            combat_resolution=combat_resolution,
            enemy_results=enemy_results,
            stage_time_limit=stage.time_limit if stage is not None else STARTER_INTRO_STAGE_TIME,
        )

    def damage_info(self) -> dict[str, object]:
        return {}

    def result(
        self,
        result: int | None = None,
        *,
        fight_style: FightStyle | None = None,
        hero_level: int = 1,
        stage: BattleStageDefinition | None = None,
    ) -> dict[str, object]:
        summary = self.combat_summary(
            fight_style=fight_style,
            hero_level=hero_level,
            stage=stage,
        )
        stage_result = summary.result if result is None else result
        completion = (
            self.complete_stage(summary)
            if stage_result == 1
            else self.completions.get(summary.stage_id)
        )
        return {
            "StageId": summary.stage_id,
            "Result": stage_result,
            "Time": summary.time,
            "RewardList": summary.result_rewards if stage_result == 1 else [],
            "StageInfo": [
                (
                    completion.to_stage_info()
                    if completion is not None
                    else {
                        "Id": summary.stage_id,
                        "Status": stage_result,
                        "StarList": [],
                        "FullStarTime": 0,
                    }
                )
            ],
        }

    def end_gm(
        self,
        result: int | None = None,
        *,
        fight_style: FightStyle | None = None,
        hero_level: int = 1,
        stage: BattleStageDefinition | None = None,
    ) -> dict[str, object]:
        summary = self.combat_summary(
            fight_style=fight_style,
            hero_level=hero_level,
            stage=stage,
        )
        return {"Result": summary.result if result is None else result}


def _resolve_enemy_results(
    spawns: tuple[StageEnemySpawn, ...],
    combat_resolution: CombatResolution,
) -> tuple[StageEnemyCombatResult, ...]:
    remaining_damage = max(0, combat_resolution.estimated_damage)
    last_skill = ""
    for move_result in reversed(combat_resolution.move_results):
        if move_result.count or move_result.estimated_damage:
            last_skill = move_result.name
            break

    results: list[StageEnemyCombatResult] = []
    for spawn in spawns:
        hp = spawn.combat_hp
        damage_taken = min(hp, remaining_damage)
        remaining_damage = max(0, remaining_damage - damage_taken)
        results.append(
            StageEnemyCombatResult(
                uid=spawn.uid,
                enemy_id=spawn.enemy_id,
                label=spawn.label,
                display_name=spawn.display_name,
                ai_profile_key=spawn.ai_profile_key,
                placement_source=spawn.placement_source,
                authored_placement=spawn.is_authored_placement,
                max_hp=hp,
                damage_taken=damage_taken,
                defeated=damage_taken >= hp,
                last_skill=last_skill,
                threat_score=_enemy_threat_score(spawn, damage_taken),
                action_hint=_enemy_action_hint(spawn, damage_taken >= hp),
            )
        )
    return tuple(results)


def _enemy_threat_score(spawn: StageEnemySpawn, damage_taken: int) -> int:
    profile = spawn.ai_profile
    base = max(1, profile.attack_range // 80)
    if spawn.ai_profile_key in {"sludge_boss", "boss_brute", "nomu_brute"}:
        base += 4
    elif spawn.ai_profile_key == "mechanical_boss":
        base += 5
    elif spawn.ai_profile_key == "ranged_pressure":
        base += 3
    if damage_taken <= 0:
        base += 2
    return base


def _enemy_action_hint(spawn: StageEnemySpawn, defeated: bool) -> str:
    if defeated:
        return "defeated"
    profile = spawn.ai_profile
    first_skill = profile.skill_rotation[0] if profile.skill_rotation else "advance"
    return f"{profile.behavior}; next={first_skill}"
