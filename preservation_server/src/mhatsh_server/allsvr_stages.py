from __future__ import annotations

from dataclasses import dataclass


ALLSVR_STAGE_SOURCE = (
    "phone_dump/apk_extract/assets/1FO/f25c4e235cdbfcbc, "
    "./script/setting/language/en/activity/act_allsvr_stage_cfg.lua, "
    "parsed 2026-06-24"
)
ALLSVR_COND_IDS = tuple(range(1, 36))


@dataclass(frozen=True, slots=True)
class AllServerStageDefinition:
    stage_id: int
    area_id: int
    stage_index: int
    difficulty: int
    label: str
    prompt: str = ""


@dataclass(frozen=True, slots=True)
class AllServerBossStageDefinition:
    stage_id: int
    boss_id: int
    difficulty: int
    difficulty_name: str
    label: str


_REGULAR_STAGE_ROWS = (
    (
        "Entrance 1",
        "I'm very nervous, but I won't let everyone down!",
        (880101, 880201, 880301, 880401),
    ),
    (
        "Entrance 2",
        "They're not that strong... But never underestimate your enemy!",
        (880102, 880202, 880302, 880402),
    ),
    (
        "Entrance 3",
        "There are more of them coming! It's time for that move...!",
        (880103, 880203, 880303, 880403),
    ),
    ("Hallway 1", "I'll send them flying!", (880104, 880204, 880304, 880404)),
    (
        "Hallway 2",
        "Ha! That's it? I'm barely getting started!",
        (880105, 880205, 880305, 880405),
    ),
    (
        "Hallway 3",
        "You're ready for a beating for joining this stupid cult?!",
        (880106, 880206, 880306, 880406),
    ),
    (
        "Library 1",
        "It seems some of them are Quirkless... We shouldn't hit them too hard...",
        (880107, 880207, 880307, 880407),
    ),
    ("Library 2", "...I hope you can quickly solve this.", (880108, 880208, 880308, 880408)),
    ("Library 3", "Sorry, but you're in my way.", (880109, 880209, 880309, 880409)),
    (
        "Forest Pathway - 1",
        "These villains need to be stopped!",
        (8811011, 8811012, 8811013, 8811014),
    ),
    (
        "Forest Pathway - 2",
        "Don't let any villain escape!",
        (8811021, 8811022, 8811023, 8811024),
    ),
    (
        "Forest Pathway - 3",
        "Restore peace in the forest path!",
        (8811031, 8811032, 8811033, 8811034),
    ),
    (
        "Green Forest - 1",
        "The robots are out of control! Turn them off!",
        (8812011, 8812012, 8812013, 8812014),
    ),
    (
        "Green Forest - 2",
        "Destroy the robots if they're causing too much trouble!",
        (8812021, 8812022, 8812023, 8812024),
    ),
    (
        "Green Forest - 3",
        "Enjoy the scenery after taking care of the case!",
        (8812031, 8812032, 8812033, 8812034),
    ),
    (
        "Heavy Rain - 1",
        "Those smugglers tend to come out when it rains! Let's stop them!",
        (8831011, 8831012, 8831013, 8831014),
    ),
    (
        "Heavy Rain - 2",
        "Bad weather is not going to stop the villains... Make them pay for what they've done!",
        (8831021, 8831022, 8831023, 8831024),
    ),
    (
        "Heavy Rain - 3",
        "Let's finish this quick, we might have time for that afternoon tea.",
        (8831031, 8831032, 8831033, 8831034),
    ),
    (
        "Neon City - 1",
        "Clean up the evil under the neon lights!",
        (8832011, 8832012, 8832013, 8832014),
    ),
    (
        "Neon City - 2",
        "They linger in the dark... It's time to put an end to them!",
        (8832021, 8832022, 8832023, 8832024),
    ),
    (
        "Neon City - 3",
        "Take them all down! Restore the peace of the city that never sleeps!",
        (8832031, 8832032, 8832033, 8832034),
    ),
)
_BOSS_STAGE_ROWS = (
    (1, "Humarise Member", (880110, 880111, 880112)),
    (2, "Beros", (880210, 880211, 880212)),
    (3, "Sidero", (880310, 880311, 880312)),
)
_BOSS_DIFFICULTY_NAMES = ("Safe", "Danger", "Nightmare")


def _area_id_for_stage(stage_id: int) -> int:
    if stage_id < 8810000:
        return ((stage_id % 100) - 1) // 3 + 1
    return (stage_id // 1000) % 100


def _stage_index_for_stage(stage_id: int) -> int:
    if stage_id < 8810000:
        return stage_id % 100
    return (stage_id // 10) % 1000


ALLSVR_STAGES = tuple(
    AllServerStageDefinition(
        stage_id=stage_id,
        area_id=_area_id_for_stage(stage_id),
        stage_index=_stage_index_for_stage(stage_id),
        difficulty=difficulty,
        label=f"{label} Difficulty {difficulty}",
        prompt=prompt,
    )
    for label, prompt, stage_ids in _REGULAR_STAGE_ROWS
    for difficulty, stage_id in enumerate(stage_ids, start=1)
)
ALLSVR_BOSS_STAGES = tuple(
    AllServerBossStageDefinition(
        stage_id=stage_id,
        boss_id=boss_id,
        difficulty=difficulty,
        difficulty_name=_BOSS_DIFFICULTY_NAMES[difficulty - 1],
        label=f"{boss_name} {_BOSS_DIFFICULTY_NAMES[difficulty - 1]}",
    )
    for boss_id, boss_name, stage_ids in _BOSS_STAGE_ROWS
    for difficulty, stage_id in enumerate(stage_ids, start=1)
)
ALLSVR_STAGE_BY_ID = {stage.stage_id: stage for stage in ALLSVR_STAGES}
ALLSVR_BOSS_STAGE_BY_ID = {stage.stage_id: stage for stage in ALLSVR_BOSS_STAGES}
ALLSVR_BOSS_STAGE_BY_BOSS_AND_DIFFICULTY = {
    (stage.boss_id, stage.difficulty): stage for stage in ALLSVR_BOSS_STAGES
}
DEFAULT_ALLSVR_STAGE = ALLSVR_STAGES[0]
DEFAULT_ALLSVR_BOSS_STAGE = ALLSVR_BOSS_STAGES[0]
