# app/middleware/auth.py
from fastapi import Request, HTTPException
from fastapi.responses import Response
from app.core.config import settings
import os

API_KEY = os.getenv("API_KEY", "")

PUBLIC_PATHS = (
    "/health",
    "/qr/sign",
    "/qr/verify",
    "/openapi.json",
    "/docs",
    "/redoc",
)


async def api_key_auth_middleware(request: Request, call_next):
    # --- Let CORS preflight through (no API key on OPTIONS) ---
    if request.method == "OPTIONS":
        # Let CORSMiddleware (which wraps outside) decorate the response.
        return await call_next(request)

    # --- Public endpoints (prefix-aware) ---
    path = request.url.path
    if any(path.endswith(p) or path.startswith(p) for p in PUBLIC_PATHS):
        return await call_next(request)

    # --- API key check on real requests ---
    key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    # fallback to env if not set via settings
    expected = settings.API_KEY or API_KEY
    if not expected or key == expected:
        return await call_next(request)

    raise HTTPException(status_code=401, detail="Unauthorized")
