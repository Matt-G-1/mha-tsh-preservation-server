from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from pprint import pformat


DEFAULT_DRAMA_INDEX = Path("analysis") / "intro_qte_asset_index.txt"
DRAMA_FAMILY_SOURCE = (
    "analysis/intro_qte_asset_index.txt, grouped nonnumeric drama families, "
    "parsed 2026-06-24"
)
SCRIPT_RE = re.compile(r"\./script/setting/dramas/([^\s'\"\]]+)\.lua")

FAMILY_PREFIXES: dict[str, tuple[str, ...]] = {
    "activity_misc_drama_scripts": ("act", "activity_"),
    "basic_drama_misc_scripts": ("drama",),
    "beach_qte_drama_scripts": ("beachqte",),
    "bus_route_drama_scripts": ("bus",),
    "campaign_open_drama_scripts": ("campaign_open",),
    "card_guide_drama_scripts": ("cardguide",),
    "chase_drama_scripts": ("chase",),
    "city_patrol_drama_scripts": ("cp_",),
    "class_training_misc_scripts": ("tch_", "tp_"),
    "combat_branch_misc_scripts": ("bd_", "kn", "smash"),
    "companion_event_misc_scripts": ("egg_", "zy", "xz"),
    "death_usj_misc_scripts": ("death",),
    "event_branch_drama_scripts": ("event",),
    "field_activity_drama_scripts": ("huodong_",),
    "hero_side_branch_misc_scripts": ("hks_", "os_", "sty_", "adw_", "sbm_"),
    "joint_training_drama_scripts": ("jz_", "jzjt_"),
    "loose_asset_tail_drama_scripts": (
        "3011",
        "1044",
        "143",
        "210",
        "2110",
        "236",
        "255",
        "25501",
        "350010_",
        "3606_btoc",
        "404103",
        "405ceshi",
        "404205",
        "404405",
        "561203",
        "561223_g",
        "561225_mao",
        "562504_4",
        "70110201try",
    ),
    "loose_misc_drama_scripts": (
        "00",
        "123",
        "A",
        "aa",
        "ac",
        "acc",
        "aera",
        "area-",
        "area0_",
        "area`_",
        "aaaaaaq",
        "battlefield",
        "bos",
        "bsd_",
        "bug",
        "cha",
        "cs_",
        "dea",
        "dengchang",
        "facetest",
        "hostage",
        "hudong",
        "inherit",
        "ip_",
        "jianshi",
        "judahua",
        "kaohe",
        "kaoshiguize",
        "lvguw",
        "paizhao",
        "paoji",
        "pv_",
        "qingduzudui",
        "qteguide",
        "release",
        "rexuepvpguide",
        "shangyejie",
        "slg_",
        "slgcar",
        "stage_demo",
        "test_",
        "tuanben",
        "wj_",
        "word_",
        "yaliboss",
        "yhc",
        "z\\x08",
        "zhanyi",
    ),
    "night_branch_drama_scripts": ("night",),
    "scenario_journey_drama_scripts": ("sj_",),
    "secret_branch_drama_scripts": ("secret",),
    "shiliguan_drama_scripts": ("shiliguan",),
    "slg_talking_drama_scripts": ("slgtalking", "slgGalking"),
    "stage_guide_drama_scripts": ("stageguide",),
    "tc_extra_drama_scripts": ("tc_",),
    "tx_branch_drama_scripts": ("tx1_", "txbw_"),
    "pvp_guide_drama_scripts": ("pvpguide", "pvp_guide"),
    "training_yard_extra_drama_scripts": ("tyj_",),
    "usj_extra_drama_scripts": ("usj_",),
    "xht_extra_drama_scripts": ("xht_",),
    "zx_lowercase_extra_scripts": ("zx0_", "zx3_", "zx_2_"),
    "zx_uppercase_branch_scripts": ("ZX-",),
}

