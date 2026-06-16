# Intro Video Research - 2026-06-16

This note captures the intro/tutorial evidence from the requested walkthrough
video and maps it to local protocol restoration targets.

## Source Checked

- Gaming Reviving, "My Hero Academia: The Strongest Hero Walkthrough PART 1 -
  Intro (iOS 1440p)":
  https://www.youtube.com/watch?v=h6YPB14eyNw

The available video metadata identifies a 33:26 walkthrough uploaded on
2021-05-20. Direct frame capture was blocked by YouTube playback/download
limits in the current tool session, so this note relies on the retrieved
caption track, visible YouTube metadata, and local protocol/schema inspection.

## Intro Flow Evidence

The game appears to start earlier than the current preservation-server city
entry point. Excluding any channel-specific wrapper, the video begins with an
in-game MHA origin recap and then continues into tutorial material before the
open-city beginner quest.

Observed caption-outline phases:

| Approx. time | Likely game content |
| --- | --- |
| 00:11 | In-game narration about superhuman society and quirks |
| 00:35 | Giant villain / Mount Lady opening beat |
| 01:45 | Heroes framed as public peacekeepers and All Might as the icon |
| 02:23 | Bakugo, Deku, and the quirkless-origin setup |
| 04:35 | All Might saves Deku from the sludge villain |
| 05:33 | Deku asks whether a quirkless person can become a hero |
| 06:30 | Sludge villain returns and Deku runs toward Bakugo |
| 09:12 | All Might thanks Deku after the rescue moment |
| 10:59 | Long music/montage stretch, probably opening/training material |
| 15:58 | Deku resolve beat before the playable/tutorial section continues |
| 21:45 | Deku character intro line appears in the captions |
| 22:54 | Combat challenge/tutorial line appears in the captions |
| 24:54 | Full Cowling-related tutorial/combat line appears |
| 30:50 | Smash/combat-finisher line appears |

## Local Protocol Targets

The current server starts after this material by giving the archived client a
created player and sending scene `1000` at the Honei/Hoshinori Urban Area spawn.
That matches the visible All Might/Local Hero prompt for starter guide `1301`,
but it skips the earlier intro path.

Recovered protocol schemas show a dedicated login-drama chain:

- `c_login_account_info` has `DramaFlag` and `DramaStep`.
- `s_login_drama` sends `StageId`.
- `c_scene_play_drama` returns `DramaName` and `Loop`.
- `s_login_drama_finish` sends `Uid` and `StageId`.

This means the intro should not be restored by spawning random NPCs in the city.
It should be restored as a pre-city login-drama/tutorial stage, then transition
into character creation/world entry and the existing starter guide `1301`.

## Implementation Decision

The server now has opt-in login-drama probing support. The default game flow
still skips intro drama until the exact archived stage and drama asset names are
recovered. For a controlled client run, enable the account drama flags and watch
for the client to send `s_login_drama`; the logged `StageId` is the next hard
piece of evidence needed.

Once the exact `StageId` and `DramaName` are known, the restore order should be:

1. Enable the login-drama flag only for accounts that have not completed intro.
2. Reply to `s_login_drama` with the recovered `c_scene_play_drama` payload.
3. Record `s_login_drama_finish` and mark that account's intro stage complete.
4. Continue into player creation, initial user/card state, and scene entry.
5. Use the video outline as a behavior checklist for the intro/tutorial chain,
   not as a text source to copy.

