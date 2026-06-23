from __future__ import annotations

from dataclasses import dataclass

from .beginner_quest import BEGINNER_QUEST_DEATH_ARMS_UID


CATALOG_SOURCE = (
    "User-supplied AXMD raw-rip list plus en_hero_cfg evidence, 2026-06-15"
)


@dataclass(frozen=True, slots=True)
class PlayableCharacter:
    name: str
    model_asset_id: str
    hero_id: int | None = None
    shape_id: int | None = None

    @property
    def is_protocol_verified(self) -> bool:
        return self.hero_id is not None and self.shape_id is not None


@dataclass(frozen=True, slots=True)
class SupportCharacter:
    name: str
    model_asset_id: str


@dataclass(frozen=True, slots=True)
class MapCharacter:
    name: str
    model_asset_id: int
    npc_id: int | None = None

    @property
    def is_spawn_verified(self) -> bool:
        return self.npc_id is not None


@dataclass(frozen=True, slots=True)
class MapSpawn:
    label: str
    character: MapCharacter
    uid: int
    x: int
    y: int
    z: int = 0
    face: int = 0
    area_id: int = 0
    is_authored_placement: bool = False


PLAYABLE_CHARACTERS = {
    model_id: PlayableCharacter(name, model_id)
    for model_id, name in {
        "h1001": "Deku",
        "h1002": "Bakugo",
        "h1003": "All Might",
        "h1004": "Small Might?",
        "h1006": "Iida",
        "h1007": "Ochaco",
        "h1008": "Todoroki",
        "h1009": "Momo",
        "h1010": "Denki",
        "h1012": "Dabi",
        "h1013": "Kirishima",
        "h1014": "Asui",
        "h1015": "Aizawa",
        "h1016": "Ojiro",
        "h1017": "Mina?",
        "h1018": "Jiro",
        "h1019": "Shigaraki",
        "h1020": "Mineta",
        "h1021": "Endeavor",
        "h1022": "Tokoyami",
        "h1024": "Deku 2?",
        "h1026": "Hawks",
        "h1027": "Deku WHM",
        "h1028": "Bakugo WHM",
        "h1029": "Todoroki WHM",
        "h1030": "Nejire",
        "h1031": "Tamaki",
        "h1032": "Todoroki WHM 2",
        "h1039": "All For One",
        "h1110": "Stain",
        "h1998": "Momo?",
    }.items()
}

SUPPORT_CHARACTERS = {
    "h1927": SupportCharacter("Best Jeanist", "h1927"),
}

NON_PUBLIC_PLAYABLE_MODEL_REASONS = {
    "h1004": "small-form All Might variant, not a normal roster card",
    "h1018": "Kyoka Jiro has local protocol/model rows but was not public playable",
    "h1024": "alternate Deku row, not a separate public roster card",
    "h1998": "All Might art-test variant, not a normal roster card",
}

# hero_cfg verifies the hero rows and ShapeId values; shape_info independently
# maps each ShapeId to the listed AXMD model path.
for model_id, name, hero_id, shape_id in (
    ("h1001", "Izuku Midoriya", 1011, 1001),
    ("h1002", "Katsuki Bakugo", 1021, 1002),
    ("h1003", "All Might", 1041, 1003),
    ("h1004", "All Might (Small Form)", 1031, 1004),
    ("h1006", "Tenya Iida", 1061, 1006),
    ("h1007", "Ochaco Uraraka", 1071, 1007),
    ("h1008", "Shoto Todoroki", 1081, 1008),
    ("h1009", "Momo Yaoyorozu", 1091, 1009),
    ("h1010", "Denki Kaminari", 1101, 1010),
    ("h1012", "Dabi", 1121, 1012),
    ("h1013", "Eijiro Kirishima", 1131, 1013),
    ("h1014", "Tsuyu Asui", 1141, 1014),
    ("h1015", "Shota Aizawa", 1151, 1015),
    ("h1016", "Mashirao Ojiro", 1161, 1016),
    ("h1017", "Mina Ashido", 1171, 1017),
    ("h1018", "Kyoka Jiro", 1181, 1018),
    ("h1019", "Tomura Shigaraki", 1191, 1019),
    ("h1020", "Minoru Mineta", 1201, 1020),
    ("h1021", "Endeavor", 1211, 1021),
    ("h1022", "Fumikage Tokoyami", 1221, 1022),
    ("h1024", "Izuku Midoriya (Alternate)", 1241, 1024),
    ("h1026", "Hawks", 1261, 1026),
    ("h1027", "WHM Izuku Midoriya", 1271, 1027),
    ("h1028", "WHM Katsuki Bakugo", 1281, 1028),
    ("h1029", "WHM Shoto Todoroki", 1291, 1029),
    ("h1030", "Nejire Hado", 1301, 1030),
    ("h1031", "Tamaki Amajiki", 1311, 1031),
    ("h1032", "Mirio Togata", 1321, 1032),
    ("h1110", "Stain", 1111, 1011),
    ("h1998", "All Might (Art Test Variant)", 1981, 9051),
):
    PLAYABLE_CHARACTERS[model_id] = PlayableCharacter(
        name=name,
        model_asset_id=model_id,
        hero_id=hero_id,
        shape_id=shape_id,
    )

