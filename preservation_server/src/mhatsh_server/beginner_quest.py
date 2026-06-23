from __future__ import annotations


# Recovered from the local client's first tutorial trace:
# - All Might's starter prompt drives guide/task 1301.
# - The highlighted map tap sends s_client_stat NumData [1, 1301, 10011].
# - The world-task finish row uses map 1000, area 0, task 1301.
STARTER_TASK_ID = 1301
STARTER_TASK_TYPE = 1
STARTER_TASK_CONDITION_ID = 1
STARTER_GUIDE_SET_ID = 9
STARTER_GUIDE_DRAMA_ID = 20001301
STARTER_GUIDE_STEP = 10011
# The live client starts this map-selection guide immediately after scene load.
# Task 1301 alone does not suppress its local overlay.
STARTER_MAP_GUIDE_SET_ID = 12
STARTER_MAP_GUIDE_ID = 1410
STARTER_WORLD_MAP_ID = 1000
STARTER_WORLD_AREA_ID = 0

# Local client validation showed the beginner quest should level the city once
# the starter objective is acknowledged.
BEGINNER_QUEST_CITY_EXP = 100
BEGINNER_QUEST_CITY_LEVEL = 2

# This UID is server-local; the NPC row/model identity is the important
# recovered part. Keeping it stable lets repeated tests compare exact packets.
BEGINNER_QUEST_DEATH_ARMS_UID = 20001
