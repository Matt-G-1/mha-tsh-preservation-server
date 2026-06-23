from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_SKILL_SLOT_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "3BAO"
    / "59263adce53c0911"
)
DEFAULT_SKILL_GUIDE_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "2ZU"
    / "7d73b847f015e314"
)

SKILL_SLOT_TERMS = (
    "SkillData",
    "ASkill",
    "AerateSkill",
    "BaseSkill",
    "CaptainSkill",
    "DashAtk",
    "FinalSkill",
    "FirstSkill",
    "LimitDefenseSkill",
    "PassiveSkill",
    "QteBtnSkill",
    "RollSkill",
    "RushSkill",
    "S0Skill",
    "S1Skill",
    "S2Skill",
    "S3Skill",
    "S4Skill",
    "SecondSkill",
    "ThirdSkill",
)
SKILL_GUIDE_TERMS = (
    "NewHeroSkillGuide",
    "SkillGuideList",
    "SkillGuideCfg",
    "SkillDesc",
    "Normal ATK Combo",
    "SkillLagTime",
    "SkillNameList",
    "BaseSkill",
    "SkillTimeList",
    "Special Skill",
    "CaptainSkill",
    "Smash Combo",
    "FirstSkill",
    "SecondSkill",
    "ThirdSkill",
)


def _count_terms(path: Path, terms: tuple[str, ...]) -> dict[str, dict[str, object]]:
    data = path.read_bytes()
    lowered = data.lower()
    results: dict[str, dict[str, object]] = {}
    for term in terms:
        needle = term.lower().encode("utf-8")
        offsets = [match.start() for match in re.finditer(re.escape(needle), lowered)]
        results[term] = {
            "count": len(offsets),
            "locations": [
                {"source": path.as_posix(), "offset": offset}
                for offset in offsets[:8]
            ],
        }
    return results


def collect_skill_slot_hints(
    slot_asset: Path = DEFAULT_SKILL_SLOT_ASSET,
    guide_asset: Path = DEFAULT_SKILL_GUIDE_ASSET,
) -> dict[str, object]:
    return {
        "slot_asset": slot_asset.as_posix(),
        "guide_asset": guide_asset.as_posix(),
        "slot_terms": _count_terms(slot_asset, SKILL_SLOT_TERMS),
        "guide_terms": _count_terms(guide_asset, SKILL_GUIDE_TERMS),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover combat skill-slot and skill-guide label hints."
    )
    parser.add_argument("--slot-asset", type=Path, default=DEFAULT_SKILL_SLOT_ASSET)
    parser.add_argument("--guide-asset", type=Path, default=DEFAULT_SKILL_GUIDE_ASSET)
    args = parser.parse_args()

    print(
        json.dumps(
            collect_skill_slot_hints(args.slot_asset, args.guide_asset),
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
