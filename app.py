from os.path import dirname, join

import gravity.action
import gravity.database
import gravity.project
import gravity.worklog
from gravity.client import send_message
from gravity.config import BaseConfig
from gravity.frontend import run_curses
from gravity.logger import initialise_logging
from gravity.server import start_server

config = BaseConfig()
config(default_config_files=[join(dirname(__file__), 'gravity.default.conf')])

initialise_logging(config)

argument = config.argument.name

if argument == 'server':
    start_server(config)

elif argument == 'client':
    if config.frontend.interface == 'curses':
        run_curses(config)

elif argument == 'project':
    if config.argument.add:
        send_message({'request': 'add_projects', 'payload': {'projects': config.argument.add}}, config)

    elif config.argument.export:
        gravity.project.export_projects(config)

    elif config.argument.ingest:
        gravity.project.import_projects(config, config.argument.ingest)

    elif config.argument.list:
        gravity.project.list_projects(config)

    elif config.argument.remove:
        send_message({'request': 'remove_projects', 'payload': {'projects': config.argument.remove}}, config)

elif argument == 'action':
    if config.argument.add:
        _actions = gravity.action.add_actions(config.argument.add)
        send_message({'request': 'insert_actions', 'payload': {'actions': _actions}}, config)

    elif config.argument.export:
        _actions = send_message({'request': 'get_actions'}, config).get('response', {}).get('actions', [])
        gravity.action.export_actions(_actions)

    elif config.argument.ingest:
        _actions = gravity.action.import_actions(config.argument.ingest)
        send_message({'request': 'insert_actions', 'payload': {'actions': _actions}}, config)

    elif config.argument.list:
        _actions = send_message({'request': 'get_actions'}, config).get('response', {}).get('actions', [])
        gravity.action.list_actions(_actions)

    elif config.argument.remove:
        send_message({'request': 'remove_actions', 'payload': {'actions': config.argument.remove}}, config)

elif argument == 'database':
    if config.argument.drop:
        gravity.database.drop(config)

    elif config.argument.initialise:
        gravity.database.initialise(config)

    elif config.argument.prune:
        gravity.database.prune(config)

    elif config.argument.truncate:
        gravity.database.truncate(config)

elif argument == 'worklog':
    if config.argument.amend:
        message = send_message({'request': 'modify_worklog', 'payload': {'modifier': config.argument.amend[0]}}, config)
        print(message.get('response'))

    elif config.argument.remove:
        message = send_message({'request': 'remove_worklog'}, config)
        print(message.get('response'))
