# MHA TSH Preservation Progress

Last updated: 2026-06-24

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
- The recovered lottery packet family is now partially implemented for
  compatibility: `s_lottery_load`, `s_lottery_choose_up`, and `s_lottery_draw`
  return schema-matched `c_lottery_load`, `c_lottery_choose_up`, and
  `c_lottery_draw` payloads with session draw counters, guarantee progress,
  and persisted item rewards. Nearby compatibility now also covers
  `s_act_exlottery_info`, `s_act_exlottery_draw`, `s_grid_box_lottery`,
  `s_act_magic_shop_draw`, and `s_team_recruit`. Official banner/drop tables are
  still unrecovered; current rewards are clearly local placeholder items.
- The All-Server/Theater activity stage family is now parsed from the recovered
  `act_allsvr_stage_cfg.lua` asset: 84 regular stages and 9 boss stages are
  cataloged, exposed through `c_act_allsvr_stage_info`, and enterable through
  `s_act_allsvr_stage_enter` / `s_act_allsvr_stage_boss`.
- Theater compatibility now covers `s_theater_open`, `s_theater_unlock`,
  `s_theater_bonus`, `s_theater_chapterbonus`, and `s_stage_theater`, with
  stateful local unlock/clear/bonus records and protocol-encoded tests.
- Public playable character handling is now separated from recovered local hero
  rows: the gameplay-facing roster is the 26 public playable heroes, while
  Jiro, Small Might, alternate Deku, All For One, and the art-test All Might
  variant remain recovered/internal evidence unless explicitly used in a test.
  Best Jeanist remains support-only.
- Recovered dash action paths are now classified as dodge/counter evidence
  before generic attack-folder matching, reducing false move-evidence gaps for
  the public playable roster.
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
- The verified combat catalog now reports recovered action-evidence coverage
  per command. Regression tests require every public playable to keep
  parser-backed ATK/Q/W/E/R evidence and record the remaining unresolved
  dodge/passive evidence gaps explicitly, instead of silently treating
  reconstructed move labels as original asset proof.
- The public playable roster now has parser-backed `skill_info` text evidence
  for every verified playable model. The latest pass adds conservative
  original constants for Ochaco, Dabi, Aizawa, and Ojiro, including `Gravel
  Strike`, `DabiQ`, `Dabi Assist Skill E`, `相泽Q1`, `相泽大招`, `尾白Q`, and
  `尾白大招`. Tests also verify Mineta's internal `putao` action tokens are
  attached to the correct ATK/Q/W/E/R/dodge/passive move results.
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
- A third conservative `skill_info` pass now uses skill-ID neighborhoods to
  annotate 27 recovered hero models instead of only the late roster. The
  structured parser classifies 1,477 human-readable terms into command buckets,
  adding move/variant evidence for older heroes such as Midoriya, Bakugo,
  Todoroki, Asui, Mina, Mineta, Tokoyami, Stain, and Hawks as well as WHM
  Midoriya, WHM Bakugo, WHM Todoroki, Nejire, Tamaki, and Mirio. The parser
  now preserves recovered alternate skill-info prefixes for Todoroki
  (`1005xx`), Tokoyami (`1221xx`/`1231xx`), and Stain (`1111xx`) instead of
  dropping those rows because they do not match the model ID directly.
  Runtime combat telemetry exposes those labels as `SkillInfoVariants`,
  improving ATK/Q/W/E/R/Dodge/Passive evidence without overwriting curated
  primary move names.
- The `skill_info` extractor now reads both recovered localized skill-info
  assets (`language/en/skill_info.lua` and the sibling base
  `skill_info.lua`) by default, merging structured command neighborhoods across
  both files. Runtime combat telemetry exposes those late-roster structured
  labels separately as `SkillInfoVariants`, so WHM/Big Three moves can carry
  richer original sub-move labels such as WHM Bakugo's ground/air variants and
  Mirio's localized W/E labels without overwriting the curated primary
  `SkillInfoTerms`.
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
- Resolved combat telemetry now also carries the exact recovered
  `video/skill/*.flv` paths per move as `SkillVideoPaths`. The path table is
  generated from `scripts/derive_skill_video_hints.py` and cross-checked
  against the parser output. Move results also expose `EvidenceSources`,
  distinguishing parser-backed action paths, skill videos, and skill text.
  Considering those three evidence layers together, every move on every public
  playable character now has at least one original evidence trail. Jiro remains
  non-public-playable despite local protocol/model rows.
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
  and 217 drama/script route references, then promotes 37 high-confidence
  script-to-stage groups into the runtime catalog where they do not conflict
  with stronger explicit definitions. This corrects several numeric-looking
  script assumptions: for example, `901008` routes to real stage `563903`,
  `101201_1` routes to `571101`, `zx_touqiu` routes to `300301`, and the
  direct packed string `zx_501101_1` routes to `561115`. The same extractor now
  recovers nearby original route labels, and promoted `stage_cfg_route_*`
  definitions use those labels when no stronger stage definition already owns
  the ID. Runtime coverage now represents every parsed packed `stage_cfg`
  stage/zx script string; `561115` now uses parsed mechanical combat rows with
  one authored placement and one generated fallback placement.
