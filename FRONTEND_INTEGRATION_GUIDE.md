# HomeBase OMS – Frontend Integration Guide

**Document Version:** 1.0
**API Version:** Current (as of 2025-11-11)
**Prepared for:** Frontend Development Team

---

## Executive Summary

✅ **All API endpoints required for the frontend development plan are FULLY IMPLEMENTED and DEPLOYED**

✅ **All three identified API gaps have been SATISFIED and VERIFIED in production**

✅ **The API is production-ready and accessible at: https://homebase-api.neutralfuels.net**

✅ **37 operations across 30 paths verified and accessible in production**

This guide provides the frontend team with a comprehensive reference for integrating with the HomeBase API, mapped to each phase of the development plan.

**Production API Documentation:** https://homebase-api.neutralfuels.net/api/docs

---

## Table of Contents

1. [API Implementation Status](#api-implementation-status)
2. [API Gaps Resolution](#api-gaps-resolution)
3. [Phase-by-Phase Integration Guide](#phase-by-phase-integration-guide)
4. [Sorting Capabilities Reference](#sorting-capabilities-reference)
5. [Authentication and Setup](#authentication-and-setup)
6. [Error Handling Patterns](#error-handling-patterns)
7. [Testing Endpoints](#testing-endpoints)
8. [Migration Checklist](#migration-checklist)

---

## API Implementation Status

### ✅ All Core Endpoints Implemented

All endpoints mentioned in the frontend development plan are fully implemented and tested:

#### Health Check
- `GET /health` - [health.py:5](app/routers/health.py#L5)

#### Users & Authentication
- `POST /users` - [users.py:28](app/routers/users.py#L28)
- `GET /users` - [users.py:51](app/routers/users.py#L51)
- `GET /users/{userId}` - [users.py:58](app/routers/users.py#L58)
- `PATCH /users/{id}` - [users.py:72](app/routers/users.py#L72)
- `DELETE /users/{userId}` - [users.py:87](app/routers/users.py#L87)
- `POST /auth/login` - [users.py:101](app/routers/users.py#L101)

#### Signups
- `POST /signups` - [signups.py:32](app/routers/signups.py#L32)
- `GET /signups` - [signups.py:70](app/routers/signups.py#L70) *(with sorting)*
- `GET /signups/all` - [signups.py:304](app/routers/signups.py#L304) *(with sorting)*
- `POST /signups/awaiting-deployment/batch` - [signups.py:113](app/routers/signups.py#L113)
- `GET /signups/awaiting-deployment` - [signups.py:277](app/routers/signups.py#L277)
- `PATCH /signups/status/batch` - [signups.py:360](app/routers/signups.py#L360)
- `POST /signups/ad-hoc-deploy` - [signups.py:184](app/routers/signups.py#L184)

#### Households
- `POST /households` - [households.py:26](app/routers/households.py#L26)
- `GET /households` - [households.py:67](app/routers/households.py#L67) *(with sorting)*
- `GET /households/{id}` - [households.py:48](app/routers/households.py#L48)
- `GET /households/{id}/history` - [households.py:103](app/routers/households.py#L103)

#### Containers
- `POST /containers` - [containers.py:17](app/routers/containers.py#L17)
- `GET /containers` - [containers.py:42](app/routers/containers.py#L42) *(with sorting)*
- `GET /containers/{id}` - [containers.py:32](app/routers/containers.py#L32)
- `GET /containers/{containerId}/history` - [containers.py:59](app/routers/containers.py#L59) ✨ **NEW**

#### Deployments
- `POST /deployments/assign` - [deployments.py:100](app/routers/deployments.py#L100)
- `GET /deployments` - [deployments.py:132](app/routers/deployments.py#L132) *(with sorting)*
- `PATCH /deployments/{id}/assign` - [deployments.py:166](app/routers/deployments.py#L166)
- `PATCH /deployments/{id}/status` - [deployments.py:179](app/routers/deployments.py#L179)
- `POST /deployments/perform` - [deployments.py:37](app/routers/deployments.py#L37)
- `POST /deployments/swap` - [deployments.py:22](app/routers/deployments.py#L22)

#### Collection Requests
- `POST /collection-requests` - [collection_requests.py:28](app/routers/collection_requests.py#L28)
- `GET /collection-requests` - [collection_requests.py:68](app/routers/collection_requests.py#L68) *(with sorting)*
- `GET /collection-requests/check-pending` - [collection_requests.py:101](app/routers/collection_requests.py#L101)
- `PATCH /collection-requests/{id}/assign` - [collection_requests.py:116](app/routers/collection_requests.py#L116)
- `PATCH /collection-requests/{id}/status` - [collection_requests.py:131](app/routers/collection_requests.py#L131)
- `POST /collections/start-manual` - [collection_requests.py:149](app/routers/collection_requests.py#L149)

#### Collections Summary
- `GET /collections` - [collections.py:21](app/routers/collections.py#L21) ✨ **NEW** *(with sorting and date filtering)*

#### QR System (Bonus)
- `GET /qr/sign` - [qr.py:7](app/routers/qr.py#L7)
- `GET /qr/verify` - [qr.py:12](app/routers/qr.py#L12)

---

## API Gaps Resolution

All three API gaps identified in the frontend development plan have been fully addressed:

### ✅ Gap 1: Container History Endpoint

**Status:** FULLY IMPLEMENTED

**Endpoint:** `GET /containers/{containerId}/history`

**Location:** [containers.py:59](app/routers/containers.py#L59)

**What It Provides:**
```json
{
  "container": {
    "id": "container_1",
    "serial": "C-0001",
    "currentHouseholdId": "hh_1",
    "state": "active"
  },
  "assignments": [
    {
      "householdId": "hh_1",
      "assignedAt": "2024-01-15T10:00:00Z",
      "unassignedAt": null,
      "assignedBy": "user_1",
      "assignmentReason": "initial_deployment"
    }
  ],
  "deployments": [
    {
      "type": "deployment",
      "performedAt": "2024-01-15T10:30:00Z",
      "performedBy": "user_1",
      "householdId": "hh_1",
      "installedContainerId": "container_1"
    }
  ],
  "collections": [
    {
      "requestId": "req_1",
      "householdId": "hh_1",
      "requestedAt": "2024-01-16T08:00:00Z",
      "status": "completed",
      "metrics": {
        "volumeL": 20.5,
        "weightKg": 18.1
      }
    }
  ]
}
```

**Frontend Usage:**
- Phase 4: Container detail view timeline
- Show complete movement history of containers
- Track which households have used each container
- Display collection activities for each container

---

### ✅ Gap 2: Collections Summary Endpoint

**Status:** FULLY IMPLEMENTED

**Endpoint:** `GET /collections`

**Location:** [collections.py:21](app/routers/collections.py#L21)

**Query Parameters:**
- `status` - Filter by status: `requested`, `completed`, or `any` (default: `completed`)
- `dateFrom` - Filter collections from this date (YYYY-MM-DD format)
- `dateTo` - Filter collections until this date (YYYY-MM-DD format)
- `householdId` - Filter by specific household
- `assignedTo` - Filter by assigned user
- `limit` - Pagination limit (default: 100)
- `sortBy` - Sort field: `requestedAt`, `status`, `householdId` (default: `requestedAt`)
- `sortDir` - Sort direction: `asc` or `desc` (default: `desc`)

**Response Example:**
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

**Frontend Usage:**
- Phase 5: Collection Receipts view
- Filter completed collections by date range (date-only filters)
- Export collection reports
- Track performance metrics (volume, weight)
- Audit collection activities by user

**Date Filter Implementation:**
```javascript
// Example: Get collections for January 2024
const params = {
  status: 'completed',
  dateFrom: '2024-01-01',
  dateTo: '2024-01-31',
  sortBy: 'requestedAt',
  sortDir: 'desc'
};

const response = await homebaseClient.get('/collections', { params });
```

---

### ✅ Gap 3: Sorting Parameters Support

**Status:** FULLY IMPLEMENTED ACROSS ALL LIST ENDPOINTS

All list endpoints now support standardized sorting via `sortBy` and `sortDir` query parameters.

**Supported Endpoints and Sort Fields:**

| Endpoint | sortBy Options | sortDir | Default Sort |
|----------|----------------|---------|--------------|
| `GET /signups` | `createdAt`, `status`, `fullName` | `asc`, `desc` | `createdAt desc` |
| `GET /signups/all` | `createdAt`, `status`, `fullName` | `asc`, `desc` | `createdAt desc` |
| `GET /households` | `createdAt`, `villaNumber`, `community` | `asc`, `desc` | `createdAt desc` |
| `GET /containers` | `createdAt`, `serial`, `assignedHouseholdId` | `asc`, `desc` | `createdAt desc` |
| `GET /deployments` | `performedAt`, `createdAt`, `type`, `status` | `asc`, `desc` | `performedAt desc` |
| `GET /collection-requests` | `requestedAt`, `status`, `householdId` | `asc`, `desc` | `requestedAt desc` |
| `GET /collections` | `requestedAt`, `status`, `householdId` | `asc`, `desc` | `requestedAt desc` |

**Frontend Implementation:**
```javascript
// Example: Sort signups by name ascending
const response = await homebaseClient.get('/signups/all', {
  params: {
    sortBy: 'fullName',
    sortDir: 'asc'
  }
});

// Example: Sort deployments by performed date descending
const response = await homebaseClient.get('/deployments', {
  params: {
    sortBy: 'performedAt',
    sortDir: 'desc'
  }
});
```

**Benefits:**
- **Server-side sorting** reduces client-side processing for large datasets
- **Consistent API** across all list endpoints
- **Performance** optimized with database indexes
- **Scalability** ready for production data volumes

---

## Phase-by-Phase Integration Guide

### Phase 0: Foundations

#### Set Up API Client

**Base Configuration:**
```javascript
// src/services/homebaseClient.js
import axios from 'axios';
import store from '@/store';

const homebaseClient = axios.create({
  baseURL: store.state.homebase.apiBaseUrl, // e.g., 'http://localhost:8000'
  headers: {
    'x-api-key': store.state.homebase.apiKey,
    'Content-Type': 'application/json'
  }
});

// Error handling interceptor
homebaseClient.interceptors.response.use(
  response => response,
  error => {
    // Standardized error handling
    const message = error.response?.data?.detail || 'An error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

export default homebaseClient;
```

#### Health Check Test
```javascript
// Test API connectivity
const healthCheck = async () => {
  try {
    const response = await homebaseClient.get('/health');
    console.log('API Health:', response.data); // { ok: true }
    return true;
  } catch (error) {
    console.error('API is down:', error);
    return false;
  }
};
```

#### Shared Table Components

Create reusable components:
- `SortableTableHeader.vue` - Handles column sorting
- `DateRangeFilter.vue` - Date-only filter controls
- `LoadingState.vue`, `EmptyState.vue`, `ErrorState.vue`

---

### Phase 1: Signups (HomeBaseSignups.vue)

#### Endpoints to Use

**1. List All Signups**
```javascript
GET /signups/all

// Parameters:
{
  status: 'any' | 'pending' | 'awaiting_deployment' | 'active' | 'inactive' | 'deleted',
  community: 'string',
  limit: number,
  sortBy: 'createdAt' | 'status' | 'fullName',
  sortDir: 'asc' | 'desc'
}

// Example:
const fetchSignups = async (filters) => {
  const params = {
    status: filters.status || 'any',
    community: filters.community,
    limit: 100,
    sortBy: filters.sortBy || 'createdAt',
    sortDir: filters.sortDir || 'desc'
  };

  const response = await homebaseClient.get('/signups/all', { params });
  return response.data;
};
```

**2. Bulk Request Deployment**
```javascript
POST /signups/awaiting-deployment/batch

// Body:
{
  "signupIds": ["signup_1", "signup_2", "signup_3"]
}

// Example:
const requestDeployment = async (selectedSignupIds) => {
  const response = await homebaseClient.post('/signups/awaiting-deployment/batch', {
    signupIds: selectedSignupIds
  });
  return response.data;
  // Returns: [{ signupId, householdId, status: "updated" }]
};
```

**3. Batch Update Status (Optional)**
```javascript
PATCH /signups/status/batch

// Body:
{
  "items": [
    {
      "signupId": "signup_1",
      "status": "inactive",
      "reason": "user request",
      "updatedBy": "ops_1"
    }
  ]
}

// Example:
const updateSignupStatuses = async (updates) => {
  const response = await homebaseClient.patch('/signups/status/batch', {
    items: updates
  });
  return response.data; // { updated: 2, skipped: 0, errors: 0 }
};
```

#### Implementation Notes

**Table Columns:**
- Full Name
- Phone
- Email
- Community
- Villa Number
- Status (with color chips)
- Created At (formatted date)

**Filters:**
- Status: Multi-select dropdown
- Community: Dropdown or autocomplete
- Date Range: CreatedAt (date-only)
- Text Search: Name/Phone/Email (client-side filter)

**Bulk Actions:**
- Select multiple rows
- "Request Deployment" button
- Show success/error feedback

**Acceptance Criteria:**
- ✅ Sorting works on all columns (use sortBy/sortDir params)
- ✅ Bulk deployment moves selected items to `awaiting_deployment`
- ✅ Table updates after successful action

---

### Phase 2: Deployments (HomeBaseDeployments.vue)

#### Endpoints to Use

**1. Get Signups Awaiting Deployment**
```javascript
GET /signups/awaiting-deployment

// Example:
const fetchAwaitingDeployment = async () => {
  const response = await homebaseClient.get('/signups/awaiting-deployment');
  return response.data;
};
```

**2. Assign Deployment Tasks**
```javascript
POST /deployments/assign

// Body:
{
  "householdId": "hh_1",
  "assignedTo": "user_alex",
  "notes": "Deliver by Tuesday"
}

// Example:
const assignDeployment = async (householdId, userId, notes) => {
  const response = await homebaseClient.post('/deployments/assign', {
    householdId,
    assignedTo: userId,
    notes
  });
  return response.data; // { id: "dep_task_...", status: "assigned" }
};
```

**3. List Deployment Tasks**
```javascript
GET /deployments

// Parameters:
{
  assignedTo: 'user_id',
  status: 'assigned' | 'in_progress' | 'completed' | 'any',
  type: 'deployment' | 'swap' | 'deployment_task' | 'any',
  limit: number,
  sortBy: 'performedAt' | 'createdAt' | 'type' | 'status',
  sortDir: 'asc' | 'desc'
}

// Example:
const fetchDeployments = async (filters) => {
  const params = {
    status: filters.status || 'any',
    type: 'deployment_task',
    sortBy: 'createdAt',
    sortDir: 'desc'
  };

  const response = await homebaseClient.get('/deployments', { params });
  return response.data;
};
```

**4. Update Task Status**
```javascript
PATCH /deployments/{id}/status

// Body:
{
  "status": "in_progress" | "completed" | "cancelled"
}

// Example:
const updateTaskStatus = async (taskId, status) => {
  const response = await homebaseClient.patch(`/deployments/${taskId}/status`, {
    status
  });
  return response.data;
};
```

**5. Perform Deployment (Ground Team)**
```javascript
POST /deployments/perform

// Body:
{
  "householdId": "hh_1",
  "containerId": "container_2",
  "performedBy": "user_alex"
}

// Example:
const performDeployment = async (householdId, containerId, userId) => {
  const response = await homebaseClient.post('/deployments/perform', {
    householdId,
    containerId,
    performedBy: userId
  });
  return response.data; // { ok: true, deploymentId: "dep_..." }
};
```

#### Implementation Notes

**Two Views:**

1. **Awaiting Deployment List:**
   - Shows signups in `awaiting_deployment` status
   - Assign to ground team users
   - Bulk assign capability

2. **Deployment Tasks List:**
   - Shows assigned/in_progress/completed tasks
   - Filter by user and status
   - Update task status

**Status Flow:**
```
assigned → in_progress → completed
```

**Acceptance Criteria:**
- ✅ Can assign multiple items to a user
- ✅ Tasks reflect assignment immediately
- ✅ Completing a task transitions signup to `active`
- ✅ Items disappear from awaiting list when deployed

---

### Phase 3: Households (HomeBaseHouseHolds.vue)

#### Endpoints to Use

**1. List Households**
```javascript
GET /households

// Parameters:
{
  community: 'string',
  status: 'string',
  hasContainer: true | false,
  limit: number,
  sortBy: 'createdAt' | 'villaNumber' | 'community',
  sortDir: 'asc' | 'desc'
}

// Example:
const fetchHouseholds = async (filters) => {
  const params = {
    community: filters.community,
    hasContainer: filters.hasContainer,
    sortBy: filters.sortBy || 'createdAt',
    sortDir: filters.sortDir || 'desc',
    limit: 100
  };

  const response = await homebaseClient.get('/households', { params });
  return response.data;
};
```

**2. Get Household Details**
```javascript
GET /households/{householdId}

// Example:
const fetchHouseholdDetails = async (householdId) => {
  const response = await homebaseClient.get(`/households/${householdId}`);
  return response.data;
};
```

**3. Get Household History**
```javascript
GET /households/{householdId}/history

// Response:
{
  "household": {
    "id": "hh_1",
    "currentContainerId": "container_1"
  },
  "assignments": [
    {
      "containerId": "container_1",
      "assignedAt": "2024-01-15T10:00:00Z"
    }
  ],
  "deployments": [
    {
      "type": "deployment",
      "performedAt": "2024-01-15T10:30:00Z"
    }
  ],
  "totalVolumeCollectedL": 120.0
}

// Example:
const fetchHouseholdHistory = async (householdId) => {
  const response = await homebaseClient.get(`/households/${householdId}/history`);
  return response.data;
};
```

#### Implementation Notes

**Table Columns:**
- Household ID
- Head of Household (from linked signup)
- Community
- Villa Number
- Current Container (serial number)
- Status
- Created At

**Detail View/Drawer:**
- Household information
- Assignment history timeline
- Deployment/swap history
- Total volume collected
- Current container details

**Acceptance Criteria:**
- ✅ List view with filters and sorting
- ✅ History view shows complete timeline
- ✅ Volume metrics displayed correctly

---

### Phase 4: Containers (HomeBaseCotainers.vue)

#### Endpoints to Use

**1. List Containers**
```javascript
GET /containers

// Parameters:
{
  unassigned: true | false,
  limit: number,
  sortBy: 'createdAt' | 'serial' | 'assignedHouseholdId',
  sortDir: 'asc' | 'desc'
}

// Example:
const fetchContainers = async (filters) => {
  const params = {
    unassigned: filters.unassigned,
    sortBy: filters.sortBy || 'serial',
    sortDir: filters.sortDir || 'asc',
    limit: 100
  };

  const response = await homebaseClient.get('/containers', { params });
  return response.data;
};
```

**2. Get Container Details**
```javascript
GET /containers/{containerId}

// Example:
const fetchContainerDetails = async (containerId) => {
  const response = await homebaseClient.get(`/containers/${containerId}`);
  return response.data;
};
```

**3. Get Container History** ✨ **NEW**
```javascript
GET /containers/{containerId}/history

// Response:
{
  "container": {
    "id": "container_1",
    "serial": "C-0001",
    "currentHouseholdId": "hh_1",
    "state": "active"
  },
  "assignments": [
    {
      "householdId": "hh_1",
      "assignedAt": "2024-01-15T10:00:00Z",
      "unassignedAt": null,
      "assignedBy": "user_1",
      "assignmentReason": "initial_deployment"
    }
  ],
  "deployments": [
    {
      "type": "deployment",
      "performedAt": "2024-01-15T10:30:00Z",
      "performedBy": "user_1",
      "householdId": "hh_1",
      "installedContainerId": "container_1"
    }
  ],
  "collections": [
    {
      "requestId": "req_1",
      "householdId": "hh_1",
      "requestedAt": "2024-01-16T08:00:00Z",
      "status": "completed",
      "metrics": {
        "volumeL": 20.5,
        "weightKg": 18.1
      }
    }
  ]
}

// Example:
const fetchContainerHistory = async (containerId) => {
  const response = await homebaseClient.get(`/containers/${containerId}/history`);
  return response.data;
};
```

#### Implementation Notes

**Table Columns:**
- Serial Number
- Type (wheelieBin, etc.)
- Capacity (L)
- Assigned Household (if any)
- Status (Deployed/Unassigned)
- Last Activity Date

**Detail View:**
- Container profile (serial, type, capacity)
- Current assignment status
- Timeline of movements:
  - Assignments
  - Deployments
  - Swaps
  - Collections

**Status Indicators:**
- 🟢 Deployed (has currentHouseholdId)
- ⚪ Unassigned (no currentHouseholdId)

**Acceptance Criteria:**
- ✅ At-a-glance deployment status visible
- ✅ Detail view shows complete history timeline
- ✅ Can filter by unassigned containers

---

### Phase 5: Collection Receipts (HomeBaseCollectionReceipts.vue)

#### Endpoints to Use

**1. Get Completed Collections** ✨ **NEW**
```javascript
GET /collections

// Parameters:
{
  status: 'completed',
  dateFrom: 'YYYY-MM-DD',
  dateTo: 'YYYY-MM-DD',
  householdId: 'string',
  assignedTo: 'string',
  limit: number,
  sortBy: 'requestedAt' | 'status' | 'householdId',
  sortDir: 'asc' | 'desc'
}

// Example:
const fetchCollectionReceipts = async (filters) => {
  const params = {
    status: 'completed',
    dateFrom: filters.dateFrom, // '2024-01-01'
    dateTo: filters.dateTo,     // '2024-01-31'
    householdId: filters.householdId,
    assignedTo: filters.assignedTo,
    sortBy: 'requestedAt',
    sortDir: 'desc',
    limit: 100
  };

  const response = await homebaseClient.get('/collections', { params });
  return response.data;
};
```

**Alternative: Use Collection Requests Endpoint**
```javascript
GET /collection-requests

// Parameters:
{
  status: 'completed',
  householdId: 'string',
  assignedTo: 'string',
  limit: number,
  sortBy: 'requestedAt',
  sortDir: 'desc'
}
```

#### Implementation Notes

**Table Columns:**
- Collection Date (formatted)
- Household (ID or name)
- Container (serial)
- Volume (L)
- Weight (Kg)
- Performed By (username)
- Notes

**Filters:**
- Date Range (date-only, no time)
- Household (dropdown/autocomplete)
- Performed By (user dropdown)

**Export Functionality:**
```javascript
// CSV Export
const exportToCSV = (data) => {
  const headers = ['Date', 'Household', 'Container', 'Volume (L)', 'Weight (Kg)', 'Performed By'];
  const rows = data.map(item => [
    formatDate(item.requestedAt),
    item.householdId,
    item.containerId,
    item.volumeL,
    item.weightKg,
    item.performedBy
  ]);

  // Create CSV blob and download
  const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `collection-receipts-${Date.now()}.csv`;
  a.click();
};
```

**Acceptance Criteria:**
- ✅ Completed collections visible
- ✅ Date-only filters work (no time input)
- ✅ Export to CSV functional
- ✅ Metrics (volume, weight) displayed correctly

---

### Phase 6: Users (HomeBaseUsers.vue)

#### Endpoints to Use

**1. Create User**
```javascript
POST /users

// Body:
{
  "username": "alex",
  "password": "secret"
}

// Example:
const createUser = async (username, password) => {
  const response = await homebaseClient.post('/users', {
    username,
    password
  });
  return response.data; // { id, username, createdAt }
};
```

**2. List Users**
```javascript
GET /users

// Parameters:
{
  limit: number
}

// Example:
const fetchUsers = async () => {
  const response = await homebaseClient.get('/users', {
    params: { limit: 100 }
  });
  return response.data;
};
```

**3. Get User Details**
```javascript
GET /users/{userId}

// Example:
const fetchUserDetails = async (userId) => {
  const response = await homebaseClient.get(`/users/${userId}`);
  return response.data;
};
```

**4. Update User Password**
```javascript
PATCH /users/{userId}

// Body:
{
  "password": "newSecret"
}

// Example:
const updateUserPassword = async (userId, newPassword) => {
  const response = await homebaseClient.patch(`/users/${userId}`, {
    password: newPassword
  });
  return response.data;
};
```

**5. Delete User**
```javascript
DELETE /users/{userId}

// Example:
const deleteUser = async (userId) => {
  const response = await homebaseClient.delete(`/users/${userId}`);
  return response.data;
};
```

**6. Login (Authentication)**
```javascript
POST /auth/login

// Body:
{
  "username": "alex",
  "password": "secret"
}

// Example:
const login = async (username, password) => {
  const response = await homebaseClient.post('/auth/login', {
    username,
    password
  });
  return response.data; // { ok: true, userId, username }
};
```

#### Implementation Notes

**Table Columns:**
- Username
- User ID
- Created At
- Actions (Edit, Delete)

**Create/Edit Modal:**
- Username input (unique)
- Password input (hidden)
- Validation:
  - Username required
  - Password min length
  - Confirm password match

**Delete Confirmation:**
- Show warning modal
- Confirm destructive action
- Check for active assignments before deleting

**Acceptance Criteria:**
- ✅ Create user with unique username
- ✅ Edit password flow works
- ✅ Delete with confirmation
- ✅ Validation and error feedback

---

## Sorting Capabilities Reference

### Universal Sorting Parameters

All list endpoints support these query parameters:

```javascript
{
  sortBy: 'string',    // Field to sort by (endpoint-specific)
  sortDir: 'asc' | 'desc'  // Sort direction (default: desc)
}
```

### Endpoint-Specific Sort Fields

| Endpoint | Available sortBy Fields | Default |
|----------|------------------------|---------|
| `GET /signups` | `createdAt`, `status`, `fullName` | `createdAt` |
| `GET /signups/all` | `createdAt`, `status`, `fullName` | `createdAt` |
| `GET /households` | `createdAt`, `villaNumber`, `community` | `createdAt` |
| `GET /containers` | `createdAt`, `serial`, `assignedHouseholdId` | `createdAt` |
| `GET /deployments` | `performedAt`, `createdAt`, `type`, `status` | `performedAt` |
| `GET /collection-requests` | `requestedAt`, `status`, `householdId` | `requestedAt` |
| `GET /collections` | `requestedAt`, `status`, `householdId` | `requestedAt` |

### Frontend Sorting Implementation

**Reusable Table Header Component:**
```vue
<!-- SortableTableHeader.vue -->
<template>
  <th @click="toggleSort" class="sortable">
    {{ label }}
    <span v-if="isActive">
      {{ sortDir === 'asc' ? '↑' : '↓' }}
    </span>
  </th>
</template>

<script>
export default {
  props: {
    label: String,
    field: String,
    currentSortBy: String,
    currentSortDir: String
  },
  computed: {
    isActive() {
      return this.currentSortBy === this.field;
    }
  },
  methods: {
    toggleSort() {
      const newDir = this.isActive && this.currentSortDir === 'asc' ? 'desc' : 'asc';
      this.$emit('sort', { sortBy: this.field, sortDir: newDir });
    }
  }
};
</script>
```

**Usage Example:**
```vue
<template>
  <table>
    <thead>
      <tr>
        <SortableTableHeader
          label="Name"
          field="fullName"
          :currentSortBy="sortBy"
          :currentSortDir="sortDir"
          @sort="handleSort"
        />
        <SortableTableHeader
          label="Created"
          field="createdAt"
          :currentSortBy="sortBy"
          :currentSortDir="sortDir"
          @sort="handleSort"
        />
      </tr>
    </thead>
  </table>
</template>

<script>
export default {
  data() {
    return {
      sortBy: 'createdAt',
      sortDir: 'desc'
    };
  },
  methods: {
    handleSort({ sortBy, sortDir }) {
      this.sortBy = sortBy;
      this.sortDir = sortDir;
      this.fetchData(); // Re-fetch with new sort params
    },
    async fetchData() {
      const params = {
        sortBy: this.sortBy,
        sortDir: this.sortDir
      };
      const response = await homebaseClient.get('/signups/all', { params });
      this.items = response.data;
    }
  }
};
</script>
```

---

## Authentication and Setup

### API Key Configuration

**Development (Localhost):**
```javascript
// store/modules/homebase.js
export default {
  state: {
    apiBaseUrl: 'http://localhost:8000',
    apiKey: 'your-development-api-key'
  }
};
```

**Production:**
```javascript
// Use environment variables
export default {
  state: {
    apiBaseUrl: process.env.VUE_APP_HOMEBASE_API_URL,
    apiKey: process.env.VUE_APP_HOMEBASE_API_KEY
  }
};
```

### Required Headers

All authenticated requests must include:
```javascript
{
  'x-api-key': 'YOUR_API_KEY',
  'Content-Type': 'application/json'
}
```

### Public Endpoints (No API Key Required)

These endpoints are public and don't require the `x-api-key` header:
- `GET /health`
- `GET /qr/sign`
- `GET /qr/verify`
- `POST /auth/login`

---

## Error Handling Patterns

### Standard HTTP Status Codes

| Status Code | Meaning | Frontend Action |
|-------------|---------|-----------------|
| 400 | Bad Request | Show validation errors to user |
| 401 | Unauthorized | Check API key, redirect to login |
| 404 | Not Found | Show "not found" message |
| 409 | Conflict | Show conflict error (e.g., duplicate username) |
| 500 | Server Error | Show generic error, log to console |

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Frontend Error Handler

```javascript
// src/services/homebaseClient.js
homebaseClient.interceptors.response.use(
  response => response,
  error => {
    const status = error.response?.status;
    const message = error.response?.data?.detail || 'An unexpected error occurred';

    switch (status) {
      case 400:
        // Validation error
        showNotification('error', message);
        break;
      case 401:
        // Unauthorized
        showNotification('error', 'Authentication failed. Please check your API key.');
        break;
      case 404:
        showNotification('error', 'Resource not found.');
        break;
      case 409:
        // Conflict (e.g., duplicate)
        showNotification('error', message);
        break;
      default:
        showNotification('error', 'An error occurred. Please try again.');
    }

    return Promise.reject(error);
  }
);
```

---

## Testing Endpoints

### Health Check

**Test API Connectivity:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "ok": true
}
```

### Authentication Test

**Test API Key:**
```bash
curl http://localhost:8000/users \
  -H "x-api-key: YOUR_API_KEY"
```

**Expected:** 200 OK with user list

### Login Test

**Test User Credentials:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alex", "password": "secret"}'
```

**Expected Response:**
```json
{
  "ok": true,
  "userId": "user_alex",
  "username": "alex"
}
```

---

## Migration Checklist

### Pre-Development Setup

- [ ] Obtain API key from backend team
- [ ] Configure base URL in store (`localhost:8000` for dev)
- [ ] Set up axios client with interceptors
- [ ] Test health endpoint connectivity
- [ ] Test authentication with API key

### Phase 0: Foundations

- [ ] Create homebaseClient.js with proper configuration
- [ ] Build reusable table components (SortableTableHeader, etc.)
- [ ] Create date-only filter component (DateRangeFilter)
- [ ] Build loading/empty/error state components
- [ ] Test API connectivity with health check

### Phase 1: Signups

- [ ] Implement signups list view with filters
- [ ] Add sorting to all columns
- [ ] Implement bulk selection
- [ ] Integrate `POST /signups/awaiting-deployment/batch`
- [ ] Test bulk deployment flow
- [ ] Add status batch update (optional)

### Phase 2: Deployments

- [ ] Implement awaiting deployment list (`GET /signups/awaiting-deployment`)
- [ ] Build assignment panel with user selection
- [ ] Integrate `POST /deployments/assign`
- [ ] Create deployment tasks list (`GET /deployments`)
- [ ] Implement status update flow (`PATCH /deployments/{id}/status`)
- [ ] Test complete deployment workflow

### Phase 3: Households

- [ ] Implement households list with filters
- [ ] Add sorting capability
- [ ] Build household detail view/drawer
- [ ] Integrate `GET /households/{id}/history`
- [ ] Display timeline of assignments/deployments
- [ ] Show total volume collected metric

### Phase 4: Containers

- [ ] Implement containers list with filters
- [ ] Add unassigned filter toggle
- [ ] Build container detail view
- [ ] Integrate `GET /containers/{containerId}/history` ✨
- [ ] Display movement timeline
- [ ] Show deployment status indicators

### Phase 5: Collection Receipts

- [ ] Implement collections list view
- [ ] Integrate `GET /collections` with status=completed ✨
- [ ] Add date-only filter controls (dateFrom, dateTo)
- [ ] Implement household and user filters
- [ ] Build CSV export functionality
- [ ] Display volume/weight metrics

### Phase 6: Users

- [ ] Implement users list view
- [ ] Build create user modal
- [ ] Build edit password modal
- [ ] Add delete confirmation dialog
- [ ] Integrate all user CRUD endpoints
- [ ] Add validation and error handling

### Phase 7: QA & Hardening

- [ ] Audit all loading states
- [ ] Audit all error states
- [ ] Test all filter combinations
- [ ] Test sorting on all endpoints
- [ ] Verify pagination works correctly
- [ ] Test bulk operations
- [ ] Add input validation
- [ ] Implement guard rails for destructive actions
- [ ] Performance testing with large datasets
- [ ] E2E smoke tests for primary flows

### Phase 8: Productionization

- [ ] Update base URL to production API
- [ ] Move API key to environment variables/secrets
- [ ] Remove localhost-specific logic
- [ ] Update CI/CD configuration
- [ ] Perform final security audit
- [ ] Deploy to staging
- [ ] User acceptance testing
- [ ] Deploy to production

---

## Additional Resources

### API Documentation Files

- **Complete API Reference:** [API_REFERENCE.md](API_REFERENCE.md)
  - Detailed endpoint documentation
  - Request/response examples
  - Common types and data structures
  - Error handling patterns

### Backend Team Contacts

For questions or issues:
- Backend API issues: Contact backend team lead
- API key requests: Contact DevOps/Security team
- Documentation updates: Submit PR to API_REFERENCE.md

### OpenAPI/Swagger Documentation

The API provides interactive documentation at:
- **Development:** `http://localhost:8000/docs`
- **Production:** `https://your-production-url.com/docs`

Use this for:
- Testing endpoints interactively
- Viewing request/response schemas
- Generating API client code

---

## Summary

### ✅ What's Ready

1. **All 30+ endpoints** mentioned in the development plan are implemented
2. **All 3 API gaps** are satisfied:
   - Container history endpoint ✅
   - Collections summary endpoint ✅
   - Sorting parameters ✅
3. **Comprehensive API documentation** available
4. **Authentication** and security in place
5. **Error handling** standardized across all endpoints

### 🎯 Next Steps

1. **Week 1:** Set up API client and complete Phase 0 + Phase 1 (Signups)
2. **Week 2:** Implement Phase 2 (Deployments) + Phase 3 (Households list)
3. **Week 3:** Complete Phase 3 (Households history) + Phase 4 (Containers)
4. **Week 4:** Finish Phase 4 (Container detail) + Phase 5 (Collection Receipts)
5. **Week 5:** Phase 6 (Users) + Phase 7 (QA) + Phase 8 (Production)

### 📞 Support

For any questions or clarifications about the API:
1. Check [API_REFERENCE.md](API_REFERENCE.md) first
2. Test endpoints at `/docs` (Swagger UI)
3. Contact backend team for urgent issues

---

**Document prepared by:** Backend Team
**Date:** 2025-11-11
**Status:** Ready for Frontend Integration
