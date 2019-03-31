import pytest

from gravity.config import BaseConfig


@pytest.fixture(scope='module')
def prepared_config() -> BaseConfig:
    """Prepare config values to be used in tests"""
    config = BaseConfig()
    config(['test'])

    return config
