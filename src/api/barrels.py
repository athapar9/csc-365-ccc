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
   
    tot_gold = 0
    red_ml = 0
    blue_ml = 0
    green_ml = 0
    dark_ml = 0

    for barrel in barrels_delivered:
        tot_gold += barrel.price * barrel.quantity
        if barrel.potion_type == [1,0,0,0]:
            red_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0,1,0,0]:
            green_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0,0,1,0]:
            blue_ml += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type == [0,0,0,1]:
            dark_ml += barrel.ml_per_barrel * barrel.quantity
        else:
            raise Exception("Invalid potion type")

        print(f"gold_paid: {tot_gold} red_ml: {red_ml} blue_ml: {blue_ml} green_ml: {green_ml} dark_ml: {dark_ml}")
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE global_inventory SET 
                    red_ml = red_ml + :red_ml,
                    green_ml = green_ml + :green_ml,
                    blue_ml = blue_ml + :blue_ml,
                    dark_ml = dark_ml + :dark_ml,
                    gold = gold - :tot_gold
                    """),
                [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml, "tot_gold": tot_gold}])
        return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_blue_potions, num_green_potions, gold FROM global_inventory"))
    print(f"catalog result: {result}")
    first_row = result.first()

    #current status of all vars
    cur_red_potions = first_row.num_red_potions
    cur_blue_potions = first_row.num_blue_potions
    cur_green_potions = first_row.num_green_potions
    cur_gold = first_row.gold

    #barrels to buy
    purchased_red_potions = 0
    purchased_green_potions = 0
    purchased_blue_potions = 0

    tot_red_ml = 0
    tot_green_ml = 0
    tot_blue_ml = 0

    barrels = []

    #RED
    for barrel in wholesale_catalog:
        barrels_purchased = 0
        if "red" in barrel.sku.lower():
                if cur_red_potions < 10:
                    if cur_gold >= barrel.price * barrel.quantity and purchased_red_potions < 10:
                        print("BUYING RED BARREL:", barrel.quantity)
                        barrels_purchased += barrel.quantity
                        barrel.quantity -= barrels_purchased
                        cur_gold -= barrel.price
                        tot_red_ml += barrel.ml_per_barrel
                        purchased_red_potions = tot_red_ml // 100
                        if barrels_purchased > 0:
                            barrels.append(
                                {
                                    "sku": "SMALL_RED_BARREL",
                                    "quantity": barrels_purchased,
                                })
        #BLUE
        if "blue" in barrel.sku.lower():
            if cur_blue_potions < 10:
                if cur_gold >= barrel.price * barrel.quantity and purchased_blue_potions < 10:
                    print("BUYING BLUE BARREL:", barrel.quantity)
                    barrels_purchased += barrel.quantity
                    barrel.quantity -= barrels_purchased
                    cur_gold -= barrel.price
                    tot_blue_ml += barrel.ml_per_barrel
                    purchased_blue_potions = tot_blue_ml // 100
                    if barrels_purchased > 0:
                        barrels.append(
                            {
                                "sku": "SMALL_BLUE_BARREL",
                                "quantity": barrels_purchased,
                            })
        # GREEN
        elif "green" in barrel.sku.lower():
            if cur_green_potions < 10:
                if cur_gold >= barrel.price * barrel.quantity and purchased_green_potions < 10:
                    print("BUYING GREEN BARRELS:", barrel.quantity)
                    barrels_purchased += barrel.quantity
                    barrel.quantity -= barrels_purchased
                    cur_gold -= barrel.price
                    tot_green_ml += barrel.ml_per_barrel
                    purchased_green_potions = tot_green_ml // 100
                    if barrels_purchased > 0:
                        barrels.append(
                            {
                                "sku": "SMALL_GREEN_BARREL",
                                "quantity": barrels_purchased,
                            })
    print(f"barrels:", barrels)
    return barrels
        