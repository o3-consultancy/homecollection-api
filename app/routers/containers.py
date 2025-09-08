from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from app.dependencies.db import get_db
from app.utils.ids import new_id

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
async def list_containers(unassigned: bool | None = None, limit: int = 50):
    db = get_db()
    q = {}
    if unassigned is True:
        q["assignedHouseholdId"] = None
    cur = db.containers.find(q).limit(min(limit, 200))
    return [{"id": d["_id"], **{k: v for k, v in d.items() if k != "_id"}} async for d in cur]
