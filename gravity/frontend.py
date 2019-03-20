import curses
import curses.panel
from collections import namedtuple
from re import match
from typing import Sequence
import uuid

Project = namedtuple('project', ['id', 'name'])

projects = [
    Project(uuid.uuid4(), 'taod'),
    Project(uuid.uuid4(), 'AOK BW/ITSCARE'),
    Project(uuid.uuid4(), 'Boxine'),
    Project(uuid.uuid4(), 'Chronext'),
    Project(uuid.uuid4(), 'ERGO/ITERGO'),
    Project(uuid.uuid4(), 'NetCologne'),
    Project(uuid.uuid4(), 'Santander'),
    Project(uuid.uuid4(), 'SCHUFA')
]


def main(stdscr, projects: Sequence[str], column_limit: int = 2):
    _actions = {'S': 'Start', 'F': 'Finish', 'P': 'Pause', 'U': 'Unpause'}
    _controls = {'C': 'Commit', 'Q': 'Quit'}
    _projects = dict(enumerate(projects))

    # TODO: consider using a (scrollable) pad to avoid errors if we have
    # _many_ projects (or a very, very small window)
    height, _ = stdscr.getmaxyx()

    curses.curs_set(0)

    stdscr.addstr(0, 0, 'Actions: ')
    for idx, action in enumerate(_actions.values()):
        stdscr.addstr(idx + 1, 0, f'[{action[0:1].upper()}]{action[1:]} ')

    curses.savetty()

    while True:
        command = stdscr.getkey()
        command = command.upper() if match(r'[a-zA-Z]+', command) else None

        if command in _actions:
            action = _actions[command]
            break

    stdscr.clear()

    stdscr.addstr(0, 0, 'Projects:')
    for idx, project in _projects.items():
        y = idx if idx < height else idx % height
        x = 0 if idx < height else int(idx / height) * 50
        stdscr.addstr(y + 1, x, f'[{idx}] {project.name}')
        stdscr.clrtoeol()

    while True:
        key = stdscr.getstr(3).decode('utf-8')
        key = int(key) if match(r'\d+', key) else None

        if key in _projects:
            project = _projects[key]
            break

    stdscr.clear()

    stdscr.hline('=', 16)
    stdscr.addstr(1, 0, f'Command: {action}')
    stdscr.addstr(2, 0, f'Project: {project.name}')
    stdscr.move(3, 0)
    stdscr.hline('=', 16)

    stdscr.move(5, 0)
    for idx, control in enumerate(_controls.values()):
        stdscr.addstr(f'[{control[0:1].upper()}]{control[1:]} ')

    while True:
        select = stdscr.getkey()
        select = select.upper() if match(r'[a-zA-Z]+', select) else None

        if select == 'C':
            break
        elif select == 'Q':
            break


if __name__ == '__main__':
    curses.wrapper(main, projects)
