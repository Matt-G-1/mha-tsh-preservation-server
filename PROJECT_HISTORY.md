# MHA TSH Project History

This public history is intentionally sanitized. It records compatibility
findings and implementation milestones without publishing private environment
details or deployment automation.

## Preservation Scope

The project is an unofficial, noncommercial, clean-room compatibility effort
for the discontinued Android client of *My Hero Academia: The Strongest Hero*.
The repository contains original interoperability code, compact protocol
metadata, tests, and public documentation. It does not distribute original APKs,
OBBs, extracted assets, signing material, credentials, or copyrighted game
content.

## Client Analysis

The archived client was inspected from an untouched source copy. Compatibility
testing uses a separately signed clone so the original installed package remains
unchanged.

Recovered launch and protocol details include:

- Bootstrap endpoints for guest login, server selection, player listing, and
  player creation reporting.
- Axon TCP framing with a seed handshake, rolling XOR streams, checksums, and
  schema-driven payload encoding.
- A protocol ID table where recovered CSV IDs are one greater than the actual
  wire IDs.
- Packet schemas for the login path, role provisioning, scene entry, guide
  completion, base-station initialization, time ping, reconnect, card roster,
  and map-character creation.

## Server Milestones

The clean-room server now supports:

- Local bootstrap responses for the compatibility clone.
- Guest login and server-list flow.
- Empty-account handling and minimal local role provisioning.
- Login version/account/check responses.
- Correct `c_login_player_info` field order:
  `Uid`, `Name`, `Level`, `HostId`, `ServerName`, `CreateTime`.
- Initial user creation and scene-player packets.
- Honei Urban Area scene entry.
- Scene-load completion acknowledgment.
- Starter owned-card inventory.
- Guide-finish and base-station replies sufficient to open the world quest map.
- Time-ping replies and login-level reconnect acknowledgment.
- A verified Death Arms map-character demonstration packet.

## Character Catalog

The supplied raw-rip model list has been translated into a typed catalog:

- 31 playable-model entries from the supplied list.
- 40 map/NPC-model entries.
- 3 chibi-model entries.
- 29 playable entries matched to recovered `hero_cfg` and `shape_info` rows.
- 2 remaining asset-only playable entries: All For One `h1039` and Best
  Jeanist `h1927`.

Recovered table matches corrected two tentative names:

- `h1032` is Mirio Togata.
- `h1998` is an All Might variant.

## Current Direction

The next build series is focused on characters and tutorial completion:

1. Keep the starter roster stable as the default compatibility path.
2. Add an opt-in expanded roster for protocol-verified playable characters.
3. Add tests for expanded card serialization and active-avatar stability.
4. Expand map-character support using recovered NPC rows and sanitized
   placement metadata.
5. Reconstruct enough quest/activity state to complete the archived tutorial.

Private deployment notes are deliberately kept outside this repository.
