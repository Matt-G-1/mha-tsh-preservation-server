from __future__ import annotations

from pathlib import Path

from mhatsh_server.protocol import (
    FrameDecoder,
    ProtocolCodec,
    RollingXor,
    checksum_base,
    decode_number,
    decode_string,
    encode_frame,
    encode_number,
    encode_string,
)
from mhatsh_server.schema import SchemaRegistry


ROOT = Path(__file__).resolve().parents[2]


def registry() -> SchemaRegistry:
    return SchemaRegistry.from_files(
        ROOT / "allproto_readable.lua", ROOT / "analysis" / "protocol_ids.csv"
    )


def test_number_round_trip() -> None:
    for value in (0, 1, -1, 255, 256, -65536, (1 << 48) - 1):
        encoded = encode_number(value)
        decoded, offset = decode_number(memoryview(encoded), 0)
        assert decoded == value
        assert offset == len(encoded)


def test_string_round_trip_short_and_long() -> None:
    for value in ("", "MHA", "x" * 300):
        encoded = encode_string(value)
        decoded, offset = decode_string(memoryview(encoded), 0)
        assert decoded == value
        assert offset == len(encoded)


def test_login_version_schema_round_trip() -> None:
    codec = ProtocolCodec(registry())
    values = {"ClientVersion": "40009.7.2", "PtoVersion": 48, "VerifyStr": "test"}
    encoded = codec.encode_message("s_login_version", values)
    assert codec.decode_message("s_login_version", encoded) == values


def test_recovered_player_info_schema_round_trip() -> None:
    current = registry()
    codec = ProtocolCodec(current)
    assert current.protocol_ids["s_login_version"] == 1
    assert current.protocol_ids["c_login_version"] == 3
    assert current.protocol_ids["c_login_player_info"] == 654
    values = {
        "Uid": 10001,
        "Name": "Local Hero",
        "Level": 1,
        "HostId": 1,
        "ServerName": "Local Preservation Server",
        "CreateTime": 123456,
    }
    encoded = codec.encode_message("c_login_player_info", values)
    assert codec.decode_message("c_login_player_info", encoded) == values


def test_encrypted_frame_round_trip() -> None:
    seed = 0x12345678
    body = b"\x04MHA\x02\x30\x05test"
    encoded = encode_frame(2, body, RollingXor(seed))
    frames = FrameDecoder(RollingXor(seed)).feed(encoded)
    assert frames == [(2, body)]


def test_checksum_zero_and_odd_byte_order() -> None:
    assert checksum_base(b"") == 0
    assert checksum_base(b"\x01") == 0x6C6B
