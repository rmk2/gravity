from datetime import datetime

from sqlalchemy import MetaData, Table, Column, VARCHAR, TIMESTAMP, ForeignKey

_metadata = MetaData()

project = Table(
    'project', _metadata,
    Column('project_id', VARCHAR(37), primary_key=True),
    Column('project_name', VARCHAR, nullable=False), Column('description', VARCHAR, nullable=True),
    Column('created', TIMESTAMP(timezone=True), nullable=False, default=datetime.now),
    Column('updated', TIMESTAMP(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now),
    Column('deleted', TIMESTAMP(timezone=True), nullable=True, default=None))

action = Table(
    'action', _metadata,
    Column('action_id', VARCHAR(37), primary_key=True),
    Column('action_name', VARCHAR, nullable=False), Column('description', VARCHAR, nullable=True),
    Column('created', TIMESTAMP(timezone=True), nullable=False, default=datetime.now),
    Column('updated', TIMESTAMP(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now),
    Column('deleted', TIMESTAMP(timezone=True), nullable=True, default=None))

worklog = Table(
    'worklog', _metadata,
    Column('project_id', VARCHAR(37), ForeignKey('project.project_id'), primary_key=True),
    Column('timestamp', TIMESTAMP(timezone=True), primary_key=True, default=datetime.now),
    Column('action_id', VARCHAR(37), ForeignKey('action.action_id'), nullable=False))
