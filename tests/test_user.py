from io import BytesIO

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

#  Тест обращения к корневому ресурсу (переадресация на /user)
def test_index(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


#  Тест доступности ресурса auth
def test_auth(client):
    response = client.get('/auth')
    assert response.status_code == 200


#  Тест неавторизованного пользователя
def test_user_guest(client):
    response = client.get('/user')
    assert response.status_code == 200
    assert response.json == {'id': 1, 'name': 'guest', 'email': 'guest@mail.com', 'password': 'password', 'id_role': 3}


#  Тест регистрации
@pytest.mark.dependency()
def test_user_register(client):
    response = client.post('/user', json={'name': 'test', 'email': 'test@mail.com', 'password': 'password'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


#  Тест авторизации
@pytest.mark.dependency(depends=['test_user_register'])
def test_user_auth(client):
    response = client.post('/auth', json={'email': 'test@mail.com', 'password': 'password'})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')


#  Тест загрузки файла
@pytest.mark.dependency(depends=['test_user_auth'])
def test_upload(client):
    client.post('/auth', json={'email': 'test@mail.com', 'password': 'password'})
    response = client.post('/file', data={
        'file': (BytesIO(open('tests/test_user.py', 'rb').read()), 'test_user.py')},
                           content_type='multipart/form-data')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/files')


#  Тест скачивания файла
@pytest.mark.dependency(depends=['test_upload'])
def test_download(client):
    client.post('/auth', json={'email': 'test@mail.com', 'password': 'password'})
    response = client.get('/files')
    assert response.status_code == 200
    file_id = response.json[0]['id']
    response = client.get(f'/file/{file_id}/download')
    assert response.status_code == 200
    assert response.data == open('tests/test_user.py', 'rb').read()


#  Тест ошибки авторизации
@pytest.mark.dependency(depends=['test_download'])
def test_auth_fail(client):
    response = client.post('/auth', json={'email': 'notexist', 'password': 'notexist'})
    assert response.status_code == 401
    assert response.json == {'error': 'Invalid credentials'}


#  Тест удаления пользователя
@pytest.mark.dependency(depends=['test_auth_fail'])
def test_user_delete(client):
    client.post('/auth', json={'email': 'test@mail.com', 'password': 'password'})
    response = client.delete('/user')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/user')
