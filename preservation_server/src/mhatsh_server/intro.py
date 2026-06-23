"""Recovered starter-intro evidence and IDs.

The values here are intentionally metadata only. The original client media and
script chunks stay outside the repository.
"""

from __future__ import annotations

from dataclasses import dataclass

from .stages import STARTER_INTRO_STAGE_ID


INTRO_EVIDENCE_SOURCE = (
    "local FLV asset 1294fd82be3620d3 plus en_hero_cfg_readable.lua, 2026-06-16"
)


@dataclass(frozen=True, slots=True)
class IntroVideoAsset:
    label: str
    hashed_asset_path: str
    md5: str
    width: int
    height: int
    duration_seconds: int
    fps: int
    logical_name_candidates: tuple[str, ...] = ()
    contains_qte_overlay: bool = False


@dataclass(frozen=True, slots=True)
class IntroCostume:
    label: str
    owner_model_asset_id: str
    hero_cfg_row: int
    npc_id: int
    shape_id: int
    preload_shape_ids: tuple[int, ...]
    scope: str

    @property
    def is_intro_only(self) -> bool:
        return self.scope == "starter_intro"


STARTER_RECAP_VIDEO = IntroVideoAsset(
    label="starter_recap_all_might_sludge_villain",
    hashed_asset_path="4YOU/1294fd82be3620d3",
    md5="85546BD65E1B15BBFDE53A28E4DB39C6",
    width=1600,
    height=720,
    duration_seconds=40,
    fps=30,
    logical_name_candidates=("video/zx/chapter2/lvb01.flv",),
    contains_qte_overlay=False,
)

SCHOOL_MIDORIYA_INTRO_COSTUME = IntroCostume(
    label="school_uniform_midoriya",
    owner_model_asset_id="h1001",
    hero_cfg_row=192,
    npc_id=71104,
    shape_id=2993,
    preload_shape_ids=(2993, 2994),
    scope="starter_intro",
)

STARTER_INTRO_STAGE_CANDIDATES = {
    STARTER_INTRO_STAGE_ID: {
        "label": "zx_battle_intro_candidate",
        "drama_scripts": (
            "zx_battle01",
            "zx_battle02",
            "zx_battle03",
            "zx_battle05",
            "zx_battle06",
            "zx_battle07",
            "zx_lvb_001",
            "zx_lvb_002",
            "zx_lvb_003",
            "zx_lvb_004",
        ),
        "characters": ("All Might", "Sludge", "Midoriya", "Bakugo"),
        "video_assets": (STARTER_RECAP_VIDEO.label,),
    }
}

INTRO_ONLY_COSTUMES = (SCHOOL_MIDORIYA_INTRO_COSTUME,)
