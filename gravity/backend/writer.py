import csv
import logging
import os
from datetime import datetime
from typing import Dict, Any

from sqlalchemy import event

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import worklog


def csv_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    try:
        # Calculate number of rows in the CSV file to generate a sequential worklog_id
        # NB: Unlike database sequences, this id will be off by n if we delete n rows
        if os.path.isfile(config.csv.output):
            with open(config.csv.output, mode='rb') as infile:
                offset = sum(1 for _ in infile) - 1
        else:
            offset = 0

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
                outfile,
                fieldnames=[x.name for x in worklog.columns],
                delimiter=config.csv.delimiter,
                quoting=_quoting)

            if os.stat(config.csv.output).st_size == 0:
                writer.writeheader()

            _row = {'worklog_id': offset + 1, **row, 'timestamp': datetime.now().isoformat()}

            writer.writerow(_row)

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


def sqlite_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    database = config.sqlite.database

    try:
        assert os.path.isfile(database), 'Database file {database} does not exist'
        engine = get_engine(config)

        # Override pysqlite's default transaction behaviour
        # cf. https://docs.sqlalchemy.org/en/latest/dialects/sqlite.html
        @event.listens_for(engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # disable pysqlite's emitting of the BEGIN statement entirely.
            # also stops it from emitting COMMIT before any DDL.
            dbapi_connection.isolation_level = None
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        @event.listens_for(engine, "begin")
        def do_begin(connection):
            # emit our own BEGIN
            connection.execute("BEGIN EXCLUSIVE")

        with engine.begin() as connection:
            connection.execute(worklog.insert(), row)

    except Exception as e:
        logging.error(str(e))
        raise e
