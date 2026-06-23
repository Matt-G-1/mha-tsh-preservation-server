from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_MONSTER_CFG_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "1FO"
    / "fee3a47c0b4a95e9"
)

DEFAULT_MONSTER_IDS = (
    2005,
    2202,
    2470,
    2471,
    2472,
    3002,
    3003,
    3005,
    3006,
    3007,
    3016,
    3125,
)

ANIMATION_KEY_RE = re.compile(rb"(?P<key>\d{4,7}_[A-Za-z0-9]+(?:_[A-Za-z0-9]+)*)")
DISPLAY_NAME_RE = re.compile(rb"[A-Z][A-Za-z]+(?:[ .'][A-Z][A-Za-z]+){0,3}")

NOISE_TOKENS = {
    "BOSS",
    "Boss",
    "NPC",
    "PVP",
    "NA",
    "VA",
    "USJ",
    "PVP-USJ",
    "FA",
    "A1",
    "A2",
    "B1",
    "B2",
}


def _is_display_name_candidate(token: str) -> bool:
    if token in NOISE_TOKENS or any(noise in token for noise in ("BOSS", "USJ", "NPC")):
        return False
    if re.fullmatch(r"[A-Z0-9.+/-]{1,4}", token):
        return False
    return any(char.islower() for char in token) or " " in token or "'" in token


def _display_name_candidates_after(data: bytes, end_offset: int) -> list[str]:
    window = data[end_offset : end_offset + 260]
    candidates: list[str] = []
    for match in DISPLAY_NAME_RE.finditer(window):
        candidate = match.group(0).decode("ascii", "ignore").strip(" .")
        if _is_display_name_candidate(candidate) and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def collect_monster_cfg_hints(
    path: Path,
    monster_ids: tuple[int, ...] = DEFAULT_MONSTER_IDS,
) -> dict[int, dict[str, object]]:
    wanted = {str(monster_id) for monster_id in monster_ids}
    animation_keys: dict[int, set[str]] = defaultdict(set)
    display_names: dict[int, set[str]] = defaultdict(set)
    data = path.read_bytes()

    for match in ANIMATION_KEY_RE.finditer(data):
        animation_key = match.group("key").decode("ascii", "ignore")
        monster_id_text = animation_key.split("_", 1)[0]
        if monster_id_text not in wanted:
            continue
        monster_id = int(monster_id_text)
        animation_keys[monster_id].add(animation_key)
        display_names[monster_id].update(_display_name_candidates_after(data, match.end()))

    return {
        monster_id: {
            "animation_keys": sorted(animation_keys.get(monster_id, ())),
            "display_names": sorted(display_names.get(monster_id, ())),
        }
        for monster_id in monster_ids
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover conservative monster_cfg enemy hints from packed assets."
    )
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_MONSTER_CFG_ASSET)
    parser.add_argument(
        "--monster-id",
        action="append",
        type=int,
        dest="monster_ids",
        help="Monster ID to inspect. May be passed multiple times.",
    )
    args = parser.parse_args()

    monster_ids = (
        tuple(args.monster_ids) if args.monster_ids else DEFAULT_MONSTER_IDS
    )
    print(
        json.dumps(
            collect_monster_cfg_hints(args.path, monster_ids),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
