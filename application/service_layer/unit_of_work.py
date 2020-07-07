from __future__ import annotations
import abc

from sqlalchemy.orm import scoped_session

from flask import _app_ctx_stack

from application.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    repo: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
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
        self.session = scoped_session(self.session_factory, scopefunc=_app_ctx_stack.__ident_func__)
        print('In unit of work')
        self.repo = repository.SqlAlchemyRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def close_current_session(self):
        if self.session is not None:
            self.session.close()
