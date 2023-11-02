from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from datetime import datetime
from enum import Enum

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):

    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """
    if search_page == "":
        search_page = 0

    query = """
        SELECT carts.customer, carts.created_at, potions.sku, cart_items.quantity, potions.price
        FROM carts
        JOIN cart_items ON cart_items.cart_id = carts.cart_id
        JOIN potions ON cart_items.potion_id = potions.potion_id
        """

    res = {}

    if customer_name and potion_sku:
        query += "WHERE carts.customer ILIKE :customer AND potions.sku ILIKE :sku"
        res = {"customer": f"%{customer_name}%", "sku": f"%{potion_sku}%"}
    elif customer_name:
        query += "WHERE carts.customer ILIKE :customer"
        res = {"customer": f"%{customer_name}%"}
    elif potion_sku:
        query += "WHERE potions.sku ILIKE :sku"
        res = {"sku": f"%{potion_sku}%"}

    res["offset"] = search_page  # Replace offset_value with the desired offset

    sort_col_mapping = {
        search_sort_options.customer_name: "carts.customer",
        search_sort_options.item_sku: "cart_items.sku",
        search_sort_options.line_item_total: "cart_items.quantity * potions.price",
        search_sort_options.timestamp: "carts.created_at",
    }

    query += f"""
        ORDER BY {sort_col_mapping[sort_col]}
        {sort_order.value}
        OFFSET :offset LIMIT 6;
    """
    search_res = []
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(query), res).all()
        line_item_id = 1
        for row in result:
            search_res.append({
                "line_item_id": line_item_id,
                "item_sku": str(row.quantity) + " " + row.sku,
                "customer_name": row.customer,
                "line_item_total": row.quantity * row.price,
                "timestamp": row.created_at,
            })
        line_item_id += 1

    return {
        "previous": str(int(search_page) - 5 if int(search_page) - 5 >= 0 else ""),
        "next": str(int(search_page) + 5 if len(search_res) > 5 else ""),
        "results": search_res,
    }

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
            """), [{"potion_changed": -row.quantity, "tick_id": tick_id, "potion_id": row.potion_id}])

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