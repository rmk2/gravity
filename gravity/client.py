import asyncio
import json
import sys
from typing import Any, Dict, Union

from gravity.config import BaseConfig


async def message_writer(message: Dict[str, Any], config: BaseConfig) -> Union[Dict[str, Any], None]:
    """Pass a byte-encoded JSON message to a server via TCP or UNIX socket"""
    if config.socket.type == 'tcp':
        reader, writer = await asyncio.open_connection(host=config.tcp.host, port=config.tcp.port)
    elif config.socket.type == 'unix':
        reader, writer = await asyncio.open_unix_connection(path=config.unix.socket)
    else:
        raise AssertionError(f"Requested socket type is not one of: 'tcp', 'unix'")

    writer.write(json.dumps(message).encode(encoding='utf-8'))
    writer.write_eof()
    await writer.drain()

    data = await reader.read()
    assert data, 'No data has been received'
    response = json.loads(data.decode(encoding='utf-8'))

    writer.close()

    return response


def send_message(message: Dict[str, Any], config: BaseConfig) -> Union[Dict[str, Any], None]:
    try:
        message = asyncio.run(message_writer(message, config))

        if isinstance(message.get('response'), dict):
            error = message.get('response', {}).get('error')
        else:
            error = False

        if error:
            raise Exception(error)
        else:
            return message

    except Exception as e:
        print(str(e), file=sys.stderr)
        exit(1)
