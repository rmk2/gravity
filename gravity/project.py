from datetime import datetime
import json
import logging
import os.path
from typing import Any, Dict, Sequence, Union
from uuid import uuid4

from gravity.config import BaseConfig
from gravity.database import get_engine
from gravity.model import project


def insert_projects(projects: Sequence[Dict[str, str]], config: BaseConfig) -> None:
    try:
        engine = get_engine(config)

        with engine.begin() as connection:
            connection.execute(project.insert(), projects)

    except Exception as e:
        logging.error(str(e))
        raise e


def add_projects(projects: Sequence[str]) -> Sequence[Dict[str, str]]:
    try:
        # Explicitly cast uuid4 objects to str, since sqlite doesn't take kindly to any other form
        # NB: postgresql has a native UUID datatype, but for portability's sake, we use TEXT instead
        _projects = [dict(project_id=str(uuid4()), project_name=project) for project in projects]

        return _projects

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
            result = connection.execute(project.select().where(project.c.deleted == None))

            return result.fetchall()

    except Exception as e:
        logging.error(str(e))
        raise e


def list_projects(projects: Sequence[Dict[str, str]]) -> None:
    for _project in projects:
        print(f'{_project["project_id"]}\t{_project["project_name"]}')


def export_projects(projects: Sequence[Dict[str, str]]) -> None:
    keys = ['project_id', 'project_name']

    _projects = [{k: v for k, v in p.items() if k in keys} for p in projects]

    print(json.dumps(_projects, indent=4))


def get_projects(config: BaseConfig) -> Sequence[Dict[str, Any]]:
    try:
        if config.backend.driver in ['sqlite', 'postgresql']:
            projects = _get_projects(config)
            projects = [{k: v for k, v in x.items() if k in ['project_id', 'project_name']} for x in projects]
        else:
            assert os.path.isfile(config.gravity.projects), f'Projects file "{config.gravity.projects}" does not exist'

            with open(config.gravity.projects, mode='r', encoding='utf-8') as infile:
                projects = json.load(infile)

        assert len(projects) > 0, 'No projects could be imported'
        return projects

    except Exception as e:
        logging.error(str(e))
        raise e


def import_projects(filename: str) -> Sequence[Dict[str, str]]:
    try:
        assert os.path.isfile(filename), f'Projects file "{filename}" does not exist'

        with open(filename, mode='r', encoding='utf-8') as infile:
            _projects = json.load(infile)

        return _projects

    except Exception as e:
        logging.error(str(e))
        raise e

