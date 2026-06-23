# MHA TSH Preservation Progress

Last updated: 2026-06-23

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
- Starter scene entry no longer emits the local Death Arms validation spawn by
  default. Accepting starter task `1301`, or completing the same starter-guide
  bridge through observed `s_client_stat`/`s_guide_finish`, now sends the
  verified Death Arms quest NPC through `c_scene_npc_create`, keeping the city
  spawn clean until the beginner quest is active.
- Completing beginner guide/task `1301` now emits `c_city_level_add_exp`,
  `c_city_level_up`, refreshed `c_city_level_info`, and refreshed
  `c_world_task_info`, marking map `1000` task `1301` finished and moving the
  local city-level state to level 2.
- A controlled on-device run of the current server code validated the starter
  task bridge live: tapping the highlighted map marker produced
  `s_client_stat` `[1, 1301, 10011]`, `s_guide_finish` for guide `1301`,
  `s_guide_drama`, and `s_base_station_all_info`; the server sent the Death
  Arms quest NPC (`Id=5007`, `Uid=20001`) before the completion packets, and the
  client accepted `c_scene_npc_create`, `c_task_info_update`, `c_guide_finish`,
  `c_base_station_all_info`, `c_city_level_info`, and `c_world_task_info`, then
  opened the world map UI with visible map markers.
- World-map compatibility handlers now acknowledge city-level clicks,
  world-task reward-rate requests, auto-finish-tip preference changes,
  world-task auto-finish requests, and prestige reward picks through recovered
  packet schemas.
- Empty-state compatibility handlers now cover the first surrounding
  activity/task panels that can be reached from world UI probes:
  stage-activity info, activity-shop info, entrust-task list, secret-area task,
  USJ task, offline-PVP task, battlefield-task info, and group-map opening.
- World-session telemetry now records player movement (`s_scene_move`),
  frame-stat heartbeats (`s_client_stat_frame`), and client error reports
  (`s_client_error`) without sending unsafe extra replies.
- Unhandled decoded client messages are retained in the session world state,
  giving controlled live runs a concrete protocol to-do list without sending
  speculative responses.
- The world HUD, minimap, controls, tutorial prompt, and local ping indicator
  render on-device during controlled testing.
- `s_time_ping` receives an echoed `c_time_ping` response.
- A replacement TCP session receives `c_reconnect_flag` after
  `s_login_reconnect`, restoring the local account and player identity.
- The supplied AXMD raw-rip list plus `en_hero_cfg` evidence is represented in
  a typed catalog covering 31 playable models, 1 support model, 40 map/NPC
  models, and 3 chibi models.
- Thirty of the 31 playable model entries have recovered `hero_cfg` rows and
  independently matched `shape_info` model paths. The remaining asset-only
  playable entry is All For One `h1039`; Best Jeanist `h1927` is tracked
  separately as support-only.
- The recovered tables correct two tentative names in the supplied list:
  `h1031` is Tamaki Amajiki, `h1032` is Mirio Togata, and `h1998` is an All
  Might art-test variant.
- The initial `c_card_seeinfo` roster contains a validated starter set by
  default. In verified-roster mode, deployed cards now drive the active scene
  avatar through `c_card_go_to_fight`, `c_scene_hero_change`, and a refreshed
  `c_scene_player_info` payload.
- An opt-in expanded roster path serializes the 26 public playable characters
  in `c_card_seeinfo` while preserving Midoriya as the first active card. The
  extra protocol-verified config rows for Small Might, Jiro, alternate Deku,
  and the All Might art-test variant are retained as recovered/internal
  evidence instead of being treated as playable roster targets. Regression
  tests now explicitly keep Jiro out of the public playable roster and Best
  Jeanist out of playable-card serialization as support-only data.
- The server now keeps a session-level playable roster state and answers the
  first character-selection packet family:
  `s_userinfo_heros`, `s_card_go_to_fight`, `s_card_go_to_bridge_fight`,
  `s_team_change_hero`, `s_team_change_play`, and
  `s_area_event_switch_hero`.
- Card, bridge-card, team-hero, team-play, and area-event switch requests are
  packet-tested against the recovered schemas. Team hero changes also emit a
  matching `c_scene_hero_change` for the active visible avatar.
