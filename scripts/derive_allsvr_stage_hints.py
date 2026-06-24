from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_ALLSVR_STAGE_ASSET = (
    Path("phone_dump")
    / "apk_extract"
    / "assets"
    / "1FO"
    / "f25c4e235cdbfcbc"
)
FALLBACK_ALLSVR_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "1FO"
    / "f25c4e235cdbfcbc"
)
ALLSVR_STAGE_SOURCE = (
    "phone_dump/apk_extract/assets/1FO/f25c4e235cdbfcbc, "
    "./script/setting/language/en/activity/act_allsvr_stage_cfg.lua"
)
BOSS_DIFFICULTY_NAMES = ("Safe", "Danger", "Nightmare")
BOSS_NAMES = {
    1: "Humarise Member",
    2: "Beros",
    3: "Sidero",
}
CONTROL_STRINGS = {
    "Cost",
    "PassReward",
    "StageCfg",
    "StageDifficultCfg",
}


def _asset_path(path: Path) -> Path:
    if path.exists():
        return path
    if path == DEFAULT_ALLSVR_STAGE_ASSET and FALLBACK_ALLSVR_STAGE_ASSET.exists():
        return FALLBACK_ALLSVR_STAGE_ASSET
    return path


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_allsvr_stage_id(value: int | None) -> bool:
    return value is not None and 880000 <= value <= 8839999


def _stage_cfg_constants(constants: list[object]) -> list[object]:
    try:
        start = constants.index("StageCfg") + 1
        end = constants.index("StageDifficultCfg")
    except ValueError:
        return []
    return constants[start:end]


def _last_strings(values: list[object], end: int) -> list[str]:
    strings: list[str] = []
    for value in values[:end]:
        if isinstance(value, str) and value not in CONTROL_STRINGS:
            strings.append(value)
    return strings


def _regular_stages(constants: list[object]) -> list[dict[str, object]]:
    section = _stage_cfg_constants(constants)
    rows: list[dict[str, object]] = []
    index = 0
    while index < len(section):
        value = _as_int(section[index])
        if not _is_allsvr_stage_id(value):
            index += 1
            continue
        stage_ids = []
        cursor = index
        while cursor < len(section) and len(stage_ids) < 4:
            stage_id = _as_int(section[cursor])
            if _is_allsvr_stage_id(stage_id):
                stage_ids.append(int(stage_id))
            cursor += 1
        if len(stage_ids) < 4:
            index += 1
            continue
        strings = _last_strings(section, index)
        label = strings[-1] if strings else f"All-Server stage {stage_ids[0]}"
        prompt = strings[-3] if len(strings) >= 3 else ""
        for difficulty, stage_id in enumerate(stage_ids, start=1):
            rows.append(
                {
                    "stage_id": stage_id,
                    "area_id": _area_id_for_stage(stage_id),
                    "stage_index": _stage_index_for_stage(stage_id),
                    "difficulty": difficulty,
                    "label": f"{label} Difficulty {difficulty}",
                    "prompt": prompt,
                    "source": ALLSVR_STAGE_SOURCE,
                }
            )
        index = cursor
    return rows


def _boss_stages(constants: list[object]) -> list[dict[str, object]]:
    try:
        start = constants.index("BossDifficultCfg")
        end = constants.index("BossShapeCfg")
    except ValueError:
        return []
    stages = []
    for value in constants[start:end]:
        stage_id = _as_int(value)
        if stage_id is None or stage_id not in {
            880110,
            880111,
            880112,
            880210,
            880211,
            880212,
            880310,
            880311,
            880312,
        }:
            continue
        boss_id = (stage_id - 880000) // 100
        difficulty = (stage_id % 10) + 1
        stages.append(
            {
                "stage_id": stage_id,
                "boss_id": boss_id,
                "difficulty": difficulty,
                "difficulty_name": BOSS_DIFFICULTY_NAMES[difficulty - 1],
                "label": (
                    f"{BOSS_NAMES.get(boss_id, f'Boss {boss_id}')} "
                    f"{BOSS_DIFFICULTY_NAMES[difficulty - 1]}"
                ),
                "source": ALLSVR_STAGE_SOURCE,
            }
        )
    return stages


def _area_id_for_stage(stage_id: int) -> int:
    if stage_id < 8810000:
        return ((stage_id % 100) - 1) // 3 + 1
    return (stage_id // 1000) % 100


def _stage_index_for_stage(stage_id: int) -> int:
    if stage_id < 8810000:
        return stage_id % 100
    return (stage_id // 10) % 1000


def collect_allsvr_stage_hints(
    allsvr_stage_asset: Path = DEFAULT_ALLSVR_STAGE_ASSET,
) -> dict[str, object]:
    asset = _asset_path(allsvr_stage_asset)
    constants = _RootConstantReader(asset.read_bytes()).root_constants()
    stages = _regular_stages(constants)
    bosses = _boss_stages(constants)
    return {
        "source": ALLSVR_STAGE_SOURCE,
        "constant_count": len(constants),
        "stage_count": len(stages),
        "boss_stage_count": len(bosses),
        "stages": stages,
        "boss_stages": bosses,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover All-Server activity stage rows from packed Lua constants."
    )
    parser.add_argument("--asset", type=Path, default=DEFAULT_ALLSVR_STAGE_ASSET)
    args = parser.parse_args()
    print(
        json.dumps(
            collect_allsvr_stage_hints(args.asset),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
