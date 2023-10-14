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
        result = connection.execute(sqlalchemy.text("SELECT SUM(inventory) AS total_potions FROM potions"))
        first_row = result.first()
        total_potions = first_row.total_potions

        result = connection.execute(sqlalchemy.text("SELECT SUM(red_ml + green_ml + blue_ml) AS total_ml FROM global_inventory"))
        first_row = result.first()
        total_ml = first_row.total_ml

        result = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
        first_row = result.first()
        tot_gold = first_row.gold

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
