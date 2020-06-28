import abc
from application.domain.model import User

from sqlalchemy.orm.exc import NoResultFound


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add_user(self, user):
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, username):
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_users(self, username):
        raise NotImplementedError



class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session):
        self.session = session

    def add_user(self, user):
        self.session.add(user)

    def get_user(self, username):
        user = None

        try:
            user = self.session.query(User).filter_by(username=username).one()
        except NoResultFound:
            pass

        return user

    def get_all_users(self):
        return self.session.query(User).all()
