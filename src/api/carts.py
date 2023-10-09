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
#unique key and then num_items is id?

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    #counter to update cart_id
    #add new entry

    print(f"create_cart: new_cart {new_cart}")
    cart_id = 1
    for cart_id in cart_dict:
        cart_id += 1
    cart_dict[cart_id] = {"new_cart":new_cart}
    print(f"cart dict:", cart_dict)
    return {"cart_id": cart_id}

@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """
    #displaying cart
    print(f"cart id", cart_id)
    return cart_dict[cart_id]


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    #similar to plan
    cart = get_cart(cart_id)
    print(f"cart", cart)
    print(f"quantity", cart_item)
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, \
            num_blue_potions, num_blue_ml, gold FROM global_inventory"))
        first_row = result.first()

        num_red_potions = first_row.num_red_potions
        num_green_potions = first_row.num_green_potions
        num_blue_potions = first_row.num_blue_potions
        cur_gold = first_row.gold
        for items in cart: 
            if item_sku == "RED_POTION_0" and num_red_potions >= cart_item.quantity:
                print(f"Proceed Red")
                # num_red_potions -= cart_item.quantity
                # cur_gold += cart_item.quantity * 50
                print(f"num_red_potions", num_red_potions)
                print(f"cur_gold", cur_gold)
            elif item_sku == "BLUE_POTION_0" and num_blue_potions >= cart_item.quantity:
                print(f"Proceed Blue")
                num_blue_potions -= cart_item.quantity
                cur_gold += cart_item.quantity * 50  
            elif item_sku == "GREEN_POTION_0" and num_green_potions >= cart_item.quantity:
                print(f"Proceed Green")
                num_green_potions -= cart_item.quantity
                cur_gold += cart_item.quantity * 50
            else:
                print(f"Item_sku Entered is Incorrect")

    return "OK"



class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """
    #executing
    # current_cart = cart_dict[cart_id]
    # for items in current_cart:

    cur_cart = cart_dict[cart_id]
    items_purchased = 0
    gold_spent = 0
    print(f"cur_cart", cur_cart)
    print(f"cart_id", cart_id)
    print(f"payment", cart_checkout)
    
 

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, \
            num_blue_potions, gold FROM global_inventory"))
        first_row = result.first()

        num_red_potions = first_row.num_red_potions
        num_green_potions = first_row.num_green_potions
        num_blue_potions = first_row.num_blue_potions
        cur_gold = first_row.gold
        print(f"num_red", num_red_potions)
        print(f"num_gold", cur_gold)
        

    return {"total_potions_bought": 1, "total_gold_paid": 50}