STARTER_CHARACTER = PLAYABLE_CHARACTERS["h1001"]
INITIAL_PLAYABLE_ROSTER = tuple(
    PLAYABLE_CHARACTERS[model_id]
    for model_id in ("h1001", "h1002", "h1006", "h1007", "h1008", "h1009", "h1010")
)
PUBLIC_PLAYABLE_MODEL_IDS = (
    "h1001",
    "h1002",
    "h1003",
    "h1006",
    "h1007",
    "h1008",
    "h1009",
    "h1010",
    "h1012",
    "h1013",
    "h1014",
    "h1015",
    "h1016",
    "h1017",
    "h1019",
    "h1020",
    "h1021",
    "h1022",
    "h1026",
    "h1027",
    "h1028",
    "h1029",
    "h1030",
    "h1031",
    "h1032",
    "h1110",
)
VERIFIED_PLAYABLE_ROSTER = tuple(
    PLAYABLE_CHARACTERS[model_id]
    for model_id in PUBLIC_PLAYABLE_MODEL_IDS
    if PLAYABLE_CHARACTERS[model_id].is_protocol_verified
)


def playable_roster(mode: str | None = None) -> tuple[PlayableCharacter, ...]:
    normalized = (mode or "starter").strip().lower()
    if normalized in {"starter", "initial", "default"}:
        return INITIAL_PLAYABLE_ROSTER
    if normalized in {"verified", "expanded", "all"}:
        return VERIFIED_PLAYABLE_ROSTER
    raise ValueError(
        f"unknown playable roster mode {mode!r}; expected starter or verified"
    )


MAP_CHARACTERS = {
    model_id: MapCharacter(name, model_id)
    for model_id, name in {
        2005: "Train Enemy",
        2202: "Enemy",
        2470: "Nomu 2",
        2471: "Nomu 3",
        2472: "Twice?",
        3002: "Sludge Monster",
        3003: "Octopus Boss",
        3005: "Giant Mech Boss",
        3006: "USJ Water Boss",
        3007: "Nomu",
        3016: "Muscular",
        3125: "Kurogiri",
        4006: "Small Might",
        4346: "Random Female",
        4355: "Unknown NPC",
        5001: "Mei Hatsume",
        5006: "Mt. Lady",
        5007: "Death Arms",
        5008: "Kamui Woods",
        5009: "Naomasa Tsukauchi",
        5010: "Muscular",
        5011: "Midnight",
        5012: "Tokoyami or Vlad King",
        5013: "Power Loader",
        5014: "Cementos",
        5015: "Snipe",
        5016: "Uwabami",
        5017: "Mina",
        5019: "Koda",
        5020: "Mixed NPC group including All For One",
        5022: "Backdraft",
        5023: "Police Cat",
        5025: "Gran Torino",
        5026: "Female Reporter",
        5035: "Ectoplasm",
        5041: "Gran Torino 2",
        5054: "Fourth Kind",
        5057: "Possibly Toga",
        5058: "Rody",
        5815: "All Might",
    }.items()
}

# The archived npc_cfg chunk independently verifies row 5007, ShapeId 5007,
# display name "Death Arms", and the map-system minimap icon.
MAP_CHARACTERS[5007] = MapCharacter(
    name="Death Arms",
    model_asset_id=5007,
    npc_id=5007,
)

# npc_cfg constants verify these row IDs and names near the recovered table's
# map-system NPC block. These are packet-validation rows, not starter-area
# placement data.
for model_id, name in (
    (5001, "Mei Hatsume (Story)"),
    (5008, "Kamui Woods"),
    (5009, "Naomasa Tsukauchi"),
    (5011, "Mt. Lady"),
    (5035, "Shota Aizawa"),
    (5041, "Mei Hatsume (U.A.)"),
):
    MAP_CHARACTERS[model_id] = MapCharacter(
        name=name,
        model_asset_id=model_id,
        npc_id=model_id,
    )

