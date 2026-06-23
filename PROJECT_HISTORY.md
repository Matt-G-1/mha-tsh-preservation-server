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
- Session-level roster state for active card, active hero, and active shape.
- Hero-list, card fight, bridge-card fight, team-hero, team-play, and
  area-event hero-switch responses grounded on recovered schemas.
- Scene visible-hero updates after team hero changes and deployed-card changes.
- Profile-backed role and active-card state so the selected deployed hero can
  survive a server restart without storing local deployment paths in the repo.
- Guide-finish and base-station replies sufficient to open the world quest map.
- City-level and world-task seed replies that populate the opened world map's
  city/open-map compatibility state.
- Stateful guide, teach-finish, and base-station tracking for the first
  tutorial-practice exchanges.
- A minimal task journal that can list, accept, submit, sync, and acknowledge
  starter task-stage entry through recovered task packet schemas.
- Observed first-guide client telemetry is recorded and used to complete the
  starter task once; this guide/task bridge has now been validated on-device
  through the map-marker tutorial step, including the map opening with visible
  markers after the new world-task seed packets.
- World-task compatibility acknowledgments for city-level click, reward-rate,
  auto-finish-tip preference, auto-finish, and prestige-pick requests.
- Empty-state replies for the first surrounding activity/task panels:
  stage-activity info, activity-shop info, entrust-task list, secret-area task,
  USJ task, offline-PVP task, battlefield-task info, and group-map opening.
- Movement, frame-stat, and client-error telemetry is retained in world-session
  state for live validation and future quest conditions.
- Time-ping replies and login-level reconnect acknowledgment.
- A verified Death Arms map-character demonstration packet.
- An opt-in verified map/NPC demo cast covering Death Arms, Mei Hatsume,
  Kamui Woods, Naomasa Tsukauchi, Mt. Lady, Shota Aizawa, and a U.A.
  Mei Hatsume row.
- Live validation confirmed the demo cast serializes and renders in-world;
  its temporary coordinates are crowded, so the starter map spawn remains the
  compatibility default. The validation cast is deliberately not tied to broad
  map-spawn aliases such as `expanded`.
- An opt-in starter intro stage probe that acknowledges starter task-stage
  entry and sends `c_stage_enter` for the current `zx_battle*` candidate stage,
  plus minimal stage loading/report lifecycle handling for controlled battle
  validation.
- A recovered starter-intro metadata catalog for the original
  `4YOU/1294fd82be3620d3` FLV, the current `zx_battle*` / `zx_lvb*` stage
  candidate cluster, and intro-only school-uniform Midoriya (`hero_cfg` row
  `192`, `NpcId=71104`, `ShapeId=2993`). The media itself remains outside the
  repository.
- The starter-guide intro probe is now deferred until the client reports its
  later WorldMapView telemetry. Live testing showed that injecting
  `c_stage_enter` during `s_guide_finish` or immediately after base-station
  synchronization causes a guide callback timeout. The next narrated-origin
  lead is the local `zx_ruxue*` drama/copyright cluster, not the 40-second
  sludge-villain FLV.
- An opt-in unlocked restoration state uses the recovered agency cap 70 and
  city cap 60, exposes all 26 public playable cards and function IDs, and
  seeds starter task/guide/world completion so development can proceed beyond
  the blocking map-click tutorial while the authentic quest is reconstructed.
- Live validation confirmed that a verified roster card can be deployed from
  the Hero screen, reflected in the world avatar on scene entry, and restored
  after a server restart through the profile store.
- Recovered battle-stage parsing now has a typed server catalog sourced from
  the local QTE/drama index and OBB candidate scan. It includes the starter
  `299301` cluster, the All Might `502601` cluster, 17 additional numeric
  drama-stage candidates, the `zx_battle*` script-only family, and first-pass
  enemy AI profiles/spawns for later fight-style work.
