import pytest

from application.adapters.repository import AbstractRepository

from application.service_layer.unit_of_work import AbstractUnitOfWork
from application.service_layer import services

from application.domain.model import User


class FakeRepository(AbstractRepository):

    def __init__(self):
        self.users = [
            User('Andrew', 'andrew@gmail.com'),
            User('Cindy', 'cindy@gmail.com')
        ]

    def add_user(self, user):
        usernames = [user.username for user in self.users]
        if user.username not in usernames:
            self.users.append(user)

    def get_user(self, username):
        return next((user for user in self.users if user.username == username), None)

    def get_all_users(self, username):
        return self.users


class FakeUnitOfWork(AbstractUnitOfWork):

    def __init__(self):
        self.repo = FakeRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


def test_can_add_user():
    print('Testing')
    new_username = 'Kelly'
    new_email = 'Kelly@gmail.com'

    uow = FakeUnitOfWork()
    services.add_user(new_username, new_email, uow)

    items = services.get_user(new_username, uow)
    assert items['username'] == new_username
    assert items['email'] == new_email


def test_cannot_add_user_with_existing_name():
    username = 'Andrew'
    email = 'andrew@gmail.com'

    uow = FakeUnitOfWork()
    with pytest.raises(services.NameNotUniqueException):
        services.add_user(username, email, uow)
