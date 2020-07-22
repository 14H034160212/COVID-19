"""Initialize Flask app."""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from sqlalchemy.pool import NullPool

from application.adapters import memory_repository, database_repository
from application.adapters.orm import metadata, map_model_to_tables
from application.service_layer.services import add_user
from application.service_layer.unit_of_work import SqlAlchemyUnitOfWork, InMemoryUnitOfWork

from application.domain.model import User


uow = None


def create_app(test_config=None):
    """Construct the core application."""
    global uow

    # Create the Flask app object.
    app = Flask(__name__)

    # Configure the app from configuration-file settings.
    app.config.from_object('config.Config')
    data_path = 'application\\data'

    if test_config is not None:
        # Load test configuration, and override any configuration settings.
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    if app.config['REPOSITORY'] == 'memory':
        print('In memory config')
        # Create the InMemoryUnitOfWork and MemoryRepository implementations for a memory-based repository.
        repo = memory_repository.MemoryRepository()
        uow = InMemoryUnitOfWork(repo)
        memory_repository.populate(data_path, repo)
        print('Repo loaded with # articles ', repo.get_number_of_articles())

    elif app.config['REPOSITORY'] == 'database':
        print('database config')
        # Configure database.
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool)

        if app.config['TESTING']:
            clear_mappers()
            # Conditionally create database tables.
            metadata.create_all(engine)
            # Remove any existing data.
            for table in reversed(metadata.sorted_tables):
                engine.execute(table.delete())
            # Populate database tables.
            database_repository.populate(engine, data_path)

        elif len(engine.table_names()) == 0:
            # Database doesn't contain any tables. Create and populate the tables.
            metadata.create_all(engine)
            database_repository.populate(engine, data_path)

        # Create session factory.
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Generate mappings that map domain model classes to relational tables.
        map_model_to_tables()

        # Create the SqlAlchemyUnitOfWork object to be used by the service_layer layer.
        uow = SqlAlchemyUnitOfWork(session_factory)

    # Build the application - these steps require an application context.
    app.url_map._rules.clear()
    with app.app_context():
        print('Defined entry points')
        from .entrypoints import routes
        print('Map ', app.url_map)

        # Register a tear-down method that will be called after each request has been processed.
        @app.teardown_appcontext
        def shutdown_session(exception=None):
            if isinstance(uow, SqlAlchemyUnitOfWork):
                uow.close_current_session()

    return app
