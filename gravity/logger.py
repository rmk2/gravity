import logging

from gravity.config import BaseConfig

_log_levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


def initialise_logging(config: BaseConfig):
    handlers = []
    fh = logging.FileHandler(config.log.file, 'a', 'utf-8')
    ch = logging.StreamHandler()

    if 'file' in config.log.targets:
        handlers.append(fh)

    if 'console' in config.log.targets:
        handlers.append(ch)

    logging_conf = {
        'level': _log_levels[config.log.level],
        'handlers': handlers,
        'format': '%(asctime)s %(levelname)s %(module)s: %(message)s'
    }

    logging.basicConfig(**logging_conf)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.captureWarnings(True)
