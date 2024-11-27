from database import model


class Role(model.Model):
    def __init__(self):
        super().__init__()
        self.id: int = 0
        self.name: str = ""
        self.level: int = 0

    def get_role_by_name(self, name):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"select * from {self.get_table()} where name = '{name}'")
        conn.commit()
        self.apply_data(list(*cur))
        return self


class User(model.Model):
    def __init__(self):
        super().__init__()
        self._table = "fs_user"

        self.id: int = 0
        self.name: str = ""
        self.email: str = ""
        self.password: str = ""
        self.id_role: int = 0

    def delete(self):
        files = File().get_all_by_owner_id(self.id)
        for file in files:
            file.delete()
        accesses = FileAccess().get_all_by_user(self.id)
        for access in accesses:
            access.delete()
        super().delete()

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

    def get_user_by_email(self, email):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"select * from {self.get_table()} where email = '{email}'")
        conn.commit()
        self.apply_data(list(*cur))
        return self

    def get_guest(self):
        return self[1]

    def __bool__(self):
        return self.id > 0


class FileAccessLvl(model.Model):
    def __init__(self):
        super().__init__()
        self._table = "file_access_lvl"

        self.id: int = 0
        self.name: str = ""
        self.level: int = 0

    def get_access_lvl_by_name(self, name):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(f"select * from {self.get_table()} where name = '{name}'")
        conn.commit()
        self.apply_data(list(*cur))
        return self


class FileAccess(model.Model):
    def __init__(self):
        super().__init__()
        self._uid = "id_user", "id_file"
        self._table = "file_access"
        self._serial = None

        self.id_user: int = 0
        self.id_file: int = 0
        self.id_access_lvl: int = 0

    def get_user(self):
        user = User()
        return user[self.id_user]

    def get_file(self):
        file = File()
        return file[self.id_file]

    def get_access_lvl(self):
        access_lvl = FileAccessLvl()
        return access_lvl[self.id_access_lvl]

    def get_all_by_file(self, id_file):
        return self.fetch_all(f"id_file = {id_file}")

    def get_all_by_user(self, id_user):
        return self.fetch_all(f"id_user = {id_user}")

    def __bool__(self):
        return self.id_user > 0


class File(model.Model):
    def __init__(self):
        super().__init__()

        self.id: int = 0
        self.name: str = ""
        self.id_owner: int = 0

    def delete(self):
        accesses = FileAccess().get_all_by_file(self.id)
        for access in accesses:
            access.delete()
        super().delete()

    def get_all_by_owner_id(self, owner_id):
        return self.fetch_all(f"id_owner = {owner_id}")

    def get_owner(self):
        user = User()
        return user[self.id_owner]

    def give_access(self, user, access_lvl):
        access = FileAccess()
        access.id_user = user.id
        access.id_file = self.id
        access.id_access_lvl = access_lvl.id
        access.insert()

    def get_access_lvl(self, user):
        if user.id == self.id_owner:  # owner
            return FileAccessLvl().get_access_lvl_by_name("owner")
        if user.get_role().level == Role().get_role_by_name("admin").level:  # admin
            return FileAccessLvl().get_access_lvl_by_name("delete")
        access = FileAccess()
        return access[user.id, self.id].get_access_lvl()

    def __bool__(self):
        return self.id > 0
