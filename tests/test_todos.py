from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models import Todo, TodoState, User
from tests.conftest import TodoFactory


def test_create_todo(client: TestClient, token: str):
    response = client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Todo',
            'description': 'Test todo description',
            'state': 'draft',
        },
    )

    data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert data == {
        'id': 1,
        'title': 'Test Todo',
        'description': 'Test todo description',
        'state': 'draft',
        'created_at': data['created_at'],
        'updated_at': data['updated_at'],
    }


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(size=5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_pagination_should_return_2_todos(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(size=5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(size=5, user_id=user.id, title='Test todo 1')
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            size=5, user_id=user.id, description='description'
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            size=5, user_id=user.id, state=TodoState.draft
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?state=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            size=5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )

    session.add_all(
        TodoFactory.create_batch(
            size=3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )
    await session.commit()

    response = client.get(
        (
            '/todos/?title=Test todo combined&description=combined description'
            '&state=done'
        ),
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_less_3(client: TestClient, token: str):
    response = client.get(
        '/todos/?state=ab',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_todos_filter_title_greater_20(
    client: TestClient, token: str
):
    response = client.get(
        '/todos/?state=abcdefghijklmnopqrstuvwxyz',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_patch_todo_not_found(client: TestClient, token: str):
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'New title', 'description': 'New description'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Task not found'


@pytest.mark.asyncio
async def test_patch_todo(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'New title', 'description': 'New description'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'New title'
    assert response.json()['description'] == 'New description'


@pytest.mark.asyncio
async def test_delete_todo(
    session: AsyncSession, user: User, client: TestClient, token: str
):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


@pytest.mark.asyncio
async def test_delete_todo_not_found(client: TestClient, token: str):
    response = client.delete(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


@pytest.mark.asyncio
async def test_todo_state_invalid_value(session: AsyncSession, user: User):
    todo = Todo(
        user_id=user.id,
        title='Test Todo',
        description='Test description',
        state='invalid_state',
    )
    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError, match='invalid_state'):
        await session.scalar(select(Todo).where(Todo.id == todo.id))
