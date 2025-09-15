from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from app.dependencies.db import get_db
from app.utils.ids import new_id
from typing import List, Literal

router = APIRouter()


class ContainerCreate(BaseModel):
    serial: str
    capacityL: int | None = None
    type: str | None = "wheelieBin"


@router.post("/containers")
async def create_container(payload: ContainerCreate):
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    cid = new_id("container")
    doc = {
        "_id": cid, "serial": payload.serial, "state": "new",
        "attributes": {"capacityL": payload.capacityL, "type": payload.type},
        "assignedHouseholdId": None, "qrVersion": 1, "createdAt": now,
        "history": {}
    }
    await db.containers.insert_one(doc)
    return {"id": cid}


@router.get("/containers/{container_id}")
async def get_container(container_id: str):
    db = get_db()
    c = await db.containers.find_one({"_id": container_id})
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    c["id"] = c.pop("_id")
    return c


@router.get("/containers")
async def list_containers(
    unassigned: bool | None = None, 
    limit: int = 50,
    sortBy: Literal["createdAt", "serial", "assignedHouseholdId"] = "createdAt",
    sortDir: Literal["asc", "desc"] = "desc"
):
    db = get_db()
    q = {}
    if unassigned is True:
        q["assignedHouseholdId"] = None
    sort_field = sortBy
    sort_direction = -1 if sortDir == "desc" else 1
    cur = db.containers.find(q).sort(sort_field, sort_direction).limit(min(limit, 200))
    return [{"id": d["_id"], **{k: v for k, v in d.items() if k != "_id"}} async for d in cur]


@router.get("/containers/{container_id}/history")
async def get_container_history(container_id: str):
    db = get_db()
    container = await db.containers.find_one({"_id": container_id})
    if not container:
        raise HTTPException(status_code=404, detail="Container not found")

    # Container assignment history
    assn_cur = db.container_assignments.find({"containerId": container_id}).sort("assignedAt", 1)
    assignments = [
        {
            "householdId": d.get("householdId"),
            "assignedAt": d.get("assignedAt"),
            "unassignedAt": d.get("unassignedAt"),
            "assignedBy": d.get("assignedBy"),
            "assignmentReason": d.get("assignmentReason"),
            "unassignmentReason": d.get("unassignmentReason"),
        }
        async for d in assn_cur
    ]

    # Deployments involving this container
    dep_cur = db.deployments.find({
        "$or": [
            {"installedContainerId": container_id},
            {"removedContainerId": container_id}
        ]
    }).sort("performedAt", 1)
    deployments = [
        {
            "type": d.get("type"),
            "performedAt": d.get("performedAt"),
            "performedBy": d.get("performedBy"),
            "householdId": d.get("householdId"),
            "installedContainerId": d.get("installedContainerId"),
            "removedContainerId": d.get("removedContainerId"),
        }
        async for d in dep_cur
    ]

    # Collection requests involving this container
    req_cur = db.collection_requests.find({"containerId": container_id}).sort("requestedAt", 1)
    collections = [
        {
            "requestId": d.get("_id"),
            "householdId": d.get("householdId"),
            "requestedAt": d.get("requestedAt"),
            "status": d.get("status"),
            "requestSource": d.get("requestSource"),
            "metrics": d.get("metrics"),
            "swap": d.get("swap"),
        }
        async for d in req_cur
    ]

    return {
        "container": {
            "id": container["_id"],
            "serial": container.get("serial"),
            "currentHouseholdId": container.get("assignedHouseholdId"),
            "state": container.get("state"),
        },
        "assignments": assignments,
        "deployments": deployments,
        "collections": collections,
    }
