import csv
import os
from typing import Dict, Any

from gravity.config import BaseConfig


def csv_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    with open(config.backend.output, mode='a', encoding='utf-8', newline='') as outfile:
        if config.csv.quote == 'all':
            _quoting = csv.QUOTE_ALL
        elif config.csv.quote == 'minimal':
            _quoting = csv.QUOTE_MINIMAL
        elif config.csv.quote == 'nonnumeric':
            _quoting = csv.QUOTE_NONNUMERIC
        elif config.csv.quote == 'none':
            _quoting = csv.QUOTE_NONE

        writer = csv.DictWriter(outfile, fieldnames=config.header, delimiter=config.csv.delimiter, quoting=_quoting)

        if os.stat(config.backend.output).st_size == 0:
            writer.writeheader()

        writer.writerow(row)


def log_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    pass


def postgresql_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    pass


def sqlite3_writer(row: Dict[str, Any], config: BaseConfig) -> None:
    pass