- The `stage_cfg` route promotion table now covers all 71 routed stage IDs
  reported by `scripts/derive_stage_cfg_route_hints.py`, adding 32 more
  enterable route-backed stages while preserving stronger existing definitions
  such as asset-owned `561225`. Newly enterable examples include USJ routes
  `310401`/`310405`, night routes `412101`/`412164`, early area tutorial
  routes `211066`/`211266`, and route-only script IDs such as `606000`.
- The same packed `stage_cfg.lua` data now has an encounter-group extractor:
  `scripts/derive_stage_cfg_encounter_hints.py`. It recovers 33
  stage-to-encounter group links from script neighborhoods, adds the
  `310403`/`zx_usj_03002` route, and attaches authored enemy group IDs to
  runtime candidates such as `300401`, `563903`, and `571101`. The extractor
  now also emits parser-backed `combat_enemy_ids` by cross-checking the raw
  group IDs against recovered `monster_cfg` combat markers; current output
  separates 75 combat IDs from 62 NPC/object/helper IDs across 137 raw group
  IDs. Runtime `BattleStageDefinition` entries now expose that filtered
  `combat_enemy_ids` layer separately from raw `enemy_group_ids`, and
  encounter generation uses the filtered combat list first so helper rows do
  not become accidental battle targets.
- Route-backed `stage_cfg_route_*` definitions deliberately keep recovered raw
  encounter groups as metadata unless the monster cross-check marks them as
  combat rows. A follow-up audit of raw-only routes such as `201005`, `300502`,
  and `561112` found NPC/object/helper names (`npc_idle3`, `Metal Plate`,
  `Ochaco`, bystanders, and photograph props), so those stages continue to use
  generated combat probes rather than placing noncombat rows into battle.
  Global activity monster rosters, such as `act_daily_stage` metadata, are
  intentionally not promoted this way until a true per-stage mapping is
  recovered.
- Those stage encounter IDs are now cross-checked against packed
  `monster_cfg` evidence through `scripts/derive_stage_monster_evidence.py`.
  The extractor recovers 137 target IDs, marks 75 as combat candidates, and
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
- A fourth authored-position pass handles corrupted/variant map-section keys
  such as `MoWsterInfo` and wider `Times` rows with delay/BTParam fields
  interleaved with coordinates. Authored placement recovery is now 60 hints
  across 20 stages. Newly promoted runtime rows complete `405252` and add
  parser-backed spawns for `40510301`, `40630503`, `40650501`, `56240702`,
  `56240751`, `56250409`, and `56390101`; only 10 routed stages still have
  combat IDs without authored coordinates.
- The spawn parser also accepts the `0x79` string tag used by the `406205` map
  chunk. This recovers and promotes all three `406205` combat spawns, bringing
  authored placement recovery to 63 hints across 21 stages and reducing routed
  stages with missing combat coordinates to 9.
- The spawn parser now also reads keyed `AreaX`/`AreaY`/`AreaZ`/`Face`
  dictionaries in `MonsterInfo` rows. This recovers 69 authored placements
  across 25 stages and promotes parser-backed runtime coordinates for
  `16000101`, `20100603`, `31040301`, `40011801`, and the full `561211` combat
  trio, reducing routed stages with missing combat coordinates to 4.
- A final fallback for `MonsterInfo` rows that store only X/Y before
  `Face`/`Id` now recovers `40650603` and `56111303`. Authored placement
  recovery is up to 72 hints across 27 stages; the only remaining routed
  combat-coordinate gaps are the tower special rows `56240652` and `56240771`.
- Runtime authored-spawn data is now parity-checked against the parser output
  for all 72 recovered placements. This corrected stale promoted coordinates
  for `40420103` and `40510301`, including the recovered `40510301` Z/face
  values instead of older local fallback placement data.
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
  `monster_cfg` stage-enemy names and promotes 35 AI overrides from stable
  name markers such as BOSS, elite, ranged/gun, mechanical, and Nomu. Runtime
  stage spawns now distinguish `elite_chaser` and `mechanical_patrol` enemies
  in addition to the existing melee, ranged, boss, Nomu, sludge, mechanical
  boss, and training profiles. Current enterable-stage spawn coverage includes
  boss, elite, mechanical, ranged, Nomu, sludge, and training behaviors instead
  of collapsing nearly every parsed stage enemy into the generic melee profile.
