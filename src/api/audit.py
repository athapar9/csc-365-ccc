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
    #just select and then set local vars to wtv is in the database
    # with db.engine.begin() as connection:
    #     connection.execute(sqlalchemy.text("SELECT num_red_potions, gold, num_red_ml SET num_red_potions = "))
    #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = 100"))
    #     connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = 0"))

    return {"number_of_potions": 0, "ml_in_barrels": 0, "gold": 100}

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
