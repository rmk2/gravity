from datetime import datetime
import json
import logging
from typing import Sequence, Union
from uuid import uuid4

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import action


def add_actions(actions: Sequence[str], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        _actions = [dict(action_id=uuid4(), action_name=action) for action in actions]

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
            result = connection.execute(action.select())

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
