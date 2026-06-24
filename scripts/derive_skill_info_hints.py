from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from derive_stage_cfg_route_hints import _RootConstantReader


DEFAULT_SKILL_INFO_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "2ZU"
    / "0a6af507ecd6f4a5"
)
DEFAULT_SKILL_INFO_LOCALIZED_ASSET = (
    Path("analysis")
    / "mediafire_20260620"
    / "apk_extract"
    / "assets"
    / "2ZU"
    / "c2667c89e1b517d5"
)
DEFAULT_SKILL_INFO_ASSETS = (
    DEFAULT_SKILL_INFO_ASSET,
    DEFAULT_SKILL_INFO_LOCALIZED_ASSET,
)

STRUCTURED_SKILL_INFO_MODEL_PREFIXES = {
    "h1027": 1027,
    "h1028": 1028,
    "h1029": 1029,
    "h1030": 1030,
    "h1031": 1031,
    "h1032": 1032,
}

SKILL_INFO_TERMS_BY_MODEL = {
    "h1001": ("Smash", "One For All", "Detroit Smash"),
    "h1002": ("Extra Explosion", "Bakugo"),
    "h1003": ("I Am Here!",),
    "h1006": ("Recipro Extend",),
    "h1007": (
        "Gravel Strike",
        "Meteor Storm",
        "个性无重力",
        "失重冲击",
        "御茶子必杀技",
        "御茶子极限闪避QTE",
    ),
    "h1008": ("Half-Cold Half-Hot", "Charge Ice Spear"),
    "h1009": ("Meteor Storm", "Q - Weapon Creation", "Yaoyorozu"),
    "h1010": ("Lightning Bolt",),
    "h1012": (
        "Dabi普攻1",
        "DabiQ",
        "DabiQ变身",
        "Dabi Assist Skill E",
        "Dabi大招（PVE)",
        "Dabi ability fire",
    ),
    "h1013": (
        "Kirishima Defense counter Q 2 tap",
        "Kirishima Q change 2 tap",
        "Kirishima Q change return",
        "Talent Aeration 4",
        "Kirishima W change Aeration 4",
        "Kirishima W Talent 10 cooldown",
    ),
    "h1014": ("Tongue Swipe",),
    "h1015": (
        "正常普攻1",
        "相泽Q1",
        "相泽W陷阱",
        "相泽E远程",
        "相泽大招",
        "相泽闪避",
        "相泽能力",
    ),
    "h1016": (
        "尾白普攻1",
        "尾白Q",
        "尾巴强化Q",
        "尾白W",
        "尾白强化W",
        "尾白E",
        "尾白强化E",
        "尾白大招",
        "尾白闪避攻击",
        "尾白能力",
    ),
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


def _as_skill_id(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if 100000 <= value <= 199999 else None
    if isinstance(value, float) and value.is_integer():
        numeric_value = int(value)
        return numeric_value if 100000 <= numeric_value <= 199999 else None
    return None


def _command_for_skill_values(values: list[str]) -> str | None:
    normalized = " ".join(values).lower()
    if any(token in normalized for token in ("skill04", "skill4", "ult", "必杀", "大招")):
        return "R"
    if any(token in normalized for token in ("skill03", "skill3")):
        return "E"
    if any(token in normalized for token in ("skill02", "skill2")):
        return "W"
    if any(token in normalized for token in ("skill01", "skill1", "skill0_")):
        return "Q"
    if any(token in normalized for token in ("dash", "roll", "闪避")):
        return "DODGE"
    if any(token in normalized for token in ("ability", "nengli", "被动", "能力")):
        return "PASSIVE"
    if any(token in normalized for token in ("atk", "normal atk", "普攻")):
        return "ATK"
    return None


def _is_human_skill_term(value: str) -> bool:
    term = value.strip()
    lowered = term.lower()
    if not term or len(term) > 48:
        return False
    rejected_fragments = (
        "#",
        "pve_",
        "pvp_",
        "apvp_",
        "skill0",
        "skill1",
        "skill2",
        "skill3",
        "skill4",
        "atk_",
        "atk0",
        "rush_",
        "cd:",
        "changeicon",
        "nolimit",
    )
    if any(fragment in lowered for fragment in rejected_fragments):
        return False
    if lowered in {"q", "w", "e", "r", "stun", "true", "false"}:
        return False
    return any(char.isalpha() for char in term)


def _command_for_skill_term(term: str, fallback: str) -> str:
    normalized = term.lower()
    if "normal atk" in normalized or "普攻" in term:
        return "ATK"
    if "闪避" in term or "dodge" in normalized:
        return "DODGE"
    if "被动" in term or "ability" in normalized:
        return "PASSIVE"
    if "ult" in normalized or "必杀" in term or "大招" in term:
        return "R"
    if re.search(r"(^|[\s_-])q(\d+)?($|[\s_-])", normalized) or re.search(
        r"Q\d?$", term
    ):
        return "Q"
    if re.search(r"(^|[\s_-])w(\d+)?($|[\s_-])", normalized) or re.search(
        r"W\d?$", term
    ):
        return "W"
    if re.search(r"(^|[\s_-])e(\d+)?($|[\s_-])", normalized) or re.search(
        r"E\d?$", term
    ):
        return "E"
    if re.search(r"(^|[\s_-])r(\d+)?($|[\s_-])", normalized) or re.search(
        r"R\d?$", term
    ):
        return "R"
    return fallback


def collect_structured_skill_info_hints(path: Path = DEFAULT_SKILL_INFO_ASSET) -> dict[str, dict[str, object]]:
    constants = _RootConstantReader(path.read_bytes()).root_constants()
    model_by_prefix = {
        prefix: model_id for model_id, prefix in STRUCTURED_SKILL_INFO_MODEL_PREFIXES.items()
    }
    hints: dict[str, dict[str, object]] = {
        model_id: {"command_terms": {}} for model_id in STRUCTURED_SKILL_INFO_MODEL_PREFIXES
    }

    for index, value in enumerate(constants):
        skill_id = _as_skill_id(value)
        if skill_id is None:
            continue
        model_id = model_by_prefix.get(skill_id // 100)
        if model_id is None:
            continue

        values: list[str] = []
        for cursor in range(index + 1, min(len(constants), index + 30)):
            if _as_skill_id(constants[cursor]) is not None:
                break
            if isinstance(constants[cursor], str):
                values.append(constants[cursor])
        command = _command_for_skill_values(values) or "UNKNOWN"

        command_terms = hints[model_id]["command_terms"]
        assert isinstance(command_terms, dict)
        terms = command_terms.setdefault(command, {})
        for term in values:
            if not _is_human_skill_term(term):
                continue
            term_command = _command_for_skill_term(term, command)
            if term_command == "UNKNOWN":
                continue
            terms = command_terms.setdefault(term_command, {})
            if term not in terms:
                terms[term] = {"skill_ids": [], "constant_indexes": []}
            terms[term]["skill_ids"].append(skill_id)
            terms[term]["constant_indexes"].append(index)
    return hints


def _merge_structured_skill_info_hints(
    paths: tuple[Path, ...]
) -> dict[str, dict[str, object]]:
    merged: dict[str, dict[str, object]] = {
        model_id: {"command_terms": {}}
        for model_id in STRUCTURED_SKILL_INFO_MODEL_PREFIXES
    }
    for path in paths:
        structured = collect_structured_skill_info_hints(path)
        for model_id, structured_hints in structured.items():
            command_terms = structured_hints["command_terms"]
            assert isinstance(command_terms, dict)
            merged_command_terms = merged[model_id]["command_terms"]
            assert isinstance(merged_command_terms, dict)
            for command, terms in command_terms.items():
                merged_terms = merged_command_terms.setdefault(command, {})
                assert isinstance(terms, dict)
                assert isinstance(merged_terms, dict)
                for term, term_evidence in terms.items():
                    merged_evidence = merged_terms.setdefault(
                        term, {"skill_ids": [], "constant_indexes": []}
                    )
                    merged_evidence["skill_ids"].extend(term_evidence["skill_ids"])
                    merged_evidence["constant_indexes"].extend(
                        term_evidence["constant_indexes"]
                    )
    return merged


def collect_skill_info_hints(
    path_or_paths: Path | tuple[Path, ...],
) -> dict[str, dict[str, object]]:
    paths = _coerce_paths(path_or_paths)
    blobs = tuple((path, path.read_bytes()) for path in paths)
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
    structured = _merge_structured_skill_info_hints(paths)
    for model_id, structured_hints in structured.items():
        hints.setdefault(model_id, {"terms": {}})["structured_terms"] = structured_hints[
            "command_terms"
        ]
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