- Deployed-card state is now profile-backed. The server records the selected
  card per account, reloads it on the next server process, and uses it for
  `c_user_create`, `c_card_seeinfo`, and `c_scene_player_info` scene entry.
- Live validation on the local mobile client confirmed that deploying a WHM
  Bakugo card (`CardUid=1024`, `ShowHeroId=1281`) changes the city avatar after
  reconnect, then survives a full server restart through the profile store.
- The archived `npc_cfg` table verifies Death Arms at row `5007` with
  `ShapeId=5007`; additional recovered NPC rows now verify Mei Hatsume,
  Kamui Woods, Naomasa Tsukauchi, Mt. Lady, Shota Aizawa, and a U.A. Mei
  Hatsume row.
- Initial map-character emission now uses a typed spawn catalog, so future NPC
  rows and authored placements can be added without hardcoding each packet in
  the scene-entry handler. The compatibility default still emits only Death
  Arms, while the opt-in `demo_cast` spawn mode serializes all seven verified
  demonstration NPCs for controlled testing.
- Controlled on-device validation of `demo_cast` confirmed that all seven
  verified NPC rows can be serialized through `c_scene_npc_create` and render
  in-world. The current demo coordinates are intentionally temporary and are
  too crowded for normal play, so `starter` remains the default spawn mode.
  Broad names such as `expanded` are intentionally not accepted for map-spawn
  mode; expanded playable rosters must not implicitly add validation-only
  NPCs to the starter area.
- Intro-video research confirms the current world-entry path starts after the
  archived game's pre-city intro/tutorial material. The server now has opt-in
  login-drama probing support: `c_login_account_info` can request drama via
  `DramaFlag`/`DramaStep`, `s_login_drama` is recorded and can return
  `c_scene_play_drama` when a recovered `DramaName` is configured, and
  `s_login_drama_finish` records completed intro stages.
- Local client asset research confirms the QTE buttons are driven by drama
  scripts, with `CreateQte` available in the recovered drama configuration.
  The strongest current starter-battle candidate is the `zx_battle*` /
  `zx_lvb_*` cluster around stage-like ID `299301`; the server now has an
  opt-in `c_stage_enter` probe for this path via `MHATSH_INTRO_STAGE_MODE`.
- Live testing showed the current starter-map route does not send
  `s_task_enter_stage`; it completes guide `1301` through `s_client_stat` and
  `s_guide_finish`. The intro-stage probe can therefore be configured to fire
  on the starter-guide signal with `MHATSH_INTRO_STAGE_TRIGGER=starter_guide`.
  The live client timed out when `c_stage_enter` was injected directly inside
  the `s_guide_finish` callback and again immediately after base-station sync.
  The server now queues that trigger until the later WorldMapView telemetry
  tuple `[0, 1404, 10351]` is observed.
- An opt-in unlocked restoration profile now sends all 26 public playable
  cards, account/card level 70, city level 60, all function-open IDs, and
  starter task/guide/world-task completion state. The recovered client
  explicitly identifies agency level 70 and city level 60 as the respective
  caps. `TopLevel` remains zero because it is separate post-cap progression.
- Packet tests verify that the unlocked profile suppresses the beginner NPC,
  cannot re-run task `1301`, serializes every verified card, and can switch the
  active player to the last verified roster entry.
- The latest packet tests also cover active-card persistence across fresh
  server instances and the deploy-time scene-player refresh used by the live
  client.
- Live tracing identified map-selection guide `1410` in guide set `12` as the
  post-scene overlay that survives task `1301` completion. The unlocked profile
  now seeds both guides before scene entry to avoid the client's guide callback
  race and reconnect.
- Live packet timing showed the local `c_guide_finish` acknowledgment arriving
  in the same millisecond as `s_guide_finish`; the archived client then timed
  out despite receiving the packet. Guide acknowledgments now use the same
  small callback-registration delay as time-ping replies.
- Stage lifecycle handling now covers `s_stage_finish_loading` with
  `c_stage_finish_loading`, records `s_stage_damage_info` and `s_stage_report`,
  acknowledges damage-info polling, and can emit drop/result/end packets for
  controlled post-battle testing. The result packet now derives stage ID,
  result, time, star list, simple reward echoes, combo, damage, skill-level,
  and monster-kill summary state from the client's submitted battle report.
