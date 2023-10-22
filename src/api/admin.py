from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    #update gold to equal 100
    #update and then set 
    #update num_potions to 0 and ml to 0
    with db.engine.begin() as connection: 
            connection.execute(sqlalchemy.text("TRUNCATE ticks CASCADE"))           
            connection.execute(sqlalchemy.text("TRUNCATE carts CASCADE"))

            description = "RESET"
            tick_id = connection.execute(sqlalchemy.text("INSERT INTO ticks (description) VALUES (:description) RETURNING tick_id"), {"description": description}).scalar()

            connection.execute(sqlalchemy.text("INSERT INTO gold_ledger_items (gold_changed, tick_id) VALUES (100, :tick_id)"), {"tick_id": tick_id})
            connection.execute(sqlalchemy.text("INSERT INTO barrel_ledger_items (tick_id, red_ml_changed, green_ml_changed, blue_ml_changed, dark_ml_changed) VALUES (:tick_id, 0, 0, 0, 0)"), {"tick_id": tick_id})
            for i in range(1, 8):
                connection.execute(sqlalchemy.text("INSERT INTO potion_ledger_items (potion_changed, tick_id, potion_id) VALUES (0, :tick_id, :potion_id)"), {"tick_id": tick_id, "potion_id": i})       

    return "OK"



@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Ananya's Potion Shop",
        "shop_owner": "Ananya Thapar",
    }

