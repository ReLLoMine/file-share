import database.db as db
import database.model as model

database = db.Database()
database.connect_db()
database.init_db()
