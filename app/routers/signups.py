from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.dependencies.db import get_db
from app.utils.ids import new_id
from typing import List


router = APIRouter()


class GeoPoint(BaseModel):
    latitude: float
    longitude: float


class SignupCreate(BaseModel):
    fullName: str
    phone: str
    email: EmailStr
    addressText: str
    villaNumber: str | None = None
    community: str | None = None
    location: GeoPoint


class SignupOut(BaseModel):
    id: str
    status: str


@router.post("/signups", response_model=SignupOut)
async def create_signup(payload: SignupCreate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    signup_id = new_id("signup")
    doc = {
        "_id": signup_id,
        "fullName": payload.fullName,
        "phone": payload.phone,
        "email": payload.email,
        "addressText": payload.addressText,
        "villaNumber": payload.villaNumber,
        "community": payload.community,
        "location": {"latitude": payload.location.latitude, "longitude": payload.location.longitude},
        "status": "pending",
        "createdAt": now,
        "dedupeKey": f"phone:{payload.phone}|geo:{round(payload.location.latitude, 5)},{round(payload.location.longitude, 5)}",
        "linkedHouseholdId": None,
        "source": "flyer_qr_v1",
    }
    await db.signups.insert_one(doc)
    return {"id": signup_id, "status": "pending"}


# --- NEW GET ENDPOINT ---
class SignupListOut(BaseModel):
    id: str
    fullName: str
    phone: str
    email: str
    addressText: str
    villaNumber: str | None
    community: str | None
    location: GeoPoint
    status: str
    createdAt: str


@router.get("/signups", response_model=List[SignupListOut])
async def list_active_signups():
    db = get_db()
    # Query all signups where status is not "inactive" or "deleted"
    cursor = db.signups.find({"status": {"$in": ["pending", "active"]}})
    results = []
    async for doc in cursor:
        results.append(
            SignupListOut(
                id=doc["_id"],
                fullName=doc.get("fullName"),
                phone=doc.get("phone"),
                email=doc.get("email"),
                addressText=doc.get("addressText"),
                villaNumber=doc.get("villaNumber"),
                community=doc.get("community"),
                location=GeoPoint(
                    latitude=doc["location"]["latitude"],
                    longitude=doc["location"]["longitude"],
                ),
                status=doc.get("status"),
                createdAt=doc.get("createdAt"),
            )
        )
    return results
