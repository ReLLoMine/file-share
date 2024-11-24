from database import model


class Role(model.Model):
    def __init__(self):
        super().__init__()
        self._uid = "id"

        self.id: int = 0
        self.name: str = ""
        self.level: int = 0


class User(model.Model):
    def __init__(self):
        super().__init__()
        self._table = "fs_user"
        self._uid = "id"

        self.id: int = 0
        self.name: str = ""
        self.email: str = ""
        self.password: str = ""
        self.id_role: int = 0

    def authenticate(self, email, password):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"select * from {self.get_table()} where email = '{email}' and password = '{password}'")
        conn.commit()
        self.apply_data(list(*cur))
        return self

    def get_role(self):
        role = Role()
        return role[self.id_role]

    def get_files(self):
        file = File()
        return file.fetch_all(f"id_owner = {self.id}")

    def __bool__(self):
        return self.id > 0

class File(model.Model):
    def __init__(self):
        super().__init__()
        self._uid = "id"

        self.id: int = 0
        self.name: str = ""
        self.id_owner: int = 0

    def get_user(self):
        user = User()
        return user[self.id_owner]

    def __bool__(self):
        return self.id > 0