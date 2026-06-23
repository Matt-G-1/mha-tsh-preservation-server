# Starter Intro QTE and All Might Stage Research - 2026-06-16

This note records the local evidence used for the first starter-intro battle
probe. It intentionally summarizes asset/script findings instead of committing
copied client chunks or large extracted string dumps.

## Local Client Evidence

- The archived asset buckets contain a QTE UI script named
  `script/ui/qte/qteDramaClickButtonView.lua`. Its recovered strings reference
  drama QTE buttons, success/failure callbacks, click/touch handlers, and the
  `DRAMA_QTE` / `CHASE_QTE` modes.
- The drama configuration script exposes client-side commands for creating and
  finishing drama stages, including a `CreateQte` command. That points to QTEs
  being driven by client drama/stage scripts once the correct stage is loaded,
  not by a standalone server-to-client QTE packet.
- A starter battle/drama cluster references `zx_battle01`, `zx_battle02`,
  `zx_battle03`, `zx_battle05`, `zx_battle06`, `zx_battle07`,
  `zx_lvb_001`, `zx_lvb_002`, `zx_lvb_003`, `zx_lvb_004`, and stage-like ID
  `299301`. The same cluster includes monster/group references, which makes it
  the strongest current candidate for the opening battle path.
- A separate pre-city/narration cluster references `zx_ruxue01`,
  `zx_ruxue02`, `zx_ruxue03`, `zx_ruxue03_2`, `zx_ruxue03_2_1`,
  `zx_ruxue04`, `zx_ruxue05`, and copyright-prefixed assets such as
  `_copyright/zx_ruxue02_0` and `_1_copyright/zx_ruxue03_2_1_0`. Those names
  are a closer match for the user-supplied All Might silhouette/subtitle
  screenshot than the recovered sludge-villain recap FLV.
- The user-supplied FLV `1294fd82be3620d3(1).flv` maps to the original client
  patch manifest entry `4YOU/1294fd82be3620d3`. Its metadata is 1600x720,
  30 fps, 40 seconds, MD5 `85546BD65E1B15BBFDE53A28E4DB39C6`.
  Frame inspection shows All Might, classroom Midoriya/Bakugo, the sludge
  villain rescue, and Deku/Bakugo near the sludge villain. No QTE overlay is
  visible in the video asset itself, and the sampled frames do not match the
  blue All Might silhouette/subtitle screenshot.
- `en_hero_cfg_readable.lua` contains the intro-only school-uniform Midoriya
  row as `L3_3[192]`, localized name `校服绿谷`, `NpcId=71104`,
  `ShapeId=2993`, and preloaded shapes `{2993, 2994}`. This should be used
  only for intro/stage fighter data, not for the normal city roster.
- A separate All Might-related drama cluster references `stage502601`,
  `stage502601a`, and `stage502601b`. That may be another All Might encounter,
  but it is not yet proven to be the first playable intro battle.

## Protocol Decision

The recovered protocol schema has `c_stage_enter` with:

- `StageId`
- `StageUid`
- `Level`
- `Time`
- `Drama`
- `IsReconnect`
- `NeedLagLog`
- `IsRecord`
- `Extra`

There is no recovered server packet whose shape looks like "show QTE button".
The cleanest probe is therefore to acknowledge the starter task-stage request
and then send `c_stage_enter` for the candidate archived stage with `Drama=1`.
If the stage ID matches the archived stage table, the client should load its
own intro drama/QTE/battle scripts.

## Implemented Probe Defaults

- `MHATSH_INTRO_STAGE_MODE=starter` enables the probe.
- `MHATSH_INTRO_STAGE_TRIGGER` defaults to `task_enter`; use `starter_guide`
  to queue the candidate stage when guide `1301` completion telemetry appears.
  Live testing showed the client can time out if `c_stage_enter` is injected
  inside the `s_guide_finish` callback. Sending it immediately after the
  base-station/city/world-task seed responses still reproduced the timeout, so
  the `starter_guide` trigger now waits for the later client telemetry tuple
  `[0, 1404, 10351]` containing `WorldMapView`.
- `MHATSH_INTRO_STAGE_DELAY` defaults to `0.25` seconds for that deferred
  starter-guide path. Tests set it to zero.
- `MHATSH_INTRO_STAGE_ID` defaults to `299301`.
- `MHATSH_INTRO_STAGE_UID` defaults to `2993010001`.
- `MHATSH_INTRO_STAGE_DRAMA` defaults to `1`.
- `MHATSH_STAGE_REPORT_RESPONSE=record` records reports without immediately
  ending the stage. Use `complete` only when testing post-battle completion.
- `mhatsh_server.intro` records the recovered starter-recap video metadata,
  intro stage candidate scripts, and the intro-only school Midoriya costume so
  later `c_frame_fighter_data` work can use `ShapeId=2993` without leaking it
  into normal world entry.

The first controlled run after adding the task-enter probe reached the starter
city and completed guide `1301`, but the client did not send
`s_task_enter_stage`; it used `s_client_stat` and `s_guide_finish` for that
route. Both the immediate `starter_guide` injection and the first deferred
post-base-station injection caused the live client to time out waiting for
`s_guide_finish`, so the stage probe now waits for the observed WorldMapView
telemetry boundary.

These defaults are a candidate, not a final claim. Controlled on-device testing
must confirm whether `299301` displays the expected intro/QTE/All Might battle
or whether the next candidate stage should be tried.

The 40-second FLV is not enough by itself to restore the playable QTE sequence;
it is recap/cinematic material. The QTE and All Might battle should still be
restored by loading the correct drama/stage script cluster and, once fighter
packet data is implemented, using the intro-only Midoriya shape only in that
stage context.
