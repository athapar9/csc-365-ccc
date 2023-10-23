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
        result = connection.execute(sqlalchemy.text("SELECT SUM(potion_changed) AS total_potions FROM potion_ledger_items"))
        first_row = result.first()
        total_potions = first_row.total_potions

        result = connection.execute(sqlalchemy.text("SELECT SUM(red_ml_changed + green_ml_changed + blue_ml_changed) AS total_ml FROM barrel_ledger_items"))
        first_row = result.first()
        total_ml = first_row.total_ml

        result = connection.execute(sqlalchemy.text("SELECT SUM(gold_changed) AS gold FROM gold_ledger_items"))
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
