from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import struct
import time
from dataclasses import dataclass, field
from typing import Any

from .activity_state import ActivityState
from .character_menu import CharacterMenuState
from .characters import (
    STARTER_CHARACTER,
    map_spawns,
    playable_roster,
    scene_npc_from_spawn,
)
from .protocol import FrameDecoder, ProtocolCodec, ProtocolError, RollingXor, encode_frame
from .roster import RosterState
from .schema import SchemaRegistry
from .tasks import TaskState
from .tutorial import TutorialState
from .world import WorldState
from .world_tasks import WorldTaskState


LOG = logging.getLogger("mhatsh.game")

STARTER_CARD_UID = 1001
STARTER_HERO_ID = STARTER_CHARACTER.hero_id
STARTER_SHAPE_ID = STARTER_CHARACTER.shape_id
STARTER_SCENE_ID = 1000
STARTER_SCENE_X = 4221
STARTER_SCENE_Y = 19931
STARTER_SCENE_Z = 0
@dataclass(slots=True)
class Session:
    seed: int
    decoder: FrameDecoder
    outbound: RollingXor
    urs: str = "local-account"
    uid: int = 10001
    account_info_urs: str | None = None
    tutorial: TutorialState = field(default_factory=TutorialState)
    tasks: TaskState = field(default_factory=TaskState)
    world: WorldState = field(default_factory=WorldState)
    world_tasks: WorldTaskState = field(default_factory=WorldTaskState)
    activities: ActivityState = field(default_factory=ActivityState)
    character_menu: CharacterMenuState = field(default_factory=CharacterMenuState)
    roster: RosterState | None = None


