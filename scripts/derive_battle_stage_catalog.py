from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


STAGE_SCRIPT_RE = re.compile(r"(?:^|/)(stage\d+(?:_[a-z0-9]+)?|zx_[a-z0-9_]+)\.lua")
NUMERIC_STAGE_RE = re.compile(r"^stage(\d+)")


def load_candidate_assets(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_stage_index(path: Path) -> dict[str, set[str]]:
    scripts: dict[str, set[str]] = defaultdict(set)
    for match in STAGE_SCRIPT_RE.finditer(
        path.read_text(encoding="utf-8", errors="ignore")
    ):
        script = match.group(1)
        numeric = NUMERIC_STAGE_RE.match(script)
        key = numeric.group(1) if numeric else script
        scripts[key].add(script)
    return scripts


def collect_asset_names(candidates: list[dict[str, Any]]) -> dict[str, set[str]]:
    clusters: dict[str, set[str]] = defaultdict(set)
    for item in candidates:
        for name in item.get("names", []):
            for token in re.findall(r"zx_(?:battle|lvb|ruxue)[a-z0-9_+]*", name):
                clusters[token].add(name)
            if "BATTLE/HERO/allmight" in name or "allmight" in name.lower():
                clusters["allmight"].add(name)
    return clusters


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize recovered MHA TSH battle/drama stage evidence."
    )
    parser.add_argument(
        "--stage-index",
        type=Path,
        default=Path("analysis/intro_qte_asset_index.txt"),
    )
    parser.add_argument(
        "--asset-catalog",
        type=Path,
        default=Path("analysis/battle_stage_candidate_catalog.json"),
    )
    args = parser.parse_args()

    scripts = parse_stage_index(args.stage_index)
    assets = collect_asset_names(load_candidate_assets(args.asset_catalog))
    summary = {
        "numeric_stage_count": sum(key.isdigit() for key in scripts),
        "zx_script_count": sum(key.startswith("zx_") for key in scripts),
        "numeric_stages": {
            key: sorted(values)
            for key, values in sorted(scripts.items())
            if key.isdigit()
        },
        "zx_scripts": {
            key: sorted(values)
            for key, values in sorted(scripts.items())
            if key.startswith("zx_")
        },
        "asset_clusters": {
            key: sorted(values)[:25] for key, values in sorted(assets.items())
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
