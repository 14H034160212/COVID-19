from werkzeug.security import generate_password_hash, check_password_hash

from application.domain.model import User, make_comment, Article
from application.adapters.repository import AbstractRepository
from application.service_layer import unit_of_work

# Can we get the UOW from the app context instead of passing it in as a parameter?
from application.service_layer.dto import articles_to_dto, article_to_dto, comments_to_dto, user_to_dto, tags_to_dto


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


class NonExistentArticleException(Exception):
    pass


def add_user(username: str, password: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # Check that the given username is available.
        user = uow.repo.get_user(username)
        if user is not None:
            raise NameNotUniqueException

        # Encrypt password so that the database doesn't store passwords 'in the clear'.
        password_hash = generate_password_hash(password)

        # Create and store the new User, with password encrypted.
        user = User(username, password_hash)
        uow.repo.add_user(user)
        uow.commit()


def get_user(username: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        user = uow.repo.get_user(username)
        if user is None:
            raise UnknownUserException

        return user_to_dto(user)


def authenticate_user(username: str, password: str, uow: unit_of_work.AbstractUnitOfWork):
    authenticated = False

    with uow:
        user = uow.repo.get_user(username)
        if user is not None:
            authenticated = check_password_hash(user.password, password)
        if not authenticated:
            raise AuthenticationException


def add_comment(article_id: int, comment_text: str, username: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        # Check that the article exists.
        article = uow.repo.get_article(article_id)
        if article is None:
            raise NonExistentArticleException

        user = uow.repo.get_user(username)
        if user is None:
            raise UnknownUserException

        # Create comment.
        comment = make_comment(comment_text, user, article)

        # Update the repository.
        uow.repo.add_comment(comment)
        uow.commit()


def get_article(article_id: int, uow: unit_of_work.AbstractUnitOfWork):
    article = None
    with uow:
        article = uow.repo.get_article(article_id)

        if article is None:
            raise NonExistentArticleException

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
        articles = uow.repo.get_articles_by_date(target_date=date)

        articles_dto = list()
        prev_date = next_date = None

        if len(articles) > 0:
            prev_date = uow.repo.get_date_of_previous_article(articles[0])
            next_date = uow.repo.get_date_of_next_article(articles[0])

            # Convert Articles to dictionary form.
            articles_dto = articles_to_dto(articles)

        return articles_dto, prev_date, next_date


def get_article_ids_for_tag(tag_name, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        article_ids = uow.repo.get_article_ids_for_tag(tag_name)

        return article_ids


def get_articles_by_id(id_list, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        articles = uow.repo.get_articles_by_id(id_list)

        # Convert Articles to dictionary form.
        articles_dto = articles_to_dto(articles)

        return articles_dto


def get_comments_for_article(article_id, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        article = uow.repo.get_article(article_id)

        if article is None:
            raise NonExistentArticleException

        return comments_to_dto(article.comments)


def get_tags(uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        tags = uow.repo.get_tags()

        return tags_to_dto(tags)