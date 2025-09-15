from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr
from app.dependencies.db import get_db
from app.utils.ids import new_id
from typing import List, Literal


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
async def list_active_signups(
    sortBy: Literal["createdAt", "status", "fullName"] = "createdAt",
    sortDir: Literal["asc", "desc"] = "desc"
):
    db = get_db()
    # Query all signups where status is not "inactive" or "deleted"
    sort_field = sortBy
    sort_direction = -1 if sortDir == "desc" else 1
    cursor = db.signups.find({"status": {"$in": ["pending", "awaiting_deployment", "active"]}}).sort(sort_field, sort_direction)
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


class BatchProcessPayload(BaseModel):
    signupIds: List[str]


class BatchProcessResult(BaseModel):
    signupId: str
    householdId: str | None = None
    status: str
    message: str | None = None


@router.post("/signups/awaiting-deployment/batch", response_model=List[BatchProcessResult])
async def move_pending_to_awaiting_deployment(payload: BatchProcessPayload):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    results: List[BatchProcessResult] = []

    for signup_id in payload.signupIds:
        signup = await db.signups.find_one({"_id": signup_id})
        if not signup:
            results.append(BatchProcessResult(signupId=signup_id, householdId=None, status="skipped", message="signup not found"))
            continue

        if signup.get("status") != "pending":
            results.append(BatchProcessResult(signupId=signup_id, householdId=signup.get("linkedHouseholdId"), status="skipped", message=f"status is {signup.get('status')}, expected pending"))
            continue

        # Create household from signup details
        household_id = new_id("hh")
        household_doc = {
            "_id": household_id,
            "villaNumber": signup.get("villaNumber"),
            "community": signup.get("community"),
            "addressText": signup.get("addressText"),
            "location": {
                "latitude": signup["location"]["latitude"],
                "longitude": signup["location"]["longitude"],
            },
            "primaryContact": {
                "fullName": signup.get("fullName"),
                "phone": signup.get("phone"),
                "email": signup.get("email"),
            },
            "status": "active",
            "createdAt": now,
            "updatedAt": now,
            "currentContainerId": None,
            "previousContainerIds": [],
        }

        await db.households.insert_one(household_doc)

        # Update signup to awaiting_deployment and link household
        await db.signups.update_one(
            {"_id": signup_id},
            {"$set": {"status": "awaiting_deployment", "linkedHouseholdId": household_id, "updatedAt": now}},
        )

        results.append(BatchProcessResult(signupId=signup_id, householdId=household_id, status="updated", message=None))

    return results


class AdHocDeployIn(BaseModel):
    fullName: str
    phone: str
    email: EmailStr
    addressText: str
    villaNumber: str | None = None
    community: str | None = None
    location: GeoPoint
    containerId: str
    performedBy: str


class AdHocDeployOut(BaseModel):
    signupId: str
    householdId: str
    deploymentId: str
    status: str


@router.post("/signups/ad-hoc-deploy", response_model=AdHocDeployOut)
async def ad_hoc_signup_and_deploy(payload: AdHocDeployIn):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    # Validate container
    container = await db.containers.find_one({"_id": payload.containerId})
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    if container.get("assignedHouseholdId"):
        raise HTTPException(status_code=400, detail="Container already assigned")

    # Create signup (will end as active)
    signup_id = new_id("signup")
    signup_doc = {
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
        "source": "ad_hoc_v1",
    }

    # Create household from signup details
    household_id = new_id("hh")
    household_doc = {
        "_id": household_id,
        "villaNumber": payload.villaNumber,
        "community": payload.community,
        "addressText": payload.addressText,
        "location": {"latitude": payload.location.latitude, "longitude": payload.location.longitude},
        "primaryContact": {
            "fullName": payload.fullName,
            "phone": payload.phone,
            "email": payload.email,
        },
        "status": "active",
        "createdAt": now,
        "updatedAt": now,
        "currentContainerId": None,
        "previousContainerIds": [],
    }

    # Persist signup and household
    await db.signups.insert_one(signup_doc)
    await db.households.insert_one(household_doc)

    # Assign container to household
    await db.containers.update_one(
        {"_id": payload.containerId},
        {"$set": {"assignedHouseholdId": household_id, "history.lastAssignedAt": now}},
    )
    await db.households.update_one(
        {"_id": household_id},
        {"$set": {"currentContainerId": payload.containerId, "lastDeploymentAt": now}},
    )
    await db.container_assignments.insert_one({
        "_id": f"assn_{payload.containerId}_{now}",
        "containerId": payload.containerId,
        "householdId": household_id,
        "assignedAt": now,
        "assignedBy": payload.performedBy,
        "assignmentReason": "initial_deployment",
        "unassignedAt": None,
    })

    # Deployment record
    deployment_id = new_id("dep")
    await db.deployments.insert_one({
        "_id": deployment_id,
        "type": "deployment",
        "performedAt": now,
        "performedBy": payload.performedBy,
        "householdId": household_id,
        "installedContainerId": payload.containerId,
    })

    # Activate signup and link household
    await db.signups.update_one(
        {"_id": signup_id},
        {"$set": {"status": "active", "linkedHouseholdId": household_id, "updatedAt": now}},
    )

    return AdHocDeployOut(signupId=signup_id, householdId=household_id, deploymentId=deployment_id, status="active")


@router.get("/signups/awaiting-deployment", response_model=List[SignupListOut])
async def list_awaiting_deployment_signups():
    db = get_db()
    cursor = db.signups.find({"status": "awaiting_deployment"})
    results: List[SignupListOut] = []
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


# OMS: list-all with filters
@router.get("/signups/all", response_model=List[SignupListOut])
async def list_all_signups(
    status: Literal["pending", "awaiting_deployment", "active", "inactive", "deleted", "any"] = Query("any"),
    community: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    sortBy: Literal["createdAt", "status", "fullName"] = "createdAt",
    sortDir: Literal["asc", "desc"] = "desc"
):
    db = get_db()
    q: dict = {}
    if status != "any":
        q["status"] = status
    if community:
        q["community"] = community
    sort_field = sortBy
    sort_direction = -1 if sortDir == "desc" else 1
    cursor = db.signups.find(q).sort(sort_field, sort_direction).limit(limit)
    results: List[SignupListOut] = []
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


class SignupStatusUpdateItem(BaseModel):
    signupId: str
    status: Literal["pending", "awaiting_deployment", "active", "inactive", "deleted"]
    reason: str | None = None
    updatedBy: str | None = None


class SignupStatusBatchIn(BaseModel):
    items: List[SignupStatusUpdateItem]


class SignupStatusBatchOut(BaseModel):
    updated: int
    skipped: int
    errors: int


@router.patch("/signups/status/batch", response_model=SignupStatusBatchOut)
async def batch_update_signup_status(payload: SignupStatusBatchIn):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    updated = 0
    skipped = 0
    errors = 0
    for item in payload.items:
        try:
            res = await db.signups.update_one(
                {"_id": item.signupId},
                {"$set": {"status": item.status, "updatedAt": now, "statusReason": item.reason, "statusUpdatedBy": item.updatedBy}},
            )
            if res.matched_count == 0:
                skipped += 1
            else:
                updated += 1
        except Exception:
            errors += 1
    return SignupStatusBatchOut(updated=updated, skipped=skipped, errors=errors)
