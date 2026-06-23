from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


DEFAULT_SKILL_LVUP_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "3BAO"
    / "e926ca71d98a942f"
)

MODELS_BY_VIDEO_PREFIX = {
    "andewa": ("h1021",),
    "babaiwan": ("h1009",),
    "baohao": ("h1002",),
    "baohaowhm": ("h1028",),
    "bodong": ("h1030",),
    "changan": ("h1022",),
    "fantian": ("h1006",),
    "hong": ("h1008",),
    "hongwhm": ("h1029",),
    "huokesi": ("h1026",),
    "lvgu": ("h1001",),
    "lvguwhm": ("h1027",),
    "ouermaite": ("h1003", "h1004"),
    "sannai": ("h1017",),
    "shangming": ("h1010",),
    "sibingmu": ("h1019",),
    "sitanyin": ("h1110",),
    "tiancanhuan": ("h1031",),
    "tongxingbaiwan": ("h1032",),
    "tupi": ("h1012",),
    "wachui": ("h1014",),
    "weibai": ("h1016",),
    "xiangze": ("h1015",),
    "xlvgu": ("h1024",),
    "xqiedao": ("h1013",),
    "yuchazi": ("h1007",),
}

VIDEO_RE = re.compile(rb"video/skill/[A-Za-z0-9_./-]+\.flv")


def _category(prefix: str, path: str) -> str:
    stem = Path(path).name.removesuffix(".flv")
    suffix = stem[len(prefix) + 1 :]
    return suffix.split("_", 1)[0].upper()


def collect_skill_video_hints(path: Path) -> dict[str, dict[str, object]]:
    paths = sorted(
        {
            match.group(0).decode("ascii", "ignore")
            for match in VIDEO_RE.finditer(path.read_bytes())
        }
    )
    by_prefix: dict[str, list[str]] = defaultdict(list)
    for video_path in paths:
        prefix = Path(video_path).name.split("_", 1)[0]
        by_prefix[prefix].append(video_path)

    by_model: dict[str, dict[str, object]] = {}
    for prefix, model_ids in sorted(MODELS_BY_VIDEO_PREFIX.items()):
        videos = tuple(by_prefix.get(prefix, ()))
        categories = tuple(sorted({_category(prefix, video) for video in videos}))
        for model_id in model_ids:
            by_model[model_id] = {
                "prefix": prefix,
                "count": len(videos),
                "categories": categories,
                "videos": videos,
            }
    return dict(sorted(by_model.items()))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover MHA TSH skill-video hints from skill_lvup_cfg."
    )
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_SKILL_LVUP_ASSET)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_skill_video_hints(args.path),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
