from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_ROGUELIKE_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "0QIU"
    / "864e28b93a350f99"
)
ROGUELIKE_STAGE_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/0QIU/864e28b93a350f99, "
    "./script/setting/stage/roguelike_cfg.lua, parsed 2026-06-24"
)


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_roguelike_stage_id(value: int | None) -> bool:
    return value is not None and 400100 <= value <= 400199


def collect_roguelike_stage_hints(
    roguelike_stage_asset: Path = DEFAULT_ROGUELIKE_STAGE_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(roguelike_stage_asset.read_bytes()).root_constants()
    stages: list[dict[str, object]] = []

    try:
        start = constants.index("StageList")
        end = constants.index("RankReward")
    except ValueError:
        start = end = 0

    for index in range(start + 1, end):
        stage_id = _as_int(constants[index])
        if _is_roguelike_stage_id(stage_id):
            stages.append(
                {
                    "stage_id": int(stage_id),
                    "mode": "random",
                    "display_order": len(stages) + 1,
                    "constant_index": index,
                }
            )

    try:
        endless_key = constants.index("EndlessStageId")
    except ValueError:
        endless_key = -1
    if endless_key >= 0 and endless_key + 1 < len(constants):
        endless_stage_id = _as_int(constants[endless_key + 1])
        if _is_roguelike_stage_id(endless_stage_id) and all(
            stage["stage_id"] != endless_stage_id for stage in stages
        ):
            stages.append(
                {
                    "stage_id": int(endless_stage_id),
                    "mode": "endless",
                    "display_order": len(stages) + 1,
                    "constant_index": endless_key + 1,
                }
            )

    return {
        "source": ROGUELIKE_STAGE_SOURCE,
        "constant_count": len(constants),
        "stage_count": len(stages),
        "stages": stages,
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    stages = [
        {
            key: stage[key]
            for key in ("stage_id", "mode", "display_order", "constant_index")
        }
        for stage in payload["stages"]
        if isinstance(stage, dict)
    ]
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n\n\n"
        "ROGUELIKE_STAGE_SOURCE = "
        + repr(str(payload["source"]))
        + "\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class RoguelikeStageDefinition:\n"
        "    stage_id: int\n"
        "    mode: str\n"
        "    display_order: int\n"
        "    constant_index: int\n\n"
        "    @property\n"
        "    def label(self) -> str:\n"
        "        return f'Roguelike {self.mode} stage {self.stage_id}'\n\n"
        "    def as_dict(self) -> dict[str, object]:\n"
        "        return {\n"
        "            'StageId': self.stage_id,\n"
        "            'Mode': self.mode,\n"
        "            'DisplayOrder': self.display_order,\n"
        "            'Source': ROGUELIKE_STAGE_SOURCE,\n"
        "        }\n\n\n"
        "ROGUELIKE_STAGES = tuple(\n"
        "    RoguelikeStageDefinition(**item)\n"
        "    for item in "
        + pformat(stages, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "ROGUELIKE_STAGE_BY_ID = {stage.stage_id: stage for stage in ROGUELIKE_STAGES}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover roguelike random/endless stages from roguelike_cfg."
    )
    parser.add_argument(
        "--roguelike-stage",
        type=Path,
        default=DEFAULT_ROGUELIKE_STAGE_ASSET,
    )
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()

    payload = collect_roguelike_stage_hints(args.roguelike_stage)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