- The newest authored placement promotions are now also AI-regression tested:
  `40011801` stays a Nomu brute, `40650603` stays a boss brute, and the
  `561211` trio keeps two melee rows plus the final boss-brute row.
- The promoted `561115` route contributes two mechanical patrol combat rows
  (`56111503`, `56111505`) and one authored compact-table coordinate for
  `56111505`, while the other mechanical row remains generated until its
  authored placement is recovered.
- The current stage spawn gap audit leaves exactly three generated fallback
  combat rows with no authored coordinate evidence from the parser:
  `56111503`, `56240652`, and `56240771`. The spawn parser was rerun directly
  against those IDs and recovered no positions, so they remain generated
  placeholders rather than guessed authored placements.
- Seeding a recovered stage now also stores per-enemy AI directives in
  `StageState`: enemy ID, display alias, profile, behavior, BT name, home
  coordinates, attack range, leash radius, skill rotation, and combat HP. This
  keeps the client monster-frame seed schema stable while giving battle
  simulation and debugging code deterministic enemy behavior data. Combat
  summary tests also cover surviving enemies, including their next action hint
  and threat score, so AI behavior remains visible even when an encounter is
  not fully defeated.
- Stage enemy AI directives and combat summaries now also report placement
  provenance: explicit hand-authored spawn, parser-authored `stage_cfg`
  coordinate, generated `stage_cfg` fallback, or pure generated-stage fallback.
  This keeps validation rows such as the unresolved `56111503` separate from
  recovered authored placements without changing the client scene-NPC schema.
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
- Generic `s_stage_report` wins now also bridge back into recovered
  area-event quest progression. When the client finishes a recovered
  area-event stage through the normal battle-report path instead of the
  area-event-specific fight-over packet, the server now emits the matching
  stage-pass/info/sync packets, advances the paired task, refreshes the visible
  task list, and persists both stage and task state.
- Contact/dialogue-style recovered quest completions now send
  `c_area_event_sync_status` after their linked stage-pass/info packets. This
  keeps contact tasks and combat tasks on the same area-event UI update path.
- `s_area_event_enter_stage` now resolves blank or zero `StageId` requests to
  the current active recovered area-event stage from the parsed quest order.
  This prevents the client from falling back into the intro/generated stage
  path when the quest UI asks to enter the next available area-event battle
  without repeating the canonical stage ID.
- Recovered quest `accept`/`submit` handling now refuses hidden future
  recovered tasks instead of finishing arbitrary parsed IDs out of order. The
  compatibility path for unknown/local task IDs remains intact, but parsed
  quest-chain tasks must be visible through their recovered predecessor links
  before direct task packets can accept or finish them.
- Verified active quest-contact NPC spawns now also emit
  `c_task_trigger_sync` for the spawned scene UID. This currently applies to
  the recovered Tsukauchi contact path and keeps the trigger packet scoped to
  parser-backed active contacts rather than normal starter/map spawns.
- Campaign trigger interactions now bridge into the same recovered active
  contact-task path as `s_task_sync_info`: `s_campaign_trigger_on` is
  acknowledged, `s_campaign_trigger_see` is accepted without speculative
  replies, and `s_campaign_trigger_interact` can complete a visible
  parser-backed contact task by recovered FieldId/AreaId/NPC IDs, then sends
  the matching area-event stage pass/info/sync packets.
- Completed stage rewards now also grant saved normal-item counts in the
  profile store, giving later inventory/UI packet work a persistent
  player-data backing store.
- Saved normal-item counts now surface through protocol packets: accounts with
  stored items receive a startup `c_item_normal_list`, and lottery/ex-lottery
  rewards send `c_item_amount` updates after the draw result.
- Basic normal-item actions now update saved counts and reply through recovered
  inventory schemas: `s_item_use`, `s_item_sell`, `s_item_resolve`, and
  `s_item_select_reward` emit `c_item_deduct`/`c_item_sell`/`c_item_del` as
  appropriate, while `s_item_lock` is accepted as a no-op until special-item
  lock persistence is recovered.
- The recovered stage catalog now tracks numeric `stage500` plus major
  script-only `zx_ruxue`, USJ, beach, commercial-street, and training-yard
  drama groups. Generated fallback encounters now select enemy-specific AI
  profiles for Nomu, ranged, sludge, mechanical boss, training, and melee
  enemies.
