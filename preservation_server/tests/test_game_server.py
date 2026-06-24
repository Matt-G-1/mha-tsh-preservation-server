from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import struct
from pathlib import Path
from unittest.mock import AsyncMock, patch

from mhatsh_server.allsvr_stages import (
    ALLSVR_BOSS_STAGE_BY_ID,
    ALLSVR_BOSS_STAGES,
    ALLSVR_STAGE_BY_ID,
    ALLSVR_STAGE_SOURCE,
    ALLSVR_STAGES,
)
from mhatsh_server.activity_state import ActivityState
from mhatsh_server.area_event_stages import (
    AREA_EVENT_STAGE_BY_ID,
    AREA_EVENT_STAGES,
    AREA_EVENT_STAGE_SOURCE,
)
from mhatsh_server.act_daily_stages import (
    ACT_DAILY_MONSTER_IDS,
    ACT_DAILY_STAGE_BY_ID,
    ACT_DAILY_STAGE_SOURCE,
    ACT_DAILY_STAGES,
    ACT_DAILY_TOTAL_LIMIT,
)
from mhatsh_server.empty_shop_stages import (
    EMPTY_SHOP_END_TASK_ID,
    EMPTY_SHOP_STAGE_BY_ID,
    EMPTY_SHOP_STAGE_SOURCE,
    EMPTY_SHOP_START_TASK_ID,
    EMPTY_SHOP_STAGES,
)
from mhatsh_server.beginner_quest import (
    BEGINNER_QUEST_DEATH_ARMS_UID,
    STARTER_MAP_GUIDE_ID,
    STARTER_MAP_GUIDE_SET_ID,
)
from mhatsh_server.game_server import (
    CITY_LEVEL_CAP,
    FUNCTION_OPEN_IDS,
    PLAYER_LEVEL_CAP,
    STARTER_CARD_UID,
    STARTER_HERO_ID,
    STARTER_SCENE_ID,
    STARTER_SCENE_X,
    STARTER_SCENE_Y,
    STARTER_SCENE_Z,
    STARTER_SHAPE_ID,
    GameServer,
    Session,
)
from mhatsh_server.intro import (
    INTRO_EVIDENCE_SOURCE,
    INTRO_ONLY_COSTUMES,
    SCHOOL_MIDORIYA_INTRO_COSTUME,
    STARTER_INTRO_STAGE_CANDIDATES,
    STARTER_RECAP_VIDEO,
)
from mhatsh_server.characters import (
    CATALOG_SOURCE,
    CHIBI_MODEL_ASSETS,
    DEATH_ARMS,
    DEATH_ARMS_DEMO_SPAWN,
    DEMO_CAST_MAP_SPAWNS,
    INITIAL_MAP_SPAWNS,
    INITIAL_PLAYABLE_ROSTER,
    MAP_CHARACTERS,
    NON_PUBLIC_PLAYABLE_MODEL_REASONS,
    PLAYABLE_CHARACTERS,
    PUBLIC_PLAYABLE_MODEL_IDS,
    RECOVERED_HERO_CHARACTERS,
    SUPPORT_CARD_ITEM_IDS,
    STARTER_CHARACTER,
    SUPPORT_CHARACTERS,
    TUTORIAL_MAP_SPAWNS,
    VERIFIED_PLAYABLE_ROSTER,
    map_spawns,
    playable_card,
    playable_roster,
    scene_npc,
    scene_npc_from_spawn,
    support_card_book_entries,
)
from mhatsh_server.combat import (
    COMBAT_CATALOG_SOURCE,
    DEFAULT_MOVES,
    HERO_CFG_AI_NAMES_BY_MODEL,
    HERO_CFG_ACTION_MAP_BY_MODEL,
    FIGHT_STYLES_BY_MODEL,
    HERO_CFG_COMBAT_METADATA_BY_MODEL,
    HERO_SKILL_INFO_EVIDENCE_BY_MODEL,
    HERO_SUPPORT_SKILL_EVIDENCE_BY_MODEL,
    HERO_SKILL_VIDEO_EVIDENCE_BY_MODEL,
    NON_PLAYABLE_FIGHT_STYLE_MODEL_IDS,
    fight_style_for_character,
    skill_slot_labels_for_command,
)
from mhatsh_server.combat_action_hints import RECOVERED_HERO_ACTION_HINTS_BY_MODEL
from mhatsh_server.combat_internal_action_hints import (
    RECOVERED_INTERNAL_ACTION_HINTS_BY_MODEL,
)
from mhatsh_server.herochip_stages import (
    HEROCHIP_STAGE_BY_ID,
    HEROCHIP_STAGE_SOURCE,
    HEROCHIP_STAGES,
)
from mhatsh_server.relax_stages import (
    RELAX_STAGE_BY_ID,
    RELAX_STAGE_SOURCE,
    RELAX_STAGES,
)
from mhatsh_server.roguelike_stages import (
    ROGUELIKE_STAGE_BY_ID,
    ROGUELIKE_STAGE_SOURCE,
    ROGUELIKE_STAGES,
)
from mhatsh_server.secret_area_stages import (
    DEFAULT_SECRET_AREA_STAGE,
    SECRET_AREA_STAGE_BY_ID,
    SECRET_AREA_STAGE_SOURCE,
    SECRET_AREA_STAGES,
)
from mhatsh_server.usj_stages import (
    USJ_POINT_BY_ID,
    USJ_POINTS,
    USJ_STAGE_BY_ID,
    USJ_STAGE_SOURCE,
    USJ_STAGES,
)
from mhatsh_server.skill_info_structured_terms import (
    STRUCTURED_SKILL_INFO_TERMS_BY_MODEL,
)
from mhatsh_server.protocol import FrameDecoder, ProtocolCodec, RollingXor, encode_frame
from mhatsh_server.schema import SchemaRegistry
from mhatsh_server.stages import (
    ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS,
    ENEMY_AI_PROFILES,
    RECOVERED_BATTLE_STAGE_BY_ID,
    RECOVERED_BATTLE_STAGE_BY_KEY,
    RECOVERED_BATTLE_STAGES,
    LOCAL_STAGE_FIRST_REWARD_ITEM_ID,
    LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
    LOCAL_STAGE_PASS_REWARD_ITEM_ID,
    LOCAL_STAGE_STYLE_REWARD_ITEM_ID,
    MONSTER_CFG_EVIDENCE_BY_ID,
    STARTER_INTRO_STAGE_DRAMA,
    STARTER_INTRO_STAGE_ID,
    STARTER_INTRO_STAGE_LEVEL,
    STARTER_INTRO_STAGE_TIME,
    STARTER_INTRO_STAGE_UID,
    STAGE_CATALOG_SOURCE,
    STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE,
    STAGE_CFG_AI_PROFILE_OVERRIDES_BY_ENEMY_ID,
    STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE,
    STAGE_CFG_ENCOUNTER_GROUPS,
    STAGE_CFG_ROUTE_LABELS,
    StageState,
    STAGE_CFG_SCRIPT_ROUTE_GROUPS,
    ZX_NUMERIC_STAGE_SCRIPT_GROUPS,
    generated_enemy_profile_key,
    generated_stage_spawns,
    stage_candidate_by_id,
    stage_candidate_by_key,
)
from mhatsh_server.tasks import (
    STARTER_GUIDE_ID,
    STARTER_GUIDE_STEP,
    STARTER_TASK,
    TASK_STATUS_ACCEPTED,
    TASK_STATUS_FINISHED,
    TaskState,
)
from mhatsh_server.tutorial import TutorialState
from mhatsh_server.world import ScenePosition, WorldState
from mhatsh_server.world_tasks import (
    BEGINNER_QUEST_CITY_EXP,
    BEGINNER_QUEST_CITY_LEVEL,
    STARTER_WORLD_AREA_ID,
    STARTER_WORLD_MAP_ID,
    WorldTaskState,
)


ROOT = Path(__file__).resolve().parents[2]
LEGACY_STARTER_ENV = {
    "MHATSH_PLAYER_LEVEL": "1",
    "MHATSH_HERO_LEVEL": "1",
    "MHATSH_CITY_LEVEL": "1",
    "MHATSH_SKIP_STARTER_QUEST": "0",
    "MHATSH_UNLOCK_ALL_FUNCTIONS": "0",
    "MHATSH_ROSTER_MODE": "starter",
}


