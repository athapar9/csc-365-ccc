from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, gold FROM global_inventory"))
        first_row = result.first()
        cur_red_ml = first_row.num_red_ml
        gold_amount = first_row.gold

        for barrel in barrels_delivered:
            cur_red_ml += barrel.ml_per_barrel * barrel.quantity
            gold_amount -= barrel.price * barrel.quantity
    
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :cur_red_ml, gold = :gold_amount"), {"cur_red_ml" : cur_red_ml, "gold_amount": gold_amount})
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, gold FROM global_inventory"))
    # print(f"catalog result: {result}")
    first_row = result.first()
    num_red_potions = first_row.num_red_potions
    gold_amount = first_row.gold
    
    print(f"num_red_potions: {num_red_potions}; Gold: {gold_amount}")
    if num_red_potions < 10:
        # for each barrel in wholesale_catalog:
        for barrel in wholesale_catalog:
            if gold_amount >= barrel.price * barrel.quantity:
                return [
                    {
                        "sku": "SMALL_RED_BARREL",
                        "quantity": 1,
                    }
                ]
            else:
                return []
