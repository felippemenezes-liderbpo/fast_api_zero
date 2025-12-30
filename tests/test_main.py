from http import HTTPStatus

from fastapi.testclient import TestClient


def test_create_user(client: TestClient) -> None:
    user = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 'secret',
    }
    response = client.post(
        '/users/',
        json=user,
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': user['username'],
        'email': user['email'],
    }


def test_create_user_invalid_password(client: TestClient) -> None:
    user = {
        'username': 'alice',
        'email': 'alice@example.com',
        'password': 12345678,
    }
    response = client.post(
        '/users/',
        json=user,
    )
    response_detail = response.json()['detail'][0]

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response_detail['msg'] == 'Input should be a valid string'


def test_read_users(client: TestClient) -> None:
    response = client.get('/users/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'id': 1,
                'username': 'alice',
                'email': 'alice@example.com',
            }
        ]
    }


def test_read_user(client: TestClient) -> None:
    response = client.get('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'alice',
        'email': 'alice@example.com',
    }


def test_read_user_not_found(client: TestClient) -> None:
    response = client.get('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client: TestClient) -> None:
    new_user: dict[str, str] = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'newpassword',
    }
    response = client.put('/users/1', json=new_user)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': new_user['username'],
        'email': new_user['email'],
    }


def test_update_user_not_found(client: TestClient) -> None:
    new_user: dict[str, str] = {
        'username': 'bob',
        'email': 'bob@example.com',
        'password': 'newpassword',
    }
    response = client.put('/users/999', json=new_user)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client: TestClient) -> None:
    response = client.delete('/users/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted successfully'}


def test_delete_user_not_found(client: TestClient) -> None:
    response = client.delete('/users/999')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
