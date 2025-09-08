from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.dependencies.db import get_db
from app.services.qr import verify_action
from app.utils.ids import new_id

router = APIRouter()


class GeoPoint(BaseModel):
    latitude: float
    longitude: float


class RequestCreate(BaseModel):
    containerId: str
    householdId: str
    geoAtRequest: GeoPoint | None = None


class RequestOut(BaseModel):
    id: str
    status: str


@router.post("/collection-requests", response_model=RequestOut)
async def create_collection_request(payload: RequestCreate, sig: str = Query(...)):
    if not verify_action(payload.containerId, sig):
        raise HTTPException(
            status_code=401, detail="Invalid or expired QR signature")

    db = get_db()
    container = await db.containers.find_one({"_id": payload.containerId})
    if not container or container.get("assignedHouseholdId") != payload.householdId:
        raise HTTPException(
            status_code=400, detail="Container not assigned to household")

    now = datetime.now(timezone.utc).isoformat()
    req_id = new_id("req")
    doc = {
        "_id": req_id,
        "householdId": payload.householdId,
        "containerId": payload.containerId,
        "requestedAt": now,
        "requestSource": "container_qr",
        "status": "requested",
        "geoAtRequest": (
            {"latitude": payload.geoAtRequest.latitude,
                "longitude": payload.geoAtRequest.longitude}
            if payload.geoAtRequest else None
        ),
    }
    await db.collection_requests.insert_one(doc)
    return {"id": req_id, "status": "requested"}
