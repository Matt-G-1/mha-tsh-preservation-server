from __future__ import annotations

import asyncio
import struct
from pathlib import Path
from unittest.mock import AsyncMock, patch

from mhatsh_server.activity_state import ActivityState
from mhatsh_server.game_server import (
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
from mhatsh_server.characters import (
    CATALOG_SOURCE,
    CHIBI_MODEL_ASSETS,
    DEATH_ARMS,
    DEATH_ARMS_DEMO_SPAWN,
    DEMO_CAST_MAP_SPAWNS,
    INITIAL_MAP_SPAWNS,
    INITIAL_PLAYABLE_ROSTER,
    MAP_CHARACTERS,
    PLAYABLE_CHARACTERS,
    STARTER_CHARACTER,
    SUPPORT_CHARACTERS,
    TUTORIAL_MAP_SPAWNS,
    VERIFIED_PLAYABLE_ROSTER,
    map_spawns,
    playable_card,
    playable_roster,
    scene_npc,
    scene_npc_from_spawn,
)
from mhatsh_server.protocol import FrameDecoder, ProtocolCodec, RollingXor, encode_frame
from mhatsh_server.schema import SchemaRegistry
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
    STARTER_WORLD_MAP_ID,
    WorldTaskState,
)


ROOT = Path(__file__).resolve().parents[2]


def roster_card(
    character,
    card_uid: int,
    *,
    fighting: int = 0,
) -> dict[str, object]:
    values = playable_card(character, card_uid)
    values["Fighting"] = fighting
    return values


def test_starter_identity_matches_archived_midoriya_config() -> None:
    assert STARTER_HERO_ID == 1011
    assert STARTER_SHAPE_ID == 1001


def test_axmd_catalog_keeps_asset_ids_separate_from_protocol_ids() -> None:
    assert "AXMD raw-rip" in CATALOG_SOURCE
    assert "en_hero_cfg" in CATALOG_SOURCE
    assert len(PLAYABLE_CHARACTERS) == 31
    assert len(SUPPORT_CHARACTERS) == 1
    assert len(MAP_CHARACTERS) == 40
    assert len(CHIBI_MODEL_ASSETS) == 3
    assert SUPPORT_CHARACTERS["h1927"].name == "Best Jeanist"
    assert STARTER_CHARACTER == PLAYABLE_CHARACTERS["h1001"]
    assert STARTER_CHARACTER.hero_id == 1011
    assert STARTER_CHARACTER.shape_id == 1001
    assert sum(
        character.is_protocol_verified
        for character in PLAYABLE_CHARACTERS.values()
    ) == 30
    assert PLAYABLE_CHARACTERS["h1031"].name == "Tamaki Amajiki"
    assert PLAYABLE_CHARACTERS["h1031"].hero_id == 1311
    assert PLAYABLE_CHARACTERS["h1031"].shape_id == 1031
    assert PLAYABLE_CHARACTERS["h1032"].name == "Mirio Togata"
    assert PLAYABLE_CHARACTERS["h1032"].hero_id == 1321
    assert PLAYABLE_CHARACTERS["h1110"].shape_id == 1011
    assert PLAYABLE_CHARACTERS["h1998"].name == "All Might (Art Test Variant)"
    assert PLAYABLE_CHARACTERS["h1998"].shape_id == 9051
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
    assert DEATH_ARMS_DEMO_SPAWN.label == "death_arms_demo_near_honei_spawn"
    assert DEATH_ARMS_DEMO_SPAWN.character == DEATH_ARMS
    assert DEATH_ARMS_DEMO_SPAWN.uid == 20001
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
    assert len(VERIFIED_PLAYABLE_ROSTER) == 30
    assert {character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER} == {
        model_id
        for model_id, character in PLAYABLE_CHARACTERS.items()
        if character.is_protocol_verified
    }
    assert "h1039" not in {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }
    assert "h1927" not in PLAYABLE_CHARACTERS
    assert "h1927" not in {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }


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
    reply_id, reply_body = replies[6]
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
    reply_id, reply_body = replies[7]
    assert codec.decode_message("c_scene_npc_create", reply_body) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in INITIAL_MAP_SPAWNS]
    }
    reply_id, reply_body = replies[8]
    assert codec.decode_message("c_data_merge_to", reply_body) == {
        "str": "c_login_ok"
    }
    assert game.roles == {"test-user": 4242}


def test_expanded_roster_mode_serializes_all_verified_playable_cards() -> None:
    asyncio.run(_run_expanded_roster_cards())


def test_demo_cast_scene_sends_verified_map_character_rows() -> None:
    asyncio.run(_run_demo_cast_scene_sends_verified_map_character_rows())


async def _run_demo_cast_scene_sends_verified_map_character_rows() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
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
        )
        for index, character in enumerate(VERIFIED_PLAYABLE_ROSTER)
    ]
    assert len(card_info) == 30
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


def test_character_roster_requests_are_stateful() -> None:
    asyncio.run(_run_character_roster_requests())


def test_character_menu_requests_return_roster_backed_empty_state() -> None:
    asyncio.run(_run_character_menu_requests())


