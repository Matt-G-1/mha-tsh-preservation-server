from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_asset_drama_stage_hints import DEFAULT_ASSET_ROOT
from derive_monster_cfg_hints import DEFAULT_MONSTER_CFG_ASSET
from derive_stage_cfg_route_hints import (
    DEFAULT_STAGE_CFG_ASSET,
    _RootConstantReader,
    collect_stage_cfg_route_hints,
)


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _same_stage_group_ids(
    constants: list[object],
    stage_id: int,
    constant_index: int,
    lookbehind: int = 18,
    lookahead: int = 22,
) -> tuple[int, ...]:
    prefix = str(stage_id)
    group_ids: list[int] = []
    start = max(0, constant_index - lookbehind)
    end = min(len(constants), constant_index + lookahead)
    for value in constants[start:end]:
        number = _as_int(value)
        if number is None or number == stage_id:
            continue
        if str(number).startswith(prefix) and number not in group_ids:
            group_ids.append(number)
    return tuple(group_ids)


def collect_stage_cfg_encounter_hints(
    stage_cfg_asset: Path = DEFAULT_STAGE_CFG_ASSET,
    asset_root: Path = DEFAULT_ASSET_ROOT,
    monster_cfg_asset: Path | None = None,
) -> dict[str, object]:
    constants = _RootConstantReader(stage_cfg_asset.read_bytes()).root_constants()
    route_hints = collect_stage_cfg_route_hints(stage_cfg_asset, asset_root)
    encounters: dict[str, dict[str, object]] = {}
    for script, route in route_hints["routes"].items():
        stage_id = route.get("route_stage_id")
        constant_index = route.get("constant_index")
        if not isinstance(stage_id, int) or not isinstance(constant_index, int):
            continue
        group_ids = _same_stage_group_ids(constants, stage_id, constant_index)
        if not group_ids:
            continue
        stage_key = str(stage_id)
        entry = encounters.setdefault(
            stage_key,
            {"stage_id": stage_id, "scripts": [], "enemy_group_ids": []},
        )
        entry["scripts"].append(script)
        for group_id in group_ids:
            if group_id not in entry["enemy_group_ids"]:
                entry["enemy_group_ids"].append(group_id)

    combat_enemy_ids_by_stage = _combat_enemy_ids_by_stage(
        encounters,
        monster_cfg_asset or _default_monster_cfg_asset_for(stage_cfg_asset),
    )
    return {
        "stage_count": len(encounters),
        "encounters": {
            stage_id: {
                "stage_id": value["stage_id"],
                "scripts": sorted(value["scripts"]),
                "enemy_group_ids": sorted(value["enemy_group_ids"]),
                "combat_enemy_ids": combat_enemy_ids_by_stage.get(
                    int(stage_id), []
                ),
            }
            for stage_id, value in sorted(encounters.items(), key=lambda item: int(item[0]))
        },
    }


def _default_monster_cfg_asset_for(stage_cfg_asset: Path) -> Path:
    if DEFAULT_MONSTER_CFG_ASSET.exists():
        return DEFAULT_MONSTER_CFG_ASSET
    for parent in stage_cfg_asset.resolve().parents:
        candidate = parent / DEFAULT_MONSTER_CFG_ASSET
        if candidate.exists():
            return candidate
    return DEFAULT_MONSTER_CFG_ASSET


def _combat_enemy_ids_by_stage(
    encounters: dict[str, dict[str, object]],
    monster_cfg_asset: Path,
) -> dict[int, list[int]]:
    from derive_stage_monster_evidence import collect_stage_monster_evidence

    target_ids = tuple(
        sorted(
            {
                enemy_id
                for encounter in encounters.values()
                for enemy_id in encounter["enemy_group_ids"]
                if isinstance(enemy_id, int)
            }
        )
    )
    monster_evidence = collect_stage_monster_evidence(
        monster_cfg_asset=monster_cfg_asset,
        target_ids=target_ids,
    )
    combat_ids = {
        int(enemy_id)
        for enemy_id, item in monster_evidence["evidence"].items()
        if item["combat_candidate"]
    }
    return {
        int(stage_id): [
            enemy_id
            for enemy_id in sorted(value["enemy_group_ids"])
            if isinstance(enemy_id, int) and enemy_id in combat_ids
        ]
        for stage_id, value in encounters.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover stage_cfg same-prefix enemy/group IDs near routed scripts."
    )
    parser.add_argument("--stage-cfg", type=Path, default=DEFAULT_STAGE_CFG_ASSET)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    parser.add_argument("--monster-cfg", type=Path, default=DEFAULT_MONSTER_CFG_ASSET)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_stage_cfg_encounter_hints(
                args.stage_cfg,
                args.asset_root,
                args.monster_cfg,
            ),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
