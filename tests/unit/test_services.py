from typing import List

from adapters.repository import AbstractRepository
from domain.model import User, Article, Tag, make_comment, make_tag_association

from datetime import date

from service_layer import services

import pytest


@pytest.fixture
def fake_repo():
    return FakeRepository()

@pytest.fixture
def fake_session():
    return FakeSession()


class FakeRepository(AbstractRepository):
    def __init__(self):
        self._users, \
        self._articles,\
        self._comments,\
        self._tags = make_domain_model()

    def add_user(self, user: User):
        usernames = [user.username for user in self._users]
        if user.username not in usernames:
            self._users.append(user)

    def get_user(self, username) -> User:
        return next((user for user in self._users if user.username == username), None)

    def get_article(self, id):
        return next((article for article in self._articles if article.id == id), None)

    def get_articles(self, date: date = None) -> List[Article]:
        results = self._articles

        if date is None:
            results = [article for article in self.articles if article.date == date]
        return results

    def get_tags(self) -> List[Tag]:
        return self._tags

    def add_comment(self, comment):
        self._comments.append(comment)


class FakeSession():
    _committed = False

    def commit(self):
        self._committed = True

    def is_committed(self):
        return self._committed


def test_can_add_user(fake_repo, fake_session):
    username = 'Kelly'
    password = 'abcd1A23'

    services.add_user(username, password, fake_repo, fake_session)

    assert fake_repo.get_user(username).username == username

def test_cannot_add_user_with_existing_name(fake_repo, fake_session):
    username = 'Andrew'
    password = 'abcd1A23'

    with pytest.raises(services.NameNotUniqueException):
        services.add_user(username, password, fake_repo, fake_session)

def test_cannot_add_user_with_weak_password(fake_repo, fake_session):
    username = 'Kelly'
    password = 'abcd'

    with pytest.raises(services.PasswordException):
        services.add_user(username, password, fake_repo, fake_session)

def test_can_add_comment(fake_repo, fake_session):
    article_id = 1
    comment_text = 'COVID is here in NZ!'
    username = 'Cindy'

    # Call the service layer to add the comment.
    services.add_comment(article_id, comment_text, username, fake_repo, fake_session)

    # Retrieve the commented article from the repo.
    article = fake_repo.get_article(article_id)

    # Check that the article's comments include a comment with the new comment text.
    assert next((comment for comment in article.comments if comment.comment == comment_text), None) is not None

def test_cannot_add_comment_for_non_existent_article(fake_repo, fake_session):
    article_id = 4
    comment_text = 'COVID is here in NZ!'
    username = 'Cindy'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(services.NonExistentArticleException):
        services.add_comment(article_id, comment_text, username, fake_repo, fake_session)

def test_cannot_add_comment_for_non_comment_containing_profanity(fake_repo, fake_session):
    article_id = 1
    comment_text = 'Fuck you!'
    username = 'Cindy'

    # Call the service layer to attempt to add the comment.
    with pytest.raises(services.ProfanityException):
        services.add_comment(article_id, comment_text, username, fake_repo, fake_session)

def test_cannot_add_comment_for_non_existent_user():
    pass
    # Return to this later - need to consider too that only a logged in user can post a comment.

def make_domain_model():
    users = [
        User('Andrew', '1111'),
        User('Cindy', '1234')
    ]

    articles = [
        Article(
            date(2020, 2, 28),
            'Coronavirus: First case of virus in New Zealand',
            'The first case of coronavirus has been confirmed in New Zealand and authorities are now scrambling to track down people who may have come into contact with the patient.',
            'https://www.stuff.co.nz/national/health/119899280/ministry-of-health-gives-latest-update-on-novel-coronavirus',
            'https://resources.stuff.co.nz/content/dam/images/1/z/e/3/w/n/image.related.StuffLandscapeSixteenByNine.1240x700.1zduvk.png/1583369866749.jpg',
            1
        ),
        Article(
            date(2020, 3, 1),
            'Coronavirus: Jacinda Ardern urges calm as panicked shoppers empty supermarket shelves',
            'Panicked shoppers have forced the closure of a major food wholesaler on Saturday and today despite the Prime Minister urging New Zealanders to go about their daily lives after the countrys first case of coronavirus.',
            'https://www.nzherald.co.nz/nz/news/article.cfm?c_id=1&objectid=12312828',
            'https://www.nzherald.co.nz/resizer/CqBdC_bgpLVpthKbUUYSwL8UNLw=/620x465/smart/filters:quality(70)/arc-anglerfish-syd-prod-nzme.s3.amazonaws.com/public/I2F5HQJSBREH7P6YRXBVBKSP6A.jpg',
            2
        ),
        Article(
            date(2020, 3, 1),
            'Coronavirus: Rest homes and retirement villages plead for national aged care response plan',
            'The aged care sector is urgently asking health authorities to coordinate a national response to the coronavirus threat.',
            'https://www.nzherald.co.nz/nz/news/article.cfm?c_id=1&objectid=12313398',
            'https://www.nzherald.co.nz/resizer/6Nn7A2Yb4d_czHwT_bPQJaSuskk=/620x349/smart/filters:quality(70)/arc-anglerfish-syd-prod-nzme.s3.amazonaws.com/public/X46IV6IWXRC45PQBIJX6XPXHQM.jpg',
            3
        )
    ]

    comments = [
        make_comment('COVID in NZ!', users[0], articles[0]),
        make_comment('Loonies cleaning out the supermarkets', users[0], articles[1]),
        make_comment('Bad news', users[1], articles[0])
    ]

    tags = [
        Tag('News'),
        Tag('New Zealand'),
        Tag('World')
    ]

    make_tag_association(articles[0], tags[0])
    make_tag_association(articles[0], tags[1])
    make_tag_association(articles[1], tags[0])

    return users, articles, comments, tags