- Fight-style data can now translate reported stage button counters back into
  per-character move usage, e.g. ATK/Q/W/E/R mapped onto the active hero's
  named move slots. This is intentionally internal telemetry for now, not a
  guessed wire-field extension.
- The combat layer now resolves those move counters into deterministic
  per-move hit and damage estimates, scaled back to the client's reported
  total damage when available. Stage-result handling passes the active roster
  character and current recovered stage into that resolver, so post-battle
  summaries can identify the active hero's named moves and estimated defeated
  targets.
- All 26 public playable characters now have non-generic
  character-specific ATK/Q/W/E/R/dodge/passive move pools in the combat
  catalog. Tests enforce that verified playable styles no longer fall back to
  the generic default tuple.
- The combat catalog preserves recovered `BATTLE/HERO/...` action/audio hints
  and now maps representative paths into runtime move results for most
  verified playable styles, not just the original Midoriya/Bakugo/Ochaco/All
  Might set. The action classifier covers canonical `Qskill`/`Wskill`/
  `Eskill`/`Rskill` names plus hero-specific `skill01`/`skill02`/`skill03`/
  `skill04` naming, normal-attack folders, dodge, and passive/ability assets.
  `scripts/derive_combat_action_hints.py` now scans the extracted asset tree
  plus analysis indexes and reproduces 28 recovered hero action prefixes, 27
  of them mapped to playable model IDs. The generated
  `combat_action_hints.py` evidence table promotes that into 665 recovered
  runtime action paths across 25 playable model IDs. The runtime also aliases
  alternate Deku, Small Might, and the All Might art-test variant to the
  matching recovered action families, and handles recovered `skillex`/WHM
  Todoroki zero-based skill naming.
- Mineta now has parsed internal action/audio hints despite lacking clean
  `BATTLE/HERO/...` paths. `scripts/derive_internal_combat_action_hints.py`
  recovers 49 `putao` tokens from the extracted asset tree, and the promoted
  `combat_internal_action_hints.py` table maps 24 command-bearing Mineta
  tokens onto ATK/Q/W/E/R/dodge/passive move results. Momo's Q evidence is now
  resolved through a narrow model-specific override: her skill text and video
  catalog expose Q/`Q - Weapon Creation`, while the recovered action path is
  named `BATTLE/HERO/babaiwan/skills/Wskill_create`. All 26 public playable
  characters now have recovered ATK/Q/W/E/R action evidence. Jiro has
  `bot_dianqi`/`character/h1018` config evidence, but she is tracked as
  non-playable recovered data rather than a roster-completion blocker.
- The combat catalog now also attaches canonical `hero_cfg` combat metadata
  for every protocol-verified playable character: config row, `ShapeId`,
  `SkillGroupId`, `SkillIds`, `QShapeId`, passive activation mode, preload
  effects, recovered `AiName`, and non-default `ActionMap` substitutions.
  `scripts/derive_hero_combat_metadata.py` reproduces this layer from
  `C:\Users\MatMa\Downloads\en_hero_cfg_readable.lua`; these IDs are retained
  as parsed evidence and are not yet substituted into live button-skill packet
  fields until a direct packet mapping is proven.
- The packed `skill_lvup_cfg` asset now yields 321 recovered
  `video/skill/*.flv` paths. The combat catalog stores compact per-hero skill
  video evidence for 27 direct video prefixes plus Small Might sharing the All
  Might `ouermaite` set: recovered prefix, path count, and action categories
  such as ATK/Q/W/E/R/dash/break/rush/pre/QTE/ability. Mineta (`h1020`) does
  not currently have matching skill-video strings in that asset among the
  public playable roster. Jiro (`h1018`) and the art-test All Might variant
  (`h1998`) also lack matches, but they are retained as non-public/internal
  recovered rows. `scripts/derive_skill_video_hints.py` reproduces the full
  path inventory from the packed asset.
