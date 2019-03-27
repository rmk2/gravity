import asyncio
from functools import partial
import json
import signal
import sys

import daemon

from gravity.backend import csv_writer, log_writer, postgresql_writer, sqlite3_writer
from gravity.config import BaseConfig


async def message_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, config: BaseConfig) -> None:
    """Receive and decode bytes received by the server before handling them"""
    data = await reader.readline()
    assert data, 'No data has been received'
    message = json.loads(data.decode(encoding='utf-8'))

    if config.backend.driver == 'csv':
        csv_writer(message, config)
    elif config.backend.driver == 'log':
        log_writer(message, config)
    elif config.backend.driver == 'postgresql':
        postgresql_writer(message, config)
    elif config.backend.driver == 'sqlite3':
        sqlite3_writer(message, config)
    elif config.backend.driver == 'stdout':
        print(message)

    writer.close()


async def start_listener(config: BaseConfig) -> None:
    """Receive messages send by clients via TCP or UNIX socket"""
    _message_handler = partial(message_handler, config=config)

    if config.socket.type == 'tcp':
        server = await asyncio.start_server(_message_handler, host=config.tcp.host, port=config.tcp.port)
    elif config.socket.type == 'unix':
        server = await asyncio.start_unix_server(_message_handler, path=config.unix.socket)
    else:
        raise AssertionError(f"Requested socket type is not one of: 'tcp', 'unix'")

    print(f'Listening on {server.sockets[0].getsockname()}')

    async with server:
        await server.serve_forever()


def start_server(config: BaseConfig) -> None:
    def daemon_shutdown(signum, frame):
        sys.exit(0)

    with daemon.DaemonContext(signal_map={signal.SIGTERM: daemon_shutdown, signal.SIGTSTP: daemon_shutdown}):
        asyncio.run(start_listener(config))


if __name__ == '__main__':
    raise NotImplementedError('Server cannot be called directly')
