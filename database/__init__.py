from database.db import *
from database.model import *

database = Database()
database.connect_db()
database.init_db()
