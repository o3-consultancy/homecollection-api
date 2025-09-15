from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Literal
from app.dependencies.db import get_db

router = APIRouter()


class CollectionSummaryOut(BaseModel):
    id: str
    householdId: str
    containerId: str
    requestedAt: str
    status: str
    volumeL: float | None = None
    weightKg: float | None = None
    performedBy: str | None = None
    assignedTo: str | None = None


@router.get("/collections", response_model=List[CollectionSummaryOut])
async def list_collections_summary(
    status: Literal["requested", "completed", "any"] = Query("any"),
    dateFrom: str | None = None,
    dateTo: str | None = None,
    householdId: str | None = None,
    assignedTo: str | None = None,
    limit: int = 100,
    sortBy: Literal["requestedAt", "status", "householdId"] = "requestedAt",
    sortDir: Literal["asc", "desc"] = "desc"
):
    db = get_db()
    q = {}
    if status != "any":
        q["status"] = status
    if householdId:
        q["householdId"] = householdId
    if assignedTo:
        q["assignedTo"] = assignedTo
    
    # Date range filtering
    if dateFrom or dateTo:
        date_filter = {}
        if dateFrom:
            date_filter["$gte"] = dateFrom
        if dateTo:
            date_filter["$lte"] = dateTo
        q["requestedAt"] = date_filter
    
    sort_field = sortBy
    sort_direction = -1 if sortDir == "desc" else 1
    cur = db.collection_requests.find(q).sort(sort_field, sort_direction).limit(min(limit, 500))
    
    results: List[CollectionSummaryOut] = []
    async for d in cur:
        metrics = d.get("metrics") or {}
        results.append(CollectionSummaryOut(
            id=d["_id"],
            householdId=d.get("householdId"),
            containerId=d.get("containerId"),
            requestedAt=d.get("requestedAt"),
            status=d.get("status"),
            volumeL=metrics.get("volumeL"),
            weightKg=metrics.get("weightKg"),
            performedBy=metrics.get("measuredBy"),
            assignedTo=d.get("assignedTo"),
        ))
    return results