- The character combat layer now has a typed fight-style catalog for every
  verified playable hero, including slot-based move definitions for normal
  attack, Q/W/E/R, dodge, and passive. Skill-level and training responses now
  expose those move slots, and incoming `s_frame_monster_data` is retained for
  enemy AI/state debugging.
- Stage combat reporting now records `s_stage_damage_info`, acknowledges it
  with the recovered empty `c_stage_damage_info`, and converts the client's
  `s_stage_report` into a stateful combat summary. Optional post-battle
  `c_stage_result` packets now reflect submitted stage ID, pass/fail result,
  clear time, stars, simple item echoes, skill levels, combo, damage, and
  monster-kill telemetry instead of static empty result data.
- Fight-style definitions can now map reported battle button counters back to
  the active character's named ATK/Q/W/E/R/dodge/passive move slots for future
  damage tuning and live battle validation.
- Combat resolution now consumes the active roster character, recovered
  fight-style moves, reported stage button counters, client-reported damage,
  and the current recovered stage encounter to produce deterministic per-move
  hit/damage estimates and defeated-target estimates. Numeric recovered stages
  without authored spawn rows also receive generated encounter probes so they
  can be used for controlled playability testing while exact stage tables are
  still being recovered.
- The public playable roster no longer uses generic fallback move pools: each
  of the 26 playable characters has a character-specific ATK/Q/W/E/R/dodge/
  passive set. Extra protocol-verified rows such as Jiro and the art-test All
  Might variant remain recovered/internal evidence instead of public playable
  targets, with tests explicitly preventing Jiro from returning to the public
  roster. Stage combat summaries now distribute resolved damage over the
  active encounter and retain enemy-by-enemy outcome telemetry.
- Recovered bundle strings now annotate the combat catalog with direct
  action/audio evidence for Midoriya/Deku (`lvgu`), Bakugo (`baohao`), Ochaco
  (`yuchazi`), and All Might (`allmight`). All Might now carries recovered
  common attack, Q/W/E/R, dodge, and VO cues from the intro/QTE asset index,
  keeping the starter All Might battle path closer to the original data. The
  local `scripts/derive_combat_action_hints.py` utility reproduces that
  evidence from the recovered analysis JSON and text indexes.
- Parsed `hero_cfg` metadata now annotates every protocol-verified playable
  fight style with its canonical row, shape, skill group, explicit skill IDs
  where present, Q-shape, passive mode, preload effects, recovered `AiName`,
  and non-default `ActionMap` substitutions. The local
  `scripts/derive_hero_combat_metadata.py` utility reproduces this from the
  extracted readable Lua and keeps the parsed IDs separate from unproven live
  packet skill-slot mappings.
- The packed `skill_lvup_cfg` asset now contributes 321 recovered
  `video/skill/*.flv` paths. Fight styles retain compact per-hero skill-video
  evidence for the recovered prefixes and action categories, while the full
  path inventory remains reproducible through
  `scripts/derive_skill_video_hints.py`. Stage combat move summaries now
  carry matching skill-video categories per move where available, so combat
  telemetry can distinguish parsed presentation evidence from reconstructed
  move labels.
- The English `skill_info.lua` packed asset now contributes parsed skill-text
  evidence through `scripts/derive_skill_info_hints.py`. The first promoted
  batch attaches original move strings such as `Detroit Smash`, `Recipro
  Extend`, `Half-Cold Half-Hot`, `Charge Ice Spear`, `Meteor Storm`, `Hawks Q
  open`, `Hawks ult`, `Permeate Uppercut`, and `Dagger Throw` to resolved
  fight-style telemetry without replacing reconstructed button mappings that
  still need stronger packet/animation proof.
- A second `skill_info` promotion adds parser-backed move text for All Might,
  Denki, Kirishima, Asui, Mina, Mineta, Tokoyami, Tamaki, Mirio, and additional
  Stain terms, including `I Am Here!`, `Lightning Bolt`, `Tongue Swipe`,
  `Mina Perfect Dodge QTE`, `Grape Rain`, `Abyssal Talons`,
  `Tentacles Grasp`, `Mirio TogataW`, `Mirio TogataE`, `Aura of Fear`, and
  `Shadowy Surprise`.
