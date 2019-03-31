import argparse
import copy
from typing import Sequence, Tuple

from oslo_config import cfg

# Choices
_log_choices = ['error', 'warning', 'info', 'debug']
_backend_choices = ['stdout', 'csv', 'log', 'sqlite', 'postgresql']
_frontend_choices = ['cli', 'curses']
_socket_choices = ['tcp', 'unix']
_quote_choices = ['all', 'minimal', 'nonnumeric', 'none']

# Option groups
_gravity_group = cfg.OptGroup(name='gravity', help='Configure gravity project options.')
_log_group = cfg.OptGroup(name='log', help='Configure logging options')
_socket_group = cfg.OptGroup(name='socket', help='Configure client/server socket options.')
_tcp_group = cfg.OptGroup(name='tcp', help='Configure TCP socket options.')
_unix_group = cfg.OptGroup(name='unix', help='Configure UNIX socket options.')
_frontend_group = cfg.OptGroup(name='frontend', help='Configure client frontend options.')
_backend_group = cfg.OptGroup(name='backend', help='Configure storage backend options.')
_csv_group = cfg.OptGroup(name='csv', help='Configure CSV storage backend options.')
_sqlite_group = cfg.OptGroup(name='sqlite', help='Configure sqlite storage backend options.')
_postgresql_group = cfg.OptGroup(name='postgresql', help='Configure postgresql storage backend options.')

# Options
_gravity_opts = [
    cfg.StrOpt(name='projects', default='gravity_projects.json', help='Path to gravity projects file', short='p'),
    cfg.StrOpt(name='actions', default='gravity_actions.json', help='Path to gravity actions file', short='a'),
    cfg.BoolOpt(name='daemon', default=False, help='Run server as daemon')
]

_log_opts = [
    cfg.StrOpt(name='level', default='info', help='Log level'),
    cfg.StrOpt(name='file', default='gravity.log', help='Log File'),
    cfg.ListOpt(name='targets', default=['file', 'console'], help='Log target(s)', bounds=True)
]

_socket_opts = [
    cfg.StrOpt(name='type', default='tcp', help='Client/server socket type.', choices=_socket_choices, short='t')
]

_tcp_opts = [
    cfg.HostAddressOpt(name='host', default='127.0.0.1', help='Host to bind socket on.', short='H'),
    cfg.PortOpt(name='port', min=1, max=65535, default=4242, help='Port to bind socket on.', short='P'),
]

_unix_opts = [
    cfg.StrOpt(name='socket', default='/var/run/gravity.sock', help='UNIX socket path', short='S')
]

_frontend_opts = [
    cfg.StrOpt(name='interface', default='curses', help='Client frontend', choices=_frontend_choices, short='F')
]

_backend_opts = [
    cfg.StrOpt(name='driver', default='sqlite', help='Storage backend', choices=_backend_choices, short='B')
]

_csv_opts = [
    cfg.StrOpt(name='output', default='gravity_storage.csv', help='CSV output file'),
    cfg.StrOpt(name='delimiter', default=';', help='CSV field delimiter'),
    cfg.StrOpt(name='quoting', default='all', help='CSV quoting character', choices=_quote_choices)
]

_sqlite_opts = [
    cfg.StrOpt(name='database', default='gravity_storage.sqlite', help='SQLite database file')
]

_postgresql_opts = [
    cfg.StrOpt(name='hostname', default=None, help='PostgreSQL database'),
    cfg.PortOpt(name='port', min=1, max=65535, default=5432, help='PostgreSQL port'),
    cfg.StrOpt(name='username', default='postgres', help='PostgreSQL username'),
    cfg.StrOpt(name='password', default='', secret=True, help='PostgreSQL password'),
    cfg.StrOpt(name='database', default='worklogs', help='PostgreSQL database')
]

_opts = [
    (_gravity_group, _gravity_opts),
    (_log_group, _log_opts),
    (_socket_group, _socket_opts),
    (_tcp_group, _tcp_opts),
    (_unix_group, _unix_opts),
    (_frontend_group, _frontend_opts),
    (_backend_group, _backend_opts),
    (_csv_group, _csv_opts),
    (_sqlite_group, _sqlite_opts),
    (_postgresql_group, _postgresql_opts)
]


def add_subparsers(subparsers: argparse.ArgumentParser) -> cfg.SubCommandOpt:
    project = subparsers.add_parser('project')
    # project.add_argument('command', choices=['add', 'export', 'list', 'remove'])
    # project.add_argument('projects', type=str, nargs='*')
    _project = project.add_mutually_exclusive_group(required=True)
    _project.add_argument('-a', '--add', nargs=argparse.REMAINDER, metavar='PROJECT', help='Add project(s)')
    _project.add_argument('-e', '--export', action='store_true', help='Export projects)')
    _project.add_argument('-l', '--list', action='store_true', help='List projects')
    _project.add_argument('-r', '--remove', nargs=argparse.REMAINDER, metavar='PROJECT', help='Remove project(s)')

    server = subparsers.add_parser('server')
    # server.add_argument('command', choices=['start', 'stop'])

    client = subparsers.add_parser('client')
    # client.add_argument('command', choices=['record'])

    action = subparsers.add_parser('action')
    # action.add_argument('command', choices=['add', 'export', 'list', 'remove'])
    # action.add_argument('actions', type=str, nargs='*')
    _action = action.add_mutually_exclusive_group(required=True)
    _action.add_argument('-a', '--add', nargs=argparse.REMAINDER, metavar='ACTION', help='Add action(s)')
    _action.add_argument('-e', '--export', action='store_true', help='Export actions)')
    _action.add_argument('-l', '--list', action='store_true', help='List actions')
    _action.add_argument('-r', '--remove', nargs=argparse.REMAINDER, metavar='ACTION', help='Remove action(s)')

    database = subparsers.add_parser('database')
    # database.add_argument('command', choices=['initialise', 'truncate'])
    _database = database.add_mutually_exclusive_group(required=True)
    _database.add_argument('-d', '--drop', action='store_true', help='Drop database tables')
    _database.add_argument('-i', '--initialise', action='store_true', help='Initialise database tables')
    _database.add_argument('-p', '--prune', action='store_true', help='Prune database tables')
    _database.add_argument('-t', '--truncate', action='store_true', help='Truncate database tables')


def list_opts() -> Sequence[Tuple[cfg.OptGroup, Sequence[cfg.Opt]]]:
    """List all options. Used by oslo.config to generate example config files"""
    return [(g, copy.deepcopy(o)) for g, o in _opts]


class BaseConfig(cfg.ConfigOpts):
    def __init__(self) -> None:
        super(BaseConfig, self).__init__()

        for group, opts in _opts:
            self.register_group(group)
            self.register_opts(opts, group)
            self.register_cli_opts(opts, group)

        self.register_cli_opt(cfg.SubCommandOpt('argument', handler=add_subparsers))

        # Populate config object via its __call__ method. Otherwise, command-line argument parsing etc. won't work
        # This slightly odd call lets us avoid the worse option of having a global "CONFIG" variable
        self.__call__()
