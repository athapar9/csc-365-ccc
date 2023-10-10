from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))
        first_row = result.first()
        red = first_row.num_red_potions
        green = first_row.num_green_potions
        blue = first_row.num_blue_potions
        red_ml = first_row.num_red_ml
        green_ml = first_row.num_green_ml
        blue_ml = first_row.num_blue_ml
        tot_gold = first_row.gold
        total_potions = red + green + blue
        total_ml = red_ml + green_ml + blue_ml
    
    return {"number_of_potions": total_potions, "ml_in_barrels": total_ml, "gold": tot_gold}


class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
