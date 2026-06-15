from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any

from .schema import Field, SchemaRegistry


class ProtocolError(ValueError):
    pass


def checksum_base(data: bytes) -> int:
    total = 0
    even_length = len(data) & ~1
    for offset in range(0, even_length, 2):
        total += int.from_bytes(data[offset : offset + 2], "little")
    if len(data) & 1:
        total += data[-1] << 8
    if total == 0:
        return 0
    low_added = 0x6B6B + (total & 0xFFFF)
    return (((total >> 16) ^ low_added) + (low_added >> 16)) & 0xFFFF


@dataclass(slots=True)
class RollingXor:
    key: int
    frozen: bool = False

    def transform(self, data: bytes) -> bytes:
        output = bytearray(len(data))
        key = self.key & 0xFFFFFFFF
        for index, source in enumerate(data):
            plain = source ^ (key & 0xFF)
            output[index] = plain
            if not self.frozen:
                key = (key + (plain & 3)) & 0xFFFFFFFF
        self.key = key
        return bytes(output)

    def encrypt(self, data: bytes) -> bytes:
        output = bytearray(len(data))
        key = self.key & 0xFFFFFFFF
        for index, plain in enumerate(data):
            output[index] = plain ^ (key & 0xFF)
            if not self.frozen:
                key = (key + (plain & 3)) & 0xFFFFFFFF
        self.key = key
        return bytes(output)