def _load_stage_cfg_hint_script():
    script_path = ROOT / "scripts" / "derive_stage_cfg_string_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_stage_cfg_string_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_asset_drama_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_asset_drama_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_asset_drama_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_stage_cfg_route_hint_script():
    script_path = ROOT / "scripts" / "derive_stage_cfg_route_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_stage_cfg_route_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_area_event_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_area_event_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_area_event_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_act_daily_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_act_daily_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_act_daily_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_usj_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_usj_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_usj_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_herochip_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_herochip_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_herochip_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_roguelike_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_roguelike_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_roguelike_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_relax_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_relax_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_relax_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_allsvr_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_allsvr_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_allsvr_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_empty_shop_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_empty_shop_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_empty_shop_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_secret_area_stage_hint_script():
    script_path = ROOT / "scripts" / "derive_secret_area_stage_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_secret_area_stage_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_stage_cfg_encounter_hint_script():
    script_path = ROOT / "scripts" / "derive_stage_cfg_encounter_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_stage_cfg_encounter_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_stage_monster_evidence_script():
    script_path = ROOT / "scripts" / "derive_stage_monster_evidence.py"
    spec = importlib.util.spec_from_file_location(
        "derive_stage_monster_evidence", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_enemy_ai_profile_hint_script():
    script_path = ROOT / "scripts" / "derive_enemy_ai_profile_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_enemy_ai_profile_hints", script_path
    )
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_stage_spawn_hint_script():
    script_path = ROOT / "scripts" / "derive_stage_spawn_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_stage_spawn_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_monster_cfg_hint_script():
    script_path = ROOT / "scripts" / "derive_monster_cfg_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_monster_cfg_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_skill_info_hint_script():
    script_path = ROOT / "scripts" / "derive_skill_info_hints.py"
    spec = importlib.util.spec_from_file_location("derive_skill_info_hints", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_support_skill_hint_script():
    script_path = ROOT / "scripts" / "derive_hero_support_skill_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_hero_support_skill_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_skill_slot_hint_script():
    script_path = ROOT / "scripts" / "derive_skill_slot_hints.py"
    spec = importlib.util.spec_from_file_location("derive_skill_slot_hints", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_combat_action_hint_script():
    script_path = ROOT / "scripts" / "derive_combat_action_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_combat_action_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_internal_combat_action_hint_script():
    script_path = ROOT / "scripts" / "derive_internal_combat_action_hints.py"
    spec = importlib.util.spec_from_file_location(
        "derive_internal_combat_action_hints", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def roster_card(
    character,
    card_uid: int,
    *,
    fighting: int = 0,
    level: int = 1,
) -> dict[str, object]:
    values = playable_card(character, card_uid, level=level)
    values["Fighting"] = fighting
    return values


def test_starter_identity_matches_archived_midoriya_config() -> None:
    assert STARTER_HERO_ID == 1011
    assert STARTER_SHAPE_ID == 1001


def test_axmd_catalog_keeps_asset_ids_separate_from_protocol_ids() -> None:
    assert "AXMD raw-rip" in CATALOG_SOURCE
    assert "en_hero_cfg" in CATALOG_SOURCE
    assert len(RECOVERED_HERO_CHARACTERS) == 31
    assert len(PLAYABLE_CHARACTERS) == 26
    assert len(SUPPORT_CHARACTERS) == 12
    assert len(MAP_CHARACTERS) == 40
    assert len(CHIBI_MODEL_ASSETS) == 3
    assert SUPPORT_CHARACTERS["h1927"].name == "Best Jeanist"
    assert SUPPORT_CHARACTERS["h1927"].item_id == 6230016
    assert SUPPORT_CHARACTERS["h1927"].shape_id == 1927
    assert SUPPORT_CHARACTERS["h1927"].support_type == 2
    assert 6230016 in SUPPORT_CARD_ITEM_IDS
    assert support_card_book_entries()[0] == {"ItemId": 6111045, "Type": 2}
    assert support_card_book_entries()[-1] == {"ItemId": 6230016, "Type": 2}
    assert STARTER_CHARACTER == PLAYABLE_CHARACTERS["h1001"]
    assert STARTER_CHARACTER.hero_id == 1011
    assert STARTER_CHARACTER.shape_id == 1001
    assert sum(
        character.is_protocol_verified
        for character in RECOVERED_HERO_CHARACTERS.values()
    ) == 30
    assert len(PUBLIC_PLAYABLE_MODEL_IDS) == 26
    assert set(PLAYABLE_CHARACTERS) == set(PUBLIC_PLAYABLE_MODEL_IDS)
    assert "h1018" not in PUBLIC_PLAYABLE_MODEL_IDS
    assert "h1018" not in PLAYABLE_CHARACTERS
    assert "h1927" not in PUBLIC_PLAYABLE_MODEL_IDS
    assert set(NON_PUBLIC_PLAYABLE_MODEL_REASONS) == {
        "h1004",
        "h1018",
        "h1024",
        "h1039",
        "h1998",
    }
    assert "not public playable" in NON_PUBLIC_PLAYABLE_MODEL_REASONS["h1018"]
    assert all(
        character.model_asset_id != "h1018"
        for character in VERIFIED_PLAYABLE_ROSTER
    )
    assert PLAYABLE_CHARACTERS["h1031"].name == "Tamaki Amajiki"
    assert PLAYABLE_CHARACTERS["h1031"].hero_id == 1311
    assert PLAYABLE_CHARACTERS["h1031"].shape_id == 1031
    assert PLAYABLE_CHARACTERS["h1032"].name == "Mirio Togata"
    assert PLAYABLE_CHARACTERS["h1032"].hero_id == 1321
    assert PLAYABLE_CHARACTERS["h1110"].shape_id == 1011
    assert RECOVERED_HERO_CHARACTERS["h1998"].name == "All Might (Art Test Variant)"
    assert RECOVERED_HERO_CHARACTERS["h1998"].shape_id == 9051
    assert [
        (character.hero_id, character.shape_id)
        for character in INITIAL_PLAYABLE_ROSTER
    ] == [
        (1011, 1001),
        (1021, 1002),
        (1061, 1006),
        (1071, 1007),
        (1081, 1008),
        (1091, 1009),
        (1101, 1010),
    ]
    assert MAP_CHARACTERS[5007].name == "Death Arms"
    assert MAP_CHARACTERS[5007].npc_id == 5007
    assert MAP_CHARACTERS[5007].is_spawn_verified
    verified_map_names = {
        model_id: MAP_CHARACTERS[model_id].name
        for model_id in (5001, 5008, 5009, 5011, 5035, 5041)
    }
    assert verified_map_names == {
        5001: "Mei Hatsume (Story)",
        5008: "Kamui Woods",
        5009: "Naomasa Tsukauchi",
        5011: "Mt. Lady",
        5035: "Shota Aizawa",
        5041: "Mei Hatsume (U.A.)",
    }
    assert all(
        MAP_CHARACTERS[model_id].npc_id == model_id
        for model_id in verified_map_names
    )


def test_starter_intro_evidence_catalog_tracks_video_and_school_costume() -> None:
    assert "1294fd82be3620d3" in INTRO_EVIDENCE_SOURCE
    assert STARTER_RECAP_VIDEO.hashed_asset_path == "4YOU/1294fd82be3620d3"
    assert STARTER_RECAP_VIDEO.md5 == "85546BD65E1B15BBFDE53A28E4DB39C6"
    assert (STARTER_RECAP_VIDEO.width, STARTER_RECAP_VIDEO.height) == (1600, 720)
    assert STARTER_RECAP_VIDEO.duration_seconds == 40
    assert STARTER_RECAP_VIDEO.contains_qte_overlay is False
    assert "video/zx/chapter2/lvb01.flv" in (
        STARTER_RECAP_VIDEO.logical_name_candidates
    )

    assert SCHOOL_MIDORIYA_INTRO_COSTUME.label == "school_uniform_midoriya"
    assert SCHOOL_MIDORIYA_INTRO_COSTUME.owner_model_asset_id == "h1001"
    assert SCHOOL_MIDORIYA_INTRO_COSTUME.hero_cfg_row == 192
    assert SCHOOL_MIDORIYA_INTRO_COSTUME.npc_id == 71104
    assert SCHOOL_MIDORIYA_INTRO_COSTUME.shape_id == 2993
    assert SCHOOL_MIDORIYA_INTRO_COSTUME.preload_shape_ids == (2993, 2994)
    assert SCHOOL_MIDORIYA_INTRO_COSTUME.is_intro_only
    assert INTRO_ONLY_COSTUMES == (SCHOOL_MIDORIYA_INTRO_COSTUME,)

    assert STARTER_INTRO_STAGE_CANDIDATES[STARTER_INTRO_STAGE_ID]["characters"] == (
        "All Might",
        "Sludge",
        "Midoriya",
        "Bakugo",
    )


def test_recovered_battle_stage_catalog_promotes_parsed_stage_assets() -> None:
    assert "battle_stage_candidate_catalog" in STAGE_CATALOG_SOURCE
    assert len(RECOVERED_BATTLE_STAGES) >= 851
    assert len(RECOVERED_BATTLE_STAGE_BY_ID) >= 844
    stage_ids = [
        stage.stage_id for stage in RECOVERED_BATTLE_STAGES if stage.stage_id is not None
    ]
    assert len(stage_ids) == len(set(stage_ids))
    assert RECOVERED_BATTLE_STAGE_BY_KEY["battle_drama_zx_only"].stage_id is None
    assert stage_candidate_by_id(500).scripts == ("stage500",)
    assert stage_candidate_by_id(101002).scripts == ("zx_101002_1",)
    assert stage_candidate_by_id(404001).scripts == (
        "zx_404001_1",
        "zx_404001_2",
        "zx_404001_21",
        "zx_404001_22",
        "zx_404001_23",
        "zx_404001_3",
    )
    assert "zx_801201_7" in stage_candidate_by_id(801201).scripts
    assert stage_candidate_by_id(801204).scripts == ("zx_801204_1",)
    assert stage_candidate_by_id(801206).scripts == ("zx_801206_1",)
    assert set(ZX_NUMERIC_STAGE_SCRIPT_GROUPS).issubset(RECOVERED_BATTLE_STAGE_BY_ID)

    area_event_stage = stage_candidate_by_id(21111)
    assert area_event_stage.key == "area_event_stage_21111"
    assert area_event_stage.label == "1-1首次出击"
    assert area_event_stage.scripts == ("area1_1",)
    assert area_event_stage.source == AREA_EVENT_STAGE_SOURCE
    assert [spawn.enemy_id for spawn in area_event_stage.encounter_spawns] == [2005]
    assert area_event_stage.encounter_spawns[0].placement_source == (
        "generated_fallback"
    )
    assert stage_candidate_by_id(211461).label == "14-6林中小路"

    act_daily_stage = stage_candidate_by_id(880004)
    assert act_daily_stage.key == "act_daily_stage_880004"
    assert act_daily_stage.label == "爆豪胜己"
    assert act_daily_stage.source == ACT_DAILY_STAGE_SOURCE
    assert act_daily_stage.enemy_group_ids == ACT_DAILY_MONSTER_IDS
    assert [spawn.enemy_id for spawn in act_daily_stage.encounter_spawns] == [
        2202,
        2472,
        3007,
    ]
    assert stage_candidate_by_id(882008).label == "snowman_daily_challenge 882008"

    usj_stage = stage_candidate_by_id(700101)
    assert usj_stage.key == "usj_stage_700101"
    assert usj_stage.label == "USJ point 100101 stage 700101"
    assert usj_stage.source == USJ_STAGE_SOURCE
    assert [spawn.enemy_id for spawn in usj_stage.encounter_spawns] == [
        2202,
        2472,
        3007,
    ]
    assert stage_candidate_by_id(723706).label == "USJ point 100304 stage 723706"

    herochip_stage = stage_candidate_by_id(370101)
    assert herochip_stage.key == "herochip_stage_370101"
    assert herochip_stage.label == "英雄的志愿"
    assert herochip_stage.source == HEROCHIP_STAGE_SOURCE
    assert herochip_stage.character_refs == ()
    assert [spawn.enemy_id for spawn in herochip_stage.encounter_spawns] == [
        2005,
        2202,
    ]
    assert stage_candidate_by_id(370107).label == "精神的支柱"

    roguelike_stage = stage_candidate_by_id(400101)
    assert roguelike_stage.key == "roguelike_stage_400101"
    assert roguelike_stage.label == "Roguelike random stage 400101"
    assert roguelike_stage.source == ROGUELIKE_STAGE_SOURCE
    assert [spawn.enemy_id for spawn in roguelike_stage.encounter_spawns] == [
        2202,
        2005,
        2202,
    ]
    assert stage_candidate_by_id(400119).label == "Roguelike endless stage 400119"
    assert stage_candidate_by_id(400115).key == "stage_cfg_route_400115"

    starter = stage_candidate_by_id(STARTER_INTRO_STAGE_ID)
    assert starter.key == "starter_intro_299301"
    assert starter.stage_uid == STARTER_INTRO_STAGE_UID
    assert "zx_battle01" in starter.scripts
    assert "zx_battle07" in starter.scripts
    assert "zx_lvb_004" in starter.scripts
    assert "PLOT_zx_battle07_05" in starter.audio_events
    assert "zx_lvb006" in starter.actor_sets
    assert "video/zx/chapter2/lvb04.flv" in starter.video_assets
    assert {spawn.enemy_id for spawn in starter.enemy_spawns} == {2005, 3002}
    assert starter.combat_enemy_ids == (3002, 2005)
    assert 3003016 in starter.enemy_group_ids

    all_might_stage = stage_candidate_by_key("all_might_stage_502601")
    assert all_might_stage.stage_id == 502601
    assert all_might_stage.resolved_stage_uid == 5026010001
    assert all_might_stage.encounter_target_count == 1
    assert all_might_stage.scripts == (
        "stage502601",
        "stage502601a",
        "stage502601b",
        "stage502601c",
    )
    assert any("allmight" in event.lower() for event in all_might_stage.audio_events)

    generated_stage = stage_candidate_by_key("stage_404103")
    assert generated_stage.enemy_spawns == ()
    assert [spawn.enemy_id for spawn in generated_stage.encounter_spawns] == [
        2202,
        2005,
        2202,
    ]
    assert [spawn.ai_profile_key for spawn in generated_stage.encounter_spawns] == [
        "melee_chaser",
        "training_enemy",
        "melee_chaser",
    ]

    parsed_branch_stage = stage_candidate_by_key("stage_561203")
    assert [spawn.enemy_id for spawn in parsed_branch_stage.encounter_spawns] == [
        56120302,
        56120303,
    ]
    assert [spawn.ai_profile_key for spawn in parsed_branch_stage.encounter_spawns] == [
        "melee_chaser",
        "elite_chaser",
    ]

    ruxue = stage_candidate_by_key("ruxue_intro_drama_scripts")
    assert ruxue.stage_id is None
    assert "zx_ruxue03_2" in ruxue.scripts
    assert "PLOT_zx_ruxue02_05" in ruxue.audio_events
    assert "PLOT_copyright_zx_ruxue03_2_1_06" in ruxue.audio_events
    assert "PLOT_zx_ruxue03_2_09" in ruxue.audio_events
    assert "zx_exam_001" in ruxue.actor_sets
    assert "zx_ruxue03_2_1_06" in ruxue.actor_sets
    assert "video/zx/chapter2/ruxue_1.flv" in ruxue.video_assets
    assert "zx_usj_007" in stage_candidate_by_key("usj_drama_scripts").scripts
    beach = stage_candidate_by_key("beach_event_scripts")
    assert "zx_beach_carry_suc5" in beach.scripts
    assert "video/zx/chapter2/beach_01.flv" in beach.video_assets
    assert "zx_shangyejie_qte" in stage_candidate_by_key(
        "commercial_street_scripts"
    ).scripts
    assert "zx_shangyejie1" in stage_candidate_by_key(
        "commercial_street_scripts"
    ).scripts
    assert "zx_shangyejie_10" in stage_candidate_by_key(
        "commercial_street_scripts"
    ).actor_sets
    chapter1 = stage_candidate_by_key("stage_cfg_chapter1_zx_evidence")
    assert chapter1.stage_id is None
    assert "zx_2_7" in chapter1.scripts
    assert "video/zx/chapter1/judahua.flv" in chapter1.video_assets
    assert "video/zx/chapter1/yuniguai_1.flv" in chapter1.video_assets
    training_yard = stage_candidate_by_key("training_yard_scripts")
    assert "zx_tyj_dilei02" in training_yard.scripts
    assert "zx_touqiu" in training_yard.scripts
    assert "video/zx/chapter2/touqiu.flv" in training_yard.video_assets

    relax_stage = stage_candidate_by_id(400301)
    assert relax_stage.key == "relax_stage_400301"
    assert relax_stage.label == "01 Trial of the Strongest Easy"
    assert relax_stage.scripts == ("400301_1", "400301_2", "400301_3")
    assert relax_stage.source == RELAX_STAGE_SOURCE
    assert stage_candidate_by_id(400318).label == "06 End of the Light Hard"
    assert stage_candidate_by_key("asset_drama_stage_520001").scripts == ("520001",)
    assert stage_candidate_by_id(901008).scripts == ("901008",)
    assert [spawn.ai_profile_key for spawn in relax_stage.encounter_spawns] == [
        "melee_chaser",
        "training_enemy",
        "melee_chaser",
    ]

    secret_area_stage = stage_candidate_by_id(100101)
    assert secret_area_stage.key == "secret_area_stage_100101"
    assert secret_area_stage.label == "Town Nightraid 1001 Floor 1"
    assert secret_area_stage.source == SECRET_AREA_STAGE_SOURCE
    assert stage_candidate_by_id(101608).key == "secret_area_stage_101608"
    assert stage_candidate_by_id(101101).key == "zx_stage_101101"
    assert stage_candidate_by_id(101201).key == "asset_drama_stage_101201"

    allsvr_stage = stage_candidate_by_id(880101)
    assert allsvr_stage.key == "allsvr_stage_880101"
    assert allsvr_stage.label == "Entrance 1 Difficulty 1"
    assert allsvr_stage.source == ALLSVR_STAGE_SOURCE
    assert stage_candidate_by_id(8832034).label == "Neon City - 3 Difficulty 4"
    allsvr_boss_stage = stage_candidate_by_id(880312)
    assert allsvr_boss_stage.key == "allsvr_boss_stage_880312"
    assert allsvr_boss_stage.label == "Sidero Nightmare"

    empty_shop_stage = stage_candidate_by_id(9001001)
    assert empty_shop_stage.key == "empty_shop_stage_9001001"
    assert empty_shop_stage.label == "起跑开始，击败敌人完成热身运动吧！"
    assert empty_shop_stage.source == EMPTY_SHOP_STAGE_SOURCE
    assert stage_candidate_by_id(9006003).key == "empty_shop_stage_9006003"
    assert EMPTY_SHOP_STAGE_BY_ID[9005001].fighting == (
        17320,
        21640,
        25960,
        31160,
        37400,
    )

    stage_cfg_route = stage_candidate_by_id(563903)
    assert stage_cfg_route.key == "stage_cfg_route_563903"
    assert stage_cfg_route.label == "新城区9塔1级-独立支线2-战斗"
    assert stage_cfg_route.scripts == ("901008",)
    assert stage_cfg_route.enemy_group_ids == (
        56390301,
        56390302,
        56390303,
        56390304,
        56390305,
        56390306,
    )
    assert stage_cfg_route.combat_enemy_ids == (56390301, 56390302, 56390303)
    assert stage_cfg_route.source == "parsed from packed stage_cfg constant routes, 2026-06-23"
    assert STAGE_CFG_ROUTE_LABELS[160001] == "All Might's guidance"
    assert STAGE_CFG_ROUTE_LABELS[300401] == "聚集的敌人"
    assert stage_candidate_by_id(300401).label == "聚集的敌人"
    assert stage_candidate_by_id(571101).label == "本英町"
    assert stage_candidate_by_id(571101).scripts == ("101201_1",)
    assert stage_candidate_by_id(571101).enemy_group_ids == (
        57110101,
        57110102,
        57110104,
    )
    assert stage_candidate_by_id(300301).scripts == ("zx_touqiu",)
    assert stage_candidate_by_id(300401).scripts == ("zx_usj_002",)
    assert stage_candidate_by_id(300401).enemy_group_ids == (
        30040101,
        30040102,
        30040103,
        30040104,
        30040105,
        30040106,
        30040107,
        30040108,
        30040109,
    )
    assert stage_candidate_by_id(300401).combat_enemy_ids == (
        30040101,
        30040102,
        30040103,
        30040104,
        30040105,
        30040106,
        30040107,
        30040108,
        30040109,
    )
    assert tuple(spawn.enemy_id for spawn in stage_candidate_by_id(300401).encounter_spawns) == (
        30040101,
        30040102,
        30040103,
        30040104,
        30040105,
        30040106,
        30040107,
        30040108,
        30040109,
    )
    stage_300401_spawns = stage_candidate_by_id(300401).encounter_spawns
    assert stage_300401_spawns[0].label == "stage_cfg_authored_300401_enemy_30040101"
    assert (stage_300401_spawns[0].x, stage_300401_spawns[0].y) == (13493, 19529)
    assert (stage_300401_spawns[-1].x, stage_300401_spawns[-1].y) == (
        13472,
        17177,
    )
    assert stage_300401_spawns[-1].face == 180
    assert [spawn.ai_profile_key for spawn in stage_300401_spawns] == [
        "melee_chaser",
        "melee_chaser",
        "melee_chaser",
        "elite_chaser",
        "melee_chaser",
        "melee_chaser",
        "melee_chaser",
        "boss_brute",
        "elite_chaser",
    ]
    assert stage_candidate_by_id(310403).scripts == ("zx_usj_03002",)
    assert stage_candidate_by_id(310403).enemy_group_ids == (31040301,)
    assert stage_candidate_by_id(310403).encounter_spawns[0].ai_profile_key == (
        "nomu_brute"
    )
    assert STAGE_CFG_SCRIPT_ROUTE_GROUPS[160001] == (
        "stage160001_lose",
        "stage160001_start",
        "stage160001_win",
    )
    assert STAGE_CFG_ENCOUNTER_GROUPS[160001] == (16000101,)
    assert stage_candidate_by_id(160001).encounter_spawns[0].label == (
        "main_stage_training_enemy"
    )
    start_stage_spawn = STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE[160001][0]
    assert start_stage_spawn.label == "stage_cfg_authored_160001_enemy_16000101"
    assert (start_stage_spawn.x, start_stage_spawn.y, start_stage_spawn.z) == (
        5193,
        23257,
        526,
    )
    assert STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE[563903] == (
        56390301,
        56390302,
        56390303,
    )
    raw_only_training = stage_candidate_by_id(300502)
    assert raw_only_training.enemy_group_ids == (
        30050201,
        30050202,
        30050204,
        30050205,
    )
    assert raw_only_training.combat_enemy_ids == ()
    assert tuple(spawn.enemy_id for spawn in raw_only_training.encounter_spawns) == tuple(
        spawn.enemy_id for spawn in generated_stage_spawns(300502)
    )
    assert stage_candidate_by_id(160001).enemy_group_ids == (16000101,)
    assert tuple(spawn.enemy_id for spawn in stage_candidate_by_id(563903).encounter_spawns) == (
        56390301,
        56390302,
        56390303,
    )
    assert stage_candidate_by_id(563903).encounter_spawns[0].label == (
        "stage_cfg_authored_563903_enemy_56390301"
    )
    assert (
        stage_candidate_by_id(563903).encounter_spawns[0].x,
        stage_candidate_by_id(563903).encounter_spawns[0].y,
        stage_candidate_by_id(563903).encounter_spawns[0].z,
    ) == (7821, 21904, 944)
    assert [
        spawn.ai_profile_key for spawn in stage_candidate_by_id(563903).encounter_spawns
    ] == ["melee_chaser", "ranged_pressure", "elite_chaser"]
    assert tuple(spawn.enemy_id for spawn in stage_candidate_by_id(562610).encounter_spawns) == (
        56261001,
        56261002,
        56261003,
        56261004,
    )
    assert stage_candidate_by_id(562610).encounter_spawns[2].face == 180
    assert tuple(spawn.enemy_id for spawn in stage_candidate_by_id(571101).encounter_spawns) == (
        57110101,
        57110102,
    )
    first_branch_spawn = stage_candidate_by_id(571101).encounter_spawns[0]
    assert first_branch_spawn.label == "stage_cfg_authored_571101_enemy_57110101"
    assert (first_branch_spawn.x, first_branch_spawn.y, first_branch_spawn.z) == (
        10144,
        2366,
        27144,
    )
    assert first_branch_spawn.face == 90
    partial_authored = stage_candidate_by_id(563701).encounter_spawns
    assert tuple(spawn.enemy_id for spawn in partial_authored) == (
        56370101,
        56370102,
        56370103,
    )
    assert partial_authored[0].label == "stage_cfg_authored_563701_enemy_56370101"
    assert partial_authored[1].label == "stage_cfg_authored_563701_enemy_56370102"
    assert partial_authored[2].label == "stage_cfg_authored_563701_enemy_56370103"
    assert [spawn.ai_profile_key for spawn in partial_authored] == [
        "elite_chaser",
        "melee_chaser",
        "elite_chaser",
    ]
    assert (partial_authored[2].x, partial_authored[2].y, partial_authored[2].z) == (
        30747,
        24369,
        982,
    )
    assert {
        spawn.enemy_id for spawn in STAGE_CFG_AUTHORED_SPAWN_HINTS_BY_STAGE[406305]
    } == {40630501, 40630503, 40630506}
    assert tuple(
        spawn.enemy_id for spawn in stage_candidate_by_id(405252).encounter_spawns
    ) == (
        40525201,
        40525202,
        40525203,
        40525204,
        40525251,
        40525272,
    )
    assert stage_candidate_by_id(405252).encounter_spawns[0].face == 90
    assert stage_candidate_by_id(405252).encounter_spawns[4].face == 270
    assert tuple(
        spawn.enemy_id for spawn in stage_candidate_by_id(406205).encounter_spawns
    ) == (
        40620502,
        40620503,
        40620504,
    )
    assert stage_candidate_by_id(406205).encounter_spawns[1].face == 160
    assert (
        stage_candidate_by_id(201006).encounter_spawns[0].enemy_id,
        stage_candidate_by_id(201006).encounter_spawns[0].face,
    ) == (20100603, 300)
    assert (
        stage_candidate_by_id(310403).encounter_spawns[0].label
        == "stage_cfg_authored_310403_enemy_31040301"
    )
    assert (
        stage_candidate_by_id(310403).encounter_spawns[0].x,
        stage_candidate_by_id(310403).encounter_spawns[0].y,
    ) == (13952, 19206)
    assert (
        stage_candidate_by_id(400118).encounter_spawns[0].enemy_id,
        stage_candidate_by_id(400118).encounter_spawns[0].face,
    ) == (40011801, 90)
    assert (
        stage_candidate_by_id(406506).encounter_spawns[0].label
        == "stage_cfg_authored_406506_enemy_40650603"
    )
    assert (
        stage_candidate_by_id(406506).encounter_spawns[0].x,
        stage_candidate_by_id(406506).encounter_spawns[0].y,
        stage_candidate_by_id(406506).encounter_spawns[0].face,
    ) == (10636, 4708, 180)
    assert tuple(
        spawn.enemy_id for spawn in stage_candidate_by_id(561113).encounter_spawns
    ) == (56111303, 56111304)
    assert stage_candidate_by_id(561113).encounter_spawns[0].face == 180
    assert tuple(
        spawn.enemy_id for spawn in stage_candidate_by_id(561211).encounter_spawns
    ) == (
        56121101,
        56121102,
        56121103,
    )
    assert {
        (spawn.x, spawn.y, spawn.z)
        for spawn in stage_candidate_by_id(561211).encounter_spawns
    } == {(15186, 14578, 2034)}
    route_only_signal_stage = stage_candidate_by_id(561115)
    assert route_only_signal_stage.scripts == ("zx_501101_1",)
    assert route_only_signal_stage.label == "training signal tower 5 branch battle 1"
    assert tuple(
        spawn.enemy_id for spawn in route_only_signal_stage.encounter_spawns
    ) == (56111503, 56111505)
    assert [
        spawn.ai_profile_key for spawn in route_only_signal_stage.encounter_spawns
    ] == ["mechanical_patrol", "mechanical_patrol"]
    assert route_only_signal_stage.encounter_spawns[0].label == (
        "stage_cfg_561115_enemy_56111503"
    )
    assert route_only_signal_stage.encounter_spawns[0].placement_source == (
        "stage_cfg_generated"
    )
    assert route_only_signal_stage.encounter_spawns[0].is_authored_placement is False
    assert route_only_signal_stage.encounter_spawns[1].label == (
        "stage_cfg_authored_561115_enemy_56111505"
    )
    assert route_only_signal_stage.encounter_spawns[1].placement_source == (
        "stage_cfg_authored"
    )
    assert route_only_signal_stage.encounter_spawns[1].is_authored_placement is True
    assert (
        route_only_signal_stage.encounter_spawns[1].x,
        route_only_signal_stage.encounter_spawns[1].y,
    ) == (31319, 25275)

    assert all(
        stage.encounter_target_count > 0
        for stage in RECOVERED_BATTLE_STAGES
        if stage.can_enter_by_stage_id
    )


def test_stage_cfg_string_hint_parser_tracks_recovered_videos_and_hooks() -> None:
    module = _load_stage_cfg_hint_script()
    hints = module.collect_stage_cfg_string_hints(
        tuple(ROOT / path for path in module.DEFAULT_STAGE_CFG_ASSETS)
    )

    assert hints["stage_script_count"] == 12
    assert hints["zx_script_count"] == 51
    assert hints["video_asset_count"] == 6
    assert "zx_touqiu" in hints["zx_scripts"]
    assert "stage502601c" in hints["stage_scripts"]
    assert "video/zx/chapter2/ruxue_1.flv" in hints["video_assets"]
    assert "video/zx/chapter2/beach_01.flv" in hints["video_assets"]
    assert "video/zx/chapter2/touqiu.flv" in hints["video_assets"]
    assert "video/zx/chapter1/judahua.flv" in hints["video_assets"]
    assert "MonsterDeath" in hints["event_hooks"]
    assert "DramaEndFinishEvent" in hints["event_hooks"]


def test_asset_drama_stage_hint_parser_tracks_numeric_stage_groups() -> None:
    module = _load_asset_drama_stage_hint_script()
    hints = module.collect_drama_stage_hints(ROOT / module.DEFAULT_ASSET_ROOT)

    assert hints["script_count"] == 1260
    assert hints["numeric_stage_count"] == 111
    assert ASSET_NUMERIC_DRAMA_STAGE_SCRIPT_GROUPS[400301] == (
        "400301_1",
        "400301_2",
        "400301_3",
    )
    assert hints["numeric_stage_groups"]["400301"] == [
        "400301_1",
        "400301_2",
        "400301_3",
    ]
    assert hints["numeric_stage_groups"]["520001"] == ["520001"]
    assert hints["numeric_stage_groups"]["901008"] == ["901008"]


def test_stage_cfg_route_hint_parser_tracks_script_to_stage_routes() -> None:
    module = _load_stage_cfg_route_hint_script()
    hints = module.collect_stage_cfg_route_hints(
        ROOT / module.DEFAULT_STAGE_CFG_ASSET,
        ROOT / module.DEFAULT_ASSET_ROOT,
    )

    assert hints["constant_count"] == 10440
    assert hints["script_route_count"] == 217
    assert hints["routes"]["stage160001_start"] == {
        "route_stage_id": 160001,
        "confidence": "embedded",
        "constant_index": 1542,
        "route_label": "All Might's guidance",
    }
    assert hints["routes"]["901008"]["route_stage_id"] == 563903
    assert hints["routes"]["901008"]["confidence"] == "prefix-neighborhood"
    assert hints["routes"]["901008"]["route_label"] == "新城区9塔1级-独立支线2-战斗"
    assert hints["routes"]["101201_1"]["route_stage_id"] == 571101
    assert hints["routes"]["101201_1"]["route_label"] == "本英町"
    assert hints["routes"]["zx_touqiu"]["route_stage_id"] == 300301
    assert hints["routes"]["zx_touqiu"]["route_label"] == "Quirk Mastery Test"
    assert hints["routes"]["zx_501101_1"] == {
        "route_stage_id": 561115,
        "confidence": "prefix-neighborhood",
        "constant_index": 7472,
        "route_label": "yhc-训练场信号塔5支线战斗1",
    }


def test_area_event_stage_hint_parser_tracks_progression_rows() -> None:
    module = _load_area_event_stage_hint_script()
    hints = module.collect_area_event_stage_hints(
        ROOT / module.DEFAULT_AREA_EVENT_ASSET
    )

    assert hints["constant_count"] == 2577
    assert hints["stage_count"] == 75
    assert AREA_EVENT_STAGE_SOURCE == hints["source"]
    assert len(AREA_EVENT_STAGES) == hints["stage_count"]
    assert AREA_EVENT_STAGES[0].stage_id == 21111
    assert AREA_EVENT_STAGES[0].name == "1-1首次出击"
    assert AREA_EVENT_STAGES[0].area_name == "旧城区"
    assert AREA_EVENT_STAGES[0].open_drama == "area1_1"
    assert AREA_EVENT_STAGES[0].next_stage_id == 21121
    assert AREA_EVENT_STAGE_BY_ID[21121].previous_stage_id == 21111
    assert AREA_EVENT_STAGE_BY_ID[21761].name == "7-6车站治安"
    assert AREA_EVENT_STAGE_BY_ID[21761].reward_tips_item_id == 1013204
    assert AREA_EVENT_STAGES[-1].stage_id == 211461
    assert AREA_EVENT_STAGES[-1].next_stage_id == 0

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[21111]["name"] == AREA_EVENT_STAGE_BY_ID[21111].name
    assert generated_rows[211461]["description"] == (
        AREA_EVENT_STAGE_BY_ID[211461].description
    )


def test_act_daily_stage_hint_parser_tracks_activity_stage_rows() -> None:
    module = _load_act_daily_stage_hint_script()
    hints = module.collect_act_daily_stage_hints(
        ROOT / module.DEFAULT_ACT_DAILY_STAGE_ASSET
    )

    assert hints["constant_count"] == 191
    assert hints["stage_count"] == 34
    assert hints["total_limit"] == 65
    assert ACT_DAILY_STAGE_SOURCE == hints["source"]
    assert ACT_DAILY_TOTAL_LIMIT == hints["total_limit"]
    assert len(ACT_DAILY_STAGES) == hints["stage_count"]
    assert ACT_DAILY_STAGES[0].stage_id == 860001
    assert ACT_DAILY_STAGES[0].section == "daily_stage"
    assert ACT_DAILY_STAGE_BY_ID[880004].name == "爆豪胜己"
    assert ACT_DAILY_STAGE_BY_ID[880004].member_ids == (1046,)
    assert ACT_DAILY_STAGE_BY_ID[890001].member_shape_ids == (37002,)
    assert ACT_DAILY_STAGES[-1].stage_id == 882008
    assert ACT_DAILY_STAGES[-1].sub_id == 0
    assert ACT_DAILY_MONSTER_IDS[:6] == (2005, 2051, 3003, 2206, 2044, 3007)

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[880004]["name"] == ACT_DAILY_STAGE_BY_ID[880004].name
    assert generated_rows[882008]["sub_id"] == 0
    assert hints["monsters"][0]["monster_id"] == 2005


def test_usj_stage_hint_parser_tracks_point_stage_matrix() -> None:
    module = _load_usj_stage_hint_script()
    hints = module.collect_usj_stage_hints(ROOT / module.DEFAULT_USJ_STAGE_ASSET)

    assert hints["constant_count"] == 1952
    assert hints["point_count"] == 12
    assert hints["stage_count"] == 323
    assert USJ_STAGE_SOURCE == hints["source"]
    assert len(USJ_POINTS) == hints["point_count"]
    assert len(USJ_STAGES) == hints["stage_count"]
    assert USJ_POINTS[0].point_id == 100101
    assert USJ_POINTS[0].stage_ids[:3] == (700101, 700201, 700202)
    assert len(USJ_POINT_BY_ID[100101].stage_ids) == 27
    assert len(USJ_POINT_BY_ID[100303].stage_ids) == 26
    assert USJ_STAGE_BY_ID[700101].point_id == 100101
    assert USJ_STAGE_BY_ID[723706].point_id == 100304
    assert USJ_STAGES[-1].stage_id == 723706

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[700101]["point_id"] == 100101
    assert generated_rows[723706]["stage_order"] == 27


def test_herochip_stage_hint_parser_tracks_trial_rows() -> None:
    module = _load_herochip_stage_hint_script()
    hints = module.collect_herochip_stage_hints(
        ROOT / module.DEFAULT_HEROCHIP_STAGE_ASSET
    )

    assert hints["constant_count"] == 186
    assert hints["stage_count"] == 7
    assert HEROCHIP_STAGE_SOURCE == hints["source"]
    assert len(HEROCHIP_STAGES) == hints["stage_count"]
    assert HEROCHIP_STAGES[0].stage_id == 370101
    assert HEROCHIP_STAGES[0].title == "英雄的志愿"
    assert HEROCHIP_STAGES[0].hero_class_id == 124
    assert HEROCHIP_STAGES[0].reward_item_id == 1012124
    assert HEROCHIP_STAGES[0].unlock_stage_id == 280103
    assert HEROCHIP_STAGE_BY_ID[370102].hero_class_id == 110
    assert HEROCHIP_STAGE_BY_ID[370107].title == "精神的支柱"

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[370101]["title"] == HEROCHIP_STAGE_BY_ID[370101].title
    assert generated_rows[370107]["unlock_stage_id"] == 280706


def test_roguelike_stage_hint_parser_tracks_random_and_endless_rows() -> None:
    module = _load_roguelike_stage_hint_script()
    hints = module.collect_roguelike_stage_hints(
        ROOT / module.DEFAULT_ROGUELIKE_STAGE_ASSET
    )

    assert hints["constant_count"] == 1315
    assert hints["stage_count"] == 24
    assert ROGUELIKE_STAGE_SOURCE == hints["source"]
    assert len(ROGUELIKE_STAGES) == hints["stage_count"]
    assert ROGUELIKE_STAGES[0].stage_id == 400101
    assert ROGUELIKE_STAGES[0].mode == "random"
    assert ROGUELIKE_STAGE_BY_ID[400119].mode == "endless"
    assert ROGUELIKE_STAGES[-1].stage_id == 400119

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[400101]["constant_index"] == 1114
    assert generated_rows[400119]["mode"] == "endless"
    assert generated_rows[400119]["constant_index"] == 1227


def test_relax_stage_hint_parser_tracks_joint_operations_rows() -> None:
    module = _load_relax_stage_hint_script()
    hints = module.collect_relax_stage_hints(ROOT / module.DEFAULT_RELAX_STAGE_ASSET)

    assert hints["constant_count"] == 396
    assert hints["stage_count"] == 18
    assert RELAX_STAGE_SOURCE == f"{hints['source']}, parsed 2026-06-24"
    assert len(RELAX_STAGES) == hints["stage_count"]
    assert RELAX_STAGES[0].stage_id == 400301
    assert RELAX_STAGES[0].group_name == "01 Trial of the Strongest"
    assert RELAX_STAGES[0].fighting == (2640, 2940, 3080, 3240, 3520)
    assert RELAX_STAGES[0].scripts == ("400301_1", "400301_2", "400301_3")
    assert RELAX_STAGE_BY_ID[400310].group_name == "04 Explosive Crisis"
    assert RELAX_STAGE_BY_ID[400316].open_level == 65

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[400301]["tips"].startswith(
        "Challenge from the No.1 Hero"
    )
    assert generated_rows[400301]["scripts"] == [
        "400301_1",
        "400301_2",
        "400301_3",
    ]
    assert generated_rows[400309]["tips"].endswith(
        "to cancel out Creation Stance."
    )
    assert generated_rows[400318]["difficulty_name"] == "Hard"


def test_allsvr_stage_hint_parser_tracks_activity_rows() -> None:
    module = _load_allsvr_stage_hint_script()
    hints = module.collect_allsvr_stage_hints(ROOT / module.DEFAULT_ALLSVR_STAGE_ASSET)

    assert hints["constant_count"] == 3470
    assert hints["stage_count"] == 84
    assert hints["boss_stage_count"] == 9
    assert ALLSVR_STAGE_SOURCE == f"{hints['source']}, parsed 2026-06-24"
    assert len(ALLSVR_STAGES) == hints["stage_count"]
    assert len(ALLSVR_BOSS_STAGES) == hints["boss_stage_count"]
    assert ALLSVR_STAGES[0].stage_id == 880101
    assert ALLSVR_STAGES[0].label == "Entrance 1 Difficulty 1"
    assert ALLSVR_STAGE_BY_ID[8832034].label == "Neon City - 3 Difficulty 4"
    assert ALLSVR_BOSS_STAGE_BY_ID[880110].label == "Humarise Member Safe"
    assert ALLSVR_BOSS_STAGE_BY_ID[880312].label == "Sidero Nightmare"

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[880101]["prompt"] == (
        "I'm very nervous, but I won't let everyone down!"
    )
    assert generated_rows[8812014]["label"] == "Green Forest - 1 Difficulty 4"
    assert generated_rows[8832034]["area_id"] == 32
    boss_rows = {
        stage["stage_id"]: stage
        for stage in hints["boss_stages"]
        if isinstance(stage, dict)
    }
    assert boss_rows[880211]["difficulty_name"] == "Danger"


def test_empty_shop_stage_hint_parser_tracks_challenge_rows() -> None:
    module = _load_empty_shop_stage_hint_script()
    hints = module.collect_empty_shop_stage_hints(
        ROOT / module.DEFAULT_EMPTY_SHOP_STAGE_ASSET
    )

    assert hints["constant_count"] == 110
    assert hints["stage_count"] == 18
    assert hints["start_task_id"] == EMPTY_SHOP_START_TASK_ID
    assert hints["end_task_id"] == EMPTY_SHOP_END_TASK_ID
    assert EMPTY_SHOP_STAGE_SOURCE == f"{hints['source']}, parsed 2026-06-24"
    assert len(EMPTY_SHOP_STAGES) == hints["stage_count"]
    assert EMPTY_SHOP_STAGES[0].stage_id == 9001001
    assert EMPTY_SHOP_STAGES[0].challenge_index == 1
    assert EMPTY_SHOP_STAGES[-1].stage_id == 9006003

    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[9001001]["label"] == "起跑开始，击败敌人完成热身运动吧！"
    assert generated_rows[9002001]["fighting"] == [
        6920,
        8640,
        10360,
        12440,
        14920,
    ]
    assert generated_rows[9006002]["challenge_index"] == 6
    assert generated_rows[9001003]["label"] == "Empty Shop challenge 13"


def test_secret_area_stage_hint_parser_tracks_stage_key_rows() -> None:
    module = _load_secret_area_stage_hint_script()
    hints = module.collect_secret_area_stage_hints(
        ROOT / module.DEFAULT_SECRET_AREA_ASSET
    )

    assert hints["constant_count"] == 1407
    assert hints["stage_count"] == 88
    assert SECRET_AREA_STAGE_SOURCE == f"{hints['source']}, parsed 2026-06-24"
    assert len(SECRET_AREA_STAGES) == hints["stage_count"]
    assert SECRET_AREA_STAGES[0].stage_id == 100101
    assert SECRET_AREA_STAGES[0].level_range_id == 1001
    assert SECRET_AREA_STAGES[0].floor == 1
    assert SECRET_AREA_STAGES[-1].stage_id == 101608
    assert SECRET_AREA_STAGE_BY_ID[100608].floor == 8
    assert DEFAULT_SECRET_AREA_STAGE.stage_id == 100101

    groups = {
        group["group_id"]: group["group_name"]
        for group in hints["groups"]
        if isinstance(group, dict)
    }
    assert groups[11001] == "Town Nightraid"
    assert groups[11002] == "Abandoned Chemical Plant"
    assert groups[11003] == "Forest Training"
    generated_rows = {
        stage["stage_id"]: stage
        for stage in hints["stages"]
        if isinstance(stage, dict)
    }
    assert generated_rows[100101]["label"] == "Secret Area 1001 Floor 1"
    assert generated_rows[101608]["level_range_id"] == 1016


def test_stage_cfg_encounter_hint_parser_tracks_stage_enemy_groups() -> None:
    module = _load_stage_cfg_encounter_hint_script()
    hints = module.collect_stage_cfg_encounter_hints(
        ROOT / module.DEFAULT_STAGE_CFG_ASSET,
        ROOT / module.DEFAULT_ASSET_ROOT,
    )

    assert hints["stage_count"] == 33
    assert hints["encounters"]["160001"]["enemy_group_ids"] == [16000101]
    assert hints["encounters"]["300401"]["enemy_group_ids"] == [
        30040101,
        30040102,
        30040103,
        30040104,
        30040105,
        30040106,
        30040107,
        30040108,
        30040109,
    ]
    assert hints["encounters"]["300401"]["combat_enemy_ids"] == [
        *STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE[300401],
    ]
    assert hints["encounters"]["310403"] == {
        "stage_id": 310403,
        "scripts": ["zx_usj_03002"],
        "enemy_group_ids": [31040301],
        "combat_enemy_ids": [31040301],
    }
    assert hints["encounters"]["300502"]["combat_enemy_ids"] == []
    assert hints["encounters"]["405103"]["enemy_group_ids"] == [
        40510301,
        40510304,
        40510371,
        40510372,
        40510373,
        40510374,
    ]
    assert hints["encounters"]["405103"]["combat_enemy_ids"] == [
        *STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE[405103],
    ]
    assert hints["encounters"]["563903"]["enemy_group_ids"] == [
        56390301,
        56390302,
        56390303,
        56390304,
        56390305,
        56390306,
    ]
    assert hints["encounters"]["563903"]["combat_enemy_ids"] == [
        *STAGE_CFG_COMBAT_ENEMY_IDS_BY_STAGE[563903],
    ]
    assert hints["encounters"]["571101"]["enemy_group_ids"] == [
        57110101,
        57110102,
        57110104,
    ]
    assert hints["encounters"]["561115"] == {
        "stage_id": 561115,
        "scripts": ["zx_501101_1"],
        "enemy_group_ids": [56111501, 56111502, 56111503, 56111505],
        "combat_enemy_ids": [56111503, 56111505],
    }


def test_stage_monster_evidence_parser_filters_combat_candidates() -> None:
    module = _load_stage_monster_evidence_script()
    hints = module.collect_stage_monster_evidence(
        monster_cfg_asset=ROOT / module.DEFAULT_MONSTER_CFG_ASSET,
        stage_cfg_asset=ROOT / module.DEFAULT_STAGE_CFG_ASSET,
        asset_root=ROOT / module.DEFAULT_ASSET_ROOT,
    )

    assert hints["target_count"] == 137
    assert hints["evidence_count"] == 137
    assert hints["combat_candidate_count"] == 75
    assert hints["evidence"]["30040101"]["combat_candidate"] is True
    assert hints["evidence"]["31040301"]["combat_candidate"] is True
    assert hints["evidence"]["56390301"]["combat_candidate"] is True
    assert hints["evidence"]["57110101"]["combat_candidate"] is True
    assert hints["evidence"]["56111503"]["combat_candidate"] is True
    assert hints["evidence"]["56111505"]["combat_candidate"] is True
    assert hints["evidence"]["56390304"]["combat_candidate"] is False
    assert hints["evidence"]["56390305"]["combat_candidate"] is False
    assert hints["evidence"]["56390306"]["combat_candidate"] is False
    assert hints["evidence"]["57110104"]["combat_candidate"] is False


def test_stage_spawn_hint_parser_tracks_conservative_authored_positions() -> None:
    module = _load_stage_spawn_hint_script()
    hints = module.collect_stage_spawn_hints(
        asset_root=ROOT / module.DEFAULT_ASSET_ROOT,
        stage_cfg_asset=ROOT / module.DEFAULT_STAGE_CFG_ASSET,
        monster_cfg_asset=ROOT / module.DEFAULT_MONSTER_CFG_ASSET,
    )

    assert hints["target_count"] == 75
    assert hints["stage_count"] == 27
    assert hints["spawn_count"] == 72
    assert hints["stages"]["160001"] == [
        {
            "enemy_id": 16000101,
            "x": 5193,
            "y": 23257,
            "z": 526,
            "face": 0,
            "pattern": "MonsterInfo",
            "source_asset": "2ZU/2b4f06e9edb4a36f",
        },
    ]
    assert hints["stages"]["201006"] == [
        {
            "enemy_id": 20100603,
            "x": 10290,
            "y": 28269,
            "z": 2033,
            "face": 300,
            "pattern": "MonsterInfo",
            "source_asset": "4YOU/142f4c8ef1c136ff",
        },
    ]
    assert len(hints["stages"]["300401"]) == 9
    assert hints["stages"]["300401"][0] == {
        "enemy_id": 30040101,
        "x": 13493,
        "y": 19529,
        "z": 0,
        "face": 0,
        "pattern": "compact_enemy_table",
        "source_asset": "1FO/261c9e5c9ad0eaff",
    }
    assert hints["stages"]["300401"][-1] == {
        "enemy_id": 30040109,
        "x": 13472,
        "y": 17177,
        "z": 0,
        "face": 180,
        "pattern": "compact_enemy_table",
        "source_asset": "1FO/261c9e5c9ad0eaff",
    }
    assert hints["stages"]["571101"] == [
        {
            "enemy_id": 57110101,
            "x": 10144,
            "y": 2366,
            "z": 27144,
            "face": 90,
            "pattern": "drama_monster_command",
            "source_asset": "0QIU/2692ecef6794dc44",
        },
        {
            "enemy_id": 57110102,
            "x": 10333,
            "y": 2240,
            "z": 27160,
            "face": -8,
            "pattern": "drama_monster_command",
            "source_asset": "0QIU/2692ecef6794dc44",
        },
    ]
    assert hints["stages"]["561115"] == [
        {
            "enemy_id": 56111505,
            "x": 31319,
            "y": 25275,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "3BAO/e0343be05671e895",
        },
    ]
    assert hints["stages"]["563701"] == [
        {
            "enemy_id": 56370101,
            "x": 30655,
            "y": 23585,
            "z": 0,
            "face": 180,
            "pattern": "compact_enemy_table",
            "source_asset": "4YOU/49d248130af6a140",
        },
        {
            "enemy_id": 56370102,
            "x": 30917,
            "y": 23188,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "4YOU/49d248130af6a140",
        },
        {
            "enemy_id": 56370103,
            "x": 30747,
            "y": 24369,
            "z": 982,
            "face": 0,
            "pattern": "MonsterInfo",
            "source_asset": "4YOU/49d248130af6a140",
        }
    ]
    assert hints["stages"]["562610"] == [
        {
            "enemy_id": 56261001,
            "x": 14679,
            "y": 14883,
            "z": 670,
            "face": 0,
            "pattern": "map_monster_info_times",
            "source_asset": "2ZU/57cb3401afd5056d",
        },
        {
            "enemy_id": 56261002,
            "x": 14877,
            "y": 13745,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "2ZU/57cb3401afd5056d",
        },
        {
            "enemy_id": 56261003,
            "x": 14797,
            "y": 12399,
            "z": 661,
            "face": 180,
            "pattern": "MonsterInfo",
            "source_asset": "2ZU/57cb3401afd5056d",
        },
        {
            "enemy_id": 56261004,
            "x": 14183,
            "y": 12526,
            "z": 0,
            "face": 0,
            "pattern": "map_monster_info_times",
            "source_asset": "2ZU/57cb3401afd5056d",
        },
    ]
    assert hints["stages"]["405252"] == [
        {
            "enemy_id": 40525201,
            "x": 22330,
            "y": 16891,
            "z": 164,
            "face": 90,
            "pattern": "MonsterInfo",
            "source_asset": "1FO/0ff00360167bd2b8",
        },
        {
            "enemy_id": 40525202,
            "x": 22942,
            "y": 17316,
            "z": 0,
            "face": 157,
            "pattern": "compact_enemy_table",
            "source_asset": "1FO/0ff00360167bd2b8",
        },
        {
            "enemy_id": 40525203,
            "x": 21633,
            "y": 16617,
            "z": 0,
            "face": 230,
            "pattern": "map_monster_info_times",
            "source_asset": "1FO/0ff00360167bd2b8",
        },
        {
            "enemy_id": 40525204,
            "x": 23411,
            "y": 17080,
            "z": 0,
            "face": 0,
            "pattern": "map_monster_info_times",
            "source_asset": "1FO/0ff00360167bd2b8",
        },
        {
            "enemy_id": 40525251,
            "x": 22002,
            "y": 17132,
            "z": 0,
            "face": 270,
            "pattern": "map_monster_info_times",
            "source_asset": "1FO/0ff00360167bd2b8",
        },
        {
            "enemy_id": 40525272,
            "x": 21361,
            "y": 17640,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "1FO/0ff00360167bd2b8",
        },
    ]
    assert hints["stages"]["406205"] == [
        {
            "enemy_id": 40620502,
            "x": 11350,
            "y": 3476,
            "z": 0,
            "face": 43,
            "pattern": "compact_enemy_table",
            "source_asset": "0QIU/e97e111e09e62fcf",
        },
        {
            "enemy_id": 40620503,
            "x": 11117,
            "y": 3820,
            "z": 0,
            "face": 160,
            "pattern": "map_monster_info_times",
            "source_asset": "0QIU/e97e111e09e62fcf",
        },
        {
            "enemy_id": 40620504,
            "x": 11639,
            "y": 2918,
            "z": 0,
            "face": 0,
            "pattern": "map_monster_info_times",
            "source_asset": "0QIU/e97e111e09e62fcf",
        },
    ]
    assert hints["stages"]["310403"] == [
        {
            "enemy_id": 31040301,
            "x": 13952,
            "y": 19206,
            "z": 0,
            "face": 0,
            "pattern": "MonsterInfo",
            "source_asset": "3BAO/719e9de02011b287",
        },
    ]
    assert hints["stages"]["400118"] == [
        {
            "enemy_id": 40011801,
            "x": 18484,
            "y": 10491,
            "z": 186,
            "face": 90,
            "pattern": "MonsterInfo",
            "source_asset": "2ZU/fbe646e45765e35b",
        },
    ]
    assert hints["stages"]["406506"] == [
        {
            "enemy_id": 40650603,
            "x": 10636,
            "y": 4708,
            "z": 0,
            "face": 180,
            "pattern": "MonsterInfoXY",
            "source_asset": "2ZU/206565765646b295",
        },
    ]
    assert hints["stages"]["561113"] == [
        {
            "enemy_id": 56111303,
            "x": 26375,
            "y": 23089,
            "z": 0,
            "face": 180,
            "pattern": "MonsterInfoXY",
            "source_asset": "0QIU/1132c4410f808cb9",
        },
        {
            "enemy_id": 56111304,
            "x": 26315,
            "y": 23088,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "0QIU/1132c4410f808cb9",
        },
    ]
    assert hints["stages"]["561211"] == [
        {
            "enemy_id": 56121101,
            "x": 15186,
            "y": 14578,
            "z": 2034,
            "face": 0,
            "pattern": "MonsterInfo",
            "source_asset": "4YOU/fd660f5163e8f171",
        },
        {
            "enemy_id": 56121102,
            "x": 15186,
            "y": 14578,
            "z": 2034,
            "face": 0,
            "pattern": "MonsterInfo",
            "source_asset": "4YOU/fd660f5163e8f171",
        },
        {
            "enemy_id": 56121103,
            "x": 15186,
            "y": 14578,
            "z": 2034,
            "face": 0,
            "pattern": "MonsterInfo",
            "source_asset": "4YOU/fd660f5163e8f171",
        },
    ]
    assert hints["stages"]["563903"] == [
        {
            "enemy_id": 56390301,
            "x": 7821,
            "y": 21904,
            "z": 944,
            "face": 90,
            "pattern": "map_monster_info_times",
            "source_asset": "1FO/eda2b453448dedb2",
        },
        {
            "enemy_id": 56390302,
            "x": 6220,
            "y": 21612,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "1FO/eda2b453448dedb2",
        },
        {
            "enemy_id": 56390303,
            "x": 6536,
            "y": 21355,
            "z": 0,
            "face": 0,
            "pattern": "compact_enemy_table",
            "source_asset": "1FO/eda2b453448dedb2",
        },
    ]


def test_enemy_ai_profiles_can_seed_battle_npcs_and_monster_frames() -> None:
    sludge_ai = ENEMY_AI_PROFILES["sludge_boss"]
    assert sludge_ai.bt_name == "bt_preservation_sludge_boss"
    assert sludge_ai.attack_range > ENEMY_AI_PROFILES["training_enemy"].attack_range
    assert ENEMY_AI_PROFILES["elite_chaser"].attack_range > (
        ENEMY_AI_PROFILES["melee_chaser"].attack_range
    )
    assert ENEMY_AI_PROFILES["mechanical_patrol"].bt_name == (
        "bt_preservation_mechanical_patrol"
    )
    assert generated_enemy_profile_key(3005) == "mechanical_boss"
    assert generated_enemy_profile_key(3007) == "nomu_brute"
    assert generated_enemy_profile_key(2472) == "ranged_pressure"
    assert generated_enemy_profile_key(30040108) == "boss_brute"
    assert generated_enemy_profile_key(30040109) == "elite_chaser"
    assert generated_enemy_profile_key(40525202) == "mechanical_patrol"
    assert generated_enemy_profile_key(40650205) == "ranged_pressure"
    assert generated_enemy_profile_key(40011801) == "nomu_brute"
    assert generated_enemy_profile_key(40650603) == "boss_brute"
    assert generated_enemy_profile_key(56111503) == "mechanical_patrol"
    assert generated_enemy_profile_key(56111505) == "mechanical_patrol"
    assert generated_enemy_profile_key(56121103) == "boss_brute"

    sludge_spawn = stage_candidate_by_key("starter_intro_299301").enemy_spawns[0]
    assert sludge_spawn.ai_profile is sludge_ai
    assert sludge_spawn.placement_source == "explicit"
    assert sludge_spawn.is_authored_placement is True
    assert sludge_spawn.to_scene_npc()["BTName"] == sludge_ai.bt_name
    monster_seed = sludge_spawn.to_monster_frame_seed()
    assert monster_seed["Uid"] == sludge_spawn.uid
    assert monster_seed["SkillId"] == 0
    assert monster_seed["Info"]["Id"] == 3002
    assert monster_seed["Info"]["BTParam"] == list(sludge_ai.skill_rotation)
    directive = sludge_spawn.to_ai_directive()
    assert directive["Profile"] == "sludge_boss"
    assert directive["Behavior"] == sludge_ai.behavior
    assert directive["AttackRange"] == sludge_ai.attack_range
    assert directive["CombatHp"] == sludge_spawn.combat_hp
    assert directive["PlacementSource"] == "explicit"
    assert directive["AuthoredPlacement"] == 1

    state = StageState()
    assert state.record_monster_frame_data({"monster_data": [monster_seed]}) == [
        monster_seed
    ]
    assert state.monster_frames == [monster_seed]
    state.enter_recovered_stage(stage_candidate_by_id(563903))
    assert [directive["Profile"] for directive in state.ai_directives] == [
        "melee_chaser",
        "ranged_pressure",
        "elite_chaser",
    ]
    assert state.ai_directives[1]["EnemyId"] == 56390302
    assert state.ai_directives[1]["SkillRotation"][0] == "ranged_shot"
    assert state.ai_directives[2]["AttackRange"] == ENEMY_AI_PROFILES[
        "elite_chaser"
    ].attack_range
    state.enter_recovered_stage(stage_candidate_by_id(406506))
    assert state.ai_directives[0]["EnemyId"] == 40650603
    assert state.ai_directives[0]["Profile"] == "boss_brute"
    assert state.ai_directives[0]["Home"] == {
        "X": 10636,
        "Y": 4708,
        "Z": 0,
        "Face": 180,
    }
    state.enter_recovered_stage(stage_candidate_by_id(561211))
    assert [directive["Profile"] for directive in state.ai_directives] == [
        "melee_chaser",
        "melee_chaser",
        "boss_brute",
    ]


def test_enemy_ai_profile_hint_parser_tracks_monster_name_markers() -> None:
    module = _load_enemy_ai_profile_hint_script()
    hints = module.collect_enemy_ai_profile_hints(
        monster_cfg_asset=ROOT / module.DEFAULT_MONSTER_CFG_ASSET,
        stage_cfg_asset=ROOT / module.DEFAULT_STAGE_CFG_ASSET,
        asset_root=ROOT / module.DEFAULT_ASSET_ROOT,
    )

    assert hints["source_combat_candidate_count"] == 75
    assert hints["profile_override_count"] == 35
    assert {
        int(enemy_id): item["profile"]
        for enemy_id, item in hints["profiles"].items()
    } == STAGE_CFG_AI_PROFILE_OVERRIDES_BY_ENEMY_ID
    assert hints["profiles"]["30040108"]["profile"] == "boss_brute"
    assert hints["profiles"]["40525202"]["profile"] == "mechanical_patrol"
    assert hints["profiles"]["40650205"]["profile"] == "ranged_pressure"
    assert hints["profiles"]["56111503"]["profile"] == "mechanical_patrol"
    assert hints["profiles"]["56111505"]["profile"] == "mechanical_patrol"
    assert hints["profiles"]["56390303"]["profile"] == "elite_chaser"


def test_monster_cfg_evidence_names_generated_enemies_and_parser_output() -> None:
    assert MONSTER_CFG_EVIDENCE_BY_ID[3007].preferred_name == "Nomu"
    assert "3007_60_11" in MONSTER_CFG_EVIDENCE_BY_ID[3007].animation_keys
    assert MONSTER_CFG_EVIDENCE_BY_ID[2472].preferred_name == "Twice"
    assert MONSTER_CFG_EVIDENCE_BY_ID[3005].preferred_name == "Faux Villain"
    assert MONSTER_CFG_EVIDENCE_BY_ID[3016].preferred_name == "Muscular"

    generated_nomu = generated_stage_spawns(561203)[2]
    assert generated_nomu.enemy_id == 3007
    assert generated_nomu.display_name == "Nomu"
    assert generated_nomu.to_monster_frame_seed()["Info"]["Alias"] == "Nomu"

    module = _load_monster_cfg_hint_script()
    hints = module.collect_monster_cfg_hints(ROOT / module.DEFAULT_MONSTER_CFG_ASSET)
    assert "Nomu" in hints[3007]["display_names"]
    assert "Twice" in hints[2472]["display_names"]
    assert "Faux Villain" in hints[3005]["display_names"]
    assert "Muscular" in hints[3016]["display_names"]


def test_stage_combat_summary_uses_client_report_and_damage_info() -> None:
    state = StageState()
    state.record_damage_info(
        {
            "Members": [{"UserUid": 10001, "HurtSum": 6400}],
            "MaxCombo": 21,
            "MvpUserUid": 10001,
            "Reborn": 0,
        }
    )
    state.record_report(
        {
            "Id": STARTER_INTRO_STAGE_ID,
            "Result": 1,
            "MaxCombo": 18,
            "ComboDmg": 1200,
            "AllDmg": 6100,
            "OnHitNum": 44,
            "SoloBossNum": 1,
            "MonsterNum": [{"MonsterId": 3002, "Amount": 1}],
            "ItemNum": [{"ItemId": 1001, "Amount": 2}],
            "EndReport": {
                "RoundTimeUse": 74,
                "SkillLevel": [{"SkillId": 100101, "SkillLevel": 3}],
                "RoundFighterMoveTotal": 52,
                "RoundFighterButtonClickCountATK": 12,
                "RoundFighterButtonClickCount1": 3,
                "RoundFighterDpsTotal": 6900,
                "RoundFighterComboMax": 21,
            },
        }
    )

    summary = state.combat_summary(
        fight_style=fight_style_for_character(PLAYABLE_CHARACTERS["h1001"]),
        hero_level=7,
        stage=stage_candidate_by_key("starter_intro_299301"),
    )
    assert summary.stage_id == STARTER_INTRO_STAGE_ID
    assert summary.result == 1
    assert summary.time == 74
    assert summary.max_combo == 21
    assert summary.all_damage == 6900
    assert summary.monster_kills == ((3002, 1),)
    assert summary.skill_levels == ((100101, 3),)
    assert summary.damage_members == ((10001, 6400),)
    assert summary.combat_resolution is not None
    assert summary.combat_resolution.style_name == "One For All Rookie"
    assert summary.combat_resolution.target_count == 2
    assert summary.combat_resolution.estimated_damage == 6900
    assert summary.move_results[0]["Name"] == "Shoot Style Combo"
    assert summary.move_results[0]["EstimatedHits"] == 36
    assert summary.move_results[1]["ControlScore"] == 6
    assert summary.combat_effects == {
        "HeroId": 1011,
        "StyleName": "One For All Rookie",
        "Damage": 6900,
        "ControlScore": 6,
        "ResourceDelta": 0,
        "MobilityScore": 0,
        "DefenseScore": 0,
        "PressureScore": 75,
        "DefeatedTargets": 2,
    }
    assert summary.estimated_defeats == 2
    assert [enemy["EnemyId"] for enemy in summary.enemy_result_list] == [3002, 2005]
    assert all(enemy["Defeated"] == 1 for enemy in summary.enemy_result_list)
    assert summary.enemy_result_list[0]["LastSkill"] == "Detroit Smash"
    assert summary.enemy_result_list[0]["PlacementSource"] == "explicit"
    assert summary.enemy_result_list[0]["AuthoredPlacement"] == 1
    assert summary.enemy_result_list[0]["ThreatScore"] >= 8
    assert summary.enemy_result_list[0]["ActionHint"] == "defeated"
    result = state.result()
    assert result["RewardList"] == [{"ItemId": 1001, "count": 2, "extra": []}]
    assert result["StageInfo"][0]["StarList"] == [1, 2, 3]
    assert state.completions[STARTER_INTRO_STAGE_ID].pass_count == 1


def test_stage_combat_summary_keeps_live_ai_hints_for_surviving_enemies() -> None:
    state = StageState()
    state.record_report(
        {
            "Id": 563903,
            "Result": 1,
            "AllDmg": 100,
            "EndReport": {
                "RoundTimeUse": 120,
                "RoundFighterButtonClickCountATK": 1,
            },
        }
    )

    summary = state.combat_summary(
        fight_style=fight_style_for_character(PLAYABLE_CHARACTERS["h1001"]),
        hero_level=1,
        stage=stage_candidate_by_id(563903),
    )

    assert summary.combat_resolution is not None
    assert summary.combat_resolution.target_count == 3
    assert summary.estimated_defeats == 0
    assert [enemy["EnemyId"] for enemy in summary.enemy_result_list] == [
        56390301,
        56390302,
        56390303,
    ]
    assert summary.enemy_result_list[0]["ActionHint"].startswith("close distance")
    assert summary.enemy_result_list[1]["ActionHint"] == (
        "keeps distance and fires intermittent ranged attacks; next=ranged_shot"
    )
    assert summary.enemy_result_list[2]["AIProfile"] == "elite_chaser"
    assert summary.enemy_result_list[2]["PlacementSource"] == "stage_cfg_authored"
    assert summary.enemy_result_list[2]["AuthoredPlacement"] == 1
    assert summary.enemy_result_list[2]["ThreatScore"] > (
        summary.enemy_result_list[0]["ThreatScore"]
    )


def test_stage_drop_tracks_first_clear_and_repeat_rewards() -> None:
    stage = stage_candidate_by_key("starter_intro_299301")
    state = StageState()
    state.record_report(
        {
            "Id": STARTER_INTRO_STAGE_ID,
            "Result": 1,
            "ItemNum": [],
            "EndReport": {
                "RoundTimeUse": 80,
                "RoundFighterButtonClickCountATK": 12,
                "RoundFighterButtonClickCount1": 2,
                "RoundFighterButtonClickCount4": 1,
            },
        }
    )

    fight_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1001"])
    first_drop = state.stage_drop(
        fight_style=fight_style,
        hero_level=7,
        stage=stage,
    )
    assert first_drop["StagePassDrop"] == [
        {"idx": 1, "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Count": 1}
    ]
    assert first_drop["FirstReward"] == [
        {"idx": 1, "ItemId": LOCAL_STAGE_FIRST_REWARD_ITEM_ID, "Count": 1}
    ]

    result = state.result(fight_style=fight_style, hero_level=7, stage=stage)
    assert result["StageInfo"][0]["Status"] == 1

    repeat_drop = state.stage_drop(
        fight_style=fight_style,
        hero_level=7,
        stage=stage,
    )
    assert repeat_drop["StagePassDrop"] == first_drop["StagePassDrop"]
    assert repeat_drop["FirstReward"] == []


def test_intro_only_costumes_do_not_enter_normal_rosters() -> None:
    intro_shapes = {costume.shape_id for costume in INTRO_ONLY_COSTUMES}
    assert STARTER_CHARACTER.shape_id == 1001
    assert intro_shapes.isdisjoint(
        character.shape_id for character in INITIAL_PLAYABLE_ROSTER
    )
    assert intro_shapes.isdisjoint(
        character.shape_id for character in VERIFIED_PLAYABLE_ROSTER
    )


def test_initial_map_spawn_catalog_tracks_verified_npc_rows() -> None:
    assert INITIAL_MAP_SPAWNS == ()
    assert TUTORIAL_MAP_SPAWNS == (DEATH_ARMS_DEMO_SPAWN,)
    assert map_spawns("starter") == INITIAL_MAP_SPAWNS
    assert map_spawns("tutorial") == TUTORIAL_MAP_SPAWNS
    assert map_spawns("none") == ()
    assert map_spawns("demo_cast") == DEMO_CAST_MAP_SPAWNS
    assert map_spawns("validation") == DEMO_CAST_MAP_SPAWNS
    try:
        map_spawns("expanded")
    except ValueError as exc:
        assert "unknown map spawn mode" in str(exc)
    else:  # pragma: no cover - the guardrail is the behavior under test.
        raise AssertionError("expanded must not enable validation-only map spawns")
    assert DEATH_ARMS_DEMO_SPAWN.label == "beginner_quest_death_arms_honei_objective"
    assert DEATH_ARMS_DEMO_SPAWN.character == DEATH_ARMS
    assert DEATH_ARMS_DEMO_SPAWN.uid == BEGINNER_QUEST_DEATH_ARMS_UID
    assert DEATH_ARMS_DEMO_SPAWN.x == 6421
    assert DEATH_ARMS_DEMO_SPAWN.y == 21931
    assert DEATH_ARMS_DEMO_SPAWN.face == 180
    assert not DEATH_ARMS_DEMO_SPAWN.is_authored_placement
    assert [spawn.uid for spawn in DEMO_CAST_MAP_SPAWNS] == list(range(20001, 20008))
    assert {spawn.character.npc_id for spawn in DEMO_CAST_MAP_SPAWNS} == {
        5001,
        5007,
        5008,
        5009,
        5011,
        5035,
        5041,
    }


def test_roster_modes_keep_starter_default_and_verified_opt_in() -> None:
    assert playable_roster() == INITIAL_PLAYABLE_ROSTER
    assert playable_roster("starter") == INITIAL_PLAYABLE_ROSTER
    assert playable_roster("expanded") == VERIFIED_PLAYABLE_ROSTER
    assert playable_roster("verified") == VERIFIED_PLAYABLE_ROSTER
    assert len(VERIFIED_PLAYABLE_ROSTER) == 26
    assert {character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER} == {
        *PUBLIC_PLAYABLE_MODEL_IDS,
    }
    assert {
        model_id
        for model_id, character in RECOVERED_HERO_CHARACTERS.items()
        if character.is_protocol_verified
    } - {character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER} == {
        "h1004",
        "h1018",
        "h1024",
        "h1998",
    }
    assert "h1039" not in {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }
    assert "h1927" not in PLAYABLE_CHARACTERS
    assert "h1927" not in {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }
    assert "h1927" in SUPPORT_CHARACTERS
    assert "h1018" in SUPPORT_CHARACTERS


def test_fight_style_catalog_covers_verified_playable_roster() -> None:
    assert "skill-description" in COMBAT_CATALOG_SOURCE
    assert {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }.issubset(FIGHT_STYLES_BY_MODEL)
    assert "h1018" in FIGHT_STYLES_BY_MODEL
    assert NON_PLAYABLE_FIGHT_STYLE_MODEL_IDS == frozenset({"h1018"})
    assert {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }.issubset(HERO_CFG_COMBAT_METADATA_BY_MODEL)
    assert {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }.issubset(HERO_CFG_AI_NAMES_BY_MODEL)
    assert {
        character.model_asset_id
        for character in VERIFIED_PLAYABLE_ROSTER
        if character.model_asset_id not in {"h1020"}
    }.issubset(HERO_SKILL_VIDEO_EVIDENCE_BY_MODEL)
    assert {
        character.model_asset_id
        for character in VERIFIED_PLAYABLE_ROSTER
        if character.model_asset_id not in HERO_SKILL_VIDEO_EVIDENCE_BY_MODEL
    } == {"h1020"}
    assert len(RECOVERED_HERO_ACTION_HINTS_BY_MODEL) == 25
    assert sum(len(actions) for actions in RECOVERED_HERO_ACTION_HINTS_BY_MODEL.values()) == 665
    assert len(RECOVERED_INTERNAL_ACTION_HINTS_BY_MODEL["h1020"]) == 24
    action_gaps_by_model = {
        character.model_asset_id: fight_style_for_character(
            character
        ).missing_action_hint_commands()
        for character in VERIFIED_PLAYABLE_ROSTER
    }
    assert all(
        not {"ATK", "Q", "W", "E", "R"}.intersection(missing_commands)
        for missing_commands in action_gaps_by_model.values()
    )
    assert {
        model_id: gaps
        for model_id, gaps in action_gaps_by_model.items()
        if gaps
    } == {
        "h1014": ("PASSIVE",),
        "h1015": ("PASSIVE",),
        "h1017": ("PASSIVE",),
        "h1019": ("PASSIVE",),
        "h1026": ("PASSIVE",),
        "h1027": ("DODGE", "PASSIVE"),
        "h1028": ("PASSIVE",),
        "h1029": ("DODGE", "PASSIVE"),
        "h1030": ("DODGE", "PASSIVE"),
        "h1031": ("DODGE", "PASSIVE"),
        "h1032": ("DODGE", "PASSIVE"),
    }
    recovered_evidence_gaps = {}
    for character in VERIFIED_PLAYABLE_ROSTER:
        style = fight_style_for_character(character)
        missing = style.missing_recovered_evidence_commands()
        if missing:
            recovered_evidence_gaps[character.model_asset_id] = missing
    assert recovered_evidence_gaps == {}
    whm_deku_evidence = fight_style_for_character(
        PLAYABLE_CHARACTERS["h1027"]
    ).evidence_sources_by_command()
    assert whm_deku_evidence["DODGE"] == ("skill_video", "skill_info")
    assert whm_deku_evidence["PASSIVE"] == ("skill_video", "skill_info")
    asui_evidence = fight_style_for_character(
        PLAYABLE_CHARACTERS["h1014"]
    ).evidence_sources_by_command()
    assert asui_evidence["PASSIVE"] == ("skill_video",)

    deku_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1001"])
    assert deku_style.style_name == "One For All Rookie"
    assert deku_style.hero_cfg is not None
    assert deku_style.hero_cfg.config_row == 101
    assert deku_style.hero_cfg.skill_group_id == 10007
    assert deku_style.hero_cfg_skill_ids() == (1001, 1002)
    assert deku_style.hero_cfg.q_shape_id == 11001
    assert deku_style.recovered_ai_name() == "bot_lvgu"
    assert deku_style.recovered_skill_video_evidence() is not None
    assert deku_style.recovered_skill_video_evidence().prefix == "lvgu"
    assert deku_style.recovered_skill_video_evidence().count == 10
    assert "QTE" in deku_style.recovered_skill_video_evidence().categories
    assert deku_style.recovered_skill_video_evidence().videos_for_command("Q") == (
        "video/skill/lvgu_Q_1.flv",
    )
    assert deku_style.recovered_skill_video_evidence().videos_for_command(
        "PASSIVE"
    ) == ("video/skill/lvgu_abi_1.flv",)
    assert deku_style.recovered_skill_info_evidence() is not None
    assert "Detroit Smash" in (
        deku_style.recovered_skill_info_evidence().terms_for_command("Q")
    )
    assert "One For All" in (
        deku_style.recovered_skill_info_evidence().terms_for_command("R")
    )
    assert deku_style.move_names()[:3] == (
        "Shoot Style Combo",
        "Detroit Smash",
        "Delaware Smash",
    )
    assert deku_style.skill_levels(7)[0] == {"SkillId": 1, "SkillLevel": 7}
    assert deku_style.protocol_skill_levels(7)[:3] == [
        {"SkillId": 1001, "SkillLevel": 7},
        {"SkillId": 1002, "SkillLevel": 7},
        {"SkillId": 1, "SkillLevel": 7},
    ]
    assert {
        "BATTLE/HERO/lvgu/VO/One_For_All",
        "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01",
        "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01S",
        "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk03",
    }.issubset(deku_style.action_hints())

    momo_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1009"])
    assert momo_style.action_hints_for_command("Q") == (
        "BATTLE/HERO/babaiwan/skills/Wskill_create",
    )
    assert "BATTLE/HERO/babaiwan/skills/wskill_shoot" in (
        momo_style.action_hints_for_command("W")
    )

    assert deku_style.move_usage(
        (("ATK", 12), ("1", 3), ("2", 2), ("3", 1), ("4", 1))
    )[:5] == [
        {
            "Slot": 1,
            "Command": "ATK",
            "Name": "Shoot Style Combo",
            "Count": 12,
            "DamageType": "physical",
            "RangeType": "melee",
        },
        {
            "Slot": 2,
            "Command": "Q",
            "Name": "Detroit Smash",
            "Count": 3,
            "DamageType": "wind",
            "RangeType": "mid",
        },
        {
            "Slot": 3,
            "Command": "W",
            "Name": "Delaware Smash",
            "Count": 2,
            "DamageType": "wind",
            "RangeType": "ranged",
        },
        {
            "Slot": 4,
            "Command": "E",
            "Name": "Full Cowl Rush",
            "Count": 1,
            "DamageType": "physical",
            "RangeType": "melee",
        },
        {
            "Slot": 5,
            "Command": "R",
            "Name": "One For All Burst",
            "Count": 1,
            "DamageType": "wind",
            "RangeType": "area",
        },
    ]
    deku_resolution = deku_style.resolve_usage(
        (("ATK", 12), ("1", 3), ("2", 2), ("3", 1), ("4", 1)),
        hero_level=10,
        reported_damage=7200,
        target_count=2,
    )
    assert deku_resolution.estimated_damage == 7200
    assert deku_resolution.defeated_targets == 2
    assert deku_resolution.control_score == 7
    assert deku_resolution.resource_delta == -3
    assert deku_resolution.mobility_score == 2
    assert deku_resolution.pressure_score == 80
    assert deku_resolution.move_results[0].estimated_hits == 36
    assert deku_resolution.move_results[0].video_categories == (
        "ATK",
        "BREAK",
        "RUSH",
    )
    assert deku_resolution.move_results[0].skill_video_paths == (
        "video/skill/lvgu_atk_1.flv",
        "video/skill/lvgu_break_1.flv",
        "video/skill/lvgu_rush_1.flv",
    )
    assert deku_resolution.move_results[0].evidence_sources == (
        "action_hints",
        "skill_video",
    )
    assert deku_resolution.move_results[0].as_dict()["SkillVideoPaths"] == [
        "video/skill/lvgu_atk_1.flv",
        "video/skill/lvgu_break_1.flv",
        "video/skill/lvgu_rush_1.flv",
    ]
    assert deku_resolution.move_results[0].as_dict()["EvidenceSources"] == [
        "action_hints",
        "skill_video",
    ]
    assert deku_resolution.move_results[0].skill_slot_labels == (
        "BaseSkill",
        "ASkill",
        "DashAtk",
        "RushSkill",
        "Normal ATK Combo",
    )
    assert {
        "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01",
        "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01S",
        "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk03",
    }.issubset(deku_resolution.move_results[0].action_hints)
    assert deku_resolution.move_results[1].video_categories == ("Q",)
    assert deku_resolution.move_results[1].skill_video_paths == (
        "video/skill/lvgu_Q_1.flv",
    )
    assert deku_resolution.move_results[1].skill_info_terms == (
        "Smash",
        "Detroit Smash",
    )
    assert deku_resolution.move_results[1].evidence_sources == (
        "action_hints",
        "skill_video",
        "skill_info",
    )
    assert deku_resolution.move_results[1].skill_slot_labels == (
        "FirstSkill",
        "Special Skill",
    )
    assert deku_resolution.move_results[4].video_categories == ("R", "QTE")
    assert deku_resolution.move_results[4].skill_video_paths == (
        "video/skill/lvgu_R_1.flv",
        "video/skill/lvgu_qte_1.flv",
    )
    assert deku_resolution.move_results[4].skill_info_terms == ("One For All",)
    assert deku_resolution.move_results[4].skill_slot_labels == ("FinalSkill",)
    assert deku_resolution.move_results[4].resource_delta == -3
    boss_hp_resolution = deku_style.resolve_usage(
        (("ATK", 12), ("1", 3), ("2", 2), ("3", 1), ("4", 1)),
        hero_level=10,
        reported_damage=7200,
        target_count=2,
        target_hp_values=(5000, 5000),
    )
    assert boss_hp_resolution.target_count == 2
    assert boss_hp_resolution.defeated_targets == 1

    all_might_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1003"])
    assert "United States of Smash" in all_might_style.move_names()
    assert all_might_style.resource == "One For All stacks"
    assert all_might_style.recovered_skill_video_evidence() is not None
    assert all_might_style.recovered_skill_video_evidence().prefix == "ouermaite"
    assert all_might_style.recovered_skill_video_evidence().categories == (
        "ATK",
        "BREAK",
        "DASH",
        "E",
        "PRE",
        "Q",
        "QTE",
        "R",
        "RUSH",
        "W",
    )
    assert "BATTLE/HERO/allmight/skills/Rskill" in all_might_style.action_hints()
    assert "BATTLE/HERO/allmight/skills/dodge_skill" in (
        all_might_style.action_hints()
    )
    all_might_resolution = all_might_style.resolve_usage(
        (("ATK", 4), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1)),
        hero_level=20,
        reported_damage=6000,
        target_count=1,
    )
    assert all_might_style.recovered_skill_info_evidence() is not None
    assert all_might_resolution.move_results[3].skill_info_terms == ("I Am Here!",)
    assert {
        "BATTLE/HERO/allmight/skills/Qskill_01",
        "BATTLE/HERO/allmight/skills/Qskill_02",
        "BATTLE/HERO/allmight/skills/Qskill_EX_01",
        "BATTLE/HERO/allmight/skills/Qskill_EX_02",
    }.issubset(all_might_resolution.move_results[1].action_hints)
    assert {
        "BATTLE/HERO/allmight/VO/Rskill_VO_01",
        "BATTLE/HERO/allmight/VO/Rskill_VO_02",
        "BATTLE/HERO/allmight/VO/Rskill_VO_03",
        "BATTLE/HERO/allmight/skills/Rskill",
    }.issubset(all_might_resolution.move_results[4].action_hints)
    assert all_might_resolution.move_results[0].video_categories == (
        "ATK",
        "BREAK",
        "RUSH",
    )
    assert all_might_resolution.move_results[5].video_categories == ("DASH",)
    assert all_might_resolution.move_results[5].skill_video_paths == (
        "video/skill/ouermaite_dash_1.flv",
    )

    bakugo_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1002"])
    assert bakugo_style.hero_cfg is not None
    assert bakugo_style.hero_cfg.skill_group_id == 10008
    assert bakugo_style.recovered_ai_name() == "bot_baohao"
    assert bakugo_style.recovered_skill_info_evidence() is not None
    assert bakugo_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Extra Explosion",
    )
    assert bakugo_style.recovered_action_map() == (
        ("arder_biliqi", "arder_biliqi02"),
        ("arder_yaling", "arder_yaling02"),
    )
    assert "BATTLE/HERO/baohao/skills/Qskill_EX" in bakugo_style.action_hints()
    bakugo_resolution = bakugo_style.resolve_usage((("1", 1),), hero_level=1)
    assert bakugo_style.recovered_skill_video_evidence() is not None
    assert bakugo_style.recovered_skill_video_evidence().videos_for_command(
        "PASSIVE"
    ) == (
        "video/skill/baohao_abi_1.flv",
        "video/skill/baohao_pre.flv",
    )
    assert {
        "BATTLE/HERO/baohao/skills/Qskill_EX",
        "BATTLE/HERO/baohao/skills/Qskill_EX_start",
    }.issubset(bakugo_resolution.move_results[1].action_hints)

    ochaco_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1007"])
    assert ochaco_style.hero_cfg is not None
    assert ochaco_style.hero_cfg.skill_group_id == 10015
    assert ochaco_style.recovered_ai_name() == "bot_yuchazi"
    assert "BATTLE/HERO/yuchazi/skills/Wskill" in ochaco_style.action_hints()
    ochaco_resolution = ochaco_style.resolve_usage((("2", 1),), hero_level=1)
    assert "BATTLE/HERO/yuchazi/skills/Wskill" in (
        ochaco_resolution.move_results[2].action_hints
    )
    assert ochaco_style.recovered_skill_info_evidence() is not None
    assert ochaco_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Gravel Strike",
        "Meteor Storm",
    )
    assert ochaco_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "御茶子必杀技",
    )

    iida_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1006"])
    iida_resolution = iida_style.resolve_usage(
        (("ATK", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1)),
        hero_level=1,
    )
    assert "BATTLE/HERO/fantian/fantian_atk1" in (
        iida_resolution.move_results[0].action_hints
    )
    assert "BATTLE/HERO/fantian/fantian_skill1" in (
        iida_resolution.move_results[1].action_hints
    )
    assert "BATTLE/HERO/fantian/fantian_skill4" in (
        iida_resolution.move_results[4].action_hints
    )

    denki_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1010"])
    assert denki_style.recovered_skill_info_evidence() is not None
    assert denki_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "Lightning Bolt",
    )
    assert "BATTLE/HERO/shangming/skills/Rskill" in (
        denki_style.resolve_usage((("4", 1),), hero_level=1).move_results[
            4
        ].action_hints
    )

    dabi_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1012"])
    assert dabi_style.recovered_skill_info_evidence() is not None
    assert dabi_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "DabiQ",
    )
    assert dabi_style.recovered_skill_info_evidence().terms_for_command("E") == (
        "Dabi Assist Skill E",
    )
    assert dabi_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "Dabi大招（PVE)",
    )

    kirishima_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1013"])
    assert kirishima_style.recovered_skill_info_evidence() is not None
    assert "Kirishima Q change 2 tap" in (
        kirishima_style.recovered_skill_info_evidence().terms_for_command("Q")
    )

    asui_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1014"])
    assert asui_style.recovered_skill_info_evidence() is not None
    assert asui_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Tongue Swipe",
    )
    assert "BATTLE/HERO/wachui/skills/skill01" in (
        asui_style.resolve_usage((("1", 1),), hero_level=1).move_results[
            1
        ].action_hints
    )
    assert "BATTLE/HERO/wachui/skills/skillex" in (
        asui_style.resolve_usage((("4", 1),), hero_level=1).move_results[
            4
        ].action_hints
    )

    aizawa_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1015"])
    assert aizawa_style.recovered_skill_info_evidence() is not None
    assert aizawa_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "相泽Q1",
    )
    assert aizawa_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "相泽大招",
    )
    assert "BATTLE/HERO/xiangze/skills/xiangze_skillex" in (
        aizawa_style.resolve_usage((("4", 1),), hero_level=1).move_results[
            4
        ].action_hints
    )

    ojiro_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1016"])
    assert ojiro_style.recovered_skill_info_evidence() is not None
    assert ojiro_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "尾白Q",
        "尾巴强化Q",
    )
    assert ojiro_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "尾白大招",
    )

    endeavor_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1021"])
    endeavor_resolution = endeavor_style.resolve_usage(
        (("1", 1), ("4", 1), ("6", 1)), hero_level=1
    )
    assert "BATTLE/HERO/andewa/skills/Qskill_01" in (
        endeavor_resolution.move_results[1].action_hints
    )
    assert "BATTLE/HERO/andewa/skills/Rskill" in (
        endeavor_resolution.move_results[4].action_hints
    )
    assert "BATTLE/HERO/andewa/ability/ability_start" in (
        endeavor_resolution.move_results[6].action_hints
    )

    whm_bakugo_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1028"])
    assert "BATTLE/HERO/newbaohao_jcb/newbaohao_skill04" in (
        whm_bakugo_style.resolve_usage((("4", 1),), hero_level=1).move_results[
            4
        ].action_hints
    )

    whm_todoroki_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1029"])
    assert "BATTLE/HERO/newhong_jcb/1029_skill3" in (
        whm_todoroki_style.resolve_usage((("4", 1),), hero_level=1).move_results[
            4
        ].action_hints
    )

    alternate_deku_style = fight_style_for_character(
        RECOVERED_HERO_CHARACTERS["h1024"]
    )
    assert "BATTLE/HERO/lvgu/commonATK/lvgu_pve_atk01" in (
        alternate_deku_style.resolve_usage((("ATK", 1),), hero_level=1).move_results[
            0
        ].action_hints
    )

    small_might_style = fight_style_for_character(
        RECOVERED_HERO_CHARACTERS["h1004"]
    )
    assert "BATTLE/HERO/allmight/skills/Rskill" in (
        small_might_style.resolve_usage((("4", 1),), hero_level=1).move_results[
            4
        ].action_hints
    )

    art_test_all_might_style = fight_style_for_character(
        RECOVERED_HERO_CHARACTERS["h1998"]
    )
    assert "BATTLE/HERO/allmight/skills/Rskill" in (
        art_test_all_might_style.resolve_usage(
            (("4", 1),), hero_level=1
        ).move_results[4].action_hints
    )

    stain_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1110"])
    stain_resolution = stain_style.resolve_usage(
        (("1", 1), ("2", 1), ("3", 1), ("4", 1)), hero_level=1
    )
    assert "BATTLE/HERO/sitanyin/skills/Qskill" in (
        stain_resolution.move_results[1].action_hints
    )
    assert "BATTLE/HERO/sitanyin/skills/Wskill" in (
        stain_resolution.move_results[2].action_hints
    )
    assert "BATTLE/HERO/sitanyin/skills/Eskill_01" in (
        stain_resolution.move_results[3].action_hints
    )
    assert "BATTLE/HERO/sitanyin/skills/Rskill" in (
        stain_resolution.move_results[4].action_hints
    )

    mina_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1017"])
    assert mina_style.recovered_skill_info_evidence() is not None
    assert "Mina Perfect Dodge QTE" in (
        mina_style.recovered_skill_info_evidence().terms_for_command("DODGE")
    )

    shigaraki_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1019"])
    assert shigaraki_style.recovered_skill_info_evidence() is not None
    assert shigaraki_style.recovered_skill_info_evidence().terms_for_command("ATK") == (
        "Vicious Contact",
    )

    mineta_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1020"])
    assert mineta_style.recovered_skill_info_evidence() is not None
    assert mineta_style.recovered_skill_info_evidence().terms_for_command("W") == (
        "Mineta-Bounce",
        "Dimensional Bounce",
    )
    mineta_resolution = mineta_style.resolve_usage(
        (("ATK", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1), ("6", 1)),
        hero_level=1,
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_qskill_vo" in (
        mineta_resolution.move_results[1].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_rskill_vo" in (
        mineta_resolution.move_results[4].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_dash_01" in (
        mineta_resolution.move_results[5].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_atk_vo_long_a" in (
        mineta_resolution.move_results[0].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_qskill_vo" in (
        mineta_resolution.move_results[1].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_wskill_vo" in (
        mineta_resolution.move_results[2].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_eskill_vo" in (
        mineta_resolution.move_results[3].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_rskill_vo" in (
        mineta_resolution.move_results[4].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_dash_01" in (
        mineta_resolution.move_results[5].action_hints
    )
    assert "INTERNAL/HERO/putao/putao_vo/putao_gexing_vo" in (
        mineta_resolution.move_results[6].action_hints
    )

    endeavor_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1021"])
    assert endeavor_style.recovered_skill_info_evidence() is not None
    assert endeavor_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "Exploding Lance",
    )

    tokoyami_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1022"])
    assert tokoyami_style.recovered_skill_info_evidence() is not None
    assert tokoyami_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "Abyssal Talons",
    )

    deku_alt_style = fight_style_for_character(
        RECOVERED_HERO_CHARACTERS["h1024"]
    )
    assert deku_alt_style.recovered_skill_info_evidence() is not None
    assert deku_alt_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Smash!",
    )

    hawks_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1026"])
    assert hawks_style.recovered_skill_info_evidence() is not None
    assert hawks_style.recovered_skill_info_evidence().terms_for_command("E") == (
        "Hawks E",
    )
    assert hawks_style.recovered_support_skill_evidence() is not None
    assert hawks_style.recovered_support_skill_evidence().terms == ("Downfall",)

    whm_deku_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1027"])
    assert whm_deku_style.recovered_skill_info_evidence() is not None
    assert whm_deku_style.recovered_skill_info_evidence().terms_for_command("ATK") == (
        "WHM绿谷普攻1",
        "Midoriya black whip",
    )
    assert whm_deku_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Midoriya Q",
        "Midoriya Q skill down kick",
    )
    assert whm_deku_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "whm绿谷R",
    )
    assert whm_deku_style.recovered_support_skill_evidence() is not None
    assert whm_deku_style.recovered_support_skill_evidence().terms == (
        "WHM Shoot Style",
    )

    whm_bakugo_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1028"])
    assert whm_bakugo_style.recovered_skill_info_evidence() is not None
    assert whm_bakugo_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Q Ground charge",
        "Q Ground machine gun",
        "Q Air 1",
    )
    assert whm_bakugo_style.recovered_skill_info_evidence().terms_for_command("E") == (
        "E Fire tornado",
        "E Drill flame",
    )
    assert whm_bakugo_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "R Movie Ult (PVE)",
    )
    assert "W芜湖起飞" in whm_bakugo_style.structured_skill_info_terms_for_command(
        "W"
    )
    whm_bakugo_resolution = whm_bakugo_style.resolve_usage((("2", 1),), hero_level=70)
    assert "W Wuhu takeoff" in whm_bakugo_resolution.move_results[2].skill_info_variants
    assert "W芜湖起飞" in whm_bakugo_resolution.move_results[2].skill_info_variants
    assert whm_bakugo_resolution.move_results[2].as_dict()["SkillInfoVariants"]
    assert whm_bakugo_style.recovered_support_skill_evidence() is not None
    assert whm_bakugo_style.recovered_support_skill_evidence().terms == (
        "Turbo Twister",
    )

    whm_todoroki_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1029"])
    assert whm_todoroki_style.recovered_skill_info_evidence() is not None
    assert whm_todoroki_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "whm轰Q1",
        "whm轰Q2",
    )
    assert whm_todoroki_style.recovered_skill_info_evidence().terms_for_command("W") == (
        "whm轰W1",
        "冰枪1段",
    )
    assert whm_todoroki_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "whm轰R",
    )
    assert whm_todoroki_style.recovered_support_skill_evidence() is not None
    assert whm_todoroki_style.recovered_support_skill_evidence().terms == (
        "Icicle Storm",
    )

    nejire_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1030"])
    assert nejire_style.recovered_skill_info_evidence() is not None
    assert nejire_style.recovered_skill_info_evidence().terms_for_command("ATK") == (
        "测试波动普攻1",
    )
    assert nejire_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "波动Q1",
        "Wave Blast",
    )
    assert nejire_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "波动R",
    )

    mirio_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1032"])
    assert mirio_style.hero_cfg_preload_effects() == (
        2600201,
        2600202,
        2600203,
    )
    assert mirio_style.recovered_ai_name() == "bot_tongxingbaiwan"
    assert mirio_style.recovered_skill_info_evidence() is not None
    assert mirio_style.recovered_skill_info_evidence().terms_for_command("ATK") == (
        "通行百万普攻1",
    )
    assert mirio_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "通行百万Q3",
        "通行百万Q4",
    )
    assert mirio_style.recovered_skill_info_evidence().terms_for_command("W") == (
        "Mirio TogataW",
    )
    assert mirio_style.recovered_skill_info_evidence().terms_for_command("E") == (
        "Mirio TogataE",
    )
    assert mirio_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "通行百万R",
    )
    assert HERO_CFG_ACTION_MAP_BY_MODEL["h1032"] == (
        ("arder_biliqi", "arder_biliqi02"),
        ("arder_yaling", "arder_yaling02"),
    )

    stain_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1110"])
    assert stain_style.archetype == "bleed duelist"
    assert stain_style.hero_cfg is not None
    assert stain_style.hero_cfg.config_row == 111
    assert stain_style.hero_cfg.shape_id == 1011
    assert stain_style.recovered_ai_name() == "bot_sitanyin"
    assert stain_style.recovered_action_map() == (
        ("arder_biliqi", "arder_biliqi11"),
        ("arder_yaling", "arder_yaling11"),
    )
    assert stain_style.recovered_skill_video_evidence() is not None
    assert stain_style.recovered_skill_video_evidence().prefix == "sitanyin"
    assert stain_style.recovered_skill_info_evidence() is not None
    assert stain_style.recovered_skill_info_evidence().terms_for_command("W") == (
        "Dagger Throw",
    )
    assert stain_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Aura of Fear",
    )
    assert stain_style.recovered_skill_info_evidence().terms_for_command("E") == (
        "Permeate Uppercut",
    )
    assert "Bloodcurdle" in stain_style.move_names()

    todoroki_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1008"])
    assert todoroki_style.recovered_skill_info_evidence() is not None
    assert todoroki_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "Half-Cold Half-Hot",
    )

    hawks_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1026"])
    assert hawks_style.recovered_skill_info_evidence() is not None
    assert hawks_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "Hawks ult",
    )

    tamaki_style = fight_style_for_character(PLAYABLE_CHARACTERS["h1031"])
    assert tamaki_style.recovered_skill_info_evidence() is not None
    assert tamaki_style.recovered_skill_info_evidence().terms_for_command("ATK") == (
        "天喰环普攻1",
    )
    assert tamaki_style.recovered_skill_info_evidence().terms_for_command("Q") == (
        "天喰环Q1",
        "Tentacles Grasp",
    )
    assert tamaki_style.recovered_skill_info_evidence().terms_for_command("R") == (
        "天喰环R",
    )

    mirio_skill_info = mirio_style.recovered_skill_info_evidence()
    assert mirio_skill_info is not None
    assert mirio_skill_info.terms_for_command("ATK") == ("通行百万普攻1",)
    assert mirio_skill_info.terms_for_command("Q") == (
        "通行百万Q3",
        "通行百万Q4",
    )
    assert mirio_skill_info.terms_for_command("W") == ("Mirio TogataW",)
    assert mirio_skill_info.terms_for_command("E") == ("Mirio TogataE",)
    assert mirio_skill_info.terms_for_command("R") == ("通行百万R",)

    assert "通行百万W" in mirio_style.structured_skill_info_terms_for_command("W")
    assert "通行百万E" in mirio_style.structured_skill_info_terms_for_command("E")
    mirio_resolution = mirio_style.resolve_usage(
        (("2", 1), ("3", 1)),
        hero_level=70,
    )
    assert "通行百万W" in mirio_resolution.move_results[2].skill_info_variants
    assert "通行百万E" in mirio_resolution.move_results[3].skill_info_variants

    try:
        fight_style_for_character(RECOVERED_HERO_CHARACTERS["h1018"])
    except ValueError as exc:
        assert "not public playable" in str(exc)
    else:
        raise AssertionError("Jiro must stay out of gameplay fight-style lookups")

    for character in VERIFIED_PLAYABLE_ROSTER:
        style = fight_style_for_character(character)
        assert style.moves != DEFAULT_MOVES
        assert len(set(style.move_names())) == 7
        resolution = style.resolve_usage(
            (("ATK", 8), ("1", 2), ("2", 2), ("3", 2), ("4", 1), ("5", 1)),
            hero_level=20,
            reported_damage=9000,
            target_count=3,
        )
        assert resolution.hero_id == character.hero_id
        assert len(resolution.move_results) == 7
        assert resolution.estimated_damage == 9000
        assert resolution.defeated_targets >= 1
        assert resolution.pressure_score > 0
        assert any(
            result.control_score
            or result.resource_delta
            or result.mobility_score
            or result.defense_score
            for result in resolution.move_results
        )


