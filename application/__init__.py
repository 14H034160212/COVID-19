"""Initialize Flask app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from application.adapters.orm import metadata, map_model_to_tables
from application.adapters.repository import SqlAlchemyRepository
from application.service_layer.unit_of_work import SqlAlchemyUnitOfWork

uow = None


def create_app():
    """Construct the core application."""
    # Create the Flask app object, and configure it.
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Create the SQLAlchemy object, and register it with the app.
    db = SQLAlchemy()
    db.init_app(app)

    # Create a unit-of-work to be used by the service_layer layer.
    global uow
    uow = SqlAlchemyUnitOfWork(db.create_session({}))

    # Build the application - these steps require an application context.
    with app.app_context():
        from .entrypoints import routes
        metadata.create_all(bind=db.get_engine())
        map_model_to_tables()

    return app

