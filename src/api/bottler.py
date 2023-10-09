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
    
    print(potions_delivered)

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_red_ml, num_green_potions, num_green_ml, \
            num_blue_potions, num_blue_ml FROM global_inventory"))
        first_row = result.first()

        #All Vars
        cur_red_ml = first_row.num_red_ml
        cur_red_potions = first_row.num_red_potions
        cur_green_ml = first_row.num_green_ml
        cur_green_potions = first_row.num_green_potions
        cur_blue_ml = first_row.num_blue_ml
        cur_blue_potions = first_row.num_blue_potions

        print(f"pre red: ", cur_red_potions)
        print(f"pre blue: ", cur_blue_potions)
        print(f"pre green: ", cur_green_potions)
        

        for potion in potions_delivered:
            if potion.potion_type == [0, 100, 0, 0]:
                print("Delivering Green")
                print(f"pre potion quan: ", potion.quantity)
                if 100*potion.quantity <= cur_green_ml:
                    cur_green_potions += potion.quantity
                    cur_green_ml -= 100 * potion.quantity
                else:
                    print(f"not enough green, try a smaller quantity")
            if potion.potion_type == [0, 0, 100, 0]:
                if 100* potion.quantity <= cur_blue_ml:
                    print("Delivering Blue")
                    cur_blue_ml -= 100 * potion.quantity
                    cur_blue_potions += potion.quantity
                else: 
                    print(f"not enough blue,  try a smaller quantity")
            # if potion.potion_type == [100, 0, 0, 0] <= cur_red_ml:
            #     if 100* potion.quantity <= cur_red_ml:
            #         print("Delivering Red")
            #         cur_red_ml -= 100 * potion.quantity
            #         cur_red_potions += potion.quantity
            #     else:
            #         #fix these to errors later
            #         print(f"not enough red, try a smaller quantity")

        #update database
        print(f"final red ml: ", cur_red_ml)
        print(f"final blue ml: ", cur_blue_ml)
        print(f"final green ml: ", cur_green_ml)

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = :cur_red_ml"), \
            [{"cur_red_ml": cur_red_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :cur_red_potions"), \
            [{ "cur_red_potions": cur_red_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = :cur_green_ml"), \
             [{"cur_green_ml" : cur_green_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :cur_green_potions"), \
            [{"cur_green_potions": cur_green_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = :cur_blue_ml"), \
            [{"cur_blue_ml": cur_blue_ml}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :cur_blue_potions"), \
            [{"cur_blue_potions": cur_blue_potions}])
    
        print(f"final red: ", cur_red_potions)
        print(f"final blue: ", cur_blue_potions)
        print(f"final green: ", cur_green_potions)

    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_ml, num_green_ml, num_blue_ml FROM global_inventory"))
        first_row = result.first()

        cur_red_ml = first_row.num_red_ml
        cur_green_ml = first_row.num_green_ml
        cur_blue_ml = first_row.num_blue_ml

        bottles = []

    if cur_green_ml >= 100:
        print("GREEN ML")
        bottles.append(
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": cur_green_ml // 100,
            }
        )
    if cur_blue_ml >= 100:
        bottles.append(
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": cur_blue_ml // 100,
            }
        )
    # if cur_red_ml >= 100:
    #     bottles.append(
    #         {
    #             "potion_type": [100, 0, 0, 0],
    #             "quantity": cur_red_ml // 100,
    #         }
    #     )
    print(f"bottles:", bottles)
    return bottles
