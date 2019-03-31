from gravity.config import BaseConfig
from gravity.frontend import run_curses
from gravity.logger import initialise_logging
from gravity.server import start_server
import gravity.action
import gravity.database
import gravity.project

config = BaseConfig()
config(default_config_files=['gravity.default.conf'])

initialise_logging(config)

argument = config.argument.name

if argument == 'server':
    start_server(config)

elif argument == 'client':
    if config.frontend.interface == 'curses':
        run_curses(config)

elif argument == 'project':
    if config.argument.add:
        gravity.project.add_projects(config.argument.add, config)

    elif config.argument.export:
        gravity.project.export_projects(config)

    elif config.argument.list:
        gravity.project.list_projects(config)

    elif config.argument.remove:
        gravity.project.remove_projects(config.argument.remove, config)

elif argument == 'action':
    if config.argument.add:
        gravity.action.add_actions(config.argument.add, config)

    elif config.argument.export:
        gravity.action.export_actions(config)

    elif config.argument.list:
        gravity.action.list_actions(config)

    elif config.argument.remove:
        gravity.action.remove_actions(config.argument.remove, config)

elif argument == 'database':
    if config.argument.drop:
        gravity.database.drop(config)

    elif config.argument.initialise:
        gravity.database.initialise(config)

    elif config.argument.prune:
        gravity.database.prune(config)

    elif config.argument.truncate:
        gravity.database.truncate(config)
