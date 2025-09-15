from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Literal
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


class RequestListOut(BaseModel):
    id: str
    householdId: str
    containerId: str
    status: str
    requestedAt: str
    assignedTo: str | None = None


@router.get("/collection-requests", response_model=List[RequestListOut])
async def list_collection_requests(
    status: Literal["requested", "completed", "any"] = Query("any"),
    householdId: str | None = None,
    assignedTo: str | None = None,
    limit: int = 50,
):
    db = get_db()
    q = {}
    if status != "any":
        q["status"] = status
    if householdId:
        q["householdId"] = householdId
    if assignedTo:
        q["assignedTo"] = assignedTo
    cur = db.collection_requests.find(q).limit(min(limit, 200))
    results: List[RequestListOut] = []
    async for d in cur:
        results.append(RequestListOut(
            id=d["_id"],
            householdId=d.get("householdId"),
            containerId=d.get("containerId"),
            status=d.get("status"),
            requestedAt=d.get("requestedAt"),
            assignedTo=d.get("assignedTo"),
        ))
    return results


@router.get("/collection-requests/check-pending")
async def check_pending(containerId: str = Query(...), householdId: str = Query(...)):
    db = get_db()
    exists = await db.collection_requests.find_one({
        "containerId": containerId,
        "householdId": householdId,
        "status": "requested",
    })
    return {"pending": bool(exists)}


class AssignIn(BaseModel):
    assignedTo: str


@router.patch("/collection-requests/{request_id}/assign")
async def assign_request(request_id: str, payload: AssignIn):
    db = get_db()
    res = await db.collection_requests.update_one({"_id": request_id}, {"$set": {"assignedTo": payload.assignedTo}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"ok": True}


class StatusUpdateIn(BaseModel):
    status: Literal["requested", "cancelled", "completed"]
    note: str | None = None
    updatedBy: str | None = None


@router.patch("/collection-requests/{request_id}/status")
async def update_request_status(request_id: str, payload: StatusUpdateIn):
    db = get_db()
    res = await db.collection_requests.update_one(
        {"_id": request_id}, {"$set": {"status": payload.status, "updateNote": payload.note, "updatedBy": payload.updatedBy}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"ok": True}


class ManualStartIn(BaseModel):
    householdId: str
    containerId: str
    requestedBy: str
    geoAtRequest: GeoPoint | None = None


@router.post("/collections/start-manual", response_model=RequestOut)
async def start_manual_collection(payload: ManualStartIn):
    db = get_db()
    container = await db.containers.find_one({"_id": payload.containerId})
    if not container or container.get("assignedHouseholdId") != payload.householdId:
        raise HTTPException(status_code=400, detail="Container not assigned to household")
    now = datetime.now(timezone.utc).isoformat()
    req_id = new_id("req")
    doc = {
        "_id": req_id,
        "householdId": payload.householdId,
        "containerId": payload.containerId,
        "requestedAt": now,
        "requestSource": "manual",
        "requestedBy": payload.requestedBy,
        "status": "requested",
        "geoAtRequest": (
            {"latitude": payload.geoAtRequest.latitude,
                "longitude": payload.geoAtRequest.longitude}
            if payload.geoAtRequest else None
        ),
    }
    await db.collection_requests.insert_one(doc)
    return {"id": req_id, "status": "requested"}
