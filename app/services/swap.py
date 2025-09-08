from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from app.dependencies.db import get_db


async def perform_swap(payload: dict):
    """
    payload fields:
      requestId, householdId, removedContainerId, installedContainerId, volumeL?, weightKg?, performedBy
    """
    dbw = get_db()
    now = datetime.now(timezone.utc).isoformat()

    client: AsyncIOMotorClient = dbw.client
    async with await client.start_session() as s:
        try:
            async with s.start_transaction():
                old = await dbw.containers.find_one({"_id": payload["removedContainerId"]}, session=s)
                new = await dbw.containers.find_one({"_id": payload["installedContainerId"]}, session=s)
                if not old or not new:
                    raise ValueError("Container(s) not found")
                if old.get("assignedHouseholdId") != payload["householdId"]:
                    raise ValueError("Old container not assigned to household")
                if new.get("assignedHouseholdId"):
                    raise ValueError("New container must be unassigned")

                # Update pointers
                await dbw.containers.update_one(
                    {"_id": old["_id"]},
                    {"$set": {"assignedHouseholdId": None,
                              "history.lastUnassignedAt": now}},
                    session=s,
                )
                await dbw.containers.update_one(
                    {"_id": new["_id"]},
                    {"$set": {
                        "assignedHouseholdId": payload["householdId"], "history.lastAssignedAt": now}},
                    session=s,
                )
                await dbw.households.update_one(
                    {"_id": payload["householdId"]},
                    {"$set": {"currentContainerId": new["_id"], "lastSwapAt": now},
                     "$addToSet": {"previousContainerIds": old["_id"]}},
                    upsert=True,
                    session=s,
                )
                # Ledger close/open
                await dbw.container_assignments.update_one(
                    {"containerId": old["_id"],
                        "householdId": payload["householdId"], "unassignedAt": None},
                    {"$set": {"unassignedAt": now, "unassignmentReason": "swap_out"}},
                    session=s,
                )
                await dbw.container_assignments.insert_one({
                    "_id": f"assn_{new['_id']}_{now}",
                    "containerId": new["_id"], "householdId": payload["householdId"],
                    "assignedAt": now, "assignedBy": payload["performedBy"],
                    "assignmentReason": "swap_in", "unassignedAt": None
                }, session=s)

                # Complete collection request with metrics + swap block
                await dbw.collection_requests.update_one(
                    {"_id": payload["requestId"]},
                    {"$set": {
                        "status": "completed",
                        "metrics": {
                            "volumeL": payload.get("volumeL"),
                            "weightKg": payload.get("weightKg"),
                            "measuredBy": payload["performedBy"]
                        },
                        "swap": {
                            "removedContainerId": payload["removedContainerId"],
                            "installedContainerId": payload["installedContainerId"],
                            "performedAt": now, "performedBy": payload["performedBy"]
                        }
                    }},
                    session=s,
                )
                # Deployment record
                dep_id = f"dep_swap_{payload['requestId']}"
                await dbw.deployments.insert_one({
                    "_id": dep_id, "type": "swap", "performedAt": now, "performedBy": payload["performedBy"],
                    "householdId": payload["householdId"],
                    "removedContainerId": payload["removedContainerId"],
                    "installedContainerId": payload["installedContainerId"]
                }, session=s)
        except Exception as e:
            # If the underlying platform does not support transactions, the exception may indicate that.
            # You can handle a fallback best-effort path here if needed.
            raise e
