import argparse
from typing import Sequence, Tuple

from oslo_config import cfg

# Choices
_log_choices = ['error', 'warning', 'info', 'debug']

_quote_choices = [
    ('all', 'Quote all fields, regardless of type'),
    ('nonnumeric', 'Quote all non-numeric fields'),
    ('minimal', 'Only quote fields which contain special characters'),
    ('none', 'Do not quote any fields, only escape delimiters'),
]

_frontend_choices = [
    ('cli', 'Command-line interface to log events'),
    ('curses', 'Curses-based interface to log events'),
]

_socket_choices = [
    ('tcp', 'Use a TCP socket to communicate with the server'),
    ('unix', 'Use a UNIX socket to communicate with the server'),
    ('websockets', 'Use a WebSocket to communicate with the server'),
]

_backend_choices = [
    ('stdout', 'Print events to stdout'),
    ('csv', 'Write events to a CSV file'),
    ('log', 'Write events to a log file'),
    ('sqlite', 'Write events to a SQLite database'),
    ('postgresql', 'Write events to a PostgreSQL database'),
]

# Option groups
_main_group = cfg.OptGroup(name='main', help='Configure gravity project options.')
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
_main_opts = [
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
    (_main_group, _main_opts),
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


def add_subparsers(subparsers: argparse.Namespace) -> None:
    project = subparsers.add_parser('project', help='Administrate project data')
    # project.add_argument('command', choices=['add', 'export', 'list', 'remove'])
    # project.add_argument('projects', type=str, nargs='*')
    _project = project.add_mutually_exclusive_group(required=True)
    _project.add_argument('-a', '--add', nargs=argparse.REMAINDER, metavar='PROJECT', help='Add project(s)')
    _project.add_argument('-e', '--export', action='store_true', help='Export projects)')
    _project.add_argument('-i', '--ingest', '--import', metavar='FILE', type=str, help='Import projects')
    _project.add_argument('-l', '--list', action='store_true', help='List projects')
    _project.add_argument('-r', '--remove', nargs=argparse.REMAINDER, metavar='PROJECT', help='Remove project(s)')

    annotate = subparsers.add_parser('annotate', help='Annotate a given project')
    annotate.add_argument('project', metavar='PROJECT', type=str, help='Project UUID')
    annotate.add_argument('-d', '--description', metavar='DESCRIPTION', type=str, help='Project description')
    annotate.add_argument('-k', '--key', metavar='KEY', type=str, help='Project key')

    server = subparsers.add_parser('server', help='Start a gravity server instance')
    # server.add_argument('command', choices=['start', 'stop'])

    client = subparsers.add_parser('client', help='Run a gravity client instance')
    # client.add_argument('command', choices=['record'])

    action = subparsers.add_parser('action', help='Administrate event action data')
    # action.add_argument('command', choices=['add', 'export', 'list', 'remove'])
    # action.add_argument('actions', type=str, nargs='*')
    _action = action.add_mutually_exclusive_group(required=True)
    _action.add_argument('-a', '--add', nargs=argparse.REMAINDER, metavar='ACTION', help='Add action(s)')
    _action.add_argument('-e', '--export', action='store_true', help='Export actions)')
    _action.add_argument('-i', '--ingest', '--import', metavar='FILE', type=str, help='Import actions')
    _action.add_argument('-l', '--list', action='store_true', help='List actions')
    _action.add_argument('-r', '--remove', nargs=argparse.REMAINDER, metavar='ACTION', help='Remove action(s)')

    database = subparsers.add_parser('database', help='Configure the backend database')
    # database.add_argument('command', choices=['initialise', 'truncate'])
    _database = database.add_mutually_exclusive_group(required=True)
    _database.add_argument('-d', '--drop', action='store_true', help='Drop database tables')
    _database.add_argument('-i', '--initialise', action='store_true', help='Initialise database tables')
    _database.add_argument('-p', '--prune', action='store_true', help='Prune database tables')
    _database.add_argument('-t', '--truncate', action='store_true', help='Truncate database tables')

    worklog = subparsers.add_parser('worklog', help='Manipulate worklog entries')
    _worklog = worklog.add_mutually_exclusive_group(required=True)
    _worklog.add_argument('-a', '--amend', nargs=argparse.REMAINDER, metavar='WORKLOG', help='Amend last worklog')
    _worklog.add_argument('-r', '--remove', action='store_true', help='Remove last worklog')

    # Dummy parser to use for testing, making sure that "argument" is still supplied
    _ = subparsers.add_parser('test')


def list_opts() -> Sequence[Tuple[cfg.OptGroup, Sequence[cfg.Opt]]]:
    """List all options. Used by oslo.config to generate example config files"""
    return [(g, o) for g, o in _opts]


class BaseConfig(cfg.ConfigOpts):
    def __init__(self) -> None:
        super(BaseConfig, self).__init__()

        for group, opts in _opts:
            self.register_group(group)
            self.register_opts(opts, group)
            self.register_cli_opts(opts, group)

        self.register_cli_opt(cfg.SubCommandOpt('argument', handler=add_subparsers))
