import os

from flask import Flask, session, send_file
from flask import request, jsonify, redirect
import models
import utils

app = Flask(__name__)
app.secret_key = "super secret key"

def get_current_user():
    user = models.User()
    user = user[session.get('user').get('id')] if session.get('user') else None
    return user

@app.get('/')
def hello_world():
    return redirect('/user')

@app.get('/auth')
def auth_get():
    return '''
        <form method="post" action="/auth">
            <input type="text" name="email" placeholder="Email">
            <input type="password" name="password" placeholder="Password">
            <input type="submit" value="Authenticate">
        </form>
    '''

@app.post('/auth')
def auth_post():
    data = request.get_json()
    user = models.User()
    session['user'] = user.authenticate(data.get('email'), utils.digest_password(data.get('password'))).dict()
    return redirect('/user')

@app.get('/logout')
def logout():
    session.pop('user', None)
    return redirect('/user')

@app.get('/user')
def get_user():
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    match user.get_role().level:
        case 1:
            user = models.User()
            return [o.dict() for o in user.fetch_all()]
        case 2:
            return user.dict()
        case _:
            return {'error': 'Unauthorized'}, 401

@app.get('/role')
def get_role():
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    match user.get_role().level:
        case 1:
            return [o.dict() for o in models.Role().fetch_all()]
        case 2:
            return user.get_role().dict()
        case _:
            return {'error': 'Unauthorized'}, 401

@app.post('/user')
def add_user():
    data = request.get_json()
    user = models.User()

    user.name = data.get('name')
    user.email = data.get('email')
    user.password = utils.digest_password(data.get('password'))
    user.id_role = 2

    user.insert()

    return redirect('/user')

@app.patch('/user')
def patch_user():
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    data = request.get_json()

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.password = utils.digest_password(data.get('password')) if data.get('password') else user.password
    user.patch()
    return redirect('/user')

@app.get('/user/<int:id>')
def get_user_by_id(id):
    user = get_current_user()
    if user is None or user.get_role().level != 1:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    user = user[id]

    if not user:
        return {'error': 'User not found'}, 404

    return user.dict()

@app.delete('/user/<int:id>')
def delete_user(id):
    user = get_current_user()
    if user is None or user.get_role().level != 1:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    user = user[id]

    if not user:
        return {'error': 'User not found'}, 404

    user.delete()

    return redirect('/user')

@app.patch('/user/<int:id>')
def patch_user_by_id(id):
    user = get_current_user()
    if user is None or user.get_role().level != 1:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    user = user[id]

    if not user:
        return {'error': 'User not found'}, 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    user.password = utils.digest_password(data.get('password')) if data.get('password') else user.password
    user.id_role = data.get('id_role', user.id_role)

    user.patch()

    return redirect('/user/' + str(id))

@app.get('/file')
def get_file():
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    match user.get_role().level:
        case 1:
            file = models.File()
            return [o.dict() for o in file.fetch_all()]
        case 2:
            return [o.dict() for o in user.get_files()]
        case _:
            return {'error': 'Unauthorized'}, 401

@app.get('/file/<int:id>')
def get_file_by_id(id):
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    return file.dict()

@app.get('/file/download/<int:id>')
def download_file(id):
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    file = models.File()
    file = file[id]

    if file.id_owner != user.id and user.get_role().level != 1:
        return {'error': 'Unauthorized'}, 401

    if not file:
        return {'error': 'File not found'}, 404

    return send_file(f'data/{file.id_owner}/{file.name}', as_attachment=True)

@app.delete('/file/<int:id>')
def delete_file(id):
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    file = models.File()
    file = file[id]

    if file.id_owner != user.id and user.get_role().level != 1:
        return {'error': 'Unauthorized'}, 401

    if not file:
        return {'error': 'File not found'}, 404

    if os.path.exists(os.path.relpath(f'data/{file.id_owner}/{file.name}')):
        os.remove(os.path.relpath(f'data/{file.id_owner}/{file.name}'))
    file.delete()
    return redirect('/file')

@app.post('/file')
def add_file():
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    for _, file in request.files.items():
        file_db = models.File()
        file_db.name = file.filename
        file_db.id_owner = user.id
        file_db.insert()

        if os.path.exists(f'data/{file_db.id_owner}/{file.filename}'):
            return {'error': 'File already exists'}, 400

        os.makedirs(os.path.dirname(f'data/{file_db.id_owner}/'), exist_ok=True)
        with open(f'data/{file_db.id_owner}/{file.filename}', 'wb') as f:
            f.write(file.read())

    return redirect('/file')

@app.patch('/file/<int:id>')
def patch_file_by_id(id):
    user = get_current_user()
    if user is None:
        return {'error': 'Unauthorized'}, 401

    file = models.File()
    file = file[id]

    if file.id_owner != user.id and user.get_role().level != 1:
        return {'error': 'Unauthorized'}, 401

    if not file:
        return {'error': 'File not found'}, 404

    for _, file_new in request.files.items():
        file.name = file_new.filename
        file.patch()

        if os.path.exists(f'data/{file.id_owner}/{file.file}'):
            with open(f'data/{file.id_owner}/{file.file}', 'wb') as f:
                f.write(file_new.read())

    return redirect('/file/' + str(id))

if __name__ == '__main__':
    app.run()
