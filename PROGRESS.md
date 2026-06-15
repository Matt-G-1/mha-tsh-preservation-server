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
  client then opens the archived world quest map.
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
  Midoriya remains the active world avatar.
- An opt-in expanded roster path serializes all 29 protocol-verified playable
  characters in `c_card_seeinfo` while preserving Midoriya as the first active
  card.
- The archived `npc_cfg` table verifies Death Arms at row `5007` with
  `ShapeId=5007`. The server can emit it through `c_scene_npc_create` at a
  clearly labeled local demonstration position near the player spawn.
- Initial map-character emission now uses a typed spawn catalog, so future NPC
  rows and authored placements can be added without hardcoding each packet in
  the scene-entry handler.
- Automated tests cover the protocol codec, bootstrap responses, login/world
  packet flow, starter roster, map-character packet generation, and stateful
  guide/teach/base-station tutorial exchanges.

## Remaining Compatibility Work

The bootstrap, login, player provisioning, and initial world-entry path is
implemented. The client is not yet a complete playable restoration.

Current limitations:

1. Twenty-nine playable mappings are cataloged and packet-tested through the
   expanded roster path. The default emitted starter roster is still
   intentionally conservative until larger card sets are validated in
   controlled client runs. All For One `h1039` and Best Jeanist `h1927` still
   lack matching playable `hero_cfg` rows in the recovered table.
2. The broader initial activity and quest-state packet set has not been
   reconstructed. Guide, teach-finish, and base-station exchanges are now
   stateful, but a full quest/tutorial progression path is not.
3. Death Arms' protocol row is proven, but the current nearby placement is a
   local demonstration coordinate rather than an archived authored placement.
4. The client previously performed a periodic reconnect while reporting that it
   was waiting for `c_time_ping`. The reconnect acknowledgment restores the
   session, after which ping traffic remains stable, but the original waiter
   defect is not fully resolved.
5. Combat, rewards, persistence, and broader inventory systems still require
   protocol-specific state and handlers.

## Character Roadmap

1. Keep the validated starter roster as the compatibility default.
2. Validate the expanded 29-character roster in a controlled client run.
3. Add more verified NPC rows and sanitized authored-placement metadata.
4. Validate character selection and avatar swapping in controlled client runs.
5. Reconstruct enough quest/activity state to complete the archived tutorial,
   starting from the stateful guide and teach-finish handlers.

## Known Wire IDs

The recovered CSV IDs are one greater than the actual wire IDs.

| Protocol | Wire ID |
| --- | ---: |
| `s_login_version` | 1 |
| `s_login_reconnect` | 2 |
| `c_login_version` | 3 |
| `s_guide_finish` | 38 |
| `c_data_begin` | 5 |
| `c_data_fragment` | 6 |
| `c_data_end` | 7 |
| `c_chunk` | 8 |
| `c_time_ping` | 215 |
| `c_base_station_all_info` | 573 |
| `s_login_account_enter` | 275 |
| `s_login_player_enter` | 465 |
| `c_reconnect_flag` | 502 |
| `c_login_player_info` | 654 |
| `c_card_seeinfo` | 780 |
| `s_scene_enter_end` | 879 |
| `s_time_ping` | 989 |
| `s_login_player_add` | 1008 |
| `c_scene_enter_end` | 1077 |
| `c_login_checkstr` | 1138 |
| `c_guide_finish` | 1214 |
| `c_scene_npc_create` | 1292 |
| `c_scene_enter` | 1369 |
| `c_login_account_info` | 1378 |
| `c_data_merge_to` | 1564 |
| `c_scene_player_info` | 1569 |

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
