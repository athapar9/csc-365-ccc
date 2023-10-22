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
        result = connection.execute(sqlalchemy.text("""
        SELECT sku, name, inventory, price, type, SUM(potion_ledger_items.potion_changed) 
        AS inventory FROM potions
        JOIN potion_ledger_items ON potions.potion_id = potion_ledger_items.potion_id
        GROUP BY potions.potion_id
        HAVING SUM(potion_ledger_items.potion_changed) > 0 LIMIT 6
        """))
        catalog = []
        for row in result:
            catalog.append({
                "sku": row.sku,
                "name": row.name,
                "quantity": row.inventory,
                "price": row.price,
                "potion_type": row.type,
            })

    print(f"catalog:", catalog)
    return catalog
        
