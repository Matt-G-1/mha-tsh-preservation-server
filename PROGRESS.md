# MHA TSH Preservation Progress

Last updated: 2026-06-15

## Goal

Run the archived Android client against clean-room bootstrap and game-service
implementations, including login, character creation, and initial world entry.
The original installed package remains untouched; testing uses a separately
signed compatibility clone.

This public file tracks protocol and gameplay compatibility only. Private
environment details are intentionally omitted from Git.

## Proven Working

- The compatibility clone launches under its separate package name.
- The legal screen Continue action and the missing background/panel assets are
  restored in the current test clone.
- Bootstrap config, guest login, server list, and empty player list are served
  by the clean-room implementation.
- The client connects to the Axon-compatible game service.
- The five-byte seed handshake, rolling XOR streams, frame checksum, recovered
  protocol IDs, and schema payload encoding round-trip in tests and on-device.
- The client accepts `c_login_version`, `c_login_account_info`, and
  `c_login_checkstr`.
- The six recovered fields for `c_login_player_info` are encoded in callback
  order: `Uid`, `Name`, `Level`, `HostId`, `ServerName`, `CreateTime`.
- The server handles both explicit `s_login_player_add` creation and automatic
  provisioning of a minimal local role.
- The client accepts `c_user_create`, `c_scene_player_info`, and
  `c_scene_enter`, then loads scene `1000` at the archived Honei Urban Area
  spawn.
- Midoriya's player model renders on-device with hero ID `1011` and shape ID
  `1001`; the earlier hero-table lookup error no longer occurs.
- The client accepts a minimal `c_card_seeinfo` inventory containing verified
  hero/card mappings.
- The client reports `s_scene_enter_end`; the server answers
  `c_scene_enter_end`, completing the initial scene-entry exchange.
- `s_guide_finish` receives a schema-matched `c_guide_finish` acknowledgment
  based on accumulated session guide state.
- `s_teach_finish` receives a schema-matched `c_teach_finish` acknowledgment
  that tracks completed tutorial skill-practice counts by hero.
- `s_base_station_all_info` receives an empty, version-matched
  `c_base_station_all_info` through the same tutorial-state container; the
  server now follows it with minimal `c_city_level_info` and
  `c_world_task_info` seed packets so the archived world quest map has city
  and open-map state to consume.
- The server has a minimal stateful task journal for `c_task_info`,
  `c_task_info_update`, `c_task_sync_info`, and `c_task_enter_stage`, covering
  starter task listing, acceptance, submission, sync echo, and stage-entry
  acknowledgment.
- Observed first-guide telemetry (`s_client_stat` guide `1301`, step `10011`)
  is recorded in tutorial state and can complete the starter task exactly once.
- A controlled on-device run of the current server code validated the starter
  task bridge live: tapping the highlighted map marker produced
  `s_client_stat` `[1, 1301, 10011]`, `s_guide_finish` for guide `1301`,
  `s_guide_drama`, and `s_base_station_all_info`; the client accepted
  `c_task_info_update`, `c_guide_finish`, `c_base_station_all_info`,
  `c_city_level_info`, and `c_world_task_info`, then opened the world map UI
  with visible map markers.
- World-map compatibility handlers now acknowledge city-level clicks,
  world-task reward-rate requests, auto-finish-tip preference changes,
  world-task auto-finish requests, and prestige reward picks through recovered
  packet schemas.
- World-session telemetry now records player movement (`s_scene_move`),
  frame-stat heartbeats (`s_client_stat_frame`), and client error reports
  (`s_client_error`) without sending unsafe extra replies.
- The world HUD, minimap, controls, tutorial prompt, and local ping indicator
  render on-device during controlled testing.
- `s_time_ping` receives an echoed `c_time_ping` response.
- A replacement TCP session receives `c_reconnect_flag` after
  `s_login_reconnect`, restoring the local account and player identity.
- The supplied AXMD raw-rip list is represented in a typed catalog covering 31
  playable models, 40 map/NPC models, and 3 chibi models.
- Twenty-nine of the 31 supplied playable model entries have recovered
  `hero_cfg` rows and independently matched `shape_info` model paths. The two
  remaining asset-only entries are All For One `h1039` and Best Jeanist
  `h1927`.
- The recovered tables correct two tentative names in the supplied list:
  `h1032` is Mirio Togata, and `h1998` is an All Might variant.
- The initial `c_card_seeinfo` roster contains a validated starter set while
  Midoriya remains the active world avatar. The first owned card is now marked
  as the active fighting card in the serialized roster state and was accepted
  by the client in controlled on-device validation.
- An opt-in expanded roster path serializes all 29 protocol-verified playable
  characters in `c_card_seeinfo` while preserving Midoriya as the first active
  card.
- The server now keeps a session-level playable roster state and answers the
  first character-selection packet family:
  `s_userinfo_heros`, `s_card_go_to_fight`, `s_card_go_to_bridge_fight`,
  `s_team_change_hero`, `s_team_change_play`, and
  `s_area_event_switch_hero`.
- Card, bridge-card, team-hero, team-play, and area-event switch requests are
  packet-tested against the recovered schemas. Team hero changes also emit a
  matching `c_scene_hero_change` for the active visible avatar.
