from datetime import datetime
import json
import logging
from typing import Sequence, Union
from uuid import uuid4

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import project


def add_projects(projects: Sequence[str], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        _projects = [dict(project_id=uuid4(), project_name=project) for project in projects]

        with engine.begin() as connection:
            connection.execute(project.insert(), _projects)

    except Exception as e:
        logging.error(str(e))
        raise e


def remove_projects(projects: Sequence[str], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            connection.execute(project.update()
                               .where(project.c.project_id.in_(projects))
                               .values(deleted=datetime.now()))

    except Exception as e:
        logging.error(str(e))
        raise e


def _get_projects(config: BaseConfig) -> Sequence[Union[tuple, None]]:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            result = connection.execute(project.select())

            return result.fetchall()

    except Exception as e:
        logging.error(str(e))
        raise e


def list_projects(config: BaseConfig) -> None:
    projects = _get_projects(config)

    for _project in projects:
        print(f'{_project["project_id"]}\t{_project["project_name"]}')


def export_projects(config: BaseConfig) -> None:
    projects = _get_projects(config)
    keys = ['project_id', 'project_name']

    _projects = [{k: v for k, v in p.items() if k in keys} for p in projects]

    print(json.dumps(_projects, indent=4))
