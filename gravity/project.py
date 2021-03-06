import json
import logging
import os.path
from datetime import datetime
from typing import Any, Dict, Sequence, Tuple, Union
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


def _get_projects(config: BaseConfig) -> Sequence[Union[Tuple[str, Any], None]]:
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
    keys = ['project_id', 'project_name', 'project_key']

    _projects = [{k: v for k, v in p.items() if k in keys} for p in projects]

    print(json.dumps(_projects, indent=4))


def get_projects(config: BaseConfig) -> Sequence[Dict[str, Any]]:
    try:
        keys = ['project_id', 'project_name', 'project_key']

        if config.backend.driver in ['sqlite', 'postgresql']:
            projects = _get_projects(config)
            projects = [{k: v for k, v in x.items() if k in keys} for x in projects]
        else:
            assert os.path.isfile(config.gravity.projects), f'Projects file "{config.gravity.projects}" does not exist'

            with open(config.main.projects, mode='r', encoding='utf-8') as infile:
                projects = json.load(infile)

        assert len(projects) > 0, 'No projects could be found'
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


def annotate_project(annotation: Dict[str, str], config: BaseConfig) -> str:
    try:
        engine = get_engine(config)

        _projects = get_projects(config)

        _project = annotation.get('project')
        _description = annotation.get('description')
        _key = annotation.get('key')

        assert _project in [x.get('project_id') for x in _projects], f'Project {_project} does not exist'

        with engine.begin() as connection:
            connection.execute(project.update()
                               .where(project.c.project_id == _project)
                               .values(description=_description, project_key=_key))

        message = f'Annotated project {_project}'
        logging.info(message)

        return message

    except Exception as e:
        logging.error(str(e))
        raise e
