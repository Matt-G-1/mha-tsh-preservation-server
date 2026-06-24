from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_RELAX_STAGE_ASSET = (
    Path("phone_dump")
    / "apk_extract"
    / "assets"
    / "0QIU"
    / "bc4767502c3d543d"
)
FALLBACK_RELAX_STAGE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "0QIU"
    / "bc4767502c3d543d"
)
DEFAULT_DRAMA_INDEX = Path("analysis") / "intro_qte_asset_index.txt"
RELAX_STAGE_SOURCE = (
    "phone_dump/apk_extract/assets/0QIU/bc4767502c3d543d, "
    "./script/setting/language/en/stage/relax_stage_cfg.lua"
)
DIFFICULTY_NAMES = ("Easy", "Elite", "Hard")
GROUP_NAME_RE = re.compile(r"^\d{2} ")


def _as_int(value: object) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _asset_path(path: Path) -> Path:
    if path.exists():
        return path
    if path == DEFAULT_RELAX_STAGE_ASSET and FALLBACK_RELAX_STAGE_ASSET.exists():
        return FALLBACK_RELAX_STAGE_ASSET
    return path


def _previous_index(values: list[object], start: int, needle: str) -> int:
    for index in range(start, -1, -1):
        if values[index] == needle:
            return index
    return -1


def _next_index(values: list[object], start: int, needles: set[str]) -> int:
    for index in range(start, len(values)):
        if values[index] in needles:
            return index
    return len(values)


def _string_after(values: list[object], index: int) -> str:
    for cursor in range(index + 1, min(len(values), index + 4)):
        value = values[cursor]
        if isinstance(value, str):
            return value
    return ""


def _groups(values: list[object]) -> dict[int, dict[str, object]]:
    groups: dict[int, dict[str, object]] = {}
    group_id = 0
    for index, value in enumerate(values):
        if not isinstance(value, str) or not GROUP_NAME_RE.match(value):
            continue
        group_id += 1
        open_level = 1
        for cursor in range(index + 1, min(len(values), index + 8)):
            number = _as_int(values[cursor])
            if number is not None and 1 <= number <= 100:
                open_level = number
                break
        groups[group_id] = {
            "group_name": value,
            "open_level": open_level,
            "constant_index": index,
        }
    return groups


def _stage_segment(values: list[object], stage_index: int, group_start: int) -> list[object]:
    start = group_start
    for cursor in range(stage_index - 1, group_start - 1, -1):
        if _as_int(values[cursor]) is not None and 400301 <= int(values[cursor]) <= 400399:
            start = cursor + 1
            if start < stage_index and values[start] == "Tips":
                start += 2
            break
    return values[start:stage_index]


def _stage_tip(values: list[object], stage_index: int) -> str:
    if stage_index + 2 < len(values) and values[stage_index + 1] == "Tips":
        tip = values[stage_index + 2]
        if isinstance(tip, str):
            return tip
    if stage_index + 1 < len(values):
        tip = values[stage_index + 1]
        if (
            isinstance(tip, str)
            and not GROUP_NAME_RE.match(tip)
            and any(("a" <= char.lower() <= "z") for char in tip)
            and tip
            not in {
                "StageId2Difficulty",
                "StageId2Group",
                "StepsCond",
                "BoxBestRewardV",
                "BoxReward",
                "Difficulty",
                "Fighting1",
                "Fighting2",
                "Fighting3",
                "Fighting4",
                "Fighting5",
                "FlopBestReward",
                "FlopReward",
                "Pic",
                "ShowReward",
            }
        ):
            return tip.replace("\x13", "s")
    return ""


def _stage_rewards(segment: list[object]) -> tuple[int, ...]:
    numbers = [
        int(value)
        for value in (_as_int(item) for item in segment)
        if value is not None
    ]
    return tuple(value for value in numbers if value >= 1_000_000)


def _stage_fighting(segment: list[object]) -> tuple[int, ...]:
    numbers = [
        int(value)
        for value in (_as_int(item) for item in segment)
        if value is not None and value >= 1000
    ]
    if len(numbers) >= 7:
        return tuple(numbers[2:7])
    return ()


def _relax_stage_scripts(path: Path = DEFAULT_DRAMA_INDEX) -> dict[int, tuple[str, ...]]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    scripts: dict[int, list[str]] = {}
    for match in re.finditer(
        r"\./script/setting/dramas/(4003\d{2}(?:_\d+)?)\.lua",
        text,
    ):
        script = match.group(1)
        stage_id = int(script.split("_", 1)[0])
        scripts.setdefault(stage_id, [])
        if script not in scripts[stage_id]:
            scripts[stage_id].append(script)
    def sort_key(script: str) -> tuple[int, str]:
        suffix = script.split("_", 1)[1] if "_" in script else "0"
        try:
            return (int(suffix), script)
        except ValueError:
            return (0, script)

    return {
        stage_id: tuple(sorted(values, key=sort_key))
        for stage_id, values in sorted(scripts.items())
    }


def collect_relax_stage_hints(
    relax_stage_asset: Path = DEFAULT_RELAX_STAGE_ASSET,
    drama_index: Path = DEFAULT_DRAMA_INDEX,
) -> dict[str, object]:
    asset = _asset_path(relax_stage_asset)
    constants = _RootConstantReader(asset.read_bytes()).root_constants()
    stages: list[dict[str, object]] = []
    groups = _groups(constants)
    scripts_by_stage = _relax_stage_scripts(drama_index)
    for index, value in enumerate(constants):
        stage_id = _as_int(value)
        if stage_id is None or not 400301 <= stage_id <= 400399:
            continue
        group_id = ((stage_id - 400301) // 3) + 1
        difficulty_index = ((stage_id - 400301) % 3) + 1
        group = groups.get(group_id, {})
        segment = _stage_segment(
            constants, index, int(group.get("constant_index", 0))
        )
        stages.append(
            {
                "stage_id": stage_id,
                "group_id": group_id,
                "group_name": group.get("group_name", ""),
                "open_level": group.get("open_level", 1),
                "difficulty": difficulty_index,
                "difficulty_name": DIFFICULTY_NAMES[difficulty_index - 1],
                "fighting": list(_stage_fighting(segment)),
                "show_rewards": list(_stage_rewards(segment)),
                "tips": _stage_tip(constants, index),
                "scripts": list(scripts_by_stage.get(stage_id, ())),
                "source": RELAX_STAGE_SOURCE,
            }
        )
    return {
        "source": RELAX_STAGE_SOURCE,
        "constant_count": len(constants),
        "stage_count": len(stages),
        "stages": stages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover Joint Operations / relax stage rows from packed Lua constants."
    )
    parser.add_argument("--asset", type=Path, default=DEFAULT_RELAX_STAGE_ASSET)
    parser.add_argument("--drama-index", type=Path, default=DEFAULT_DRAMA_INDEX)
    args = parser.parse_args()
    print(
        json.dumps(
            collect_relax_stage_hints(args.asset, args.drama_index),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
