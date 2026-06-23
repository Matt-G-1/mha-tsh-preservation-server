from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_HERO_SUPPORTS_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "0QIU"
    / "17d0df31842d7982"
)

SUPPORT_SKILL_TERMS_BY_MODEL = {
    "h1019": ("Vicious Contact",),
    "h1021": ("Exploding Lance",),
    "h1024": ("Smash!",),
    "h1026": ("Downfall",),
    "h1027": ("WHM Shoot Style",),
    "h1028": ("Turbo Twister",),
    "h1029": ("Icicle Storm",),
    "h1030": ("Wave Blast",),
    "h1031": ("Tentacles Grasp",),
}


def _snippet(data: bytes, offset: int, term: str) -> str:
    start = max(0, offset - 120)
    end = min(len(data), offset + len(term.encode("utf-8")) + 180)
    chunk = data[start:end]
    return "".join(chr(value) if 32 <= value < 127 else "." for value in chunk)


def collect_support_skill_hints(path: Path) -> dict[str, dict[str, object]]:
    data = path.read_bytes()
    lowered = data.lower()
    hints: dict[str, dict[str, object]] = {}
    for model_id, terms in sorted(SUPPORT_SKILL_TERMS_BY_MODEL.items()):
        model_terms: dict[str, dict[str, object]] = {}
        for term in terms:
            needle = term.lower().encode("utf-8")
            offsets = [match.start() for match in re.finditer(re.escape(needle), lowered)]
            model_terms[term] = {
                "count": len(offsets),
                "locations": [
                    {"source": path.as_posix(), "offset": offset}
                    for offset in offsets[:8]
                ],
                "snippets": [_snippet(data, offset, term) for offset in offsets[:2]],
            }
        hints[model_id] = {"terms": model_terms}
    return hints


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover hero support-skill text hints from hero_supports_cfg."
    )
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_HERO_SUPPORTS_ASSET)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_support_skill_hints(args.path),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
