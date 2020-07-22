import os
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from application import InMemoryUnitOfWork, create_app
from application.adapters import memory_repository, database_repository
from application.adapters.orm import metadata, map_model_to_tables
from application.adapters.memory_repository import MemoryRepository

TEST_DATABASE_URI = 'sqlite://'
TEST_DATA_PATH = os.path.abspath(os.path.join('..', 'test_data'))


#my_app = None


@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    memory_repository.populate(TEST_DATA_PATH, repo)
    return repo


@pytest.fixture
def in_memory_uow():
    repo = MemoryRepository()
    memory_repository.populate(TEST_DATA_PATH, repo)
    return InMemoryUnitOfWork(repo)


@pytest.fixture
def session():
    engine = create_engine(TEST_DATABASE_URI)
    metadata.create_all(engine)
    database_repository.populate(engine, TEST_DATA_PATH)
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    yield session_factory()
    metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture
def session_factory():
    engine = create_engine(TEST_DATABASE_URI)
    metadata.create_all(engine)
    database_repository.populate(engine, TEST_DATA_PATH)
    map_model_to_tables()
    session_factory = sessionmaker(bind=engine)
    yield session_factory
    metadata.drop_all(engine)
    clear_mappers()


@pytest.fixture
def app():
    print('creating app fixture')
    app = create_app({
        'TESTING': True,
        'SQL_ALCHEMY_DATABASE_URI': TEST_DATABASE_URI,
        'REPOSITORY': 'database',
        'TEST_DATA_PATH': TEST_DATA_PATH
    })
    return app


@pytest.fixture
def app_mem():
    #global my_app

    my_app = create_app({
        'TESTING': True,
        'REPOSITORY': 'memory',
        'TEST_DATA_PATH': TEST_DATA_PATH
    })
    return my_app


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,
        'REPOSITORY': 'memory',
        'TEST_DATA_PATH': TEST_DATA_PATH
    })
    test_client = my_app.test_client()

    ctx = my_app.app_context()
    ctx.push()
    yield my_app.test_client()

    ctx.pop()