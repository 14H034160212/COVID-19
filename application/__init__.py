"""Initialize Flask app."""
import os

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import SingletonThreadPool, NullPool

from application.adapters.orm import metadata, map_model_to_tables
from application.adapters.repository import SqlAlchemyRepository
from application.service_layer.services import add_user
from application.service_layer.unit_of_work import SqlAlchemyUnitOfWork

from application.domain.model import User

uow = None


def create_app():
    """Construct the core application."""
    # Create the Flask app object, and configure it.
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Configure database.
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(database_url, connect_args={"check_same_thread": False}, poolclass=NullPool)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    map_model_to_tables()

    # Create a unit-of-work to be used by the service_layer layer.
    global uow
    uow = SqlAlchemyUnitOfWork(session_factory)

    # Build the application - these steps require an application context.
    with app.app_context():
        from .entrypoints import routes

    # Register a tear-down method that will be called after each request has been processed.
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        uow.close_current_session()

    return app
