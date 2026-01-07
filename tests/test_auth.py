from http import HTTPStatus

from fastapi.testclient import TestClient

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
    assert 'token_type' in token


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
