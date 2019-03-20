import copy
from typing import Sequence, Tuple

from oslo_config import cfg

# Choices
_backend_choices = ['stdout', 'csv', 'log', 'sqlite', 'postgresql']
_socket_choices = ['tcp', 'unix']
_quote_choices = ['all', 'minimal', 'nonnumeric', 'none']

# Option groups
_gravity_group = cfg.OptGroup(name='gravity', help='Configure gravity project options.')
_socket_group = cfg.OptGroup(name='socket', help='Configure client/server socket options.')
_tcp_group = cfg.OptGroup(name='tcp', help='Configure TCP socket options.')
_unix_group = cfg.OptGroup(name='unix', help='Configure UNIX socket options.')
_backend_group = cfg.OptGroup(name='backend', help='Configure storage backend options.')
_csv_group = cfg.OptGroup(name='csv', help='Configure CSV storage backend options.')
_sqlite_group = cfg.OptGroup(name='sqlite', help='Configure sqlite storage backend options.')
_postgresql_group = cfg.OptGroup(name='postgresql', help='Configure postgresql storage backend options.')

# Options
_gravity_opts = [
    cfg.StrOpt(name='file', default='~/gravity_projects.json', help='Path to gravity project file', short='f'),
    cfg.ListOpt(name='columns', required=True, bounds=True, help='Storage columns', short='c')
]

_socket_opts = [
    cfg.StrOpt(name='type', default='tcp', help='Client/server socket type.', choices=_socket_choices, short='t')
]

_tcp_opts = [
    cfg.HostAddressOpt(name='host', default='127.0.0.1', help='Host to bind socket on.', short='H'),
    cfg.PortOpt(name='port', min=1, max=65535, default=4242, help='Port to bind socket on.', short='P'),
]

_unix_opts = [
    cfg.StrOpt(name='socket', default='data-data_lineage.sock', help='UNIX socket path', short='S')
]

_backend_opts = [
    cfg.StrOpt(name='driver', default='csv', help='Storage backend', choices=_backend_choices, short='b'),
]

_csv_opts = [
    cfg.StrOpt(name='output', default='./gravity_storage.csv', help='CSV output file'),
    cfg.StrOpt(name='delimiter', default=';', help='CSV field delimiter'),
    cfg.StrOpt(name='quoting', default='all', help='CSV quoting character', choices=_quote_choices)
]

_sqlite_opts = [
    cfg.StrOpt(name='database', default='~/gravity_storage.sqlite', help='SQLite database file')
]

_postgresql_opts = [
    cfg.StrOpt(name='hostname', default='localhost', help='PostgreSQL database'),
    cfg.PortOpt(name='port', min=1, max=65535, default=5432, help='PostgreSQL port'),
    cfg.StrOpt(name='username', default='postgres', help='PostgreSQL username'),
    cfg.StrOpt(name='password', default='', secret=True, help='PostgreSQL password'),
    cfg.StrOpt(name='database', default='worklogs', help='PostgreSQL database')
]

_opts = [
    (_gravity_group, _gravity_opts),
    (_socket_group, _socket_opts),
    (_tcp_group, _tcp_opts),
    (_unix_group, _unix_opts),
    (_backend_group, _backend_opts),
    (_csv_group, _csv_opts),
    (_sqlite_group, _sqlite_opts),
    (_postgresql_group, _postgresql_opts)
]


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

        # Populate config object via its __call__ method. Otherwise, command-line argument parsing etc. won't work
        # This slightly odd call lets us avoid the worse option of having a global "CONFIG" variable
        self.__call__()