def test_skill_info_hint_parser_tracks_recovered_move_text() -> None:
    module = _load_skill_info_hint_script()
    hints = module.collect_skill_info_hints(
        tuple(ROOT / path for path in module.DEFAULT_SKILL_INFO_ASSETS)
    )

    assert len(module.DEFAULT_SKILL_INFO_ASSETS) == 2
    assert "Detroit Smash" in HERO_SKILL_INFO_EVIDENCE_BY_MODEL["h1001"].all_terms()
    assert hints["h1001"]["terms"]["Detroit Smash"]["count"] == 2
    assert hints["h1001"]["terms"]["One For All"]["count"] == 12
    assert hints["h1003"]["terms"]["I Am Here!"]["count"] == 1
    assert hints["h1008"]["terms"]["Half-Cold Half-Hot"]["count"] == 1
    assert hints["h1008"]["terms"]["Charge Ice Spear"]["count"] == 1
    assert hints["h1006"]["terms"]["Recipro Extend"]["count"] == 1
    assert hints["h1009"]["terms"]["Meteor Storm"]["count"] == 1
    assert hints["h1010"]["terms"]["Lightning Bolt"]["count"] == 1
    assert hints["h1007"]["terms"]["Gravel Strike"]["count"] == 1
    assert hints["h1007"]["terms"]["御茶子必杀技"]["count"] == 2
    assert hints["h1012"]["terms"]["DabiQ"]["count"] == 8
    assert hints["h1012"]["terms"]["Dabi Assist Skill E"]["count"] == 1
    assert hints["h1013"]["terms"]["Kirishima Q change 2 tap"]["count"] == 1
    assert hints["h1014"]["terms"]["Tongue Swipe"]["count"] == 1
    assert hints["h1015"]["terms"]["相泽Q1"]["count"] == 2
    assert hints["h1015"]["terms"]["相泽大招"]["count"] == 2
    assert hints["h1016"]["terms"]["尾白Q"]["count"] == 6
    assert hints["h1016"]["terms"]["尾白大招"]["count"] == 2
    assert hints["h1017"]["terms"]["Mina Perfect Dodge QTE"]["count"] == 1
    assert hints["h1020"]["terms"]["Grape Rain"]["count"] == 1
    assert hints["h1019"]["terms"]["Vicious Contact"]["count"] == 1
    assert hints["h1021"]["terms"]["Exploding Lance"]["count"] == 1
    assert hints["h1022"]["terms"]["Abyssal Talons"]["count"] == 1
    assert hints["h1024"]["terms"]["Smash!"]["count"] == 1
    assert hints["h1026"]["terms"]["Hawks Q open"]["count"] == 1
    assert hints["h1026"]["terms"]["Hawks ult"]["count"] == 3
    assert hints["h1027"]["terms"]["Midoriya Q"]["count"] >= 1
    assert hints["h1027"]["terms"]["whm绿谷R"]["count"] == 2
    assert "Midoriya Q" in hints["h1027"]["structured_terms"]["Q"]
    assert "Midoriya W" in hints["h1027"]["structured_terms"]["W"]
    assert "whm绿谷R" in hints["h1027"]["structured_terms"]["R"]
    assert hints["h1028"]["terms"]["Q Ground charge"]["count"] == 1
    assert hints["h1028"]["terms"]["R Movie Ult (PVE)"]["count"] == 1
    assert "Q Ground charge" in hints["h1028"]["structured_terms"]["Q"]
    assert "W Air move" in hints["h1028"]["structured_terms"]["W"]
    assert "W芜湖起飞" in hints["h1028"]["structured_terms"]["W"]
    assert "E Drill flame" in hints["h1028"]["structured_terms"]["E"]
    assert "R Movie Ult (PVE)" in hints["h1028"]["structured_terms"]["R"]
    assert hints["h1029"]["terms"]["whm轰Q1"]["count"] == 2
    assert hints["h1029"]["terms"]["whm轰R"]["count"] == 2
    assert "whm轰R" in hints["h1029"]["structured_terms"]["R"]
    assert hints["h1030"]["terms"]["测试波动普攻1"]["count"] == 4
    assert hints["h1030"]["terms"]["Wave Blast"]["count"] == 1
    assert "波动W" in hints["h1030"]["structured_terms"]["W"]
    assert "波动E1" in hints["h1030"]["structured_terms"]["E"]
    assert "波动R" in hints["h1030"]["structured_terms"]["R"]
    assert hints["h1031"]["terms"]["天喰环R"]["count"] == 2
    assert hints["h1031"]["terms"]["Tentacles Grasp"]["count"] == 1
    assert "天喰环Q1" in hints["h1031"]["structured_terms"]["Q"]
    assert "天喰环R" in hints["h1031"]["structured_terms"]["R"]
    assert hints["h1032"]["terms"]["通行百万Q3"]["count"] >= 2
    assert hints["h1032"]["terms"]["Mirio TogataW"]["count"] == 1
    assert "Mirio TogataW" in hints["h1032"]["structured_terms"]["W"]
    assert "通行百万W" in hints["h1032"]["structured_terms"]["W"]
    assert "Mirio TogataE" in hints["h1032"]["structured_terms"]["E"]
    assert "通行百万R" in hints["h1032"]["structured_terms"]["R"]
    assert hints["h1110"]["terms"]["Dagger Throw"]["count"] == 1
    assert hints["h1110"]["terms"]["Permeate Uppercut"]["count"] == 1
    assert STRUCTURED_SKILL_INFO_TERMS_BY_MODEL["h1028"]["W"] == tuple(
        hints["h1028"]["structured_terms"]["W"]
    )
    assert STRUCTURED_SKILL_INFO_TERMS_BY_MODEL["h1032"]["E"] == tuple(
        hints["h1032"]["structured_terms"]["E"]
    )


