import abc
from typing import List

from sqlalchemy import desc, asc

from application.domain.model import User, Article, Tag, Comment

from datetime import date


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: User):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username) -> User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_article(self, id: int) -> Article:
        raise NotImplementedError

    @abc.abstractmethod
    def get_first_article(self) -> Article:
        raise NotImplementedError

    @abc.abstractmethod
    def get_last_article(self) -> Article:
        raise NotImplementedError

    @abc.abstractmethod
    def get_articles(self, target_date: date = None, target_tag: str = None) -> List[Article]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_number_of_articles(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_date_of_previous_article(self, article: Article):
        raise NotImplementedError

    @abc.abstractmethod
    def get_date_of_next_article(self, article: Article):
        raise NotImplementedError

    @abc.abstractmethod
    def get_articles_by_id(self, id_list):
        raise NotImplementedError

    @abc.abstractmethod
    def get_article_ids_for_tag(self, tag_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def get_tags(self) -> List[Tag]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_comment(self, comment: Comment):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self._session = session

    def add_user(self, user: User):
        self._session.add(user)

    def get_user(self, username) -> User:
        user = None
        try:
            user = self._session.query(User).filter_by(_username=username).one()
        except:  # What's the type of Error?
            pass

        return user

    def get_article(self, id: int) -> Article:
        article = None
        try:
            #article = self._session.query(Article).filter_by(_id=id).one()
            article = self._session.query(Article).filter(Article._id==id).one()
        except:  # what's the error type?
            print('Got ORM exception, was asked for id ', id)

        return article

    def get_articles(self, target_date: date = None, target_tag: str = None) -> List[Article]:
        print('Type of date: ', type(target_date), target_date)
        if target_date is None:
            print('Returning ALL articles')
            return self._session.query(Article).all()
        elif target_date is not None:
            print('Returning articles by date')
            return self._session.query(Article).filter(Article._date == target_date).all()
            # This returns an empty list if there are no matches
        elif target_tag is not None:
            # come back to this:
            # 1. should we combine dates and tags?
            # 2. for tags, we need a more sophisticated query, or use a generator or similar to retrieve all articles and prune those with matching tags.
            return None

    def get_number_of_articles(self):
        return self._session.query(Article).count()

    def get_first_article(self):
        return self._session.query(Article).first()

    def get_last_article(self):
        return self._session.query(Article).order_by(desc(Article._id)).first()

    def get_articles_by_id(self, id_list):
        return self._session.query(Article).filter(Article._id.in_(id_list)).all()

    def get_article_ids_for_tag(self, tag_name: str):
        # Use native SQL to retrieve article ids, since there is no mapped class for the article_tags table.
        row = self._session.execute('SELECT id FROM tags WHERE name = :tag_name', {'tag_name': tag_name}).fetchone()
        tag_id = row[0]

        article_ids = self._session.execute(
            'SELECT article_id FROM article_tags WHERE tag_id = :tag_id ORDER BY article_id ASC',
            {'tag_id': tag_id}
        ).fetchall()
        article_ids = [id[0] for id in article_ids]

        return article_ids

    def get_date_of_previous_article(self, article: Article):
        """ Returns the closest previous date of an article to the argument. If there are no previous articles,
        this method returns None."""
        result = None
        prev = self._session.query(Article).filter(Article._date < article.date).order_by(desc(Article._date)).first()

        if prev is not None:
            result = prev.date
        return result

    def get_date_of_next_article(self, article: Article):
        result = None
        next = self._session.query(Article).filter(Article._date > article.date).order_by(asc(Article._date)).first()

        if next is not None:
            result = next.date
        return result

    def get_tags(self) -> List[Tag]:
        return self._session.query(Tag).all()

    def add_comment(self, comment: Comment):
        self._session.add(comment)
