from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application import map_model_to_tables
from application.domain.model import Article

engine = create_engine('sqlite:///foo2.db')
map_model_to_tables()

session_factory = sessionmaker(engine)
session = session_factory()

# Insert user
#session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
#    {'username': 'Ian', 'password': 'pass'})
#rows = list(session.execute('SELECT id from users'))
#keys = tuple(row[0] for row in rows)
#session.commit()

articles = session.query(Article).all()
for a in articles:
    print(a)