async def _run_character_roster_requests() -> None:
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
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_go_to_fight"
    assert codec.decode_message("c_card_go_to_fight", reply_body) == {
        "CardUid": STARTER_CARD_UID + 1,
        "IsShow": 1,
    }
    assert session.roster is not None
    assert session.roster.active_hero_id == 1021
    assert session.roster.active_shape_id == 1002

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
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_go_to_bridge_fight"
    assert codec.decode_message("c_card_go_to_bridge_fight", reply_body) == {
        "HeroUid": STARTER_CARD_UID + 2
    }
    assert session.roster.active_hero_id == 1061

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
        "SkillInfoList": [{"HeroUid": STARTER_CARD_UID, "SkillLevelInfo": []}]
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
        for character in INITIAL_PLAYABLE_ROSTER
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
        "Book": [],
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
            for character in INITIAL_PLAYABLE_ROSTER
        ]
    }

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
    training = codec.encode_message("s_training_hero_info", {"HeroId": 0})
    await game._dispatch(
        session,
        registry.protocol_ids["s_training_hero_info"],
        training,
        writer,
    )
    decoder = FrameDecoder(RollingXor(0x11224488))
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_training_hero_info"
    training_info = codec.decode_message("c_training_hero_info", reply_body)
    assert training_info["TrainingData"]["HeroId"] == STARTER_HERO_ID
    assert training_info["TrainingData"]["CardUid"] == STARTER_CARD_UID
    assert training_info["TrainingData"]["CardSkillLevel"] == []

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
            for character in INITIAL_PLAYABLE_ROSTER
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
    task_update = codec.decode_message("c_task_info_update", reply_body)
    assert task_update["task_info"]["Id"] == STARTER_GUIDE_ID
    assert task_update["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert codec.decode_message("c_city_level_add_exp", replies[2][1]) == {
        "Exp": BEGINNER_QUEST_CITY_EXP
    }
    assert codec.decode_message("c_city_level_up", replies[3][1]) == {
        "Level": BEGINNER_QUEST_CITY_LEVEL
    }
    assert codec.decode_message("c_city_level_info", replies[4][1]) == {
        "Level": BEGINNER_QUEST_CITY_LEVEL,
        "ClickList": [],
    }
    assert codec.decode_message("c_world_task_info", replies[5][1])["FinishList"] == [
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
        "Sets": [9, 10],
        "Ids": [1301, 1302],
    }


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


async def _run_client_stat() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
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
        "c_task_info_update",
        "c_city_level_add_exp",
        "c_city_level_up",
        "c_city_level_info",
        "c_world_task_info",
    ]
    reply_id, reply_body = replies[0]
    assert registry.protocol_names[reply_id] == "c_task_info_update"
    task_update = codec.decode_message("c_task_info_update", reply_body)
    assert task_update["task_info"]["Id"] == STARTER_GUIDE_ID
    assert task_update["task_info"]["Status"] == TASK_STATUS_FINISHED
    assert codec.decode_message("c_city_level_add_exp", replies[1][1]) == {
        "Exp": BEGINNER_QUEST_CITY_EXP
    }
    assert codec.decode_message("c_city_level_up", replies[2][1]) == {
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


def test_task_requests_receive_stateful_protocol_responses() -> None:
    asyncio.run(_run_task_requests())


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


async def _run_base_station_info() -> None:
    registry = SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )
    codec = ProtocolCodec(registry)
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
        ("s_activity_shop_info", {"ActType": 17}),
        ("s_entrust_task_list", {}),
        ("s_secret_area_task", {}),
        ("s_usj_task", {}),
        ("s_offlinepvp_task", {}),
        ("s_battlefield_task_info", {}),
        ("s_group_open_map", {}),
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
        "c_activity_shop_info",
        "c_entrust_task_list",
        "c_secret_area_task",
        "c_usj_task",
        "c_offlinepvp_task",
        "c_battlefield_task_info",
        "c_group_open_map",
    ]
    assert codec.decode_message("c_stage_activity_info", replies[0][1]) == {
        "ProgressInfo": []
    }
    assert codec.decode_message("c_activity_shop_info", replies[1][1]) == {
        "BuyInfo": []
    }
    assert codec.decode_message("c_entrust_task_list", replies[2][1]) == {
        "Version": 1,
        "EntrustTaskData": [],
    }
    assert codec.decode_message("c_secret_area_task", replies[3][1]) == {
        "TaskList": []
    }
    assert codec.decode_message("c_usj_task", replies[4][1]) == {"TaskList": []}
    assert codec.decode_message("c_offlinepvp_task", replies[5][1]) == {
        "TaskList": []
    }
    assert codec.decode_message("c_battlefield_task_info", replies[6][1]) == {
        "IsFightOver": 0,
        "IsGetDayReward": 0,
        "IsGetWeekReward": 0,
        "ReplaceTimes": 0,
        "FreshenTime": 0,
        "Tasks": [],
    }
    assert codec.decode_message("c_group_open_map", replies[7][1]) == {
        "MapAttackArea": []
    }
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
