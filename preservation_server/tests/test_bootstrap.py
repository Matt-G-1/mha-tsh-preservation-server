from __future__ import annotations

import json

from mhatsh_server.bootstrap import BootstrapServer


def test_empty_player_list_response_has_legacy_success_shape() -> None:
    server = BootstrapServer("127.0.0.1", 19000)
    payload = json.loads(server.response_for("/g/1/v/1/gcli/player/list"))

    assert payload == {"code": 1, "data": {"player_list": []}}


def test_existing_player_mode_advertises_local_player() -> None:
    server = BootstrapServer("127.0.0.1", 19000, has_player=True)

    login_payload = json.loads(
        server.response_for("/ssssssssssssssssssssssss/v/1/visitor/user/login")
    )
    assert login_payload["data"]["is_player"] == 1

    player_list = json.loads(server.response_for("/g/1/v/1/gcli/player/list"))
    [player] = player_list["data"]["player_list"]
    assert player["uid"] == 10001
    assert player["name"] == "Local Hero"
    assert player["srv_id"] == 1

    server_list = json.loads(server.response_for("/g/1/v/1/gcli/server/list"))
    assert server_list["data"]["player_list"] == [player]
    assert server_list["data"]["srv_list"][0]["player_list"] == [player]


def test_player_creation_report_returns_sdk_success_code() -> None:
    server = BootstrapServer("127.0.0.1", 19000)
    payload = json.loads(server.response_for("/v/1/report/player/create"))

    assert payload == {"code": 0, "data": {}}


def test_client_config_advertises_configured_lan_host_and_port() -> None:
    server = BootstrapServer("192.0.2.10", 19000, 18081)
    payload = json.loads(server.response_for("/g/1/v/1/gcli/client/config"))
    config = payload["data"]["config_info"]

    assert config["hot_url"] == ["http://192.0.2.10:18081/assets"]
    assert config["server_url"] == (
        "http://192.0.2.10:18081/g/1/v/1/gcli/server/list"
    )
