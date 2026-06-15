from __future__ import annotations

import asyncio
import struct
from pathlib import Path
from unittest.mock import AsyncMock, patch

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
    INITIAL_MAP_SPAWNS,
    INITIAL_PLAYABLE_ROSTER,
    MAP_CHARACTERS,
    PLAYABLE_CHARACTERS,
    STARTER_CHARACTER,
    VERIFIED_PLAYABLE_ROSTER,
    playable_card,
    playable_roster,
    scene_npc,
    scene_npc_from_spawn,
)
from mhatsh_server.protocol import FrameDecoder, ProtocolCodec, RollingXor, encode_frame
from mhatsh_server.schema import SchemaRegistry


ROOT = Path(__file__).resolve().parents[2]


def test_starter_identity_matches_archived_midoriya_config() -> None:
    assert STARTER_HERO_ID == 1011
    assert STARTER_SHAPE_ID == 1001


def test_axmd_catalog_keeps_asset_ids_separate_from_protocol_ids() -> None:
    assert "AXMD raw-rip" in CATALOG_SOURCE
    assert len(PLAYABLE_CHARACTERS) == 31
    assert len(MAP_CHARACTERS) == 40
    assert len(CHIBI_MODEL_ASSETS) == 3
    assert STARTER_CHARACTER == PLAYABLE_CHARACTERS["h1001"]
    assert STARTER_CHARACTER.hero_id == 1011
    assert STARTER_CHARACTER.shape_id == 1001
    assert sum(
        character.is_protocol_verified
        for character in PLAYABLE_CHARACTERS.values()
    ) == 29
    assert PLAYABLE_CHARACTERS["h1032"].name == "Mirio Togata"
    assert PLAYABLE_CHARACTERS["h1032"].hero_id == 1321
    assert PLAYABLE_CHARACTERS["h1110"].shape_id == 1011
    assert PLAYABLE_CHARACTERS["h1998"].name == "All Might (Variant)"
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


def test_initial_map_spawn_catalog_tracks_verified_npc_rows() -> None:
    assert INITIAL_MAP_SPAWNS == (DEATH_ARMS_DEMO_SPAWN,)
    assert DEATH_ARMS_DEMO_SPAWN.label == "death_arms_demo_near_honei_spawn"
    assert DEATH_ARMS_DEMO_SPAWN.character == DEATH_ARMS
    assert DEATH_ARMS_DEMO_SPAWN.uid == 20001
    assert DEATH_ARMS_DEMO_SPAWN.face == 180
    assert not DEATH_ARMS_DEMO_SPAWN.is_authored_placement


def test_roster_modes_keep_starter_default_and_verified_opt_in() -> None:
    assert playable_roster() == INITIAL_PLAYABLE_ROSTER
    assert playable_roster("starter") == INITIAL_PLAYABLE_ROSTER
    assert playable_roster("expanded") == VERIFIED_PLAYABLE_ROSTER
    assert playable_roster("verified") == VERIFIED_PLAYABLE_ROSTER
    assert len(VERIFIED_PLAYABLE_ROSTER) == 29
    assert {character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER} == {
        model_id
        for model_id, character in PLAYABLE_CHARACTERS.items()
        if character.is_protocol_verified
    }
    assert "h1039" not in {
        character.model_asset_id for character in VERIFIED_PLAYABLE_ROSTER
    }
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
            playable_card(character, STARTER_CARD_UID + index)
            for index, character in enumerate(INITIAL_PLAYABLE_ROSTER)
        ],
    }
    reply_id, reply_body = replies[3]
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
    reply_id, reply_body = replies[4]
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
    reply_id, reply_body = replies[5]
    assert codec.decode_message("c_scene_npc_create", reply_body) == {
        "NpcList": [scene_npc_from_spawn(spawn) for spawn in INITIAL_MAP_SPAWNS]
    }
    reply_id, reply_body = replies[6]
    assert codec.decode_message("c_data_merge_to", reply_body) == {
        "str": "c_login_ok"
    }
    assert game.roles == {"test-user": 4242}


def test_expanded_roster_mode_serializes_all_verified_playable_cards() -> None:
    asyncio.run(_run_expanded_roster_cards())


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
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_card_seeinfo"
    card_info = codec.decode_message("c_card_seeinfo", reply_body)["CardInfo"]
    assert card_info == [
        playable_card(character, STARTER_CARD_UID + index)
        for index, character in enumerate(VERIFIED_PLAYABLE_ROSTER)
    ]
    assert len(card_info) == 29
    assert card_info[0]["HeroId"] == STARTER_HERO_ID
    assert card_info[0]["ShapeId"] == STARTER_SHAPE_ID


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
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_guide_finish"
    assert codec.decode_message("c_guide_finish", reply_body) == {
        "Sets": [9],
        "Ids": [1301],
    }


def test_base_station_info_preserves_client_version() -> None:
    asyncio.run(_run_base_station_info())


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
    [(reply_id, reply_body)] = decoder.feed(bytes(writer.data))
    assert registry.protocol_names[reply_id] == "c_base_station_all_info"
    assert codec.decode_message("c_base_station_all_info", reply_body) == {
        "iClientVersion": 23,
        "arrFinishAidCount": [],
        "arrBaseStationInfo": [],
    }


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
