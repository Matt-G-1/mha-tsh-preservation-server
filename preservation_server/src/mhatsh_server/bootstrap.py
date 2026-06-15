from __future__ import annotations

import asyncio
import json
import logging
import time
from urllib.parse import urlsplit


LOG = logging.getLogger("mhatsh.bootstrap")


class BootstrapServer:
    def __init__(
        self, game_host: str, game_port: int, bootstrap_port: int = 18080
    ) -> None:
        self.game_host = game_host
        self.game_port = game_port
        self.bootstrap_port = bootstrap_port

    async def serve(self, host: str, port: int) -> None:
        server = await asyncio.start_server(self.handle_client, host, port)
        addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
        LOG.info("bootstrap server listening on %s", addresses)
        async with server:
            await server.serve_forever()

    async def handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            header = await reader.readuntil(b"\r\n\r\n")
            request_line = header.split(b"\r\n", 1)[0].decode("latin-1")
            method, target, _ = request_line.split(" ", 2)
            content_length = 0
            for line in header.split(b"\r\n")[1:]:
                if line.lower().startswith(b"content-length:"):
                    content_length = int(line.split(b":", 1)[1].strip())
            body = await reader.readexactly(content_length) if content_length else b""
            path = urlsplit(target).path
            LOG.info("%s %s body=%s", method, target, body.decode(errors="replace"))
            payload = self.response_for(path)
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json; charset=utf-8\r\n"
                + f"Content-Length: {len(payload)}\r\n".encode()
                + b"Connection: close\r\n\r\n"
                + payload
            )
            writer.write(response)
            await writer.drain()
        except (asyncio.IncompleteReadError, ValueError) as exc:
            LOG.warning("malformed bootstrap request: %s", exc)
        finally:
            writer.close()
            await writer.wait_closed()

    def response_for(self, path: str) -> bytes:
        server = {
            "srv_id": 1,
            "ip": self.game_host,
            "domain": self.game_host,
            "client_port": self.game_port,
            "srv_name": "Local Preservation Server",
            "pf_srv_name": "Local Preservation Server",
            "status": 1,
            "pf_srv_status": 1,
            "style_status": 0,
            "is_white": 0,
            "pf_srv_hide_type": 0,
            "is_recommend": 1,
            "pf_srv_tag": 1,
            "flag": 1,
            "tag": 1,
            "is_skip_check": 1,
            "open_time": 0,
            "pf_open_time": 0,
            "GcloudSvrId": 1,
            "maintain_notice": "",
            "flagTips": "",
            "player_list": [],
        }
        if path.endswith("/client/config"):
            base = f"http://{self.game_host}:{self.bootstrap_port}"
            config_info = {
                "hot_url": [f"{base}/assets"],
                "server_url": f"{base}/g/1/v/1/gcli/server/list",
                "sub_version": "40009.7.2.48",
                "puffer_url": f"{base}/assets",
                "maintain_notice_url": "",
                "login_notice_url": "",
                "android_apk_url": "",
                "show_fps": False,
                "is_tishen": False,
                "show_repair": False,
                "announcement_asset_url": f"{base}/assets",
                "need_auto_login": False,
                "is_open_select_account": False,
                "force_update_ver": 0,
                "is_aab": False,
                "use_cjson": True,
                "server_list_analysis_type": "JSON",
                "extend_version": "40009,7,2,48",
            }
            data = {
                "code": 1,
                "data": {"config_info": config_info},
            }
        elif path.endswith("/server/list"):
            data = {
                "code": 0,
                "status": 1,
                "data": {"srv_list": [server], "player_list": [], "group_list": []},
            }
        elif path.endswith("/player/list"):
            # GMSReqRoleList uses the legacy success code and requires the
            # player_list key even when the account has no characters.
            data = {"code": 1, "data": {"player_list": []}}
        elif path.endswith("/visitor/user/register") or path.endswith(
            "/visitor/user/login"
        ):
            data = {
                "code": 0,
                "data": {
                    "user_id": "local-guest",
                    "user_sid": "local-session",
                    "time": int(time.time()),
                    "is_player": 0,
                },
            }
        elif path.endswith("/f/herosdk/ch/0/user/login"):
            data = {
                "code": 0,
                "data": {
                    "account_id": "local-guest",
                    "account_name": "Local Guest",
                    "token": "local-access-token",
                    "time": int(time.time()),
                    "adult": 2,
                },
            }
        elif path.endswith("/report/player/create"):
            data = {"code": 0, "data": {}}
        elif path.endswith("/login/step"):
            data = {"code": 1, "data": {}}
        else:
            data = {"code": 1, "data": {}}
        return json.dumps(data, separators=(",", ":")).encode()
