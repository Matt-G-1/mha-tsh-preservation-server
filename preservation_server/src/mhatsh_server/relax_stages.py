from __future__ import annotations

from dataclasses import dataclass


RELAX_STAGE_SOURCE = (
    "phone_dump/apk_extract/assets/0QIU/bc4767502c3d543d, "
    "./script/setting/language/en/stage/relax_stage_cfg.lua, parsed 2026-06-24"
)


@dataclass(frozen=True, slots=True)
class RelaxStageDefinition:
    stage_id: int
    group_id: int
    group_name: str
    open_level: int
    difficulty: int
    difficulty_name: str
    fighting: tuple[int, ...]
    tips: str = ""
    show_rewards: tuple[int, ...] = ()

    @property
    def label(self) -> str:
        return f"{self.group_name} {self.difficulty_name}"

    def as_round_data(self, *, status: int = 0, reward: int = 0) -> dict[str, object]:
        return {"Id": self.stage_id, "Status": int(status), "Reward": int(reward)}


RELAX_STAGES = tuple(
    RelaxStageDefinition(**item)
    for item in [
        {
            "stage_id": 400301,
            "group_id": 1,
            "group_name": "01 Trial of the Strongest",
            "open_level": 20,
            "difficulty": 1,
            "difficulty_name": "Easy",
            "fighting": (2640, 2940, 3080, 3240, 3520),
            "tips": "Challenge from the No.1 Hero, All Might. Detroit Smash: Stay within the green circles to avoid damage.",
            "show_rewards": (1021005, 1029040, 1021025, 1021026, 1029034),
        },
        {
            "stage_id": 400302,
            "group_id": 1,
            "group_name": "01 Trial of the Strongest",
            "open_level": 20,
            "difficulty": 2,
            "difficulty_name": "Elite",
            "fighting": (4700, 5220, 5480, 5740, 6260),
            "tips": "Challenge from the No.1 Hero, All Might. Tornado: Stay outside the yellow circle to mitigate the pulling effect.",
            "show_rewards": (1029001, 1029035),
        },
        {
            "stage_id": 400303,
            "group_id": 1,
            "group_name": "01 Trial of the Strongest",
            "open_level": 20,
            "difficulty": 3,
            "difficulty_name": "Hard",
            "fighting": (7480, 8300, 8720, 9140, 9960),
            "tips": "Challenge from the No.1 Hero, All Might. When the shield is broken, All Might will be weakened, giving you a chance to deal damage.",
            "show_rewards": (1021027,),
        },
        {
            "stage_id": 400304,
            "group_id": 2,
            "group_name": "02 Glacier and Flames",
            "open_level": 30,
            "difficulty": 1,
            "difficulty_name": "Easy",
            "fighting": (6220, 6900, 7240, 7600, 8280),
            "tips": "Challenge from Todoroki, it's dangerous to get close, be careful with the Fire Fist Charge!",
            "show_rewards": (1029036,),
        },
        {
            "stage_id": 400305,
            "group_id": 2,
            "group_name": "02 Glacier and Flames",
            "open_level": 30,
            "difficulty": 2,
            "difficulty_name": "Elite",
            "fighting": (12340, 13700, 14380, 15080, 16440),
            "show_rewards": (1029002,),
        },
        {
            "stage_id": 400306,
            "group_id": 2,
            "group_name": "02 Glacier and Flames",
            "open_level": 30,
            "difficulty": 3,
            "difficulty_name": "Hard",
            "fighting": (16480, 18300, 19220, 20140, 21960),
        },
        {
            "stage_id": 400307,
            "group_id": 3,
            "group_name": "03 Dawn of Creation",
            "open_level": 40,
            "difficulty": 1,
            "difficulty_name": "Easy",
            "fighting": (16240, 18040, 18940, 19840, 21640),
            "tips": "Spear: The fixated player needs to stay away from teammates, and the traps must be properly unarmed.",
        },
        {
            "stage_id": 400308,
            "group_id": 3,
            "group_name": "03 Dawn of Creation",
            "open_level": 40,
            "difficulty": 2,
            "difficulty_name": "Elite",
            "fighting": (21220, 23580, 24760, 25940, 28300),
            "tips": "Scythe: Use the slow effect of Tape to counter the absorbing effect of the Scythe.",
            "show_rewards": (1029003,),
        },
        {
            "stage_id": 400309,
            "group_id": 3,
            "group_name": "03 Dawn of Creation",
            "open_level": 40,
            "difficulty": 3,
            "difficulty_name": "Hard",
            "fighting": (30400, 33780, 35460, 37160, 40540),
            "tips": "Creation Stance: The targeted player needs to lure the cannon barrage's attacks to break Momo Yaoyorozu's shield to cancel out Creation Stance.",
        },
        {
            "stage_id": 400310,
            "group_id": 4,
            "group_name": "04 Explosive Crisis",
            "open_level": 50,
            "difficulty": 1,
            "difficulty_name": "Easy",
            "fighting": (19080, 21200, 22260, 23320, 25440),
            "tips": "Challenge from Bakugo. Watch out for his Stun Grenade. When he goes on a rampage, dodge his combos carefully.",
            "show_rewards": (1029037,),
        },
        {
            "stage_id": 400311,
            "group_id": 4,
            "group_name": "04 Explosive Crisis",
            "open_level": 50,
            "difficulty": 2,
            "difficulty_name": "Elite",
            "fighting": (30780, 34200, 35920, 37620, 41040),
            "show_rewards": (1029004,),
        },
        {
            "stage_id": 400312,
            "group_id": 4,
            "group_name": "04 Explosive Crisis",
            "open_level": 50,
            "difficulty": 3,
            "difficulty_name": "Hard",
            "fighting": (40560, 45060, 47320, 49560, 54080),
        },
        {
            "stage_id": 400313,
            "group_id": 5,
            "group_name": "05 Night of Eradication",
            "open_level": 60,
            "difficulty": 1,
            "difficulty_name": "Easy",
            "fighting": (27940, 31040, 32600, 34140, 37240),
            "tips": "Being hit by Stain will trigger his Vigor. Keep attacking him and remember to dodge his damage",
        },
        {
            "stage_id": 400314,
            "group_id": 5,
            "group_name": "05 Night of Eradication",
            "open_level": 60,
            "difficulty": 2,
            "difficulty_name": "Elite",
            "fighting": (37520, 41680, 43760, 45840, 50020),
            "show_rewards": (1029005,),
        },
        {
            "stage_id": 400315,
            "group_id": 5,
            "group_name": "05 Night of Eradication",
            "open_level": 60,
            "difficulty": 3,
            "difficulty_name": "Hard",
            "fighting": (49600, 55100, 57860, 60620, 66120),
            "show_rewards": (1021006, 1021028, 1029031),
        },
        {
            "stage_id": 400316,
            "group_id": 6,
            "group_name": "06 End of the Light",
            "open_level": 65,
            "difficulty": 1,
            "difficulty_name": "Easy",
            "fighting": (39500, 43890, 48270, 52660, 57050),
            "tips": "Shigaraki will teleport after entering the mist! Dodge his attack!",
        },
        {
            "stage_id": 400317,
            "group_id": 6,
            "group_name": "06 End of the Light",
            "open_level": 65,
            "difficulty": 2,
            "difficulty_name": "Elite",
            "fighting": (46460, 51590, 56740, 61900, 67060),
        },
        {
            "stage_id": 400318,
            "group_id": 6,
            "group_name": "06 End of the Light",
            "open_level": 65,
            "difficulty": 3,
            "difficulty_name": "Hard",
            "fighting": (56430, 62700, 68970, 75240, 81510),
            "show_rewards": (1021007, 1029038),
        },
    ]
)

RELAX_STAGE_BY_ID = {stage.stage_id: stage for stage in RELAX_STAGES}
