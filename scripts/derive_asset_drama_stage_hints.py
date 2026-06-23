from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_ASSET_ROOT = Path("analysis") / "mediafire_20260620" / "apk_extract" / "assets"
SCRIPT_PREFIX = b"/script/setting/dramas/"


def _script_name_from_header(path: Path) -> str | None:
    data = path.read_bytes()[:256]
    start = data.find(SCRIPT_PREFIX)
    if start < 0:
        return None
    end = data.find(b"\x00", start)
    raw = data[start + len(SCRIPT_PREFIX) : end if end >= 0 else len(data)]
    name = raw.decode("utf-8", "ignore").strip()
    if not name.endswith(".lua") or "/" in name:
        return None
    return Path(name).stem.strip()


def _numeric_stage_id(script_name: str) -> int | None:
    match = re.match(r"^stage(\d{3,6})(?:[a-z]|_\d+|_[a-z]+)?$", script_name)
    if match:
        return int(match.group(1))
    match = re.match(r"^(\d{6})(?:[_-]\d+|_[a-z]+|[a-z])?$", script_name)
    if match:
        return int(match.group(1))
    return None


def collect_drama_stage_hints(root: Path) -> dict[str, object]:
    scripts: list[dict[str, object]] = []
    groups: dict[int, set[str]] = {}
    for path in sorted(root.glob("*/*")):
        if not path.is_file():
            continue
        script_name = _script_name_from_header(path)
        if script_name is None:
            continue
        stage_id = _numeric_stage_id(script_name)
        scripts.append(
            {
                "script": script_name,
                "asset": path.as_posix(),
                "size": path.stat().st_size,
                "stage_id": stage_id,
            }
        )
        if stage_id is not None:
            groups.setdefault(stage_id, set()).add(script_name)
    return {
        "script_count": len(scripts),
        "numeric_stage_count": len(groups),
        "scripts": scripts,
        "numeric_stage_groups": {
            str(stage_id): sorted(group)
            for stage_id, group in sorted(groups.items())
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover drama-stage script names from packed Lua chunk headers."
    )
    parser.add_argument("root", nargs="?", type=Path, default=DEFAULT_ASSET_ROOT)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_drama_stage_hints(args.root),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
