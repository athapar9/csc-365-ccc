from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime


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
        additional_potions = sum(p.quantity for p in potions_delivered)
        red_ml = sum(p.quantity * p.potion_type[0] for p in potions_delivered)
        green_ml = sum(p.quantity * p.potion_type[1] for p in potions_delivered)
        blue_ml = sum(p.quantity * p.potion_type[2] for p in potions_delivered)
        dark_ml = sum(p.quantity * p.potion_type[3] for p in potions_delivered)
        
        date = datetime.now()
        time = date.strftime("%m/%d/%Y %H:%M:%S")

        description = "POTIONS DELIVERED AT " + time 
        print(description)
        with db.engine.begin() as connection:
            tick_id = connection.execute(sqlalchemy.text(
                """INSERT INTO ticks (description) 
                VALUES (:description) 
                RETURNING tick_id"""), 
                [{"description": description}]).scalar()
            for potions in potions_delivered:
                connection.execute(sqlalchemy.text(
                    """INSERT INTO potion_ledger_items (potion_changed, tick_id, potion_id) 
                    SELECT :potion_changed, :tick_id, potion_id 
                    FROM potions
                    WHERE potions.type = :potion_type
                    """), [{"potion_changed": potions.quantity, "tick_id": tick_id, "potion_type": potions.potion_type}])
                
            
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO barrel_ledger_items 
                (tick_id, red_ml_changed, green_ml_changed, blue_ml_changed, dark_ml_changed)
                VALUES (:tick_id, :red_ml_changed, :green_ml_changed, :blue_ml_changed, :dark_ml_changed)
                """), 
                [{"tick_id": tick_id, 
                "red_ml_changed": -red_ml, 
                "green_ml_changed": -green_ml, 
                "blue_ml_changed": -blue_ml,
                "dark_ml_changed": -dark_ml}])
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(
            """
            SELECT potions.type, SUM(potion_ledger_items.potion_changed) AS quantity
            FROM potions
            JOIN potion_ledger_items ON potions.potion_id = potion_ledger_items.potion_id
            GROUP BY potions.type
            ORDER BY quantity
            """))
            
        bottles = [] 
        ordered_potions = result.fetchall()  

        result = connection.execute(sqlalchemy.text(
            "SELECT SUM(potion_changed) AS total_potions FROM potion_ledger_items"))
        first_row = result.first()
        tot_potions = first_row.total_potions 

        barrels = connection.execute(sqlalchemy.text(
            """
            SELECT SUM(red_ml_changed) AS red_ml, 
            SUM(green_ml_changed) AS green_ml, 
            SUM(blue_ml_changed) AS blue_ml, 
            SUM(dark_ml_changed) AS dark_ml
            FROM barrel_ledger_items
            """))
        
        barrels = barrels.first()
        red_ml = barrels.red_ml
        green_ml = barrels.green_ml
        blue_ml = barrels.blue_ml
        dark_ml = barrels.dark_ml
        total_ml = red_ml + green_ml + blue_ml + dark_ml
        
        potential_bottles = (total_ml) // 100
        bottles_per_type = potential_bottles // 6

        if bottles_per_type == 0 and potential_bottles > 0:
            bottles_per_type = potential_bottles
        elif green_ml > 0 and red_ml == 0 and blue_ml == 0:
            bottles_per_type = potential_bottles
        elif red_ml > 0 and blue_ml == 0 and  green_ml== 0:
            bottles_per_type = potential_bottles
        elif blue_ml > 0 and green_ml == 0 and red_ml == 0:
            bottles_per_type = potential_bottles  

        for potion in ordered_potions:
            inventory = 0
            while (tot_potions < 300 and potential_bottles > 0 and inventory < bottles_per_type and red_ml >= potion.type[0] and green_ml >= potion.type[1] and blue_ml >= potion.type[2] and dark_ml >= potion.type[3]):
                red_ml -= potion.type[0]
                blue_ml -= potion.type[2]
                green_ml -= potion.type[1]
                dark_ml -= potion.type[3]
                inventory += 1
                potential_bottles -= 1
                tot_potions += 1
                
            if inventory > 0:
                bottles.append(
                        {
                            "potion_type": potion.type,
                            "quantity": inventory,
                        })

        if red_ml // 100 > 0:
            remaining = 300 - tot_potions
            if red_ml//100 <= remaining:
                bottles.append(
                    {
                        "potion_type": [100, 0, 0, 0],
                        "quantity": red_ml//100
                    }
                )
                tot_potions += red_ml // 100

        if green_ml // 100 > 0:
            remaining = 300 - tot_potions
            if green_ml//100 <= remaining:
                bottles.append(
                    {
                        "potion_type": [0, 100, 0, 0],
                        "quantity": green_ml//100
                    }
                )
                tot_potions += green_ml // 100

        if blue_ml // 100 > 0:
            remaining = 300 - tot_potions
            if blue_ml//100 <= remaining:
                bottles.append(
                    {
                        "potion_type": [0, 0, 100, 0],
                        "quantity": blue_ml//100
                    }
                )
                tot_potions += blue_ml // 100
        print(f"bottles:", bottles)
        return bottles