def test_support_skill_hint_parser_tracks_hero_support_text() -> None:
    module = _load_support_skill_hint_script()
    hints = module.collect_support_skill_hints(ROOT / module.DEFAULT_HERO_SUPPORTS_ASSET)

    assert HERO_SUPPORT_SKILL_EVIDENCE_BY_MODEL["h1026"].terms == ("Downfall",)
    assert hints["h1026"]["terms"]["Downfall"]["count"] == 1
    assert hints["h1027"]["terms"]["WHM Shoot Style"]["count"] == 1
    assert hints["h1028"]["terms"]["Turbo Twister"]["count"] == 1
    assert hints["h1029"]["terms"]["Icicle Storm"]["count"] == 1
    assert hints["h1030"]["terms"]["Wave Blast"]["count"] == 1
    assert hints["h1031"]["terms"]["Tentacles Grasp"]["count"] == 1


def test_skill_slot_hint_parser_tracks_button_slot_labels() -> None:
    module = _load_skill_slot_hint_script()
    hints = module.collect_skill_slot_hints(
        ROOT / module.DEFAULT_SKILL_SLOT_ASSET,
        ROOT / module.DEFAULT_SKILL_GUIDE_ASSET,
    )

    assert hints["slot_terms"]["BaseSkill"]["count"] == 1
    assert hints["slot_terms"]["FirstSkill"]["count"] == 1
    assert hints["slot_terms"]["SecondSkill"]["count"] == 1
    assert hints["slot_terms"]["ThirdSkill"]["count"] == 1
    assert hints["slot_terms"]["FinalSkill"]["count"] == 1
    assert hints["slot_terms"]["QteBtnSkill"]["count"] == 1
    assert hints["guide_terms"]["Normal ATK Combo"]["count"] == 2
    assert hints["guide_terms"]["Special Skill"]["count"] == 14
    assert skill_slot_labels_for_command("ATK") == (
        "BaseSkill",
        "ASkill",
        "DashAtk",
        "RushSkill",
        "Normal ATK Combo",
    )
    assert skill_slot_labels_for_command("Q") == ("FirstSkill", "Special Skill")
    assert skill_slot_labels_for_command("R") == ("FinalSkill",)


def test_combat_action_hint_parser_tracks_extracted_asset_prefixes() -> None:
    module = _load_combat_action_hint_script()
    hints = module.collect_action_hints(
        (
            ROOT / "analysis" / "stage_candidates.json",
            ROOT / "analysis" / "stage_candidates",
            ROOT / "analysis" / "battle_stage_candidate_catalog.json",
            ROOT / "analysis" / "intro_qte_asset_index.txt",
            ROOT / "analysis" / "mediafire_20260620" / "apk_extract" / "assets",
        )
    )
    summary = {
        hero_key: {
            "model_asset_id": module.KNOWN_HERO_ACTION_MODELS.get(hero_key),
            "actions": sorted(actions),
        }
        for hero_key, actions in sorted(hints.items())
    }

    assert len(summary) == 28
    assert sum(1 for item in summary.values() if item["model_asset_id"]) == 27
    assert summary["andewa"]["model_asset_id"] == "h1021"
    assert "BATTLE/HERO/andewa/skills/Rskill" in summary["andewa"]["actions"]
    assert summary["newbaohao_jcb"]["model_asset_id"] == "h1028"
    assert (
        "BATTLE/HERO/newbaohao_jcb/newbaohao_skill04"
        in summary["newbaohao_jcb"]["actions"]
    )
    assert summary["sitanyin"]["model_asset_id"] == "h1110"
    assert "BATTLE/HERO/sitanyin/skills/Rskill" in summary["sitanyin"]["actions"]
    assert summary["allmight_boss"]["model_asset_id"] is None


