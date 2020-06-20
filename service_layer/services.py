from domain.model import User, make_comment
from adapters.repository import AbstractRepository

from better_profanity import profanity
from password_validator import PasswordValidator

from typing import List


class ProfanityException(Exception):
    pass


class NameNotUniqueException(Exception):
    pass


class PasswordException(Exception):
    pass


class NonExistentArticleException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_user(username: str, password: str, repo: AbstractRepository, session):
    # Check that the given username is available.
    user = repo.get_user(username)
    if user is not None:
        raise NameNotUniqueException

    # Check that the password is sufficient.
    schema = PasswordValidator()
    schema \
        .min(8) \
        .has().uppercase() \
        .has().lowercase() \
        .has().digits()
    if not schema.validate(password):
        raise PasswordException

    # Create and store the new User.
    user = User(username, password)
    repo.add_user(user)
    session.commit()

def get_user(username: str, repo: AbstractRepository, session):
    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    return {'username': user.username, 'password': user.password}


def add_comment(article_id: int, comment_text: str, username: str, repo: AbstractRepository, session):
    # Check comment for any profanities.
    if profanity.contains_profanity(comment_text):
        raise ProfanityException

    # Check that the article exists.
    article = repo.get_article(article_id)
    if article is None:
        raise NonExistentArticleException

    user = repo.get_user(username)

    # Create comment.
    comment = make_comment(comment_text, user, article)

    # Update the repository.
    repo.add_comment(comment)
    session.commit()

def get_comments_for_article(article_id, repo: AbstractRepository, session):
    article = repo.get_article(article_id)

    if article is None:
        raise NonExistentArticleException

    comments = list()
    for comment in article.comments:
        comments.append(
            {'author': comment.user.username,
             'article': comment.article.id,
             'comment': comment.comment,
             'timestamp': comment.timestamp.isoformat()
             }
        )
    return comments

