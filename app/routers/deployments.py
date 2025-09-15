from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from app.dependencies.db import get_db
from app.services.swap import perform_swap
from app.utils.ids import new_id
from typing import List, Literal

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


class DeploymentAssignIn(BaseModel):
    householdId: str
    assignedTo: str
    notes: str | None = None


@router.post("/deployments/assign")
async def create_deployment_assignment(payload: DeploymentAssignIn):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    # Ensure household exists
    h = await db.households.find_one({"_id": payload.householdId})
    if not h:
        raise HTTPException(status_code=404, detail="Household not found")
    dep_id = new_id("dep_task")
    doc = {
        "_id": dep_id,
        "type": "deployment_task",
        "status": "assigned",
        "assignedTo": payload.assignedTo,
        "householdId": payload.householdId,
        "createdAt": now,
        "notes": payload.notes,
    }
    await db.deployments.insert_one(doc)
    return {"id": dep_id, "status": "assigned"}


class DeploymentListOut(BaseModel):
    id: str
    type: str
    status: str | None = None
    householdId: str | None = None
    assignedTo: str | None = None
    performedAt: str | None = None
    createdAt: str | None = None


@router.get("/deployments", response_model=List[DeploymentListOut])
async def list_deployments(
    assignedTo: str | None = None,
    status: Literal["assigned", "in_progress", "completed", "any"] = "any",
    type: Literal["deployment", "swap", "deployment_task", "any"] = "any",
    limit: int = 100,
    sortBy: Literal["performedAt", "createdAt", "type", "status"] = "performedAt",
    sortDir: Literal["asc", "desc"] = "desc"
):
    db = get_db()
    q: dict = {}
    if assignedTo:
        q["assignedTo"] = assignedTo
    if status != "any":
        q["status"] = status
    if type != "any":
        q["type"] = type
    sort_field = sortBy
    sort_direction = -1 if sortDir == "desc" else 1
    cur = db.deployments.find(q).sort(sort_field, sort_direction).limit(min(limit, 200))
    results: List[DeploymentListOut] = []
    async for d in cur:
        results.append(DeploymentListOut(
            id=d["_id"], type=d.get("type"), status=d.get("status"),
            householdId=d.get("householdId"), assignedTo=d.get("assignedTo"),
            performedAt=d.get("performedAt"), createdAt=d.get("createdAt"),
        ))
    return results


class DeploymentAssignUpdateIn(BaseModel):
    assignedTo: str


@router.patch("/deployments/{deployment_id}/assign")
async def update_deployment_assignment(deployment_id: str, payload: DeploymentAssignUpdateIn):
    db = get_db()
    res = await db.deployments.update_one({"_id": deployment_id}, {"$set": {"assignedTo": payload.assignedTo}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"ok": True}


class DeploymentStatusUpdateIn(BaseModel):
    status: Literal["assigned", "in_progress", "completed", "cancelled"]


@router.patch("/deployments/{deployment_id}/status")
async def update_deployment_status(deployment_id: str, payload: DeploymentStatusUpdateIn):
    db = get_db()
    res = await db.deployments.update_one({"_id": deployment_id}, {"$set": {"status": payload.status}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return {"ok": True}