def test_internal_combat_action_hint_parser_tracks_mineta_tokens() -> None:
    module = _load_internal_combat_action_hint_script()
    hints = module.collect_internal_action_hints(ROOT / module.DEFAULT_ASSET_ROOT)

    mineta = hints["h1020"]
    assert mineta["prefixes"] == ["putao"]
    assert len(mineta["tokens"]) == 49
    assert "putao_vo/putao_qskill_vo" in mineta["tokens"]
    assert "putao_vo/putao_wskill_vo" in mineta["tokens"]
    assert "putao_vo/putao_eskill_vo" in mineta["tokens"]
    assert "putao_vo/putao_rskill_vo" in mineta["tokens"]
    assert "putao_dash_01" in mineta["tokens"]
    assert "putao_vo_en/putao_gexing_vo" in mineta["tokens"]


def test_stage_star_scoring_uses_actual_encounter_completion() -> None:
    state = StageState()
    state.record_report(
        {
            "Id": STARTER_INTRO_STAGE_ID,
            "Result": 1,
            "AllDmg": 2000,
            "ItemNum": [],
            "EndReport": {
                "RoundTimeUse": 60,
                "RoundFighterButtonClickCountATK": 1,
                "RoundFighterButtonClickCount1": 1,
            },
        }
    )

    result = state.result(
        fight_style=fight_style_for_character(PLAYABLE_CHARACTERS["h1001"]),
        hero_level=7,
        stage=stage_candidate_by_key("starter_intro_299301"),
    )

    assert result["Result"] == 1
    assert result["StageInfo"][0]["StarList"] == [1]
    assert state.completions[STARTER_INTRO_STAGE_ID].stars == (1,)


def test_generated_stage_rewards_include_full_clear_and_style_bonus() -> None:
    state = StageState()
    state.record_report(
        {
            "Id": STARTER_INTRO_STAGE_ID,
            "Result": 1,
            "AllDmg": 9000,
            "ItemNum": [],
            "EndReport": {
                "RoundTimeUse": 70,
                "RoundFighterDpsTotal": 9000,
                "RoundFighterButtonClickCountATK": 18,
                "RoundFighterButtonClickCount1": 4,
                "RoundFighterButtonClickCount2": 4,
                "RoundFighterButtonClickCount3": 4,
                "RoundFighterButtonClickCount4": 2,
            },
        }
    )

    result = state.result(
        fight_style=fight_style_for_character(PLAYABLE_CHARACTERS["h1001"]),
        hero_level=70,
        stage=stage_candidate_by_key("starter_intro_299301"),
    )

    assert result["StageInfo"][0]["StarList"] == [1, 2, 3]
    assert result["RewardList"] == [
        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "count": 2, "extra": []},
        {"ItemId": LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID, "count": 3, "extra": []},
        {"ItemId": LOCAL_STAGE_STYLE_REWARD_ITEM_ID, "count": 1, "extra": []},
    ]


def test_verified_roster_can_resolve_clears_for_enterable_stage_catalog() -> None:
    standard_combo = (
        ("ATK", 18),
        ("1", 4),
        ("2", 4),
        ("3", 4),
        ("4", 2),
        ("5", 2),
        ("6", 2),
    )
    enterable_stages = [
        stage for stage in RECOVERED_BATTLE_STAGES if stage.can_enter_by_stage_id
    ]

    assert len(enterable_stages) >= 19
    assert len(enterable_stages) >= 70
    for character in VERIFIED_PLAYABLE_ROSTER:
        style = fight_style_for_character(character)
        for stage in enterable_stages:
            resolution = style.resolve_usage(
                standard_combo,
                hero_level=70,
                target_count=stage.encounter_target_count,
                target_hp_values=tuple(
                    spawn.combat_hp for spawn in stage.encounter_spawns
                ),
            )
            assert resolution.estimated_damage > 0
            assert resolution.defeated_targets == stage.encounter_target_count, (
                character.model_asset_id,
                stage.key,
                resolution.estimated_damage,
                resolution.defeated_targets,
                stage.encounter_target_count,
            )


def test_death_arms_scene_npc_uses_verified_protocol_row() -> None:
    expected = {
        "Uid": 20001,
        "Id": 5007,
        "X": 1,
        "Y": 2,
        "Z": 0,
        "Face": 0,
        "Version": 1,
        "ShapeId": 5007,
        "Attach": [],
        "HideStatus": 0,
        "AreaId": 0,
        "StartAnim": "",
        "BTName": "",
        "ForceShow": 0,
    }
    assert scene_npc(DEATH_ARMS, uid=20001, x=1, y=2) == expected
    assert scene_npc_from_spawn(DEATH_ARMS_DEMO_SPAWN) == {
        **expected,
        "X": DEATH_ARMS_DEMO_SPAWN.x,
        "Y": DEATH_ARMS_DEMO_SPAWN.y,
        "Face": DEATH_ARMS_DEMO_SPAWN.face,
    }


def test_tutorial_state_accumulates_guides_teach_and_base_station() -> None:
    state = TutorialState()

    assert state.finish_guides([9], [1301]) == {"Sets": [9], "Ids": [1301]}
    assert state.finish_guides([9, 10], [1301, 1302]) == {
        "Sets": [9, 10],
        "Ids": [1301, 1302],
    }
    assert state.record_login_drama_request(101, "", 0) is None
    assert state.requested_login_drama_stages == [101]
    assert state.record_login_drama_request(102, "login_intro_drama", 0) == {
        "DramaName": "login_intro_drama",
        "Loop": 0,
    }
    state.finish_login_drama(10001, 102)
    assert state.finished_login_drama_stages == {102: 10001}
    state.record_guide_drama(20001301, 10011)
    assert state.guide_drama_steps == {20001301: 10011}
    assert state.record_client_stat(2, [1, 1301, 10011], ["", ""]) == {
        "StatId": 2,
        "NumData": [1, 1301, 10011],
        "StrData": ["", ""],
    }
    assert state.client_stats == [
        {"StatId": 2, "NumData": [1, 1301, 10011], "StrData": ["", ""]}
    ]
    assert state.finish_teach(
        1011,
        [{"SkillId": 2, "Count": 1}, {"SkillId": 1, "Count": 3}],
    ) == {
        "HeroCId": 1011,
        "SkillList": [{"SkillId": 1, "Count": 3}, {"SkillId": 2, "Count": 1}],
    }
    assert state.finish_teach(1011, [{"SkillId": 2, "Count": 4}]) == {
        "HeroCId": 1011,
        "SkillList": [{"SkillId": 1, "Count": 3}, {"SkillId": 2, "Count": 4}],
    }
    assert state.base_station_all_info(23) == {
        "iClientVersion": 23,
        "arrFinishAidCount": [],
        "arrBaseStationInfo": [],
    }
    assert state.base_station_client_version == 23


def test_task_state_lists_accepts_submits_and_syncs_tasks() -> None:
    state = TaskState()

    task_info = state.task_info(STARTER_TASK.type)
    assert task_info == {
        "tasks": [STARTER_TASK.to_protocol()],
        "finishs": [],
        "IsStart": 1,
        "IsEnd": 1,
    }
    accept = state.accept(STARTER_TASK.id)
    assert accept["action_type"] == 1
    assert accept["task_info"]["Status"] == TASK_STATUS_ACCEPTED
    submit = state.submit(STARTER_TASK.id)
    assert submit["action_type"] == 2
    assert submit["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert state.task_info()["finishs"] == [STARTER_TASK.id]
    assert state.sync_info(STARTER_TASK.id, "guide", ["1301"]) == {
        "TaskId": STARTER_TASK.id,
        "Type": "guide",
        "ParamList": ["1301"],
    }
    assert state.enter_stage(1) == {"IsEnter": 1}
    guide_state = TaskState()
    guide_update = guide_state.complete_guide(STARTER_GUIDE_ID)
    assert guide_update is not None
    assert guide_update["task_info"]["Id"] == STARTER_GUIDE_ID
    assert guide_update["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert guide_update["task_info"]["Cond"][0]["CompCount"] == 1
    assert guide_update["task_info"]["Cond"][0]["ParamList"] == [
        STARTER_GUIDE_ID,
        STARTER_GUIDE_STEP,
    ]
    assert guide_state.complete_guide(STARTER_GUIDE_ID) is None
    stat_state = TaskState()
    stat_update = stat_state.observe_client_stat(
        {"StatId": 2, "NumData": [1, STARTER_GUIDE_ID, STARTER_GUIDE_STEP]}
    )
    assert stat_update is not None
    assert stat_update["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert stat_state.observe_client_stat(
        {"StatId": 2, "NumData": [0, STARTER_GUIDE_ID, STARTER_GUIDE_STEP]}
    ) is None


def test_activity_state_returns_empty_compatibility_payloads() -> None:
    state = ActivityState()

    assert state.stage_activity_info() == {"ProgressInfo": []}
    assert state.activity_shop_info(7) == {"BuyInfo": []}
    assert state.activity_shop_info(7) == {"BuyInfo": []}
    assert state.requested_activity_types == [7]
    assert state.entrust_task_list() == {"Version": 1, "EntrustTaskData": []}
    assert state.secret_area_task() == {"TaskList": []}
    assert state.usj_task() == {"TaskList": []}
    assert state.offlinepvp_task() == {"TaskList": []}
    assert state.battlefield_task_info() == {
        "IsFightOver": 0,
        "IsGetDayReward": 0,
        "IsGetWeekReward": 0,
        "ReplaceTimes": 0,
        "FreshenTime": 0,
        "Tasks": [],
    }
    assert state.group_open_map() == {"MapAttackArea": []}
    assert state.requested_group_maps == 1


def test_world_state_records_movement_frames_and_errors() -> None:
    state = WorldState()

    assert state.record_move([]) is None
    position = state.record_move(
        [
            {
                "X": 4221,
                "Y": 2040,
                "Z": 19931,
                "Face": 359,
                "Speed": 0,
                "ChState": 6,
                "ChAction": 1,
                "Extra": 0,
            }
        ]
    )
    assert position == ScenePosition(
        x=4221,
        y=2040,
        z=19931,
        face=359,
        character_state=6,
        character_action=1,
    )
    assert state.move_count == 1

    frame = state.record_frame_stat(uid=10001, stage_id=0, frame=30000, image_level=4)
    assert frame.uid == 10001
    assert state.frame_stats == [frame]

    state.record_client_error("local-guest:wait[c_time_ping]")
    assert state.client_errors == ["local-guest:wait[c_time_ping]"]

    state.record_unhandled_message("s_future_probe", 9999, {"Value": 1})
    assert state.unhandled_messages == [
        {"Name": "s_future_probe", "ProtocolId": 9999, "Values": {"Value": 1}}
    ]


def test_version_and_account_login_exchange() -> None:
    asyncio.run(_run_login_exchange())


async def _run_login_exchange() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    game.auto_provision_role = False
    server = await asyncio.start_server(game.handle_client, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]

    async with server:
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        handshake = await reader.readexactly(5)
        assert handshake[0] == 0
        seed = struct.unpack("<I", handshake[1:])[0]
        outbound = RollingXor(seed)
        inbound = FrameDecoder(RollingXor(seed ^ 0x6666))

        version = codec.encode_message(
            "s_login_version",
            {"ClientVersion": "40009.7.2", "PtoVersion": 48, "VerifyStr": "local"},
        )
        writer.write(encode_frame(registry.protocol_ids["s_login_version"], version, outbound))
        await writer.drain()
        reply_id, reply_body = await _read_frame(reader, inbound)
        assert registry.protocol_names[reply_id] == "c_login_version"
        assert codec.decode_message("c_login_version", reply_body) == {"server_id": 1}

        account = codec.encode_message(
            "s_login_account_enter", {"Account": "test-user", "Password": ""}
        )
        writer.write(
            encode_frame(registry.protocol_ids["s_login_account_enter"], account, outbound)
        )
        await writer.drain()
        reply_id, reply_body = await _read_frame(reader, inbound)
        assert registry.protocol_names[reply_id] == "c_login_account_info"
        values = codec.decode_message("c_login_account_info", reply_body)
        assert values["URS"] == "test-user"
        assert values["Uid"] == 0
        assert values["IsNewAccount"] == 1
        assert values["RoleList"] == []

        writer.close()
        await writer.wait_closed()


def test_player_creation_and_entry_responses() -> None:
    asyncio.run(_run_player_responses())


async def _run_player_responses() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x12345678),
        urs="test-user",
    )
    player_add = codec.encode_message("s_login_player_add", {"TypeId": 1})
    await game._dispatch(
        session,
        registry.protocol_ids["s_login_player_add"],
        player_add,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x12345678))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_login_player_info"
    player_info = codec.decode_message("c_login_player_info", reply_body)
    assert player_info == {
        "Uid": 10001,
        "Name": "Local Hero",
        "Level": 1,
        "HostId": 1,
        "ServerName": "Local Preservation Server",
        "CreateTime": player_info["CreateTime"],
    }
    assert game.roles == {"test-user": 10001}

    writer.data.clear()
    session.outbound = RollingXor(0x87654321)
    player_enter = codec.encode_message("s_login_player_enter", {"id": 4242})
    await game._dispatch(
        session,
        registry.protocol_ids["s_login_player_enter"],
        player_enter,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x87654321))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_login_checkstr",
        "c_user_create",
        "c_card_seeinfo",
        "c_card_show_info",
        "c_card_hero_bio_info",
        "c_area_event_login_data",
        "c_scene_player_info",
        "c_scene_enter",
        "c_scene_npc_create",
        "c_data_merge_to",
    ]
    reply_id, reply_body = replies[0]
    assert codec.decode_message("c_login_checkstr", reply_body) == {
        "CheckStr": "local-check"
    }
    reply_id, reply_body = replies[1]
    user_create = codec.decode_message("c_user_create", reply_body)
    assert user_create == {
        "user": {
            "Uid": 4242,
            "Name": "Local Hero",
            "Level": 1,
            "TopLevel": 0,
            "Gold": 0,
            "BindGold": 0,
            "HeroId": STARTER_HERO_ID,
            "CardUid": STARTER_CARD_UID,
            "Fighting": 0,
            "ReNameTimes": 0,
            "FirstRename": 0,
            "TotalLoginDays": 1,
            "PayZoneId": 1,
            "CreateTime": user_create["user"]["CreateTime"],
            "ShowHeroId": STARTER_HERO_ID,
        },
        "shape": STARTER_SHAPE_ID,
        "attach": [],
        "shape_cache_id": 0,
        "version": 1,
        "operator": 0,
        "ShowShapeId": STARTER_SHAPE_ID,
        "ShowShapeCacheId": 0,
    }
    reply_id, reply_body = replies[2]
    assert codec.decode_message("c_card_seeinfo", reply_body) == {
        "Uid": 4242,
        "CardInfo": [
            roster_card(
                character,
                STARTER_CARD_UID + index,
                fighting=int(index == 0),
            )
            for index, character in enumerate(INITIAL_PLAYABLE_ROSTER)
        ],
    }
    reply_id, reply_body = replies[3]
    assert codec.decode_message("c_card_show_info", reply_body) == {
        "ActiveAttachedCardIdList": []
    }
    reply_id, reply_body = replies[4]
    assert codec.decode_message("c_card_hero_bio_info", reply_body) == {
        "HeroBiographyList": [
            {"CardUid": STARTER_CARD_UID + index, "BiographyIdList": []}
            for index, _ in enumerate(INITIAL_PLAYABLE_ROSTER)
        ]
    }
    reply_id, reply_body = replies[5]
    area_event_login = codec.decode_message("c_area_event_login_data", reply_body)
    assert len(area_event_login["StageData"]) == len(AREA_EVENT_STAGES)
    assert area_event_login["StageData"][0] == {
        "StageId": 21111,
        "PassedTimes": 0,
        "DropCountTimes": 0,
        "Star": 0,
    }
    assert area_event_login["NormalLineup"] == [STARTER_CARD_UID]
    assert area_event_login["CacheStageId"] == 21111
    reply_id, reply_body = replies[6]
    assert codec.decode_message("c_scene_player_info", reply_body) == {
        "Uid": 4242,
        "Camp": 0,
        "Name": "Local Hero",
        "Level": 1,
        "TopLevel": 0,
        "ShowHeroId": STARTER_HERO_ID,
        "LeagueId": 0,
        "LeagueName": "",
        "TitleId": 0,
        "MoodId": 0,
        "Version": 1,
    }
    reply_id, reply_body = replies[7]
    assert codec.decode_message("c_scene_enter", reply_body) == {
        "SceneUid": STARTER_SCENE_ID,
        "X": STARTER_SCENE_X,
        "Y": STARTER_SCENE_Y,
        "Z": STARTER_SCENE_Z,
        "SceneId": STARTER_SCENE_ID,
        "Mode": 0,
        "EnterMode": 0,
        "Climbing": {
            "IsClimbing": 0,
            "ClimbMoveDir": 0,
            "Normal": {"X": 0, "Y": 0, "Z": 0},
        },
        "Extra": [],
    }
    reply_id, reply_body = replies[8]
    assert codec.decode_message("c_scene_npc_create", reply_body) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in INITIAL_MAP_SPAWNS]
    }
    reply_id, reply_body = replies[9]
    assert codec.decode_message("c_data_merge_to", reply_body) == {
        "str": "c_login_ok"
    }
    assert game.roles == {"test-user": 4242}


def test_expanded_roster_mode_serializes_all_verified_playable_cards() -> None:
    asyncio.run(_run_expanded_roster_cards())


def test_unlocked_profile_seeds_max_progress_and_all_verified_heroes() -> None:
    asyncio.run(_run_unlocked_profile())


def test_demo_cast_scene_sends_verified_map_character_rows() -> None:
    asyncio.run(_run_demo_cast_scene_sends_verified_map_character_rows())


async def _run_demo_cast_scene_sends_verified_map_character_rows() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    legacy_environment = {
        "MHATSH_PLAYER_LEVEL": "1",
        "MHATSH_HERO_LEVEL": "1",
        "MHATSH_CITY_LEVEL": "1",
        "MHATSH_SKIP_STARTER_QUEST": "0",
        "MHATSH_UNLOCK_ALL_FUNCTIONS": "0",
        "MHATSH_ROSTER_MODE": "starter",
    }
    with patch.dict(os.environ, legacy_environment, clear=False):
        game = GameServer(registry)
    game.map_spawns = DEMO_CAST_MAP_SPAWNS
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x12344321),
        uid=4242,
    )

    await game._send_initial_scene(writer, session)

    decoder = FrameDecoder(RollingXor(0x12344321))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_scene_player_info",
        "c_scene_enter",
        "c_scene_npc_create",
    ]
    reply_id, reply_body = replies[2]
    assert codec.decode_message("c_scene_npc_create", reply_body) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in DEMO_CAST_MAP_SPAWNS]
    }


async def _run_expanded_roster_cards() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    game.playable_roster = VERIFIED_PLAYABLE_ROSTER
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x13572468),
        uid=4242,
    )

    await game._send_initial_cards(writer, session)

    decoder = FrameDecoder(RollingXor(0x13572468))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_card_seeinfo",
        "c_card_show_info",
        "c_card_hero_bio_info",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_card_seeinfo"
    card_info = codec.decode_message("c_card_seeinfo", reply_body)["CardInfo"]
    assert card_info == [
        roster_card(
            character,
            STARTER_CARD_UID + index,
            fighting=int(index == 0),
            level=PLAYER_LEVEL_CAP,
        )
        for index, character in enumerate(VERIFIED_PLAYABLE_ROSTER)
    ]
    assert len(card_info) == len(VERIFIED_PLAYABLE_ROSTER) == 26
    assert card_info[0]["HeroId"] == STARTER_HERO_ID
    assert card_info[0]["ShapeId"] == STARTER_SHAPE_ID
    assert codec.decode_message("c_card_show_info", replies[1][1]) == {
        "ActiveAttachedCardIdList": []
    }
    assert codec.decode_message("c_card_hero_bio_info", replies[2][1]) == {
        "HeroBiographyList": [
            {"CardUid": STARTER_CARD_UID + index, "BiographyIdList": []}
            for index, _ in enumerate(VERIFIED_PLAYABLE_ROSTER)
        ]
    }


async def _run_unlocked_profile() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, {}, clear=True):
        game = GameServer(registry)

    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x44332211),
        uid=4242,
    )
    request = codec.encode_message("s_login_player_enter", {"id": 4242})
    await game._dispatch(
        session,
        registry.protocol_ids["s_login_player_enter"],
        request,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x44332211))
    replies = decoder.feed(bytes(writer.data))
    names = [registry.protocol_names[reply_id] for reply_id, _ in replies]
    assert names == [
        "c_login_checkstr",
        "c_user_create",
        "c_card_seeinfo",
        "c_card_show_info",
        "c_card_hero_bio_info",
        "c_area_event_login_data",
        "c_funcopen_list",
        "c_scene_player_info",
        "c_scene_enter",
        "c_scene_npc_create",
        "c_data_merge_to",
    ]
    user = codec.decode_message("c_user_create", replies[1][1])
    assert user["user"]["Level"] == PLAYER_LEVEL_CAP
    cards = codec.decode_message("c_card_seeinfo", replies[2][1])["CardInfo"]
    assert len(cards) == len(VERIFIED_PLAYABLE_ROSTER) == 26
    assert {card["Lv"] for card in cards} == {PLAYER_LEVEL_CAP}
    area_event_login = codec.decode_message("c_area_event_login_data", replies[5][1])
    assert len(area_event_login["StageData"]) == len(AREA_EVENT_STAGES)
    assert area_event_login["NormalLineup"] == [STARTER_CARD_UID]
    assert codec.decode_message("c_funcopen_list", replies[6][1]) == {
        "idlist": list(FUNCTION_OPEN_IDS)
    }
    scene_player = codec.decode_message("c_scene_player_info", replies[7][1])
    assert scene_player["Level"] == PLAYER_LEVEL_CAP
    task_info = session.tasks.task_info()
    assert task_info["finishs"] == [STARTER_TASK.id]
    assert task_info["tasks"][0]["Status"] == TASK_STATUS_FINISHED
    assert task_info["tasks"][0]["Cond"][0]["CompCount"] == 1
    assert session.tasks.should_spawn_beginner_npc(STARTER_TASK.id) is False
    assert STARTER_GUIDE_ID in session.tutorial.completed_guide_ids
    assert STARTER_MAP_GUIDE_ID in session.tutorial.completed_guide_ids
    assert STARTER_MAP_GUIDE_SET_ID in session.tutorial.completed_guide_sets
    assert session.world_tasks.city_level_info()["Level"] == CITY_LEVEL_CAP
    assert session.world_tasks.world_task_info()["FinishList"] == [
        {
            "Map": STARTER_WORLD_MAP_ID,
            "Area": STARTER_WORLD_AREA_ID,
            "TaskId": STARTER_TASK.id,
        }
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x44332212)
    query = codec.encode_message(
        "s_funcopen_query", {"TargetUid": 4242, "OpenId": 240}
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_funcopen_query"],
        query,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x44332212))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_funcopen_query"
    assert codec.decode_message("c_funcopen_query", reply_body) == {
        "TargetUid": 4242,
        "OpenId": 240,
        "Result": 1,
    }

    writer.data.clear()
    session.outbound = RollingXor(0x44332214)
    guide = codec.encode_message(
        "s_guide_finish",
        {
            "setIdList": [STARTER_MAP_GUIDE_SET_ID],
            "guideIdList": [STARTER_MAP_GUIDE_ID],
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_guide_finish"],
        guide,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x44332214))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_card_seeinfo",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_card_seeinfo"
    guide_cards = codec.decode_message("c_card_seeinfo", reply_body)
    assert guide_cards == {"Uid": 0, "CardInfo": []}

    writer.data.clear()
    session.outbound = RollingXor(0x44332213)
    last_card_uid = STARTER_CARD_UID + len(VERIFIED_PLAYABLE_ROSTER) - 1
    switch = codec.encode_message(
        "s_card_go_to_fight",
        {"CardUid": last_card_uid, "IsShow": 1},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_go_to_fight"],
        switch,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x44332213))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_card_go_to_fight",
        "c_scene_hero_change",
        "c_scene_player_info",
    ]
    assert codec.decode_message("c_card_go_to_fight", replies[0][1]) == {
        "CardUid": last_card_uid,
        "IsShow": 1,
    }
    assert session.roster is not None
    assert session.roster.active_hero_id == VERIFIED_PLAYABLE_ROSTER[-1].hero_id
    assert session.roster.active_shape_id == VERIFIED_PLAYABLE_ROSTER[-1].shape_id
    assert codec.decode_message("c_scene_hero_change", replies[1][1]) == {
        "Uid": 4242,
        "ShowHeroId": session.roster.active_hero_id,
        "ShapeCacheId": 0,
    }
    assert codec.decode_message("c_scene_player_info", replies[2][1])[
        "ShowHeroId"
    ] == session.roster.active_hero_id


def test_character_roster_requests_are_stateful() -> None:
    asyncio.run(_run_character_roster_requests())


def test_active_card_persists_across_server_instances(tmp_path: Path) -> None:
    asyncio.run(_run_active_card_persistence(tmp_path))


def test_stage_progress_persists_across_server_instances(tmp_path: Path) -> None:
    asyncio.run(_run_stage_progress_persistence(tmp_path))


def test_stage_family_progress_persists_across_server_instances(
    tmp_path: Path,
) -> None:
    asyncio.run(_run_stage_family_progress_persistence(tmp_path))


def test_character_menu_requests_return_roster_backed_empty_state() -> None:
    asyncio.run(_run_character_menu_requests())


async def _run_character_roster_requests() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x11223344),
        uid=4242,
    )

    userinfo_heros = codec.encode_message(
        "s_userinfo_heros",
        {"Cid": [STARTER_HERO_ID, 9999, 1021]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_userinfo_heros"],
        userinfo_heros,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x11223344))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_userinfo_hero_set"
    assert codec.decode_message("c_userinfo_hero_set", reply_body) == {
        "Heros": [STARTER_HERO_ID, 1021]
    }

    writer.data.clear()
    session.outbound = RollingXor(0x22334455)
    card_fight = codec.encode_message(
        "s_card_go_to_fight",
        {"CardUid": STARTER_CARD_UID + 1, "IsShow": 1},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_go_to_fight"],
        card_fight,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x22334455))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_card_go_to_fight",
        "c_scene_hero_change",
        "c_scene_player_info",
    ]
    assert codec.decode_message("c_card_go_to_fight", replies[0][1]) == {
        "CardUid": STARTER_CARD_UID + 1,
        "IsShow": 1,
    }
    assert session.roster is not None
    assert session.roster.active_hero_id == 1021
    assert session.roster.active_shape_id == 1002
    assert codec.decode_message("c_scene_hero_change", replies[1][1]) == {
        "Uid": 4242,
        "ShowHeroId": 1021,
        "ShapeCacheId": 0,
    }
    assert codec.decode_message("c_scene_player_info", replies[2][1])[
        "ShowHeroId"
    ] == 1021

    writer.data.clear()
    session.outbound = RollingXor(0x2A3B4C5D)
    session.roster = None
    restored_roster = game._ensure_roster(session)
    assert restored_roster.active_hero_id == 1021
    session.roster = restored_roster
    writer.data.clear()
    session.outbound = RollingXor(0x2A3B4C5D)
    bridge_fight = codec.encode_message(
        "s_card_go_to_bridge_fight",
        {"HeroUid": STARTER_CARD_UID + 2},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_go_to_bridge_fight"],
        bridge_fight,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x2A3B4C5D))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_card_go_to_bridge_fight",
        "c_scene_hero_change",
        "c_scene_player_info",
    ]
    assert codec.decode_message("c_card_go_to_bridge_fight", replies[0][1]) == {
        "HeroUid": STARTER_CARD_UID + 2
    }
    assert session.roster.active_hero_id == 1061
    assert codec.decode_message("c_scene_hero_change", replies[1][1]) == {
        "Uid": 4242,
        "ShowHeroId": 1061,
        "ShapeCacheId": 0,
    }
    assert codec.decode_message("c_scene_player_info", replies[2][1])[
        "ShowHeroId"
    ] == 1061

    writer.data.clear()
    session.outbound = RollingXor(0x33445566)
    team_change = codec.encode_message("s_team_change_hero", {"HeroId": 1061})
    await game._dispatch(
        session,
        registry.protocol_ids["s_team_change_hero"],
        team_change,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x33445566))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_team_change_hero",
        "c_scene_hero_change",
    ]
    assert codec.decode_message("c_team_change_hero", replies[0][1]) == {
        "UserUId": 4242,
        "HeroId": 1061,
        "Fighting": 1,
        "Vitality": 100,
        "ShapeId": 1006,
        "MLv": 1,
    }
    assert codec.decode_message("c_scene_hero_change", replies[1][1]) == {
        "Uid": 4242,
        "ShowHeroId": 1061,
        "ShapeCacheId": 0,
    }

    writer.data.clear()
    session.outbound = RollingXor(0x44556677)
    team_play = codec.encode_message(
        "s_team_change_play",
        {"PlayId": 7, "Extra": [11, 22]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_team_change_play"],
        team_play,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x44556677))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_team_change_play"
    assert codec.decode_message("c_team_change_play", reply_body) == {
        "PlayId": 7,
        "Extra": [{"Key": "1", "Val": 11}, {"Key": "2", "Val": 22}],
    }

    writer.data.clear()
    session.outbound = RollingXor(0x55667788)
    area_switch = codec.encode_message(
        "s_area_event_switch_hero",
        {"HeroUId": STARTER_CARD_UID + 3},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_area_event_switch_hero"],
        area_switch,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55667788))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_area_event_switch_hero"
    assert codec.decode_message("c_area_event_switch_hero", reply_body) == {
        "ControlId": STARTER_CARD_UID + 3
    }
    assert session.roster.active_hero_id == 1071


