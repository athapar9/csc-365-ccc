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
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_blue_ml, num_green_ml, gold FROM global_inventory"))
        first_row = result.first()
        cur_red_ml = first_row.num_red_ml
        cur_blue_ml = first_row.num_blue_ml
        cur_green_ml = first_row.num_green_ml
        tot_gold = first_row.gold
   

        for barrel in barrels_delivered:
                if "red" in barrel.sku.lower():
                    cur_red_ml += barrel.ml_per_barrel * barrel.quantity
                    tot_gold -= barrel.price * barrel.quantity
                if "green" in barrel.sku.lower():
                    cur_green_ml += barrel.ml_per_barrel * barrel.quantity
                    tot_gold -= barrel.price * barrel.quantity
                if "blue" in barrel.sku.lower():
                    cur_blue_ml += barrel.ml_per_barrel * barrel.quantity
                    tot_gold -= barrel.price * barrel.quantity

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :tot_gold"), [{"tot_gold": tot_gold }])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :cur_red_ml"), [{"cur_red_ml" : cur_red_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :cur_green_ml"), [{"cur_green_ml" : cur_green_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :cur_blue_ml"), [{"cur_blue_ml" : cur_blue_ml}])
        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green_potions, gold FROM global_inventory"))
    # print(f"catalog result: {result}")
    first_row = result.first()

    #current status of all vars
    cur_red_potions = first_row.num_red_potions
    cur_blue_potions = first_row.num_blue_potions
    cur_green_potions = first_row.num_green_potions
    cur_gold = first_row.gold

    #barrels to buy
    purchased_red_potions = 217
    purchased_green_potions = 0
    purchased_blue_potions = 0

    tot_red_ml = 0
    tot_green_ml = 0
    tot_blue_ml = 0

    barrels = []
    
    print(f"num_red_potions: {cur_red_potions}; num_blue_potions: {cur_blue_potions}, num_green_potions: {cur_green_potions}, Gold: {cur_gold}")

    #RED
    for barrel in wholesale_catalog:
        barrels_purchased = 0
        if "red" in barrel.sku.lower():
            if cur_red_potions < 10:
                print("cur gold: ", cur_gold)
                print("quantity: ", barrels_purchased)
                print("potential red: ", purchased_red_potions)
                print("barrel price: ", barrel.price)
            
            while cur_gold >= barrel.price:
                print("buy barrels")
                barrels_purchased += 1
                if barrels_purchased > barrel.quantity:
                    barrels_purchased = barrel.quantity
                barrel.quantity -= 1
                cur_gold -= barrel.price
                tot_red_ml += barrel.ml_per_barrel
                purchased_red_potions = tot_red_ml // 100
                if barrels_purchased > 0:
                    barrels.append(
                        {
                            "sku": "SMALL_RED_BARREL",
                            "quantity": barrels_purchased,
                        })
        #GREEN
        if "green" in barrel.sku.lower():
            if cur_green_potions < 10:
                while cur_gold >= barrel.price:
    
                    barrels_purchased += 1
                    if barrels_purchased > barrel.quantity:
                        barrels_purchased = barrel.quantity
                    barrel.quantity -= 1
                    cur_gold -= barrel.price
                    tot_green_ml += barrel.ml_per_barrel
                    purchased_green_potions = tot_green_ml // 100
                    if barrels_purchased > 0:
                        barrels.append(
                            {
                                "sku": "SMALL_GREEN_BARREL",
                                "quantity": barrels_purchased,
                            })

        #BLUE
        elif "blue" in barrel.sku.lower():
            if cur_green_potions < 10:
                while cur_gold >= barrel.price:
    
                    barrels_purchased += 1
                    if barrels_purchased > barrel.quantity:
                        barrels_purchased = barrel.quantity
                    barrel.quantity -= 1
                    cur_gold -= barrel.price
                    tot_blue_ml += barrel.ml_per_barrel
                    purchased_blue_potions = tot_blue_ml // 100
                    if barrels_purchased > 0:
                        barrels.append(
                            {
                                "sku": "SMALL_BLUE_BARREL",
                                "quantity": barrels_purchased,
                            })
    return barrels
        