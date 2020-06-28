# Sample project

## Installation

**Installation via `requirements.txt`**:

```shell
$ cd project-pattern
$ py -3 -m venv venv
$ venv\Scripts\activate
$ pip install -r requirements.txt
$ flask run
```

## Usage

Replace the values in **.env** with your values:

* `FLASK_APP`: Entry point of your application (should be `wsgi.py`).
* `FLASK_ENV`: The environment to run your app in (either `development` or `production`).
* `SECRET_KEY`: Randomly generated string of characters used to encrypt your app's data.
* `SQLALCHEMY_DATABASE_URI`: SQLAlchemy connection URI to a SQL database.

*Remember never to commit secrets saved in .env files to Github.*

-----

## Description

This project involves a very simple app that maintains information about users. It stores user data in a SQLite database which is abstracted using SQLAlchemy's ORM. The project originally came from https://hackersandslackers.com/your-first-flask-application.

The project has been developed to demonstrate:

* Application of the Repository, Service Layer and Unit of Work arhictecture patterns.
* Factory pattern for creating a Flask object.
* Unit testing, integration testing and end-to-end testing. 

The project serves as a template for other Flask/SqlAlchemy projects.



