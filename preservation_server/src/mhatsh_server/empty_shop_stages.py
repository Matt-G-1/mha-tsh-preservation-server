from __future__ import annotations

from dataclasses import dataclass


EMPTY_SHOP_STAGE_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/3BAO/f42243de568cd0f0, "
    "./script/setting/activity/act_empty_shop_cfg.lua, parsed 2026-06-24"
)
EMPTY_SHOP_START_TASK_ID = 404001
EMPTY_SHOP_END_TASK_ID = 404007


@dataclass(frozen=True, slots=True)
class EmptyShopStageDefinition:
    stage_id: int
    stage_index: int
    challenge_index: int
    generation: int
    label: str
    desc: str = ""
    fighting: tuple[int, ...] = ()


EMPTY_SHOP_STAGES = tuple(
    EmptyShopStageDefinition(**item)
    for item in [
        {
            "stage_id": 9001001,
            "stage_index": 1,
            "challenge_index": 1,
            "generation": 1,
            "label": "起跑开始，击败敌人完成热身运动吧！",
            "desc": "起跑开始，击败敌人完成热身运动吧！",
            "fighting": (4420, 5520, 6620, 7940, 9520),
        },
        {
            "stage_id": 9002001,
            "stage_index": 2,
            "challenge_index": 2,
            "generation": 1,
            "label": "先发制人，比敌人更快一步！",
            "desc": "先发制人，比敌人更快一步！",
            "fighting": (6920, 8640, 10360, 12440, 14920),
        },
        {
            "stage_id": 9003001,
            "stage_index": 3,
            "challenge_index": 3,
            "generation": 1,
            "label": "现在放弃的话，英雄的梦想要怎么实现？",
            "desc": "现在放弃的话，英雄的梦想要怎么实现？",
            "fighting": (8880, 11100, 13320, 15980, 19180),
        },
        {
            "stage_id": 9004001,
            "stage_index": 4,
            "challenge_index": 4,
            "generation": 1,
            "label": "区区敌人，无法阻挡这迈进的脚步！",
            "desc": "区区敌人，无法阻挡这迈进的脚步！",
            "fighting": (13600, 17000, 20400, 24480, 29380),
        },
        {
            "stage_id": 9005001,
            "stage_index": 5,
            "challenge_index": 5,
            "generation": 1,
            "label": "火力全开，让敌人看到这份决心吧！",
            "desc": "火力全开，让敌人看到这份决心吧！",
            "fighting": (17320, 21640, 25960, 31160, 37400),
        },
        {
            "stage_id": 9006001,
            "stage_index": 6,
            "challenge_index": 6,
            "generation": 1,
            "label": "击败最后的敌人，终点冲刺就在前方！",
            "desc": "击败最后的敌人，终点冲刺就在前方！",
        },
        {
            "stage_id": 9001002,
            "stage_index": 7,
            "challenge_index": 1,
            "generation": 2,
            "label": "正月的冷气还有点冷，先来个热身运动！",
            "desc": "正月的冷气还有点冷，先来个热身运动！",
        },
        {
            "stage_id": 9002002,
            "stage_index": 8,
            "challenge_index": 2,
            "generation": 2,
            "label": "给这些扰乱除夜安宁得敌人一点小教训吧！",
            "desc": "给这些扰乱除夜安宁得敌人一点小教训吧！",
        },
        {
            "stage_id": 9003002,
            "stage_index": 9,
            "challenge_index": 3,
            "generation": 2,
            "label": "不管是新年还是平日，都要好好履行英雄得职责！",
            "desc": "不管是新年还是平日，都要好好履行英雄得职责！",
        },
        {
            "stage_id": 9004002,
            "stage_index": 10,
            "challenge_index": 4,
            "generation": 2,
            "label": "把这些敌人打败，新年初梦应该会梦到茄子吧！",
            "desc": "把这些敌人打败，新年初梦应该会梦到茄子吧！",
        },
        {
            "stage_id": 9005002,
            "stage_index": 11,
            "challenge_index": 5,
            "generation": 2,
            "label": "除夜的钟声就要敲响了，别给敌人喘息的机会！",
            "desc": "除夜的钟声就要敲响了，别给敌人喘息的机会！",
        },
        {
            "stage_id": 9006002,
            "stage_index": 12,
            "challenge_index": 6,
            "generation": 2,
            "label": "赶紧击败最后的敌人，大家一起去神社参拜吧~",
            "desc": "赶紧击败最后的敌人，大家一起去神社参拜吧~",
        },
        {
            "stage_id": 9001003,
            "stage_index": 13,
            "challenge_index": 1,
            "generation": 3,
            "label": "Empty Shop challenge 13",
        },
        {
            "stage_id": 9002003,
            "stage_index": 14,
            "challenge_index": 2,
            "generation": 3,
            "label": "Empty Shop challenge 14",
        },
        {
            "stage_id": 9003003,
            "stage_index": 15,
            "challenge_index": 3,
            "generation": 3,
            "label": "Empty Shop challenge 15",
        },
        {
            "stage_id": 9004003,
            "stage_index": 16,
            "challenge_index": 4,
            "generation": 3,
            "label": "Empty Shop challenge 16",
        },
        {
            "stage_id": 9005003,
            "stage_index": 17,
            "challenge_index": 5,
            "generation": 3,
            "label": "Empty Shop challenge 17",
        },
        {
            "stage_id": 9006003,
            "stage_index": 18,
            "challenge_index": 6,
            "generation": 3,
            "label": "Empty Shop challenge 18",
        },
    ]
)

EMPTY_SHOP_STAGE_BY_ID = {stage.stage_id: stage for stage in EMPTY_SHOP_STAGES}
EMPTY_SHOP_STAGE_BY_INDEX = {stage.stage_index: stage for stage in EMPTY_SHOP_STAGES}
EMPTY_SHOP_STAGE_BY_CHALLENGE_INDEX = {
    stage.challenge_index: stage
    for stage in EMPTY_SHOP_STAGES
    if stage.generation == 1
}
DEFAULT_EMPTY_SHOP_STAGE = EMPTY_SHOP_STAGES[0]