- A third conservative skill-info pass reads the cleaner late-roster skill-ID
  neighborhoods and adds original ATK/Q/W/E/R text evidence for WHM Midoriya,
  WHM Bakugo, Nejire, Tamaki, and Mirio, plus Q/W/E/R evidence for WHM
  Todoroki. The extractor now exposes those late-roster skill-ID neighborhoods
  as structured command buckets, giving the runtime labels reproducible
  original-asset evidence beyond simple byte-search matches.
- The remaining public-roster skill-info gaps now have parser-backed terms:
  Ochaco, Dabi, Aizawa, and Ojiro all carry original constants from
  `skill_info.lua`, and Mineta's internal `putao` action tokens are regression
  tested against ATK/Q/W/E/R/dodge/passive move result buckets. Jiro remains
  excluded from the public playable roster.
- A separate support-skill promotion parses the English `hero_supports_cfg.lua`
  asset under `assets/0QIU/17d0df31842d7982`. It records support-skill evidence
  for Shigaraki (`Vicious Contact`), Endeavor (`Exploding Lance`), alternate
  Midoriya (`Smash!`), Hawks (`Downfall`), WHM Midoriya (`WHM Shoot Style`),
  WHM Bakugo (`Turbo Twister`), WHM Todoroki (`Icicle Storm`), Nejire
  (`Wave Blast`), and Tamaki (`Tentacles Grasp`) through
  `scripts/derive_hero_support_skill_hints.py` without mixing support-only
  strings into player move telemetry.
- The English `skill_slot.lua` and `skill_guide.lua` assets now contribute
  original client slot-family labels through `scripts/derive_skill_slot_hints.py`.
  Combat result telemetry now carries labels such as `BaseSkill`, `FirstSkill`,
  `SecondSkill`, `ThirdSkill`, `FinalSkill`, `RollSkill`, `PassiveSkill`,
  `QteBtnSkill`, `Normal ATK Combo`, and `Special Skill`.
- The packed `stage_cfg` assets now have a reproducible string-hint extractor,
  `scripts/derive_stage_cfg_string_hints.py`, which recovers 12 numeric stage
  script names, 51 `zx_*` script names, six `video/zx/*.flv` cinematics, and
  47 stage/event hook tokens. The recovered stage catalog now attaches
  `video/zx/chapter2/ruxue_1.flv`, `video/zx/chapter2/beach_01.flv`, and
  `video/zx/chapter2/touqiu.flv` to their matching enrollment, beach, and
  training-yard route clusters. The follow-up coverage sweep now leaves no
  recovered `stage_cfg` script/video strings unrepresented: `801204` and
  `801206` were promoted as generated numeric stage entries, direct
  `zx_shangyejie1`/`zx_shangyejie3` aliases were added, and the chapter 1
  `zx_2_*` plus `judahua`/`yuniguai_1` videos are tracked as evidence-only
  until their exact route is proven.
- Packed Lua chunk headers now feed `scripts/derive_asset_drama_stage_hints.py`,
  which recovers 1,260 drama script headers and 111 numeric drama-stage groups.
  Ninety-one new concrete stage IDs not already covered by explicit or `zx_*`
  recovery are now represented as enterable `asset_drama_stage_*` catalog
  entries with generated encounters pending authored spawn recovery.
- The English `stage_cfg.lua` constant pool now feeds
  `scripts/derive_stage_cfg_route_hints.py`, recovering 10,440 root constants
  and 215 drama-script route references. Thirty-six high-confidence
  script-to-stage groups are represented as `stage_cfg_route_*` definitions
  where they do not conflict with stronger explicit stage entries, including
  `901008 -> 563903`, `101201_1 -> 571101`, and `zx_touqiu -> 300301`.
  Nearby original route labels are now parsed too, so promoted route stages can
  use recovered names instead of generic numeric labels.
