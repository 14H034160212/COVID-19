import pytest

import datetime

from service_layer import unit_of_work
from domain import model


def insert_article(session):
    article_date = datetime.date(2020, 2, 28)
    session.execute(
        'INSERT INTO articles (date, title, first_para, hyperlink, image_hyperlink) VALUES '
        '(:date, "Coronavirus: First case of virus in New Zealand", '
        '"The first case of coronavirus has been confirmed in New Zealand  and authorities are now scrambling to track down people who may have come into contact with the patient.", '
        '"https://www.stuff.co.nz/national/health/119899280/ministry-of-health-gives-latest-update-on-novel-coronavirus", '
        '"https://resources.stuff.co.nz/content/dam/images/1/z/e/3/w/n/image.related.StuffLandscapeSixteenByNine.1240x700.1zduvk.png/1583369866749.jpg")',
        {'date': article_date.isoformat()}
    )
    row = session.execute('SELECT id from articles').fetchone()
    return row[0]

def insert_user(session, values=None):
    new_name = "Andrew"
    new_password = "1234"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                    {'username': new_name, 'password': new_password})
    row = session.execute('SELECT id from users where username = :username',
                          {'username': new_name}).fetchone()
    return row[0]

def get_comment_row(session, author_key: str):
    row = session.execute('SELECT article_id, comment FROM comments WHERE user_id=:author_key',
                          {'author_key': author_key}).fetchone()
    return row

def test_uow_can_retrieve_an_article_and_add_a_comment_to_it(session_factory):
    session = session_factory()
    article_key = insert_article(session)
    user_key = insert_user(session, ['Cindy', '1111'])
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        # Fetch Article and User.
        article = uow.repo.get_article(article_key)
        author = uow.repo.get_user('Cindy')

        # Create a new Comment, connecting it to the Article and User.
        comment = model.make_comment('The virus is here!', author, article)

        # Commit the changes.
        uow.commit()

    # Check that a Comment row has been added that links to the Article and User.
    comment_row = get_comment_row(session, user_key)
    assert comment_row[0] == article_key
    assert comment_row[1] == 'The virus is here!'

def test_uow_rolls_back_uncommited_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_article(uow.session)

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM articles'))
    assert rows == []


def test_uow_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_article(uow.session)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute('SELECT * FROM articles'))
    assert rows == []




