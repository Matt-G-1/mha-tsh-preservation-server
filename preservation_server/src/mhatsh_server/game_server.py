from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
import struct
import time
from dataclasses import dataclass, field, replace
from typing import Any

from .activity_state import ActivityState
from .beginner_quest import (
    STARTER_MAP_GUIDE_ID,
    STARTER_MAP_GUIDE_SET_ID,
    STARTER_TASK_ID,
)
from .character_menu import CharacterMenuState
from .characters import (
    STARTER_CHARACTER,
    TUTORIAL_MAP_SPAWNS,
    map_spawns,
    playable_roster,
    scene_npc_from_spawn,
)
from .combat import fight_style_for_character
from .profile_store import ProfileStore
from .protocol import FrameDecoder, ProtocolCodec, ProtocolError, RollingXor, encode_frame
from .roguelike_stages import ROGUELIKE_STAGES
from .roster import RosterState
from .schema import SchemaRegistry
from .stages import (
    STARTER_INTRO_STAGE_DRAMA,
    STARTER_INTRO_STAGE_ID,
    STARTER_INTRO_STAGE_LEVEL,
    STARTER_INTRO_STAGE_TIME,
    STARTER_INTRO_STAGE_UID,
    BattleStageDefinition,
    StageState,
    stage_candidate_by_id,
    stage_candidate_by_key,
    stage_candidate_or_generated,
)
from .tasks import TaskState
from .tutorial import TutorialState
from .world import WorldState
from .world_tasks import WorldTaskState
from .world_config_hints import (
    CITY_LEVEL_CAP,
    FUNCTION_OPEN_IDS,
    PLAYER_LEVEL_CAP,
)


LOG = logging.getLogger("mhatsh.game")

STARTER_CARD_UID = 1001
STARTER_HERO_ID = STARTER_CHARACTER.hero_id
STARTER_SHAPE_ID = STARTER_CHARACTER.shape_id
STARTER_SCENE_ID = 1000
STARTER_SCENE_X = 4221
STARTER_SCENE_Y = 19931
STARTER_SCENE_Z = 0

def _env_enabled(name: str, default: str) -> bool:
    return os.environ.get(name, default).lower() not in {"0", "false", "no", "skip"}


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
    stage: StageState = field(default_factory=StageState)
    roster: RosterState | None = None
    pending_starter_intro_stage: bool = False
    profile_configured: bool = False


