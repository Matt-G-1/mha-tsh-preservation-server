from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_SECRET_AREA_ASSET = (
    Path("phone_dump")
    / "apk_extract"
    / "assets"
    / "0QIU"
    / "e64de4e82ab94375"
)
FALLBACK_SECRET_AREA_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "3BAO"
    / "87e9e569745ed298"
)
SECRET_AREA_SOURCE = (
    "phone_dump/apk_extract/assets/0QIU/e64de4e82ab94375, "
    "./script/setting/language/en/secret_area_cfg_new.lua"
)
GROUP_NAMES = {
    11001: "Town Nightraid",
    11002: "Abandoned Chemical Plant",
    11003: "Forest Training",
}


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _asset_path(path: Path) -> Path:
    if path.exists():
        return path
    if path == DEFAULT_SECRET_AREA_ASSET and FALLBACK_SECRET_AREA_ASSET.exists():
        return FALLBACK_SECRET_AREA_ASSET
    return path


def _is_secret_area_stage_id(value: int | None) -> bool:
    if value is None:
        return False
    level_key = value // 100
    floor = value % 100
    return 1001 <= level_key <= 1016 and 1 <= floor <= 40


def _stage_ids(constants: list[object]) -> list[int]:
    try:
        start = constants.index("StageKey") + 1
    except ValueError:
        return []
    stage_ids: list[int] = []
    for value in constants[start:]:
        stage_id = _as_int(value)
        if _is_secret_area_stage_id(stage_id):
            stage_ids.append(int(stage_id))
    return stage_ids


def _group_hints(constants: list[object]) -> list[dict[str, object]]:
    groups: list[dict[str, object]] = []
    for index, value in enumerate(constants):
        group_id = _as_int(value)
        if group_id not in GROUP_NAMES:
            continue
        groups.append({"group_id": group_id, "group_name": GROUP_NAMES[group_id]})
    return groups


def collect_secret_area_stage_hints(
    secret_area_asset: Path = DEFAULT_SECRET_AREA_ASSET,
) -> dict[str, object]:
    asset = _asset_path(secret_area_asset)
    constants = _RootConstantReader(asset.read_bytes()).root_constants()
    stage_ids = _stage_ids(constants)
    stages = [
        {
            "stage_id": stage_id,
            "level_range_id": stage_id // 100,
            "floor": stage_id % 100,
            "group_name": "Secret Area",
            "label": f"Secret Area {stage_id // 100} Floor {stage_id % 100}",
            "source": SECRET_AREA_SOURCE,
        }
        for stage_id in stage_ids
    ]
    return {
        "source": SECRET_AREA_SOURCE,
        "constant_count": len(constants),
        "stage_count": len(stages),
        "groups": _group_hints(constants),
        "stages": stages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover Secret Area stage keys from packed Lua constants."
    )
    parser.add_argument("--asset", type=Path, default=DEFAULT_SECRET_AREA_ASSET)
    args = parser.parse_args()
    print(
        json.dumps(
            collect_secret_area_stage_hints(args.asset),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
