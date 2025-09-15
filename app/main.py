import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.auth import api_key_auth_middleware
from app.dependencies.db import get_db
from app.routers import health, qr, signups, collection_requests, deployments, containers, households, users

app = FastAPI(
    title="HomeCollection API",
    version="0.1.0",
    openapi_url=f"{settings.API_BASE_PATH}/openapi.json",
    docs_url=f"{settings.API_BASE_PATH}/docs",
    redoc_url=f"{settings.API_BASE_PATH}/redoc",
)

# CORS for Firebase Hosting
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*", "x-api-key"],
        expose_headers=["*"],
        max_age=86400,  # cache preflight for a day
    )

# API key middleware
app.middleware("http")(api_key_auth_middleware)

# Routers
app.include_router(
    health.router, prefix=settings.API_BASE_PATH, tags=["health"])
app.include_router(qr.router, prefix=settings.API_BASE_PATH, tags=["qr"])
app.include_router(
    signups.router, prefix=settings.API_BASE_PATH, tags=["signups"])
app.include_router(collection_requests.router,
                   prefix=settings.API_BASE_PATH, tags=["collection-requests"])
app.include_router(deployments.router,
                   prefix=settings.API_BASE_PATH, tags=["deployments"])
app.include_router(containers.router,
                   prefix=settings.API_BASE_PATH, tags=["containers"])
app.include_router(households.router,
                   prefix=settings.API_BASE_PATH, tags=["households"])
app.include_router(users.router,
                   prefix=settings.API_BASE_PATH, tags=["users", "auth"])

# Background worker for outbox (optional)
_stop_event: asyncio.Event | None = None
_task: asyncio.Task | None = None


async def startup_event():
    db = get_db()
    try:
        await db.ensure_indexes()
    except Exception as e:
        # Never block startup if indexes can’t be created at runtime
        import logging
        logging.getLogger("uvicorn.error").warning(
            "ensure_indexes failed, continuing: %s", e)
    global _stop_event, _task


@app.on_event("shutdown")
async def shutdown_event():
    global _stop_event, _task
    if _stop_event and _task:
        _stop_event.set()
        await _task
