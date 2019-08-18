import asyncio
import json
import logging
import signal
import sys
from functools import partial
from typing import Any, Dict

import daemon

from gravity.action import add_actions, import_actions, remove_actions
from gravity.config import BaseConfig
from gravity.project import add_projects, import_projects, remove_projects
from gravity.worklog import add_worklog, modify_worklog, remove_worklog


def request_handler(message: Dict[str, Any], config: BaseConfig) -> callable:
    """Dispatch request handler as specified in decoded requests passed by the server"""
    assert 'request' in message, 'No request has been received'
    # assert 'payload' in message, 'No payload has been received'

    request = message.get('request')
    payload = message.get('payload')

    request_types = {
        # actions
        'add_actions': lambda: add_actions(payload.get('actions'), config),
        'get_actions': lambda: {'actions': import_actions(config)},
        'remove_actions': lambda: remove_actions(payload.get('actions'), config),
        # projects
        'add_projects': lambda: add_projects(payload.get('projects'), config),
        'get_projects': lambda: {'projects': import_projects(config)},
        'remove_projects': lambda: remove_projects(payload.get('projects'), config),
        # worklogs
        'add_worklog': lambda: add_worklog(payload.get('worklog'), config),
        'modify_worklog': lambda: modify_worklog(payload.get('modifier'), config),
        'remove_worklog': lambda: remove_worklog(config)
    }
    request_types['get_data'] = lambda: {**request_types['get_projects'](), **request_types['get_actions']()}

    assert request in request_types, 'No valid request has been received'

    return request_types.get(request, None)


async def socket_handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, config: BaseConfig) -> None:
    """Receive, decode, and handle data received by the server via TCP/UNIX socket before handling them"""
    try:
        data = await reader.readline()
        assert data, 'No data has been received'
        request = json.loads(data.decode(encoding='utf-8'))

        logging.debug(request)

        handler = request_handler(request, config)
        response = json.dumps({'response': handler()}).encode(encoding='utf-8')

        logging.debug(response)

        writer.write(response)
        await writer.drain()
        writer.close()

    except Exception as e:
        logging.error(repr(e))


async def start_listener(config: BaseConfig) -> None:
    _socket_handler = partial(socket_handler, config=config)

    if config.socket.type == 'tcp':
        server = await asyncio.start_server(_socket_handler, host=config.tcp.host, port=config.tcp.port)
    elif config.socket.type == 'unix':
        server = await asyncio.start_unix_server(_socket_handler, path=config.unix.socket)
    else:
        raise AssertionError(f"Requested socket type is not one of: 'tcp', 'unix'")

    server_options = {
        'type': config.socket.type,
        'socket': server.sockets[0].getsockname(),
        'backend': config.backend.driver,
        'daemon': config.gravity.daemon
    }

    logging.info(f'Server started. Listening on {server_options["socket"]}')
    logging.debug(f'{server_options}')

    async with server:
        await server.serve_forever()


def start_server(config: BaseConfig) -> None:
    def daemon_shutdown(signum, frame):
        sys.exit(0)

    try:
        if not config.gravity.daemon:
            asyncio.run(start_listener(config))
        elif config.gravity.daemon:
            with daemon.DaemonContext(signal_map={signal.SIGTERM: daemon_shutdown, signal.SIGTSTP: daemon_shutdown}):
                asyncio.run(start_listener(config))

    except KeyboardInterrupt:
        exit(0)


if __name__ == '__main__':
    raise NotImplementedError('Server cannot be called directly')
