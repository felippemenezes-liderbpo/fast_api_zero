from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from app.models import Todo, TodoState, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='john',
            password='secret',
            email='john@example.com',
        )

        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'john'))

    assert asdict(user) == {
        'id': 1,
        'username': 'john',
        'password': 'secret',
        'email': 'john@example.com',
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


@pytest.mark.asyncio
async def test_create_todo(session: Session, user: User, mock_db_time):
    with mock_db_time(model=Todo) as time:
        new_todo = Todo(
            title='Buy milk',
            description='Go to the store and buy milk',
            state=TodoState.todo,
            user_id=user.id,
        )

        session.add(new_todo)
        await session.commit()

    todo = await session.scalar(select(Todo))

    assert asdict(todo) == {
        'id': 1,
        'title': 'Buy milk',
        'description': 'Go to the store and buy milk',
        'state': TodoState.todo,
        'user_id': user.id,
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_user_todo_relationship(session: Session, user: User):
    todo = Todo(
        title='Buy milk',
        description='Go to the store and buy milk',
        state=TodoState.todo,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
