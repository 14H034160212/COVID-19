import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from datetime import date, datetime

from orm import metadata, map_model_to_tables

@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine

@pytest.fixture
def session(in_memory_db):
    map_model_to_tables()
    yield sessionmaker(bind=in_memory_db)()

    # Teardown code.
    clear_mappers()

@pytest.fixture
def populated_session(in_memory_db):
    map_model_to_tables()
    session = sessionmaker(bind=in_memory_db)()
    insert_data(session)
    yield session

    # Teardown code.
    clear_mappers()

def insert_data(session):
    print('Populating the database')
    # Insert data into the database tables as follows:
    # - 3 Articles
    # - 3 Tags - News, NZ, World
    # - 2 Users - Andrew and Cindy
    # - 3 Comments
    # Associations:
    # - Article 1 has 2 Comments, one by Andrew and the other by Cindy. Article 2 has one 
    #   Comment by Andrew. Article 3 has no comments.
    # - Article 1 is tagged with News and NZ. Article 2 is tagged with News. Article 3 has
    #   no tags.
    session.execute(
        'INSERT INTO articles (date, title, first_para, hyperlink, image_hyperlink) VALUES '
        '(:date, "Coronavirus: First case of virus in New Zealand", ' 
        '"The first case of coronavirus has been confirmed in New Zealand  and authorities are now scrambling to track down people who may have come into contact with the patient.", '
        '"https://www.stuff.co.nz/national/health/119899280/ministry-of-health-gives-latest-update-on-novel-coronavirus", '
        '"https://resources.stuff.co.nz/content/dam/images/1/z/e/3/w/n/image.related.StuffLandscapeSixteenByNine.1240x700.1zduvk.png/1583369866749.jpg")',
        dict(date = date(2020, 2, 28).isoformat())
    )
    session.execute(
        'INSERT INTO articles (date, title, first_para, hyperlink, image_hyperlink) VALUES '
        '(:date, "Coronavirus: Jacinda Ardern urges calm as panicked shoppers empty supermarket shelves", ' 
        '"Panicked shoppers have forced the closure of a major food wholesaler on Saturday and today despite the Prime Minister urging New Zealanders to go about their daily lives after the countrys first case of coronavirus.", '
        '"https://www.nzherald.co.nz/nz/news/article.cfm?c_id=1&objectid=12312828", '
        '"https://www.nzherald.co.nz/resizer/CqBdC_bgpLVpthKbUUYSwL8UNLw=/620x465/smart/filters:quality(70)/arc-anglerfish-syd-prod-nzme.s3.amazonaws.com/public/I2F5HQJSBREH7P6YRXBVBKSP6A.jpg")',
        dict(date = date(2020, 3, 1).isoformat())
    )
    session.execute(
        'INSERT INTO articles (date, title, first_para, hyperlink, image_hyperlink) VALUES '
        '(:date, "Coronavirus: Rest homes and retirement villages plead for national aged care response plan", ' 
        '"The aged care sector is urgently asking health authorities to coordinate a national response to the coronavirus threat.", '
        '"https://www.nzherald.co.nz/nz/news/article.cfm?c_id=1&objectid=12313398", '
        '"https://www.nzherald.co.nz/resizer/6Nn7A2Yb4d_czHwT_bPQJaSuskk=/620x349/smart/filters:quality(70)/arc-anglerfish-syd-prod-nzme.s3.amazonaws.com/public/X46IV6IWXRC45PQBIJX6XPXHQM.jpg")',
        dict(date = date(2020, 3, 1).isoformat())
    )
    rows = list(session.execute('SELECT id from articles'))
    article_keys = [row[0] for row in rows]

    session.execute(
        'INSERT INTO tags (name) VALUES ("News"), ("New Zealand"), ("World")'
    )
    rows = list(session.execute('SELECT id from tags'))
    tag_keys = [row[0] for row in rows]

    session.execute(
        'INSERT INTO users (username, password) VALUES '
        '("Andrew", "1111"), '
        '("Cindy", "1234")'
    )
    rows = list(session.execute('SELECT id from users'))
    user_keys = [row[0] for row in rows]

    session.execute(
        'INSERT INTO comments (user_id, article_id, comment, timestamp) VALUES '
        '(:user_one, :article_one, "COVID in NZ!", :timestamp_one), '
        '(:user_one, :article_two, "Loonies cleaning out the supermarkets", :timestamp_two), '
        '(:user_two, :article_one, "Bad news", :timestamp_three) ',
        dict(
            user_one = user_keys[0],
            user_two = user_keys[1],
            article_one = article_keys[0],
            article_two = article_keys[1],
            timestamp_one = datetime(2020, 2, 28, 18, 12).strftime('%Y-%m-%d %H:%M:%S'),
            timestamp_two = datetime(2020, 3, 1, 19, 1).strftime('%Y-%m-%d %H:%M:%S'),
            timestamp_three = datetime(2020, 3, 1, 7, 19).strftime('%Y-%m-%d %H:%M:%S')
        )
    )

    session.execute(
        'INSERT INTO article_tags (article_id, tag_id) VALUES '
        '(:article_one, :tag_news), '
        '(:article_one, :tag_nz), '
        '(:article_two, :tag_news) ',
        dict(
            article_one = article_keys[0],
            article_two = article_keys[1],
            tag_news = tag_keys[0],
            tag_nz = tag_keys[1]
        )
    )

