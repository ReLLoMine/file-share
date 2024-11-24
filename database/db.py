import psycopg2
import os

from utils import Singleton


class Database(metaclass=Singleton):
    instance = None
    def __init__(self, *args, **kwargs):
        self.instance = self
        self.connection = None

        self.database_host = kwargs.get("database_host", os.getenv('DB_URL'))
        self.database_name = kwargs.get("database_name", os.getenv('DB_NAME'))
        self.database_username = kwargs.get("database_username", os.getenv('DB_USERNAME'))
        self.database_password = kwargs.get("database_password", os.getenv('DB_PASSWORD'))
        self.do_insert = kwargs.get("do_insert", os.getenv('DO_INSERT'))

        self.init_sql = open(os.path.relpath("database/init.sql"), "r").read() if os.path.exists(
            os.path.relpath("database/init.sql")) else ""

        self.inserts = open(os.path.relpath("database/inserts.sql"), "r").read() if os.path.exists(
            os.path.relpath("database/inserts.sql")) else ""

    def connect_db(self):
        conn = psycopg2.connect(host=self.database_host,
                                database=self.database_name,
                                user=self.database_username,
                                password=self.database_password)
        self.connection = conn
        return conn

    def init_db(self):
        if self.init_sql:
            cur = self.connection.cursor()
            cur.execute(self.init_sql)
            self.connection.commit()
            cur.close()

        if self.do_insert:
            cur = self.connection.cursor()
            cur.execute(self.inserts)
            self.connection.commit()
            cur.close()
