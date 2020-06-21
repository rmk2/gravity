import logging
import re
from datetime import timedelta
from typing import Dict, Union

from gravity.backend.writer import csv_writer, log_writer, postgresql_writer, sqlite_writer
from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import worklog


def _parse_modifier(modifier: str) -> Union[timedelta, None]:
    delta = None

    modifier = modifier.lower()
    _modifier = re.match(r'(?i)([+-]){1}([0-9]+)([smh]{1})', modifier)

    assert _modifier, f'Expression "{modifier}" does not match required format: [+-][0-9]+[smh]'
    assert len(_modifier.groups()) == 3, f'Could not extract all required options from expression "{modifier}"'

    operator, offset, unit = _modifier.groups()

    if unit == 's':
        delta = timedelta(seconds=int(f'{operator}{offset}'))
    elif unit == 'm':
        delta = timedelta(minutes=int(f'{operator}{offset}'))
    elif unit == 'h':
        delta = timedelta(hours=int(f'{operator}{offset}'))

    return delta


def modify_worklog(modifier: str, config: BaseConfig) -> str:
    try:
        engine = get_engine(config)

        delta = _parse_modifier(modifier)

        with engine.begin() as connection:
            select_query = worklog.select().order_by(worklog.c.worklog_id.desc()).limit(1)
            select_row = connection.execute(select_query).fetchone()

            _id = select_row['worklog_id']
            _timestamp = select_row['timestamp'] + delta

            connection.execute(worklog.update().where(worklog.c.worklog_id == _id).values(timestamp=_timestamp))

            message = f'Modified last worklog: {select_row["timestamp"]} → {_timestamp}'
            logging.info(f'Modified last worklog: {select_row["timestamp"]} → {_timestamp}')

            return message

    except Exception as e:
        logging.error(str(e))
        raise e


def remove_worklog(config: BaseConfig) -> str:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            select_query = worklog.select().order_by(worklog.c.worklog_id.desc()).limit(1)
            select_row = connection.execute(select_query).fetchone()

            _id = select_row['worklog_id']

            connection.execute(worklog.delete().where(worklog.c.worklog_id == _id))

            message = 'Removed last worklog'
            logging.info(message)

            return message

    except Exception as e:
        logging.error(str(e))
        raise e


def add_worklog(row: Dict[str, str], config: BaseConfig) -> None:
    try:
        if config.backend.driver == 'csv':
            csv_writer(row, config)
        elif config.backend.driver == 'log':
            log_writer(row, config)
        elif config.backend.driver == 'postgresql':
            postgresql_writer(row, config)
        elif config.backend.driver == 'sqlite':
            sqlite_writer(row, config)
        elif config.backend.driver == 'stdout':
            print(row)

    except Exception as e:
        logging.error(str(e))
        raise e