def encode_number(value: Any) -> bytes:
    integer = int(value)
    negative = integer < 0
    magnitude = abs(integer)
    if magnitude >= (1 << 48):
        raise ProtocolError("Axon number exceeds the 48-bit wire limit")
    length = max(1, (magnitude.bit_length() + 7) // 8)
    tag = (length << 1) | int(negative)
    return bytes((tag,)) + magnitude.to_bytes(length, "little")


def decode_number(data: memoryview, offset: int) -> tuple[int, int]:
    _require(data, offset, 1)
    tag = data[offset]
    offset += 1
    length = tag >> 1
    if not 1 <= length <= 6:
        raise ProtocolError(f"Invalid Axon number length: {length}")
    _require(data, offset, length)
    magnitude = int.from_bytes(data[offset : offset + length], "little")
    value = -magnitude if tag & 1 else magnitude
    return value, offset + length


def encode_string(value: Any) -> bytes:
    raw = value if isinstance(value, bytes) else str(value).encode("utf-8")
    wire_length = len(raw) + 1
    if wire_length > 0xFFFF:
        raise ProtocolError("Axon string exceeds the 65534-byte wire limit")
    if wire_length <= 0xFF:
        prefix = bytes((wire_length,))
    else:
        prefix = b"\x00" + wire_length.to_bytes(2, "little")
    return prefix + raw


def decode_string(data: memoryview, offset: int) -> tuple[str, int]:
    _require(data, offset, 1)
    wire_length = data[offset]
    offset += 1
    if wire_length == 0:
        _require(data, offset, 2)
        wire_length = int.from_bytes(data[offset : offset + 2], "little")
        offset += 2
    if wire_length < 1:
        raise ProtocolError("Invalid Axon string length")
    raw_length = wire_length - 1
    _require(data, offset, raw_length)
    raw = bytes(data[offset : offset + raw_length])
    return raw.decode("utf-8", errors="replace"), offset + raw_length


class ProtocolCodec:
    def __init__(self, registry: SchemaRegistry) -> None:
        self.registry = registry

    def encode_message(self, name: str, values: dict[str, Any]) -> bytes:
        schema = self.registry.schema(name)
        output = bytearray()
        for item in schema.fields:
            output.extend(self._encode_field(item, values.get(item.name)))
        return bytes(output)

    def decode_message(self, name: str, data: bytes) -> dict[str, Any]:
        schema = self.registry.schema(name)
        view = memoryview(data)
        values, offset = self._decode_fields(schema.fields, view, 0)
        if offset != len(view):
            raise ProtocolError(
                f"{name} left {len(view) - offset} unread payload byte(s)"
            )
        return values

    def _encode_field(self, item: Field, value: Any) -> bytes:
        if item.repeated:
            values = [] if value is None else list(value)
            if len(values) > 0xFF:
                raise ProtocolError(f"{item.name} has more than 255 entries")
            output = bytearray((len(values),))
            for entry in values:
                output.extend(self._encode_single(item, entry))
            return bytes(output)
        return self._encode_single(item, value)

    def _encode_single(self, item: Field, value: Any) -> bytes:
        kind = item.type_name
        if kind == "number":
            return encode_number(0 if value is None else value)
        if kind == "byte":
            return struct.pack("<B", 0 if value is None else int(value))
        if kind == "word":
            return struct.pack("<H", 0 if value is None else int(value))
        if kind == "dword":
            return struct.pack("<I", 0 if value is None else int(value))
        if kind == "float":
            return struct.pack("<f", 0.0 if value is None else float(value))
        if kind == "double":
            return struct.pack("<d", 0.0 if value is None else float(value))
        if kind == "string":
            return encode_string("" if value is None else value)

        fields = item.children
        if kind != "table":
            fields = self.registry.schema(kind).fields
        values = {} if value is None else value
        output = bytearray()
        for child in fields:
            output.extend(self._encode_field(child, values.get(child.name)))
        return bytes(output)

    def _decode_fields(
        self, fields: list[Field], data: memoryview, offset: int
    ) -> tuple[dict[str, Any], int]:
        values: dict[str, Any] = {}
        for item in fields:
            if item.repeated:
                _require(data, offset, 1)
                count = data[offset]
                offset += 1
                entries = []
                for _ in range(count):
                    entry, offset = self._decode_single(item, data, offset)
                    entries.append(entry)
                values[item.name] = entries
            else:
                values[item.name], offset = self._decode_single(item, data, offset)
        return values, offset

    def _decode_single(
        self, item: Field, data: memoryview, offset: int
    ) -> tuple[Any, int]:
        kind = item.type_name
        if kind == "number":
            return decode_number(data, offset)
        if kind == "string":
            return decode_string(data, offset)
        formats = {
            "byte": "<B",
            "word": "<H",
            "dword": "<I",
            "float": "<f",
            "double": "<d",
        }
        if kind in formats:
            size = struct.calcsize(formats[kind])
            _require(data, offset, size)
            return struct.unpack_from(formats[kind], data, offset)[0], offset + size

        fields = item.children
        if kind != "table":
            fields = self.registry.schema(kind).fields
        return self._decode_fields(fields, data, offset)


def encode_frame(protocol_id: int, body: bytes, cipher: RollingXor | None) -> bytes:
    payload = struct.pack("<H", protocol_id) + body
    frame = (
        struct.pack("<H", len(payload))
        + payload
        + struct.pack("<H", checksum_base(payload))
    )
    return cipher.encrypt(frame) if cipher else frame


class FrameDecoder:
    def __init__(self, cipher: RollingXor | None) -> None:
        self.cipher = cipher
        self.buffer = bytearray()

    def feed(self, data: bytes) -> list[tuple[int, bytes]]:
        self.buffer.extend(self.cipher.transform(data) if self.cipher else data)
        frames: list[tuple[int, bytes]] = []
        while len(self.buffer) >= 2:
            payload_length = int.from_bytes(self.buffer[0:2], "little")
            if payload_length < 2:
                raise ProtocolError(f"Invalid frame payload length: {payload_length}")
            frame_length = payload_length + 4
            if len(self.buffer) < frame_length:
                break
            payload = bytes(self.buffer[2 : 2 + payload_length])
            expected = int.from_bytes(
                self.buffer[2 + payload_length : frame_length], "little"
            )
            actual = checksum_base(payload)
            del self.buffer[:frame_length]
            if actual != expected:
                raise ProtocolError(
                    f"Checksum mismatch: expected {expected:#06x}, got {actual:#06x}"
                )
            protocol_id = int.from_bytes(payload[:2], "little")
            frames.append((protocol_id, payload[2:]))
        return frames


def _require(data: memoryview, offset: int, size: int) -> None:
    if offset + size > len(data):
        raise ProtocolError(
            f"Truncated payload at offset {offset}: need {size}, "
            f"have {len(data) - offset}"
        )
