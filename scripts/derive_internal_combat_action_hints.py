from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_ASSET_ROOT = Path("analysis/mediafire_20260620/apk_extract/assets")

INTERNAL_ACTION_PREFIXES_BY_MODEL = {
    "h1020": ("putao",),
}

SKIP_SUFFIXES = {
    ".flv",
    ".jpg",
    ".mp3",
    ".png",
    ".wav",
}


def _input_files(root: Path) -> tuple[Path, ...]:
    return tuple(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() not in SKIP_SUFFIXES
    )


def _token_re(prefixes: tuple[str, ...]) -> re.Pattern[bytes]:
    joined = b"|".join(re.escape(prefix.encode("ascii")) for prefix in prefixes)
    return re.compile(
        rb"(?<![A-Za-z0-9_])("
        + joined
        + rb"(?:/[A-Za-z0-9_]+|_[A-Za-z0-9_]+){0,3})"
    )


def collect_internal_action_hints(
    asset_root: Path = DEFAULT_ASSET_ROOT,
) -> dict[str, dict[str, object]]:
    prefixes = tuple(
        prefix
        for model_prefixes in INTERNAL_ACTION_PREFIXES_BY_MODEL.values()
        for prefix in model_prefixes
    )
    token_re = _token_re(prefixes)
    tokens_by_prefix: dict[str, set[str]] = defaultdict(set)
    locations_by_prefix: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in _input_files(asset_root):
        data = path.read_bytes()
        for match in token_re.finditer(data):
            token = match.group(1).decode("ascii", errors="ignore").rstrip("_.")
            prefix = token.split("/", 1)[0].split("_", 1)[0]
            tokens_by_prefix[prefix].add(token)
            if len(locations_by_prefix[prefix]) < 8:
                locations_by_prefix[prefix].append(
                    {"source": path.as_posix(), "offset": match.start()}
                )

    summary: dict[str, dict[str, object]] = {}
    for model_id, model_prefixes in sorted(INTERNAL_ACTION_PREFIXES_BY_MODEL.items()):
        model_tokens = {
            token
            for prefix in model_prefixes
            for token in tokens_by_prefix.get(prefix, ())
        }
        model_locations = [
            location
            for prefix in model_prefixes
            for location in locations_by_prefix.get(prefix, ())
        ]
        summary[model_id] = {
            "prefixes": list(model_prefixes),
            "tokens": sorted(model_tokens),
            "locations": model_locations[:8],
        }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover internal hero combat/action tokens without BATTLE/HERO paths."
    )
    parser.add_argument("asset_root", nargs="?", type=Path, default=DEFAULT_ASSET_ROOT)
    args = parser.parse_args()
    print(
        json.dumps(
            collect_internal_action_hints(args.asset_root),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
