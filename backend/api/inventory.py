from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..data.inventory_db import (
    create_inventory,
    initialize_inventory_database,
    list_decay_history,
    list_inventory,
    update_inventory,
)
from .predict import PredictRequest, run_prediction

router = APIRouter()


class InventoryCreateRequest(BaseModel):
    id: str
    batch: str
    supplier: str
    variety: str
    shelf: str
    ph: float = Field(ge=0, le=14)
    moisture: float = Field(ge=0, le=1.5)
    temp: float = Field(ge=-50, le=80)


class InventoryUpdateRequest(BaseModel):
    temp: float | None = Field(default=None, ge=-50, le=80)


@router.on_event("startup")
def initialize_database() -> None:
    initialize_inventory_database()


@router.get("/inventory")
def get_inventory():
    return list_inventory()


@router.get("/inventory/decay")
def get_inventory_decay():
    return list_decay_history()


@router.post("/inventory", status_code=201)
def add_inventory(request: InventoryCreateRequest):
    try:
        values = request.model_dump()
        prediction = run_prediction(PredictRequest(
            variety=values["variety"],
            shelf=values["shelf"],
            ph=values["ph"],
            moisture=values["moisture"],
            temperatures=[values["temp"] - 1, values["temp"], values["temp"], values["temp"], values["temp"]],
        ))
        values["status"] = prediction["status"]
        values["days"] = prediction["predicted_days"]
        return create_inventory(values)
    except HTTPException:
        raise
    except sqlite3.IntegrityError as error:
        raise HTTPException(status_code=409, detail="Inventory batch ID already exists.") from error
    except Exception as error:
        raise HTTPException(status_code=503, detail="Inventory batch could not be created and analyzed.") from error


@router.patch("/inventory/{item_id}")
def edit_inventory(item_id: str, request: InventoryUpdateRequest):
    try:
        updated = update_inventory(item_id, request.model_dump(exclude_none=True))
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    if updated is None:
        raise HTTPException(status_code=404, detail="Inventory batch not found.")
    return updated
