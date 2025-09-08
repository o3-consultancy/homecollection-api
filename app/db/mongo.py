# app/db/mongo.py
import logging

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import OperationFailure

from app.core.config import settings

log = logging.getLogger("uvicorn.error")


class MongoClientWrapper:
    def __init__(self):
        # Firestore's Mongo-compatible URI already includes TLS and auth.
        # uuidRepresentation="standard" is recommended with modern drivers.
        self.client = AsyncIOMotorClient(
            settings.MONGO_URI,
            uuidRepresentation="standard",
        )
        self.db = self.client[settings.MONGO_DB]

    # --- Collections ---
    @property
    def signups(self):
        return self.db["signups"]

    @property
    def households(self):
        return self.db["households"]

    @property
    def containers(self):
        return self.db["containers"]

    @property
    def collection_requests(self):
        return self.db["collection_requests"]

    @property
    def deployments(self):
        return self.db["deployments"]

    @property
    def container_assignments(self):
        return self.db["container_assignments"]

    # --- Utilities ---

    async def ping(self):
        # Connectivity check
        await self.db.command("ping")

    async def ensure_indexes(self):
        """
        Some Mongo-compatible backends (e.g., Firestore’s Mongo API) block runtime index creation.
        Make this optional and non-fatal.
        """
        if not settings.DB_CREATE_INDEXES:
            log.info("DB_CREATE_INDEXES=false -> skipping runtime index creation.")
            return

        try:
            # signups: list & triage
            await self.signups.create_index([("status", 1), ("createdAt", -1)])

            # households: lookup by community + villa
            await self.households.create_index([("community", 1), ("villaNumber", 1)], unique=False)

            # containers: who has what, current state
            await self.containers.create_index([("assignedHouseholdId", 1), ("state", 1)])

            # collection_requests: dashboards + history
            await self.collection_requests.create_index([("status", 1), ("requestedAt", -1)])
            await self.collection_requests.create_index([("householdId", 1), ("requestedAt", -1)])

            # container_assignments: audit trails
            await self.container_assignments.create_index([("householdId", 1), ("assignedAt", -1)])
            await self.container_assignments.create_index([("containerId", 1), ("assignedAt", -1)])

            log.info("Indexes ensured (Mongo driver).")
        except OperationFailure as e:
            # Firestore Mongo API often blocks createIndex -> do not fail startup
            log.warning(
                "Index creation denied by backend. Continuing without runtime createIndex. Details: %s",
                e,
            )
        except Exception as e:
            log.warning(
                "Index creation failed non-fatally. Continuing. Details: %s", e)
