from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_SKILL_INFO_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "2ZU"
    / "0a6af507ecd6f4a5"
)
DEFAULT_SKILL_INFO_ASSETS = (DEFAULT_SKILL_INFO_ASSET,)

SKILL_INFO_TERMS_BY_MODEL = {
    "h1001": ("Smash", "One For All", "Detroit Smash"),
    "h1002": ("Extra Explosion", "Bakugo"),
    "h1003": ("I Am Here!",),
    "h1006": ("Recipro Extend",),
    "h1008": ("Half-Cold Half-Hot", "Charge Ice Spear"),
    "h1009": ("Meteor Storm", "Q - Weapon Creation", "Yaoyorozu"),
    "h1010": ("Lightning Bolt",),
    "h1013": (
        "Kirishima Defense counter Q 2 tap",
        "Kirishima Q change 2 tap",
        "Kirishima Q change return",
        "Talent Aeration 4",
        "Kirishima W change Aeration 4",
        "Kirishima W Talent 10 cooldown",
    ),
    "h1014": ("Tongue Swipe",),
    "h1017": (
        "Mina Q",
        "Mina Enhanced Q",
        "Mina W slip",
        "Mina W end",
        "Mina E ready to spin",
        "Mina E upper cut",
        "Mina R",
        "Mina Q acid",
        "Mina Perfect Dodge slow",
        "Mina Perfect Dodge effect",
        "Mina Perfect Dodge QTE",
    ),
    "h1020": (
        "Firing Mode",
        "Exit Firing Mode",
        "Mineta-Bounce",
        "Dimensional Bounce",
        "Grape Rain",
        "Dodge 2",
    ),
    "h1021": ("Endeavor", "Exploding Lance"),
    "h1022": ("Abyssal Claw", "Shadow Zone", "Abyssal Talons"),
    "h1024": ("Smash!",),
    "h1019": ("Vicious Contact",),
    "h1026": (
        "Hawks passive",
        "Hawks Normal ATK 1",
        "Hawks Q open",
        "Hawks W",
        "Hawks E",
        "Hawks ult",
    ),
    "h1027": (
        "WHM绿谷普攻1",
        "Midoriya black whip",
        "Midoriya Q",
        "Midoriya W",
        "Midoriya E",
        "whm绿谷R",
    ),
    "h1028": (
        "Normal ATK 6 (Fly)",
        "Q Ground charge",
        "Q Ground machine gun",
        "Q Air 1",
        "W Wuhu takeoff",
        "W Air move",
        "E Fire tornado",
        "E Drill flame",
        "R Movie Ult (PVE)",
    ),
    "h1029": (
        "whm轰Q1",
        "whm轰Q2",
        "whm轰W1",
        "冰枪1段",
        "whm轰E",
        "火焰喷射",
        "whm轰R",
    ),
    "h1030": (
        "测试波动普攻1",
        "波动Q1",
        "Wave Blast",
        "波动W",
        "波动E1",
        "波动E2",
        "波动R",
    ),
    "h1031": (
        "天喰环普攻1",
        "天喰环Q1",
        "Tentacles Grasp",
        "天喰环W",
        "天喰环E1",
        "天喰环E2",
        "天喰环R",
    ),
    "h1032": (
        "通行百万普攻1",
        "通行百万Q3",
        "通行百万Q4",
        "Mirio TogataW",
        "Mirio TogataE",
        "通行百万R",
    ),
    "h1110": (
        "Permeate Uppercut",
        "Dagger Throw",
        "Aura of Fear",
        "Shadowy Surprise",
        "Vigor",
        "Stain",
    ),
}


def _snippet(data: bytes, offset: int, term: str) -> str:
    start = max(0, offset - 96)
    end = min(len(data), offset + len(term.encode("utf-8")) + 160)
    chunk = data[start:end]
    return "".join(chr(value) if 32 <= value < 127 else "." for value in chunk)


def _coerce_paths(path_or_paths: Path | tuple[Path, ...]) -> tuple[Path, ...]:
    if isinstance(path_or_paths, tuple):
        return path_or_paths
    return (path_or_paths,)


def collect_skill_info_hints(
    path_or_paths: Path | tuple[Path, ...],
) -> dict[str, dict[str, object]]:
    blobs = tuple((path, path.read_bytes()) for path in _coerce_paths(path_or_paths))
    hints: dict[str, dict[str, object]] = {}
    for model_id, terms in sorted(SKILL_INFO_TERMS_BY_MODEL.items()):
        model_terms: dict[str, dict[str, object]] = {}
        for term in terms:
            needle = term.lower().encode("utf-8")
            matches: list[tuple[str, int, bytes]] = []
            for path, data in blobs:
                lowered = data.lower()
                matches.extend(
                    (path.as_posix(), match.start(), data)
                    for match in re.finditer(re.escape(needle), lowered)
                )
            model_terms[term] = {
                "count": len(matches),
                "locations": [
                    {"source": source, "offset": offset}
                    for source, offset, _ in matches[:8]
                ],
                "snippets": [
                    _snippet(data, offset, term) for _, offset, data in matches[:2]
                ],
            }
        hints[model_id] = {"terms": model_terms}
    return hints


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover hero skill-info text hints from the English skill_info asset."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=DEFAULT_SKILL_INFO_ASSETS,
        help="Packed skill-info assets. Defaults to the current English skill_info asset.",
    )
    args = parser.parse_args()

    print(
        json.dumps(
            collect_skill_info_hints(tuple(args.paths)),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
