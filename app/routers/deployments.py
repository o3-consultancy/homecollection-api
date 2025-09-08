from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.swap import perform_swap

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
