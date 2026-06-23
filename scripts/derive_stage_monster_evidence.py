from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_asset_drama_stage_hints import DEFAULT_ASSET_ROOT
from derive_stage_cfg_encounter_hints import collect_stage_cfg_encounter_hints
from derive_stage_cfg_route_hints import DEFAULT_STAGE_CFG_ASSET, _RootConstantReader
from derive_monster_cfg_hints import DEFAULT_MONSTER_CFG_ASSET


ANIMATION_KEY_RE = re.compile(r"^\d{4,8}_[A-Za-z0-9_]+$")

COMBAT_NAME_MARKERS = (
    "\u5c0f\u602a",  # small monster
    "\u7cbe\u82f1",  # elite
    "\u602a",  # monster
    "\u654c",  # enemy
    "\u8111\u65e0",  # Nomu
    "-\u901f",  # speed type
    "-\u529b",  # power type
    "-\u6280",  # technique type
    "BOSS",
    "Boss",
    "Monster",
    "monster",
    "Villain",
    "villain",
    "Nomu",
)

NON_COMBAT_NAME_MARKERS = (
    "NPC",
    "npc",
    "\u7a7a\u6a21\u578b",  # empty model
    "\u9632\u62a4\u7f69",  # shield
    "\u673a\u5173",  # mechanism
    "\u7279\u6b8a",  # special object
    "\u6d88\u9632\u6813",  # fire hydrant
    "\u6c34\u9f99\u5377",  # water cyclone/hazard
    "Protective Mask",
)


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _target_enemy_ids(
    stage_cfg_asset: Path,
    asset_root: Path,
) -> tuple[int, ...]:
    hints = collect_stage_cfg_encounter_hints(stage_cfg_asset, asset_root)
    ids: set[int] = set()
    for encounter in hints["encounters"].values():
        for enemy_id in encounter["enemy_group_ids"]:
            if isinstance(enemy_id, int):
                ids.add(enemy_id)
    return tuple(sorted(ids))


def _name_after(constants: list[object], index: int) -> str:
    for value in constants[index + 1 : index + 8]:
        if not isinstance(value, str):
            continue
        if ANIMATION_KEY_RE.match(value):
            continue
        return value
    return ""


def _animation_keys_near(constants: list[object], index: int) -> tuple[str, ...]:
    start = max(0, index - 6)
    end = min(len(constants), index + 10)
    keys = {
        value
        for value in constants[start:end]
        if isinstance(value, str) and ANIMATION_KEY_RE.match(value)
    }
    return tuple(sorted(keys))


def _is_combat_name(name: str) -> bool:
    if any(marker in name for marker in NON_COMBAT_NAME_MARKERS):
        return False
    return any(marker in name for marker in COMBAT_NAME_MARKERS)


def collect_stage_monster_evidence(
    monster_cfg_asset: Path = DEFAULT_MONSTER_CFG_ASSET,
    stage_cfg_asset: Path | None = None,
    asset_root: Path | None = None,
    target_ids: tuple[int, ...] | None = None,
) -> dict[str, object]:
    if target_ids is None:
        target_ids = _target_enemy_ids(
            stage_cfg_asset or DEFAULT_STAGE_CFG_ASSET,
            asset_root or DEFAULT_ASSET_ROOT,
        )

    constants = _RootConstantReader(monster_cfg_asset.read_bytes()).root_constants()
    wanted = set(target_ids)
    evidence: dict[int, dict[str, object]] = {}
    for index, value in enumerate(constants):
        enemy_id = _as_int(value)
        if enemy_id not in wanted or enemy_id in evidence:
            continue
        name = _name_after(constants, index)
        evidence[enemy_id] = {
            "enemy_id": enemy_id,
            "name": name,
            "animation_keys": _animation_keys_near(constants, index),
            "combat_candidate": _is_combat_name(name),
        }

    return {
        "target_count": len(target_ids),
        "evidence_count": len(evidence),
        "combat_candidate_count": sum(
            1 for item in evidence.values() if item["combat_candidate"]
        ),
        "evidence": {
            str(enemy_id): evidence[enemy_id]
            for enemy_id in sorted(evidence)
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover stage encounter enemy names and combat-candidate hints."
    )
    parser.add_argument("--monster-cfg", type=Path, default=DEFAULT_MONSTER_CFG_ASSET)
    parser.add_argument("--enemy-id", action="append", type=int, dest="enemy_ids")
    args = parser.parse_args()

    print(
        json.dumps(
            collect_stage_monster_evidence(
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
