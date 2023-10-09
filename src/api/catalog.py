from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, num_blue_potions FROM global_inventory"))
        first_row = result.first()

        red_potions_to_sell = first_row.num_red_potions
        green_potions_to_sell = first_row.num_green_potions
        blue_potions_to_sell = first_row.num_blue_potions
        print(f"catalog result: {result}")

        catalog = []
        # if num_red_potions == 0:
        #     return 0
        if red_potions_to_sell > 0:
            catalog.append(
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": red_potions_to_sell,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                })
        if green_potions_to_sell > 0:
            catalog.append(
                {
                    "sku": "GREEN_POTION_0",
                    "name": "red potion",
                    "quantity": green_potions_to_sell,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                })
        if blue_potions_to_sell > 0:
            catalog.append(
                {
                    "sku": "BLUE_POTION_0",
                    "name": "red potion",
                    "quantity": blue_potions_to_sell,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                })
    print(f"catalog:", catalog)
    return catalog
        
