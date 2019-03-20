import copy
from typing import Sequence, Tuple

from oslo_config import cfg

# Choices
_backend_choices = ['stdout', 'csv', 'log', 'sqlite3', 'postgresql']
_socket_choices = ['tcp', 'unix']
_quote_choices = ['all', 'minimal', 'nonnumeric', 'none']

# Option groups
_socket_group = cfg.OptGroup(name='socket', help='Configure client/server socket options.')
_tcp_group = cfg.OptGroup(name='tcp', help='Configure TCP socket options.')
_unix_group = cfg.OptGroup(name='unix', help='Configure UNIX socket options.')
_project_group = cfg.OptGroup(name='project', help='Configure gravity project options.')
_backend_group = cfg.OptGroup(name='backend', help='Configure storage backend options.')
_csv_group = cfg.OptGroup(name='csv', help='Configure CSV storage backend options.')

# Options
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

_project_opts = [
    cfg.StrOpt(name='file', default='~/gravity_projects.json', help='Path to gravity project file', short='f')
]

_backend_opts = [
    cfg.StrOpt(name='driver', default='csv', help='Storage backend', choices=_backend_choices, short='b'),
    cfg.StrOpt(name='output', default='/dev/shm/gravity_storage.csv', help='Output file', short='O')
]

_csv_opts = [
    cfg.StrOpt(name='delimiter', default=';', help='Delimiter for CSV fields', short='d'),
    cfg.StrOpt(name='quote', default='all', help='Quoting style for CSV fields', choices=_quote_choices, short='q')
]

_opts = [
    (_socket_group, _socket_opts),
    (_tcp_group, _tcp_opts),
    (_unix_group, _unix_opts),
    (_project_group, _project_opts),
    (_backend_group, _backend_opts),
    (_csv_group, _csv_opts)
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

        self.header = ['key', 'value']

        # Populate config object via its __call__ method. Otherwise, command-line argument parsing etc. won't work
        # This slightly odd call lets us avoid the worse option of having a global "CONFIG" variable
        self.__call__()