DEATH_ARMS = MAP_CHARACTERS[5007]
BEGINNER_QUEST_DEATH_ARMS_SPAWN = MapSpawn(
    label="beginner_quest_death_arms_honei_objective",
    character=DEATH_ARMS,
    uid=BEGINNER_QUEST_DEATH_ARMS_UID,
    x=6421,
    y=21931,
    z=0,
    face=180,
)
DEATH_ARMS_DEMO_SPAWN = BEGINNER_QUEST_DEATH_ARMS_SPAWN
INITIAL_MAP_SPAWNS: tuple[MapSpawn, ...] = ()
TUTORIAL_MAP_SPAWNS = (BEGINNER_QUEST_DEATH_ARMS_SPAWN,)
DEMO_CAST_MAP_SPAWNS = (
    DEATH_ARMS_DEMO_SPAWN,
    MapSpawn(
        label="validation_only_mei_story_near_honei_spawn",
        character=MAP_CHARACTERS[5001],
        uid=20002,
        x=4321,
        y=19881,
        face=90,
    ),
    MapSpawn(
        label="validation_only_kamui_woods_near_honei_spawn",
        character=MAP_CHARACTERS[5008],
        uid=20003,
        x=4521,
        y=19881,
        face=270,
    ),
    MapSpawn(
        label="validation_only_tsukauchi_near_honei_spawn",
        character=MAP_CHARACTERS[5009],
        uid=20004,
        x=4221,
        y=19831,
        face=0,
    ),
    MapSpawn(
        label="validation_only_mt_lady_near_honei_spawn",
        character=MAP_CHARACTERS[5011],
        uid=20005,
        x=4621,
        y=19931,
        face=180,
    ),
    MapSpawn(
        label="validation_only_aizawa_near_honei_spawn",
        character=MAP_CHARACTERS[5035],
        uid=20006,
        x=4121,
        y=19931,
        face=0,
    ),
    MapSpawn(
        label="validation_only_mei_ua_near_honei_spawn",
        character=MAP_CHARACTERS[5041],
        uid=20007,
        x=4421,
        y=19831,
        face=180,
    ),
)


def map_spawns(mode: str | None = None) -> tuple[MapSpawn, ...]:
    normalized = (mode or "starter").strip().lower()
    if normalized in {"starter", "initial", "default"}:
        return INITIAL_MAP_SPAWNS
    if normalized in {"tutorial", "beginner", "quest"}:
        return TUTORIAL_MAP_SPAWNS
    if normalized in {"demo_cast", "demo-cast", "validation", "lab"}:
        return DEMO_CAST_MAP_SPAWNS
    if normalized in {"none", "off", "disabled"}:
        return ()
    raise ValueError(
        f"unknown map spawn mode {mode!r}; expected starter, demo_cast, or none"
    )


CHIBI_MODEL_ASSETS = {
    1000105: "Todoroki",
    1000110: "Denki",
    1000115: "Aizawa",
}


def playable_card(
    character: PlayableCharacter,
    card_uid: int,
    *,
    level: int = 1,
) -> dict[str, object]:
    if not character.is_protocol_verified:
        raise ValueError(
            f"{character.model_asset_id} has an AXMD model but no verified protocol mapping"
        )
    return {
        "Uid": card_uid,
        "HeroId": character.hero_id,
        "Lv": max(1, int(level)),
        "Exp": 0,
        "ShapeId": character.shape_id,
        "FashionId": 0,
        "Fighting": 0,
        "Satiety": 0,
        "WorkoutLv": 0,
        "WorkoutItem": [],
        "ResonateLv": 0,
        "ResonatePiece": [],
        "IsLock": 0,
        "IsLockSkill": [],
        "SupportSkills": [],
        "FameLv": 0,
        "FameExp": 0,
    }


def scene_npc(
    character: MapCharacter,
    *,
    uid: int,
    x: int,
    y: int,
    z: int = 0,
    face: int = 0,
    area_id: int = 0,
) -> dict[str, object]:
    if not character.is_spawn_verified:
        raise ValueError(
            f"{character.model_asset_id} has a verified model but no verified NPC row"
        )
    return {
        "Uid": uid,
        "Id": character.npc_id,
        "X": x,
        "Y": y,
        "Z": z,
        "Face": face,
        "Version": 1,
        "ShapeId": character.model_asset_id,
        "Attach": [],
        "HideStatus": 0,
        "AreaId": area_id,
        "StartAnim": "",
        "BTName": "",
        "ForceShow": 0,
    }


def scene_npc_from_spawn(spawn: MapSpawn) -> dict[str, object]:
    return scene_npc(
        spawn.character,
        uid=spawn.uid,
        x=spawn.x,
        y=spawn.y,
        z=spawn.z,
        face=spawn.face,
        area_id=spawn.area_id,
    )