FAMILY_LABELS: dict[str, str] = {
    "activity_misc_drama_scripts": "activity and event drama scripts without recovered stage ids",
    "basic_drama_misc_scripts": "basic drama config and branch scripts",
    "beach_qte_drama_scripts": "beach event QTE drama scripts",
    "bus_route_drama_scripts": "bus route drama scripts",
    "campaign_open_drama_scripts": "campaign opening drama scripts",
    "card_guide_drama_scripts": "card tutorial guide drama scripts",
    "chase_drama_scripts": "chase and vehicle QTE drama scripts",
    "city_patrol_drama_scripts": "city patrol branch drama scripts",
    "class_training_misc_scripts": "class training miscellaneous drama scripts",
    "combat_branch_misc_scripts": "combat branch miscellaneous drama scripts",
    "companion_event_misc_scripts": "companion event miscellaneous drama scripts",
    "death_usj_misc_scripts": "Death Arms and USJ miscellaneous drama scripts",
    "event_branch_drama_scripts": "event branch drama scripts",
    "field_activity_drama_scripts": "field activity drama scripts",
    "hero_side_branch_misc_scripts": "hero side branch miscellaneous drama scripts",
    "joint_training_drama_scripts": "joint training branch drama scripts",
    "loose_asset_tail_drama_scripts": "loose asset/numeric tail drama scripts",
    "loose_misc_drama_scripts": "miscellaneous loose drama scripts",
    "night_branch_drama_scripts": "night branch drama scripts",
    "scenario_journey_drama_scripts": "scenario journey drama scripts",
    "secret_branch_drama_scripts": "secret branch drama scripts",
    "shiliguan_drama_scripts": "shiliguan challenge drama scripts",
    "slg_talking_drama_scripts": "strategy talking drama scripts",
    "stage_guide_drama_scripts": "stage tutorial guide drama scripts",
    "tc_extra_drama_scripts": "TC prefixed extra drama scripts",
    "tx_branch_drama_scripts": "TX branch and training drama scripts",
    "pvp_guide_drama_scripts": "PVP tutorial guide drama scripts",
    "training_yard_extra_drama_scripts": "training-yard extra drama scripts",
    "usj_extra_drama_scripts": "USJ extra drama scripts",
    "xht_extra_drama_scripts": "XHT extra drama scripts",
    "zx_lowercase_extra_scripts": "lowercase ZX extra branch drama scripts",
    "zx_uppercase_branch_scripts": "uppercase ZX branch drama scripts",
}


def _natural_key(value: str) -> tuple[object, ...]:
    return tuple(
        int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value)
    )


def _family_key(script: str) -> str | None:
    for key, prefixes in FAMILY_PREFIXES.items():
        if any(script.startswith(prefix) for prefix in prefixes):
            return key
    return None


def collect_drama_family_stage_hints(
    drama_index: Path = DEFAULT_DRAMA_INDEX,
) -> dict[str, object]:
    text = drama_index.read_text(encoding="utf-8", errors="ignore")
    groups: dict[str, list[str]] = {key: [] for key in FAMILY_PREFIXES}
    for match in SCRIPT_RE.finditer(text):
        script = match.group(1)
        family_key = _family_key(script)
        if family_key is None:
            continue
        scripts = groups[family_key]
        if script not in scripts:
            scripts.append(script)

    families = [
        {
            "key": key,
            "label": FAMILY_LABELS[key],
            "scripts": tuple(sorted(scripts, key=_natural_key)),
        }
        for key, scripts in sorted(groups.items())
        if scripts
    ]
    return {
        "source": DRAMA_FAMILY_SOURCE,
        "family_count": len(families),
        "script_count": sum(len(item["scripts"]) for item in families),
        "families": families,
    }


def _emit_python_module(payload: dict[str, object]) -> str:
    rows = [
        {
            "key": item["key"],
            "label": item["label"],
            "scripts": item["scripts"],
        }
        for item in payload["families"]
        if isinstance(item, dict)
    ]
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n\n\n"
        "DRAMA_FAMILY_STAGE_SOURCE = "
        + repr(str(payload["source"]))
        + "\n\n\n"
        "@dataclass(frozen=True, slots=True)\n"
        "class DramaFamilyStageDefinition:\n"
        "    key: str\n"
        "    label: str\n"
        "    scripts: tuple[str, ...]\n\n\n"
        "DRAMA_FAMILY_STAGES = tuple(\n"
        "    DramaFamilyStageDefinition(**item)\n"
        "    for item in "
        + pformat(rows, width=88, sort_dicts=False)
        + "\n"
        ")\n\n"
        "DRAMA_FAMILY_STAGE_BY_KEY = {stage.key: stage for stage in DRAMA_FAMILY_STAGES}\n"
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Group nonnumeric drama script families from the extracted drama index."
    )
    parser.add_argument("--drama-index", type=Path, default=DEFAULT_DRAMA_INDEX)
    parser.add_argument("--python-module", action="store_true")
    args = parser.parse_args()
    payload = collect_drama_family_stage_hints(args.drama_index)
    if args.python_module:
        print(_emit_python_module(payload))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
