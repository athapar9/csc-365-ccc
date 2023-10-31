import os
import dotenv
from sqlalchemy import create_engine
import sqlalchemy

def database_connection_url():
    dotenv.load_dotenv()

    return os.environ.get("POSTGRES_URI")

engine = create_engine(database_connection_url(), pool_pre_ping=True)
metadata_obj = sqlalchemy.MetaData()
potions = sqlalchemy.Table("potions", metadata_obj, autoload_with=engine)
potion_ledger_items = sqlalchemy.Table("potion_ledger_items", metadata_obj, autoload_with=engine)
gold_ledger_items = sqlalchemy.Table("gold_ledger_items", metadata_obj, autoload_with=engine)
barrel_ledger_items = sqlalchemy.Table("barrel_ledger_items", metadata_obj, autoload_with=engine)
carts = sqlalchemy.Table("carts", metadata_obj, autoload_with=engine)
cart_items = sqlalchemy.Table("cart_items", metadata_obj, autoload_with=engine)
ticks = sqlalchemy.Table("ticks", metadata_obj, autoload_with=engine)