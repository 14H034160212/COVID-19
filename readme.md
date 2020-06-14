# Covid-19 Web Application

Branch repository
-----------------
Application of the Repository pattern. Defines a Repository interface (port) for COVID-19 application. 
Defines an implementation (adapter) that uses the SQLAlchemy framework. Classical ORM mappings are used
to avoid coupling the COVID-19 domain model to the SQLAlchemy framework. Other implementations of the
Repository interface can be written to persist the domain model using different technologies.


Dependencies:
-------------
pytest - unit testing framework. Install using pip "pip install -U pytest".

SQLAlchemy - ORM framework. Install using pip "pip install SQLAlchemy".


Modules:
--------
conftest.py - contains pytest fixtures that are used by unit tests.

model.py - contains domain model classes for the COVID-19 application. This is essentially an object-
oriented model. Model classes include User (a person who can login and comment on news articles), 
Comment (a comment made by a logged in user), NewsArticle (a news article written by a news/media 
agency), Tag (a means to tag/classify news articles, e.g. "news", "new zealand", "world", "economy" 
etc.).

orm.py - uses SQLAlchemy to defines mappings between the domain model classes and relational database
tables. The model includes bidirectional associations between classes and the model maps to a 
database design that involves two one-to-many and one many-to-many relationships.

repository.py - defines a Repository interface for retrieving and persisting domain objects. Also
includes a Repository implementation that uses the SQLAlchemy ORM framework.

test_orm.py - a set of pytest unit tests for testing that the mappings defined in module orm.py are
correct and allow domain model instances to be retrieved from and persisted to a SQL database using
the SQLAlchemy ORM. When constructed correctly, the mappings allows for object associations to be
managed.

test_repository.py - a set of pytest unit tests for testing the Repository implementation that uses
the SQLAlchemy ORM for managing persistence of the domaim model.
