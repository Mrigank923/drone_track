import os
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional

from database import get_db
import schemas

router = APIRouter()

# Authentication key used to accept POST requests. Set via environment variable `AUTH_KEY`.
AUTH_KEY = os.getenv("AUTH_KEY", "devkey")


def _verify_key(provided: str) -> bool:
    return provided == AUTH_KEY


def _serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict with string id."""
    if not doc:
        return doc
    out = dict(doc)
    _id = out.pop("_id", None)
    if _id is not None:
        out["id"] = str(_id)
    return out

# create a mine
@router.post("/mines", response_model=schemas.CoordOut)
async def create_mine(mine: schemas.MineCreate, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(mine.auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    doc = {"latitude": mine.latitude, "longitude": mine.longitude, "label": mine.label}
    result = await db["mines"].insert_one(doc)
    inserted = await db["mines"].find_one({"_id": result.inserted_id})
    return _serialize_doc(inserted)

# delete all mines (requires auth_key as query parameter)
@router.delete("/mines")
async def delete_mines(auth_key: str, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    result = await db["mines"].delete_many({})
    return JSONResponse({"status": "deleted", "count": result.deleted_count})

# create a pole
@router.post("/poles", response_model=schemas.CoordOut)
async def create_pole(pole: schemas.PoleCreate, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(pole.auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    doc = {"latitude": pole.latitude, "longitude": pole.longitude, "label": pole.label}
    result = await db["poles"].insert_one(doc)
    inserted = await db["poles"].find_one({"_id": result.inserted_id})
    return _serialize_doc(inserted)

# delete all poles (requires auth_key as query parameter)
@router.delete("/poles")
async def delete_poles(auth_key: str, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    result = await db["poles"].delete_many({})
    return JSONResponse({"status": "deleted", "count": result.deleted_count})

# create a drone position
@router.post("/drone")
async def receive_drone(drone: schemas.DroneCreate, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(drone.auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    doc = {"latitude": drone.latitude, "longitude": drone.longitude}
    result = await db["drone_positions"].insert_one(doc)
    inserted = await db["drone_positions"].find_one({"_id": result.inserted_id})
    payload = _serialize_doc(inserted)

    # No websocket: frontend should poll or call the API to fetch positions
    return JSONResponse({"status": "ok", "data": payload})

# delete all drone positions (requires auth_key as query parameter)
@router.delete("/drone")
async def delete_drone(auth_key: str, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    result = await db["drone_positions"].delete_many({})
    return JSONResponse({"status": "deleted", "count": result.deleted_count})

# get all poles
@router.get("/poles", response_model=List[schemas.CoordOut])
async def get_poles(db=Depends(get_db)):
    cursor = db["poles"].find()
    docs = await cursor.to_list(length=None)
    return [_serialize_doc(d) for d in docs]

# get all mines
@router.get("/mines", response_model=List[schemas.CoordOut])
async def get_mines(db=Depends(get_db)):
    cursor = db["mines"].find()
    docs = await cursor.to_list(length=None)
    return [_serialize_doc(d) for d in docs]

# get all drone positions
@router.get("/drone", response_model=List[schemas.CoordOut])
async def list_drone(db=Depends(get_db)):
    """Return all drone positions."""
    cursor = db["drone_positions"].find()
    docs = await cursor.to_list(length=None)
    return [_serialize_doc(d) for d in docs]

# get latest drone position
@router.get("/drone/latest", response_model=schemas.CoordOut)
async def latest_drone(db=Depends(get_db)):
    doc = await db["drone_positions"].find_one(sort=[("_id", -1)])
    if not doc:
        return JSONResponse({"error": "not found"}, status_code=404)
    return _serialize_doc(doc)
