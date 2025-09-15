# HomeCollection API – Project Plan and Checklist

This document tracks the phased implementation plan and checklists of API endpoints for the Home-based Used Cooking Oil collection project. Items already available in the codebase are marked as completed. Use this to check off tasks as we build and test.

Note: All routes are mounted under `{API_BASE_PATH}` from `app/core/config.py` in `main.py`.

## How to run (local)
- Install deps: `pip install -r requirements.txt`
- Set env vars for Mongo and settings (see `app/core/config.py`).
- Run: `uvicorn app.main:app --reload`
- Open docs: `{API_BASE_PATH}/docs`

## Phase 1 – Baseline APIs (available)
- [x] Health
  - GET `{API_BASE_PATH}/health`
- [x] Signups – Create
  - POST `{API_BASE_PATH}/signups`
- [x] Signups – List active set (pending | awaiting_deployment | active)
  - GET `{API_BASE_PATH}/signups`
- [x] Signups – Batch move pending → awaiting_deployment and create households
  - POST `{API_BASE_PATH}/signups/awaiting-deployment/batch`
- [x] Signups – List awaiting_deployment
  - GET `{API_BASE_PATH}/signups/awaiting-deployment`
- [x] Households – Create
  - POST `{API_BASE_PATH}/households`
- [x] Households – Get by id
  - GET `{API_BASE_PATH}/households/{household_id}`
- [x] Containers – Create
  - POST `{API_BASE_PATH}/containers`
- [x] Containers – Get by id
  - GET `{API_BASE_PATH}/containers/{container_id}`
- [x] Containers – List (filters: `unassigned`, `limit`)
  - GET `{API_BASE_PATH}/containers`
- [x] QR – Sign and Verify
  - GET `{API_BASE_PATH}/qr/sign`
  - GET `{API_BASE_PATH}/qr/verify`
- [x] Collection Requests – Create from QR (validates signature + assignment)
  - POST `{API_BASE_PATH}/collection-requests`
- [x] Deployments – Swap to fulfill a collection (records metrics + history)
  - POST `{API_BASE_PATH}/deployments/swap`

## Phase 2 – Deployment Workflows
- [x] Deployments – Perform initial deployment to household (assign container, create deployment record, activate signup)
  - POST `{API_BASE_PATH}/deployments/perform`
- [x] Signups – Ad-hoc signup with immediate deployment (create signup+household, assign container, activate)
  - POST `{API_BASE_PATH}/signups/ad-hoc-deploy`

## Phase 3 – Collections Operations
- [x] Collection Requests – List (filters: `status=requested|completed`, `householdId`, `assignedTo`, pagination)
  - GET `{API_BASE_PATH}/collection-requests`
- [x] Collection Requests – Assign to user
  - PATCH `{API_BASE_PATH}/collection-requests/{id}/assign`
- [x] Collection Requests – Update status
  - PATCH `{API_BASE_PATH}/collection-requests/{id}/status`
- [x] Collection Requests – Check pending for container+household (landing page pre-check)
  - GET `{API_BASE_PATH}/collection-requests/check-pending?containerId=...&householdId=...`
- [x] Collections – Start manual (optional, no QR)
  - POST `{API_BASE_PATH}/collections/start-manual`

## Phase 4 – Households Insights
- [x] Households – List (filters + pagination)
  - GET `{API_BASE_PATH}/households`
- [x] Households – History and stats (assignments, swaps, current container, total volume)
  - GET `{API_BASE_PATH}/households/{id}/history`

## Phase 5 – Users and Authentication
- [x] Users – Create (store password hash)
  - POST `{API_BASE_PATH}/users`
- [x] Users – List
  - GET `{API_BASE_PATH}/users`
- [x] Users – Get/Update/Delete
  - GET/PATCH/DELETE `{API_BASE_PATH}/users/{id}`
- [x] Auth – Login (optional, returns token/session)
  - POST `{API_BASE_PATH}/auth/login`

## Phase 6 – Task Assignment
- [x] Deployments – Assign to user
  - POST `{API_BASE_PATH}/deployments/assign`
- [x] Deployments – List (filters: `assignedTo`, `status`, date ranges)
  - GET `{API_BASE_PATH}/deployments`
- [x] Collections – Assignments surfaced via Collection Requests (Phase 3)

## Phase 7 – OMS Integration
- [x] Signups – List all (any status with filters)
  - GET `{API_BASE_PATH}/signups/all?status=...&limit=...`
- [x] Signups – Batch status update (inactive, deleted, awaiting_deployment, etc.)
  - PATCH `{API_BASE_PATH}/signups/status/batch`

## Tracking and Testing
- Mark items as completed once the endpoint is implemented and tested (manual via `{API_BASE_PATH}/docs` or automated tests once added).
- For each completed item, record brief test notes (input example and expected outcome) in your PR or commit message.
