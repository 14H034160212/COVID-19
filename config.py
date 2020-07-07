"""Flask configuration variables."""
from os import environ, path, getenv
from dotenv import load_dotenv

# Load environment variables from file .env, stored in this directory.
load_dotenv()


class Config:
    """Set Flask configuration from .env file."""

    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
