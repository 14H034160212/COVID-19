from application.domain.model import User, make_comment, Article
from application.adapters.repository import AbstractRepository
from application.service_layer import unit_of_work

from better_profanity import profanity
from password_validator import PasswordValidator

from typing import List


# Can we get the UOW from the app context instead of passing it in as a parameter?
from application.service_layer.dto import articles_to_dto, article_to_dto, comments_to_dto, user_to_dto


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


def add_user(username: str, password: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # Check that the given username is available.
        user = uow.repo.get_user(username)
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
        uow.repo.add_user(user)
        uow.commit()


def get_user(username: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        user = uow.repo.get_user(username)
        if user is None:
            raise UnknownUserException

        return user_to_dto(user)


def add_comment(article_id: int, comment_text: str, username: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # Check comment for any profanities.
        #if profanity.contains_profanity(comment_text):
        #    raise ProfanityException

        # Check that the article exists.
        article = uow.repo.get_article(article_id)
        if article is None:
            raise NonExistentArticleException

        user = uow.repo.get_user(username)

        # Create comment.
        comment = make_comment(comment_text, user, article)

        # Update the repository.
        uow.repo.add_comment(comment)
        uow.commit()


def get_article(article_id: int, uow: unit_of_work.AbstractUnitOfWork):
    print('Services get_article() looking up article ', article_id)
    article = None
    with uow:
        article = uow.repo.get_article(article_id)
    return article_to_dto(article)


def get_first_article(uow: unit_of_work.AbstractUnitOfWork):
    article = None
    with uow:
        article = uow.repo.get_first_article()
        print('Fetched first article')
        if article is None:
            print('It is null')
    return article_to_dto(article)


def get_last_article(uow: unit_of_work.AbstractUnitOfWork):
    article = None
    with uow:
        article = uow.repo.get_last_article()
    return article_to_dto(article)


def get_articles_by_date(date, uow: unit_of_work.AbstractUnitOfWork):
    # Returns articles for the target date (empty if no matches), the date of the previous article (might be null), the date of the next article (might be null)
    with uow:
        articles = uow.repo.get_articles(target_date=date)

        articles_dto = list()
        prev_date = next_date = None

        if len(articles) > 0:
            prev_date = uow.repo.get_date_of_previous_article(articles[0])
            next_date = uow.repo.get_date_of_next_article(articles[0])

            # Convert Articles to dictionary form.
            articles_dto = articles_to_dto(articles)

        return articles_dto, prev_date, next_date


def get_comments_for_article(article_id, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        article = uow.repo.get_article(article_id)

        if article is None:
            raise NonExistentArticleException

        return comments_to_dto(article.comments)
