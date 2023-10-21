from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    with db.engine.begin() as connection:
            result = connection.execute(sqlalchemy.text(
                """INSERT INTO carts 
                (customer) 
                VALUES 
                (:customer_name) 
                RETURNING cart_id
                """), 
                [{"customer_name": new_cart.customer}])
            cart_id = result.scalar()

    return {"cart_id": cart_id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    return cart_id

class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text(
                """
                INSERT INTO cart_items 
                (cart_id, quantity, potion_id) 
                SELECT :cart_id, :quantity, potion_id 
                FROM potions WHERE potions.sku = :item_sku
                """),
            [{"cart_id": cart_id, "quantity": cart_item.quantity, "item_sku": item_sku}])
    print("CURRENT CART: ", item_sku, " NO.ITEMS: ", cart_item.quantity)       

    return "OK"

class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    gold_paid = 0
    potions_bought = 0

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text(
            """
            UPDATE potions
            SET inventory = potions.inventory - cart_items.quantity
            FROM cart_items
            WHERE potions.potion_id = cart_items.potion_id and cart_items.cart_id = :cart_id;
            """),
            [{"cart_id": cart_id}])
        
        result = connection.execute(sqlalchemy.text("SELECT SUM(potions.price * cart_items.quantity)\
             AS gold_paid, SUM(cart_items.quantity) \
                AS potions_bought FROM potions JOIN cart_items \
                    ON potions.potion_id = cart_items.potion_id WHERE cart_items.cart_id = :cart_id"), \
                        [{"cart_id": cart_id}])

        first_row = result.first()
        gold_paid = first_row.gold_paid
        potions_bought = first_row.potions_bought

        connection.execute(sqlalchemy.text("""
            UPDATE global_inventory 
            SET gold = gold + :gold_paid,
            total_potions = total_potions
            """),
            [{"potions_bought": potions_bought, "gold_paid": gold_paid}])

    print("total_potions_bought:", {potions_bought}, "total_gold_paid:", {gold_paid})    
    return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}