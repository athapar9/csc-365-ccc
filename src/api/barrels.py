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
        result = connection.execute(sqlalchemy.text("SELECT red_ml, blue_ml, green_ml, gold FROM global_inventory"))
    print(f"catalog result: {result}")
    first_row = result.first()

    tot_gold = first_row.gold
    red_ml = first_row.red_ml
    green_ml = first_row.green_ml
    blue_ml = first_row.blue_ml

    barrels = []

    #RED
    for barrel in wholesale_catalog:
        barrels_purchased = 0
        if "red" in barrel.sku.lower():
            while barrels_purchased < 1 and tot_gold >= barrel.price * barrel.quantity:
                barrels_purchased += barrel.quantity
                barrel.quantity -= barrels_purchased
                tot_gold -= barrel.price
                red_ml += barrel.ml_per_barrel
                if barrels_purchased > 0:
                    barrels.append(
                        {
                            "sku": barrel.sku,
                            "ml_per_barrel": barrel.ml_per_barrel,
                            "potion_type": barrel.potion_type,
                            "price": barrel.price,
                            "quantity": barrels_purchased
                        })
        #BLUE
        elif "blue" in barrel.sku.lower():
            while tot_gold >= barrel.price * barrel.quantity:
                barrels_purchased += barrel.quantity
                barrel.quantity -= barrels_purchased
                tot_gold -= barrel.price
                blue_ml += barrel.ml_per_barrel
                if barrels_purchased > 0:
                    barrels.append(
                        {
                            "sku": barrel.sku,
                            "ml_per_barrel": barrel.ml_per_barrel,
                            "potion_type": barrel.potion_type,
                            "price": barrel.price,
                            "quantity": barrels_purchased
                        })
        # GREEN
        elif "green" in barrel.sku.lower():
            while tot_gold >= barrel.price * barrel.quantity:
                barrels_purchased += barrel.quantity
                barrel.quantity -= barrels_purchased
                tot_gold -= barrel.price
                green_ml += barrel.ml_per_barrel
                if barrels_purchased > 0:
                    barrels.append(
                        {
                            "sku": barrel.sku,
                            "ml_per_barrel": barrel.ml_per_barrel,
                            "potion_type": barrel.potion_type,
                            "price": barrel.price,
                            "quantity": barrels_purchased
                        })
    print(f"barrels:", barrels)
    return barrels