- Parsed numeric `zx_<stage>_<part>` drama-script clusters are now promoted
  into enterable stage definitions instead of remaining loose script evidence.
  This adds 51 recovered stage IDs, including `101002`, `404001`, and
  `801201`, while keeping exact authored spawns as future parse work.
- The battle-stage catalog extractor now preserves all concrete `zx_*` asset
  tokens it sees, not just the starter `battle`/`lvb`/`ruxue` prefixes. Runtime
  evidence clusters now retain the recovered `zx_exam_*` intro exam assets,
  `zx_shangyejie_10`, expanded `zx_ruxue02`/`zx_ruxue03_2_1` actor tokens, and
  the full recovered ruxue/battle plot-audio set. A direct catalog comparison
  leaves only generic search-pattern labels (`zx_battle`, `zx_lvb`,
  `zx_ruxue`) unpromoted rather than concrete recovered asset names.
- Fight-style resolution now produces deterministic style-effect telemetry:
  control, resource delta, mobility, defense, pressure, and per-enemy threat
  hints. Stage lifecycle compatibility now covers stage frame reports,
  play-sync echoing, is-back checks, stage leave, and quick-reborn telemetry.
- A roster-wide combat-entry audit now drives every verified public playable
  character through `s_training_enter` into a recovered combat stage and checks
  the returned fighter payload for the selected HeroId, CardUid, ShapeId, and
  recovered `CardSkillLevel` list. This proves the current 26-character roster
  is not merely serialized in menus; each card can be selected into a stage
  with its own combat-skill payload.
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
- Relax/Joint Operations stage recovery now cross-links its packed
  `relax_stage_cfg.lua` rows with the extracted drama-script index. The first
  six relax stages (`400301` through `400306`) now carry their recovered
  `40030x` script groups into runtime `BattleStageDefinition` metadata, so
  those enterable stages preserve both config rows and local drama hooks.
- A new numeric-drama-index extractor promotes 43 additional pure numeric
  script groups from `analysis/intro_qte_asset_index.txt` into enterable
  generated battle-stage definitions when no stronger explicit, `zx`, or asset
  header definition already owns the stage ID. Newly represented groups include
  `1015023`, `36050101`, `56110901`, and `90100703`, keeping the recovered
  local script names while using generated encounters until enemy placement
  data is recovered.
- Area-event stage recovery now cross-links the 75 parsed `areaevent_cfg.lua`
  progression rows with the extracted drama-script index. The runtime stage
  catalog now preserves chapter/step local hooks such as `area1_1_1start`,
  boss/end scripts, blank-open stages like `21431`, and late chapter hooks such
  as `area14_6` instead of exposing only the first `OpenDrama`.
- Prefixed numeric drama-stage recovery now promotes 23 additional unowned
  `xht_*`, `tc_*`, and `fzx_*` stage groups, including `401001`, `603301`,
  `801203`, and `1001101`, while preserving stronger `zx`, asset-header,
  stage-cfg, and USJ ownership for conflicting IDs. The numeric index parser
  also now captures the 42-script `562502` stage branch.
- Nonnumeric drama-family recovery now groups 622 extracted script hooks into
  32 evidence-only clusters, including activity/event scripts, chase and bus
  QTEs, city patrol branches, stage/PVP/card guides, campaign openings,
  training-yard extras, beach QTEs, TX branches, XHT extras, USJ extras,
  lowercase/uppercase ZX branches, and the remaining loose asset-tail and
  miscellaneous refs. These stay non-enterable until stronger stage IDs or
  quest routes are recovered, but the server catalog now preserves them for
  quest/tutorial ordering work. A regression test also verifies that all 1,257
  indexed drama scripts from the intro/QTE asset index are represented by the
  recovered runtime stage catalog.
- The recovered packed `task_cfg.lua` constants now have a repeatable quest
  hint parser: `scripts/derive_task_cfg_hints.py`. It currently reads 2,856
  constants, preserves 798 narrative task text hints, 75 area-event task
  links, 21 `act*` ordering markers, and 15 non-area-event act task records
  in `mhatsh_server.task_cfg_hints`. Early anchors include `act1001`, the
  `280101`/`280102`/`280103` first-sortie area-event chain, and the
  `280301`/`280302` training/practical exercise entries, with nearby
  stage/NPC/drama references retained for later quest sequencing. The parser
  now also emits task type and condition ID from the recovered
  `区域事件|event|step` marker instead of relying on literal server constants.
