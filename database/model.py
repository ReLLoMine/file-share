from database import Database


class Model:
    __exclude__ = ['_table']

    def __init__(self):
        self.__conn = Database().connection

    def __getitem__(self, index):
        if isinstance(index, tuple):
            cur = self.__conn.cursor()
            qry = f"select {', '.join(self.get_cols())} from {self.get_table()} where "
            qry += ' and '.join([f"{key} = {value}" for key, value in zip(self.get_uid_cols(), index)])
            cur.execute(qry)
            self.__conn.commit()
            self.set_values(dict(zip(self.get_cols(), list(*cur))))
        else:
            cur = self.__conn.cursor()
            cur.execute(f"select {', '.join(self.get_cols())} from {self.get_table()} where {self.get_uid_cols()} = {index}")
            self.__conn.commit()
            self.set_values(dict(zip(self.get_cols(), list(*cur))))
        return self

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    def get_cols(self, no_id=False):
        return list(
            map(lambda y: y[0],
                filter(lambda x: not (x[0].startswith("_") or callable(x[1]) or x[0] in self.__exclude__ or (
                            no_id and x[0] == self.get_uid_cols())),
                       self.__dict__.items())))

    def get_values(self, no_id=False):
        return list(
            map(lambda y: y[1],
                filter(lambda x: not (x[0].startswith("_") or callable(x[1]) or x[0] in self.__exclude__ or (
                            no_id and x[0] == self.get_uid_cols())),
                       self.__dict__.items())))

    def set_values(self, data):
        for key, value in data.items():
            if key in self.__dict__:
                self.__dict__[key] = value
        return self

    def get_conn(self):
        return self.__conn

    def apply_data(self, data):
        return self.set_values(dict(zip(self.get_cols(), data)))


    def dict(self):
        return dict(zip(self.get_cols(), self.get_values()))

    def get_table(self):
        return self.__dict__.get('_table', self.__class__.__name__.lower())

    def get_uid_cols(self):
        return self.__dict__.get('_uid', 'id')

    def get_uid(self):
        return self.__dict__[self.__dict__.get('_uid', 'id')]

    def select(self, where=None):
        qry = f"select {', '.join(self.get_cols())} from {self.get_table()}"
        if where:
            qry += f" where {where}"
        return qry

    def fetch_all(self, where=None):
        cur = self.__conn.cursor()
        cur.execute(self.select(where))
        self.__conn.commit()
        return [self.__class__().apply_data(row) for row in cur]

    def insert(self):
        def wrap_str(string):
            return "'" + str(string) + "'" if isinstance(string, str) else str(string)

        cur = self.__conn.cursor()
        cur.execute(f"insert into {self.get_table()} ({', '.join(self.get_cols(True))}) values ({', '.join(map(wrap_str, self.get_values(True)))})")
        self.__conn.commit()
        return self

    def delete(self):
        cur = self.__conn.cursor()
        qry = f"delete from {self.get_table()} where "
        if isinstance(self.get_cols(), tuple):
            qry += ' and '.join([f"{key} = {value}" for key, value in zip(self.get_uid_cols(), self.get_values())])
        else:
            qry += f"{self.get_uid_cols()} = {self.get_uid()}"

        cur.execute(qry)
        self.__conn.commit()


    def patch(self):
        def wrap_str(string):
            return "'" + str(string) + "'" if isinstance(string, str) else str(string)

        cur = self.__conn.cursor()
        qry = f"update {self.get_table()} set {', '.join([f'{key} = {wrap_str(value)}' for key, value in zip(self.get_cols(), self.get_values())])} where "

        if isinstance(self.get_cols(), tuple):
            qry += ' and '.join([f"{key} = {value}" for key, value in zip(self.get_uid_cols(), self.get_values())])
        else:
            qry += f"{self.get_uid_cols()} = {self.get_uid()}"

        cur.execute(qry)
        self.__conn.commit()
        return self