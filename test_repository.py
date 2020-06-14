import model
import repository

import pytest

from datetime import datetime, date

def test_repository_can_add_a_user(session):
    user = model.User("Dave", "123456789")
    repo = repository.SqlAlchemyRepository(session)
    repo.add_user(user)
    session.commit()

    rows = list(session.execute(
        'SELECT username, password FROM users'
    ))
    assert rows == [("Dave","123456789")]

def test_repository_can_retrieve_a_user(populated_session):
    repo = repository.SqlAlchemyRepository(populated_session)
    user = repo.get_user("Andrew")

    assert user == model.User("Andrew", "1111")

def test_repository_can_retrieve_all_articles(populated_session):
    repo = repository.SqlAlchemyRepository(populated_session)
    articles = repo.get_articles()

    # Check that the query returned 3 Articles.
    assert len(articles) == 3

    # Check that each Article has the expected title.
    article_one = [article for article in articles if article.title == "Coronavirus: First case of virus in New Zealand"][0]
    article_two = [article for article in articles if article.title == "Coronavirus: Jacinda Ardern urges calm as panicked shoppers empty supermarket shelves"][0]
    article_three = [article for article in articles if article.title == "Coronavirus: Rest homes and retirement villages plead for national aged care response plan"][0]

    # Check that Articles are commented as expected.
    article_one_comment_one = [comment for comment in article_one.comments if comment.comment == "COVID in NZ!"][0]
    article_one_comment_two = [comment for comment in article_one.comments if comment.comment == "Bad news"][0]
    article_two_comment_one = [comment for comment in article_two.comments if comment.comment == "Loonies cleaning out the supermarkets"][0]
    assert article_one_comment_one.user.username == "Andrew"
    assert article_one_comment_two.user.username == "Cindy"
    assert article_two_comment_one.user.username == "Andrew"
    
    # Check that Articles are tagged as expected.
    assert article_one.is_tagged_by(model.Tag("News"))
    assert article_one.is_tagged_by(model.Tag("New Zealand"))
    assert article_two.is_tagged_by(model.Tag("News"))
    assert not article_three.is_tagged()

def test_repository_can_retrieve_articles_by_date(populated_session):
    repo = repository.SqlAlchemyRepository(populated_session)
    articles = repo.get_articles(date(2020, 3, 1))

    # Check that the query returned 2 Articles.
    assert len(articles) == 2

    # Check that the two Articles returned have dates matching the query date.
    article_two = [article for article in articles if article.date == date(2020, 3, 1)][0]
    article_three = [article for article in articles if article.date == date(2020, 3, 1)][0]

def test_repository_can_retrieve_tags(populated_session):
    repo = repository.SqlAlchemyRepository(populated_session)
    tags = repo.get_tags()

    assert len(tags) == 3
    tag_one = [tag for tag in tags if tag.tag_name == "News"][0]
    tag_two = [tag for tag in tags if tag.tag_name == "New Zealand"][0]
    tag_three = [tag for tag in tags if tag.tag_name == "World"][0]

    article_one_for_tag_one = [article for article in tag_one.tagged_articles if article.title == "Coronavirus: First case of virus in New Zealand"][0]
    article_one_for_tag_two = [article for article in tag_two.tagged_articles if article.title == "Coronavirus: First case of virus in New Zealand"][0]
    article_two_for_tag_one = [article for article in tag_one.tagged_articles if article.title == "Coronavirus: Jacinda Ardern urges calm as panicked shoppers empty supermarket shelves"][0]

    assert len(tag_three.tagged_articles) == 0




