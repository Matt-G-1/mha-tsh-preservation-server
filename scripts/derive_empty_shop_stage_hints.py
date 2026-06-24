from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_EMPTY_SHOP_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "3BAO"
    / "f42243de568cd0f0"
)
EMPTY_SHOP_STAGE_SOURCE = (
    "analysis/mediafire_20260620/apk_extract/assets/3BAO/f42243de568cd0f0, "
    "./script/setting/activity/act_empty_shop_cfg.lua"
)


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _is_empty_shop_stage_id(value: int | None) -> bool:
    return value is not None and 9001001 <= value <= 9006003 and value % 1000 in {
        1,
        2,
        3,
    }


def _const_value(constants: list[object], key: str) -> int:
    try:
        index = constants.index(key)
    except ValueError:
        return 0
    value = _as_int(constants[index + 1]) if index + 1 < len(constants) else None
    return int(value or 0)


def _stage_desc(constants: list[object], stage_index: int) -> str:
    if stage_index > 0 and isinstance(constants[stage_index - 1], str):
        previous = constants[stage_index - 1]
        is_hash = len(previous) == 32 and all(
            character in "0123456789abcdef" for character in previous.lower()
        )
        if previous not in {"StageId", "__md5", "__version"} and not is_hash:
            return previous
    for cursor in range(max(0, stage_index - 6), stage_index):
        if constants[cursor] != "StageDesc":
            continue
        if cursor + 1 < stage_index and isinstance(constants[cursor + 1], str):
            return constants[cursor + 1]
    return ""


def _fighting_thresholds(constants: list[object], stage_index: int) -> tuple[int, ...]:
    thresholds: list[int] = []
    cursor = stage_index + 1
    while cursor < len(constants):
        value = _as_int(constants[cursor])
        if value is None or _is_empty_shop_stage_id(value):
            break
        thresholds.append(value)
        cursor += 1
    return tuple(thresholds[:5])


def _challenge_index(stage_id: int) -> int:
    return (stage_id - 9000000) // 1000


def _generation(stage_id: int) -> int:
    return stage_id % 1000


def _empty_shop_stages(constants: list[object]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[int] = set()
    for index, value in enumerate(constants):
        stage_id = _as_int(value)
        if not _is_empty_shop_stage_id(stage_id) or stage_id in seen:
            continue
        seen.add(stage_id)
        desc = _stage_desc(constants, index)
        stage_index = len(rows) + 1
        rows.append(
            {
                "stage_id": stage_id,
                "stage_index": stage_index,
                "challenge_index": _challenge_index(stage_id),
                "generation": _generation(stage_id),
                "label": desc or f"Empty Shop challenge {stage_index}",
                "desc": desc,
                "fighting": list(_fighting_thresholds(constants, index)),
                "source": EMPTY_SHOP_STAGE_SOURCE,
            }
        )
    return rows


def collect_empty_shop_stage_hints(
    empty_shop_stage_asset: Path = DEFAULT_EMPTY_SHOP_STAGE_ASSET,
) -> dict[str, object]:
    constants = _RootConstantReader(empty_shop_stage_asset.read_bytes()).root_constants()
    stages = _empty_shop_stages(constants)
    return {
        "source": EMPTY_SHOP_STAGE_SOURCE,
        "constant_count": len(constants),
        "stage_count": len(stages),
        "start_task_id": _const_value(constants, "START_TASK_ID"),
        "end_task_id": _const_value(constants, "END_TASK_ID"),
        "stages": stages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover Empty Shop challenge stage rows from packed Lua constants."
    )
    parser.add_argument("--asset", type=Path, default=DEFAULT_EMPTY_SHOP_STAGE_ASSET)
    args = parser.parse_args()
    print(
        json.dumps(
            collect_empty_shop_stage_hints(args.asset),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
