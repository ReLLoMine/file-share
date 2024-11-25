import pytest
from app import app as flask_app


@pytest.fixture()
def app():
    app = flask_app
    app.testing = True

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


def test_auth(client):
    response = client.get('/auth')
    assert response.status_code == 200


def test_user_guest(client):
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json == {'id': 1, 'name': 'guest', 'email': 'guest@mail.com', 'password': 'password', 'id_role': 3}


@pytest.mark.dependency()
def test_user_register(client):
    response = client.post('/user', json={'name': 'test', 'email': 'test@mail.com', 'password': 'password'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


@pytest.mark.dependency(depends=['test_user_register'])
def test_user_auth(client):
    response = client.post('/auth', json={'email': 'test@mail.com', 'password': 'password'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


@pytest.mark.dependency(depends=['test_user_auth'])
def test_user_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


@pytest.mark.dependency(depends=['test_user_logout'])
def test_auth_fail(client):
    response = client.post('/auth', json={'email': 'notexist', 'password': 'notexist'})
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}


@pytest.mark.dependency(depends=['test_user_logout'])
def test_user_delete(client):
    client.post('/auth', json={'email': 'test@mail.com', 'password': 'password'})
    response = client.delete('/user')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')