class GameServer:
    def __init__(self, registry: SchemaRegistry) -> None:
        self.registry = registry
        self.codec = ProtocolCodec(registry)
        self.profile_store = ProfileStore(
            os.environ.get("MHATSH_PROFILE_STORE") or None
        )
        self.roles = self.profile_store.roles
        self.active_cards = self.profile_store.active_cards
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
        self.login_drama_enabled = _env_enabled("MHATSH_LOGIN_DRAMA_MODE", "skip")
        self.login_drama_flag = int(os.environ.get("MHATSH_LOGIN_DRAMA_FLAG", "1"))
        self.login_drama_step = int(os.environ.get("MHATSH_LOGIN_DRAMA_STEP", "0"))
        self.login_drama_name = os.environ.get("MHATSH_LOGIN_DRAMA_NAME", "")
        self.login_drama_loop = int(os.environ.get("MHATSH_LOGIN_DRAMA_LOOP", "0"))
        self.send_initial_user = os.environ.get(
            "MHATSH_SEND_INITIAL_USER", "1"
        ).lower() not in {"0", "false", "no"}
        self.send_initial_scene = os.environ.get(
            "MHATSH_SEND_INITIAL_SCENE", "1"
        ).lower() not in {"0", "false", "no"}
        self.send_map_characters = os.environ.get(
            "MHATSH_SEND_MAP_CHARACTERS", "1"
        ).lower() not in {"0", "false", "no"}
        self.send_stage_encounter_npcs = _env_enabled(
            "MHATSH_SEND_STAGE_ENCOUNTER_NPCS", "0"
        )
        self.player_level = min(
            PLAYER_LEVEL_CAP,
            max(
                1,
                int(os.environ.get("MHATSH_PLAYER_LEVEL", str(PLAYER_LEVEL_CAP))),
            ),
        )
        self.hero_level = max(
            1, int(os.environ.get("MHATSH_HERO_LEVEL", str(PLAYER_LEVEL_CAP)))
        )
        self.city_level = min(
            CITY_LEVEL_CAP,
            max(
                1,
                int(os.environ.get("MHATSH_CITY_LEVEL", str(CITY_LEVEL_CAP))),
            ),
        )
        self.skip_starter_quest = _env_enabled(
            "MHATSH_SKIP_STARTER_QUEST", "1"
        )
        self.unlock_all_functions = _env_enabled(
            "MHATSH_UNLOCK_ALL_FUNCTIONS", "1"
        )
        self.roster_mode = os.environ.get("MHATSH_ROSTER_MODE", "verified")
        self.map_spawn_mode = os.environ.get("MHATSH_MAP_SPAWN_MODE", "starter")
        self.playable_roster = playable_roster(self.roster_mode)
        self.map_spawns = map_spawns(self.map_spawn_mode)
        self.intro_stage_enabled = _env_enabled("MHATSH_INTRO_STAGE_MODE", "skip")
        self.intro_stage_key = os.environ.get(
            "MHATSH_INTRO_STAGE_KEY", "starter_intro_299301"
        )
        try:
            self.intro_stage_candidate = stage_candidate_by_key(self.intro_stage_key)
        except KeyError:
            self.intro_stage_candidate = stage_candidate_by_key(
                "starter_intro_299301"
            )
        default_intro_stage_id = (
            self.intro_stage_candidate.stage_id
            if self.intro_stage_candidate.stage_id is not None
            else STARTER_INTRO_STAGE_ID
        )
        self.intro_stage_id = int(
            os.environ.get("MHATSH_INTRO_STAGE_ID", default_intro_stage_id)
        )
        self.intro_stage_uid = int(
            os.environ.get(
                "MHATSH_INTRO_STAGE_UID",
                (
                    self.intro_stage_candidate.resolved_stage_uid
                    if self.intro_stage_candidate.stage_id == self.intro_stage_id
                    else self.intro_stage_id * 10000 + 1
                ),
            )
        )
        self.intro_stage_level = int(
            os.environ.get(
                "MHATSH_INTRO_STAGE_LEVEL", self.intro_stage_candidate.level
            )
        )
        self.intro_stage_time = int(
            os.environ.get(
                "MHATSH_INTRO_STAGE_TIME", self.intro_stage_candidate.time_limit
            )
        )
        self.intro_stage_drama = int(
            os.environ.get("MHATSH_INTRO_STAGE_DRAMA", self.intro_stage_candidate.drama)
        )
        self.intro_stage_trigger = os.environ.get(
            "MHATSH_INTRO_STAGE_TRIGGER", "task_enter"
        ).lower()
        self.intro_stage_delay = max(
            0.0, float(os.environ.get("MHATSH_INTRO_STAGE_DELAY", "0.25"))
        )
        self.stage_report_response = os.environ.get(
            "MHATSH_STAGE_REPORT_RESPONSE", "record"
        ).lower()
        self.ping_response_delay = max(
            0.0, float(os.environ.get("MHATSH_PING_RESPONSE_DELAY", "0.05"))
        )
        self.guide_response_delay = max(
            0.0, float(os.environ.get("MHATSH_GUIDE_RESPONSE_DELAY", "1.0"))
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
        self._configure_session(session)
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
        self._configure_session(session)
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
        elif name == "s_login_drama":
            response = session.tutorial.record_login_drama_request(
                int(values.get("StageId") or 0),
                self.login_drama_name,
                self.login_drama_loop,
            )
            if response is not None:
                await self._send(writer, session, "c_scene_play_drama", response)
        elif name == "s_login_drama_finish":
            session.tutorial.finish_login_drama(
                int(values.get("Uid") or 0),
                int(values.get("StageId") or 0),
            )
        elif name == "s_login_player_add":
            self._remember_role(session.urs, session.uid)
            await self._send(
                writer,
                session,
                "c_login_player_info",
                {
                    "Uid": session.uid,
                    "Name": "Local Hero",
                    "Level": self.player_level,
                    "HostId": 1,
                    "ServerName": "Local Preservation Server",
                    "CreateTime": int(time.time()),
                },
            )
        elif name == "s_login_player_enter":
            requested_uid = int(values.get("id") or session.uid)
            self._remember_role(session.urs, requested_uid)
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
                await self._send_area_event_login_data(writer, session)
                if self.unlock_all_functions:
                    await self._send_initial_function_unlocks(writer, session)
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
        elif name == "s_funcopen_query":
            await self._send(
                writer,
                session,
                "c_funcopen_query",
                {
                    "TargetUid": int(values.get("TargetUid") or session.uid),
                    "OpenId": int(values.get("OpenId") or 0),
                    "Result": int(self.unlock_all_functions),
                },
            )
        elif name == "s_guide_finish":
            set_ids = [int(item) for item in list(values.get("setIdList") or [])]
            guide_ids = [
                int(item) for item in list(values.get("guideIdList") or [])
            ]
            session.tutorial.finish_guides(set_ids, guide_ids)
            guide_response = {
                "Sets": sorted(set(set_ids)),
                "Ids": sorted(set(guide_ids)),
            }
            if self.skip_starter_quest:
                # The patched preservation client waits for c_card_seeinfo here.
                # Keep this acknowledgement tiny and target a non-player UID:
                # repeating the full 30-card self roster is ignored by the
                # archived client's waiter and would also redo card state. Still
                # send the normal guide acknowledgement afterward so the stock
                # guide overlay can clear its own completion callback.
                if self.guide_response_delay:
                    await asyncio.sleep(self.guide_response_delay)
                await self._send(
                    writer,
                    session,
                    "c_card_seeinfo",
                    {"Uid": 0, "CardInfo": []},
                )
                await self._send(writer, session, "c_guide_finish", guide_response)
                if {
                    STARTER_TASK_ID,
                    STARTER_MAP_GUIDE_ID,
                }.intersection(guide_response["Ids"]):
                    await self._send(
                        writer,
                        session,
                        "c_task_info",
                        session.tasks.task_info(),
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
                return
            # The archived client installs this callback just after SendPto.
            # A same-tick local response can arrive before the waiter exists.
            if self.guide_response_delay:
                await asyncio.sleep(self.guide_response_delay)
            await self._send(
                writer,
                session,
                "c_guide_finish",
                guide_response,
            )
            for guide_id in guide_response["Ids"]:
                if (
                    int(guide_id) == STARTER_TASK_ID
                    and session.tasks.should_spawn_beginner_npc(STARTER_TASK_ID)
                ):
                    await self._send_beginner_npc(writer, session)
                if int(guide_id) == STARTER_TASK_ID:
                    self._queue_starter_intro_stage(session, "starter_guide")
                task_update = session.tasks.complete_guide(int(guide_id))
                if task_update is not None:
                    await self._send_task_progression(
                        writer, session, task_update
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
            should_spawn_beginner_npc = self._is_starter_guide_stat(
                stat
            ) and session.tasks.should_spawn_beginner_npc(STARTER_TASK_ID)
            if should_spawn_beginner_npc:
                await self._send_beginner_npc(writer, session)
            if self._is_starter_guide_stat(stat):
                self._queue_starter_intro_stage(session, "starter_guide")
            task_update = session.tasks.observe_client_stat(stat)
            if task_update is not None:
                await self._send_task_progression(writer, session, task_update)
            if self._is_world_map_view_stat(stat):
                await self._send_pending_starter_intro_stage(
                    writer, session, "starter_guide"
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
            self._remember_active_card(session, roster)
            await self._send(
                writer,
                session,
                "c_scene_hero_change",
                roster.scene_hero_change(session.uid),
            )
            await self._send_scene_player_info(writer, session, roster)
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
            self._remember_active_card(session, roster)
            await self._send(
                writer,
                session,
                "c_scene_hero_change",
                roster.scene_hero_change(session.uid),
            )
            await self._send_scene_player_info(writer, session, roster)
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
        elif name == "s_card_support_skill":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_card_support_skill",
                session.character_menu.card_support_skill(
                    hero_cid=int(values.get("HeroCId") or 0),
                    index=int(values.get("Index") or 0),
                    support_hero_cid=int(values.get("SupportHeroCId") or 0),
                    roster=roster,
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
        elif name == "s_skill_get_skill_level":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_skill_get_skill_level",
                session.character_menu.skill_level(
                    int(values.get("HeroUid") or 0),
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
        elif name == "s_skill_get_spec_level":
            await self._send(
                writer,
                session,
                "c_skill_get_spec_level",
                session.character_menu.spec_level(
                    int(values.get("HeroUid") or 0)
                ),
            )
        elif name == "s_gem_list":
            await self._send(
                writer,
                session,
                "c_gem_list",
                session.character_menu.gem_list(
                    [int(item) for item in list(values.get("HeroCId") or [])]
                ),
            )
        elif name == "s_toplist_pages":
            await self._send(
                writer,
                session,
                "c_toplist_pages",
                session.character_menu.toplist_pages(
                    int(values.get("ID") or 0),
                    int(values.get("SubName") or 0),
                    [int(item) for item in list(values.get("PageNums") or [])],
                    int(values.get("SelfUid") or session.uid),
                    int(values.get("IsCross") or 0),
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
        elif name == "s_training_info":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_training_info",
                session.character_menu.training_info(roster),
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
                session.character_menu.attached_card_oper(
                    hero_id=int(values.get("HeroId") or 0),
                    index=int(values.get("Index") or 0),
                    oper=int(values.get("Oper") or 0),
                    attached_card_uid=int(values.get("ACardUid") or 0),
                    roster=roster,
                ),
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
            if session.tasks.should_spawn_beginner_npc(
                int(values.get("task_id") or 0)
            ):
                await self._send_beginner_npc(writer, session)
        elif name == "s_task_submit":
            await self._send_task_progression(
                writer,
                session,
                session.tasks.submit(int(values.get("task_id") or 0)),
            )
        elif name == "s_task_sync_info":
            task_id = int(values.get("TaskId") or 0)
            await self._send(
                writer,
                session,
                "c_task_sync_info",
                session.tasks.sync_info(
                    task_id,
                    str(values.get("Type") or ""),
                    list(values.get("ParamList") or []),
                ),
            )
            task_update = session.tasks.complete_active_quest_contact(task_id)
            if task_update is not None:
                await self._send_task_progression(writer, session, task_update)
                area_stage_id = session.tasks.area_event_stage_id_for_task(task_id)
                if area_stage_id:
                    stage_pass = session.stage.ensure_area_event_stage_passed(
                        area_stage_id
                    )
                    self.profile_store.remember_stage_progress(
                        session.urs,
                        session.stage.export_completions(),
                    )
                    await self._send(
                        writer,
                        session,
                        "c_area_event_stage_pass",
                        stage_pass,
                    )
                    await self._send(
                        writer,
                        session,
                        "c_area_event_info",
                        session.stage.area_event_info(area_stage_id),
                    )
        elif name == "s_task_enter_stage":
            await self._send(
                writer,
                session,
                "c_task_enter_stage",
                session.tasks.enter_stage(int(values.get("IsEnter") or 0)),
            )
            if int(values.get("IsEnter") or 0):
                await self._maybe_send_starter_intro_stage(
                    writer, session, "task_enter"
                )
        elif name == "s_training_enter":
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("StageId") or 0),
                hero_id=int(values.get("HeroCId") or 0),
            )
        elif name == "s_teach_pvp_enter":
            hero_ids = [int(item) for item in list(values.get("HeroCId") or [])]
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("StageId") or 0),
                hero_id=hero_ids[0] if hero_ids else 0,
            )
        elif name in {
            "s_resource_stage_enter",
            "s_resource_stage_reenter",
        }:
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("Id") or 0),
                card_uid=int(values.get("HeroUid") or 0),
            )
        elif name == "s_herochip_stage_enter":
            await self._send(
                writer,
                session,
                "c_herochip_stage_sync_data",
                session.stage.herochip_stage_sync_data(),
            )
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("Id") or 0),
                card_uid=int(values.get("HeroUid") or 0),
            )
        elif name in {
            "s_pressure_stage_enter",
            "s_hero_rank_stage_enter",
        }:
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("StageId") or 0),
            )
        elif name == "s_act_daily_stage_enter":
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("Id") or 0),
                hero_id=int(values.get("HeroId") or 0),
            )
        elif name in {
            "s_act_empty_shop_stage_enter",
            "s_act_empty_shop_stage_reenter",
        }:
            stage_index = int(values.get("StageIndex") or 0)
            await self._send(
                writer,
                session,
                "c_act_empty_shop_info",
                session.stage.empty_shop_stage_update(stage_index=stage_index),
            )
            await self._enter_requested_stage(
                writer,
                session,
                session.stage.empty_shop_stage(stage_index).stage_id,
                card_uid=int(values.get("HeroUid") or 0),
            )
        elif name == "s_act_allsvr_stage_enter":
            act_id = int(values.get("ActId") or 0)
            level_id = int(values.get("LevelId") or 0)
            await self._send(
                writer,
                session,
                "c_act_allsvr_stage_update_level",
                session.stage.allsvr_stage_update_level(act_id, level_id),
            )
            await self._enter_requested_stage(
                writer,
                session,
                session.stage.allsvr_stage(level_id).stage_id,
                hero_id=int(values.get("Cid") or 0),
            )
        elif name == "s_act_allsvr_stage_boss":
            act_id = int(values.get("ActId") or 0)
            boss_id = int(values.get("BossId") or 0)
            difficulty = int(values.get("Diffcult") or 0)
            stage = session.stage.allsvr_boss_stage(boss_id, difficulty)
            await self._send(
                writer,
                session,
                "c_act_allsvr_stage_update_boss",
                session.stage.allsvr_stage_update_boss(act_id, boss_id, difficulty),
            )
            await self._enter_requested_stage(
                writer,
                session,
                stage.stage_id,
                hero_id=int(values.get("Cid") or 0),
            )
        elif name == "s_act_boss_challenge_svr_point":
            await self._send(
                writer,
                session,
                "c_act_boss_challenge_svr_point",
                session.stage.boss_challenge_point(),
            )
        elif name == "s_act_boss_challenge_svr_ach_reward":
            await self._send(
                writer,
                session,
                "c_act_boss_challenge_svr_ach_reward",
                session.stage.boss_challenge_ach_reward(
                    int(values.get("AchId") or 0)
                ),
            )
            self._remember_stage_family_progress(session)
        elif name == "s_act_boss_challenge_join":
            await self._enter_requested_stage(
                writer,
                session,
                session.stage.allsvr_boss_stage().stage_id,
                card_uid=int(values.get("HeroUid") or 0),
            )
            await self._send(
                writer,
                session,
                "c_act_boss_challenge_server_ach",
                session.stage.boss_challenge_server_ach(),
            )
        elif name == "s_act_boss_challenge_rejoin":
            roster = self._ensure_roster(session)
            await self._enter_requested_stage(
                writer,
                session,
                session.stage.allsvr_boss_stage().stage_id,
                card_uid=roster.active_card_uid,
            )
        elif name == "s_act_boss_challenge_over":
            over = session.stage.boss_challenge_over(
                int(values.get("Damage") or 0)
            )
            await self._send(writer, session, "c_act_boss_challenge_over", over)
            await self._send(
                writer,
                session,
                "c_act_boss_challenge_svr_point",
                session.stage.boss_challenge_point(),
            )
            await self._send(
                writer,
                session,
                "c_act_boss_challenge_server_ach",
                session.stage.boss_challenge_server_ach(),
            )
            self._remember_stage_family_progress(session)
        elif name == "s_act_daily_stage_choose":
            await self._send(
                writer,
                session,
                "c_act_daily_stage_info",
                session.stage.act_daily_stage_info(int(values.get("ActId") or 0)),
            )
        elif name == "s_usj_enter_activity_ui":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_usj_load",
                session.stage.usj_load(
                    hero_uids=sorted(roster.cards),
                    current_hero_uid=roster.active_card_uid,
                ),
            )
        elif name == "s_usj_cycle_id":
            await self._send(
                writer,
                session,
                "c_usj_cycle_id",
                session.stage.usj_cycle_id(),
            )
        elif name == "s_usj_enter_stage":
            roster = self._ensure_roster(session)
            point_id = int(values.get("PointId") or 0)
            await self._send(
                writer,
                session,
                "c_usj_enter_stage",
                session.stage.usj_enter_stage(
                    zone_id=int(values.get("ZoneId") or 0),
                    point_id=point_id,
                    hero_uid=int(values.get("HeroUid") or roster.active_card_uid),
                ),
            )
            await self._enter_requested_stage(
                writer,
                session,
                session.stage.usj_first_stage_for_point(point_id),
                card_uid=int(values.get("HeroUid") or roster.active_card_uid),
            )
        elif name == "s_usj_enter_next_zone":
            await self._send(
                writer,
                session,
                "c_usj_enter_next_zone",
                session.stage.usj_enter_next_zone(int(values.get("ZoneId") or 0)),
            )
        elif name == "s_area_event_enter_stage":
            hero_uids = [int(item) for item in list(values.get("HerosUId") or [])]
            stage_id = int(values.get("StageId") or 0)
            await self._enter_requested_stage(
                writer,
                session,
                stage_id,
                card_uid=hero_uids[0] if hero_uids else 0,
            )
            await self._send(
                writer,
                session,
                "c_area_event_info",
                session.stage.area_event_info(stage_id),
            )
        elif name in {
            "s_campaign_fight",
            "s_new_hero_fight",
            "s_secret_target_stage",
            "s_relax_stage_choose",
        }:
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("StageId") or values.get("stageId") or 0),
                card_uid=int(values.get("HeroUid") or 0),
            )
        elif name == "s_pressure_hero_fight":
            hero_uid = int(values.get("HeroUid") or 0)
            await self._send(
                writer,
                session,
                "c_pressure_hero_fight",
                {"HeroUid": hero_uid},
            )
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("StageId") or 0),
                card_uid=hero_uid,
            )
        elif name == "s_night_fight_enter_stage":
            stage_id = int(values.get("StageId") or 0)
            lineup = [int(item) for item in list(values.get("Lineup") or [])]
            await self._send(
                writer,
                session,
                "c_night_fight_cache_stage_id",
                {"CacheStageId": stage_id},
            )
            await self._enter_requested_stage(
                writer,
                session,
                stage_id,
                card_uid=lineup[0] if lineup else 0,
            )
        elif name == "s_night_fight_info":
            roster = self._ensure_roster(session)
            hero_uids = sorted(roster.cards)
            await self._send(
                writer,
                session,
                "c_night_fight_info",
                session.stage.night_fight_info(),
            )
            await self._send(
                writer,
                session,
                "c_night_fight_hero_lineup",
                session.stage.night_fight_hero_lineup(hero_uids),
            )
            await self._send(
                writer,
                session,
                "c_night_fight_sync_status",
                session.stage.night_fight_sync_status(
                    session.stage.current_stage_id, hero_uids
                ),
            )
        elif name == "s_night_fight_enter_fight":
            roster = self._ensure_roster(session)
            hero_uid = int(values.get("HeroUid") or roster.active_card_uid)
            await self._send(
                writer,
                session,
                "c_night_fight_hero_lineup",
                session.stage.night_fight_hero_lineup([hero_uid]),
            )
            await self._enter_requested_stage(
                writer,
                session,
                int(values.get("StageId") or 0),
                card_uid=hero_uid,
            )
        elif name == "s_night_fight_fight_over":
            roster = self._ensure_roster(session)
            stage_id = int(values.get("StageId") or session.stage.current_stage_id or 0)
            hero_uid = roster.active_card_uid
            is_win = int(values.get("IsWin") or 0)
            await self._send(
                writer,
                session,
                "c_night_fight_fight_over",
                session.stage.night_fight_fight_over(stage_id, hero_uid, is_win),
            )
            reward = session.stage.night_fight_reward(is_win)
            self._grant_stage_reward_list(
                session,
                list(reward.get("FixedReward") or [])
                + list(reward.get("ExtraReward") or [])
                + list(reward.get("SpecialReward") or []),
            )
            await self._send(writer, session, "c_night_fight_reward", reward)
            await self._send(
                writer,
                session,
                "c_night_fight_sync_status",
                session.stage.night_fight_sync_status(
                    stage_id, sorted(roster.cards)
                ),
            )
            self.profile_store.remember_stage_progress(
                session.urs,
                session.stage.export_completions(),
            )
            self._remember_stage_family_progress(session)
        elif name == "s_night_fight_leave_stage":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_night_fight_sync_status",
                session.stage.night_fight_sync_status(
                    session.stage.current_stage_id, sorted(roster.cards)
                ),
            )
        elif name == "s_rogue_endless_fight":
            hero_index = int(values.get("HeroIndex") or 0)
            rogue_index = int(values.get("Index") or 0)
            await self._send(
                writer,
                session,
                "c_rogue_endless_fight",
                {"HeroIndex": hero_index, "Index": rogue_index},
            )
            await self._enter_requested_stage(
                writer,
                session,
                self._rogue_endless_stage_id(rogue_index),
            )
        elif name == "s_area_event_fight_over":
            stage_id = int(values.get("StageId") or session.stage.current_stage_id or 0)
            is_win = int(values.get("IsWin") or 0)
            stage_pass = session.stage.record_area_event_fight_over(
                stage_id=stage_id,
                is_win=is_win,
                use_time=int(values.get("UseTime") or 0),
            )
            self.profile_store.remember_stage_progress(
                session.urs,
                session.stage.export_completions(),
            )
            await self._send(writer, session, "c_area_event_stage_pass", stage_pass)
            await self._send(
                writer,
                session,
                "c_area_event_info",
                session.stage.area_event_info(stage_id),
            )
            if is_win:
                task_update = session.tasks.complete_area_event_stage(stage_id)
                if task_update is not None:
                    await self._send_task_progression(writer, session, task_update)
        elif name == "s_area_event_reset_stage_times":
            await self._send(
                writer,
                session,
                "c_area_event_fight_times_status",
                {
                    "StageFightTimes": session.stage.area_event_stage_times_for(
                        int(values.get("StageId") or 0)
                    )
                },
            )
        elif name == "s_area_event_trigger_on":
            await self._send(
                writer,
                session,
                "c_area_event_trigger_change",
                {
                    "EventRound": int(values.get("AreaId") or 0),
                    "TriggerOnMap": [int(values.get("AreaId") or 0)],
                },
            )
        elif name == "s_area_event_wipe":
            await self._send(
                writer,
                session,
                "c_area_event_wipe",
                {"AreaEventId": int(values.get("AreaEventId") or 0)},
            )
        elif name == "s_area_event_leave_stage":
            await self._send(
                writer,
                session,
                "c_area_event_leave_stage",
                {"LeaveType": int(values.get("LeaveType") or 0)},
            )
        elif name == "s_resource_stage_info":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_resource_stage_info",
                session.stage.resource_stage_info(roster.active_card_uid),
            )
        elif name == "s_usj_server_score":
            await self._send(
                writer,
                session,
                "c_usj_update_score",
                {
                    "ServerTotalScore": sum(session.stage.pressure_scores.values()),
                    "List": [{"Id": 1, "State": 0}, {"Id": 2, "State": 0}],
                },
            )
        elif name == "s_usj_get_point_reward":
            point_ids = [int(item) for item in list(values.get("PointList") or [])]
            point_reward = session.stage.usj_point_reward(
                int(values.get("ZoneId") or 0),
                point_ids,
            )
            self._grant_stage_reward_list(
                session,
                [
                    reward
                    for group in list(point_reward.get("RewardList") or [])
                    if isinstance(group, dict)
                    for reward in list(group.get("Reward") or [])
                    if isinstance(reward, dict)
                ],
            )
            await self._send(writer, session, "c_usj_get_point_reward", point_reward)
        elif name == "s_usj_get_score_reward":
            await self._send(
                writer,
                session,
                "c_usj_update_score_reward",
                session.stage.usj_score_reward(int(values.get("Id") or 0)),
            )
        elif name == "s_usj_get_zone_reward":
            await self._send(
                writer,
                session,
                "c_usj_get_zone_reward",
                session.stage.usj_zone_reward(
                    int(values.get("ZoneId") or 0),
                    int(values.get("RewardType") or 0),
                ),
            )
        elif name == "s_usj_have_show_end_reward":
            await self._send(
                writer,
                session,
                "c_usj_get_end_reward",
                {},
            )
        elif name == "s_pressure_stage_detail":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_pressure_stage_detail",
                session.stage.pressure_stage_detail(
                    int(values.get("StageId") or 0),
                    hero_list=[
                        {
                            "HeroId": card.hero_id,
                            "Power": roster.hero_level * 1000 + card.hero_id,
                        }
                        for card in sorted(
                            roster.cards.values(), key=lambda item: item.card_uid
                        )
                    ],
                ),
            )
        elif name == "s_pressure_stage_finish":
            session.stage.record_pressure_stage_finish(values)
            self._remember_stage_family_progress(session)
        elif name == "s_hero_rank_stage_end":
            update = session.stage.hero_rank_stage_update(
                int(values.get("Id") or session.stage.current_stage_id or 0),
                [int(item) for item in list(values.get("Star") or [])],
            )
            await self._send(writer, session, "c_hero_rank_stage_update", update)
            self.profile_store.remember_stage_progress(
                session.urs,
                session.stage.export_completions(),
            )
        elif name == "s_usj_get_stage_record":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_usj_get_stage_record",
                session.stage.usj_stage_record(
                    point_id=int(values.get("PointId") or 0),
                    uid=session.uid,
                    user_level=self.player_level,
                    hero_id=roster.active_hero_id,
                    fighting=roster.hero_level * 1000 + roster.active_hero_id,
                ),
            )
        elif name == "s_usj_end_stage":
            roster = self._ensure_roster(session)
            usj_result = session.stage.usj_end_stage(
                values,
                hero_uid=int(values.get("HeroUid") or roster.active_card_uid),
            )
            self._remember_stage_family_progress(session)
            await self._send(
                writer,
                session,
                "c_usj_end_stage",
                usj_result,
            )
        elif name == "s_act_daily_stage_report":
            daily_result = session.stage.act_daily_stage_result(values)
            self._remember_stage_family_progress(session)
            self._grant_stage_reward_list(
                session,
                [
                    reward
                    for group in list(daily_result.get("RewardList") or [])
                    if isinstance(group, dict)
                    for reward in list(group.get("AddLog") or [])
                    if isinstance(reward, dict)
                ],
            )
            await self._send(
                writer,
                session,
                "c_act_daily_stage_result",
                daily_result,
            )
        elif name == "s_stage_finish_loading":
            await self._send(
                writer,
                session,
                "c_stage_finish_loading",
                session.stage.finish_loading(session.uid),
            )
        elif name == "s_stage_damage_info":
            session.stage.record_damage_info(values)
            await self._send(
                writer,
                session,
                "c_stage_damage_info",
                session.stage.damage_info(),
            )
        elif name == "s_stage_report":
            session.stage.record_report(values)
            if self.stage_report_response in {"complete", "result"}:
                roster = self._ensure_roster(session)
                fight_style = fight_style_for_character(roster.active_card.character)
                stage = self._current_stage_definition(session)
                stage_drop = session.stage.stage_drop(
                    fight_style=fight_style,
                    hero_level=roster.hero_level,
                    stage=stage,
                )
                await self._send(
                    writer,
                    session,
                    "c_stage_drop",
                    stage_drop,
                )
                stage_result = session.stage.result(
                    fight_style=fight_style,
                    hero_level=roster.hero_level,
                    stage=stage,
                )
                self.profile_store.remember_stage_progress(
                    session.urs,
                    session.stage.export_completions(),
                )
                self._grant_stage_rewards(session, stage_result, stage_drop)
                await self._send(
                    writer,
                    session,
                    "c_stage_result",
                    stage_result,
                )
                await self._send(
                    writer,
                    session,
                    "c_stage_end_gm",
                    session.stage.end_gm(
                        fight_style=fight_style,
                        hero_level=roster.hero_level,
                        stage=stage,
                    ),
                )
        elif name == "s_frame_monster_data":
            session.stage.record_monster_frame_data(values)
        elif name == "s_stage_frame_report":
            await self._send(
                writer,
                session,
                "c_stage_frame_report",
                session.stage.record_frame_report(),
            )
        elif name == "s_stage_play_sync":
            await self._send(
                writer,
                session,
                "c_stage_play_sync",
                session.stage.record_play_sync(
                    session.uid,
                    list(values.get("SyncData") or []),
                ),
            )
        elif name == "s_stage_is_back":
            await self._send(
                writer,
                session,
                "c_stage_is_back",
                session.stage.stage_is_back(int(values.get("StageId") or 0)),
            )
        elif name == "s_stage_leave":
            await self._send(
                writer,
                session,
                "c_stage_leave",
                session.stage.leave_stage(int(values.get("StageId") or 0)),
            )
        elif name == "s_stage_theater":
            await self._send(
                writer,
                session,
                "c_theater_finish",
                session.stage.theater_finish(values),
            )
        elif name == "s_stage_bonus":
            bonus = session.stage.stage_bonus(values)
            self._grant_stage_reward_list(
                session,
                [item for item in list(bonus.get("RewardList") or []) if isinstance(item, dict)],
            )
            self.profile_store.remember_stage_progress(
                session.urs,
                session.stage.export_completions(),
            )
            await self._send(writer, session, "c_stage_show_reward", bonus)
        elif name == "s_stage_extra_reward":
            extra_reward = session.stage.stage_extra_reward(session.uid)
            self.profile_store.grant_items(
                session.urs,
                [
                    (
                        int(item.get("ItemId") or 0),
                        int(item.get("Num") or 0),
                    )
                    for item in list(extra_reward.get("DrawItems") or [])
                    if isinstance(item, dict)
                ],
            )
            await self._send(writer, session, "c_stage_extra_reward", extra_reward)
        elif name == "s_stage_quick_reborn":
            session.stage.record_quick_reborn(int(values.get("RebornCount") or 0))
        elif name == "s_stage_activity_info":
            await self._send(
                writer,
                session,
                "c_stage_activity_info",
                session.activities.stage_activity_info(),
            )
            await self._send(
                writer,
                session,
                "c_act_allsvr_stage_info",
                session.stage.allsvr_stage_info(),
            )
            await self._send(
                writer,
                session,
                "c_relax_stage_sync_data",
                session.stage.relax_stage_sync_data(),
            )
        elif name == "s_theater_open":
            await self._send(
                writer,
                session,
                "c_theater_open",
                session.stage.theater_open(),
            )
        elif name == "s_theater_unlock":
            await self._send(
                writer,
                session,
                "c_theater_unlock",
                session.stage.theater_unlock(int(values.get("StageId") or 0)),
            )
        elif name == "s_theater_bonus":
            await self._send(
                writer,
                session,
                "c_theater_bonus",
                session.stage.theater_bonus(
                    int(values.get("CfgType") or 0),
                    int(values.get("BonusIdx") or 0),
                ),
            )
        elif name == "s_theater_chapterbonus":
            await self._send(
                writer,
                session,
                "c_theater_chapterbonus",
                session.stage.theater_chapter_bonus(
                    int(values.get("chapterid") or 0),
                    int(values.get("starIdx") or 0),
                ),
            )
        elif name == "s_relax_stage_get_box":
            await self._send(
                writer,
                session,
                "c_relax_stage_boxinfo",
                session.stage.relax_stage_boxinfo(session.uid),
            )
        elif name == "s_relax_cond_get_reward":
            await self._send(
                writer,
                session,
                "c_relax_stage_sync_cond",
                session.stage.relax_stage_sync_cond(
                    int(values.get("Type") or 0),
                    int(values.get("Id") or 0),
                ),
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
        elif name == "s_secret_area_task_reward":
            task_id = int(values.get("TaskId") or 0)
            await self._send(
                writer,
                session,
                "c_secret_area_task_update",
                {"TaskList": [{"Id": task_id, "Status": 1, "CurValue": 1}]},
            )
        elif name == "s_secret_area_active_key":
            roster = self._ensure_roster(session)
            await self._send(
                writer,
                session,
                "c_secret_area_cycle",
                session.stage.secret_area_cycle(),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_times",
                session.stage.secret_area_times(),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_key",
                session.stage.secret_area_key(),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_all_hero",
                session.stage.secret_area_all_hero(
                    [card.hero_id for card in roster.cards.values()]
                ),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_players",
                session.stage.secret_area_players(
                    uid=session.uid,
                    hero_id=roster.active_hero_id,
                    level=roster.hero_level,
                    fighting=roster.hero_level * 1000 + roster.active_hero_id,
                ),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_history",
                session.stage.secret_area_history(),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_cycle_record",
                session.stage.secret_area_cycle_record(
                    session.uid,
                    roster.active_hero_id,
                ),
            )
        elif name == "s_secret_area_history":
            await self._send(
                writer,
                session,
                "c_secret_area_history",
                session.stage.secret_area_history(),
            )
        elif name == "s_secret_area_finish_stage":
            await self._send(
                writer,
                session,
                "c_secret_area_stage_finish",
                session.stage.secret_area_stage_finish(session.uid, values),
            )
            await self._send(
                writer,
                session,
                "c_secret_area_history_add",
                session.stage.secret_area_history_add(),
            )
        elif name == "s_secret_area_drop_card":
            await self._send(
                writer,
                session,
                "c_secret_area_drop_card",
                session.stage.secret_area_drop_card(
                    session.uid,
                    int(values.get("CardPos") or 0),
                ),
            )
        elif name == "s_secret_insert_key":
            await self._send(
                writer,
                session,
                "c_secret_insert_key",
                {
                    "KeyOwerUid": int(values.get("KeyOwerUid") or session.uid),
                    "KeyId": int(values.get("KeyId") or 0),
                },
            )
        elif name == "s_secret_apply_insert_key":
            await self._send(
                writer,
                session,
                "c_secret_apply_insert_key",
                {
                    "KeyOwerUid": session.uid,
                    "KeyId": int(values.get("KeyId") or 0),
                    "OwnerName": "Local Hero",
                },
            )
        elif name == "s_secret_refuse_key":
            await self._send(
                writer,
                session,
                "c_secret_refuse_key",
                {"UserUid": int(values.get("UserUid") or session.uid)},
            )
        elif name == "s_secret_out_key":
            await self._send(writer, session, "c_secret_out_key", {})
        elif name == "s_secret_area_jump_key":
            await self._send(writer, session, "c_secret_area_jump_key", {})
        elif name == "s_secret_area_cycle_reward":
            await self._send(writer, session, "c_secret_area_clear_cycle_record", {})
        elif name == "s_act_secret_record_list":
            await self._send(
                writer,
                session,
                "c_act_secret_record_list",
                session.stage.act_secret_record_list(
                    int(values.get("ActId") or 0),
                ),
            )
        elif name == "s_all_server_cond_get_info":
            await self._send(
                writer,
                session,
                "c_all_server_cond_get_info",
                {
                    "ServerCondInfo": [
                        {"Id": item["Id"], "Status": item["State"], "PlayerList": []}
                        for item in session.stage.allsvr_cond_list()
                    ]
                },
            )
        elif name == "s_all_server_cond_get_reward":
            cond_id = int(values.get("Id") or 0)
            cond_state = next(
                (
                    item["State"]
                    for item in session.stage.allsvr_cond_list()
                    if item["Id"] == cond_id
                ),
                0,
            )
            await self._send(
                writer,
                session,
                "c_all_server_cond_get_reward",
                {"Id": cond_id, "Status": cond_state},
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
        else:
            session.world.record_unhandled_message(name, protocol_id, values)
            LOG.warning("unhandled %d %s %s", protocol_id, name, rendered)

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
            self._remember_role(session.urs, role_uid)
        await self._send(
            writer,
            session,
            "c_login_account_info",
            {
                "URS": session.urs,
                "Uid": 0 if role_uid is None else role_uid,
                "DramaFlag": self.login_drama_flag if self.login_drama_enabled else 0,
                "DramaStep": self.login_drama_step if self.login_drama_enabled else 0,
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
                    "Level": self.player_level,
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
        await self._send_scene_player_info(writer, session, roster)
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

    async def _send_area_event_login_data(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        roster = self._ensure_roster(session)
        await self._send(
            writer,
            session,
            "c_area_event_login_data",
            session.stage.area_event_login_data(
                normal_lineup=[roster.active_card_uid],
            ),
        )

    async def _send_initial_function_unlocks(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        await self._send(
            writer,
            session,
            "c_funcopen_list",
            {"idlist": list(FUNCTION_OPEN_IDS)},
        )

    def _ensure_roster(self, session: Session) -> RosterState:
        if session.roster is None:
            session.roster = RosterState(
                self.playable_roster,
                first_card_uid=STARTER_CARD_UID,
                hero_level=self.hero_level,
            )
            try:
                session.roster.select_card(self.active_cards.get(session.urs, 0), 1)
            except KeyError:
                pass
        return session.roster

    def _remember_active_card(self, session: Session, roster: RosterState) -> None:
        self.profile_store.remember_active_card(session.urs, roster.active_card_uid)

    def _remember_role(self, urs: str, uid: int) -> None:
        self.profile_store.remember_role(urs, uid)

    def _current_stage_definition(self, session: Session) -> BattleStageDefinition:
        if session.stage.current_stage_key:
            try:
                return stage_candidate_by_key(session.stage.current_stage_key)
            except KeyError:
                pass
        if session.stage.current_stage_id:
            return stage_candidate_or_generated(session.stage.current_stage_id)
        return self.intro_stage_candidate

    async def _enter_requested_stage(
        self,
        writer: asyncio.StreamWriter,
        session: Session,
        stage_id: int,
        *,
        hero_id: int = 0,
        card_uid: int = 0,
    ) -> None:
        stage = stage_candidate_or_generated(stage_id or self.intro_stage_id)
        roster = self._ensure_roster(session)
        changed = False
        if card_uid:
            try:
                roster.select_card(card_uid, 1)
                changed = True
            except KeyError:
                pass
        if hero_id:
            try:
                roster.select_hero(hero_id)
                changed = True
            except KeyError:
                pass
        if changed:
            self._remember_active_card(session, roster)
        await self._send_stage_enter(writer, session, roster, stage)

    async def _send_stage_enter(
        self,
        writer: asyncio.StreamWriter,
        session: Session,
        roster: RosterState,
        stage: BattleStageDefinition,
    ) -> None:
        await self._send(
            writer,
            session,
            "c_stage_enter",
            session.stage.enter_recovered_stage(stage),
        )
        await self._send(
            writer,
            session,
            "c_frame_fighter_data",
            self._frame_fighter_data(session, roster),
        )
        if self.send_stage_encounter_npcs and stage.encounter_spawns:
            await self._send(
                writer,
                session,
                "c_scene_npc_create",
                {
                    "NpcList": [
                        spawn.to_scene_npc()
                        for spawn in stage.encounter_spawns
                    ]
                },
            )

    def _frame_fighter_data(
        self, session: Session, roster: RosterState
    ) -> dict[str, Any]:
        active = roster.active_card
        skill_levels = fight_style_for_character(
            active.character
        ).protocol_skill_levels(roster.hero_level)
        support_skills = session.character_menu.training_support_skills(
            active.hero_id, roster
        )
        return {
            "Uid": session.uid,
            "X": STARTER_SCENE_X,
            "Y": STARTER_SCENE_Y,
            "Face": 0,
            "Camp": 0,
            "Name": "Local Hero",
            "Level": self.player_level,
            "StageLevel": roster.hero_level,
            "Exp": 0,
            "HeroId": active.hero_id,
            "CardUid": active.card_uid,
            "Fighting": roster.hero_level * 1000 + active.hero_id,
            "AvatarId": 0,
            "AvatarFrameId": 0,
            "RobotId": 0,
            "Heros": [
                {
                    "Mid": active.card_uid,
                    "HeroId": active.hero_id,
                    "ShapeId": active.shape_id,
                    "FashionId": 0,
                    "PeakAttrId": 0,
                    "Infos": [],
                    "CardSkillLevel": skill_levels,
                    "CardSpecLevel": [],
                    "RuneSpecList": [],
                    "Buffs": [],
                    "AttachedCardBuff": [],
                    "ActiveCards": [],
                    "SupportSkill": support_skills,
                }
            ],
            "EquipHideAttr": [],
            "CampaignBuffArgs": [],
            "GroupBuffs": [],
        }

    async def _send_scene_player_info(
        self,
        writer: asyncio.StreamWriter,
        session: Session,
        roster: RosterState,
    ) -> None:
        await self._send(
            writer,
            session,
            "c_scene_player_info",
            {
                "Uid": session.uid,
                "Camp": 0,
                "Name": "Local Hero",
                "Level": self.player_level,
                "TopLevel": 0,
                "ShowHeroId": roster.active_hero_id,
                "LeagueId": 0,
                "LeagueName": "",
                "TitleId": 0,
                "MoodId": 0,
                "Version": 1,
            },
        )

    def _configure_session(self, session: Session) -> None:
        if session.profile_configured:
            return
        session.stage.load_completions(
            self.profile_store.stage_progress.get(session.urs, {})
        )
        session.stage.load_family_progress(
            self.profile_store.stage_family_progress.get(session.urs, {})
        )
        session.tasks.seed_finished_tasks(
            self.profile_store.finished_tasks.get(session.urs, ())
        )
        session.tasks.seed_completed_area_event_stages(
            stage_id
            for stage_id, completion in session.stage.completions.items()
            if completion.status == 1 and completion.pass_count > 0
        )
        session.world_tasks.city_level = self.city_level
        if self.skip_starter_quest:
            session.tasks.skip_starter_quest()
            session.tutorial.seed_completed_guide(STARTER_TASK_ID)
            session.tutorial.seed_completed_guide(
                STARTER_MAP_GUIDE_ID,
                STARTER_MAP_GUIDE_SET_ID,
            )
            session.world_tasks.seed_unlocked(self.city_level)
        session.profile_configured = True

    def _remember_stage_family_progress(self, session: Session) -> None:
        self.profile_store.remember_stage_family_progress(
            session.urs,
            session.stage.export_family_progress(),
        )

    def _grant_stage_rewards(
        self,
        session: Session,
        stage_result: dict[str, object],
        stage_drop: dict[str, object],
    ) -> None:
        if int(stage_result.get("Result") or 0) != 1:
            return

        rewards: list[tuple[int, int]] = self._stage_reward_items(
            list(stage_result.get("RewardList") or [])
        )
        for item in list(stage_drop.get("FirstReward") or []):
            if not isinstance(item, dict):
                continue
            rewards.append(
                (
                    int(item.get("ItemId") or 0),
                    int(item.get("count") or item.get("Count") or 0),
                )
            )
        self.profile_store.grant_items(session.urs, rewards)

    def _grant_stage_reward_list(
        self, session: Session, reward_list: list[dict[str, object]]
    ) -> None:
        self.profile_store.grant_items(
            session.urs,
            self._stage_reward_items(reward_list),
        )

    @staticmethod
    def _stage_reward_items(
        reward_list: list[dict[str, object]],
    ) -> list[tuple[int, int]]:
        rewards: list[tuple[int, int]] = []
        for item in reward_list:
            if not isinstance(item, dict):
                continue
            rewards.append(
                (
                    int(item.get("ItemId") or 0),
                    int(item.get("count") or item.get("Count") or 0),
                )
            )
        return rewards

    def _is_starter_guide_stat(self, stat: dict[str, object]) -> bool:
        nums = list(stat.get("NumData") or [])
        if len(nums) < 2:
            return False
        return int(nums[0]) == 1 and int(nums[1]) == STARTER_TASK_ID

    def _is_world_map_view_stat(self, stat: dict[str, object]) -> bool:
        nums = list(stat.get("NumData") or [])
        strings = [str(item) for item in list(stat.get("StrData") or [])]
        return (
            len(nums) >= 3
            and int(nums[0]) == 0
            and int(nums[1]) == 1404
            and int(nums[2]) == 10351
            and any("WorldMapView" in item for item in strings)
        )

    async def _send_beginner_npc(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        await self._send(
            writer,
            session,
            "c_scene_npc_create",
            {
                "NpcList": [
                    scene_npc_from_spawn(spawn)
                    for spawn in TUTORIAL_MAP_SPAWNS
                ]
            },
        )

    async def _send_task_progression(
        self,
        writer: asyncio.StreamWriter,
        session: Session,
        task_update: dict[str, Any],
    ) -> None:
        await self._send(writer, session, "c_task_info_update", task_update)
        task_info = task_update.get("task_info")
        if not isinstance(task_info, dict):
            return
        if int(task_info.get("Status") or 0) == 3:
            self.profile_store.remember_finished_tasks(
                session.urs, session.tasks.finished
            )
            if session.tasks.should_refresh_progression_list(
                int(task_info.get("Id") or 0)
            ):
                await self._send(
                    writer,
                    session,
                    "c_task_info",
                    session.tasks.task_info(),
                )
        if int(task_info.get("Id") or 0) != STARTER_TASK_ID:
            return
        if int(task_info.get("Status") or 0) != 3:
            return
        for packet_name, packet_values in session.world_tasks.complete_beginner_quest():
            await self._send(writer, session, packet_name, packet_values)

    async def _send_starter_intro_stage(
        self, writer: asyncio.StreamWriter, session: Session
    ) -> None:
        roster = self._ensure_roster(session)
        await self._send_stage_enter(
            writer, session, roster, self._intro_stage_definition()
        )

    def _intro_stage_definition(self) -> BattleStageDefinition:
        return replace(
            self.intro_stage_candidate,
            stage_id=self.intro_stage_id,
            stage_uid=self.intro_stage_uid,
            level=self.intro_stage_level,
            time_limit=self.intro_stage_time,
            drama=self.intro_stage_drama,
        )

    @staticmethod
    def _rogue_endless_stage_id(index: int) -> int:
        stages = tuple(sorted(ROGUELIKE_STAGES, key=lambda stage: stage.display_order))
        if index > 0:
            for stage in stages:
                if stage.display_order == index or stage.constant_index == index:
                    return stage.stage_id
        endless = tuple(stage for stage in stages if stage.mode == "endless")
        return (endless or stages)[0].stage_id

    async def _maybe_send_starter_intro_stage(
        self, writer: asyncio.StreamWriter, session: Session, trigger: str
    ) -> None:
        if not self.intro_stage_enabled or self.intro_stage_trigger != trigger:
            return
        if session.stage.current_stage_id == self.intro_stage_id:
            return
        await self._send_starter_intro_stage(writer, session)

    def _queue_starter_intro_stage(self, session: Session, trigger: str) -> None:
        if not self.intro_stage_enabled or self.intro_stage_trigger != trigger:
            return
        if session.stage.current_stage_id == self.intro_stage_id:
            return
        session.pending_starter_intro_stage = True

    async def _send_pending_starter_intro_stage(
        self, writer: asyncio.StreamWriter, session: Session, trigger: str
    ) -> None:
        if not session.pending_starter_intro_stage:
            return
        if not self.intro_stage_enabled or self.intro_stage_trigger != trigger:
            session.pending_starter_intro_stage = False
            return
        if session.stage.current_stage_id == self.intro_stage_id:
            session.pending_starter_intro_stage = False
            return
        if self.intro_stage_delay:
            await asyncio.sleep(self.intro_stage_delay)
        session.pending_starter_intro_stage = False
        await self._send_starter_intro_stage(writer, session)

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
