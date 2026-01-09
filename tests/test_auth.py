from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from app.models import User


def test_get_token(client: TestClient, user: User):
    response = client.post(
        '/auth/token/',
        data={
            'username': user.email,
            'password': 'testtest',
        },
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'bearer'


def test_token_expired_after_time(client: TestClient, user: User, token_time):
    with token_time() as time:
        with freeze_time(time['creation']):
            response = client.post(
                '/auth/token',
                data={'username': user.email, 'password': user.clean_password},
            )
            assert response.status_code == HTTPStatus.OK
            token = response.json()['access_token']

        with freeze_time(time['expired']):
            response = client.put(
                f'/users/{user.id}',
                headers={'Authorization': f'Bearer {token}'},
                json={
                    'username': 'wrong',
                    'email': 'wrong@wrong.com',
                    'password': 'wrong',
                },
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert response.json() == {
                'detail': 'Could not validate credentials'
            }


def test_refresh_token(client: TestClient, token: str):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(
    client: TestClient, user: User, token_time
):
    with token_time() as time:
        with freeze_time(time['creation']):
            response = client.post(
                '/auth/token',
                data={'username': user.email, 'password': user.clean_password},
            )
            assert response.status_code == HTTPStatus.OK
            token = response.json()['access_token']

        with freeze_time(time['expired']):
            response = client.post(
                '/auth/refresh_token',
                headers={'Authorization': f'Bearer {token}'},
            )
            assert response.status_code == HTTPStatus.UNAUTHORIZED
            assert response.json() == {
                'detail': 'Could not validate credentials'
            }


def test_login_incorrect_email(client: TestClient):
    response = client.post(
        '/auth/token/',
        data={'username': 'nonexistent@example.com', 'password': 'password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_login_incorrect_password(client: TestClient, user: User):
    response = client.post(
        '/auth/token/',
        data={'username': user.email, 'password': 'wrongpassword'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
