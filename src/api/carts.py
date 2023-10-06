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

cart_dict = {}

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    #counter to update cart_id
    #add new entry
    cart_id = 0
 
    for cart in new_cart:
        if cart not in cart_dict:
            cart_dict[cart_id] += 1
        else:
            cart_dict[cart_id] = 0
    return {"cart_id": cart_id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    #displaying cart
    return cart_dict


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    cart_dict[cart_id][item_sku] = cart_item.quantity
    #similar to plan
    return "OK"



class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #executing
    # current_cart = cart_dict[cart_id]
    # for items in current_cart:
    return {"total_potions_bought": 1, "total_gold_paid": 50}