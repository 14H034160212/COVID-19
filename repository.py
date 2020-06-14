import abc
import model

from datetime import date

class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add_user(self, user: model.User):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username) -> model.User:
        raise NotImplementedError

    @abc.abstractmethod
    def get_articles(self) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def get_articles(self, date:date) -> list:
        raise NotImplementedError

    @abc.abstractmethod
    def get_tags(self) -> list:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self._session = session

    def add_user(self, user: model.User):
        self._session.add(user)

    def get_user(self, username) -> model.User:
        return self._session.query(model.User).filter_by(_username=username).one()

    def get_articles(self, date: date = None) -> list:
        if date is None:
            return self._session.query(model.Article).all()
        else:
            print('Searching by date ', date)
            return self._session.query(model.Article).filter_by(_date=date).all()

    def get_tags(self) -> list:
        return self._session.query(model.Tag).all()