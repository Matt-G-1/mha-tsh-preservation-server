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
client-stat tracking, empty-state replies for early activity/task panels,
world-session movement/frame/error tracking, time-ping replies, and the
login-level reconnect acknowledgment.
Unknown client messages are decoded and logged for iterative compatibility
work.

By default, the server advertises a minimal local role so the archived client
constructs its required `clsUserData` record before `c_login_ok`. Set
`MHATSH_AUTO_PROVISION_ROLE=0` to exercise the empty-account creation branch.
`MHATSH_PING_RESPONSE_DELAY` controls the small delay that avoids a
callback-registration race in the archived client. It defaults to `0.05`
seconds. `MHATSH_SEND_MAP_CHARACTERS=0` disables local demonstration NPC
spawns without disabling scene entry. `MHATSH_MAP_SPAWN_MODE=demo_cast`
enables the opt-in seven-NPC packet-validation cast for controlled testing.
This mode is not starter-area-authored content and is intentionally separate
from expanded playable roster testing.

The client now reaches Honei Urban Area, renders Midoriya and its world HUD,
and opens the world quest map. The server's initial owned-card roster contains
Midoriya, Bakugo, Iida, Ochaco, Todoroki, Momo, and Denki. Death Arms is sent
through `c_scene_npc_create` at an explicitly local demonstration position by
default; the opt-in demo-cast mode serializes Death Arms plus six additional
verified NPC rows. The catalog contains 30 protocol-verified playable
mappings; only All For One `h1039` and Best Jeanist `h1927` remain
asset-only. The roster and NPC additions pass packet-level tests. The roster
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

See `../PROGRESS.md` for the exact verified state and remaining compatibility
work.

## Test

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest -q
```

Public documentation intentionally omits private deployment, network routing,
and device-control instructions.
