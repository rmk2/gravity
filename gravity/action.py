from datetime import datetime
import json
import logging
import os.path
from typing import Any, Dict, Sequence, Union
from uuid import uuid4

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import action


def add_actions(actions: Sequence[str], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        # Explicitly cast uuid4 objects to str, since sqlite doesn't take kindly to any other form
        # NB: postgresql has a native UUID datatype, but for portability's sake, we use TEXT instead
        _actions = [dict(action_id=str(uuid4()), action_name=action) for action in actions]

        with engine.begin() as connection:
            connection.execute(action.insert(), _actions)

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


def _get_actions(config: BaseConfig) -> Sequence[Union[tuple, None]]:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            result = connection.execute(action.select().where(action.c.deleted == None))

            return result.fetchall()

    except Exception as e:
        logging.error(str(e))
        raise e


def list_actions(config: BaseConfig) -> None:
    actions = _get_actions(config)

    for _action in actions:
        print(f'{_action["action_id"]}\t{_action["action_name"]}')


def export_actions(config: BaseConfig) -> None:
    actions = _get_actions(config)
    keys = ['action_id', 'action_name']

    _actions = [{k: v for k, v in p.items() if k in keys} for p in actions]

    print(json.dumps(_actions, indent=4))


def import_actions(config: BaseConfig) -> Sequence[Dict[str, Any]]:
    try:
        if config.backend.driver in ['sqlite', 'postgresql']:
            actions = _get_actions(config)
            actions = [{k: v for k, v in x.items() if k in ['action_id', 'action_name']} for x in actions]
        else:
            assert os.path.isfile(config.gravity.actions), f'Actions file "{config.gravity.actions}" does not exist'

            with open(config.gravity.actions, mode='r', encoding='utf-8') as infile:
                actions = json.load(infile)

        assert len(actions) > 0, 'No actions could be imported'
        return actions

    except Exception as e:
        logging.error(str(e))
        raise e
