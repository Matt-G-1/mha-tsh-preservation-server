from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_STAGE_CFG_ASSETS = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "1FO"
    / "534765b72e39ddc4",
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "4YOU"
    / "16eeb8bc82c44019",
)

ASCII_TOKEN_RE = re.compile(rb"[A-Za-z0-9_./+-]{4,}")
STAGE_SCRIPT_RE = re.compile(r"^stage\d+[a-z0-9_]*$")
ZX_SCRIPT_RE = re.compile(r"^zx_[a-z0-9_]+$")
STAGE_VIDEO_RE = re.compile(r"^video/zx/[A-Za-z0-9_./+-]+\.flv$")
EVENT_TOKEN_RE = re.compile(
    r"(?:Monster|Drama|Finish|Event|Drop|Death|Win|Lose|Hostage|StagePass|Trigger)"
)


def collect_stage_cfg_string_hints(paths: tuple[Path, ...]) -> dict[str, object]:
    tokens: set[str] = set()
    sources: list[str] = []
    for path in paths:
        sources.append(path.as_posix())
        tokens.update(
            match.group(0).decode("ascii", "ignore")
            for match in ASCII_TOKEN_RE.finditer(path.read_bytes())
        )

    stage_scripts = sorted(token for token in tokens if STAGE_SCRIPT_RE.match(token))
    zx_scripts = sorted(token for token in tokens if ZX_SCRIPT_RE.match(token))
    video_assets = sorted(token for token in tokens if STAGE_VIDEO_RE.match(token))
    event_hooks = sorted(token for token in tokens if EVENT_TOKEN_RE.search(token))

    return {
        "sources": sources,
        "stage_script_count": len(stage_scripts),
        "zx_script_count": len(zx_scripts),
        "video_asset_count": len(video_assets),
        "event_hook_count": len(event_hooks),
        "stage_scripts": stage_scripts,
        "zx_scripts": zx_scripts,
        "video_assets": video_assets,
        "event_hooks": event_hooks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover stage_cfg string hints from packed MHA TSH assets."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=DEFAULT_STAGE_CFG_ASSETS,
        help="Packed stage_cfg asset paths. Defaults to the current extracted assets.",
    )
    args = parser.parse_args()

    print(
        json.dumps(
            collect_stage_cfg_string_hints(tuple(args.paths)),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
