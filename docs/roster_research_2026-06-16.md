# MHA TSH Roster Research - 2026-06-16

This note reconciles the local preservation server character catalogs with public
wikis, guides, and official/near-official game coverage before continuing game
development.

## Sources Checked

- TSH Fandom character roster:
  https://myheroacademiathestrongesthero.fandom.com/wiki/Characters
- Main MHA Wiki page for The Strongest Hero:
  https://myheroacademia.fandom.com/wiki/My_Hero_Academia:_The_Strongest_Hero
- Sony Pictures official game page:
  https://www.sonypictures.com/games/myheroacademiathestrongesthero
- BlueStacks beginner guide:
  https://www.bluestacks.com/blog/game-guides/my-hero-academia-the-strongest-hero/mha-beginner-guide-en.html
- Anime Trending / Crunchyroll Games launch coverage:
  https://anitrendz.net/news/2022/04/07/crunchyroll-games-releases-my-hero-academia-the-strongest-hero-mobile-game/
- Community support-card guide:
  https://www.reddit.com/r/MHATheStrongestHero/comments/qpftqo/community_support_card_guide/

## Playable Roster Verdict

The public TSH-specific wiki lists 26 playable heroes. Its list matches the
core public playable set we currently expose through `PUBLIC_PLAYABLE_MODEL_IDS`,
including Class 1-A characters, pro heroes, villains, WHM variants, and the Big
Three.

The broader MHA wiki page for the game separately lists playable heroes,
playable villains, and limited WHM events. It corroborates the same broad set,
but also names Himiko Toga as a playable villain. The current local AXMD/config
catalog has not yet produced a verified playable Toga model entry, so Toga should
not be added to the server roster until local client data confirms the model id,
hero id, and shape id path.

Current local roster status:

| Model | Character | Status |
| --- | --- | --- |
| h1001 | Izuku Midoriya | Verified playable |
| h1002 | Katsuki Bakugo | Verified playable |
| h1003 | All Might | Verified playable |
| h1004 | All Might (Small Form) | Verified playable/local variant |
| h1006 | Tenya Iida | Verified playable |
| h1007 | Ochaco Uraraka | Verified playable |
| h1008 | Shoto Todoroki | Verified playable |
| h1009 | Momo Yaoyorozu | Verified playable |
| h1010 | Denki Kaminari | Verified playable |
| h1012 | Dabi | Verified playable |
| h1013 | Eijiro Kirishima | Verified playable |
| h1014 | Tsuyu Asui | Verified playable |
| h1015 | Shota Aizawa | Verified playable |
| h1016 | Mashirao Ojiro | Verified playable |
| h1017 | Mina Ashido | Verified playable |
| h1018 | Kyoka Jiro | Local protocol/model row; not public playable |
| h1019 | Tomura Shigaraki | Verified playable |
| h1020 | Minoru Mineta | Verified playable |
| h1021 | Endeavor | Verified playable |
| h1022 | Fumikage Tokoyami | Verified playable |
| h1024 | Izuku Midoriya (Alternate) | Verified playable/local variant |
| h1026 | Hawks | Verified playable |
| h1027 | WHM Izuku Midoriya | Verified playable |
| h1028 | WHM Katsuki Bakugo | Verified playable |
| h1029 | WHM Shoto Todoroki | Verified playable |
| h1030 | Nejire Hado | Verified playable |
| h1031 | Tamaki Amajiki | Verified playable |
| h1032 | Mirio Togata | Verified playable |
| h1039 | All For One | Asset-only/unverified playable |
| h1110 | Stain | Verified playable |
| h1998 | All Might (Art Test Variant) | Verified local asset/test variant |

## Support Roster Verdict

Best Jeanist should remain support-only. Public game coverage describes Best
Jeanist as a character summon card, and the wiki playable lists do not include
him as a playable hero for The Strongest Hero. This matches the current local
server split:

| Model | Character | Status |
| --- | --- | --- |
| h1927 | Best Jeanist | Support-only |

The support-card system needs its own catalog instead of being mixed into the
playable hero list. Public guides identify both active and passive support-card
types, and community card guides list examples such as Kamui Woods, Snipe, Nezu,
Rody, Muscular, Kurogiri, Mr. Compress, Nomu, and Mastermind.

## Game Systems To Preserve

The official game page and beginner guides describe the game as an open-world
action RPG with story progression, daily quests, special stages, boss fights,
PvP arena modes, alliances/unions, dorm/social systems, recruitment, skills,
talents, chips, assists, and support cards.

For near-term restoration, that means the character work should be ordered as:

1. Keep playable heroes and support cards as separate server concepts.
2. Finish the playable roster packets for verified local characters.
3. Add a support-card catalog and return support-card inventory separately.
4. Confirm any missing online-playable characters, especially Toga, against
   local model/config data before exposing them.
5. Keep All For One as asset-only until local hero config or live packet demand
   proves a playable implementation path.
6. Avoid spawning battle enemies or boss-sized NPCs in the starter city unless a
   quest/activity state explicitly requests them.
