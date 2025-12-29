from http import HTTPStatus

from fastapi.testclient import TestClient


def test_create_user(client: TestClient) -> None:
    user: dict[str, str] = {
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


# TODO: Adicionar validação para criar usuário com inputs errados


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


# TODO: Adicionar validação listar usuários com db vazio


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