class GameServer:
    def __init__(self, registry: SchemaRegistry) -> None:
        self.registry = registry
        self.codec = ProtocolCodec(registry)
        self.roles: dict[str, int] = {}
        self.response_id_bias = int(os.environ.get("MHATSH_RESPONSE_ID_BIAS", "0"))
        self.login_completion = os.environ.get(
            "MHATSH_LOGIN_COMPLETION", "merge"
        ).lower()
        self.merge_target = os.environ.get(
            "MHATSH_MERGE_TARGET", "c_login_ok"
        )
        self.auto_provision_role = os.environ.get(
            "MHATSH_AUTO_PROVISION_ROLE", "1"
        ).lower() not in {"0", "false", "no"}
        self.send_initial_user = os.environ.get(
            "MHATSH_SEND_INITIAL_USER", "1"
        ).lower() not in {"0", "false", "no"}
        self.send_initial_scene = os.environ.get(
            "MHATSH_SEND_INITIAL_SCENE", "1"
        ).lower() not in {"0", "false", "no"}
        self.send_map_characters = os.environ.get(
            "MHATSH_SEND_MAP_CHARACTERS", "1"
        ).lower() not in {"0", "false", "no"}
        self.roster_mode = os.environ.get("MHATSH_ROSTER_MODE", "starter")
        self.map_spawn_mode = os.environ.get("MHATSH_MAP_SPAWN_MODE", "starter")
        self.playable_roster = playable_roster(self.roster_mode)
        self.map_spawns = map_spawns(self.map_spawn_mode)
        self.ping_response_delay = max(
            0.0, float(os.environ.get("MHATSH_PING_RESPONSE_DELAY", "0.05"))
        )

    async def serve(self, host: str, port: int) -> None:
        server = await asyncio.start_server(self.handle_client, host, port)
        addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
        LOG.info("game server listening on %s", addresses)
        async with server:
            await server.serve_forever()

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        peer = writer.get_extra_info("peername")
        seed = secrets.randbits(31) or 1
        session = Session(
            seed=seed,
            decoder=FrameDecoder(RollingXor(seed)),
            outbound=RollingXor(seed ^ 0x6666),
        )
        writer.write(b"\x00" + struct.pack("<I", seed))
        await writer.drain()
        LOG.info("client %s connected; handshake seed=%#010x", peer, seed)

        try:
            while data := await reader.read(65536):
                for protocol_id, body in session.decoder.feed(data):
                    await self._dispatch(session, protocol_id, body, writer)
        except (ConnectionError, ProtocolError) as exc:
            LOG.warning("client %s ended with %s", peer, exc)
        finally:
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), timeout=1)
            except (TimeoutError, ConnectionError, OSError):
                pass
            LOG.info("client %s disconnected", peer)

    async def _dispatch(
        self,
        session: Session,
        protocol_id: int,
        body: bytes,
        writer: asyncio.StreamWriter,
    ) -> None:
        name = self.registry.protocol_names.get(protocol_id, f"unknown_{protocol_id}")
        try:
            values = self.codec.decode_message(name, body)
            rendered = json.dumps(values, ensure_ascii=True, separators=(",", ":"))
        except (KeyError, ProtocolError) as exc:
            values = {}
            rendered = f"<decode failed: {exc}; hex={body.hex()}>"
        LOG.info("recv %d %s %s", protocol_id, name, rendered)

        if name == "s_login_version":
            self._apply_verify_identity(session, values.get("VerifyStr"))
            await self._send(writer, session, "c_login_version", {"server_id": 1})
            # This archived build can report NeedSdk() as false after repackaging,
            # which suppresses its usual s_login_account_enter request.
            await self._send_account_info(writer, session)
        elif name == "s_login_account_enter":
            session.urs = str(values.get("Account") or "local-account")
            await self._send_account_info(writer, session)
        elif name == "s_login_reconnect":
            session.urs = str(values.get("Urs") or session.urs)
            session.uid = int(values.get("Uid") or session.uid)
            await self._send(writer, session, "c_reconnect_flag", {"Falg": 1})
        elif name == "s_login_player_add":
            self.roles[session.urs] = session.uid
            await self._send(
                writer,
                session,
                "c_login_player_info",
                {
                    "Uid": session.uid,
                    "Name": "Local Hero",
                    "Level": 1,
                    "HostId": 1,
                    "ServerName": "Local Preservation Server",
                    "CreateTime": int(time.time()),
                },
            )
        elif name == "s_login_player_enter":
            requested_uid = int(values.get("id") or session.uid)
            self.roles[session.urs] = requested_uid
            session.uid = requested_uid
            await self._send(
                writer,
                session,
                "c_login_checkstr",
                {"CheckStr": "local-check"},
            )
            if self.send_initial_user:
                await self._send_initial_user(writer, session)
                await self._send_initial_cards(writer, session)
            if self.send_initial_scene:
                await self._send_initial_scene(writer, session)
            if self.login_completion == "merge":
                await self._send(
                    writer,
                    session,
                    "c_data_merge_to",
                    {"str": self.merge_target},
                )
        elif name == "s_scene_enter_end":
            await self._send(writer, session, "c_scene_enter_end", {})
        elif name == "s_guide_finish":
            guide_response = session.tutorial.finish_guides(
                list(values.get("setIdList") or []),
                list(values.get("guideIdList") or []),
            )
            await self._send(
                writer,
                session,
                "c_guide_finish",
                guide_response,
            )
            for guide_id in guide_response["Ids"]:
                task_update = session.tasks.complete_guide(int(guide_id))
                if task_update is not None:
                    await self._send(
                        writer,
                        session,
                        "c_task_info_update",
                        task_update,
                    )
        elif name == "s_guide_drama":
            session.tutorial.record_guide_drama(
                int(values.get("Id") or 0),
                int(values.get("Step") or 0),
            )
        elif name == "s_client_stat":
            stat = session.tutorial.record_client_stat(
                int(values.get("StatId") or 0),
                [int(item) for item in list(values.get("NumData") or [])],
                [str(item) for item in list(values.get("StrData") or [])],
            )
            task_update = session.tasks.observe_client_stat(stat)
            if task_update is not None:
                await self._send(
                    writer,
                    session,
                    "c_task_info_update",
                    task_update,
                )
        elif name == "s_teach_finish":
            await self._send(
                writer,
                session,
                "c_teach_finish",
                session.tutorial.finish_teach(
                    int(values.get("HeroCId") or 0),
                    list(values.get("SkillList") or []),
                ),
            )
        elif name == "s_base_station_all_info":
            await self._send(
                writer,
                session,
                "c_base_station_all_info",
                session.tutorial.base_station_all_info(
                    int(values.get("iClientVersion") or 0)
                ),
            )
            await self._send(
                writer,
                session,
                "c_city_level_info",
                session.world_tasks.city_level_info(),
            )
            await self._send(
                writer,
                session,
                "c_world_task_info",
                session.world_tasks.world_task_info(),
            )
        elif name == "s_city_level_click":
            await self._send(
                writer,
                session,
                "c_city_level_click",
                session.world_tasks.city_level_click(int(values.get("Level") or 0)),
            )
        elif name == "s_world_task_reward_rate":
            await self._send(
                writer,
                session,
                "c_world_task_reward_rate",
                session.world_tasks.world_task_reward_rate(
                    int(values.get("Rate") or 0)
                ),
            )
        elif name == "s_world_task_ignore_auto_finish_tips":
            await self._send(
                writer,
                session,
                "c_world_task_ignore_auto_finish_tips",
                session.world_tasks.ignore_auto_finish_tips_response(
                    int(values.get("Flag") or 0)
                ),
            )
        elif name == "s_world_task_auto_finish":
            await self._send(
                writer,
                session,
                "c_world_task_auto_finish",
                session.world_tasks.auto_finish_response(
                    int(values.get("TaskId") or 0)
                ),
            )
        elif name == "s_world_task_pick_prestige":
            await self._send(
                writer,
                session,
                "c_world_task_pick_prestige",
                session.world_tasks.pick_prestige_response(),
            )
        elif name == "s_userinfo_heros":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_userinfo_hero_set",
                {"Heros": roster.hero_set(list(values.get("Cid") or []))},
            )
        elif name == "s_card_go_to_fight":
            roster = self._ensure_roster(session)
            try:
                response = roster.card_fight_response(
                    int(values.get("CardUid") or 0),
                    int(values.get("IsShow") or 0),
                )
            except KeyError:
                response = {
                    "CardUid": roster.active_card_uid,
                    "IsShow": roster.active_show,
                }
            await self._send(writer, session, "c_card_go_to_fight", response)
        elif name == "s_card_go_to_bridge_fight":
            roster = self._ensure_roster(session)
            try:
                response = roster.card_fight_response(
                    int(values.get("HeroUid") or 0),
                    1,
                )
            except KeyError:
                response = {
                    "CardUid": roster.active_card_uid,
                    "IsShow": roster.active_show,
                }
            await self._send(
                writer,
                session,
                "c_card_go_to_bridge_fight",
                {"HeroUid": response["CardUid"]},
            )
        elif name == "s_team_change_hero":
            roster = self._ensure_roster(session)
            try:
                team_response = roster.team_hero_response(
                    session.uid,
                    int(values.get("HeroId") or 0),
                )
            except KeyError:
                team_response = roster.team_hero_response(
                    session.uid,
                    roster.active_hero_id,
                )
            await self._send(writer, session, "c_team_change_hero", team_response)
            await self._send(
                writer,
                session,
                "c_scene_hero_change",
                roster.scene_hero_change(session.uid),
            )
        elif name == "s_team_change_play":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_team_change_play",
                roster.team_play_response(
                    int(values.get("PlayId") or 0),
                    [int(item) for item in list(values.get("Extra") or [])],
                ),
            )
        elif name == "s_area_event_switch_hero":
            roster = self._ensure_roster(session)
            try:
                response = roster.area_event_switch_response(
                    int(values.get("HeroUId") or 0)
                )
            except KeyError:
                response = {"ControlId": roster.active_card_uid}
            await self._send(writer, session, "c_area_event_switch_hero", response)
        elif name == "s_card_show_oper":
            await self._send(
                writer,
                session,
                "c_card_show_oper",
                session.character_menu.card_show_oper(int(values.get("Id") or 0)),
            )
        elif name == "s_card_lock":
            await self._send(
                writer,
                session,
                "c_card_lock",
                session.character_menu.card_lock(
                    int(values.get("Uid") or 0),
                    int(values.get("IsLock") or 0),
                ),
            )
        elif name == "s_card_lock_skill":
            await self._send(
                writer,
                session,
                "c_card_lock_skill",
                session.character_menu.card_lock_skill(
                    int(values.get("HeroCId") or 0),
                    int(values.get("Index") or 0),
                    int(values.get("IsLock") or 0),
                ),
            )
        elif name == "s_skill_get_skill_level_list":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_skill_level_list",
                session.character_menu.skill_level_list(
                    [int(item) for item in list(values.get("HeroUidList") or [])],
                    roster,
                ),
            )
        elif name == "s_skill_get_spec_level_list":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_skill_spec_level_list",
                session.character_menu.spec_level_list(
                    [int(item) for item in list(values.get("HeroUidList") or [])],
                    roster,
                ),
            )
        elif name == "s_hero_rank_info":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_hero_rank_info",
                session.character_menu.hero_rank_info(roster),
            )
        elif name == "s_training_hero_info":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_training_hero_info",
                session.character_menu.training_hero_info(roster),
            )
        elif name == "s_attached_card_book":
            await self._send(
                writer,
                session,
                "c_attached_card_book",
                session.character_menu.attached_card_book(),
            )
        elif name == "s_attached_card_oper":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_attached_card_info",
                session.character_menu.attached_card_info(roster),
            )
        elif name == "s_equip_on":
            await self._send(
                writer,
                session,
                "c_equip_list",
                session.character_menu.equip_list(),
            )
            await self._send(
                writer,
                session,
                "c_equip_attr",
                session.character_menu.equip_attr(int(values.get("EquipUid") or 0)),
            )
        elif name == "s_equip_off":
            await self._send(
                writer,
                session,
                "c_equip_list",
                session.character_menu.equip_list(),
            )
        elif name == "s_equip_lock":
            await self._send(
                writer,
                session,
                "c_equip_attr",
                session.character_menu.equip_attr(int(values.get("EquipUid") or 0)),
            )
        elif name == "s_area_event_hero_list":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_area_event_hero_list",
                session.character_menu.area_event_hero_list(
                    int(values.get("Type") or 0),
                    [int(item) for item in list(values.get("Lineup") or [])],
                    roster,
                ),
            )
        elif name == "s_league_pvp_self_hero_list":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_league_pvp_self_hero_list",
                session.character_menu.league_pvp_self_hero_list(roster),
            )
        elif name == "s_task_get_tasklist_bytype":
            await self._send(
                writer,
                session,
                "c_task_info",
                session.tasks.task_info(int(values.get("task_type") or 0)),
            )
        elif name == "s_task_accept":
            await self._send(
                writer,
                session,
                "c_task_info_update",
                session.tasks.accept(int(values.get("task_id") or 0)),
            )
        elif name == "s_task_submit":
            await self._send(
                writer,
                session,
                "c_task_info_update",
                session.tasks.submit(int(values.get("task_id") or 0)),
            )
        elif name == "s_task_sync_info":
            await self._send(
                writer,
                session,
                "c_task_sync_info",
                session.tasks.sync_info(
                    int(values.get("TaskId") or 0),
                    str(values.get("Type") or ""),
                    list(values.get("ParamList") or []),
                ),
            )
        elif name == "s_task_enter_stage":
            await self._send(
                writer,
                session,
                "c_task_enter_stage",
                session.tasks.enter_stage(int(values.get("IsEnter") or 0)),
            )
        elif name == "s_stage_activity_info":
            await self._send(
                writer,
                session,
                "c_stage_activity_info",
                session.activities.stage_activity_info(),
            )
        elif name == "s_activity_shop_info":
            await self._send(
                writer,
                session,
                "c_activity_shop_info",
                session.activities.activity_shop_info(
                    int(values.get("ActType") or 0)
                ),
            )
        elif name == "s_entrust_task_list":
            await self._send(
                writer,
                session,
                "c_entrust_task_list",
                session.activities.entrust_task_list(),
            )
        elif name == "s_secret_area_task":
            await self._send(
                writer,
                session,
                "c_secret_area_task",
                session.activities.secret_area_task(),
            )
        elif name == "s_usj_task":
            await self._send(
                writer,
                session,
                "c_usj_task",
                session.activities.usj_task(),
            )
        elif name == "s_offlinepvp_task":
            await self._send(
                writer,
                session,
                "c_offlinepvp_task",
                session.activities.offlinepvp_task(),
            )
        elif name == "s_battlefield_task_info":
            await self._send(
                writer,
                session,
                "c_battlefield_task_info",
                session.activities.battlefield_task_info(),
            )
        elif name == "s_group_open_map":
            await self._send(
                writer,
                session,
                "c_group_open_map",
                session.activities.group_open_map(),
            )
        elif name == "s_scene_move":
            session.world.record_move(list(values.get("Path") or []))
        elif name == "s_client_stat_frame":
            session.world.record_frame_stat(
                int(values.get("uid") or 0),
                int(values.get("iStageId") or 0),
                int(values.get("iFrame") or 0),
                int(values.get("iImageLevel") or 0),
            )
        elif name == "s_client_error":
            session.world.record_client_error(str(values.get("Msg") or ""))
        elif name == "s_time_ping":
            # Local replies can beat the archived client's callback setup.
            if self.ping_response_delay:
                await asyncio.sleep(self.ping_response_delay)
            await self._send(
                writer,
                session,
                "c_time_ping",
                {
                    "SendTime": int(values.get("SendTime") or 0),
                    "ServerTime": int(time.time()),
                },
            )

    def _apply_verify_identity(self, session: Session, raw_verify: Any) -> None:
        if not isinstance(raw_verify, str):
            return
        try:
            verify = json.loads(raw_verify)
        except json.JSONDecodeError:
            return
        extra = verify.get("extra")
        if not isinstance(extra, dict):
            return
        account = extra.get("user_id") or extra.get("uid")
        if account:
            session.urs = str(account)

    async def _send_account_info(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        if session.account_info_urs == session.urs:
            return
        role_uid = self.roles.get(session.urs)
        if role_uid is None and self.auto_provision_role:
            role_uid = session.uid
            self.roles[session.urs] = role_uid
        await self._send(
            writer,
            session,
            "c_login_account_info",
            {
                "URS": session.urs,
                "Uid": 0 if role_uid is None else role_uid,
                "DramaFlag": 0,
                "DramaStep": 0,
                "RoleList": [] if role_uid is None else [{"Uid": role_uid}],
                "IsNewAccount": int(role_uid is None),
            },
        )
        session.account_info_urs = session.urs

    async def _send_initial_user(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        roster = self._ensure_roster(session)
        await self._send(
            writer,
            session,
            "c_user_create",
            {
                "user": {
                    "Uid": session.uid,
                    "Name": "Local Hero",
                    "Level": 1,
                    "TopLevel": 0,
                    "Gold": 0,
                    "BindGold": 0,
                    "HeroId": roster.active_hero_id,
                    "CardUid": roster.active_card_uid,
                    "Fighting": 0,
                    "ReNameTimes": 0,
                    "FirstRename": 0,
                    "TotalLoginDays": 1,
                    "PayZoneId": 1,
                    "CreateTime": int(time.time()),
                    "ShowHeroId": roster.active_hero_id,
                },
                "shape": roster.active_shape_id,
                "attach": [],
                "shape_cache_id": 0,
                "version": 1,
                "operator": 0,
                "ShowShapeId": roster.active_shape_id,
                "ShowShapeCacheId": 0,
            },
        )

    async def _send_initial_scene(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        roster = self._ensure_roster(session)
        await self._send(
            writer,
            session,
            "c_scene_player_info",
            {
                "Uid": session.uid,
                "Camp": 0,
                "Name": "Local Hero",
                "Level": 1,
                "TopLevel": 0,
                "ShowHeroId": roster.active_hero_id,
                "LeagueId": 0,
                "LeagueName": "",
                "TitleId": 0,
                "MoodId": 0,
                "Version": 1,
            },
        )
        await self._send(
            writer,
            session,
            "c_scene_enter",
            {
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
            },
        )
        if self.send_map_characters:
            await self._send(
                writer,
                session,
                "c_scene_npc_create",
                {
                    "NpcList": [
                        scene_npc_from_spawn(spawn)
                        for spawn in self.map_spawns
                    ]
                },
            )

    async def _send_initial_cards(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        roster = self._ensure_roster(session)
        await self._send(
            writer,
            session,
            "c_card_seeinfo",
            {
                "Uid": session.uid,
                "CardInfo": roster.card_info(),
            },
        )
        await self._send(
            writer,
            session,
            "c_card_show_info",
            session.character_menu.card_show_info(),
        )
        await self._send(
            writer,
            session,
            "c_card_hero_bio_info",
            session.character_menu.card_hero_bio_info(roster),
        )

    def _ensure_roster(self, session: Session) -> RosterState:
        if session.roster is None:
            session.roster = RosterState(
                self.playable_roster,
                first_card_uid=STARTER_CARD_UID,
            )
        return session.roster

    async def _send(
        self,
        writer: asyncio.StreamWriter,
        session: Session,
        name: str,
        values: dict[str, Any],
    ) -> None:
        protocol_id = self.registry.protocol_ids[name]
        body = self.codec.encode_message(name, values)
        wire_protocol_id = protocol_id + self.response_id_bias
        key_before = session.outbound.key
        plain_frame = encode_frame(wire_protocol_id, body, None)
        encrypted_frame = session.outbound.encrypt(plain_frame)
        writer.write(encrypted_frame)
        await writer.drain()
        LOG.info(
            "sent %d %s %s key=%#010x plain=%s encrypted=%s",
            wire_protocol_id,
            name,
            json.dumps(values),
            key_before,
            plain_frame.hex(),
            encrypted_frame.hex(),
        )
