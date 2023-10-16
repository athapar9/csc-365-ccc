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
        result = connection.execute(sqlalchemy.text("SELECT sku, name, inventory, price, type FROM potions WHERE inventory > 0 LIMIT 6"))
        catalog = []
        for row in result:
            catalog.append({
                "sku": row.sku,
                "name": row.name,
                "quantity": row.inventory,
                "price": row.price,
                "potion_type": row.type,
            })

        # red_potions_to_sell = first_row.num_red_potions
        # green_potions_to_sell = first_row.num_green_potions
        # blue_potions_to_sell = first_row.num_blue_potions
        # print(f"catalog result: {result}")

        # catalog = []
        # # if num_red_potions == 0:
        # #     return 0
        # if red_potions_to_sell > 0:
        #     catalog.append(
        #         {
        #             "sku": "RED_POTION_0",
        #             "name": "red potion",
        #             "quantity": red_potions_to_sell,
        #             "price": 50,
        #             "potion_type": [100, 0, 0, 0],
        #         })
        # if green_potions_to_sell > 0:
        #     catalog.append(
        #         {
        #             "sku": "GREEN_POTION_0",
        #             "name": "green potion",
        #             "quantity": green_potions_to_sell,
        #             "price": 50,
        #             "potion_type": [0, 100, 0, 0],
        #         })
        # if blue_potions_to_sell > 0:
        #     catalog.append(
        #         {
        #             "sku": "BLUE_POTION_0",
        #             "name": "blue potion",
        #             "quantity": blue_potions_to_sell,
        #             "price": 50,
        #             "potion_type": [0, 0, 100, 0],
        #         })
    print(f"catalog:", catalog)
    return catalog
        
