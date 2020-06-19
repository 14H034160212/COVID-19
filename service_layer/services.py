from domain.model import User, make_comment
from adapters.repository import AbstractRepository

from better_profanity import profanity
from password_validator import PasswordValidator


class ProfanityException(Exception):
    pass


class NameNotUniqueException(Exception):
    pass


class PasswordException(Exception):
    pass


class NonExistentArticleException(Exception):
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
