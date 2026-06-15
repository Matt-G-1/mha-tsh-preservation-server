from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass, field
from pathlib import Path


LUA_HEADER = b"\x1bLua"
STRING_TAGS = {4, 0x37}


@dataclass
class Proto:
    index: int
    start: int
    end: int = 0
    line_start: int = 0
    line_end: int = 0
    constant_tag_offsets: list[int] = field(default_factory=list)
    children: list["Proto"] = field(default_factory=list)


class Reader:
    def __init__(self, data: bytes) -> None:
        self.data = data
        self.offset = 12
        self.protos: list[Proto] = []
        self.string_size_offsets: list[int] = []
        self.count_values: list[tuple[int, int]] = []

    def read(self, size: int) -> bytes:
        end = self.offset + size
        if end > len(self.data):
            raise ValueError(
                f"unexpected end at {self.offset}: need {size}, have {len(self.data) - self.offset}"
            )
        value = self.data[self.offset : end]
        self.offset = end
        return value

    def u8(self) -> int:
        return self.read(1)[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.read(4))[0]

    def lua_string(self) -> None:
        size_offset = self.offset
        encoded_size = self.u32()
        size = encoded_size & 0xFFFF
        self.string_size_offsets.append(size_offset)
        if size:
            self.read(size)

    def count(self, minimum_item_size: int = 1) -> int:
        count_offset = self.offset
        encoded_count = self.u32()
        remaining = len(self.data) - self.offset
        count = encoded_count
        if count * minimum_item_size > remaining:
            count = encoded_count & 0xFF
        self.count_values.append((count_offset, count))
        return count

    def count_bytes(self, item_size: int) -> None:
        self.read(self.count(item_size) * item_size)

    def parse_proto(self) -> Proto:
        proto = Proto(index=len(self.protos), start=self.offset)
        self.protos.append(proto)

        self.lua_string()
        proto.line_start = self.u32()
        proto.line_end = self.u32()
        self.read(4)

        self.count_bytes(4)

        for _ in range(self.count()):
            tag_offset = self.offset
            tag = self.u8()
            if tag == 0:
                continue
            if tag == 1:
                self.read(1)
                continue
            if tag == 3:
                self.read(8)
                continue
            if tag in STRING_TAGS:
                proto.constant_tag_offsets.append(tag_offset)
                self.lua_string()
                continue
            raise ValueError(f"unsupported constant tag {tag:#x} at {tag_offset}")

        for _ in range(self.count(12)):
            proto.children.append(self.parse_proto())

        self.count_bytes(4)
        local_count = self.count(12)
        for local_index in range(local_count):
            try:
                self.lua_string()
                self.read(8)
            except ValueError as exc:
                raise ValueError(
                    f"proto {proto.index} local {local_index}/{local_count}: {exc}"
                ) from exc
        upvalue_count = self.count(4)
        for upvalue_index in range(upvalue_count):
            try:
                self.lua_string()
            except ValueError as exc:
                raise ValueError(
                    f"proto {proto.index} upvalue {upvalue_index}/{upvalue_count}: {exc}"
                ) from exc

        proto.end = self.offset
        return proto


def normalize_subtree(
    chunk: bytes,
    proto: Proto,
    string_size_offsets: list[int],
    count_values: list[tuple[int, int]],
) -> bytes:
    output = bytearray(chunk[:12] + chunk[proto.start : proto.end])
    for item in walk(proto):
        for absolute_offset in item.constant_tag_offsets:
            relative_offset = 12 + absolute_offset - proto.start
            if output[relative_offset] == 0x37:
                output[relative_offset] = 4
    for absolute_offset in string_size_offsets:
        if proto.start <= absolute_offset < proto.end:
            relative_offset = 12 + absolute_offset - proto.start
            output[relative_offset + 2 : relative_offset + 4] = b"\x00\x00"
    for absolute_offset, count in count_values:
        if proto.start <= absolute_offset < proto.end:
            relative_offset = 12 + absolute_offset - proto.start
            output[relative_offset : relative_offset + 4] = struct.pack("<I", count)
    return bytes(output)


def walk(proto: Proto):
    yield proto
    for child in proto.children:
        yield from walk(child)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="List or extract normalized protos from MHA TSH Lua 5.1 chunks"
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--proto", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--start", type=int, help="absolute proto start offset")
    parser.add_argument("--end", type=int, help="absolute proto end offset")
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="list or extract fully parsed protos before a later parse error",
    )
    args = parser.parse_args()

    data = args.input.read_bytes()
    header_offset = data.find(LUA_HEADER)
    if header_offset < 0:
        encoded_header_offset = data.find(b"LuaQ")
        if encoded_header_offset < 0:
            parser.error("Lua header not found")
        data = b"\x1b" + data[encoded_header_offset:]
    else:
        data = data[header_offset:]
    if (args.start is None) != (args.end is None):
        parser.error("--start and --end must be used together")
    if args.start is not None and args.end is not None:
        data = data[:12] + data[args.start : args.end]

    reader = Reader(data)
    try:
        reader.parse_proto()
    except ValueError as exc:
        if not args.allow_partial:
            raise
        print(f"warning: partial parse stopped: {exc}")
    if not args.allow_partial and reader.offset != len(data):
        parser.error(f"{len(data) - reader.offset} trailing bytes remain")

    if args.proto is None:
        for proto in reader.protos:
            print(
                f"{proto.index:3} lines={proto.line_start}..{proto.line_end} "
                f"bytes={proto.start}..{proto.end} children={len(proto.children)}"
            )
        return

    if args.output is None:
        parser.error("--output is required with --proto")
    try:
        selected = reader.protos[args.proto]
    except IndexError:
        parser.error(f"proto index {args.proto} is out of range")
    if not selected.end:
        parser.error(f"proto index {args.proto} was not fully parsed")
    args.output.write_bytes(
        normalize_subtree(
            data, selected, reader.string_size_offsets, reader.count_values
        )
    )


if __name__ == "__main__":
    main()