- The archived `npc_cfg` table verifies Death Arms at row `5007` with
  `ShapeId=5007`. The server can emit it through `c_scene_npc_create` at a
  clearly labeled local demonstration position near the player spawn.
- Initial map-character emission now uses a typed spawn catalog, so future NPC
  rows and authored placements can be added without hardcoding each packet in
  the scene-entry handler.
- Automated tests cover the protocol codec, bootstrap responses, login/world
  packet flow, starter roster, map-character packet generation, and stateful
  guide/teach/base-station/task/client-stat/world-telemetry exchanges.

## Remaining Compatibility Work

The bootstrap, login, player provisioning, and initial world-entry path is
implemented. The client is not yet a complete playable restoration.

Current limitations:

1. Twenty-nine playable mappings are cataloged and packet-tested through the
   expanded roster path. The default emitted starter roster is still
   intentionally conservative until larger card sets and switch flows are
   validated in controlled client runs. All For One `h1039` and Best Jeanist
   `h1927` still lack matching playable `hero_cfg` rows in the recovered table.
2. The broader initial activity and quest-state packet set has not been
   reconstructed. Guide, teach-finish, base-station, city-level, world-map
   seed, and first task-list/update/sync handlers exist, but a full
   quest/tutorial progression path is not.
3. Death Arms' protocol row is proven, but the current nearby placement is a
   local demonstration coordinate rather than an archived authored placement.
4. The client previously performed a periodic reconnect while reporting that it
   was waiting for `c_time_ping`. The reconnect acknowledgment restores the
   session, after which ping traffic remains stable, but the original waiter
   defect is not fully resolved. Client error reports are now retained in
   world-session state for live validation.
5. Combat, rewards, persistence, and broader inventory systems still require
   protocol-specific state and handlers.

## Character Roadmap

1. Keep the validated starter roster as the compatibility default.
2. Validate the expanded 29-character roster in a controlled client run.
3. Add more verified NPC rows and sanitized authored-placement metadata.
4. Validate character selection and avatar swapping in controlled client runs,
   starting from the packet-tested roster-state handlers.
5. Reconstruct enough quest/activity state to complete the archived tutorial,
   starting from the stateful guide, teach-finish, starter-task, and
   client-stat handlers.

## Known Wire IDs

The recovered CSV IDs are one greater than the actual wire IDs.

| Protocol | Wire ID |
| --- | ---: |
| `s_login_version` | 1 |
| `s_login_reconnect` | 2 |
| `c_login_version` | 3 |
| `c_data_begin` | 5 |
| `c_data_fragment` | 6 |
| `c_data_end` | 7 |
| `c_chunk` | 8 |
| `s_guide_finish` | 38 |
| `s_city_level_click` | 88 |
| `c_team_change_hero` | 142 |
| `c_time_ping` | 215 |
| `s_world_task_pick_prestige` | 224 |
| `c_city_level_click` | 252 |
| `s_login_account_enter` | 275 |
| `c_userinfo_hero_set` | 350 |
| `s_world_task_reward_rate` | 375 |
| `c_card_go_to_fight` | 390 |
| `c_world_task_ignore_auto_finish_tips` | 424 |
| `s_login_player_enter` | 465 |
| `c_world_task_auto_finish` | 500 |
| `c_reconnect_flag` | 502 |
| `c_world_task_info` | 513 |
| `c_base_station_all_info` | 573 |
| `s_card_go_to_fight` | 617 |
| `c_login_player_info` | 654 |
| `s_userinfo_heros` | 744 |
| `c_card_seeinfo` | 780 |
| `s_team_change_play` | 805 |
| `s_scene_enter_end` | 879 |
| `s_area_event_switch_hero` | 903 |
| `s_time_ping` | 989 |
| `s_world_task_ignore_auto_finish_tips` | 999 |
| `s_login_player_add` | 1008 |
| `c_card_go_to_bridge_fight` | 1036 |
| `c_scene_enter_end` | 1077 |
| `c_login_checkstr` | 1138 |
| `c_guide_finish` | 1214 |
| `s_card_go_to_bridge_fight` | 1276 |
| `c_city_level_info` | 1282 |
| `c_scene_npc_create` | 1292 |
| `s_world_task_auto_finish` | 1296 |
| `c_team_change_play` | 1297 |
| `c_scene_enter` | 1369 |
| `c_login_account_info` | 1378 |
| `c_area_event_switch_hero` | 1419 |
| `c_data_merge_to` | 1564 |
| `c_scene_player_info` | 1569 |
| `c_world_task_reward_rate` | 1577 |
| `c_scene_hero_change` | 1644 |

## Client Record

- APK signature verification for the compatibility clone uses v1, v2, and v3.
- Only fixed-width Lua bytecode edits are considered safe for this client.

## Verify

Run the automated test suite from the server package:

```powershell
cd preservation_server
$env:PYTHONPATH = "src"
py -3.12 -m pytest -q
```

The default schema inputs are `allproto_readable.lua` and
`analysis/protocol_ids.csv` in the repository root.