async def _run_active_card_persistence(tmp_path: Path) -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    profile_path = tmp_path / "profiles.json"
    with patch.dict(
        os.environ,
        {
            "MHATSH_PROFILE_STORE": str(profile_path),
            "MHATSH_ROSTER_MODE": "verified",
        },
    ):
        first_game = GameServer(registry)
        writer = BufferWriter()
        first_session = Session(
            seed=1,
            decoder=FrameDecoder(None),
            outbound=RollingXor(0x10203040),
            urs="local-guest",
            uid=4242,
        )
        request = codec.encode_message(
            "s_card_go_to_fight",
            {"CardUid": STARTER_CARD_UID + 3, "IsShow": 1},
        )
        await first_game._dispatch(
            first_session,
            registry.protocol_ids["s_card_go_to_fight"],
            request,
            writer,
        )

        second_game = GameServer(registry)
        second_session = Session(
            seed=2,
            decoder=FrameDecoder(None),
            outbound=RollingXor(0x50607080),
            urs="local-guest",
            uid=4242,
        )
        restored = second_game._ensure_roster(second_session)

    assert profile_path.exists()
    assert restored.active_card_uid == STARTER_CARD_UID + 3
    assert restored.active_hero_id == first_session.roster.active_hero_id


async def _run_stage_progress_persistence(tmp_path: Path) -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    profile_path = tmp_path / "profiles.json"
    with patch.dict(
        os.environ,
        {
            "MHATSH_PROFILE_STORE": str(profile_path),
            "MHATSH_ROSTER_MODE": "verified",
            "MHATSH_STAGE_REPORT_RESPONSE": "complete",
        },
    ):
        first_game = GameServer(registry)
        writer = BufferWriter()
        first_session = Session(
            seed=1,
            decoder=FrameDecoder(None),
            outbound=RollingXor(0xAABBCCDD),
            urs="local-guest",
            uid=4242,
        )
        first_game._configure_session(first_session)
        first_session.stage.enter_recovered_stage(
            stage_candidate_by_key("starter_intro_299301")
        )
        report = codec.encode_message(
            "s_stage_report",
                {
                    "Id": STARTER_INTRO_STAGE_ID,
                    "Result": 1,
                    "AllDmg": 6900,
                    "ItemNum": [{"ItemId": 1001, "Amount": 2}],
                    "EndReport": {
                        "RoundTimeUse": 74,
                        "RoundFighterDpsTotal": 6900,
                        "RoundFighterButtonClickCountATK": 12,
                        "RoundFighterButtonClickCount1": 3,
                        "RoundFighterButtonClickCount4": 1,
                },
            },
        )
        await first_game._dispatch(
            first_session,
            registry.protocol_ids["s_stage_report"],
            report,
            writer,
        )

        decoder = FrameDecoder(RollingXor(0xAABBCCDD))
        replies = decoder.feed(bytes(writer.data))
        assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
            "c_stage_drop",
            "c_stage_result",
            "c_stage_end_gm",
        ]

        second_game = GameServer(registry)
        second_session = Session(
            seed=2,
            decoder=FrameDecoder(None),
            outbound=RollingXor(0xDDCCBBAA),
            urs="local-guest",
            uid=4242,
        )
        second_game._configure_session(second_session)

    raw_profile = json.loads(profile_path.read_text(encoding="utf-8"))
    saved = raw_profile["stage_progress"]["local-guest"][str(STARTER_INTRO_STAGE_ID)]
    assert saved["status"] == 1
    assert saved["stars"] == [1, 2, 3]
    assert saved["best_time"] == 74
    assert saved["pass_count"] == 1
    assert raw_profile["normal_items"]["local-guest"] == {
        str(LOCAL_STAGE_PASS_REWARD_ITEM_ID): 2,
        str(LOCAL_STAGE_FIRST_REWARD_ITEM_ID): 1,
    }

    restored = second_session.stage.completions[STARTER_INTRO_STAGE_ID]
    assert restored.status == 1
    assert restored.stars == (1, 2, 3)
    assert restored.best_time == 74
    assert restored.pass_count == 1
    assert second_game.profile_store.normal_item_list("local-guest") == [
        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Amount": 2},
        {"ItemId": LOCAL_STAGE_FIRST_REWARD_ITEM_ID, "Amount": 1},
    ]


async def _run_stage_family_progress_persistence(tmp_path: Path) -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    profile_path = tmp_path / "profiles.json"
    with patch.dict(
        os.environ,
        {
            "MHATSH_PROFILE_STORE": str(profile_path),
            "MHATSH_ROSTER_MODE": "verified",
        },
    ):
        first_game = GameServer(registry)
        first_writer = BufferWriter()
        first_session = Session(
            seed=1,
            decoder=FrameDecoder(None),
            outbound=RollingXor(0xCAFE1001),
            urs="local-guest",
            uid=4242,
        )
        pressure_finish = codec.encode_message(
            "s_pressure_stage_finish",
            {
                "StageId": 777777,
                "HeroUid": STARTER_CARD_UID,
                "Score": 12345,
                "ScoreDetails": [10000, 2000, 345],
                "Save": 1,
            },
        )
        await first_game._dispatch(
            first_session,
            registry.protocol_ids["s_pressure_stage_finish"],
            pressure_finish,
            first_writer,
        )
        assert first_writer.data == bytearray()

        first_session.outbound = RollingXor(0xCAFE1002)
        daily_report = codec.encode_message(
            "s_act_daily_stage_report",
            {"ActId": 12, "Result": 1, "Count": 4},
        )
        await first_game._dispatch(
            first_session,
            registry.protocol_ids["s_act_daily_stage_report"],
            daily_report,
            first_writer,
        )
        decoder = FrameDecoder(RollingXor(0xCAFE1002))
        [(reply_id, reply_body)] = decoder.feed(bytes(first_writer.data))
        assert registry.protocol_names[reply_id] == "c_act_daily_stage_result"
        assert codec.decode_message("c_act_daily_stage_result", reply_body)[
            "Count"
        ]["Count"] == 1

        second_game = GameServer(registry)
        second_writer = BufferWriter()
        second_session = Session(
            seed=2,
            decoder=FrameDecoder(None),
            outbound=RollingXor(0xCAFE1003),
            urs="local-guest",
            uid=4242,
        )
        second_game._configure_session(second_session)

        pressure_detail = codec.encode_message(
            "s_pressure_stage_detail",
            {"StageId": 777777},
        )
        await second_game._dispatch(
            second_session,
            registry.protocol_ids["s_pressure_stage_detail"],
            pressure_detail,
            second_writer,
        )
        decoder = FrameDecoder(RollingXor(0xCAFE1003))
        [(reply_id, reply_body)] = decoder.feed(bytes(second_writer.data))
        assert registry.protocol_names[reply_id] == "c_pressure_stage_detail"
        assert codec.decode_message("c_pressure_stage_detail", reply_body)[
            "StageScore"
        ] == 12345

    raw_profile = json.loads(profile_path.read_text(encoding="utf-8"))
    family = raw_profile["stage_family_progress"]["local-guest"]
    assert family["pressure_scores"] == {"777777": 12345}
    assert family["daily_stage_counts"] == {"12": 1}
    assert raw_profile["normal_items"]["local-guest"] == {
        str(LOCAL_STAGE_PASS_REWARD_ITEM_ID): 4
    }
    assert second_session.stage.pressure_scores == {777777: 12345}
    assert second_session.stage.daily_stage_counts == {12: 1}
    assert second_game.profile_store.normal_item_list("local-guest") == [
        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Amount": 4}
    ]


async def _run_character_menu_requests() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x66778899),
        uid=4242,
    )

    skill_level = codec.encode_message(
        "s_skill_get_skill_level_list",
        {"HeroUidList": [STARTER_CARD_UID, STARTER_CARD_UID + 99]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_skill_get_skill_level_list"],
        skill_level,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66778899))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_skill_level_list"
    assert codec.decode_message("c_skill_level_list", reply_body) == {
        "SkillInfoList": [
            {
                "HeroUid": STARTER_CARD_UID,
                "SkillLevelInfo": fight_style_for_character(
                    STARTER_CHARACTER
                ).protocol_skill_levels(PLAYER_LEVEL_CAP),
            }
        ]
    }

    writer.data.clear()
    session.outbound = RollingXor(0x778899AA)
    spec_level = codec.encode_message(
        "s_skill_get_spec_level_list",
        {"HeroUidList": [STARTER_CARD_UID + 1]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_skill_get_spec_level_list"],
        spec_level,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x778899AA))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_skill_spec_level_list"
    assert codec.decode_message("c_skill_spec_level_list", reply_body) == {
        "SpecInfoList": [
            {"HeroUid": STARTER_CARD_UID + 1, "SpecLevelInfo": []}
        ]
    }

    detail_requests = [
        (
            "s_skill_get_skill_level",
            {"HeroUid": STARTER_CARD_UID + 2},
            "c_skill_get_skill_level",
            {
                "SkillInfo": {
                    "HeroUid": STARTER_CARD_UID + 2,
                    "SkillLevelInfo": fight_style_for_character(
                        INITIAL_PLAYABLE_ROSTER[2]
                    ).protocol_skill_levels(PLAYER_LEVEL_CAP),
                }
            },
        ),
        (
            "s_skill_get_spec_level",
            {"HeroUid": STARTER_CARD_UID + 2},
            "c_skill_get_spec_level",
            {
                "SpecInfo": {
                    "HeroUid": STARTER_CARD_UID + 2,
                    "SpecLevelInfo": [],
                }
            },
        ),
        (
            "s_gem_list",
            {"HeroCId": [INITIAL_PLAYABLE_ROSTER[2].hero_id]},
            "c_gem_list",
            {
                "Total": 0,
                "HeroGemData": [
                    {
                        "HeroCId": INITIAL_PLAYABLE_ROSTER[2].hero_id,
                        "GemData": [],
                    }
                ],
            },
        ),
        (
            "s_toplist_pages",
            {
                "ID": 102,
                "SubName": 132,
                "PageNums": [1],
                "SelfUid": 4242,
                "IsCross": 0,
            },
            "c_toplist_pages",
            {
                "ID": 102,
                "SubName": 132,
                "PageNums": [1],
                "MaxPageNum": 0,
                "SelfUid": 4242,
                "Pages": [],
                "SelfRankInfo": {"Rank": 0, "Number": [], "String": []},
                "IsCross": 0,
            },
        ),
    ]
    for index, (request_name, request, response_name, response) in enumerate(
        detail_requests
    ):
        writer.data.clear()
        key = 0x788899AA + index
        session.outbound = RollingXor(key)
        await game._dispatch(
            session,
            registry.protocol_ids[request_name],
            codec.encode_message(request_name, request),
            writer,
        )
        decoder = FrameDecoder(RollingXor(key))
        [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
        assert registry.protocol_names[reply_id] == response_name
        assert codec.decode_message(response_name, reply_body) == response

    writer.data.clear()
    session.outbound = RollingXor(0x8899AABB)
    await game._dispatch(
        session,
        registry.protocol_ids["s_hero_rank_info"],
        codec.encode_message("s_hero_rank_info", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x8899AABB))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_hero_rank_info"
    rank_info = codec.decode_message("c_hero_rank_info", reply_body)
    assert rank_info["TotalStar"] == 0
    assert rank_info["HeroStar"] == [
        {"Cid": character.hero_id, "Star": 0}
        for character in VERIFIED_PLAYABLE_ROSTER
    ]
    assert rank_info["TaskList"] == []

    writer.data.clear()
    session.outbound = RollingXor(0x99AABBCC)
    show_oper = codec.encode_message("s_card_show_oper", {"Id": 17})
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_show_oper"],
        show_oper,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x99AABBCC))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_show_oper"
    assert codec.decode_message("c_card_show_oper", reply_body) == {"Id": 17}
    assert session.character_menu.opened_show_ids == [17]

    writer.data.clear()
    session.outbound = RollingXor(0xAABBCCDD)
    card_lock = codec.encode_message(
        "s_card_lock", {"Uid": STARTER_CARD_UID, "IsLock": 1}
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_lock"],
        card_lock,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xAABBCCDD))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_lock"
    assert codec.decode_message("c_card_lock", reply_body) == {
        "Uid": STARTER_CARD_UID,
        "IsLock": 1,
    }

    writer.data.clear()
    session.outbound = RollingXor(0xBBCCDDEE)
    skill_lock = codec.encode_message(
        "s_card_lock_skill", {"HeroCId": STARTER_HERO_ID, "Index": 2, "IsLock": 1}
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_lock_skill"],
        skill_lock,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xBBCCDDEE))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_lock_skill"
    assert codec.decode_message("c_card_lock_skill", reply_body) == {
        "HeroCId": STARTER_HERO_ID,
        "Index": 2,
        "IsLock": 1,
    }

    support_hero = INITIAL_PLAYABLE_ROSTER[1]
    writer.data.clear()
    session.outbound = RollingXor(0xBBCCDDEF)
    support_skill = codec.encode_message(
        "s_card_support_skill",
        {
            "HeroCId": STARTER_HERO_ID,
            "Index": 1,
            "SupportHeroCId": support_hero.hero_id,
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_support_skill"],
        support_skill,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xBBCCDDEF))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_support_skill"
    assert codec.decode_message("c_card_support_skill", reply_body) == {
        "Supports": [
            {
                "HeroCId": STARTER_HERO_ID,
                "Index": 1,
                "SupportHeroCId": support_hero.hero_id,
                "IsAuto": 0,
            }
        ]
    }

    writer.data.clear()
    session.outbound = RollingXor(0xCCDDEEFF)
    await game._dispatch(
        session,
        registry.protocol_ids["s_attached_card_book"],
        codec.encode_message("s_attached_card_book", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xCCDDEEFF))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_attached_card_book"
    assert codec.decode_message("c_attached_card_book", reply_body) == {
        "Page": 0,
        "Book": support_card_book_entries(),
    }

    writer.data.clear()
    session.outbound = RollingXor(0xDDEEFF11)
    attached_oper = codec.encode_message(
        "s_attached_card_oper",
        {"HeroId": STARTER_HERO_ID, "Index": 1, "Oper": 0, "ACardUid": 0},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_attached_card_oper"],
        attached_oper,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xDDEEFF11))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_attached_card_info"
    assert codec.decode_message("c_attached_card_info", reply_body) == {
        "AttachedCardInfo": [
            {"HeroId": character.hero_id, "SlotInfo": []}
            for character in VERIFIED_PLAYABLE_ROSTER
        ]
    }

    writer.data.clear()
    session.outbound = RollingXor(0xDDEEFF12)
    attached_oper = codec.encode_message(
        "s_attached_card_oper",
        {
            "HeroId": STARTER_HERO_ID,
            "Index": 1,
            "Oper": 0,
            "ACardUid": SUPPORT_CHARACTERS["h1927"].item_id,
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_attached_card_oper"],
        attached_oper,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xDDEEFF12))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_attached_card_info"
    attached_info = codec.decode_message("c_attached_card_info", reply_body)
    assert attached_info["AttachedCardInfo"][0] == {
        "HeroId": STARTER_HERO_ID,
        "SlotInfo": [{"Index": 1, "ACardUid": SUPPORT_CHARACTERS["h1927"].item_id}],
    }

    assert session.character_menu.card_show_info() == {
        "ActiveAttachedCardIdList": [SUPPORT_CHARACTERS["h1927"].item_id]
    }

    writer.data.clear()
    session.outbound = RollingXor(0xDDEEFF14)
    attached_clear = codec.encode_message(
        "s_attached_card_oper",
        {
            "HeroId": STARTER_HERO_ID,
            "Index": 1,
            "Oper": 1,
            "ACardUid": SUPPORT_CHARACTERS["h1927"].item_id,
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_attached_card_oper"],
        attached_clear,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xDDEEFF14))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_attached_card_info"
    assert codec.decode_message("c_attached_card_info", reply_body)[
        "AttachedCardInfo"
    ][0] == {"HeroId": STARTER_HERO_ID, "SlotInfo": []}

    writer.data.clear()
    session.outbound = RollingXor(0xEEFF1122)
    equip_on = codec.encode_message("s_equip_on", {"EquipUid": 1234})
    await game._dispatch(
        session,
        registry.protocol_ids["s_equip_on"],
        equip_on,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xEEFF1122))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_equip_list",
        "c_equip_attr",
    ]
    assert codec.decode_message("c_equip_list", replies[0][1]) == {"UidList": []}
    assert codec.decode_message("c_equip_attr", replies[1][1]) == {
        "EquipAttrList": {"Uid": 1234, "ExtraAttr": [], "HideAttr": []}
    }

    writer.data.clear()
    session.outbound = RollingXor(0xFF112233)
    area_list = codec.encode_message(
        "s_area_event_hero_list",
        {"Type": 2, "Lineup": [STARTER_CARD_UID + 2]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_area_event_hero_list"],
        area_list,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xFF112233))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_area_event_hero_list"
    assert codec.decode_message("c_area_event_hero_list", reply_body) == {
        "Type": 2,
        "NormalLineup": [STARTER_CARD_UID + 2],
        "ActLineup": [],
    }

    writer.data.clear()
    session.outbound = RollingXor(0x11224488)
    await game._dispatch(
        session,
        registry.protocol_ids["s_training_info"],
        codec.encode_message("s_training_info", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x11224488))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_training_info"
    assert codec.decode_message("c_training_info", reply_body) == {
        "HeroData": [
            {"HeroCId": character.hero_id, "FinishList": [], "GetList": []}
            for character in VERIFIED_PLAYABLE_ROSTER
        ]
    }

    writer.data.clear()
    session.outbound = RollingXor(0x11224489)
    training = codec.encode_message("s_training_hero_info", {"HeroId": 0})
    await game._dispatch(
        session,
        registry.protocol_ids["s_training_hero_info"],
        training,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x11224489))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_training_hero_info"
    training_info = codec.decode_message("c_training_hero_info", reply_body)
    assert training_info["TrainingData"]["HeroId"] == STARTER_HERO_ID
    assert training_info["TrainingData"]["CardUid"] == STARTER_CARD_UID
    assert training_info["TrainingData"]["CardSkillLevel"] == [
        {
            "HeroUid": STARTER_CARD_UID,
            "SkillLevel": fight_style_for_character(
                STARTER_CHARACTER
            ).protocol_skill_levels(PLAYER_LEVEL_CAP),
        }
    ]
    assert training_info["TrainingData"]["SupportSkill"] == [
        {
            "Index": 1,
            "HeroId": support_hero.hero_id,
            "ShapeId": support_hero.shape_id,
            "FashionId": 0,
        }
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x1122448A)
    support_clear = codec.encode_message(
        "s_card_support_skill",
        {"HeroCId": STARTER_HERO_ID, "Index": 1, "SupportHeroCId": 0},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_card_support_skill"],
        support_clear,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x1122448A))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_support_skill"
    assert codec.decode_message("c_card_support_skill", reply_body) == {
        "Supports": []
    }

    writer.data.clear()
    session.outbound = RollingXor(0x22448811)
    league_heroes = codec.encode_message("s_league_pvp_self_hero_list", {"Uid": 4242})
    await game._dispatch(
        session,
        registry.protocol_ids["s_league_pvp_self_hero_list"],
        league_heroes,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x22448811))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_league_pvp_self_hero_list"
    assert codec.decode_message("c_league_pvp_self_hero_list", reply_body) == {
        "HeroList": [
            {
                "HeroCId": character.hero_id,
                "Hp": 100,
                "BuffLayer": 0,
                "CdTime": 0,
            }
            for character in VERIFIED_PLAYABLE_ROSTER
        ]
    }


def test_scene_load_completion_response() -> None:
    asyncio.run(_run_scene_load_completion())


async def _run_scene_load_completion() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0xAABBCCDD),
    )
    scene_loaded = codec.encode_message(
        "s_scene_enter_end", {"SceneId": STARTER_SCENE_ID}
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_scene_enter_end"],
        scene_loaded,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0xAABBCCDD))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_scene_enter_end"
    assert codec.decode_message("c_scene_enter_end", reply_body) == {}


def test_time_ping_echoes_send_time() -> None:
    asyncio.run(_run_time_ping())


def test_guide_finish_acknowledges_completed_sets_and_guides() -> None:
    asyncio.run(_run_guide_finish())


async def _run_guide_finish() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x10203040),
    )
    guide_finish = codec.encode_message(
        "s_guide_finish",
        {"setIdList": [9], "guideIdList": [1301]},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_guide_finish"],
        guide_finish,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x10203040))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_guide_finish",
        "c_scene_npc_create",
        "c_task_info_update",
        "c_city_level_add_exp",
        "c_city_level_up",
        "c_city_level_info",
        "c_world_task_info",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_guide_finish"
    assert codec.decode_message("c_guide_finish", reply_body) == {
        "Sets": [9],
        "Ids": [1301],
    }
    reply_id, reply_body = replies[1]
    assert registry.protocol_names[reply_id] == "c_scene_npc_create"
    assert codec.decode_message("c_scene_npc_create", reply_body) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in TUTORIAL_MAP_SPAWNS]
    }
    reply_id, reply_body = replies[2]
    task_update = codec.decode_message("c_task_info_update", reply_body)
    assert task_update["task_info"]["Id"] == STARTER_GUIDE_ID
    assert task_update["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert codec.decode_message("c_city_level_add_exp", replies[3][1]) == {
        "Exp": BEGINNER_QUEST_CITY_EXP
    }
    assert codec.decode_message("c_city_level_up", replies[4][1]) == {
        "Level": BEGINNER_QUEST_CITY_LEVEL
    }
    assert codec.decode_message("c_city_level_info", replies[5][1]) == {
        "Level": BEGINNER_QUEST_CITY_LEVEL,
        "ClickList": [],
    }
    assert codec.decode_message("c_world_task_info", replies[6][1])["FinishList"] == [
        {"Map": STARTER_WORLD_MAP_ID, "Area": 0, "TaskId": STARTER_GUIDE_ID}
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x20304050)
    next_guide_finish = codec.encode_message(
        "s_guide_finish",
        {"setIdList": [10], "guideIdList": [1302]},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_guide_finish"],
        next_guide_finish,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x20304050))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_guide_finish"
    assert codec.decode_message("c_guide_finish", reply_body) == {
        "Sets": [10],
        "Ids": [1302],
    }
    assert session.tutorial.completed_guide_sets == {9, 10}
    assert session.tutorial.completed_guide_ids == {1301, 1302}


def test_guide_drama_records_tutorial_step_without_extra_reply() -> None:
    asyncio.run(_run_guide_drama())


async def _run_guide_drama() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x10203040),
    )
    guide_drama = codec.encode_message(
        "s_guide_drama",
        {"Uid": 10001, "Id": 20001301, "Step": 10011, "skip": 0},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_guide_drama"],
        guide_drama,
        writer,
    )

    assert writer.data == bytearray()
    assert session.tutorial.guide_drama_steps == {20001301: 10011}


def test_client_stat_can_complete_starter_task_once() -> None:
    asyncio.run(_run_client_stat())


def test_starter_intro_stage_payload_matches_recovered_schema() -> None:
    state = StageState()

    assert state.enter_stage() == {
        "StageId": STARTER_INTRO_STAGE_ID,
        "StageUid": STARTER_INTRO_STAGE_UID,
        "Level": STARTER_INTRO_STAGE_LEVEL,
        "Time": STARTER_INTRO_STAGE_TIME,
        "Drama": STARTER_INTRO_STAGE_DRAMA,
        "IsReconnect": 0,
        "NeedLagLog": 0,
        "IsRecord": 0,
        "Extra": [],
    }
    assert state.finish_loading(10001) == {"Uid": 10001}
    assert state.finished_loading_count == 1

    all_might_payload = state.enter_recovered_stage(
        stage_candidate_by_key("all_might_stage_502601")
    )
    assert all_might_payload["StageId"] == 502601
    assert all_might_payload["StageUid"] == 5026010001
    assert state.current_stage_key == "all_might_stage_502601"


def test_intro_stage_key_selects_recovered_candidate_defaults() -> None:
    with patch.dict(
        os.environ,
        {
            "MHATSH_INTRO_STAGE_KEY": "all_might_stage_502601",
            "MHATSH_INTRO_STAGE_MODE": "starter",
        },
        clear=False,
    ):
        game = GameServer(
            SchemaRegistry.from_files(
                ROOT / "allproto_readable.lua",
                ROOT / "analysis" / "protocol_ids.csv",
            )
        )

    assert game.intro_stage_candidate.key == "all_might_stage_502601"
    assert game.intro_stage_id == 502601
    assert game.intro_stage_uid == 5026010001


async def _run_client_stat() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x31415926),
    )
    stat = codec.encode_message(
        "s_client_stat",
        {"StatId": 2, "NumData": [1, 1301, 10011], "StrData": ["", ""]},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_client_stat"],
        stat,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x31415926))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_scene_npc_create",
        "c_task_info_update",
        "c_city_level_add_exp",
        "c_city_level_up",
        "c_city_level_info",
        "c_world_task_info",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_scene_npc_create"
    assert codec.decode_message("c_scene_npc_create", reply_body) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in TUTORIAL_MAP_SPAWNS]
    }
    reply_id, reply_body = replies[1]
    assert registry.protocol_names[reply_id] == "c_task_info_update"
    task_update = codec.decode_message("c_task_info_update", reply_body)
    assert task_update["task_info"]["Id"] == STARTER_GUIDE_ID
    assert task_update["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert codec.decode_message("c_city_level_add_exp", replies[2][1]) == {
        "Exp": BEGINNER_QUEST_CITY_EXP
    }
    assert codec.decode_message("c_city_level_up", replies[3][1]) == {
        "Level": BEGINNER_QUEST_CITY_LEVEL
    }
    assert session.tutorial.client_stats == [
        {"StatId": 2, "NumData": [1, 1301, 10011], "StrData": ["", ""]}
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x27182818)
    await game._dispatch(
        session,
        registry.protocol_ids["s_client_stat"],
        stat,
        writer,
    )
    assert writer.data == bytearray()


def test_teach_finish_acknowledges_skill_practice_state() -> None:
    asyncio.run(_run_teach_finish())


async def _run_teach_finish() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x22334455),
    )
    teach_finish = codec.encode_message(
        "s_teach_finish",
        {
            "HeroCId": STARTER_HERO_ID,
            "SkillList": [{"SkillId": 11, "Count": 1}],
        },
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_teach_finish"],
        teach_finish,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x22334455))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_teach_finish"
    assert codec.decode_message("c_teach_finish", reply_body) == {
        "HeroCId": STARTER_HERO_ID,
        "SkillList": [{"SkillId": 11, "Count": 1}],
    }


def test_base_station_info_preserves_client_version() -> None:
    asyncio.run(_run_base_station_info())


def test_login_drama_packets_record_stage_and_can_play_configured_drama() -> None:
    asyncio.run(_run_login_drama_packets())


def test_account_info_can_request_login_drama_when_enabled() -> None:
    asyncio.run(_run_account_info_login_drama_flags())


def test_task_requests_receive_stateful_protocol_responses() -> None:
    asyncio.run(_run_task_requests())


def test_starter_intro_stage_probe_packets() -> None:
    asyncio.run(_run_starter_intro_stage_probe())


def test_stage_loading_and_report_lifecycle_packets() -> None:
    asyncio.run(_run_stage_lifecycle_packets())


def test_requested_stage_enter_packets_start_combat_stages() -> None:
    asyncio.run(_run_requested_stage_enter_packets())


def test_verified_roster_characters_can_enter_combat_with_skill_payloads() -> None:
    asyncio.run(_run_verified_roster_stage_entry_payloads())


def test_stage_enter_can_emit_recovered_encounter_npcs() -> None:
    asyncio.run(_run_stage_enter_encounter_npcs())


def test_stage_family_info_packets_are_stateful() -> None:
    asyncio.run(_run_stage_family_info_packets())


def test_starter_guide_can_trigger_intro_stage_probe() -> None:
    asyncio.run(_run_starter_guide_intro_stage_probe())


def test_world_telemetry_packets_update_session_without_reply() -> None:
    asyncio.run(_run_world_telemetry())