- The English `skill_info.lua` packed asset now has a parser-backed text layer
  through `scripts/derive_skill_info_hints.py`. The first promoted batch
  covers original move/hero strings for Midoriya (`Smash`, `One For All`,
  `Detroit Smash`), Bakugo (`Extra Explosion`), Iida (`Recipro Extend`),
  Todoroki (`Half-Cold Half-Hot`, `Charge Ice Spear`), Momo (`Meteor Storm`,
  `Q - Weapon Creation`), Hawks (`Hawks Q open`, `Hawks W`, `Hawks E`,
  `Hawks ult`, passive/normal attack labels), Endeavor, and Stain
  (`Permeate Uppercut`, `Dagger Throw`). These terms are attached to resolved
  move telemetry as evidence without overwriting reconstructed move names where
  the exact command mapping is still partial.
- A second `skill_info` pass now promotes additional original move text for
  All Might (`I Am Here!`), Denki (`Lightning Bolt`), Kirishima's Q/W/aeration
  labels, Asui (`Tongue Swipe`), Mina's Q/W/E/R/perfect-dodge labels, Mineta's
  firing/bounce/grape-rain labels, Tokoyami (`Abyssal Claw`, `Shadow Zone`,
  `Abyssal Talons`), Tamaki (`Tentacles Grasp`), Mirio's W/E labels, and
  Stain's `Aura of Fear`, `Permeate Uppercut`, `Shadowy Surprise`, and
  `Vigor` evidence. These are parser-backed annotations for combat telemetry,
  not a claim that every packet-side skill slot is fully proven yet.
- A third conservative `skill_info` pass now uses the cleaner late-roster
  skill-ID neighborhoods to annotate WHM Midoriya, WHM Bakugo, WHM Todoroki,
  Nejire, Tamaki, and Mirio. WHM Midoriya, WHM Bakugo, Nejire, Tamaki, and
  Mirio now have original ATK/Q/W/E/R text evidence attached to combat
  telemetry; WHM Todoroki has Q/W/E/R evidence and only ATK remains unlabeled
  at this layer. The public-roster original-text gap count dropped from 25 to
  20 characters with at least one missing ATK/Q/W/E/R label. The extractor now
  also parses structured skill-ID neighborhoods for `h1027` through `h1032`,
  classifies human-readable labels into command buckets, and verifies that the
  promoted late-roster terms are present in the original packed constants.
- A separate support-skill pass now parses the packed English
  `hero_supports_cfg.lua` asset at
  `analysis/mediafire_20260620/apk_extract/assets/0QIU/17d0df31842d7982`.
  It records support-skill text for Shigaraki (`Vicious Contact`), Endeavor
  (`Exploding Lance`), alternate Midoriya (`Smash!`), Hawks (`Downfall`), WHM
  Midoriya (`WHM Shoot Style`), WHM Bakugo (`Turbo Twister`), WHM Todoroki
  (`Icicle Storm`), Nejire (`Wave Blast`), and Tamaki (`Tentacles Grasp`)
  without treating support-only strings as player button-skill evidence.
  `scripts/derive_hero_support_skill_hints.py` reproduces that extraction.
- The packed English `skill_slot.lua` and `skill_guide.lua` assets now have a
  small extractor, `scripts/derive_skill_slot_hints.py`. Resolved combat
  telemetry carries original client slot-family labels such as `BaseSkill`,
  `FirstSkill`, `SecondSkill`, `ThirdSkill`, `FinalSkill`, `RollSkill`,
  `PassiveSkill`, `QteBtnSkill`, `Normal ATK Combo`, and `Special Skill`
  alongside reconstructed move names and parsed skill text.
- Resolved combat telemetry now attaches those recovered skill-video
  categories to individual move results where the categories exist. For
  example, All Might and Midoriya ATK reports carry ATK/BREAK/RUSH video
  evidence, R reports carry R/QTE evidence, dodge reports carry DASH evidence,
  and characters without matching skill-video strings remain explicitly empty.
- Recovered battle action/audio paths are now classified per command and
  attached to individual move results as `ActionHints`. The current parsed
  action layer covers Midoriya, Bakugo, All Might, and Ochaco, mapping recovered
  `commonATK`, `Qskill`, `Wskill`, `Eskill`, `Rskill`, `dodge`, and `ability`
  paths onto ATK/Q/W/E/R/dodge/passive combat telemetry.
