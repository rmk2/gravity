import os.path
from typing import Tuple

import pytest
from sqlalchemy import MetaData
from sqlalchemy.engine import Engine

from gravity.config import BaseConfig
from gravity.database import _metadata, get_engine


@pytest.fixture(scope='module')
def prepared_config() -> BaseConfig:
    """Prepare config values to be used in tests"""
    config = BaseConfig()
    config(['test'])

    return config


@pytest.fixture(scope='function')
def test_database(prepared_config, tmpdir) -> Tuple[BaseConfig, Engine, MetaData]:
    """Prepare a test database"""
    _config = prepared_config

    _config.set_override(name='driver', override='sqlite', group='backend')
    _config.set_override(name='database', override=os.path.join(tmpdir, 'test_database.sqlite'), group='sqlite')

    _engine = get_engine(_config)

    yield _config, _engine, _metadata
