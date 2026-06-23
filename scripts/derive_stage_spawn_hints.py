from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_asset_drama_stage_hints import DEFAULT_ASSET_ROOT
from derive_stage_cfg_route_hints import _RootConstantReader
from derive_stage_cfg_route_hints import DEFAULT_STAGE_CFG_ASSET
from derive_monster_cfg_hints import DEFAULT_MONSTER_CFG_ASSET
from derive_stage_monster_evidence import collect_stage_monster_evidence


SKIP_SCAN_SUFFIXES = {
    ".css",
    ".flv",
    ".html",
    ".jpg",
    ".json",
    ".mp3",
    ".png",
    ".txt",
    ".wav",
}


def _as_number(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _as_int(value: object) -> int | None:
    number = _as_number(value)
    if number is None or not number.is_integer():
        return None
    return int(number)


def _stage_id_for_enemy(enemy_id: int) -> int:
    return enemy_id // 100


def _is_coord(value: float) -> bool:
    return -100000.0 < value < 100000.0


def _last_coord_run_before(
    constants: list[object],
    index: int,
    *,
    limit: int = 12,
) -> tuple[float, float, float] | None:
    start = max(0, index - limit)
    best: tuple[float, float, float] | None = None
    run: list[float] = []
    for value in constants[start:index]:
        number = _as_number(value)
        if number is None or not _is_coord(number):
            if len(run) >= 3:
                best = tuple(run[-3:])  # type: ignore[assignment]
            run = []
            continue
        run.append(number)
    if len(run) >= 3:
        best = tuple(run[-3:])  # type: ignore[assignment]
    return best


def _coord_run_before_monster_command(
    constants: list[object],
    monster_index: int,
) -> tuple[float, float, float, int] | None:
    start = max(0, monster_index - 16)
    runs: list[list[float]] = []
    run: list[float] = []
    for value in constants[start:monster_index]:
        number = _as_number(value)
        if number is None or not _is_coord(number):
            if run:
                runs.append(run)
            run = []
            continue
        run.append(number)
    if run:
        runs.append(run)

    for run in reversed(runs):
        if len(run) >= 4 and abs(run[0]) > 1000 and abs(run[1]) > 1000:
            face = int(round(run[3])) if abs(run[3]) <= 360 else 0
            return run[0], run[1], run[2], face
    for run in reversed(runs):
        if len(run) >= 5 and abs(run[1]) > 1000 and abs(run[2]) > 1000:
            face = int(round(run[4])) if abs(run[4]) <= 360 else 0
            return run[1], run[2], run[3], face
    return None


def _coords_after(
    constants: list[object],
    index: int,
) -> tuple[float, float, float] | None:
    values = [_as_number(value) for value in constants[index + 1 : index + 4]]
    if any(value is None or not _is_coord(value) for value in values):
        return None
    return values[0], values[1], values[2]  # type: ignore[return-value]


def _face_after_coords(constants: list[object], index: int) -> int:
    number = _as_number(constants[index + 4]) if index + 4 < len(constants) else None
    if number is None or abs(number) > 360:
        return 0
    return int(round(number))


def _monster_info_index_before(constants: list[object], index: int) -> int | None:
    for cursor in range(index - 1, max(-1, index - 42), -1):
        if constants[cursor] == "MonsterInfo":
            return cursor
    return None


def _monster_command_index_before(constants: list[object], index: int) -> int | None:
    for cursor in range(index - 1, max(-1, index - 14), -1):
        if constants[cursor] == "monster":
            return cursor
        if isinstance(constants[cursor], str) and constants[cursor] in {
            "NpcInfo",
            "MonsterInfo",
        }:
            return None
    return None


def _compact_enemy_table_hint(
    constants: list[object],
    index: int,
    enemy_id: int,
) -> dict[str, object] | None:
    # Some packed stage rows are compact name/x/y/(face-or-scale)/enemy-id
    # tables instead of keyed MonsterInfo dictionaries.
    if index >= 4 and isinstance(constants[index - 4], str):
        x = _as_number(constants[index - 3])
        y = _as_number(constants[index - 2])
        face_value = _as_number(constants[index - 1])
        if (
            x is not None
            and y is not None
            and face_value is not None
            and abs(x) > 1000
            and abs(y) > 1000
            and _is_coord(x)
            and _is_coord(y)
        ):
            face = (
                int(round(face_value))
                if 2 <= abs(face_value) <= 360
                else 0
            )
            return {
                "enemy_id": enemy_id,
                "x": int(round(x)),
                "y": int(round(y)),
                "z": 0,
                "face": face,
                "pattern": "compact_enemy_table",
            }

    if index >= 3 and isinstance(constants[index - 3], str):
        x = _as_number(constants[index - 2])
        y = _as_number(constants[index - 1])
        if (
            x is not None
            and y is not None
            and abs(x) > 1000
            and abs(y) > 1000
            and _is_coord(x)
            and _is_coord(y)
        ):
            return {
                "enemy_id": enemy_id,
                "x": int(round(x)),
                "y": int(round(y)),
                "z": 0,
                "face": 0,
                "pattern": "compact_enemy_table",
            }

    return None


def _spawn_hint_for_index(
    constants: list[object],
    index: int,
    enemy_id: int,
) -> dict[str, object] | None:
    monster_info_index = _monster_info_index_before(constants, index)
    if monster_info_index is not None:
        id_key_index = None
        for cursor in range(index - 1, max(monster_info_index - 1, index - 4), -1):
            if constants[cursor] == "Id":
                id_key_index = cursor
                break
        coords = (
            _last_coord_run_before(constants, id_key_index)
            if id_key_index is not None
            else None
        )
        if coords is not None:
            return {
                "enemy_id": enemy_id,
                "x": int(round(coords[0])),
                "y": int(round(coords[1])),
                "z": int(round(coords[2])),
                "face": 0,
                "pattern": "MonsterInfo",
            }

    compact_table_hint = _compact_enemy_table_hint(constants, index, enemy_id)
    if compact_table_hint is not None:
        return compact_table_hint

    monster_command_index = _monster_command_index_before(constants, index)
    if monster_command_index is None:
        return None
    if index == monster_command_index + 1:
        command_coords = _coord_run_before_monster_command(
            constants, monster_command_index
        )
        coords = command_coords[:3] if command_coords is not None else None
        face = command_coords[3] if command_coords is not None else 0
    else:
        coords = _coords_after(constants, index)
        face = _face_after_coords(constants, index) if coords is not None else 0
    if coords is None:
        return None
    return {
        "enemy_id": enemy_id,
        "x": int(round(coords[0])),
        "y": int(round(coords[1])),
        "z": int(round(coords[2])),
        "face": face,
        "pattern": "drama_monster_command",
    }


def _spawn_hint_priority(hint: dict[str, object]) -> int:
    pattern = str(hint.get("pattern") or "")
    return {
        "MonsterInfo": 3,
        "drama_monster_command": 3,
        "compact_enemy_table": 2,
    }.get(pattern, 1)


def collect_stage_spawn_hints(
    asset_root: Path = DEFAULT_ASSET_ROOT,
    stage_cfg_asset: Path | None = None,
    monster_cfg_asset: Path = DEFAULT_MONSTER_CFG_ASSET,
    target_ids: tuple[int, ...] | None = None,
) -> dict[str, object]:
    if target_ids is None:
        evidence = collect_stage_monster_evidence(
            monster_cfg_asset=monster_cfg_asset,
            stage_cfg_asset=stage_cfg_asset or DEFAULT_STAGE_CFG_ASSET,
            asset_root=asset_root,
        )
        target_ids = tuple(
            int(enemy_id)
            for enemy_id, item in evidence["evidence"].items()
            if item["combat_candidate"]
        )
    wanted = set(target_ids)

    stage_spawns_by_enemy: dict[int, dict[str, object]] = {}
    scanned = 0
    parsed = 0
    for path in asset_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in SKIP_SCAN_SUFFIXES:
            continue
        scanned += 1
        try:
            constants = _RootConstantReader(path.read_bytes()).root_constants()
        except Exception:
            continue
        parsed += 1
        for index, value in enumerate(constants):
            enemy_id = _as_int(value)
            if enemy_id not in wanted:
                continue
            hint = _spawn_hint_for_index(constants, index, enemy_id)
            if hint is None:
                continue
            hint["source_asset"] = str(path.relative_to(asset_root)).replace("\\", "/")
            existing = stage_spawns_by_enemy.get(enemy_id)
            if existing is None or _spawn_hint_priority(hint) > _spawn_hint_priority(
                existing
            ):
                stage_spawns_by_enemy[enemy_id] = hint

    stage_spawns: dict[int, list[dict[str, object]]] = {}
    for enemy_id, hint in sorted(stage_spawns_by_enemy.items()):
        stage_spawns.setdefault(_stage_id_for_enemy(enemy_id), []).append(hint)

    return {
        "target_count": len(target_ids),
        "scanned_file_count": scanned,
        "parsed_file_count": parsed,
        "stage_count": len(stage_spawns),
        "spawn_count": sum(len(spawns) for spawns in stage_spawns.values()),
        "stages": {
            str(stage_id): sorted(spawns, key=lambda item: int(item["enemy_id"]))
            for stage_id, spawns in sorted(stage_spawns.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover conservative authored monster spawn coordinate hints."
    )
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    parser.add_argument("--stage-cfg", type=Path, default=DEFAULT_STAGE_CFG_ASSET)
    parser.add_argument("--monster-cfg", type=Path, default=DEFAULT_MONSTER_CFG_ASSET)
    parser.add_argument("--enemy-id", action="append", type=int, dest="enemy_ids")
    args = parser.parse_args()

    print(
        json.dumps(
            collect_stage_spawn_hints(
                asset_root=args.asset_root,
                stage_cfg_asset=args.stage_cfg,
                monster_cfg_asset=args.monster_cfg,
                target_ids=tuple(args.enemy_ids) if args.enemy_ids else None,
            ),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