- The English `monster_cfg` asset now contributes parsed enemy evidence through
  `scripts/derive_monster_cfg_hints.py`. High-confidence animation/display-name
  associations are promoted into the stage layer for Nomu, Twice, Faux Villain,
  Hanzo Suiden/water-boss hints, Muscular, and other generated-stage enemies;
  monster frame seeds and stage combat telemetry now expose recovered display
  names alongside internal spawn labels.
- Stage entry handling now covers training, teach-PVP, resource-stage,
  hero-chip, pressure, hero-rank, and daily-stage entry request packets. Those
  requests enter recovered stage definitions when known, generate playable
  encounter probes for unknown positive stage IDs, and can switch the active
  local roster card/hero before sending `c_stage_enter`.
- Stage clears now produce deterministic pass drops, first-clear rewards,
  stars, best clear time, and pass counts. That stage-progress state is saved
  through the local profile store and restored on the next server process.
- Completed stage rewards now also grant saved normal-item counts in the
  profile store, giving later inventory/UI packet work a persistent
  player-data backing store.
- The recovered stage catalog now also tracks numeric `stage500` plus the
  major script-only `zx_ruxue`, USJ, beach, commercial-street, and
  training-yard drama groups. Generated combat encounters now assign
  enemy-specific AI profiles for Nomu, ranged, sludge, mechanical boss,
  training, and melee enemies instead of one generic fallback behavior.
- The parser-backed stage catalog now promotes 51 numeric
  `zx_<stage>_<part>` drama-script clusters into enterable recovered stage
  definitions, including representative candidates `101002`, `404001`, and
  `801201`. Exact authored spawn rows are still future recovery work, so these
  currently use generated encounter probes.
- Fight-style resolution now produces deterministic style-effect telemetry:
  control, resource delta, mobility, defense, pressure, and per-enemy threat
  hints. Stage lifecycle compatibility also covers stage frame reports,
  play-sync echoing, is-back checks, stage leave, and quick-reborn telemetry.
- Stage combat resolution now uses actual encounter HP values from recovered
  and generated spawns when estimating defeated targets. Star scoring now
  distinguishes base pass, full encounter clear, and clean/fast clear, and a
  regression matrix verifies that every protocol-verified playable character
  can resolve a max-level clear against every enterable recovered stage
  candidate.
- Stage-family compatibility now includes stateful resource-stage info,
  pressure-stage detail/finish tracking, USJ stage-record and end-stage
  packets, and daily-stage report results. Generated rewards now distinguish
  base pass, full-clear, and style-pressure bonuses when the client does not
  submit an explicit item list.
- Pressure-stage scores, daily-stage counts, and daily-stage reward item
  grants are now profile-backed, so those stage-family loops survive a fresh
  server process alongside normal stage clears and active-card state.
- Packed `stage_cfg` route neighborhoods now contribute 32 recovered
  stage-to-encounter-group links. Routed stages such as `563903`, `571101`,
  `300401`, and newly promoted `310403` now carry authored enemy group IDs as
  metadata, while exact group-to-monster spawn mapping remains the next
  recovery layer.
- The encounter-group extractor now emits both raw `enemy_group_ids` and
  filtered `combat_enemy_ids`, using recovered `monster_cfg` combat markers to
  separate 73 combat targets from 60 NPC/object/helper IDs across the 133 raw
  group IDs. `BattleStageDefinition` now exposes those filtered combat IDs as
  runtime metadata, and routed encounter generation consumes them before
  falling back to generic probe enemies.
- The next recovery layer now cross-checks those encounter IDs against packed
  `monster_cfg` constants. `scripts/derive_stage_monster_evidence.py` recovers
  133 stage encounter target IDs, marks 73 as combat candidates, filters out
  NPC/object helpers, and lets routed stage candidates spawn recovered enemy
  IDs before using generated fallback encounters.
