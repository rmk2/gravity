from sqlalchemy.engine import Engine, url

import gravity.database


def test_get_engine_sqlite(prepared_config) -> None:
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
    config = prepared_config
    config.set_override(name='driver', override='csv', group='backend')

    engine = gravity.database.get_engine(config)

    assert engine is None


def test_drop() -> None:
    pass


def test_initialise() -> None:
    pass


def test_prune() -> None:
    pass


def test_truncate() -> None:
    pass