async def _run_world_telemetry() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0xABCDEF01),
    )

    move = codec.encode_message(
        "s_scene_move",
        {
            "Path": [
                {
                    "X": 4221,
                    "Y": 2040,
                    "Z": 19931,
                    "Face": 359,
                    "Speed": 0,
                    "ChState": 6,
                    "ChAction": 1,
                    "Extra": 0,
                }
            ]
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_scene_move"],
        move,
        writer,
    )
    assert writer.data == bytearray()
    assert session.world.last_position == ScenePosition(
        x=4221,
        y=2040,
        z=19931,
        face=359,
        character_state=6,
        character_action=1,
    )

    frame = codec.encode_message(
        "s_client_stat_frame",
        {"uid": 10001, "iStageId": 0, "iFrame": 30000, "iImageLevel": 4},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_client_stat_frame"],
        frame,
        writer,
    )
    assert writer.data == bytearray()
    assert session.world.frame_stats[-1].uid == 10001

    error = codec.encode_message("s_client_error", {"Msg": "wait[c_time_ping]"})
    await game._dispatch(
        session,
        registry.protocol_ids["s_client_error"],
        error,
        writer,
    )
    assert writer.data == bytearray()
    assert session.world.client_errors == ["wait[c_time_ping]"]

    await game._dispatch(session, 9999, b"", writer)
    assert writer.data == bytearray()
    assert session.world.unhandled_messages == [
        {"Name": "unknown_9999", "ProtocolId": 9999, "Values": {}}
    ]


async def _run_task_requests() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x66778899),
    )

    task_list = codec.encode_message(
        "s_task_get_tasklist_bytype",
        {"task_type": STARTER_TASK.type},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_task_get_tasklist_bytype"],
        task_list,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66778899))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_task_info"
    assert codec.decode_message("c_task_info", reply_body) == {
        "tasks": [STARTER_TASK.to_protocol()],
        "finishs": [],
        "IsStart": 1,
        "IsEnd": 1,
    }

    writer.data.clear()
    session.outbound = RollingXor(0x778899AA)
    accept = codec.encode_message("s_task_accept", {"task_id": STARTER_TASK.id})
    await game._dispatch(
        session,
        registry.protocol_ids["s_task_accept"],
        accept,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x778899AA))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_task_info_update",
        "c_scene_npc_create",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_task_info_update"
    accepted = codec.decode_message("c_task_info_update", reply_body)
    assert accepted["action_type"] == 1
    assert accepted["task_info"]["Id"] == STARTER_TASK.id
    assert accepted["task_info"]["Status"] == TASK_STATUS_ACCEPTED
    assert codec.decode_message("c_scene_npc_create", replies[1][1]) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in TUTORIAL_MAP_SPAWNS]
    }

    writer.data.clear()
    session.outbound = RollingXor(0x7A8B9CAD)
    repeated_accept = codec.encode_message(
        "s_task_accept", {"task_id": STARTER_TASK.id}
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_task_accept"],
        repeated_accept,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x7A8B9CAD))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_task_info_update"
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x8899AABB)
    submit = codec.encode_message("s_task_submit", {"task_id": STARTER_TASK.id})
    await game._dispatch(
        session,
        registry.protocol_ids["s_task_submit"],
        submit,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x8899AABB))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_task_info_update",
        "c_city_level_add_exp",
        "c_city_level_up",
        "c_city_level_info",
        "c_world_task_info",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_task_info_update"
    submitted = codec.decode_message("c_task_info_update", reply_body)
    assert submitted["action_type"] == 2
    assert submitted["task_info"]["Status"] == TASK_STATUS_FINISHED

    writer.data.clear()
    session.outbound = RollingXor(0x99AABBCC)
    sync = codec.encode_message(
        "s_task_sync_info",
        {"TaskId": STARTER_TASK.id, "Type": "guide", "ParamList": ["1301"]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_task_sync_info"],
        sync,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x99AABBCC))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_task_sync_info"
    assert codec.decode_message("c_task_sync_info", reply_body) == {
        "TaskId": STARTER_TASK.id,
        "Type": "guide",
        "ParamList": ["1301"],
    }

    writer.data.clear()
    session.outbound = RollingXor(0xAABBCCDD)
    enter_stage = codec.encode_message(
        "s_task_enter_stage",
        {"IsEnter": 1, "x": 12, "y": 34},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_task_enter_stage"],
        enter_stage,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xAABBCCDD))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_task_enter_stage"
    assert codec.decode_message("c_task_enter_stage", reply_body) == {"IsEnter": 1}


async def _run_starter_intro_stage_probe() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    game.intro_stage_enabled = True
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0xCAFE1234),
    )
    enter_stage = codec.encode_message(
        "s_task_enter_stage",
        {"IsEnter": 1, "x": 12, "y": 34},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_task_enter_stage"],
        enter_stage,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0xCAFE1234))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_task_enter_stage",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_task_enter_stage", replies[0][1]) == {
        "IsEnter": 1
    }
    assert codec.decode_message("c_stage_enter", replies[1][1]) == {
        "StageId": STARTER_INTRO_STAGE_ID,
        "StageUid": STARTER_INTRO_STAGE_UID,
        "Level": STARTER_INTRO_STAGE_LEVEL,
        "Time": STARTER_INTRO_STAGE_TIME,
        "Drama": STARTER_INTRO_STAGE_DRAMA,
        "IsReconnect": 0,
        "NeedLagLog": 0,
        "IsRecord": 0,
        "Extra": [],
    }
    fighter = codec.decode_message("c_frame_fighter_data", replies[2][1])
    assert fighter["HeroId"] == STARTER_HERO_ID
    assert fighter["CardUid"] == STARTER_CARD_UID
    assert fighter["Heros"][0]["ShapeId"] == STARTER_SHAPE_ID
    assert fighter["Heros"][0]["CardSkillLevel"] == fight_style_for_character(
        STARTER_CHARACTER
    ).protocol_skill_levels(1)
    assert session.stage.current_stage_id == STARTER_INTRO_STAGE_ID
    assert session.stage.encounter_frames[0]["Info"]["Id"] == 3002


async def _run_stage_lifecycle_packets() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x1234CAFE),
    )
    finish_loading = codec.encode_message("s_stage_finish_loading", {})

    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_finish_loading"],
        finish_loading,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x1234CAFE))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_finish_loading"
    assert codec.decode_message("c_stage_finish_loading", reply_body) == {
        "Uid": 10001
    }
    assert session.stage.finished_loading_count == 1

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1234)
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_report"],
        b"",
        writer,
    )

    assert writer.data == bytearray()
    assert session.stage.reports == [{}]

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1235)
    damage_info = codec.encode_message(
        "s_stage_damage_info",
        {
            "Members": [{"UserUid": 10001, "HurtSum": 6400}],
            "MaxCombo": 21,
            "MvpUserUid": 10001,
            "Reborn": 0,
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_damage_info"],
        damage_info,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0xBEEF1235))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_damage_info"
    assert codec.decode_message("c_stage_damage_info", reply_body) == {}
    assert session.stage.damage_reports[-1]["MaxCombo"] == 21

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1235)
    game.stage_report_response = "complete"
    stage_report = codec.encode_message(
        "s_stage_report",
        {
            "Id": STARTER_INTRO_STAGE_ID,
            "Result": 1,
            "MaxCombo": 18,
            "ComboDmg": 1200,
            "AllDmg": 6100,
            "OnHitNum": 44,
            "SoloBossNum": 1,
            "MonsterNum": [{"MonsterId": 3002, "Amount": 1}],
            "HostageNum": [],
            "ItemNum": [{"ItemId": 1001, "Amount": 2}],
            "EndReport": {
                "RoundTimeUse": 74,
                "SkillLevel": [{"SkillId": 100101, "SkillLevel": 3}],
                "RoundFighterMoveTotal": 52,
                "RoundFighterButtonClickCountATK": 12,
                "RoundFighterButtonClickCount1": 3,
                "RoundFighterDpsTotal": 6900,
                "RoundFighterComboMax": 21,
            },
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_report"],
        stage_report,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0xBEEF1235))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_drop",
        "c_stage_result",
        "c_stage_end_gm",
    ]
    drop = codec.decode_message("c_stage_drop", replies[0][1])
    assert drop["StagePassDrop"] == [
        {"idx": 1, "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Count": 2}
    ]
    assert drop["FirstReward"] == [
        {"idx": 1, "ItemId": LOCAL_STAGE_FIRST_REWARD_ITEM_ID, "Count": 1}
    ]
    result = codec.decode_message("c_stage_result", replies[1][1])
    assert result["StageId"] == STARTER_INTRO_STAGE_ID
    assert result["Result"] == 1
    assert result["Time"] == 74
    assert result["RewardList"] == [{"ItemId": 1001, "count": 2, "extra": []}]
    assert result["StageInfo"][0]["StarList"] == [1, 2, 3]
    assert codec.decode_message("c_stage_end_gm", replies[2][1]) == {"Result": 1}

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1236)
    monster_seed = stage_candidate_by_key(
        "starter_intro_299301"
    ).enemy_spawns[0].to_monster_frame_seed()
    monster_data = codec.encode_message(
        "s_frame_monster_data",
        {"monster_data": [monster_seed]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_frame_monster_data"],
        monster_data,
        writer,
    )

    assert writer.data == bytearray()
    assert session.stage.monster_frames == [monster_seed]

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1237)
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_frame_report"],
        codec.encode_message("s_stage_frame_report", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xBEEF1237))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_frame_report"
    assert codec.decode_message("c_stage_frame_report", reply_body) == {}
    assert session.stage.frame_report_count == 1

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1238)
    play_sync = codec.encode_message(
        "s_stage_play_sync",
        {"SyncData": [{"Key": "combo_window", "Val": 12}]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_play_sync"],
        play_sync,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xBEEF1238))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_play_sync"
    assert codec.decode_message("c_stage_play_sync", reply_body) == {
        "UUid": 10001,
        "SyncData": [{"Key": "combo_window", "Val": 12}],
    }
    assert session.stage.play_sync_reports[-1]["SyncData"] == [
        {"Key": "combo_window", "Val": 12}
    ]

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1239)
    is_back = codec.encode_message(
        "s_stage_is_back",
        {"StageId": STARTER_INTRO_STAGE_ID, "IsBack": 1},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_is_back"],
        is_back,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xBEEF1239))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_is_back"
    assert codec.decode_message("c_stage_is_back", reply_body) == {
        "StageId": STARTER_INTRO_STAGE_ID
    }

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1240)
    leave = codec.encode_message(
        "s_stage_leave",
        {"StageId": STARTER_INTRO_STAGE_ID},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_leave"],
        leave,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0xBEEF1240))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_leave"
    assert codec.decode_message("c_stage_leave", reply_body) == {
        "StageId": STARTER_INTRO_STAGE_ID
    }
    assert session.stage.leave_requests[-1] == STARTER_INTRO_STAGE_ID

    writer.data.clear()
    session.outbound = RollingXor(0xBEEF1241)
    quick_reborn = codec.encode_message(
        "s_stage_quick_reborn",
        {"RebornCount": 2},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_quick_reborn"],
        quick_reborn,
        writer,
    )
    assert writer.data == bytearray()
    assert session.stage.quick_reborn_count == 2


async def _run_stage_enter_encounter_npcs() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(
        os.environ,
        {
            "MHATSH_ROSTER_MODE": "verified",
            "MHATSH_SEND_STAGE_ENCOUNTER_NPCS": "1",
        },
        clear=False,
    ):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x55112232),
    )

    training = codec.encode_message(
        "s_training_enter",
        {"HeroCId": 1041, "StageId": 502601},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_training_enter"],
        training,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55112232))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
        "c_scene_npc_create",
    ]
    npcs = codec.decode_message("c_scene_npc_create", replies[2][1])["NpcList"]
    assert npcs == [
        {
            "Uid": 50260101,
            "Id": 3002,
            "X": 0,
            "Y": 0,
            "Z": 0,
            "Face": 0,
            "Version": 1,
            "ShapeId": 3002,
            "Attach": [],
            "HideStatus": 0,
            "AreaId": 0,
            "StartAnim": "",
            "BTName": "bt_preservation_sludge_boss",
            "ForceShow": 1,
        }
    ]
    assert session.stage.ai_directives[0]["Profile"] == "sludge_boss"


async def _run_requested_stage_enter_packets() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, {"MHATSH_ROSTER_MODE": "verified"}, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x55112233),
    )

    training = codec.encode_message(
        "s_training_enter",
        {"HeroCId": 1041, "StageId": 502601},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_training_enter"],
        training,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55112233))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    stage_enter = codec.decode_message("c_stage_enter", replies[0][1])
    assert stage_enter["StageId"] == 502601
    assert stage_enter["StageUid"] == 5026010001
    fighter = codec.decode_message("c_frame_fighter_data", replies[1][1])
    assert fighter["HeroId"] == 1041
    assert fighter["CardUid"] == session.roster.active_card_uid
    assert fighter["Heros"][0]["ShapeId"] == 1003
    assert session.stage.current_stage_key == "all_might_stage_502601"
    assert session.stage.encounter_frames[0]["Info"]["Id"] == 3002
    assert session.roster is not None
    assert session.roster.active_hero_id == 1041

    writer.data.clear()
    session.outbound = RollingXor(0x55112234)
    pressure = codec.encode_message(
        "s_pressure_stage_enter",
        {"StageId": 777777},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_pressure_stage_enter"],
        pressure,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55112234))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    generated = codec.decode_message("c_stage_enter", replies[0][1])
    assert generated["StageId"] == 777777
    assert generated["StageUid"] == 7777770001
    assert codec.decode_message("c_frame_fighter_data", replies[1][1])[
        "HeroId"
    ] == 1041
    assert session.stage.current_stage_key == "generated_stage_777777"
    assert [frame["Info"]["Id"] for frame in session.stage.encounter_frames] == [
        2202,
        2472,
        3007,
    ]
    assert [frame["Info"]["BTParam"][0] for frame in session.stage.encounter_frames] == [
        "common_atk_01",
        "ranged_shot",
        "nomu_charge",
    ]
    assert game._current_stage_definition(session).key == "generated_stage_777777"

    writer.data.clear()
    session.outbound = RollingXor(0x55112235)
    area_enter = codec.encode_message(
        "s_area_event_enter_stage",
        {"StageId": 21111, "HerosUId": [STARTER_CARD_UID + 1]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_area_event_enter_stage"],
        area_enter,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55112235))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
        "c_area_event_info",
    ]
    area_stage_enter = codec.decode_message("c_stage_enter", replies[0][1])
    assert area_stage_enter["StageId"] == 21111
    assert area_stage_enter["StageUid"] == 211110001
    area_fighter = codec.decode_message("c_frame_fighter_data", replies[1][1])
    assert area_fighter["CardUid"] == STARTER_CARD_UID + 1
    assert session.stage.current_stage_key == "area_event_stage_21111"
    area_info = codec.decode_message("c_area_event_info", replies[2][1])
    assert area_info["StageData"] == {
        "StageId": 21111,
        "PassedTimes": 0,
        "DropCountTimes": 0,
        "Star": 0,
    }
    assert session.roster is not None
    assert session.roster.active_card_uid == STARTER_CARD_UID + 1

    writer.data.clear()
    session.outbound = RollingXor(0x55112237)
    campaign = codec.encode_message(
        "s_campaign_fight",
        {"StageId": 160001, "HeroUid": STARTER_CARD_UID, "Field": 0, "AreaId": 0},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_campaign_fight"],
        campaign,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112237))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 160001
    assert codec.decode_message("c_frame_fighter_data", replies[1][1])[
        "CardUid"
    ] == STARTER_CARD_UID
    assert session.stage.current_stage_key == "main_stage_160001"

    writer.data.clear()
    session.outbound = RollingXor(0x55112238)
    secret = codec.encode_message("s_secret_target_stage", {"stageId": 299301})
    await game._dispatch(
        session,
        registry.protocol_ids["s_secret_target_stage"],
        secret,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112238))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 299301
    assert session.stage.current_stage_key == "starter_intro_299301"

    writer.data.clear()
    session.outbound = RollingXor(0x5511223C)
    new_hero = codec.encode_message(
        "s_new_hero_fight",
        {"StageId": 400101, "ActId": 0},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_new_hero_fight"],
        new_hero,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5511223C))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 400101
    assert session.stage.current_stage_key == "roguelike_stage_400101"

    writer.data.clear()
    session.outbound = RollingXor(0x5511223D)
    relax = codec.encode_message("s_relax_stage_choose", {"StageId": 502601})
    await game._dispatch(
        session,
        registry.protocol_ids["s_relax_stage_choose"],
        relax,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5511223D))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 502601
    assert session.stage.current_stage_key == "all_might_stage_502601"

    writer.data.clear()
    session.outbound = RollingXor(0x5511223E)
    allsvr = codec.encode_message(
        "s_act_allsvr_stage_enter",
        {"ActId": 51, "LevelId": 880101, "Cid": 1041},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_allsvr_stage_enter"],
        allsvr,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5511223E))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_act_allsvr_stage_update_level",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    allsvr_update = codec.decode_message(
        "c_act_allsvr_stage_update_level", replies[0][1]
    )
    assert allsvr_update["ActId"] == 51
    assert allsvr_update["AreaInfo"]["Id"] == 1
    assert allsvr_update["AreaInfo"]["LevelList"][0] == {"Id": 880101, "Count": 1}
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 880101
    assert session.stage.current_stage_key == "allsvr_stage_880101"

    writer.data.clear()
    session.outbound = RollingXor(0x5511223F)
    allsvr_boss = codec.encode_message(
        "s_act_allsvr_stage_boss",
        {"ActId": 51, "BossId": 3, "Diffcult": 3, "Cid": 1041, "BuffList": []},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_allsvr_stage_boss"],
        allsvr_boss,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5511223F))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_act_allsvr_stage_update_boss",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    allsvr_boss_update = codec.decode_message(
        "c_act_allsvr_stage_update_boss", replies[0][1]
    )
    assert allsvr_boss_update["BossInfo"]["Id"] == 3
    assert allsvr_boss_update["BossInfo"]["Score"] == 100
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 880312
    assert session.stage.current_stage_key == "allsvr_boss_stage_880312"

    writer.data.clear()
    session.outbound = RollingXor(0x55112246)
    boss_join = codec.encode_message(
        "s_act_boss_challenge_join",
        {"HeroUid": STARTER_CARD_UID + 4},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_boss_challenge_join"],
        boss_join,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112246))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
        "c_act_boss_challenge_server_ach",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 880110
    assert codec.decode_message("c_frame_fighter_data", replies[1][1])[
        "CardUid"
    ] == STARTER_CARD_UID + 4
    assert codec.decode_message(
        "c_act_boss_challenge_server_ach", replies[2][1]
    ) == {"AchList": []}
    assert session.stage.current_stage_key == "allsvr_boss_stage_880110"

    writer.data.clear()
    session.outbound = RollingXor(0x55112247)
    boss_over = codec.encode_message(
        "s_act_boss_challenge_over",
        {"Damage": 45678},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_boss_challenge_over"],
        boss_over,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112247))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_act_boss_challenge_over",
        "c_act_boss_challenge_svr_point",
        "c_act_boss_challenge_server_ach",
    ]
    assert codec.decode_message("c_act_boss_challenge_over", replies[0][1]) == {
        "JoinTimes": 1,
        "Damage": 45678,
        "TotalDamage": 45678,
        "Point": 456,
        "TotalPoint": 456,
    }
    assert codec.decode_message("c_act_boss_challenge_svr_point", replies[1][1]) == {
        "TotalPoint": 456
    }
    assert codec.decode_message(
        "c_act_boss_challenge_server_ach", replies[2][1]
    ) == {"AchList": [100]}

    writer.data.clear()
    session.outbound = RollingXor(0x55112248)
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_boss_challenge_svr_ach_reward"],
        codec.encode_message(
            "s_act_boss_challenge_svr_ach_reward",
            {"AchId": 100},
        ),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112248))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_act_boss_challenge_svr_ach_reward"
    assert codec.decode_message(
        "c_act_boss_challenge_svr_ach_reward", reply_body
    ) == {"AchId": 100}

    writer.data.clear()
    session.outbound = RollingXor(0x55112249)
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_boss_challenge_rejoin"],
        codec.encode_message("s_act_boss_challenge_rejoin", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112249))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 880110
    assert codec.decode_message("c_frame_fighter_data", replies[1][1])[
        "CardUid"
    ] == STARTER_CARD_UID + 4

    writer.data.clear()
    session.outbound = RollingXor(0x55112240)
    empty_shop = codec.encode_message(
        "s_act_empty_shop_stage_enter",
        {"StageIndex": 1, "HeroUid": STARTER_CARD_UID},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_empty_shop_stage_enter"],
        empty_shop,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112240))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_act_empty_shop_info",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    empty_shop_info = codec.decode_message("c_act_empty_shop_info", replies[0][1])
    assert empty_shop_info == {"ActId": 0, "MaxPassStage": 1}
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 9001001
    assert codec.decode_message("c_frame_fighter_data", replies[2][1])[
        "CardUid"
    ] == STARTER_CARD_UID
    assert session.stage.current_stage_key == "empty_shop_stage_9001001"

    writer.data.clear()
    session.outbound = RollingXor(0x55112241)
    empty_shop_reenter = codec.encode_message(
        "s_act_empty_shop_stage_reenter",
        {"StageIndex": 2, "HeroUid": STARTER_CARD_UID},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_empty_shop_stage_reenter"],
        empty_shop_reenter,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112241))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_act_empty_shop_info",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_act_empty_shop_info", replies[0][1]) == {
        "ActId": 0,
        "MaxPassStage": 2,
    }
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 9002001
    assert session.stage.current_stage_key == "empty_shop_stage_9002001"

    writer.data.clear()
    session.outbound = RollingXor(0x55112239)
    pressure_hero = codec.encode_message(
        "s_pressure_hero_fight",
        {"StageId": 777778, "HeroUid": STARTER_CARD_UID},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_pressure_hero_fight"],
        pressure_hero,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112239))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_pressure_hero_fight",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_pressure_hero_fight", replies[0][1]) == {
        "HeroUid": STARTER_CARD_UID
    }
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 777778
    assert codec.decode_message("c_frame_fighter_data", replies[2][1])[
        "CardUid"
    ] == STARTER_CARD_UID

    writer.data.clear()
    session.outbound = RollingXor(0x5511223A)
    night = codec.encode_message(
        "s_night_fight_enter_stage",
        {"StageId": 160001, "Lineup": [STARTER_CARD_UID + 2]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_night_fight_enter_stage"],
        night,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5511223A))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_night_fight_cache_stage_id",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_night_fight_cache_stage_id", replies[0][1]) == {
        "CacheStageId": 160001
    }
    assert codec.decode_message("c_frame_fighter_data", replies[2][1])[
        "CardUid"
    ] == STARTER_CARD_UID + 2

    writer.data.clear()
    session.outbound = RollingXor(0x55112242)
    await game._dispatch(
        session,
        registry.protocol_ids["s_night_fight_info"],
        codec.encode_message("s_night_fight_info", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112242))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_night_fight_info",
        "c_night_fight_hero_lineup",
        "c_night_fight_sync_status",
    ]
    night_info = codec.decode_message("c_night_fight_info", replies[0][1])
    assert {
        entry["NightFightId"]
        for entry in night_info["StageInfo"]
    }.issuperset({160001, 299301, 502601})
    night_lineup = codec.decode_message("c_night_fight_hero_lineup", replies[1][1])
    assert night_lineup["HeroLineup"][:3] == [
        STARTER_CARD_UID,
        STARTER_CARD_UID + 1,
        STARTER_CARD_UID + 2,
    ]
    assert len(night_lineup["HeroLineup"]) == len(VERIFIED_PLAYABLE_ROSTER)
    night_status = codec.decode_message("c_night_fight_sync_status", replies[2][1])
    assert night_status["StageId"] == 160001
    assert night_status["HeroStatus"][2] == {
        "HeroUid": STARTER_CARD_UID + 2,
        "TiredValue": 0,
    }

    writer.data.clear()
    session.outbound = RollingXor(0x55112243)
    night_enter_fight = codec.encode_message(
        "s_night_fight_enter_fight",
        {"StageId": 563903, "HeroUid": STARTER_CARD_UID + 3},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_night_fight_enter_fight"],
        night_enter_fight,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112243))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_night_fight_hero_lineup",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_night_fight_hero_lineup", replies[0][1]) == {
        "HeroLineup": [STARTER_CARD_UID + 3]
    }
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 563903
    assert session.stage.current_stage_key == "stage_cfg_route_563903"
    assert codec.decode_message("c_frame_fighter_data", replies[2][1])[
        "CardUid"
    ] == STARTER_CARD_UID + 3

    writer.data.clear()
    session.outbound = RollingXor(0x55112244)
    night_over = codec.encode_message(
        "s_night_fight_fight_over",
        {"StageId": 563903, "IsWin": 1},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_night_fight_fight_over"],
        night_over,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112244))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_night_fight_fight_over",
        "c_night_fight_reward",
        "c_night_fight_sync_status",
    ]
    assert codec.decode_message("c_night_fight_fight_over", replies[0][1]) == {
        "StageId": 563903,
        "IsWin": 1,
    }
    assert codec.decode_message("c_night_fight_reward", replies[1][1]) == {
        "FixedReward": [
            {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "count": 1, "extra": []}
        ],
        "ExtraReward": [],
        "SpecialReward": [],
    }
    night_status = codec.decode_message("c_night_fight_sync_status", replies[2][1])
    assert {
        stage["StageId"]: stage["StageStatus"]
        for stage in night_status["StageList"]
    }[563903] == 1
    assert {
        hero["HeroUid"]: hero["TiredValue"]
        for hero in night_status["HeroStatus"]
    }[STARTER_CARD_UID + 3] == 5
    assert session.stage.completions[563903].pass_count == 1
    assert game.profile_store.normal_item_list(session.urs) == [
        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Amount": 1}
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x55112245)
    await game._dispatch(
        session,
        registry.protocol_ids["s_night_fight_leave_stage"],
        codec.encode_message("s_night_fight_leave_stage", {"LeaveType": 1}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55112245))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_night_fight_sync_status"
    assert codec.decode_message("c_night_fight_sync_status", reply_body)[
        "StageId"
    ] == 563903

    writer.data.clear()
    session.outbound = RollingXor(0x5511223B)
    rogue = codec.encode_message(
        "s_rogue_endless_fight",
        {"HeroIndex": 1, "Index": 24},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_rogue_endless_fight"],
        rogue,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5511223B))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_rogue_endless_fight",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_rogue_endless_fight", replies[0][1]) == {
        "HeroIndex": 1,
        "Index": 24,
    }
    assert codec.decode_message("c_stage_enter", replies[1][1])["StageId"] == 400119
    assert session.stage.current_stage_key == "roguelike_stage_400119"

    writer.data.clear()
    session.outbound = RollingXor(0x55112236)
    area_over = codec.encode_message(
        "s_area_event_fight_over",
        {"StageId": 21111, "IsWin": 1, "UseTime": 12},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_area_event_fight_over"],
        area_over,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55112236))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_area_event_stage_pass",
        "c_area_event_info",
    ]
    stage_pass = codec.decode_message("c_area_event_stage_pass", replies[0][1])
    assert stage_pass == {
        "Star": [1, 2, 3],
        "FirstPass": 1,
        "FirstPassPrize": [],
        "ImportantPrize": [],
    }
    area_info = codec.decode_message("c_area_event_info", replies[1][1])
    assert area_info["StageData"] == {
        "StageId": 21111,
        "PassedTimes": 1,
        "DropCountTimes": 0,
        "Star": 3,
    }
    assert session.stage.completions[21111].pass_count == 1


async def _run_verified_roster_stage_entry_payloads() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, {"MHATSH_ROSTER_MODE": "verified"}, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x66110000),
    )

    for index, character in enumerate(VERIFIED_PLAYABLE_ROSTER):
        assert character.hero_id is not None
        assert character.shape_id is not None
        writer.data.clear()
        xor_seed = 0x66110000 + index + 1
        session.outbound = RollingXor(xor_seed)
        request = codec.encode_message(
            "s_training_enter",
            {"HeroCId": character.hero_id, "StageId": 502601},
        )

        await game._dispatch(
            session,
            registry.protocol_ids["s_training_enter"],
            request,
            writer,
        )

        decoder = FrameDecoder(RollingXor(xor_seed))
        replies = decoder.feed(bytes(writer.data))
        assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
            "c_stage_enter",
            "c_frame_fighter_data",
        ]
        stage_enter = codec.decode_message("c_stage_enter", replies[0][1])
        assert stage_enter["StageId"] == 502601
        fighter = codec.decode_message("c_frame_fighter_data", replies[1][1])
        assert fighter["HeroId"] == character.hero_id
        assert fighter["CardUid"] == session.roster.active_card_uid
        assert fighter["Heros"][0]["HeroId"] == character.hero_id
        assert fighter["Heros"][0]["ShapeId"] == character.shape_id
        assert fighter["Heros"][0]["CardSkillLevel"] == fight_style_for_character(
            character
        ).protocol_skill_levels(session.roster.hero_level)
        assert session.stage.current_stage_key == "all_might_stage_502601"
        assert session.roster.active_card.character == character


