# HomeCollection API Reference

This document provides a complete reference to the HomeCollection API for client applications (Ground Team app, Landing Page/QR SPA, and Operations Management System).

- Base URL prefix: `{API_BASE_PATH}` from `app/core/config.py`
- Auth: API Key via header `x-api-key: <YOUR_KEY>` unless endpoint is explicitly public
- Content-Type: `application/json`

## Authentication and Access
- Provide `x-api-key` on all requests except public endpoints.
- Public endpoints: `/health`, `/qr/sign`, `/qr/verify`, `/auth/login`, and the OpenAPI/Docs routes.

Example headers:
```http
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

## Common Types
- `GeoPoint`: `{ "latitude": number, "longitude": number }`
- Timestamps are ISO-8601 strings in UTC.

---

## Health
- GET `{API_BASE_PATH}/health`
  - Description: Liveness check
  - Response: `{ "ok": true }`

---

## QR – Landing Page/QR SPA
- GET `{API_BASE_PATH}/qr/sign?containerId=<id>`
  - Description: Create a short-lived signature for a container action
  - Response: `{ "containerId": "...", "sig": "..." }`

- GET `{API_BASE_PATH}/qr/verify?containerId=<id>&sig=<sig>`
  - Description: Verify a signature produced by `/qr/sign`
  - Response: `{ "valid": true|false }`

---

## Users and Auth – Ground Team and OMS
- POST `{API_BASE_PATH}/users`
  - Description: Create user with salted PBKDF2-hashed password
  - Body:
    ```json
    { "username": "alex", "password": "secret" }
    ```
  - Response:
    ```json
    { "id": "user_alex", "username": "alex", "createdAt": "..." }
    ```

- GET `{API_BASE_PATH}/users?limit=100`
  - Description: List users (no password fields)
  - Response: `[{ "id": "user_alex", "username": "alex", "createdAt": "..." }]`

- GET `{API_BASE_PATH}/users/{userId}`
  - Description: Get a user (no password fields)

- PATCH `{API_BASE_PATH}/users/{userId}`
  - Description: Update password
  - Body (any field optional):
    ```json
    { "password": "newSecret" }
    ```

- DELETE `{API_BASE_PATH}/users/{userId}`
  - Description: Delete a user

- POST `{API_BASE_PATH}/auth/login`
  - Public
  - Description: Verify credentials; returns a simple session object (no JWT yet)
  - Body:
    ```json
    { "username": "alex", "password": "secret" }
    ```
  - Response:
    ```json
    { "ok": true, "userId": "user_alex", "username": "alex" }
    ```

---

## Signups – Landing Page and OMS
- POST `{API_BASE_PATH}/signups`
  - Description: Create a new signup (status `pending`)
  - Body:
    ```json
    {
      "fullName": "Jane Doe",
      "phone": "+97150000000",
      "email": "jane@example.com",
      "addressText": "Street X",
      "villaNumber": "V12",
      "community": "Community A",
      "location": { "latitude": 25.2, "longitude": 55.3 }
    }
    ```
  - Response: `{ "id": "signup_...", "status": "pending" }`

- GET `{API_BASE_PATH}/signups?sortBy=createdAt|status|fullName&sortDir=asc|desc`
  - Description: List signups with status in [`pending`, `awaiting_deployment`, `active`], with sorting

- POST `{API_BASE_PATH}/signups/awaiting-deployment/batch`
  - Description: For given `signupIds`, create households and set status to `awaiting_deployment`
  - Body:
    ```json
    { "signupIds": ["signup_1", "signup_2"] }
    ```
  - Response: `[{ "signupId": "signup_1", "householdId": "hh_...", "status": "updated" }]`

- GET `{API_BASE_PATH}/signups/awaiting-deployment`
  - Description: List signups in `awaiting_deployment`

- POST `{API_BASE_PATH}/signups/ad-hoc-deploy`
  - Description: Create signup + household and deploy a container immediately; sets signup `active`
  - Body:
    ```json
    {
      "fullName": "Jane Doe",
      "phone": "+97150000000",
      "email": "jane@example.com",
      "addressText": "Street X",
      "villaNumber": "V12",
      "community": "Community A",
      "location": { "latitude": 25.2, "longitude": 55.3 },
      "containerId": "container_1",
      "performedBy": "user_alex"
    }
    ```
  - Response:
    ```json
    { "signupId": "signup_...", "householdId": "hh_...", "deploymentId": "dep_...", "status": "active" }
    ```

- GET `{API_BASE_PATH}/signups/all?status=any|pending|awaiting_deployment|active|inactive|deleted&community=...&limit=...&sortBy=createdAt|status|fullName&sortDir=asc|desc`
  - OMS: List signups across any status with filters and sorting

- PATCH `{API_BASE_PATH}/signups/status/batch`
  - OMS: Batch update signup statuses (e.g., `inactive`, `deleted`, `awaiting_deployment`)
  - Body:
    ```json
    {
      "items": [
        { "signupId": "signup_1", "status": "inactive", "reason": "user request", "updatedBy": "ops_1" },
        { "signupId": "signup_2", "status": "deleted", "reason": "duplicate", "updatedBy": "ops_1" }
      ]
    }
    ```
  - Response: `{ "updated": 2, "skipped": 0, "errors": 0 }`

---

## Households – Ground Team and OMS
- POST `{API_BASE_PATH}/households`
  - Description: Create household

- GET `{API_BASE_PATH}/households/{householdId}`
  - Description: Get a household

- GET `{API_BASE_PATH}/households?community=...&status=...&hasContainer=true|false&limit=...&sortBy=createdAt|villaNumber|community&sortDir=asc|desc`
  - Description: List households with filters and sorting

- GET `{API_BASE_PATH}/households/{householdId}/history`
  - Description: Timeline of assignments and deployments/swaps and total collected volume
  - Response example (truncated):
    ```json
    {
      "household": { "id": "hh_1", "currentContainerId": "container_1" },
      "assignments": [ { "containerId": "container_1", "assignedAt": "..." } ],
      "deployments": [ { "type": "deployment", "performedAt": "..." } ],
      "totalVolumeCollectedL": 120.0
    }
    ```

---

## Containers – Operations
- POST `{API_BASE_PATH}/containers`
  - Description: Create container
  - Body:
    ```json
    { "serial": "C-0001", "capacityL": 240, "type": "wheelieBin" }
    ```

- GET `{API_BASE_PATH}/containers/{containerId}`
  - Description: Get container

- GET `{API_BASE_PATH}/containers?unassigned=true|false&limit=50&sortBy=createdAt|serial|assignedHouseholdId&sortDir=asc|desc`
  - Description: List containers; filter by unassigned, with sorting

- GET `{API_BASE_PATH}/containers/{containerId}/history`
  - Description: Get container timeline (assignments, deployments, collections)
  - Response:
    ```json
    {
      "container": { "id": "container_1", "serial": "C-0001", "currentHouseholdId": "hh_1", "state": "active" },
      "assignments": [{ "householdId": "hh_1", "assignedAt": "...", "unassignedAt": null, "assignedBy": "user_1", "assignmentReason": "initial_deployment" }],
      "deployments": [{ "type": "deployment", "performedAt": "...", "performedBy": "user_1", "householdId": "hh_1", "installedContainerId": "container_1" }],
      "collections": [{ "requestId": "req_1", "householdId": "hh_1", "requestedAt": "...", "status": "completed", "metrics": { "volumeL": 20.5 } }]
    }
    ```

---

## Deployments – Ground Team
- POST `{API_BASE_PATH}/deployments/perform`
  - Description: Assign an unassigned container to a household; activates linked signup(s)
  - Body:
    ```json
    { "householdId": "hh_1", "containerId": "container_2", "performedBy": "user_alex" }
    ```
  - Response: `{ "ok": true, "deploymentId": "dep_..." }`

- POST `{API_BASE_PATH}/deployments/assign`
  - Description: Create a deployment task assignment for a user
  - Body:
    ```json
    { "householdId": "hh_1", "assignedTo": "user_alex", "notes": "deliver by Tue" }
    ```
  - Response: `{ "id": "dep_task_...", "status": "assigned" }`

- GET `{API_BASE_PATH}/deployments?assignedTo=...&status=assigned|in_progress|completed|any&type=deployment|swap|deployment_task|any&limit=...&sortBy=performedAt|createdAt|type|status&sortDir=asc|desc`
  - Description: List deployments and tasks with sorting

- PATCH `{API_BASE_PATH}/deployments/{id}/assign`
  - Description: Reassign a deployment task
  - Body: `{ "assignedTo": "user_bob" }`

- PATCH `{API_BASE_PATH}/deployments/{id}/status`
  - Description: Update task status (`assigned`, `in_progress`, `completed`, `cancelled`)
  - Body: `{ "status": "in_progress" }`

- POST `{API_BASE_PATH}/deployments/swap`
  - Description: Perform a swap while completing a collection request
  - Body:
    ```json
    {
      "requestId": "req_1",
      "householdId": "hh_1",
      "removedContainerId": "container_old",
      "installedContainerId": "container_new",
      "volumeL": 20.5,
      "weightKg": 18.1,
      "performedBy": "user_alex"
    }
    ```

---

## Collection Requests – Landing Page/QR SPA and OMS
- POST `{API_BASE_PATH}/collection-requests?sig=<signature>`
  - Description: Create a collection request from a signed QR action
  - Body:
    ```json
    { "containerId": "container_1", "householdId": "hh_1", "geoAtRequest": { "latitude": 25.2, "longitude": 55.3 } }
    ```
  - Response: `{ "id": "req_...", "status": "requested" }`

- GET `{API_BASE_PATH}/collection-requests?status=requested|completed|any&householdId=...&assignedTo=...&limit=...&sortBy=requestedAt|status|householdId&sortDir=asc|desc`
  - Description: List collection requests with filters and sorting

- GET `{API_BASE_PATH}/collection-requests/check-pending?containerId=...&householdId=...`
  - Description: Check if a pending request exists for a given household+container
  - Response: `{ "pending": true|false }`

- PATCH `{API_BASE_PATH}/collection-requests/{id}/assign`
  - Description: Assign a collection request to a user
  - Body: `{ "assignedTo": "user_alex" }`

- PATCH `{API_BASE_PATH}/collection-requests/{id}/status`
  - Description: Update request status (`requested`, `cancelled`, `completed`)
  - Body: `{ "status": "cancelled", "note": "duplicate", "updatedBy": "ops_1" }`

- POST `{API_BASE_PATH}/collections/start-manual`
  - Description: Create a manual collection request (no QR)
  - Body:
    ```json
    { "householdId": "hh_1", "containerId": "container_1", "requestedBy": "ops_1", "geoAtRequest": { "latitude": 25.2, "longitude": 55.3 } }
    ```
  - Response: `{ "id": "req_...", "status": "requested" }`

---

## Collections Summary – OMS
- GET `{API_BASE_PATH}/collections?status=requested|completed|any&dateFrom=...&dateTo=...&householdId=...&assignedTo=...&limit=...&sortBy=requestedAt|status|householdId&sortDir=asc|desc`
  - Description: Collections summary with volume/weight metrics, date filtering, and sorting
  - Response:
    ```json
    [
      {
        "id": "req_1",
        "householdId": "hh_1",
        "containerId": "container_1",
        "requestedAt": "2024-01-15T10:30:00Z",
        "status": "completed",
        "volumeL": 20.5,
        "weightKg": 18.1,
        "performedBy": "user_alex",
        "assignedTo": "user_alex"
      }
    ]
    ```

---

## Error Handling
- Standard HTTP status codes:
  - 400 Bad Request (validation/semantic failures)
  - 401 Unauthorized (missing/invalid API key or credentials)
  - 404 Not Found (resource doesn’t exist)
  - 409 Conflict (duplicates)
- Response body typically contains: `{ "detail": "..." }`

## Notes
- All writes set `createdAt`/`updatedAt` where applicable.
- Some endpoints maintain audit trails in `deployments` and `container_assignments` collections.
- Index creation is best-effort and may be skipped depending on the backend.


