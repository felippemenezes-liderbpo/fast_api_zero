from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def test_create_user(session: Session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='John Doe',
            password='secret',
            email='john@example.com',
        )
        session.add(new_user)
        session.commit()

    user = session.scalar(select(User).where(User.username == 'John Doe'))

    assert isinstance(user, User)
    assert asdict(user) == {
        'id': 1,
        'username': 'John Doe',
        'password': 'secret',
        'email': 'john@example.com',
        'created_at': time,
        'updated_at': time,
    }