- The packed `stage_cfg` assets now have a repeatable string-hint extractor:
  `scripts/derive_stage_cfg_string_hints.py`. The current extraction finds 12
  numeric `stage*` scripts, 51 `zx_*` scripts, six `video/zx/*.flv` cinematic
  assets, and 47 stage/event hook tokens such as `MonsterDeath` and
  `DramaEndFinishEvent`. Cleanly anchored videos are now attached to recovered
  stage groups: `ruxue_1` for the U.A. enrollment intro, `beach_01` for the
  beach event cluster, and `touqiu` plus `zx_touqiu` for the training-yard
  ball-throw route. The two chapter 1 videos remain parser evidence until
  their exact route can be tied down. A follow-up coverage sweep now leaves no
  `stage_cfg` script/video strings unrepresented: `801204`/`801206` numeric
  script stages were added, direct `zx_shangyejie1`/`zx_shangyejie3` variants
  were added to the commercial street cluster, and the odd `zx_2_*` chapter 1
  scripts plus `judahua` and `yuniguai_1` videos are tracked in an
  evidence-only stage definition.
- Packed Lua chunk headers now have a broader drama-stage extractor:
  `scripts/derive_asset_drama_stage_hints.py`. It currently finds 1,260
  drama scripts and 111 numeric drama-stage groups. Ninety-one additional
  concrete stage IDs not already covered by explicit or `zx_*` recovery were
  promoted into the runtime catalog as `asset_drama_stage_*` entries, including
  `400301`, `520001`, and `901008`; these use generated encounters until their
  authored enemy placements are recovered.
- The packed English `stage_cfg.lua` constant pool now has a route extractor:
  `scripts/derive_stage_cfg_route_hints.py`. It recovers 10,440 root constants
  and 215 drama-script route references, then promotes 36 high-confidence
  script-to-stage groups into the runtime catalog where they do not conflict
  with stronger explicit definitions. This corrects several numeric-looking
  script assumptions: for example, `901008` routes to real stage `563903`,
  `101201_1` routes to `571101`, and `zx_touqiu` routes to `300301`. The same
  extractor now recovers nearby original route labels, and promoted
  `stage_cfg_route_*` definitions use those labels when no stronger stage
  definition already owns the ID.
- The same packed `stage_cfg.lua` data now has an encounter-group extractor:
  `scripts/derive_stage_cfg_encounter_hints.py`. It recovers 32
  stage-to-encounter group links from script neighborhoods, adds the
  `310403`/`zx_usj_03002` route, and attaches authored enemy group IDs to
  runtime candidates such as `300401`, `563903`, and `571101`. The extractor
  now also emits parser-backed `combat_enemy_ids` by cross-checking the raw
  group IDs against recovered `monster_cfg` combat markers; current output
  separates 73 combat IDs from 60 NPC/object/helper IDs across 133 raw group
  IDs. Runtime `BattleStageDefinition` entries now expose that filtered
  `combat_enemy_ids` layer separately from raw `enemy_group_ids`, and
  encounter generation uses the filtered combat list first so helper rows do
  not become accidental battle targets.
- Those stage encounter IDs are now cross-checked against packed
  `monster_cfg` evidence through `scripts/derive_stage_monster_evidence.py`.
  The extractor recovers 133 target IDs, marks 73 as combat candidates, and
  filters out NPC/object helpers such as the `563903` female student, shield,
  and empty-model rows. Runtime stage spawns now use recovered combat enemy IDs
  for routed candidates before falling back to generated probes; the recovered
  `56390302` ranged row now uses the ranged-pressure AI profile.
- A first conservative authored-position pass now parses repeatable
  `MonsterInfo` and lowercase `monster` drama-command layouts through
  `scripts/derive_stage_spawn_hints.py`. It recovers eight coordinate hints
  across seven stages, including both `571101` combat rows and one authored
  spawn each for stages `404201`, `406305`, `406505`, `561203`, `561304`, and
  `563701`. Runtime stage generation merges those coordinates per enemy ID
  without dropping the remaining recovered enemies in partially parsed stages.
- A second authored-position pass now recognizes compact name/X/Y/face/enemy
  tables in packed stage chunks. The parser recovers 29 authored coordinate
  hints across 12 stages, including a full nine-enemy placement table for
  `300401`, completed `563701` positions, and additional rows for `405252`,
  `406305`, `406502`, `406505`, `561113`, `561203`, and `563901`. Runtime stage
  generation now prefers those parsed positions over generated placeholders
  while still keeping generated fallback rows for enemies whose authored
  positions are not recovered yet.
