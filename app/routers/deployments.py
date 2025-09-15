from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from app.dependencies.db import get_db
from app.services.swap import perform_swap
from app.utils.ids import new_id

router = APIRouter()


class SwapIn(BaseModel):
    requestId: str
    householdId: str
    removedContainerId: str
    installedContainerId: str
    volumeL: float | None = None
    weightKg: float | None = None
    performedBy: str


@router.post("/deployments/swap")
async def swap_endpoint(payload: SwapIn):
    try:
        result = await perform_swap(payload.model_dump())
        return {"ok": True, "deploymentId": result["deploymentId"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class DeploymentPerformIn(BaseModel):
    householdId: str
    containerId: str
    performedBy: str


@router.post("/deployments/perform")
async def perform_deployment(payload: DeploymentPerformIn):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    household = await db.households.find_one({"_id": payload.householdId})
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")

    container = await db.containers.find_one({"_id": payload.containerId})
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")
    if container.get("assignedHouseholdId"):
        raise HTTPException(status_code=400, detail="Container already assigned")

    # Assign container to household
    await db.containers.update_one(
        {"_id": payload.containerId},
        {"$set": {"assignedHouseholdId": payload.householdId, "history.lastAssignedAt": now}},
    )

    await db.households.update_one(
        {"_id": payload.householdId},
        {"$set": {"currentContainerId": payload.containerId, "lastDeploymentAt": now}},
    )

    # Open a container assignment ledger record
    await db.container_assignments.insert_one({
        "_id": f"assn_{payload.containerId}_{now}",
        "containerId": payload.containerId,
        "householdId": payload.householdId,
        "assignedAt": now,
        "assignedBy": payload.performedBy,
        "assignmentReason": "initial_deployment",
        "unassignedAt": None,
    })

    # Deployment record
    dep_id = new_id("dep")
    await db.deployments.insert_one({
        "_id": dep_id,
        "type": "deployment",
        "performedAt": now,
        "performedBy": payload.performedBy,
        "householdId": payload.householdId,
        "installedContainerId": payload.containerId,
    })

    # If there is a signup linked to this household in awaiting_deployment, activate it
    await db.signups.update_many(
        {"linkedHouseholdId": payload.householdId, "status": "awaiting_deployment"},
        {"$set": {"status": "active", "updatedAt": now}},
    )

    return {"ok": True, "deploymentId": dep_id}
