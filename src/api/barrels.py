from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime

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

    date = datetime.now()
    time = date.strftime("%m/%d/%Y %H:%M:%S")

    description = "BARRELS DELIVERED AT " + time + " red: " + str(red_ml) + " green: " + str(green_ml) + " blue: " + str(blue_ml)
    print(description)

    with db.engine.begin() as connection:
        tick_id = connection.execute(sqlalchemy.text(
            """INSERT INTO ticks (description) 
            VALUES (:description) 
            RETURNING tick_id"""), 
            [{"description": description}]).scalar()
        
        connection.execute(sqlalchemy.text(
            """INSERT INTO barrel_ledger_items (tick_id, red_ml_changed, green_ml_changed, blue_ml_changed, dark_ml_changed) 
            VALUES (:tick_id, :red_ml, :green_ml, :blue_ml, :dark_ml)
            """), 
            [{"tick_id": tick_id, "red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml}])


        connection.execute(sqlalchemy.text("""
                                            INSERT INTO gold_ledger_items (gold_changed, tick_id)
                                            VALUES (:gold, :tick_id)
                                                """), 
                                                [{"gold": -tot_gold, "tick_id": tick_id}])
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(f"barrel catalog: {wholesale_catalog}")
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(red_ml_changed) AS red_ml, 
            SUM(green_ml_changed) AS green_ml, 
            SUM(blue_ml_changed) AS blue_ml 
            FROM barrel_ledger_items
            """))
        print(f"catalog result: {result}")
        first_row = result.first()

        red_ml = first_row.red_ml
        green_ml = first_row.green_ml
        blue_ml = first_row.blue_ml
        
    barrels = []

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(gold_changed) 
            AS gold
            FROM gold_ledger_items
            """))
        first_row = result.first()
        tot_gold = first_row.gold
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(potion_changed) 
            AS total_potions
            FROM potion_ledger_items
            """)) 
        
        first_row = result.first()
        tot_potions = first_row.total_potions
        print("IN BARRELS PLAN, potions in inventory: ", tot_potions)
    
    #Cap on Potions is 300
    potions_possible = 300 - tot_potions
    ml_possible = potions_possible * 100
    red_possible = ml_possible 
    blue_possible = 0
    green_possible = 0

    print("potions_possible:", potions_possible, "ml_possible:", ml_possible, \
        "red_possible:", red_possible, "blue_possible:", blue_possible, "green_possible:", green_possible)

    #RED
    if tot_potions < 300:
        for barrel in wholesale_catalog:
            print(barrel)
            barrels_purchased = 0
            if "red" in barrel.sku.lower():
                while red_possible > 0 and tot_gold >= barrel.price and barrels_purchased < barrel.quantity:
                    barrels_purchased += 1
                    tot_gold -= barrel.price
                    red_possible -= barrel.ml_per_barrel
                    barrel.quantity -= 1
            #BLUE
            elif "blue" in barrel.sku.lower():
                while blue_possible > 0 and tot_gold >= barrel.price and barrels_purchased < barrel.quantity:
                    barrels_purchased += 1
                    tot_gold -= barrel.price
                    blue_possible -= barrel.ml_per_barrel
                    barrel.quantity -= 1
            # GREEN
            elif "green" in barrel.sku.lower():
                while green_possible > 0 and tot_gold >= barrel.price and barrels_purchased < barrel.quantity:
                    barrels_purchased += 1
                    tot_gold -= barrel.price
                    green_possible -= barrel.ml_per_barrel
                    barrel.quantity -= 1
            if barrels_purchased > 0:
                barrels.append(
                    {
                        "sku": barrel.sku,
                        "ml_per_barrel": barrel.ml_per_barrel,
                        "potion_type": barrel.potion_type,
                        "price": barrel.price,
                        "quantity": barrels_purchased
                    })
        print(f"barrels: {barrels}")
        return barrels