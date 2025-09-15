from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime, timezone
from app.dependencies.db import get_db
from app.utils.ids import new_id

router = APIRouter()


class Contact(BaseModel):
    fullName: str
    phone: str
    email: EmailStr


class HouseholdCreate(BaseModel):
    villaNumber: str
    community: str
    addressText: str
    latitude: float
    longitude: float
    primaryContact: Contact


@router.post("/households")
async def create_household(payload: HouseholdCreate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    hid = new_id("hh")
    doc = {
        "_id": hid,
        "villaNumber": payload.villaNumber,
        "community": payload.community,
        "addressText": payload.addressText,
        "location": {"latitude": payload.latitude, "longitude": payload.longitude},
        "primaryContact": payload.primaryContact.model_dump(),
        "status": "active",
        "createdAt": now,
        "updatedAt": now,
        "currentContainerId": None,
        "previousContainerIds": []
    }
    await db.households.insert_one(doc)
    return {"id": hid}


@router.get("/households/{household_id}")
async def get_household(household_id: str):
    db = get_db()
    h = await db.households.find_one({"_id": household_id})
    if not h:
        raise HTTPException(status_code=404, detail="Not found")
    h["id"] = h.pop("_id")
    return h


class HouseholdListOut(BaseModel):
    id: str
    villaNumber: str | None = None
    community: str | None = None
    addressText: str | None = None
    status: str | None = None
    currentContainerId: str | None = None


@router.get("/households", response_model=List[HouseholdListOut])
async def list_households(
    community: str | None = None,
    status: str | None = None,
    hasContainer: bool | None = None,
    limit: int = Query(50, ge=1, le=200),
):
    db = get_db()
    q: dict = {}
    if community:
        q["community"] = community
    if status:
        q["status"] = status
    if hasContainer is True:
        q["currentContainerId"] = {"$ne": None}
    if hasContainer is False:
        q["currentContainerId"] = None

    cur = db.households.find(q).limit(limit)
    results: List[HouseholdListOut] = []
    async for d in cur:
        results.append(HouseholdListOut(
            id=d["_id"],
            villaNumber=d.get("villaNumber"),
            community=d.get("community"),
            addressText=d.get("addressText"),
            status=d.get("status"),
            currentContainerId=d.get("currentContainerId"),
        ))
    return results


@router.get("/households/{household_id}/history")
async def get_household_history(household_id: str):
    db = get_db()
    h = await db.households.find_one({"_id": household_id})
    if not h:
        raise HTTPException(status_code=404, detail="Not found")

    # Container assignment history
    assn_cur = db.container_assignments.find({"householdId": household_id}).sort("assignedAt", 1)
    assignments = [
        {
            "containerId": d.get("containerId"),
            "assignedAt": d.get("assignedAt"),
            "unassignedAt": d.get("unassignedAt"),
            "assignmentReason": d.get("assignmentReason"),
        }
        async for d in assn_cur
    ]

    # Deployments and swaps
    dep_cur = db.deployments.find({"householdId": household_id}).sort("performedAt", 1)
    deployments = [
        {
            "type": d.get("type"),
            "performedAt": d.get("performedAt"),
            "performedBy": d.get("performedBy"),
            "installedContainerId": d.get("installedContainerId"),
            "removedContainerId": d.get("removedContainerId"),
        }
        async for d in dep_cur
    ]

    # Total collected volume (from completed collection requests with metrics)
    total_volume = 0.0
    cur = db.collection_requests.find({"householdId": household_id, "status": "completed"})
    async for r in cur:
        metrics = r.get("metrics") or {}
        if metrics.get("volumeL") is not None:
            try:
                total_volume += float(metrics.get("volumeL"))
            except Exception:
                pass

    return {
        "household": {"id": h["_id"], "currentContainerId": h.get("currentContainerId")},
        "assignments": assignments,
        "deployments": deployments,
        "totalVolumeCollectedL": total_volume,
    }
