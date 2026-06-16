# Beginner Quest Research - 2026-06-16

This note captures the public and local evidence used for the next beginner
quest restoration pass.

## Public Game Flow Evidence

- Sony's official game page describes the game as an open-world action RPG
  where players walk through the city, accept missions from pro heroes, fight
  villains, complete daily quests, and progress through anime story moments.
- Public beginner guides describe early progression as story and mission driven:
  players complete story missions, daily quests, side quests, Peacekeeping
  Handbook stages, training, and other PvE modes to level characters and city
  progression.
- The public TSH character wiki confirms the starter roster context: Izuku
  Midoriya is one of the core recruitable/playable heroes, with early Class 1-A
  characters such as Bakugo, Iida, Ochaco, Todoroki, Momo, and Denki also in the
  same broad progression ecosystem.

## Local Client Evidence

The current archived-client run has already shown the exact first tutorial task
bridge:

- The player enters scene `1000` at the Honei/Hoshinori Urban Area spawn.
- The client displays the beginner prompt from All Might/Local Hero asking the
  player to tap the quest map and say hi to Death Arms.
- Tapping the highlighted map marker produced `s_client_stat` with numeric data
  `[1, 1301, 10011]`.
- The client also sent `s_guide_finish` for guide `1301`, `s_guide_drama`, and
  `s_base_station_all_info`.
- The client accepted `c_task_info_update`, `c_guide_finish`,
  `c_base_station_all_info`, `c_city_level_info`, and `c_world_task_info`.

## Implementation Decision

The beginner quest should be restored as a stateful quest chain, not as a pile
of default scene spawns. For the next build:

1. The starter city should load without validation/demo NPCs already standing at
   the player spawn.
2. Accepting starter task `1301` may spawn only the verified Death Arms quest NPC
   via `c_scene_npc_create`.
3. Completing guide/task `1301` should send a normal task completion update,
   then seed city progression with `c_city_level_add_exp`, `c_city_level_up`,
   refreshed `c_city_level_info`, and refreshed `c_world_task_info`.
4. The world-task finish list should mark map `1000`, area `0`, task `1301` as
   complete once the starter objective is done.
5. Later work should recover the next actual guide/task IDs from client logs and
   local Lua/config tables instead of guessing the full tutorial chain.

## Sources

- https://www.sonypictures.com/games/myheroacademiathestrongesthero
- https://www.bluestacks.com/blog/game-guides/my-hero-academia-the-strongest-hero/mha-beginner-guide-en.html
- https://myheroacademiathestrongesthero.fandom.com/wiki/Characters

