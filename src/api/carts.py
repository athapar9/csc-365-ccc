from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime

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

    date = datetime.now()
    time = date.strftime("%m/%d/%Y %H:%M:%S")

    description = "CHECKOUT AT " + time + " cart_id: " + str(cart_id) + " payment: " + cart_checkout.payment
    print(description)

    with db.engine.begin() as connection:
        tick_id = connection.execute(sqlalchemy.text(
            """
            INSERT INTO ticks (description)
            VALUES (:description)
            RETURNING tick_id
            """), 
            [{"description": description}]).scalar()
        
        result = connection.execute(sqlalchemy.text(
            """
            SELECT quantity, potion_id
            FROM cart_items
            WHERE cart_items.cart_id = :cart_id
            """), [{"cart_id": cart_id}])

        for row in result:
            connection.execute(sqlalchemy.text(
            """
            INSERT INTO potion_ledger_items (potion_changed, tick_id, potion_id)
            VALUES (:potion_changed, :tick_id, :potion_id)
            """), {"potion_changed": -row.quantity, "tick_id": tick_id, "potion_id": row.potion_id})

        result = connection.execute(sqlalchemy.text("SELECT SUM(potions.price * cart_items.quantity)\
             AS gold_paid, SUM(cart_items.quantity) \
                AS potions_bought FROM potions JOIN cart_items \
                    ON potions.potion_id = cart_items.potion_id WHERE cart_items.cart_id = :cart_id"), \
                        [{"cart_id": cart_id}])

        first_row = result.first()
        gold_paid = first_row.gold_paid
        potions_bought = first_row.potions_bought

        connection.execute(sqlalchemy.text(
            """INSERT INTO gold_ledger_items (gold_changed, tick_id)
            VALUES (:gold_changed, :tick_id)
            """), {"gold_changed": gold_paid, "tick_id": tick_id})

    print("total_potions_bought:", {potions_bought}, "total_gold_paid:", {gold_paid})    
    return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}