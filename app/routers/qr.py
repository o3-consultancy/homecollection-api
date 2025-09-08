from fastapi import APIRouter, HTTPException, Query
from app.services.qr import sign_action, verify_action

router = APIRouter()


@router.get("/qr/sign")
def qr_sign(containerId: str = Query(...)):
    return {"containerId": containerId, "sig": sign_action(containerId)}


@router.get("/qr/verify")
def qr_verify(containerId: str = Query(...), sig: str = Query(...)):
    return {"valid": verify_action(containerId, sig)}
