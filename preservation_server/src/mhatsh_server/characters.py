from __future__ import annotations

from dataclasses import dataclass

from .beginner_quest import BEGINNER_QUEST_DEATH_ARMS_UID


CATALOG_SOURCE = (
    "User-supplied AXMD raw-rip list plus en_hero_cfg evidence, 2026-06-15"
)

# hero_cfg VmInfo.TrainCardList is only small level-60 internal test data with
# Fighting=9999. The preservation profile defaults to a capped account, so use
# a stronger live roster baseline until the full combat-power formula is wired.
DEFAULT_CARD_FIGHTING = 50000
DEFAULT_CARD_EXP = 0
DEFAULT_CARD_SATIETY = 694
DEFAULT_CARD_WORKOUT_LEVEL = 10
DEFAULT_CARD_RESONATE_LEVEL = 5


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
    item_id: int
    shape_id: int
    support_type: int = 1
    sort_id: int = 0

    def to_book_entry(self) -> dict[str, int]:
        return {"ItemId": self.item_id, "Type": self.support_type}


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


RECOVERED_HERO_CHARACTERS = {
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
    "h1003": SupportCharacter("All Might", "h1003", 6111045, 1003, 2, 1),
    "h5006": SupportCharacter("Mt. Lady", "h5006", 6121016, 5006, 1, 2),
    "h1017": SupportCharacter("Mina Ashido", "h1017", 6135016, 1017, 1, 3),
    "h5008": SupportCharacter("Kamui Woods", "h5008", 6140016, 5008, 1, 4),
    "h1021": SupportCharacter("Endeavor", "h1021", 6150016, 1021, 2, 5),
    "h5041": SupportCharacter("Gran Torino", "h5041", 6160016, 5041, 1, 6),
    "h5057": SupportCharacter("Himiko Toga", "h5057", 6180016, 5057, 1, 7),
    "h5058": SupportCharacter("Rody", "h5058", 6190016, 5058, 1, 8),
    "h2152": SupportCharacter("Beros", "h2152", 6200016, 2152, 1, 9),
    "h2151": SupportCharacter("Sidero", "h2151", 6210016, 2151, 1, 9),
    "h1018": SupportCharacter("Kyoka Jiro", "h1018", 6220016, 1018, 1, 11),
    "h1927": SupportCharacter("Best Jeanist", "h1927", 6230016, 1927, 2, 12),
}


def support_card_book_entries() -> list[dict[str, int]]:
    return [
        character.to_book_entry()
        for character in sorted(
            SUPPORT_CHARACTERS.values(),
            key=lambda item: (item.sort_id, item.item_id),
        )
    ]


SUPPORT_CARD_ITEM_IDS = frozenset(
    character.item_id for character in SUPPORT_CHARACTERS.values()
)

