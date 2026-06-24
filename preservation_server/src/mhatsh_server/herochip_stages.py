from __future__ import annotations

from dataclasses import dataclass


HEROCHIP_STAGE_SOURCE = 'analysis/mediafire_20260620/apk_extract/assets/4YOU/7e1da27f95a28f95, ./script/setting/herochip_stage_cfg.lua, parsed 2026-06-24'


@dataclass(frozen=True, slots=True)
class HerochipStageDefinition:
    stage_id: int
    display_order: int
    title: str
    stage_desc: str
    unlock_desc: str
    stage_image: str
    hero_class_id: int
    reward_item_id: int
    unlock_stage_id: int
    constant_index: int

    @property
    def label(self) -> str:
        return self.title or f'Hero chip stage {self.stage_id}'

    def as_dict(self) -> dict[str, object]:
        return {
            'StageId': self.stage_id,
            'DisplayOrder': self.display_order,
            'Title': self.title,
            'StageDesc': self.stage_desc,
            'UnlockDesc': self.unlock_desc,
            'StageImage': self.stage_image,
            'HeroClassId': self.hero_class_id,
            'RewardItemId': self.reward_item_id,
            'UnlockStageId': self.unlock_stage_id,
            'Source': HEROCHIP_STAGE_SOURCE,
        }


HEROCHIP_STAGES = tuple(
    HerochipStageDefinition(**item)
    for item in [{'stage_id': 370101,
  'display_order': 1,
  'title': '英雄的志愿',
  'stage_desc': '进行关卡挑战，可获得绿谷出久碎片',
  'unlock_desc': '通关治安事件1-3',
  'stage_image': '碎片本_关卡图_124',
  'hero_class_id': 124,
  'reward_item_id': 1012124,
  'unlock_stage_id': 280103,
  'constant_index': 63},
 {'stage_id': 370102,
  'display_order': 2,
  'title': '电光般闪耀',
  'stage_desc': '进行关卡挑战，可获得上鸣电气碎片',
  'unlock_desc': '通关治安事件2-3',
  'stage_image': '碎片本_关卡图_110',
  'hero_class_id': 110,
  'reward_item_id': 1012110,
  'unlock_stage_id': 280203,
  'constant_index': 88},
 {'stage_id': 370103,
  'display_order': 3,
  'title': '男子汉的信念',
  'stage_desc': '进行关卡挑战，可获得切岛锐儿郎碎片',
  'unlock_desc': '通关治安事件3-4',
  'stage_image': '碎片本_关卡图_113',
  'hero_class_id': 113,
  'reward_item_id': 1012113,
  'unlock_stage_id': 280304,
  'constant_index': 107},
 {'stage_id': 370106,
  'display_order': 4,
  'title': '高效的执行力',
  'stage_desc': '进行关卡挑战，可获得饭田天哉碎片',
  'unlock_desc': '通关治安事件4-5',
  'stage_image': '碎片本_关卡图_106',
  'hero_class_id': 106,
  'reward_item_id': 1012106,
  'unlock_stage_id': 280405,
  'constant_index': 125},
 {'stage_id': 370105,
  'display_order': 5,
  'title': '纯真的善意',
  'stage_desc': '进行关卡挑战，可获得丽日御茶子碎片',
  'unlock_desc': '通关治安事件5-6',
  'stage_image': '碎片本_关卡图_107',
  'hero_class_id': 107,
  'reward_item_id': 1012107,
  'unlock_stage_id': 280506,
  'constant_index': 143},
 {'stage_id': 370104,
  'display_order': 6,
  'title': '意外的惊喜',
  'stage_desc': '进行关卡挑战，可获得峰田实碎片',
  'unlock_desc': '通关治安事件6-6',
  'stage_image': '碎片本_关卡图_120',
  'hero_class_id': 120,
  'reward_item_id': 1012120,
  'unlock_stage_id': 280606,
  'constant_index': 160},
 {'stage_id': 370107,
  'display_order': 7,
  'title': '精神的支柱',
  'stage_desc': '进行关卡挑战，可获得蛙吹梅雨碎片',
  'unlock_desc': '通关治安事件7-6',
  'stage_image': '碎片本_关卡图_114',
  'hero_class_id': 114,
  'reward_item_id': 1012114,
  'unlock_stage_id': 280706,
  'constant_index': 179}]
)

HEROCHIP_STAGE_BY_ID = {stage.stage_id: stage for stage in HEROCHIP_STAGES}

