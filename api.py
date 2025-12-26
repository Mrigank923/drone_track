import os
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import List, Optional
import json

from database import get_db
import schemas
from ws_manager import manager

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


# WebSocket endpoint for live drone tracking
@router.websocket("/ws/drone")
async def websocket_drone_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time drone position updates.
    Clients connect here to receive live drone coordinates as they're updated.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and listen for any incoming messages
            # (clients can optionally send auth or other control messages)
            data = await websocket.receive_text()
            # You can process incoming messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)

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

    # Broadcast the new drone position to all connected WebSocket clients
    await manager.broadcast({
        "type": "drone_position",
        "data": payload
    })

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

# create a safe path block
@router.post("/safe_paths", response_model=schemas.SafePathCreate)
async def create_safe_path(safe_path: schemas.SafePathCreate, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(safe_path.auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    doc = {"block_latitude": safe_path.block_latitude, "block_longitude": safe_path.block_longitude}
    result = await db["safe_paths"].insert_one(doc)
    inserted = await db["safe_paths"].find_one({"_id": result.inserted_id})
    return _serialize_doc(inserted)

# delete all safe paths (requires auth_key as query parameter)
@router.delete("/safe_paths")
async def delete_safe_paths(auth_key: str, db=Depends(get_db)):
    # verify auth key
    if not _verify_key(auth_key):
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    result = await db["safe_paths"].delete_many({})
    return JSONResponse({"status": "deleted", "count": result.deleted_count})

# get all safe paths
@router.get("/safe_paths", response_model=List[schemas.SafePathOut])
async def get_safe_paths(db=Depends(get_db)):
    cursor = db["safe_paths"].find()
    docs = await cursor.to_list(length=None)
    return [_serialize_doc(d) for d in docs]
 
 # get latest safe path
@router.get("/safe_paths/latest", response_model=schemas.SafePathOut)
async def latest_safe_path(db=Depends(get_db)):
    doc = await db["safe_paths"].find_one(sort=[("_id", -1)])
    if not doc:
        return JSONResponse({"error": "not found"}, status_code=404)
    return _serialize_doc(doc)