import pytest

from tests.conftest import insert_user, create_user


def test_can_retrieve_users_add_modify_a_user(uow):
    # Insert a User into the database and commit the insertion.
    session = uow.session_factory()
    insert_user(session)
    session.commit()

    # Using uow, retrieve the User, modify it and commit the change.
    with uow:
        users = uow.repo.get_all_users()
        assert len(users) == 1
        assert users[0].username == 'Andrew'

        users[0].email = 'andrew@auckland.ac.nz'

        uow.commit()

    # Using a new uow, check that the User has been updated.
    with uow:
        users = uow.repo.get_all_users()
        assert len(users) == 1
        assert users[0].username == 'Andrew'
        assert users[0].email == 'andrew@auckland.ac.nz'


def test_uow_rolls_back_uncommitted_work_by_default(uow):
    user = create_user()

    # Insert a new User, but don't commit it.
    with uow:
        uow.repo.add_user(user)

    # Using a new uow, check that no Users have been persisted.
    with uow:
        users = uow.repo.get_all_users()
        assert len(users) == 0


def test_uow_rolls_back_on_error(uow):
    class MyException(Exception):
        pass

    user = create_user()

    # Insert a new user, but throw an exception causing a rollback.
    with pytest.raises(MyException):
        with uow:
            uow.repo.add_user(user)
            raise MyException()

    # Using a new uow, check that no Users have been persisted.
    with uow:
        users = uow.repo.get_all_users()
        assert len(users) == 0
