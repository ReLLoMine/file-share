import os

from flask import Flask, session, send_file
from flask import request, jsonify, redirect
import models
import utils

app = Flask(__name__)
app.secret_key = "super secret key"

admin_role = models.Role().get_role_by_name("admin")
user_role = models.Role().get_role_by_name("user")
guest_role = models.Role().get_role_by_name("guest")

read_file_access_lvl = models.FileAccessLvl().get_access_lvl_by_name("read")
write_file_access_lvl = models.FileAccessLvl().get_access_lvl_by_name("write")
delete_file_access_lvl = models.FileAccessLvl().get_access_lvl_by_name("delete")
owner_file_access_lvl = models.FileAccessLvl().get_access_lvl_by_name("owner")

def get_current_user():
    user = models.User()
    if 'user' not in session:
        return user.get_guest()
    return user[session.get('user').get('id')]

def get_current_user_role():
    user = get_current_user()
    return user.get_role()

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
    if request.content_type != 'application/json':
        data = {k: v for k, v in request.form.items()}
    else:
        data = request.get_json()
    user = models.User()
    session['user'] = user.authenticate(data.get('email'), utils.digest_password(data.get('password'))).dict()
    return redirect('/user')

@app.get('/logout')
def logout():
    session.pop('user', None)
    return redirect('/user')

@app.get('/role')
def get_role():
    role = get_current_user_role()
    return role.dict()

@app.get('/roles')
def get_roles():
    role = get_current_user_role()
    if role.level > admin_role.level:
        return {'error': 'Unauthorized'}, 401

    return [o.dict() for o in role.fetch_all()]

@app.get('/user')
def get_user():
    user = get_current_user()
    return user.dict()

@app.get('/users')
def get_users():
    role = get_current_user_role()
    if role.level > admin_role.level:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    return [o.dict() for o in user.fetch_all()]

@app.post('/user')
def add_user():
    data = request.get_json()
    user = models.User()

    user.name = data.get('name')
    if user.get_user_by_email(data.get('email')):
        return {'error': 'Email already exists'}, 400
    user.email = data.get('email')
    user.password = utils.digest_password(data.get('password'))
    user.id_role = user_role.id

    user.insert()

    return redirect('/user')

@app.patch('/user')
def patch_user():
    role = get_current_user_role()
    if role == guest_role:
        return {'error': 'Unauthorized'}, 401

    user = get_current_user()
    data = request.get_json()

    user.name = data.get('name', user.name)
    if user.get_user_by_email(data.get('email')):
        return {'error': 'Email already exists'}, 400
    user.email = data.get('email', user.email)
    user.password = utils.digest_password(data.get('password')) if data.get('password') else user.password
    user.patch()
    return redirect('/user')

@app.get('/user/<int:id>')
def get_user_by_id(id):
    role = get_current_user_role()
    if role.level > admin_role.level:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    user = user[id]

    if not user:
        return {'error': 'User not found'}, 404

    return user.dict()

@app.delete('/user/<int:id>')
def delete_user(id):
    role = get_current_user_role()
    if role.level > admin_role.level:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    user = user[id]

    if not user:
        return {'error': 'User not found'}, 404

    user.delete()

    return redirect('/user')

@app.patch('/user/<int:id>')
def patch_user_by_id(id):
    role = get_current_user_role()
    if role.level > admin_role.level:
        return {'error': 'Unauthorized'}, 401

    user = models.User()
    user = user[id]

    if not user:
        return {'error': 'User not found'}, 404

    data = request.get_json()
    user.name = data.get('name', user.name)
    if user.get_user_by_email(data.get('email')):
        return {'error': 'Email already exists'}, 400
    user.email = data.get('email', user.email)
    user.password = utils.digest_password(data.get('password')) if data.get('password') else user.password
    user.id = data.get('id_role', user.id)

    user.patch()

    return redirect('/user/' + str(id))

@app.get('/files')
def get_file():
    role = get_current_user_role()

    match role.level:
        case admin_role.level:
            file = models.File()
            return [o.dict() for o in file.fetch_all()]
        case user_role.level:
            return [o.dict() for o in get_current_user().get_files()]
        case _:
            return {'error': 'Unauthorized'}, 401

@app.get('/file/<int:id>')
def get_file_by_id(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    if file.get_access_lvl(user).level < read_file_access_lvl.level:
        return {'error': 'Unauthorized'}, 401

    return file.dict()

@app.get('/file/<int:id>/download')
def download_file(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    if file.get_access_lvl(user).level < read_file_access_lvl.level:
        return {'error': 'Unauthorized'}, 401

    return send_file(f'data/{file.id_owner}/{file.name}', as_attachment=True)

@app.post('/file')
def add_file():
    user = get_current_user()
    if user.get_role().level > user_role.level:
        return {'error': 'Unauthorized'}, 401

    for _, file in request.files.items():
        file_db = models.File()
        file_db.name = file.filename
        file_db.id_owner = user.id

        access = models.FileAccess()
        access.id_user = user.id
        access.id_file = file_db.id
        access.id_access_lvl = owner_file_access_lvl.id

        if os.path.exists(f'data/{file_db.id_owner}/{file.filename}'):
            return {'error': 'File already exists'}, 400

        access.insert()
        file_db.insert()

        os.makedirs(os.path.dirname(f'data/{file_db.id_owner}/'), exist_ok=True)
        with open(f'data/{file_db.id_owner}/{file.filename}', 'wb') as f:
            f.write(file.read())

    return redirect('/files')

@app.delete('/file/<int:id>')
def delete_file(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    if file.get_access_lvl(user).level < delete_file_access_lvl.level:
        return {'error': 'Unauthorized'}, 401

    if os.path.exists(os.path.relpath(f'data/{file.id_owner}/{file.name}')):
        os.remove(os.path.relpath(f'data/{file.id_owner}/{file.name}'))

    file.delete()
    return redirect('/files')

@app.patch('/file/<int:id>')
def patch_file_by_id(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    if file.get_access_lvl(user).level < write_file_access_lvl.level:
        return {'error': 'Unauthorized'}, 401

    for _, file_new in request.files.items():
        file.name = file_new.filename
        file.patch()

        if os.path.exists(f'data/{file.id_owner}/{file.file}'):
            with open(f'data/{file.id_owner}/{file.file}', 'wb') as f:
                f.write(file_new.read())

    return redirect('/file/' + str(id))

@app.get('/file/<int:id>/access_lvl')
def get_file_access_lvl(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    return file.get_access_lvl(user).dict()

@app.get('/file/<int:id>/can_access')
def get_file_who_can_access(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    if file.get_access_lvl(user).level < read_file_access_lvl.level:
        return {'error': 'Unauthorized'}, 401

    access = models.FileAccess()
    def wrap(af):
        user_ = models.User()
        user_ = user_[af.id_user]
        return {"name": user_.name, "email": user_.email, "access": af.get_access_lvl().name}

    return [wrap(o) for o in access.get_all_by_file(id)]

@app.post('/file/<int:id>/access_lvl')
def add_file_access_lvl(id):
    user = get_current_user()
    file = models.File()
    file = file[id]

    if not file:
        return {'error': 'File not found'}, 404

    if file.get_access_lvl(user).level < owner_file_access_lvl.level:
        return {'error': 'Unauthorized'}, 401

    data = request.get_json()
    access = models.FileAccess()
    access.id_user = data.get('id_user')
    access.id_file = file.id
    access.id_access_lvl = data.get('id_access_lvl')

    access.insert()

    return redirect('/file/' + str(id) + '/can_access')

if __name__ == '__main__':
    app.run()
