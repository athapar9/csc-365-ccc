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

# List cart = []

class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    #counter to update cart_id
    #add new entry

    return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    #displaying cart
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    #similar to plan
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #executing
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
    return {"total_potions_bought": 1, "total_gold_paid": 50}
