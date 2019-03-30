import csv
import logging
import os
from typing import Dict, Any

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import worklog


def csv_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    try:
        with open(config.csv.output, mode='a+', encoding='utf-8', newline='') as outfile:
            if config.csv.quoting == 'all':
                _quoting = csv.QUOTE_ALL
            elif config.csv.quoting == 'minimal':
                _quoting = csv.QUOTE_MINIMAL
            elif config.csv.quoting == 'nonnumeric':
                _quoting = csv.QUOTE_NONNUMERIC
            elif config.csv.quoting == 'none':
                _quoting = csv.QUOTE_NONE

            writer = csv.DictWriter(
                outfile, fieldnames=config.gravity.columns, delimiter=config.csv.delimiter, quoting=_quoting)

            if os.stat(config.csv.output).st_size == 0:
                writer.writeheader()

            writer.writerow(row)
    except Exception as e:
        logging.error(str(e))
        raise e


def log_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    pass


def postgresql_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            connection.execute(worklog.insert(), row)

    except Exception as e:
        logging.error(str(e))
        raise e


def sqlite3_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    database = config.sqlite.database

    try:
        assert os.path.isfile(database), 'Database file {database} does not exist'
        engine = get_engine(config)

        with engine.begin() as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute(worklog.insert(), row)

    except Exception as e:
        logging.error(str(e))
        raise e
