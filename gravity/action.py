import json
import logging
import os.path
from datetime import datetime
from typing import Any, Dict, Sequence, Tuple, Union
from uuid import uuid4

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import action


def insert_actions(actions: Sequence[Dict[str, str]], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            connection.execute(action.insert(), actions)

    except Exception as e:
        logging.error(str(e))
        raise e


def add_actions(actions: Sequence[str]) -> Sequence[Dict[str, str]]:
    try:
        # Explicitly cast uuid4 objects to str, since sqlite doesn't take kindly to any other form
        # NB: postgresql has a native UUID datatype, but for portability's sake, we use TEXT instead
        _actions = [dict(action_id=str(uuid4()), action_name=action) for action in actions]

        return _actions

    except Exception as e:
        logging.error(str(e))
        raise e


def remove_actions(actions: Sequence[str], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            connection.execute(action.update()
                               .where(action.c.action_id.in_(actions))
                               .values(deleted=datetime.now()))

    except Exception as e:
        logging.error(str(e))
        raise e


def _get_actions(config: BaseConfig) -> Sequence[Union[Tuple[str, Any], None]]:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            result = connection.execute(action.select().where(action.c.deleted == None))

            return result.fetchall()

    except Exception as e:
        logging.error(str(e))
        raise e


def list_actions(actions: Sequence[Dict[str, str]]) -> None:
    for _action in actions:
        print(f'{_action["action_id"]}\t{_action["action_name"]}')


def export_actions(actions: Sequence[Dict[str, str]]) -> None:
    keys = ['action_id', 'action_name']

    _actions = [{k: v for k, v in p.items() if k in keys} for p in actions]

    print(json.dumps(_actions, indent=4))


def get_actions(config: BaseConfig) -> Sequence[Dict[str, Any]]:
    try:
        if config.backend.driver in ['sqlite', 'postgresql']:
            actions = _get_actions(config)
            actions = [{k: v for k, v in x.items() if k in ['action_id', 'action_name']} for x in actions]
        else:
            assert os.path.isfile(config.gravity.actions), f'Actions file "{config.gravity.actions}" does not exist'

            with open(config.gravity.actions, mode='r', encoding='utf-8') as infile:
                actions = json.load(infile)

        assert len(actions) > 0, 'No actions could be found'
        return actions

    except Exception as e:
        logging.error(str(e))
        raise e


def import_actions(filename: str) -> Sequence[Dict[str, str]]:
    try:
        assert os.path.isfile(filename), f'Actions file "{filename}" does not exist'

        with open(filename, mode='r', encoding='utf-8') as infile:
            _actions = json.load(infile)

        return _actions

    except Exception as e:
        logging.error(str(e))
        raise e
