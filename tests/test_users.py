from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models import User
from app.schemas import UserPublic
from tests.conftest import UserFactory


def test_create_user(client: TestClient):
    response = client.post(
        '/users/',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    data = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert data == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
        'created_at': data['created_at'],
        'updated_at': data['updated_at'],
    }


def test_create_user_with_existing_username(client: TestClient):
    user = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }
    response = client.post(
        '/users/',
        json=user,
    )

    new_user = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }
    response = client.post(
        '/users/',
        json=new_user,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_with_existing_email(client: TestClient):
    user = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }
    response = client.post(
        '/users/',
        json=user,
    )

    new_user = {
        'username': 'bob',
        'email': 'alice@example.com',
        'password': 'secret',
    }
    response = client.post(
        '/users/',
        json=new_user,
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_read_users_with_user(
    client: TestClient, user: User, other_user: User
):
    user_schema = UserPublic.model_validate(user).model_dump(mode='json')
    other_user_schema = UserPublic.model_validate(other_user).model_dump(
        mode='json'
    )

    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [user_schema, other_user_schema],
    }


@pytest.mark.asyncio
async def test_read_users_pagination(
    session: AsyncSession, client: TestClient
):
    expected_users = 2
    session.add_all(UserFactory.create_batch(5))
    await session.commit()

    response = client.get(
        '/users/?offset=1&limit=2',
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['users']) == expected_users


def test_read_users_empty(client: TestClient):
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_user(client: TestClient, user: User):
    response = client.get(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_read_user_not_found(client: TestClient, user: User):
    response = client.get(f'/users/{user.id + 1}')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client: TestClient, user: User, token: str):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'newpassword',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'bob',
        'email': 'bob@example.com',
        'created_at': user.created_at.isoformat(),
        'updated_at': user.updated_at.isoformat(),
    }


def test_update_username_conflict(
    client: TestClient, user: User, other_user: User, token: str
):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
            'email': user.email,
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_email_conflict(
    client: TestClient, user: User, other_user: User, token: str
):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': user.username,
            'email': other_user.email,
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_update_user_insufficient_permissions(
    client: TestClient, other_user: User, token: str
):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'bob',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_delete_user(client: TestClient, user: User, token: str):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_insufficient_permissions(
    client: TestClient, other_user: User, token: str
):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