NON_PUBLIC_PLAYABLE_MODEL_REASONS = {
    "h1004": "small-form All Might variant, not a normal roster card",
    "h1018": "Kyoka Jiro has local protocol/model rows but was not public playable",
    "h1024": "alternate Deku row, not a separate public roster card",
    "h1039": "All For One has asset rows but no verified public playable card",
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
    RECOVERED_HERO_CHARACTERS[model_id] = PlayableCharacter(
        name=name,
        model_asset_id=model_id,
        hero_id=hero_id,
        shape_id=shape_id,
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
PLAYABLE_CHARACTERS = {
    model_id: RECOVERED_HERO_CHARACTERS[model_id]
    for model_id in PUBLIC_PLAYABLE_MODEL_IDS
}
STARTER_CHARACTER = PLAYABLE_CHARACTERS["h1001"]
INITIAL_PLAYABLE_ROSTER = tuple(
    PLAYABLE_CHARACTERS[model_id]
    for model_id in ("h1001", "h1002", "h1006", "h1007", "h1008", "h1009", "h1010")
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
    (5000, "All Might Contact"),
    (5001, "Mei Hatsume (Story)"),
    (5005, "Principal Contact"),
    (5006, "Recovery Girl"),
    (5008, "Kamui Woods"),
    (5009, "Naomasa Tsukauchi"),
    (5011, "Mt. Lady"),
    (5012, "Base Station Contact"),
    (5016, "Uwabami"),
    (5031, "Midnight"),
    (5034, "Training Contact"),
    (5035, "Shota Aizawa"),
    (5037, "All Might"),
    (5038, "All Might"),
    (5043, "Midnight"),
    (5049, "Arson Case Police"),
    (5041, "Mei Hatsume (U.A.)"),
    (6000, "Midnight Contact"),
    (6611, "Arson Case Police"),
    (6612, "Arson Case Police"),
    (6669, "High Ponytail Student"),
    (6675, "Fourth Kind"),
    (6676, "Fourth Kind"),
    (6677, "Fourth Kind Contact"),
    (6678, "Bank President"),
    (6680, "Fourth Kind Contact"),
    (6682, "Young Man"),
    (6683, "Female Engineer"),
    (6706, "Responding Police"),
    (6716, "Store Owner"),
    (6819, "Power Outage Contact"),
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

QUEST_CONTACT_MAP_SPAWNS = (
    MapSpawn(
        label="quest_contact_tsukauchi",
        character=MAP_CHARACTERS[5009],
        uid=20100,
        x=4041,
        y=19741,
        face=0,
    ),
    MapSpawn(
        label="quest_contact_high_ponytail_student",
        character=MAP_CHARACTERS[6669],
        uid=20101,
        x=4141,
        y=19741,
        face=0,
    ),
    MapSpawn(
        label="quest_contact_all_might_primary",
        character=MAP_CHARACTERS[5037],
        uid=20102,
        x=4241,
        y=19741,
        face=180,
    ),
    MapSpawn(
        label="quest_contact_all_might_secondary",
        character=MAP_CHARACTERS[5038],
        uid=20103,
        x=4341,
        y=19741,
        face=180,
    ),
    MapSpawn(
        label="quest_contact_recovery_girl",
        character=MAP_CHARACTERS[5006],
        uid=20104,
        x=4441,
        y=19741,
        face=180,
    ),
    MapSpawn(
        label="quest_contact_midnight_primary",
        character=MAP_CHARACTERS[5031],
        uid=20105,
        x=4541,
        y=19741,
        face=180,
    ),
    MapSpawn(
        label="quest_contact_midnight_secondary",
        character=MAP_CHARACTERS[5043],
        uid=20106,
        x=4641,
        y=19741,
        face=180,
    ),
    MapSpawn(
        label="quest_contact_young_man",
        character=MAP_CHARACTERS[6682],
        uid=20107,
        x=4041,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_bank_president",
        character=MAP_CHARACTERS[6678],
        uid=20108,
        x=4141,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_fourth_kind_primary",
        character=MAP_CHARACTERS[6675],
        uid=20109,
        x=4241,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_fourth_kind_secondary",
        character=MAP_CHARACTERS[6676],
        uid=20110,
        x=4341,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_female_engineer",
        character=MAP_CHARACTERS[6683],
        uid=20111,
        x=4441,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_arson_police_primary",
        character=MAP_CHARACTERS[5049],
        uid=20112,
        x=4541,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_arson_police_secondary",
        character=MAP_CHARACTERS[6611],
        uid=20113,
        x=4641,
        y=19841,
        face=90,
    ),
    MapSpawn(
        label="quest_contact_arson_police_tertiary",
        character=MAP_CHARACTERS[6612],
        uid=20114,
        x=4041,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_store_owner",
        character=MAP_CHARACTERS[6716],
        uid=20115,
        x=4141,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_power_outage_contact",
        character=MAP_CHARACTERS[6819],
        uid=20116,
        x=4241,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_responding_police",
        character=MAP_CHARACTERS[6706],
        uid=20117,
        x=4341,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_all_might_act1130",
        character=MAP_CHARACTERS[5000],
        uid=20118,
        x=4441,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_principal_training",
        character=MAP_CHARACTERS[5005],
        uid=20119,
        x=4541,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_base_station",
        character=MAP_CHARACTERS[5012],
        uid=20120,
        x=4641,
        y=19941,
        face=270,
    ),
    MapSpawn(
        label="quest_contact_uwabami",
        character=MAP_CHARACTERS[5016],
        uid=20121,
        x=4041,
        y=20041,
        face=0,
    ),
    MapSpawn(
        label="quest_contact_training_contact",
        character=MAP_CHARACTERS[5034],
        uid=20122,
        x=4141,
        y=20041,
        face=0,
    ),
    MapSpawn(
        label="quest_contact_midnight_act",
        character=MAP_CHARACTERS[6000],
        uid=20123,
        x=4241,
        y=20041,
        face=0,
    ),
    MapSpawn(
        label="quest_contact_fourth_kind_tertiary",
        character=MAP_CHARACTERS[6677],
        uid=20124,
        x=4341,
        y=20041,
        face=0,
    ),
    MapSpawn(
        label="quest_contact_fourth_kind_dialog",
        character=MAP_CHARACTERS[6680],
        uid=20125,
        x=4441,
        y=20041,
        face=0,
    ),
)

QUEST_CONTACT_MAP_SPAWN_BY_NPC_ID = {
    int(spawn.character.npc_id): spawn
    for spawn in QUEST_CONTACT_MAP_SPAWNS
    if spawn.character.npc_id is not None
}


def quest_contact_map_spawn(npc_id: int) -> MapSpawn | None:
    return QUEST_CONTACT_MAP_SPAWN_BY_NPC_ID.get(int(npc_id))


def map_spawns(mode: str | None = None) -> tuple[MapSpawn, ...]:
    normalized = (mode or "starter").strip().lower()
    if normalized in {"starter", "initial", "default"}:
        return INITIAL_MAP_SPAWNS
    if normalized in {"tutorial", "beginner", "quest"}:
        return TUTORIAL_MAP_SPAWNS
    if normalized in {"demo_cast", "demo-cast", "validation", "lab"}:
        return DEMO_CAST_MAP_SPAWNS
    if normalized in {"quest_contacts", "quest-contacts", "contacts"}:
        return QUEST_CONTACT_MAP_SPAWNS
    if normalized in {"none", "off", "disabled"}:
        return ()
    raise ValueError(
        f"unknown map spawn mode {mode!r}; expected starter, demo_cast, quest_contacts, or none"
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
        "Exp": DEFAULT_CARD_EXP,
        "ShapeId": character.shape_id,
        "FashionId": 0,
        "Fighting": DEFAULT_CARD_FIGHTING,
        "Satiety": DEFAULT_CARD_SATIETY,
        "WorkoutLv": DEFAULT_CARD_WORKOUT_LEVEL,
        "WorkoutItem": [],
        "ResonateLv": DEFAULT_CARD_RESONATE_LEVEL,
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