- A third authored-position pass now scans validated Lua string-tag boundaries
  for loose map `MonsterInfo*` sections whose full chunks defeat the root
  constant reader. It recovers packed `Times` coordinate runs and keyed `Face`
  values, raising authored placement recovery to 49 coordinate hints across 19
  stages. Runtime coverage now includes full authored spawn layouts for
  `400115`, `562610`, and `563903`, plus additional recovered rows for
  `404201`, `405103`, `405302`, `561211`, `561304`, and `562504`.
- The English `monster_cfg` packed asset now has a conservative hint extractor:
  `scripts/derive_monster_cfg_hints.py`. It scans animation-key neighborhoods
  for display-name candidates and feeds a typed monster evidence layer for
  high-confidence enemies such as Nomu (`3007`), Twice (`2470`/`2471`/`2472`),
  Faux Villain (`3005`), Hanzo Suiden/USJ water-boss evidence (`3006`), and
  Muscular (`3016`). Generated monster frame seeds now prefer recovered display
  names for `Info.Alias`, and combat telemetry returns both the internal spawn
  label and recovered display name.
- Stage enemy AI assignment now has a parser-backed profile pass:
  `scripts/derive_enemy_ai_profile_hints.py` consumes recovered
  `monster_cfg` stage-enemy names and promotes 33 AI overrides from stable
  name markers such as BOSS, elite, ranged/gun, mechanical, and Nomu. Runtime
  stage spawns now distinguish `elite_chaser` and `mechanical_patrol` enemies
  in addition to the existing melee, ranged, boss, Nomu, sludge, mechanical
  boss, and training profiles. Current enterable-stage spawn coverage includes
  boss, elite, mechanical, ranged, Nomu, sludge, and training behaviors instead
  of collapsing nearly every parsed stage enemy into the generic melee profile.
- Seeding a recovered stage now also stores per-enemy AI directives in
  `StageState`: enemy ID, display alias, profile, behavior, BT name, home
  coordinates, attack range, leash radius, skill rotation, and combat HP. This
  keeps the client monster-frame seed schema stable while giving battle
  simulation and debugging code deterministic enemy behavior data. Combat
  summary tests also cover surviving enemies, including their next action hint
  and threat score, so AI behavior remains visible even when an encounter is
  not fully defeated.
- Stage combat summaries now distribute estimated damage across the active
  stage encounter and produce enemy-by-enemy outcome telemetry: target UID,
  enemy ID, AI profile, HP, damage taken, defeated state, and last active move.
- Every numeric recovered battle-stage candidate now has a playable encounter
  fallback through generated stage spawns when no authored spawn row has been
  recovered yet. Authored/identified spawns, such as the starter intro and All
  Might probes, still take priority.
- The server now accepts additional combat-entry request families and routes
  them to `c_stage_enter`: `s_training_enter`, `s_teach_pvp_enter`,
  `s_resource_stage_enter`/`s_resource_stage_reenter`,
  `s_herochip_stage_enter`, `s_pressure_stage_enter`,
  `s_hero_rank_stage_enter`, and `s_act_daily_stage_enter`. Recovered stage IDs
  use typed catalog metadata; unknown positive stage IDs receive generated
  playable encounters. Hero/card IDs in those requests can switch the active
  roster character before entering the stage when the card exists locally.
- Stage clears now emit deterministic pass drops, first-clear rewards, stars,
  best clear time, and pass counts. The local profile store persists that
  stage-progress state across server restarts.
- Completed stage rewards now also grant saved normal-item counts in the
  profile store, giving later inventory/UI packet work a persistent
  player-data backing store.
- The recovered stage catalog now tracks numeric `stage500` plus major
  script-only `zx_ruxue`, USJ, beach, commercial-street, and training-yard
  drama groups. Generated fallback encounters now select enemy-specific AI
  profiles for Nomu, ranged, sludge, mechanical boss, training, and melee
  enemies.
- Parsed numeric `zx_<stage>_<part>` drama-script clusters are now promoted
  into enterable stage definitions instead of remaining loose script evidence.
  This adds 51 recovered stage IDs, including `101002`, `404001`, and
  `801201`, while keeping exact authored spawns as future parse work.
