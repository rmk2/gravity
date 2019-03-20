import asyncio
from typing import Dict, Any
import json

from gravity.config import BaseConfig


async def message_writer(message: Dict[str, Any], config: BaseConfig) -> None:
    """Pass a byte-encoded JSON message to a server via TCP or UNIX socket"""
    if config.socket.type == 'tcp':
        reader, writer = await asyncio.open_connection(host=config.tcp.host, port=config.tcp.port)
    elif config.socket.type == 'unix':
        reader, writer = await asyncio.open_unix_connection(path=config.unix.socket)
    else:
        raise AssertionError(f"Requested socket type is not one of: 'tcp', 'unix'")

    writer.write(json.dumps(message).encode(encoding='utf-8'))

    writer.close()
