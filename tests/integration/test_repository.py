from application.adapters import repository
from application.domain.model import User

from tests.conftest import insert_user, create_user


def test_repository_can_add_a_user(session):
    user = create_user()
    repo = repository.SqlAlchemyRepository(session)
    repo.add_user(user)
    session.commit()

    rows = list(session.execute(
        'SELECT username, email FROM users'
    ))
    assert rows == [('Andrew', 'andrew@police.govt.nz')]


def test_repository_can_retrieve_a_user(session):
    insert_user(session)
    user = create_user()

    repo = repository.SqlAlchemyRepository(session)
    retrieved_user = repo.get_user('Andrew')

    assert user == retrieved_user