- Fight-style resolution now produces deterministic style-effect telemetry:
  control, resource delta, mobility, defense, pressure, and per-enemy threat
  hints. Stage lifecycle compatibility now covers stage frame reports,
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
- The starter-intro evidence catalog now records the original
  `4YOU/1294fd82be3620d3` FLV metadata, candidate `zx_battle*` / `zx_lvb*`
  stage scripts, and intro-only school-uniform Midoriya from `hero_cfg` row
  `192` (`NpcId=71104`, `ShapeId=2993`, preload shapes `2993` and `2994`).
  Automated tests keep that costume out of the normal starter and verified
  playable rosters.
- The user-supplied All Might silhouette/subtitle screenshot did not match the
  recovered `1294fd82be3620d3` FLV frames. The closer local leads are the
  `zx_ruxue*` drama scripts and copyright-prefixed `zx_ruxue` assets in the
  intro/QTE asset index.
- Automated tests cover the protocol codec, bootstrap responses, login/world
  packet flow, starter roster, map-character packet generation, and stateful
  guide/teach/base-station/task/client-stat/stage/world-telemetry exchanges.

## Remaining Compatibility Work

The bootstrap, login, player provisioning, and initial world-entry path is
implemented. The client is not yet a complete playable restoration.

Current limitations:

1. Thirty playable mappings are cataloged and packet-tested through the
   verified roster path, and visible roster deployment has been live-validated
   through world entry. The default starter roster remains available as the
   conservative compatibility path. All For One `h1039` still lacks a matching
   playable `hero_cfg` row in the recovered table.
2. The broader initial activity and quest-state packet set has not been
   fully reconstructed. Guide, teach-finish, base-station, city-level,
   world-map seed, first task-list/update/sync handlers, and several
   empty-state activity/task-panel replies exist, but a full quest/tutorial
   progression path is not.
   The earlier login-drama path and the newer stage-enter intro probe are still
   candidate-driven until controlled client logs confirm the exact intro stage
   and transition behavior.
   The school-uniform Midoriya shape is cataloged for intro-only use, but the
   stage/fighter packet layer that would deploy it during the back-alley or
   All Might tutorial scene still needs to be implemented and live-tested.
3. Seven map/NPC protocol rows are proven and render in the client, but the
   current nearby placements are local demonstration coordinates rather than
   archived authored placements. The `demo_cast` placement is visibly crowded,
   is not starter-area-authored content, and should not be used for broader
   tutorial/UI validation.
4. The client can still report a one-time `s_time_ping` timeout during scene
   startup even though the server log shows matching `c_time_ping` replies.
   The reconnect acknowledgment restores the session, after which ping traffic
   remains stable, but the original waiter timing defect is not fully resolved.
   Client error reports are retained in world-session state for live validation.
5. Combat now has character-specific fight-style data for every verified
   playable character, monster-frame retention, damage reporting,
   report-derived stage results, move-usage telemetry, deterministic per-move
   damage estimates, enemy-by-enemy outcome summaries, and generated
   encounters for numeric recovered stages. Training, teach-PVP, resource,
   hero-chip, pressure, hero-rank, and daily-stage entry requests can now enter
   recovered/generated combat stages. Real drop-table rewards, authoritative
   battle scoring rules, exact authored enemy placement/AI, deeper player
   persistence, and broader inventory systems still require protocol-specific
   state and handlers.

## Character Roadmap

1. Keep the validated starter roster as the compatibility default.
2. Expand live character validation beyond the visible first-row cards and
   record any character-specific packet requests or render problems.
3. Add more verified NPC rows and sanitized authored-placement metadata.
4. Add support-card and costume-specific player-data records after their
   packet requests are observed from the live client.
5. Reconstruct enough quest/activity state to complete the archived tutorial,
   starting from the stateful guide, teach-finish, starter-task, and
   client-stat handlers, then filling in real activity/task state where live
   UI probes prove the client needs more than empty compatibility payloads.
6. Build battle moves and fight styles on top of the recovered stage catalog:
   `299301`, `502601`, the numeric drama-stage candidates, and the
   first-pass enemy AI profiles now provide the vocabulary for combat testing.
7. Use the new fight-style catalog, retained monster-frame telemetry, and
   report-derived combat summaries to reconstruct stage damage, real drop
   rewards, authored enemy behavior, and character-specific move behavior
   during live battle validation.

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
