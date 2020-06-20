import abc
from typing import List

from domain.model import User, Article, Tag, Comment

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
    def get_articles(self, date: date) -> List[Article]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_tags(self) -> List[Tag]:
        raise NotImplementedError

    @abc.abstractmethod
    def add_comment(selfself, comment: Comment):
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
            article = Article.query.get(id)
        except:  # what's the error type?
            pass

    def get_articles(self, date: date = None) -> List[Article]:
        if date is None:
            return self._session.query(Article).all()
        else:
            print('Searching by date ', date)
            return self._session.query(Article).filter_by(_date=date).all()

    def get_tags(self) -> List[Tag]:
        return self._session.query(Tag).all()

    def add_comment(self, comment: Comment):
        self.session.add(comment)
