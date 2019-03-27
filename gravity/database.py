import logging
from typing import Union

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, url

from gravity.config import BaseConfig
from gravity.model import _metadata


def get_engine(config: BaseConfig) -> Union[Engine, None]:
    backend = config.backend.driver
    engine = None

    if backend == 'sqlite':
        database_url = url.URL('sqlite', database=config.sqlite.database)
        engine = create_engine(database_url)

    elif backend == 'postgresql':
        database_url = url.URL(
            'postgresql+psycopg2',
            username=config.postgresql.username,
            password=config.postgresql.password,
            host=config.postgresql.hostname,
            port=config.postgresql.port,
            database=config.postgresql.database)
        engine = create_engine(database_url, client_encoding='utf-8', use_batch_mode=True)

    return engine


def drop(config: BaseConfig) -> None:
    try:
        engine = get_engine(config)
        assert engine is not None

        _metadata.drop_all(engine, checkfirst=True)

    except Exception as e:
        logging.error(str(e))
        raise e


def initialise(config: BaseConfig) -> None:
    try:
        engine = get_engine(config)
        assert engine is not None

        _metadata.create_all(engine, checkfirst=True)

    except Exception as e:
        logging.error(str(e))
        raise e


def prune(config: BaseConfig) -> None:
    try:
        engine = get_engine(config)
        assert engine is not None

        for table in _metadata.tables:
            _table = _metadata.tables[table]
            if _table.exists(engine) and 'deleted' in _table.c:
                engine.execute(_table.delete().where(_table.c.deleted.isnot(None)))

    except Exception as e:
        logging.error(str(e))
        raise e


def truncate(config: BaseConfig) -> None:
    try:
        engine = get_engine(config)
        assert engine is not None

        for table in _metadata.tables:
            _table = _metadata.tables[table]
            if _table.exists(engine):
                engine.execute(_table.delete())

    except Exception as e:
        logging.error(str(e))
        raise e