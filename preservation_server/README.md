# MHA TSH Preservation Server

This directory contains a clean-room compatibility server for the archived
Android client in `../phone_dump`.

Milestones:

1. Reproduce the Axon protocol framing and schema encoding.
2. Serve the launch configuration and server list locally.
3. Implement login, local player provisioning, initial state, scene entry, and
   scene-load completion.
4. Build and verify a separately signed test client that targets the local
   services.

The original APK and OBB files are treated as read-only evidence.

## Package Overview

The TCP service implements the native five-byte seed handshake, rolling XOR,
frame checksum, schema-driven payload codec, version/account responses, player
creation response, login-check response, initial user/scene packets, scene-load
completion, a stateful seven-hero card roster, first-pass character selection
responses, verified map NPC packet generation, guide-finish acknowledgment,
teach-finish acknowledgment, base-station initialization, city/world-task map
seed packets, starter task listing and updates, observed first-guide
client-stat tracking, optional starter intro stage-entry probing, stage loading
and report handling, beginner quest city-level progression, empty-state
replies for early activity/task panels, world-session movement/frame/error
tracking, time-ping replies, and the login-level reconnect acknowledgment.
Unknown client messages are decoded and logged for iterative compatibility
work.

By default, the server advertises a minimal local role so the archived client
constructs its required `clsUserData` record before `c_login_ok`. Set
`MHATSH_AUTO_PROVISION_ROLE=0` to exercise the empty-account creation branch.
`MHATSH_PING_RESPONSE_DELAY` controls the small delay that avoids a
callback-registration race in the archived client. It defaults to `0.05`
seconds. `MHATSH_GUIDE_RESPONSE_DELAY` applies the same default delay to guide
completion acknowledgments. Starter scene entry sends no NPCs by default; accepting starter task
`1301` sends the verified Death Arms quest NPC. `MHATSH_SEND_MAP_CHARACTERS=0`
disables scene-entry map-character packets without disabling scene entry.
`MHATSH_MAP_SPAWN_MODE=tutorial` restores the Death Arms quest spawn at scene
entry for controlled testing, and `MHATSH_MAP_SPAWN_MODE=demo_cast` enables the
opt-in seven-NPC packet-validation cast. These modes are not
starter-area-authored content and are intentionally separate from expanded
playable roster testing.

The client now reaches Honei Urban Area, renders Midoriya and its world HUD,
and opens the world quest map. The server's initial owned-card roster contains
Midoriya, Bakugo, Iida, Ochaco, Todoroki, Momo, and Denki. Death Arms is now
quest-gated behind starter task acceptance; the opt-in demo-cast mode
serializes Death Arms plus six additional verified NPC rows. The catalog
contains 30 protocol-verified playable
mappings; only All For One `h1039` remains asset-only in the playable list.
Best Jeanist `h1927` is tracked separately as a support character. The roster
and NPC additions pass packet-level tests. The roster
now tracks active card and active visible hero state for user-info,
card-fight, bridge-fight, team-change, and area-event switch requests. Death
Arms visibly rendered beside Midoriya, the seven-NPC demo-cast mode rendered
in controlled validation, the active starter card state was accepted, and the
map-marker guide step completed through the task/guide/base-station/world-task
handlers in controlled on-device runs. The demo-cast coordinates are crowded
and should be treated as temporary validation data, not starter-area placement.
The world map opens with visible markers after the city-level and open-map seed
packets. The server now also answers several early side-panel/task requests and
character-menu requests with schema-correct empty state so new UI probes fail
less abruptly while real quest, skill, gear, rank, and support-card data is
reconstructed. The client still performs one initial ping-waiter reconnect,
then remains stable through the implemented reconnect acknowledgment.

For post-tutorial restoration testing, the server also has an opt-in unlocked
profile. Set `MHATSH_ROSTER_MODE=verified`, `MHATSH_PLAYER_LEVEL=70`,
`MHATSH_HERO_LEVEL=70`, `MHATSH_CITY_LEVEL=60`,
`MHATSH_SKIP_STARTER_QUEST=1`, and `MHATSH_UNLOCK_ALL_FUNCTIONS=1`. This sends
all 30 protocol-verified playable cards, seeds starter task and guide `1301` as
finished, seeds map guide `1410`/set `12`, suppresses its tutorial NPC and map
overlay, reports the starter world-task finish row, and answers function-open
queries as unlocked. Level 70 and city level 60
come from the recovered client configuration; `TopLevel` remains zero because
it is separate post-cap progression. The level-1 path remains the default for
intro and quest reconstruction.

Set `MHATSH_INTRO_STAGE_MODE=starter` for controlled testing of the current
starter-intro battle candidate. This sends `c_stage_enter` for candidate stage
`299301` with drama enabled. By default it waits for a task-stage request; set
`MHATSH_INTRO_STAGE_TRIGGER=starter_guide` to probe from the observed guide
`1301` completion telemetry instead. The starter-guide trigger is queued until
the client later reports `WorldMapView`; live tests timed out when the stage
packet was injected during either `s_guide_finish` or the immediately following
base-station/city/world-task synchronization.
The default remains disabled until the candidate is validated on-device.
`mhatsh_server.intro` records the recovered starter recap FLV metadata and the
intro-only school-uniform Midoriya row (`ShapeId=2993`) so later battle/fighter
packet work can deploy that costume inside the intro without changing normal
world-entry Midoriya.

See `../PROGRESS.md` for the exact verified state and remaining compatibility
work.

## Test

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest -q
```

Public documentation intentionally omits private deployment, network routing,
and device-control instructions.
