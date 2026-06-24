from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_DRAMA_INDEX = Path("analysis") / "intro_qte_asset_index.txt"
SCRIPT_RE = re.compile(r"\./script/setting/dramas/([^\s'\"\]]+)\.lua")
PREFIXED_NUMERIC_RE = re.compile(
    r"^(?P<prefix>fzx|tc|xht)_(?P<stage_id>\d{6,8})(?:[_!].*)?$"
)


def collect_prefixed_numeric_drama_stage_hints(
    drama_index: Path = DEFAULT_DRAMA_INDEX,
) -> dict[str, object]:
    text = drama_index.read_text(encoding="utf-8", errors="ignore")
    groups: dict[int, list[str]] = {}
    for match in SCRIPT_RE.finditer(text):
        script = match.group(1)
        numeric = PREFIXED_NUMERIC_RE.match(script)
        if numeric is None:
            continue
        stage_id = int(numeric.group("stage_id"))
        scripts = groups.setdefault(stage_id, [])
        if script not in scripts:
            scripts.append(script)

    return {
        "source": drama_index.as_posix(),
        "stage_count": len(groups),
        "stages": [
            {"stage_id": stage_id, "scripts": sorted(scripts)}
            for stage_id, scripts in sorted(groups.items())
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover prefixed numeric drama-stage groups from the drama index."
    )
    parser.add_argument("--drama-index", type=Path, default=DEFAULT_DRAMA_INDEX)
    args = parser.parse_args()
    print(
        json.dumps(
            collect_prefixed_numeric_drama_stage_hints(args.drama_index),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
