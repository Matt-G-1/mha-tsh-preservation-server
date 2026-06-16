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
- `MHATSH_INTRO_STAGE_ID` defaults to `299301`.
- `MHATSH_INTRO_STAGE_UID` defaults to `2993010001`.
- `MHATSH_INTRO_STAGE_DRAMA` defaults to `1`.
- `MHATSH_STAGE_REPORT_RESPONSE=record` records reports without immediately
  ending the stage. Use `complete` only when testing post-battle completion.

These defaults are a candidate, not a final claim. Controlled on-device testing
must confirm whether `299301` displays the expected intro/QTE/All Might battle
or whether the next candidate stage should be tried.

