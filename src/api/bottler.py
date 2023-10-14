from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    with db.engine.begin() as connection:
        print(potions_delivered)
        total_potions = sum(p.quantity for p in potions_delivered)
        red_ml = sum(p.quantity * p.potion_type[0] for p in potions_delivered)
        green_ml = sum(p.quantity * p.potion_type[1] for p in potions_delivered)
        blue_ml = sum(p.quantity * p.potion_type[2] for p in potions_delivered)
        dark_ml = sum(p.quantity * p.potion_type[3] for p in potions_delivered)
        # print(potions.potion_type) 

        # result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml, num_green_potions, num_green_ml, \
        #     num_blue_potions, num_blue_ml FROM global_inventory"))
        # first_row = result.first()

        # #All Vars
        # cur_red_ml = first_row.num_red_ml
        # cur_red_potions = first_row.num_red_potions
        # cur_green_ml = first_row.num_green_ml
        # cur_green_potions = first_row.num_green_potions
        # cur_blue_ml = first_row.num_blue_ml
        # cur_blue_potions = first_row.num_blue_potions
        
        for potions in potions_delivered:
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE potions
                    SET inventory = inventory + :total_potions
                    WHERE type = :potion_type
                    """
                ),
                [{"total_potions": potions.quantity,  
                "potion_type": potions.potion_type}]
            )
        connection.execute(
            sqlalchemy.text("""
                            UPDATE global_inventory 
                            SET 
                            red_ml = red_ml - :red_ml,
                            green_ml = green_ml - :green_ml,
                            blue_ml = blue_ml - :blue_ml,
                            dark_ml = dark_ml - :dark_ml,
                            total_potions = total_potions +:total_potions
                            """),
            [{"red_ml": red_ml, "green_ml": green_ml, "blue_ml": blue_ml, "dark_ml": dark_ml, "total_potions": total_potions}])
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT red_ml, blue_ml, green_ml, dark_ml, gold FROM global_inventory"))
        first_row = result.first()

        red_ml = first_row.red_ml
        blue_ml = first_row.blue_ml
        green_ml = first_row.green_ml
        dark_ml = first_row.dark_ml

        ordered_potions = connection.execute(sqlalchemy.text("SELECT * FROM potions ORDER BY inventory"))

        bottles = []

        for potion in ordered_potions:
            inventory = 0
            while (red_ml >= potion.type[0] and green_ml >= potion.type[1] and blue_ml >= potion.type[2] and dark_ml >= potion.type[3]):
                red_ml -= potion.type[0]
                green_ml -= potion.type[1]
                blue_ml -= potion.type[2]
                dark_ml -= potion.type[3]
                inventory += 1
            
            if inventory > 0:
                bottles.append(
                        {
                            "potion_type": [potion.type[0], potion.type[1], potion.type[2], potion.type[3]],
                            "quantity": inventory,
                        })
                # print("red_ml", red_ml)
                # print("green_ml", green_ml)
                # print("blue_ml", blue_ml)
                # print("dark_ml", dark_ml)
                # print("red_required", potion.type[0])
                # print("green_required", potion.type[1])
                # print("blue_required", potion.type[2])
                # print("dark_required", potion.type[3])
                # print("inventory", inventory)
        print(f"bottles:", bottles)
        return bottles
