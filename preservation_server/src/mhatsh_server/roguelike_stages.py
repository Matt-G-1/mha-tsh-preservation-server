from __future__ import annotations

from dataclasses import dataclass


ROGUELIKE_STAGE_SOURCE = 'analysis/mediafire_20260620/apk_extract/assets/0QIU/864e28b93a350f99, ./script/setting/stage/roguelike_cfg.lua, parsed 2026-06-24'


@dataclass(frozen=True, slots=True)
class RoguelikeStageDefinition:
    stage_id: int
    mode: str
    display_order: int
    constant_index: int

    @property
    def label(self) -> str:
        return f'Roguelike {self.mode} stage {self.stage_id}'

    def as_dict(self) -> dict[str, object]:
        return {
            'StageId': self.stage_id,
            'Mode': self.mode,
            'DisplayOrder': self.display_order,
            'Source': ROGUELIKE_STAGE_SOURCE,
        }


ROGUELIKE_STAGES = tuple(
    RoguelikeStageDefinition(**item)
    for item in [{'stage_id': 400101, 'mode': 'random', 'display_order': 1, 'constant_index': 1114},
 {'stage_id': 400104, 'mode': 'random', 'display_order': 2, 'constant_index': 1115},
 {'stage_id': 400106, 'mode': 'random', 'display_order': 3, 'constant_index': 1116},
 {'stage_id': 400110, 'mode': 'random', 'display_order': 4, 'constant_index': 1117},
 {'stage_id': 400102, 'mode': 'random', 'display_order': 5, 'constant_index': 1118},
 {'stage_id': 400103, 'mode': 'random', 'display_order': 6, 'constant_index': 1119},
 {'stage_id': 400105, 'mode': 'random', 'display_order': 7, 'constant_index': 1120},
 {'stage_id': 400107, 'mode': 'random', 'display_order': 8, 'constant_index': 1121},
 {'stage_id': 400108, 'mode': 'random', 'display_order': 9, 'constant_index': 1122},
 {'stage_id': 400109, 'mode': 'random', 'display_order': 10, 'constant_index': 1123},
 {'stage_id': 400111, 'mode': 'random', 'display_order': 11, 'constant_index': 1124},
 {'stage_id': 400112, 'mode': 'random', 'display_order': 12, 'constant_index': 1125},
 {'stage_id': 400113, 'mode': 'random', 'display_order': 13, 'constant_index': 1126},
 {'stage_id': 400114, 'mode': 'random', 'display_order': 14, 'constant_index': 1127},
 {'stage_id': 400115, 'mode': 'random', 'display_order': 15, 'constant_index': 1128},
 {'stage_id': 400116, 'mode': 'random', 'display_order': 16, 'constant_index': 1129},
 {'stage_id': 400117, 'mode': 'random', 'display_order': 17, 'constant_index': 1130},
 {'stage_id': 400118, 'mode': 'random', 'display_order': 18, 'constant_index': 1131},
 {'stage_id': 400120, 'mode': 'random', 'display_order': 19, 'constant_index': 1132},
 {'stage_id': 400121, 'mode': 'random', 'display_order': 20, 'constant_index': 1133},
 {'stage_id': 400122, 'mode': 'random', 'display_order': 21, 'constant_index': 1134},
 {'stage_id': 400123, 'mode': 'random', 'display_order': 22, 'constant_index': 1135},
 {'stage_id': 400124, 'mode': 'random', 'display_order': 23, 'constant_index': 1136},
 {'stage_id': 400119, 'mode': 'endless', 'display_order': 24, 'constant_index': 1227}]
)

ROGUELIKE_STAGE_BY_ID = {stage.stage_id: stage for stage in ROGUELIKE_STAGES}