async def _run_stage_family_info_packets() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x66001122),
        uid=4242,
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_resource_stage_info"],
        codec.encode_message("s_resource_stage_info", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001122))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_resource_stage_info"
    resource_info = codec.decode_message("c_resource_stage_info", reply_body)
    assert resource_info == {
        "Progress": [],
        "HeroUid": STARTER_CARD_UID,
        "PassStage": [],
        "Chances": [
            {"Type": 1, "Chances": 3},
            {"Type": 2, "Chances": 3},
            {"Type": 3, "Chances": 3},
        ],
    }

    writer.data.clear()
    session.outbound = RollingXor(0x66001123)
    pressure_detail = codec.encode_message(
        "s_pressure_stage_detail",
        {"StageId": 777777},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_pressure_stage_detail"],
        pressure_detail,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001123))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_pressure_stage_detail"
    detail = codec.decode_message("c_pressure_stage_detail", reply_body)
    assert detail["StageId"] == 777777
    assert detail["StageScore"] == 0
    assert detail["Count"] == 3
    assert detail["HeroList"][0]["HeroId"] == STARTER_HERO_ID

    writer.data.clear()
    session.outbound = RollingXor(0x66001124)
    pressure_finish = codec.encode_message(
        "s_pressure_stage_finish",
        {
            "StageId": 777777,
            "HeroUid": STARTER_CARD_UID,
            "Score": 12345,
            "ScoreDetails": [10000, 2000, 345],
            "Save": 1,
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_pressure_stage_finish"],
        pressure_finish,
        writer,
    )
    assert writer.data == bytearray()

    writer.data.clear()
    session.outbound = RollingXor(0x66001125)
    await game._dispatch(
        session,
        registry.protocol_ids["s_pressure_stage_detail"],
        pressure_detail,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001125))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    detail = codec.decode_message("c_pressure_stage_detail", reply_body)
    assert detail["StageScore"] == 12345
    assert detail["TotalScore"] == 12345
    assert detail["TopList"] == [
        {"Rank": 1, "Number": [12345], "String": ["Local Hero"]}
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x6600112A)
    hero_rank_end = codec.encode_message(
        "s_hero_rank_stage_end",
        {"Id": 160001, "Star": [1, 3]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_hero_rank_stage_end"],
        hero_rank_end,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112A))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_hero_rank_stage_update"
    assert codec.decode_message("c_hero_rank_stage_update", reply_body) == {
        "Id": 160001,
        "Star": [1, 3],
    }
    assert session.stage.hero_rank_stage_info()["StageList"] == [
        {"Id": 160001, "Star": [1, 3]}
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x6600112B)
    stage_bonus = codec.encode_message(
        "s_stage_bonus",
        {
            "StageUid": 1600010001,
            "StageId": 160001,
            "Result": 1,
            "StarList": [1, 2, 3],
            "TotalTime": 70,
            "PuaseTime": 0,
            "DramaFinish": [],
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_bonus"],
        stage_bonus,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112B))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_show_reward"
    assert codec.decode_message("c_stage_show_reward", reply_body) == {
        "RewardList": [
            {
                "ItemId": LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID,
                "count": 3,
                "extra": [],
            }
        ]
    }
    assert session.stage.completions[160001].stars == (1, 2, 3)

    writer.data.clear()
    session.outbound = RollingXor(0x6600112C)
    await game._dispatch(
        session,
        registry.protocol_ids["s_stage_extra_reward"],
        codec.encode_message("s_stage_extra_reward", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112C))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_stage_extra_reward"
    assert codec.decode_message("c_stage_extra_reward", reply_body) == {
        "UserUid": 4242,
        "DrawItems": [
            {"ItemId": LOCAL_STAGE_STYLE_REWARD_ITEM_ID, "Num": 1}
        ],
    }
    assert game.profile_store.normal_item_list(session.urs) == [
        {"ItemId": LOCAL_STAGE_FULL_CLEAR_REWARD_ITEM_ID, "Amount": 3},
        {"ItemId": LOCAL_STAGE_STYLE_REWARD_ITEM_ID, "Amount": 1},
    ]

    writer.data.clear()
    session.outbound = RollingXor(0x66001126)
    usj_record = codec.encode_message(
        "s_usj_get_stage_record",
        {"ZoneId": 1, "PointId": 777777},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_usj_get_stage_record"],
        usj_record,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001126))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_usj_get_stage_record"
    assert codec.decode_message("c_usj_get_stage_record", reply_body)[
        "StageRecords"
    ][0]["Score"] == 12345

    session.stage.enter_stage(777777, stage_uid=7777770001)
    writer.data.clear()
    session.outbound = RollingXor(0x66001127)
    usj_end = codec.encode_message(
        "s_usj_end_stage",
        {
            "EndType": 1,
            "Reason": 0,
            "HeroUid": STARTER_CARD_UID,
            "HpPercent": 80,
            "BeHitTimes": 1,
            "HurtSum": 5000,
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_usj_end_stage"],
        usj_end,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001127))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_usj_end_stage"
    usj_result = codec.decode_message("c_usj_end_stage", reply_body)
    assert usj_result["CurrentPointId"] == 777777
    assert usj_result["CurrentHeroUid"] == STARTER_CARD_UID
    assert usj_result["Score"] == 130
    assert usj_result["HightestScore"] == 12345

    writer.data.clear()
    session.outbound = RollingXor(0x66001128)
    daily_report = codec.encode_message(
        "s_act_daily_stage_report",
        {"ActId": 12, "Result": 1, "Count": 4},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_daily_stage_report"],
        daily_report,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001128))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_act_daily_stage_result"
    assert codec.decode_message("c_act_daily_stage_result", reply_body) == {
        "ActId": 12,
        "Count": {
            "Id": 12,
            "Count": 1,
            "Extra": {"NumList": [4], "StrList": []},
        },
        "RewardList": [
            {
                "AddLog": [
                    {
                        "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                        "count": 4,
                        "extra": [],
                    }
                ]
            }
        ],
    }

    writer.data.clear()
    session.outbound = RollingXor(0x66001129)
    daily_choose = codec.encode_message(
        "s_act_daily_stage_choose",
        {"ActId": 88, "StageId": 860001},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_daily_stage_choose"],
        daily_choose,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x66001129))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_act_daily_stage_info"
    daily_info = codec.decode_message("c_act_daily_stage_info", reply_body)
    assert daily_info["ActId"] == 88
    assert len(daily_info["Count"]) == len(ACT_DAILY_STAGES)
    assert daily_info["Count"][0] == {
        "Id": 860001,
        "Count": 0,
        "Extra": {
            "NumList": [860001, 0, 1],
            "StrList": ["daily_stage", ""],
        },
    }

    writer.data.clear()
    session.outbound = RollingXor(0x6600112A)
    herochip_enter = codec.encode_message(
        "s_herochip_stage_enter",
        {"Id": 370101, "HeroUid": STARTER_CARD_UID},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_herochip_stage_enter"],
        herochip_enter,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112A))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_herochip_stage_sync_data",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    herochip_sync = codec.decode_message("c_herochip_stage_sync_data", replies[0][1])
    assert len(herochip_sync["DailyTimes"]) == len(HEROCHIP_STAGES)
    assert herochip_sync["DailyTimes"][0] == {"Id": 370101, "Times": 0}
    assert herochip_sync["PassStage"] == []
    herochip_stage = codec.decode_message("c_stage_enter", replies[1][1])
    assert herochip_stage["StageId"] == 370101
    assert codec.decode_message("c_frame_fighter_data", replies[2][1])[
        "CardUid"
    ] == STARTER_CARD_UID
    assert session.stage.current_stage_key == "herochip_stage_370101"

    writer.data.clear()
    session.outbound = RollingXor(0x6600112B)
    await game._dispatch(
        session,
        registry.protocol_ids["s_usj_cycle_id"],
        codec.encode_message("s_usj_cycle_id", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112B))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_usj_cycle_id"
    assert codec.decode_message("c_usj_cycle_id", reply_body) == {"CycleId": 1}

    writer.data.clear()
    session.outbound = RollingXor(0x6600112C)
    await game._dispatch(
        session,
        registry.protocol_ids["s_usj_enter_activity_ui"],
        codec.encode_message("s_usj_enter_activity_ui", {}),
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112C))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_usj_load"
    usj_load = codec.decode_message("c_usj_load", reply_body)
    assert len(usj_load["HeroList"]) == len(session.roster.cards)
    assert len(usj_load["ZoneList"]) == 3
    assert usj_load["ZoneList"][0]["ZoneId"] == 1001
    assert usj_load["ZoneList"][0]["AccessedPath"] == [
        point.point_id for point in USJ_POINTS[:4]
    ]
    assert usj_load["CurrentHeroUid"] == session.roster.active_card_uid

    writer.data.clear()
    session.outbound = RollingXor(0x6600112D)
    usj_enter = codec.encode_message(
        "s_usj_enter_stage",
        {"ZoneId": 1001, "PointId": 100101, "HeroUid": STARTER_CARD_UID},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_usj_enter_stage"],
        usj_enter,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112D))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_usj_enter_stage",
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_usj_enter_stage", replies[0][1]) == {
        "ZoneId": 1001,
        "PointId": 100101,
        "HeroUid": STARTER_CARD_UID,
    }
    usj_stage_enter = codec.decode_message("c_stage_enter", replies[1][1])
    assert usj_stage_enter["StageId"] == 700101
    assert codec.decode_message("c_frame_fighter_data", replies[2][1])[
        "CardUid"
    ] == STARTER_CARD_UID
    assert session.stage.current_usj_point_id == 100101
    assert session.stage.current_stage_key == "usj_stage_700101"

    writer.data.clear()
    session.outbound = RollingXor(0x6600112E)
    point_reward = codec.encode_message(
        "s_usj_get_point_reward",
        {"ZoneId": 1001, "PointList": [100101]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_usj_get_point_reward"],
        point_reward,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x6600112E))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_usj_get_point_reward"
    assert codec.decode_message("c_usj_get_point_reward", reply_body) == {
        "ZoneId": 1001,
        "RewardList": [
            {
                "PointId": 100101,
                "Reward": [
                    {
                        "ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID,
                        "count": 1,
                        "extra": [],
                    }
                ],
            }
        ],
    }


async def _run_starter_guide_intro_stage_probe() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    game.intro_stage_enabled = True
    game.intro_stage_trigger = "starter_guide"
    game.intro_stage_delay = 0.0
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x3344AABB),
    )
    stat = codec.encode_message(
        "s_client_stat",
        {"StatId": 2, "NumData": [1, 1301, 10011], "StrData": ["", ""]},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_client_stat"],
        stat,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x3344AABB))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_scene_npc_create",
        "c_task_info_update",
        "c_city_level_add_exp",
        "c_city_level_up",
        "c_city_level_info",
        "c_world_task_info",
    ]
    assert session.pending_starter_intro_stage is True

    writer.data.clear()
    session.outbound = RollingXor(0x3344AABC)
    base_station = codec.encode_message(
        "s_base_station_all_info",
        {"iClientVersion": 0},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_base_station_all_info"],
        base_station,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x3344AABC))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_base_station_all_info",
        "c_city_level_info",
        "c_world_task_info",
    ]
    assert session.pending_starter_intro_stage is True

    writer.data.clear()
    session.outbound = RollingXor(0x3344AABD)
    world_map_stat = codec.encode_message(
        "s_client_stat",
        {
            "StatId": 2,
            "NumData": [0, 1404, 10351],
            "StrData": [
                "WorldMapView",
                "map/worldMapViewUI,map/mapTaskListViewUI",
            ],
        },
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_client_stat"],
        world_map_stat,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x3344AABD))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == (
        STARTER_INTRO_STAGE_ID
    )
    assert codec.decode_message("c_frame_fighter_data", replies[1][1])[
        "HeroId"
    ] == STARTER_HERO_ID
    assert session.pending_starter_intro_stage is False

    writer.data.clear()
    session.outbound = RollingXor(0x3344AACC)
    guide_finish = codec.encode_message(
        "s_guide_finish",
        {"setIdList": [9], "guideIdList": [STARTER_GUIDE_ID]},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_guide_finish"],
        guide_finish,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x3344AACC))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_guide_finish"
    ]


async def _run_login_drama_packets() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    game.login_drama_name = "login_intro_drama"
    game.login_drama_loop = 0
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x10203040),
    )

    request = codec.encode_message("s_login_drama", {"StageId": 101})
    await game._dispatch(
        session,
        registry.protocol_ids["s_login_drama"],
        request,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x10203040))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_scene_play_drama"
    assert codec.decode_message("c_scene_play_drama", reply_body) == {
        "DramaName": "login_intro_drama",
        "Loop": 0,
    }
    assert session.tutorial.requested_login_drama_stages == [101]

    finish = codec.encode_message(
        "s_login_drama_finish",
        {"Uid": 10001, "StageId": 101},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_login_drama_finish"],
        finish,
        writer,
    )
    assert session.tutorial.finished_login_drama_stages == {101: 10001}


async def _run_account_info_login_drama_flags() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    game.login_drama_enabled = True
    game.login_drama_flag = 1
    game.login_drama_step = 7
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x90807060),
        urs="intro-user",
    )

    await game._send_account_info(writer, session)

    decoder = FrameDecoder(RollingXor(0x90807060))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_login_account_info"
    values = codec.decode_message("c_login_account_info", reply_body)
    assert values["DramaFlag"] == 1
    assert values["DramaStep"] == 7
    assert values["Uid"] == 10001


async def _run_base_station_info() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    with patch.dict(os.environ, LEGACY_STARTER_ENV, clear=False):
        game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x50607080),
    )
    request = codec.encode_message(
        "s_base_station_all_info",
        {"iClientVersion": 23},
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_base_station_all_info"],
        request,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x50607080))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_base_station_all_info",
        "c_city_level_info",
        "c_world_task_info",
    ]
    assert codec.decode_message("c_base_station_all_info", replies[0][1]) == {
        "iClientVersion": 23,
        "arrFinishAidCount": [],
        "arrBaseStationInfo": [],
    }
    assert codec.decode_message("c_city_level_info", replies[1][1]) == {
        "Level": 1,
        "ClickList": [],
    }
    assert codec.decode_message("c_world_task_info", replies[2][1]) == {
        "FinishList": [],
        "OpenWorldMap": [{"MapId": STARTER_WORLD_MAP_ID}],
        "PrestigeMap": 0,
        "PrestigeTaskStatus": 0,
        "IsFirstRewardSign": 0,
        "RewardBase": 0,
        "ExtraReward": [],
        "IgnoreAutoFinishTips": 0,
    }


def test_world_task_state_tracks_map_compatibility_values() -> None:
    world_tasks = WorldTaskState()
    assert world_tasks.world_task_info()["OpenWorldMap"] == [
        {"MapId": STARTER_WORLD_MAP_ID}
    ]

    assert world_tasks.city_level_click(3) == {"Level": 3}
    assert world_tasks.city_level_info() == {"Level": 1, "ClickList": [3]}
    assert world_tasks.complete_beginner_quest() == [
        ("c_city_level_add_exp", {"Exp": BEGINNER_QUEST_CITY_EXP}),
        ("c_city_level_up", {"Level": BEGINNER_QUEST_CITY_LEVEL}),
        (
            "c_city_level_info",
            {"Level": BEGINNER_QUEST_CITY_LEVEL, "ClickList": [3]},
        ),
        (
            "c_world_task_info",
            {
                "FinishList": [
                    {"Map": STARTER_WORLD_MAP_ID, "Area": 0, "TaskId": 1301}
                ],
                "OpenWorldMap": [{"MapId": STARTER_WORLD_MAP_ID}],
                "PrestigeMap": 0,
                "PrestigeTaskStatus": 0,
                "IsFirstRewardSign": 0,
                "RewardBase": 0,
                "ExtraReward": [],
                "IgnoreAutoFinishTips": 0,
            },
        ),
    ]
    assert world_tasks.complete_beginner_quest() == []
    assert world_tasks.city_level_info() == {
        "Level": BEGINNER_QUEST_CITY_LEVEL,
        "ClickList": [3],
    }
    assert world_tasks.world_task_reward_rate(15) == {"Rate": 15}
    assert world_tasks.ignore_auto_finish_tips_response(7) == {"Flag": 1}
    assert world_tasks.auto_finish_response(1301) == {"IsSuccess": 1}
    assert world_tasks.pick_prestige_response() == {
        "IsSuccess": 1,
        "FixedReward": [],
        "RandomReward": [],
        "RandomItem": 0,
    }
    assert world_tasks.world_task_info()["IgnoreAutoFinishTips"] == 1


def test_world_map_task_requests_receive_compatibility_replies() -> None:
    asyncio.run(_run_world_map_task_requests())


async def _run_world_map_task_requests() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x11335577),
    )

    request_cases = [
        ("s_city_level_click", {"Level": 4}),
        ("s_world_task_reward_rate", {"Rate": 25}),
        ("s_world_task_ignore_auto_finish_tips", {"Flag": 1}),
        ("s_world_task_auto_finish", {"TaskId": 1301}),
        ("s_world_task_pick_prestige", {}),
    ]

    for request_name, request_values in request_cases:
        await game._dispatch(
            session,
            registry.protocol_ids[request_name],
            codec.encode_message(request_name, request_values),
            writer,
        )

    decoder = FrameDecoder(RollingXor(0x11335577))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_city_level_click",
        "c_world_task_reward_rate",
        "c_world_task_ignore_auto_finish_tips",
        "c_world_task_auto_finish",
        "c_world_task_pick_prestige",
    ]
    assert codec.decode_message("c_city_level_click", replies[0][1]) == {"Level": 4}
    assert codec.decode_message("c_world_task_reward_rate", replies[1][1]) == {
        "Rate": 25
    }
    assert codec.decode_message(
        "c_world_task_ignore_auto_finish_tips", replies[2][1]
    ) == {"Flag": 1}
    assert codec.decode_message("c_world_task_auto_finish", replies[3][1]) == {
        "IsSuccess": 1
    }
    assert codec.decode_message("c_world_task_pick_prestige", replies[4][1]) == {
        "IsSuccess": 1,
        "FixedReward": [],
        "RandomReward": [],
        "RandomItem": 0,
    }


def test_activity_and_side_task_requests_receive_empty_state_replies() -> None:
    asyncio.run(_run_activity_and_side_task_requests())


def test_secret_area_requests_receive_recovered_mode_state() -> None:
    asyncio.run(_run_secret_area_requests())


async def _run_secret_area_requests() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x55667788),
    )

    active_key = codec.encode_message("s_secret_area_active_key", {})
    await game._dispatch(
        session,
        registry.protocol_ids["s_secret_area_active_key"],
        active_key,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55667788))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_secret_area_cycle",
        "c_secret_area_times",
        "c_secret_area_key",
        "c_secret_area_all_hero",
        "c_secret_area_players",
        "c_secret_area_history",
        "c_secret_area_cycle_record",
    ]
    assert codec.decode_message("c_secret_area_cycle", replies[0][1]) == {
        "CycleTypeId": 1,
        "SeasonId": 1,
        "CycleId": 1,
        "PersonalityGroupId": 1,
        "EndTime": 4102444800,
    }
    assert codec.decode_message("c_secret_area_times", replies[1][1]) == {
        "DayIncomeTimes": 0,
        "CycleIncomeTimes": 0,
    }
    assert codec.decode_message("c_secret_area_key", replies[2][1]) == {
        "Status": 1,
        "KeyId": 100101,
        "StageId": 100101,
        "LevelRangeId": 1001,
    }
    all_hero = codec.decode_message("c_secret_area_all_hero", replies[3][1])
    assert all_hero["AllHero"][0] == {
        "ClassId": STARTER_HERO_ID,
        "Strength": 100,
        "ReturnTime": 0,
    }
    players = codec.decode_message("c_secret_area_players", replies[4][1])
    assert players["PlayerList"][0]["HeroId"] == STARTER_HERO_ID
    assert codec.decode_message("c_secret_area_history", replies[5][1]) == {
        "HistoryList": []
    }
    assert codec.decode_message("c_secret_area_cycle_record", replies[6][1]) == {
        "PreviousRecord": [],
        "HaveRecord": 0,
        "CurrentRecord": [],
    }

    writer.data.clear()
    session.outbound = RollingXor(0x55667789)
    target_stage = codec.encode_message("s_secret_target_stage", {"stageId": 100101})
    await game._dispatch(
        session,
        registry.protocol_ids["s_secret_target_stage"],
        target_stage,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x55667789))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_enter",
        "c_frame_fighter_data",
    ]
    assert codec.decode_message("c_stage_enter", replies[0][1])["StageId"] == 100101
    assert session.stage.current_stage_key == "secret_area_stage_100101"

    writer.data.clear()
    session.outbound = RollingXor(0x5566778A)
    finish_stage = codec.encode_message(
        "s_secret_area_finish_stage",
        {"Members": [{"UserUid": 10001, "HurtSum": 12345}], "MvpUserUid": 10001},
    )
    await game._dispatch(
        session,
        registry.protocol_ids["s_secret_area_finish_stage"],
        finish_stage,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5566778A))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_secret_area_stage_finish",
        "c_secret_area_history_add",
    ]
    finish = codec.decode_message("c_secret_area_stage_finish", replies[0][1])
    assert finish["Members"][0]["DrawItems"] == [
        {"ItemId": LOCAL_STAGE_PASS_REWARD_ITEM_ID, "Num": 1}
    ]
    assert finish["KeyId"] == 100101
    assert finish["StageLevel"] == 1
    assert codec.decode_message("c_secret_area_history_add", replies[1][1])[
        "History"
    ]["StageHierarchy"] == 1

    writer.data.clear()
    session.outbound = RollingXor(0x5566778B)
    record_list = codec.encode_message("s_act_secret_record_list", {"ActId": 9})
    await game._dispatch(
        session,
        registry.protocol_ids["s_act_secret_record_list"],
        record_list,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x5566778B))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_act_secret_record_list"
    records = codec.decode_message("c_act_secret_record_list", reply_body)
    assert records["ActId"] == 9
    assert records["RecordList"][0]["StageGroupId"] == 11001
    assert records["RecordList"][0]["Floor"] == 1


async def _run_activity_and_side_task_requests() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x22446688),
    )

    request_cases = [
        ("s_stage_activity_info", {}),
        ("s_relax_stage_get_box", {}),
        ("s_relax_cond_get_reward", {"Type": 1, "Id": 400301}),
        ("s_activity_shop_info", {"ActType": 17}),
        ("s_entrust_task_list", {}),
        ("s_secret_area_task", {}),
        ("s_usj_task", {}),
        ("s_offlinepvp_task", {}),
        ("s_battlefield_task_info", {}),
        ("s_group_open_map", {}),
        ("s_theater_open", {}),
        ("s_theater_unlock", {"StageId": 880101}),
        ("s_theater_bonus", {"CfgType": 1, "BonusIdx": 2}),
        ("s_theater_chapterbonus", {"chapterid": 1, "starIdx": 3}),
        (
            "s_stage_theater",
            {
                "StageId": 880101,
                "Extra": {"HeroUid": STARTER_CARD_UID},
                "Result": 1,
                "Score": [3, 2, 1],
                "DramaFinish": [],
            },
        ),
    ]

    for request_name, request_values in request_cases:
        await game._dispatch(
            session,
            registry.protocol_ids[request_name],
            codec.encode_message(request_name, request_values),
            writer,
        )

    decoder = FrameDecoder(RollingXor(0x22446688))
    replies = decoder.feed(bytes(writer.data))
    assert [registry.protocol_names[reply_id] for reply_id, _ in replies] == [
        "c_stage_activity_info",
        "c_act_allsvr_stage_info",
        "c_relax_stage_sync_data",
        "c_relax_stage_boxinfo",
        "c_relax_stage_sync_cond",
        "c_activity_shop_info",
        "c_entrust_task_list",
        "c_secret_area_task",
        "c_usj_task",
        "c_offlinepvp_task",
        "c_battlefield_task_info",
        "c_group_open_map",
        "c_theater_open",
        "c_theater_unlock",
        "c_theater_bonus",
        "c_theater_chapterbonus",
        "c_theater_finish",
    ]
    assert codec.decode_message("c_stage_activity_info", replies[0][1]) == {
        "ProgressInfo": []
    }
    allsvr_info = codec.decode_message("c_act_allsvr_stage_info", replies[1][1])
    assert allsvr_info["ActId"] == 0
    assert len(allsvr_info["AreaInfo"]["LevelList"]) == len(ALLSVR_STAGES)
    assert allsvr_info["AreaInfo"]["LevelList"][0] == {"Id": 880101}
    assert allsvr_info["BossInfo"]["Id"] == 1
    relax_sync = codec.decode_message("c_relax_stage_sync_data", replies[2][1])
    assert len(relax_sync["RoundData"]) == len(RELAX_STAGES)
    assert relax_sync["RoundData"][0] == {"Id": 400301, "Status": 0, "Reward": 0}
    assert relax_sync["RoundData"][-1] == {"Id": 400318, "Status": 0, "Reward": 0}
    assert relax_sync["DailyBoxTimes"] == 0
    assert codec.decode_message("c_relax_stage_boxinfo", replies[3][1]) == {
        "BoxInfo": [
            {
                "Uid": 10001,
                "BoxList": [],
                "DailyBoxTimes": 0,
                "TotalBoxTimes": 0,
                "DailyRewardTimes": 0,
                "TotalRewardTimes": 0,
            }
        ]
    }
    assert codec.decode_message("c_relax_stage_sync_cond", replies[4][1]) == {
        "NewData": [{"Type": 1, "Id": 400301, "Status": 0, "Reward": 0}]
    }
    assert codec.decode_message("c_activity_shop_info", replies[5][1]) == {
        "BuyInfo": []
    }
    assert codec.decode_message("c_entrust_task_list", replies[6][1]) == {
        "Version": 1,
        "EntrustTaskData": [],
    }
    assert codec.decode_message("c_secret_area_task", replies[7][1]) == {
        "TaskList": []
    }
    assert codec.decode_message("c_usj_task", replies[8][1]) == {"TaskList": []}
    assert codec.decode_message("c_offlinepvp_task", replies[9][1]) == {
        "TaskList": []
    }
    assert codec.decode_message("c_battlefield_task_info", replies[10][1]) == {
        "IsFightOver": 0,
        "IsGetDayReward": 0,
        "IsGetWeekReward": 0,
        "ReplaceTimes": 0,
        "FreshenTime": 0,
        "Tasks": [],
    }
    assert codec.decode_message("c_group_open_map", replies[11][1]) == {
        "MapAttackArea": []
    }
    theater_open = codec.decode_message("c_theater_open", replies[12][1])
    assert len(theater_open["StageInfo"]) == len(ALLSVR_STAGES)
    assert theater_open["StageInfo"][0]["Id"] == 880101
    assert theater_open["StageInfo"][0]["Status"] == 1
    assert theater_open["UserContri"] == 0
    assert codec.decode_message("c_theater_unlock", replies[13][1]) == {
        "StageId": 880101,
        "Status": 1,
    }
    assert codec.decode_message("c_theater_bonus", replies[14][1]) == {
        "CfgType": 1,
        "BonusIdx": 2,
        "Reward": [{"Id": LOCAL_STAGE_STYLE_REWARD_ITEM_ID, "Amount": 1}],
    }
    assert codec.decode_message("c_theater_chapterbonus", replies[15][1]) == {
        "chapterid": 1,
        "starIdx": 3,
    }
    assert codec.decode_message("c_theater_finish", replies[16][1]) == {
        "newChapterInfo": [{"Id": 1, "Status": 1}],
        "newStageInfo": [{"Id": 880101, "Status": 1}],
    }
    assert session.stage.allsvr_level_counts[880101] == 1
    assert session.activities.requested_activity_types == [17]
    assert session.activities.requested_group_maps == 1


async def _run_time_ping() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x1234ABCD),
    )
    ping = codec.encode_message("s_time_ping", {"SendTime": 59718})

    with patch(
        "mhatsh_server.game_server.asyncio.sleep", new_callable=AsyncMock
    ) as sleep:
        await game._dispatch(
            session,
            registry.protocol_ids["s_time_ping"],
            ping,
            writer,
        )

    sleep.assert_awaited_once_with(0.05)

    decoder = FrameDecoder(RollingXor(0x1234ABCD))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_time_ping"
    response = codec.decode_message("c_time_ping", reply_body)
    assert response["SendTime"] == 59718
    assert response["ServerTime"] > 0


def test_reconnect_restores_identity_and_acknowledges() -> None:
    asyncio.run(_run_reconnect())


async def _run_reconnect() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x55AA55AA),
    )
    reconnect = codec.encode_message(
        "s_login_reconnect",
        {
            "ClientVersion": "553293",
            "PtoVersion": -1042211873,
            "VerifyStr": "{}",
            "CheckStr": "local-check",
            "Urs": "local-guest",
            "Uid": 10001,
        },
    )

    await game._dispatch(
        session,
        registry.protocol_ids["s_login_reconnect"],
        reconnect,
        writer,
    )

    decoder = FrameDecoder(RollingXor(0x55AA55AA))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_reconnect_flag"
    assert codec.decode_message("c_reconnect_flag", reply_body) == {"Falg": 1}
    assert session.urs == "local-guest"
    assert session.uid == 10001


def test_account_info_can_auto_provision_minimal_role() -> None:
    asyncio.run(_run_auto_provision())


async def _run_auto_provision() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
    game = GameServer(registry)
    writer = BufferWriter()
    session = Session(
        seed=1,
        decoder=FrameDecoder(None),
        outbound=RollingXor(0x11223344),
        urs="existing-user",
    )

    await game._send_account_info(writer, session)

    decoder = FrameDecoder(RollingXor(0x11223344))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_login_account_info"
    assert codec.decode_message("c_login_account_info", reply_body) == {
        "URS": "existing-user",
        "Uid": 10001,
        "DramaFlag": 0,
        "DramaStep": 0,
        "RoleList": [{"Uid": 10001}],
        "IsNewAccount": 0,
    }
    assert game.roles == {"existing-user": 10001}


class BufferWriter:
    def __init__(self) -> None:
        self.data = bytearray()

    def write(self, data: bytes) -> None:
        self.data.extend(data)

    async def drain(self) -> None:
        pass


async def _read_frame(
    reader: asyncio.StreamReader, decoder: FrameDecoder
) -> tuple[int, bytes]:
    while True:
        frames = decoder.feed(await reader.read(4096))
        if frames:
            return frames[0]