- The same parser now promotes nearby stage IDs, NPC IDs, and drama refs onto
  the recovered area-event rows, non-area `act*` task rows, and ordered quest
  chain rows themselves. This keeps early quest NPC/dialog restoration tied to
  packed task evidence, including examples like `act1111` -> NPC `5012` and
  first-sortie area-event drama refs.
- Runtime `TaskRecord` objects now preserve those parser-promoted
  stage/NPC/drama evidence tuples internally, so future quest NPC/dialog
  restoration can use the recovered task rows directly. A constant-pool pass
  found sparse task keys such as `CreateNpc`, `SceneId`, `AccNpc`, and
  `SubNpc`, but the main early chain does not yet expose enough stable
  coordinate data to spawn those NPCs authoritatively.
- The task runtime now also builds an internal recovered quest-NPC reference
  index from those rows. The ordered chain currently references 23 NPC IDs,
  including early unknown/model-unverified quest IDs like `6669` alongside
  cataloged NPCs such as `5012`, giving the next NPC/dialog pass a concrete
  task-to-NPC map without adding speculative scene spawns.
- Non-area-event `act*` task markers are now promoted into task state as
  recovered records with derived task type, label, objective, and source
  marker metadata. The starter task remains first for the archived client path,
  followed by recovered type-1 story gates such as `act1001`, `act1111`, and
  `act1120`; no conditions are invented when the packed task config does not
  expose one.
- The task parser now emits a 90-entry recovered quest chain that interleaves
  the 15 non-area `act*` tasks with the 75 area-event tasks by their original
  packed constant order. Runtime task records carry that `quest_order`, so
  all-task listings preserve the recovered sequence (`act1001`, first-sortie
  area tasks, `act1111`, and onward) while still keeping the local starter task
  first for compatibility.
- The recovered 90-entry quest chain now also stores explicit
  `previous_task_id` and `next_task_id` links. Runtime task records expose
  those links internally for the next progressive-task visibility pass without
  inventing any ordering outside the parsed packed constant sequence.
- Task-list responses now use those parsed links for conservative progressive
  visibility: the client sees the local starter task, completed recovered
  tasks, and the next unlocked recovered quest-chain task instead of receiving
  the entire 90-task chain at once. Completing an area-event stage can also
  backfill unfinished parsed predecessor gates so out-of-order stage progress
  does not strand the recovered chain.
- Known starter/recovered quest completions now follow their
  `c_task_info_update` finish packet with a refreshed `c_task_info` snapshot of
  the currently visible parsed task chain, so the client does not need a second
  manual task-list request to learn about the next recovered quest step.
- The 75 recovered `task_cfg.lua` area-event task links are now bridged to the
  75 parsed `areaevent_cfg.lua` combat stage rows in recovered order. The
  server exposes them as type-28 task records, keeps both task/event/stage IDs
  in the condition params, preserves recovered label/objective/source metadata
  internally, and marks the matching task finished once when an area-event
  stage is won, starting with `280101` -> stage `21111` for "首次出击".
- Recovered area-event task completion now restores from saved stage progress:
  when a profile already has a passed area-event stage, the next session seeds
  the paired recovered task as finished with its condition complete. This keeps
  quest state from regressing after reconnects or server restarts without
  introducing a separate hand-authored task save format.
- Finished task IDs are now profile-backed as well, so direct task submissions,
  starter-guide completions, and recovered area-event task completions survive
  reconnects and server restarts even when there is no richer task-specific
  save format yet.
- Pressure-stage scores, daily-stage counts, and daily-stage reward item
  grants are now profile-backed, so those stage-family loops survive a fresh
  server process alongside normal stage clears and active-card state.
- The starter-intro evidence catalog now records the original
  `4YOU/1294fd82be3620d3` FLV metadata, candidate `zx_battle*` / `zx_lvb*`
  stage scripts, and intro-only school-uniform Midoriya from `hero_cfg` row
  `192` (`NpcId=71104`, `ShapeId=2993`, preload shapes `2993` and `2994`).
  Automated tests keep that costume out of the normal starter and verified
  playable rosters.
- Starter-intro stage entry now deploys intro-only fighter presentation where
  recovered evidence supports it: the `299301` intro cluster can render
  Midoriya with the school-uniform `ShapeId=2993`, while the All Might
  `502601` intro/drama battle can render the owned All Might card for the
  stage without switching the player's active roster card in world state.
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
   The school-uniform Midoriya shape and All Might intro-stage fighter override
   are implemented in the stage/fighter packet layer, but the exact archived
   back-alley/QTE transition sequence still needs controlled client validation
   and any missing stage-order glue.
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
