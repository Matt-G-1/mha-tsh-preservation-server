from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path


SCHEMA_HEADER = re.compile(r"^-- === ([^=]+) ===$")
FIELD_LINE = re.compile(
    r"^(?P<indent>\s+)(?P<name>[A-Za-z0-9_]+):\s+"
    r"(?P<type>\{|[A-Za-z0-9_]+)(?P<repeated>\s+\[repeated\])?\s*$"
)
RECOVERED_PROTOCOL_ID_OFFSET = 1


@dataclass(slots=True)
class Field:
    name: str
    type_name: str
    repeated: bool = False
    children: list["Field"] = field(default_factory=list)


@dataclass(slots=True)
class Schema:
    name: str
    fields: list[Field]


class SchemaRegistry:
    def __init__(
        self,
        schemas: dict[str, Schema],
        protocol_ids: dict[str, int],
        protocol_names: dict[int, str],
    ) -> None:
        self.schemas = schemas
        self.protocol_ids = protocol_ids
        self.protocol_names = protocol_names

    @classmethod
    def from_files(cls, schema_path: Path, protocol_csv_path: Path) -> "SchemaRegistry":
        schemas = parse_schemas(schema_path.read_text(encoding="utf-8-sig"))
        protocol_ids: dict[str, int] = {}
        protocol_names: dict[int, str] = {}
        with protocol_csv_path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                protocol_id = int(row["Id"]) - RECOVERED_PROTOCOL_ID_OFFSET
                name = row["Name"]
                protocol_ids[name] = protocol_id
                protocol_names[protocol_id] = name
        # The generated schema lost this response, but rpcLogin.luac retains
        # all six callback parameters and their original order.
        player_info = Schema(
            name="c_login_player_info",
            fields=[
                Field(name="Uid", type_name="number"),
                Field(name="Name", type_name="string"),
                Field(name="Level", type_name="number"),
                Field(name="HostId", type_name="number"),
                Field(name="ServerName", type_name="string"),
                Field(name="CreateTime", type_name="number"),
            ],
        )
        schemas.setdefault(player_info.name, player_info)
        protocol_ids.setdefault(player_info.name, 654)
        protocol_names.setdefault(654, player_info.name)
        return cls(schemas, protocol_ids, protocol_names)

    def schema(self, name: str) -> Schema:
        try:
            return self.schemas[name]
        except KeyError as exc:
            raise KeyError(f"Unknown schema: {name}") from exc


def parse_schemas(text: str) -> dict[str, Schema]:
    schemas: dict[str, Schema] = {}
    current: Schema | None = None
    stack: list[tuple[int, list[Field]]] = []

    for raw_line in text.splitlines():
        header = SCHEMA_HEADER.match(raw_line)
        if header:
            name = header.group(1).strip()
            current = Schema(name=name, fields=[])
            schemas[name] = current
            stack = [(0, current.fields)]
            continue

        if current is None or not raw_line.strip():
            continue
        if raw_line.strip() == "}":
            indent = len(raw_line) - len(raw_line.lstrip())
            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()
            continue

        match = FIELD_LINE.match(raw_line)
        if not match:
            continue

        indent = len(match.group("indent"))
        while len(stack) > 1 and stack[-1][0] >= indent:
            stack.pop()

        type_name = match.group("type")
        item = Field(
            name=match.group("name"),
            type_name="table" if type_name == "{" else type_name,
            repeated=bool(match.group("repeated")),
        )
        stack[-1][1].append(item)
        if type_name == "{":
            stack.append((indent, item.children))

    return schemas
