"""Initialize Flask app."""

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import NullPool

from application.adapters import memory_repository, database_repository
from application.adapters.orm import metadata, map_model_to_tables
from application.service_layer.services import add_user
from application.service_layer.unit_of_work import SqlAlchemyUnitOfWork, InMemoryUnitOfWork

from application.domain.model import User


uow = None


def create_app():
    """Construct the core application."""
    global uow
    # Create the Flask app object, and configure it.
    app = Flask(__name__)
    app.config.from_object('config.Config')

    print(app.config.items())

    if app.config['COVID_REPOSITORY'] == 'memory':
        print('In memory config')
        # Create the InMemoryUnitOfWork and MemoryRepository implementations for a memory-based repository.
        repo = memory_repository.MemoryRepository()
        uow = InMemoryUnitOfWork(repo)

        if not app.config['TESTING']:
            # Populate the repository with data.
            memory_repository.populate('application\\data', repo)

    elif app.config['COVID_REPOSITORY'] == 'database':
        print('database config')
        # Configure database.
        database_uri = app.config['SQLALCHEMY_DATABASE_URI']
        engine = create_engine(database_uri, connect_args={"check_same_thread": False}, poolclass=NullPool)

        if not app.config['TESTING'] and len(engine.table_names()) == 0:
            # Database doesn't contain any tables, so create and populate them.
            metadata.create_all(engine)
            database_repository.populate(engine, 'application\\data')

        # Create session factory.
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Generate mappings that map domain model classes to relational tables.
        map_model_to_tables()

        # Create the SqlAlchemyUnitOfWork object to be used by the service_layer layer.
        uow = SqlAlchemyUnitOfWork(session_factory)

    # Build the application - these steps require an application context.
    with app.app_context():
        from .entrypoints import routes

    # Register a tear-down method that will be called after each request has been processed.
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if isinstance(uow, SqlAlchemyUnitOfWork):
            uow.close_current_session()

    return app
