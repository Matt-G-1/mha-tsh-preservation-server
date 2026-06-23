from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


HERO_ACTION_RE = re.compile(r"BATTLE/HERO/([^/]+)/([^\"'\s\x00]+)", re.IGNORECASE)

KNOWN_HERO_ACTION_MODELS = {
    "allmight": "h1003",
    "andewa": "h1021",
    "babaiwan": "h1009",
    "baohao": "h1002",
    "bodong": "h1030",
    "changan": "h1022",
    "fantian": "h1006",
    "fengtian": "h1006",
    "hong": "h1008",
    "huokesi": "h1026",
    "lvgu": "h1001",
    "newbaohao_jcb": "h1028",
    "newhong_jcb": "h1029",
    "newlvgu_jcb": "h1027",
    "qiedao": "h1013",
    "sannai": "h1017",
    "shangming": "h1010",
    "sibingmudiao": "h1019",
    "sitanyin": "h1110",
    "tiancanhuan": "h1031",
    "tongxingbaiwan": "h1032",
    "tupi": "h1012",
    "tupi_new": "h1012",
    "wachui": "h1014",
    "weibaiyuanfu": "h1016",
    "xiangze": "h1015",
    "yuchazi": "h1007",
}

SKIP_SUFFIXES = {
    ".flv",
    ".jpg",
    ".mp3",
    ".png",
    ".wav",
}


def _candidate_values(record: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("strings", "names"):
        for item in record.get(key) or []:
            if isinstance(item, dict):
                values.append(str(item.get("value", "")))
            else:
                values.append(str(item))
    return values


def _path_values(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        records = json.loads(text)
    except json.JSONDecodeError:
        return [text]
    if not isinstance(records, list):
        return [text]
    values: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            values.append(str(record))
            continue
        values.extend(_candidate_values(record))
    return values


def _input_files(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(
                child
                for child in path.rglob("*")
                if child.is_file() and child.suffix.lower() not in SKIP_SUFFIXES
            )
        elif path.is_file():
            files.append(path)
    return tuple(files)


def _clean_action(action: str) -> str:
    return action.rstrip("@.},")


def collect_action_hints(paths: tuple[Path, ...]) -> dict[str, set[str]]:
    hints: dict[str, set[str]] = defaultdict(set)
    for path in _input_files(paths):
        for value in _path_values(path):
            for hero_key, action in HERO_ACTION_RE.findall(value):
                normalized_action = _clean_action(action)
                hints[hero_key.lower()].add(
                    f"BATTLE/HERO/{hero_key.lower()}/{normalized_action}"
                )
    return hints


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize recovered MHA TSH hero combat action hints."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=(
            Path("analysis/stage_candidates.json"),
            Path("analysis/stage_candidates"),
            Path("analysis/battle_stage_candidate_catalog.json"),
            Path("analysis/intro_qte_asset_index.txt"),
            Path("analysis/mediafire_20260620/apk_extract/assets"),
        ),
    )
    args = parser.parse_args()

    hints = collect_action_hints(tuple(args.paths))
    summary = {
        hero_key: {
            "model_asset_id": KNOWN_HERO_ACTION_MODELS.get(hero_key),
            "actions": sorted(actions),
        }
        for hero_key, actions in sorted(hints.items())
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
