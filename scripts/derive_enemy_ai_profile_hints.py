from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_asset_drama_stage_hints import DEFAULT_ASSET_ROOT
from derive_monster_cfg_hints import DEFAULT_MONSTER_CFG_ASSET
from derive_stage_cfg_route_hints import DEFAULT_STAGE_CFG_ASSET
from derive_stage_monster_evidence import collect_stage_monster_evidence


BOSS_MARKERS = (
    "BOSS",
    "Boss",
    "boss",
    "\u5de8\u5927\u5316",
)
ELITE_MARKERS = (
    "\u7cbe\u82f1",
)
RANGED_MARKERS = (
    "\u8fdc\u7a0b",
    "\u67aa",
)
MECHANICAL_MARKERS = (
    "\u673a\u7532",
)
NOMU_MARKERS = (
    "\u8111\u65e0",
    "Nomu",
)


def profile_for_enemy_name(enemy_id: int, name: str) -> str:
    if enemy_id == 2005:
        return "training_enemy"
    if enemy_id == 3002:
        return "sludge_boss"
    if any(marker in name for marker in NOMU_MARKERS):
        return "nomu_brute"
    if any(marker in name for marker in BOSS_MARKERS):
        return "boss_brute"
    if any(marker in name for marker in RANGED_MARKERS):
        return "ranged_pressure"
    if any(marker in name for marker in MECHANICAL_MARKERS):
        return "mechanical_patrol"
    if any(marker in name for marker in ELITE_MARKERS):
        return "elite_chaser"
    return "melee_chaser"


def collect_enemy_ai_profile_hints(
    *,
    monster_cfg_asset: Path = DEFAULT_MONSTER_CFG_ASSET,
    stage_cfg_asset: Path = DEFAULT_STAGE_CFG_ASSET,
    asset_root: Path = DEFAULT_ASSET_ROOT,
) -> dict[str, object]:
    evidence = collect_stage_monster_evidence(
        monster_cfg_asset=monster_cfg_asset,
        stage_cfg_asset=stage_cfg_asset,
        asset_root=asset_root,
    )
    profiles: dict[str, dict[str, object]] = {}
    for enemy_id_text, item in evidence["evidence"].items():
        if not item["combat_candidate"]:
            continue
        enemy_id = int(enemy_id_text)
        name = str(item["name"])
        profile = profile_for_enemy_name(enemy_id, name)
        if profile == "melee_chaser":
            continue
        profiles[enemy_id_text] = {
            "enemy_id": enemy_id,
            "profile": profile,
            "name": name,
            "animation_keys": item["animation_keys"],
        }

    return {
        "source_combat_candidate_count": evidence["combat_candidate_count"],
        "profile_override_count": len(profiles),
        "profiles": dict(sorted(profiles.items(), key=lambda pair: int(pair[0]))),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Infer stage enemy AI profile hints from parsed monster names."
    )
    parser.add_argument("--monster-cfg", type=Path, default=DEFAULT_MONSTER_CFG_ASSET)
    parser.add_argument("--stage-cfg", type=Path, default=DEFAULT_STAGE_CFG_ASSET)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_enemy_ai_profile_hints(
                monster_cfg_asset=args.monster_cfg,
                stage_cfg_asset=args.stage_cfg,
                asset_root=args.asset_root,
            ),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
