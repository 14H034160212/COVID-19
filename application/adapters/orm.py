from sqlalchemy import (
    Table, MetaData, Column, Integer, Boolean, String, DateTime
)
from sqlalchemy.orm import mapper

from application.domain import model

metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(64), unique=True, nullable=False),
    Column('email', String(255), unique=True, nullable=False),
    Column('created', DateTime, unique=False, nullable=False),
    Column('bio', String(1024), unique=False, nullable=True),
    Column('admin', Boolean, unique=False, nullable=False)
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        'username': users.c.username,
        'email': users.c.email,
        'created': users.c.created,
        'bio': users.c.bio,
        'admin': users.c.admin
    })
