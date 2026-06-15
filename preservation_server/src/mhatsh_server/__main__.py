from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from .bootstrap import BootstrapServer
from .game_server import GameServer
from .schema import SchemaRegistry


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description="MHA TSH preservation server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--bootstrap-port", type=int, default=18080)
    parser.add_argument("--game-port", type=int, default=19000)
    parser.add_argument("--client-game-host", default="127.0.0.1")
    parser.add_argument(
        "--schemas", type=Path, default=project_root / "allproto_readable.lua"
    )
    parser.add_argument(
        "--protocol-ids",
        type=Path,
        default=project_root / "analysis" / "protocol_ids.csv",
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    registry = SchemaRegistry.from_files(args.schemas, args.protocol_ids)
    bootstrap = BootstrapServer(
        args.client_game_host, args.game_port, args.bootstrap_port
    )
    game = GameServer(registry)
    await asyncio.gather(
        bootstrap.serve(args.host, args.bootstrap_port),
        game.serve(args.host, args.game_port),
    )


if __name__ == "__main__":
    asyncio.run(main())
