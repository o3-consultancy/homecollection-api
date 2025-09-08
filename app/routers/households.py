from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
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
