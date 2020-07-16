from typing import List

from application.adapters.repository import AbstractRepository, MemoryRepository
from application.domain.model import User, Article, Tag, make_comment, make_tag_association

from datetime import date

from application.service_layer import services, unit_of_work

import pytest

from application.service_layer.services import AuthenticationException


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self, repo: MemoryRepository):
        self.repo = repo
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_can_add_user(in_memory_repo):
    new_username = 'jz'
    new_password = 'abcd1A23'

    uow = FakeUnitOfWork(in_memory_repo)
    services.add_user(new_username, new_password, uow)

    user_as_dict = services.get_user(new_username, uow)
    assert user_as_dict['username'] == new_username

    # Check that password has been encrypted.
    assert user_as_dict['password'].startswith('pbkdf2:sha256:')


def test_cannot_add_user_with_existing_name(in_memory_repo):
    username = 'thorke'
    password = 'abcd1A23'

    uow = FakeUnitOfWork(in_memory_repo)
    with pytest.raises(services.NameNotUniqueException):
        services.add_user(username, password, uow)


def test_authentication_with_valid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    uow = FakeUnitOfWork(in_memory_repo)
    services.add_user(new_username, new_password, uow)

    try:
        services.authenticate_user(new_username, new_password, uow)
    except AuthenticationException:
        assert False


def test_authentication_with_invalid_credentials(in_memory_repo):
    new_username = 'pmccartney'
    new_password = 'abcd1A23'

    uow = FakeUnitOfWork(in_memory_repo)
    services.add_user(new_username, new_password, uow)

    with pytest.raises(services.AuthenticationException):
        services.authenticate_user(new_username, '0987654321', uow)


def test_can_add_comment(in_memory_repo):
    article_id = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    username = 'fmercury'

    uow = FakeUnitOfWork(in_memory_repo)

    # Call the service layer to add the comment.
    services.add_comment(article_id, comment_text, username, uow)

    # Retrieve the comments for the article from the repository.
    comments_as_dict = services.get_comments_for_article(article_id, uow)

    # Check that the comments include a comment with the new comment text.
    assert next(
        (dictionary['comment_text'] for dictionary in comments_as_dict if dictionary['comment_text'] == comment_text),
        None) is not None


def test_cannot_add_comment_for_non_existent_article(in_memory_repo):
    article_id = 7
    comment_text = "COVID-19 - what's that?"
    username = 'fmercury'

    uow = FakeUnitOfWork(in_memory_repo)

    # Call the service layer to attempt to add the comment.
    with pytest.raises(services.NonExistentArticleException):
        services.add_comment(article_id, comment_text, username, uow)


def test_cannot_add_comment_by_unknown_user(in_memory_repo):
    article_id = 3
    comment_text = 'The loonies are stripping the supermarkets bare!'
    username = 'gmichael'

    uow = FakeUnitOfWork(in_memory_repo)

    # Call the service layer to attempt to add the comment.
    with pytest.raises(services.UnknownUserException):
        services.add_comment(article_id, comment_text, username, uow)


def test_can_get_article(in_memory_repo):
    article_id = 2

    uow = FakeUnitOfWork(in_memory_repo)

    article_as_dict = services.get_article(article_id, uow)

    assert article_as_dict['id'] == article_id
    assert article_as_dict['date'] == date.fromisoformat('2020-02-29')
    assert article_as_dict['title'] == 'Covid 19 coronavirus: US deaths double in two days, Trump says quarantine not necessary'
    #assert article_as_dict['first_para'] == 'US President Trump tweeted on Saturday night (US time) that he has asked the Centres for Disease Control and Prevention to issue a ""strong Travel Advisory"" but that a quarantine on the New York region"" will not be necessary.'
    assert article_as_dict['hyperlink'] == 'https://www.nzherald.co.nz/world/news/article.cfm?c_id=2&objectid=12320699'
    assert article_as_dict['image_hyperlink'] == 'https://www.nzherald.co.nz/resizer/159Vi4ELuH2fpLrv1SCwYLulzoM=/620x349/smart/filters:quality(70)/arc-anglerfish-syd-prod-nzme.s3.amazonaws.com/public/XQOAY2IY6ZEIZNSW2E3UMG2M4U.jpg'
    assert len(article_as_dict['comments']) == 0

    tag_names = [dictionary['name'] for dictionary in article_as_dict['tags']]
    assert 'World' in tag_names
    assert 'Health' in tag_names
    assert 'Politics' in tag_names


def test_cannot_get_article_with_non_existent_id(in_memory_repo):
    article_id = 7

    uow = FakeUnitOfWork(in_memory_repo)

    # Call the service layer to attempt to retrieve the Article.
    with pytest.raises(services.NonExistentArticleException):
        services.get_article(article_id, uow)


def test_get_first_article(in_memory_repo):
    uow = FakeUnitOfWork(in_memory_repo)

    article_as_dict = services.get_first_article(uow)

    assert article_as_dict['id'] == 1


def test_get_last_article(in_memory_repo):
    uow = FakeUnitOfWork(in_memory_repo)

    article_as_dict = services.get_last_article(uow)

    assert article_as_dict['id'] == 6


def test_get_articles_by_date_with_one_date(in_memory_repo):
    target_date = date.fromisoformat('2020-02-28')

    uow = FakeUnitOfWork(in_memory_repo)
    articles_as_dict, prev_date, next_date = services.get_articles_by_date(target_date, uow)

    assert len(articles_as_dict) == 1
    assert articles_as_dict[0]['id'] == 1

    assert prev_date is None
    assert next_date == date.fromisoformat('2020-02-29')


def _get_articles_by_date_with_multiple_dates(in_memory_repo):
    target_date = date.fromisoformat('2020-03-01')

    uow = FakeUnitOfWork(in_memory_repo)
    articles_as_dict, prev_date, next_date = services.get_articles_by_date(target_date, uow)

# Sort out the order on this. Don't rely on order. Try membershis, or geerating a list ansd then ordering it.
    assert len(articles_as_dict) == 3
    assert articles_as_dict[0]['id'] == 5
    assert articles_as_dict[1]['id'] == 4
    assert articles_as_dict[2]['id'] == 3

    assert prev_date == date.fromisoformat('2020-02-29')
    assert next_date == date.fromisoformat('2020-03-05')


def _get_articles_by_date_with_non_existent_date(in_memory_repo):
    uow = FakeUnitOfWork(in_memory_repo)
    # Should be an empty list.