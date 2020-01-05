from datetime import datetime

from sqlalchemy.engine import Engine, url

import gravity.database
from gravity.model import project


def test_get_engine_sqlite(prepared_config) -> None:
    """Check that getting a SQLAlchemy engine for SQLite meets expectations"""
    config = prepared_config
    config.set_override(name='driver', override='sqlite', group='backend')
    config.set_override(name='database', override='test_database.sqlite', group='sqlite')

    engine = gravity.database.get_engine(config)

    engine_string_expected = 'sqlite:///test_database.sqlite'
    engine_url_expected = url.URL(drivername='sqlite', database='test_database.sqlite')

    assert isinstance(engine, Engine)
    assert engine.name == 'sqlite'
    assert engine.url == engine_url_expected
    assert str(engine.url) == engine_string_expected


def test_get_engine_postgresql(prepared_config) -> None:
    """Check that getting a SQLAlchemy engine for PostgreSQL meets expectations"""
    config = prepared_config
    config.set_override(name='driver', override='postgresql', group='backend')
    config.set_override(name='hostname', override='localhost', group='postgresql')
    config.set_override(name='port', override=1234, group='postgresql')
    config.set_override(name='username', override='pytest', group='postgresql')
    config.set_override(name='password', override='test', group='postgresql')
    config.set_override(name='database', override='db_test', group='postgresql')

    engine = gravity.database.get_engine(config)

    engine_string_expected = 'postgresql+psycopg2://pytest:test@localhost:1234/db_test'
    engine_url_expected = url.URL(
        drivername='postgresql+psycopg2',
        host='localhost',
        port=1234,
        username='pytest',
        password='test',
        database='db_test')

    assert isinstance(engine, Engine)
    assert engine.name == 'postgresql'
    assert engine.url == engine_url_expected
    assert str(engine.url) == engine_string_expected


def test_get_engine_none(prepared_config) -> None:
    """Check that getting an empty engine for non-database backends meets expectations"""
    config = prepared_config
    config.set_override(name='driver', override='csv', group='backend')

    engine = gravity.database.get_engine(config)

    assert engine is None


def test_initialise(test_database) -> None:
    """Check that initialising all database tables meets expectations"""
    config, engine, metadata = test_database

    gravity.database.initialise(config)

    for table in metadata.tables:
        _table = metadata.tables[table]

        assert engine.has_table(_table.name)


def test_drop(test_database) -> None:
    """Check that dropping all database tables meets expectations"""
    config, engine, metadata = test_database

    gravity.database.initialise(config)
    gravity.database.drop(config)

    for table in metadata.tables:
        _table = metadata.tables[table]

        assert not engine.has_table(_table.name)


def test_prune(test_database) -> None:
    """Check that deleting entries that have been marked for deletion meets expectations"""
    config, engine, metadata = test_database

    gravity.database.initialise(config)

    # Insert synthetic rows
    _now = datetime.now()
    _keys = [x.name for x in gravity.model.project.columns]
    _select = gravity.model.project.select()

    rows = [
        ['1', 'foo', 'foo description', 'FOO', _now, _now, _now],
        ['2', 'bar', 'bar description', 'BAR', _now, _now, None],
    ]
    rows = [dict(zip(_keys, x)) for x in rows]

    engine.execute(gravity.model.project.insert(), rows)

    # Check that rows have been inserted
    assert [dict(x) for x in engine.execute(_select).fetchall()] == rows

    # Prune rows marked for deletion
    gravity.database.prune(config)

    # Check that rows have been pruned
    assert [dict(x) for x in engine.execute(_select).fetchall()] == [x for x in rows if x['deleted'] is None]
    assert [dict(x) for x in engine.execute(_select).fetchall()] != [x for x in rows if x['deleted'] is not None]


def test_truncate(test_database) -> None:
    """Check that deleting all entries in a table without dropping the table meets expectations"""
    config, engine, metadata = test_database

    gravity.database.initialise(config)

    # Insert synthetic rows
    _now = datetime.now()
    _keys = [x.name for x in gravity.model.project.columns]
    _select = gravity.model.project.select()

    rows = [
        ['1', 'foo', 'foo description', 'FOO', _now, _now, _now],
        ['2', 'bar', 'bar description', 'BAR', _now, _now, None],
    ]
    rows = [dict(zip(_keys, x)) for x in rows]

    engine.execute(gravity.model.project.insert(), rows)

    # Check that rows have been inserted
    assert [dict(x) for x in engine.execute(_select).fetchall()] == rows

    # Truncate all rows
    gravity.database.truncate(config)

    # Check that all rows have been deleted
    assert len(engine.execute(_select).fetchall()) == 0
    assert engine.execute(_select).fetchall() == []

