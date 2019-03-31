from datetime import datetime

from sqlalchemy import MetaData, Table, Column, INTEGER, VARCHAR, TIMESTAMP, ForeignKey

_metadata = MetaData()

project = Table(
    'project', _metadata,
    Column('project_id', VARCHAR(36), primary_key=True),
    Column('project_name', VARCHAR, nullable=False), Column('description', VARCHAR, nullable=True),
    Column('created', TIMESTAMP(timezone=True), nullable=False, default=datetime.now),
    Column('updated', TIMESTAMP(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now),
    Column('deleted', TIMESTAMP(timezone=True), nullable=True, default=None))

action = Table(
    'action', _metadata,
    Column('action_id', VARCHAR(36), primary_key=True),
    Column('action_name', VARCHAR, nullable=False), Column('description', VARCHAR, nullable=True),
    Column('created', TIMESTAMP(timezone=True), nullable=False, default=datetime.now),
    Column('updated', TIMESTAMP(timezone=True), nullable=False, default=datetime.now, onupdate=datetime.now),
    Column('deleted', TIMESTAMP(timezone=True), nullable=True, default=None))

worklog = Table(
    'worklog', _metadata,
    Column('worklog_id', INTEGER, primary_key=True),
    Column('project_id', VARCHAR(36), ForeignKey('project.project_id'), nullable=False),
    Column('action_id', VARCHAR(36), ForeignKey('action.action_id'), nullable=False),
    Column('timestamp', TIMESTAMP(timezone=True), nullable=False, default=datetime.now))
