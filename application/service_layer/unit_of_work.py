import abc

from application.adapters.repository import SqlAlchemyRepository

class AbstractUnitOfWork(abc.ABC):
    def __init__(self):
        repo = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.repo = SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__()
        # Don't close the session because any lazily loaded data won't be available afterwards.
        # Flask-SQLAlchemy automatically removes sessions at the end of a request.

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

