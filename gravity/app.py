from os.path import dirname, join

import gravity.action
import gravity.database
import gravity.project
import gravity.worklog
from gravity.backend.client import send_message
from gravity.config import BaseConfig
from gravity.frontend.curses import run_curses
from gravity.logger import initialise_logging
from gravity.backend.server import start_server


def main():
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
            _projects = gravity.project.add_projects(config.argument.add)
            send_message({'request': 'insert_projects', 'payload': {'projects': _projects}}, config)

        elif config.argument.export:
            _projects = send_message({'request': 'get_projects'}, config).get('response', {}).get('projects', [])
            gravity.project.export_projects(_projects)

        elif config.argument.ingest:
            _projects = gravity.project.import_projects(config.argument.ingest)
            send_message({'request': 'insert_projects', 'payload': {'projects': _projects}}, config)

        elif config.argument.list:
            _projects = send_message({'request': 'get_projects'}, config).get('response', {}).get('projects', [])
            gravity.project.list_projects(_projects)

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
            message = send_message({'request': 'modify_worklog', 'payload': {'modifier': config.argument.amend[0]}},
                                   config)
            print(message.get('response'))

        elif config.argument.remove:
            message = send_message({'request': 'remove_worklog'}, config)
            print(message.get('response'))

    elif argument == 'annotate':
        if config.argument.project and (config.argument.description or config.argument.key):
            _project = config.argument.project
            _description = config.argument.description
            _key = config.argument.key

            _annotation = {'project': _project, 'description': _description, 'key': _key}
            message = send_message({'request': 'annotate_project', 'payload': {'annotation': _annotation}}, config)
            print(message.get('response')) if message.get('response') is not None else None

        else:
            print('Missing argument: Pass at least one of --description <DESCRIPTION> or --key <KEY>')


if __name__ == '__main__':
    main()