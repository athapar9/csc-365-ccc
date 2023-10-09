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

cart_id = 0
cart_dict = {}
#unique key and then num_items is id?

@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    #counter to update cart_id
    #add new entry
    global cart_id
    cart_id += 1
    cart_dict[cart_id] = {}
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
    current_cart = cart_dict[cart_id]
    current_cart[item_sku] = cart_item.quantity
    print("current cart: ", current_cart)

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
    gold_paid = 0
    potions_bought = 0
    
    print(f"cur_cart", cur_cart)
    print(f"cart_id", cart_id)
    print(f"payment", cart_checkout)

    with db.engine.begin() as connection:
        for item_sku, quantity in cur_cart.items():
            result = connection.execute(sqlalchemy.text("SELECT num_red_potions, num_green_potions, \
                num_blue_potions, gold FROM global_inventory"))
            first_row = result.first()

            cur_red_potions = first_row.num_red_potions
            cur_green_potions = first_row.num_green_potions
            cur_blue_potions = first_row.num_blue_potions
            tot_gold = first_row.gold
            print("totals before checkout; num_red_potions: {cur_red_potions}; \
                num_blue_potions: {cur_blue_potions}, \
                    num_green_potions: {cur_green_potions},\
                         Gold: {tot_gold}")

            if item_sku == "RED_POTION_0" and cur_red_potions >= quantity:
                print(f"Proceed Red")
                cur_red_potions -= quantity
                tot_gold += quantity * 500
                potions_bought += quantity
                gold_paid += quantity * 500
                print(f"num_red_potions", cur_red_potions)
                print(f"cur_gold", tot_gold)
            elif item_sku == "BLUE_POTION_0" and cur_blue_potions >= quantity:
                print(f"Proceed Blue")
                cur_blue_potions -= quantity
                tot_gold += quantity * 50 
                potions_bought += quantity
                gold_paid += quantity * 50 
            elif item_sku == "GREEN_POTION_0" and cur_green_potions >= quantity:
                print(f"Proceed Green")
                cur_green_potions -= quantity
                tot_gold += quantity * 50
                potions_bought += quantity
                gold_paid += quantity * 50
            else:
                print(f"Item_sku Entered is Incorrect") 

            print("totals post checkout; num_red_potions: {cur_red_potions}; \
                num_blue_potions: {cur_blue_potions}, \
                    num_green_potions: {cur_green_potions},\
                         Gold: {tot_gold}")

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = :tot_gold"), [{"tot_gold": tot_gold }])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = :cur_red_potions"), [{"cur_red_potions" : cur_red_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = :cur_green_potions"), [{"cur_green_potions" : cur_green_potions}])
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = :cur_blue_potions"), [{"cur_blue_potions" : cur_blue_potions}])

    return {"total_potions_bought": potions_bought, "total_gold_paid": gold_paid}