- Authored spawn-position recovery has started with
  `scripts/derive_stage_spawn_hints.py`. The first conservative pass accepts
  only repeatable `MonsterInfo` and lowercase `monster` drama-command layouts,
  recovers eight coordinate hints across seven stages, and merges those
  positions per enemy ID while preserving generated positions for unparsed
  enemies in the same stage.
- The authored spawn parser now also recognizes compact packed
  name/X/Y/face/enemy tables, bringing recovery to 29 coordinate hints across
  12 stages. Runtime stage generation now uses the full `300401` placement
  table, completed `563701` placements, and additional authored rows from
  stages such as `405252`, `406502`, `561203`, and `563901`.
- A third authored spawn parser pass now scans loose map `MonsterInfo*`
  sections from validated Lua string tags, including packed `Times` coordinate
  runs and keyed `Face` fields in chunks where the root constant reader loses
  alignment. Authored spawn recovery now reaches 49 coordinate hints across 19
  stages, and runtime stages now use recovered layouts for `400115`, `562610`,
  `563903`, and several partially recovered route stages instead of generated
  placeholders.
- Enemy AI assignment now uses parser-backed `monster_cfg` name markers through
  `scripts/derive_enemy_ai_profile_hints.py`. Thirty-three recovered stage
  enemies receive boss, elite, ranged/gun, mechanical, or Nomu profile
  overrides, adding `elite_chaser` and `mechanical_patrol` behaviors alongside
  the existing melee, ranged, boss, Nomu, sludge, and training profiles.
- `StageState` now stores deterministic AI directives whenever a recovered
  encounter is seeded: profile, behavior, BT name, home position, range/leash,
  skill rotation, and combat HP per enemy. The client-facing monster-frame
  seed shape remains unchanged. Combat-summary coverage also checks surviving
  enemies so next-action hints and threat scores stay attached before a full
  clear.
- Combat telemetry now classifies recovered `BATTLE/HERO/...` action and audio
  paths per move command across the extracted asset tree. The recovery script
  currently finds 28 hero action prefixes, maps 27 of them to playable model
  IDs, and the generated `combat_action_hints.py` table feeds 665 recovered
  runtime action paths across 25 playable model IDs through normal-attack,
  Q/W/E/R, dodge, and passive/ability command mapping. Alternate Deku, Small
  Might, and the All Might art-test variant now reuse the matching recovered
  action families; `skillex` and WHM Todoroki zero-based skill names are
  classified into the appropriate ultimate/command slots.
- Internal-token combat recovery now covers Mineta's otherwise-missing action
  family. `scripts/derive_internal_combat_action_hints.py` finds 49 `putao`
  asset tokens, and 24 command-bearing internal hints are promoted into
  ATK/Q/W/E/R/dodge/passive telemetry for `h1020`.

## Character Catalog

The supplied raw-rip model list has been translated into a typed catalog:

- 31 playable-model entries from the supplied list.
- 40 map/NPC-model entries.
- 3 chibi-model entries.
- 30 playable entries matched to recovered `hero_cfg` and `shape_info` rows.
- All For One `h1039` remains asset-only in the recovered table.
- Best Jeanist `h1927` is tracked as support-only, not playable; tests keep
  him out of public playable-card output.

Recovered table matches corrected two tentative names:

- `h1032` is Mirio Togata.
- `h1998` is an All Might variant.

## Current Direction

The next build series is focused on characters and tutorial completion:

1. Keep the starter roster stable as the default compatibility path.
2. Keep expanding live validation over the verified playable roster.
3. Add support-card, costume, and deeper player-data records as their packets
   are observed from the live client.
4. Expand map-character support using recovered NPC rows and sanitized
   placement metadata.
5. Reconstruct enough quest/activity state to complete the archived tutorial,
   starting from stateful guide, teach-finish, starter-task, and client-stat
   handling, then validating the candidate intro stage/QTE battle path.
6. Add the next intro battle/fighter packet layer so school-uniform Midoriya is
   deployed only inside the recovered intro/tutorial stage and regular world
   entry continues to use normal playable Midoriya.

Private deployment notes are deliberately kept outside this repository.
