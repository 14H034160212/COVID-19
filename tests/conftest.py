import pytest

from datetime import datetime as dt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from application import create_app
from application.adapters.orm import metadata, map_model_to_tables
from application.domain.model import User
from application.service_layer.unit_of_work import SqlAlchemyUnitOfWork

import application

app_instance = None


@pytest.fixture
def in_memory_db():
    clear_mappers()
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    clear_mappers()
    map_model_to_tables()
    return sessionmaker(bind=in_memory_db)
    #clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture
def uow(in_memory_db):
    clear_mappers()
    map_model_to_tables()
    session_factory = sessionmaker(bind=in_memory_db)
    uow = SqlAlchemyUnitOfWork(session_factory)
    return uow
    #clear_mappers()


@pytest.fixture
def app():
    print('creating app fixture')
    global app_instance

    if app_instance is None:
        app_instance = create_app()

    yield app_instance

    wipe_database(application.uow.session_factory)


@pytest.fixture
def client(app):
    return app.test_client()


def wipe_database(session_factory):
    with app_instance.app_context():
        session = session_factory()
        session.execute('DELETE from users')
        session.commit()
        session.close()


def insert_user(session):
    new_name = "Andrew"
    new_email = "andrew@police.govt.nz"
    new_bio = 'Educated at the University of Auckland ...'

    session.execute(
        'INSERT INTO users (username, email, created, bio, admin) VALUES (:username, :email, :created, :bio, :admin)',
        {'username': new_name, 'email': new_email, 'created': dt.now(), 'bio': new_bio, 'admin': False})
    row = session.execute('SELECT id from users where username = :username',
                          {'username': new_name}).fetchone()
    return row[0]


def create_user():
    user = User('Andrew', 'andrew@police.govt.nz', 'Educated at the University of Auckland ...')
    return user
