import curses
import curses.panel
from re import match

from gravity.action import import_actions
from gravity.client import send_message
from gravity.config import BaseConfig
from gravity.project import import_projects


def _curses_main(stdscr, config: BaseConfig, column_limit: int = 4):
    def _transform_actions(config: BaseConfig):
        actions = {}
        used_commands = set()

        for action in import_actions(config):
            _id = action['action_id']
            _name = action['action_name']
            _keys = [x.upper() for x in _name if x.upper() not in used_commands]

            if len(_keys) > 0:
                _command = _keys[0]
                used_commands.add(_command)
            else:
                raise ValueError(f'Could not find unique letter in action {_name} to use as command key')

            actions[_command] = {'action_id': _id, 'action_name': _name}

        return actions

    _actions = _transform_actions(config)
    _controls = {'C': 'Commit', 'N': 'Next', 'R': 'Reset', 'Q': 'Quit'}
    _projects = dict(enumerate(sorted(import_projects(config), key=lambda x: x['project_name'])))

    # TODO: consider using a (scrollable) pad to avoid errors if we have
    # _many_ projects (or a very, very small window)
    height, _ = stdscr.getmaxyx()

    curses.curs_set(0)

    stdscr.addstr(0, 0, 'Actions: ')
    for idx, action in enumerate(_actions.items()):
        _command, _action = action
        y = idx if idx < height - 2 else idx % (height - 1)
        x = 0 if idx < height - 2 else int(idx / (height - 1)) * 50
        stdscr.addstr(y + 1, x, f'[{_command}] {_action["action_name"].capitalize()}')

    while True:
        command = stdscr.getkey()
        command = command.upper() if match(r'[a-zA-Z]+', command) else None

        if command in _actions.keys():
            action = _actions[command]
            break

    stdscr.clear()

    stdscr.addstr(0, 0, 'Projects:')
    for idx, project in _projects.items():
        y = idx if idx < height - 2 else idx % (height - 1)
        x = 0 if idx < height - 2 else int(idx / (height - 1)) * 50
        stdscr.addstr(y + 1, x, f'[{idx}] {project["project_name"]}')
        stdscr.clrtoeol()

    while True:
        key = stdscr.getstr(3).decode('utf-8')
        key = int(key) if match(r'\d+', key) else None

        if key in _projects:
            project = _projects[key]
            break

    stdscr.clear()

    stdscr.hline('=', 16)
    stdscr.addstr(1, 0, f'Command: {action["action_name"].capitalize()}')
    stdscr.addstr(2, 0, f'Project: {project["project_name"]}')
    stdscr.move(3, 0)
    stdscr.hline('=', 16)

    stdscr.move(5, 0)
    for idx, control in enumerate(_controls.values()):
        stdscr.addstr(f'[{control[0:1].upper()}]{control[1:]} ')

    while True:
        select = stdscr.getkey()
        select = select.upper() if match(r'[a-zA-Z]+', select) else None

        if select == 'C':
            message = {'project_id': project['project_id'], 'action_id': action['action_id']}
            send_message(message, config)
            exit(0)
        elif select == 'N':
            message = {'project_id': project['project_id'], 'action_id': action['action_id']}
            send_message(message, config)
            stdscr.clear()
            _curses_main(stdscr, config, column_limit)
        elif select == 'R':
            stdscr.clear()
            _curses_main(stdscr, config, column_limit)
        elif select == 'Q':
            exit(0)


def run_curses(config: BaseConfig):
    try:
        curses.wrapper(_curses_main, config)
    except KeyboardInterrupt:
        exit(1)


if __name__ == '__main__':
    raise NotImplementedError('Frontend cannot be called directly')
