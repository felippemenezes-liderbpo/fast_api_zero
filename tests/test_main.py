from http import HTTPStatus

from fastapi.testclient import TestClient

from app.main import app


def test_root_must_return_ok_and_hello_world() -> None:
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}
