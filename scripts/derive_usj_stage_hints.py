from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from pprint import pformat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_USJ_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "1FO"
    / "69fe1c61716b469f"
)
USJ_STAGE_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/1FO/69fe1c61716b469f, "
    "./script/setting/usj_cfg.lua, parsed 2026-06-24"
)


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_usj_point_id(value: int | None) -> bool:
    return value is not None and 100000 <= value <= 100999


def _is_usj_stage_id(value: int | None) -> bool:
    return value is not None and 700000 <= value <= 799999


def collect_usj_stage_hints(
    usj_stage_asset: Path = DEFAULT_USJ_STAGE_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(usj_stage_asset.read_bytes()).root_constants()
    try:
        start = constants.index("Point2StageCfg")
        end = constants.index("NextPoints")
    except ValueError:
        return {
            "source": USJ_STAGE_SOURCE,
            "constant_count": len(constants),
            "point_count": 0,
            "stage_count": 0,
            "points": [],
            "stages": [],
        }

    points: list[dict[str, object]] = []
    stages: list[dict[str, object]] = []
    current_point: dict[str, object] | None = None
    for index in range(start + 1, end):
        number = _as_int(constants[index])
        if _is_usj_point_id(number):
            current_point = {
                "point_id": int(number),
                "display_order": len(points) + 1,
                "constant_index": index,
                "stage_ids": [],
            }
            points.append(current_point)
            continue
        if current_point is None or not _is_usj_stage_id(number):
            continue
        stage_id = int(number)
        current_point["stage_ids"].append(stage_id)
        stages.append(
            {
                "stage_id": stage_id,
                "point_id": int(current_point["point_id"]),
                "point_order": int(current_point["display_order"]),
                "stage_order": len(current_point["stage_ids"]),
                "constant_index": index,
            }
        )

    return {
        "source": USJ_STAGE_SOURCE,
        "constant_count": len(constants),
        "point_count": len(points),
        "stage_count": len(stages),
        "points": points,
        "stages": stages,
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    stages = [
        {
            key: stage[key]
            for key in (
                "stage_id",
                "point_id",
                "point_order",
                "stage_order",
                "constant_index",
            )
        }
        for stage in payload["stages"]
        if isinstance(stage, dict)
    ]
    points = [
        {
            key: (
                tuple(point[key])
                if key == "stage_ids" and isinstance(point[key], list)
                else point[key]
            )
            for key in ("point_id", "display_order", "constant_index", "stage_ids")
        }
        for point in payload["points"]
        if isinstance(point, dict)
    ]
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n\n\n"
        "USJ_STAGE_SOURCE = "
        + repr(str(payload["source"]))
        + "\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class UsjStageDefinition:\n"
        "    stage_id: int\n"
        "    point_id: int\n"
        "    point_order: int\n"
        "    stage_order: int\n"
        "    constant_index: int\n\n"
        "    @property\n"
        "    def label(self) -> str:\n"
        "        return f'USJ point {self.point_id} stage {self.stage_id}'\n\n"
        "    def as_dict(self) -> dict[str, object]:\n"
        "        return {\n"
        "            'StageId': self.stage_id,\n"
        "            'PointId': self.point_id,\n"
        "            'PointOrder': self.point_order,\n"
        "            'StageOrder': self.stage_order,\n"
        "            'Source': USJ_STAGE_SOURCE,\n"
        "        }\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class UsjPointDefinition:\n"
        "    point_id: int\n"
        "    display_order: int\n"
        "    constant_index: int\n"
        "    stage_ids: tuple[int, ...]\n\n\n"
        "USJ_STAGES = tuple(\n"
        "    UsjStageDefinition(**item)\n"
        "    for item in "
        + pformat(stages, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "USJ_STAGE_BY_ID = {stage.stage_id: stage for stage in USJ_STAGES}\n\n"
        "USJ_POINTS = tuple(\n"
        "    UsjPointDefinition(**item)\n"
        "    for item in "
        + pformat(points, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "USJ_POINT_BY_ID = {point.point_id: point for point in USJ_POINTS}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover USJ point-to-stage IDs from usj_cfg."
    )
    parser.add_argument("--usj-stage", type=Path, default=DEFAULT_USJ_STAGE_ASSET)
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()

    payload = collect_usj_stage_hints(args.usj_stage)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
