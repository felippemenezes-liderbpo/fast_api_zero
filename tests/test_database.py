from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


@pytest.mark.asyncio
async def test_create_user(session: Session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='john',
            password='secret',
            email='john@example.com',
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'john'))

    assert isinstance(user, User)
    assert asdict(user) == {
        'id': 1,
        'username': 'john',
        'password': 'secret',
        'email': 'john@example.com',
        'created_at': time,
        'updated_at': time,
    }
