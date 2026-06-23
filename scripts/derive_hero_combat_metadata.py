from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_HERO_CFG = Path.home() / "Downloads" / "en_hero_cfg_readable.lua"

MODEL_BY_SHAPE_ID = {
    1001: "h1001",
    1002: "h1002",
    1003: "h1003",
    1004: "h1004",
    1006: "h1006",
    1007: "h1007",
    1008: "h1008",
    1009: "h1009",
    1010: "h1010",
    1011: "h1110",
    1012: "h1012",
    1013: "h1013",
    1014: "h1014",
    1015: "h1015",
    1016: "h1016",
    1017: "h1017",
    1018: "h1018",
    1019: "h1019",
    1020: "h1020",
    1021: "h1021",
    1022: "h1022",
    1024: "h1024",
    1026: "h1026",
    1027: "h1027",
    1028: "h1028",
    1029: "h1029",
    1030: "h1030",
    1031: "h1031",
    1032: "h1032",
    9051: "h1998",
}

ROW_RE = re.compile(r"\bL\d+_\d+\[(\d+)\]\s*=\s*\{")
INT_FIELD_RE = re.compile(r"\b{field}\s*=\s*(-?\d+)")
STRING_FIELD_RE = re.compile(r'\b{field}\s*=\s*"([^"]*)"')


def _balanced_block(text: str, open_brace_index: int) -> str:
    depth = 0
    in_string = False
    escape = False
    for index in range(open_brace_index, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_index : index + 1]
    raise ValueError("unclosed table block")


def _int_field(block: str, field: str, default: int = 0) -> int:
    match = re.search(INT_FIELD_RE.pattern.format(field=re.escape(field)), block)
    if match is None:
        return default
    return int(match.group(1))


def _string_field(block: str, field: str) -> str:
    match = re.search(STRING_FIELD_RE.pattern.format(field=re.escape(field)), block)
    if match is None:
        return ""
    return match.group(1)


def _list_field(block: str, field: str) -> tuple[int, ...]:
    match = re.search(rf"\b{re.escape(field)}\s*=\s*\{{", block)
    if match is None:
        return ()
    table = _balanced_block(block, match.end() - 1)
    return tuple(int(value) for value in re.findall(r"-?\d+", table))


def _string_map_field(block: str, field: str) -> tuple[tuple[str, str], ...]:
    match = re.search(rf"\b{re.escape(field)}\s*=\s*\{{", block)
    if match is None:
        return ()
    table = _balanced_block(block, match.end() - 1)
    return tuple(
        (key, value)
        for key, value in re.findall(r'\b([A-Za-z0-9_]+)\s*=\s*"([^"]*)"', table)
    )


def parse_hero_cfg(path: Path) -> dict[str, dict[str, object]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    records: dict[str, dict[str, object]] = {}
    seen_rows: set[tuple[int, int]] = set()

    for match in ROW_RE.finditer(text):
        row = int(match.group(1))
        block = _balanced_block(text, match.end() - 1)
        shape_id = _int_field(block, "ShapeId", -1)
        model_asset_id = MODEL_BY_SHAPE_ID.get(shape_id)
        if model_asset_id is None:
            continue
        if model_asset_id in records:
            continue
        row_key = (row, shape_id)
        if row_key in seen_rows:
            continue
        seen_rows.add(row_key)
        records[model_asset_id] = {
            "config_row": row,
            "shape_id": shape_id,
            "hero_name": _string_field(block, "HeroName"),
            "rname": _string_field(block, "Rname"),
            "ai_name": _string_field(block, "AiName"),
            "action_map": _string_map_field(block, "ActionMap"),
            "skill_group_id": _int_field(block, "SkillGroupId", -1),
            "skill_ids": _list_field(block, "SkillIds"),
            "q_shape_id": _int_field(block, "QShapeId", -1),
            "passive_skill_active": _int_field(block, "PassiveSkillActive"),
            "preload_effects": _list_field(block, "PreLoadEffect"),
        }
    return dict(sorted(records.items()))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recover MHA TSH playable hero combat metadata from hero_cfg."
    )
    parser.add_argument("path", nargs="?", type=Path, default=DEFAULT_HERO_CFG)
    args = parser.parse_args()

    records = parse_hero_cfg(args.path)
    print(json.dumps(records, indent=2, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
