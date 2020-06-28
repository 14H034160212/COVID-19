from datetime import datetime as dt

from application.domain.model import User


class NameNotUniqueException(Exception):
    pass


def add_user(username, email, uow):
    with uow:
        existing_user = uow.repo.get_user(username)

        if existing_user:
            raise NameNotUniqueException()

        new_user = User(
            username=username,
            email=email,
            bio="In West Philadelphia born and raised, \
                        on the playground is where I spent most of my days",
            created=dt.now(),
            admin=False
        )  # Create an instance of the User class

        uow.repo.add_user(new_user)  # Adds new User record to database
        uow.commit()  # Commits all changes


def get_user(username, uow):
    user = None
    with uow:
        user = uow.repo.get_user(username)
    return {'username': user.username, 'email': user.email}


def get_all_users(uow):
    all_users = None
    with uow:
        all_users = uow.repo.get_all_users()
    return all_users
