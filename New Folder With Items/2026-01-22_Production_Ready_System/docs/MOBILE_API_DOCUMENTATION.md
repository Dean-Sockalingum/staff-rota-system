# Mobile App API Documentation

**Created:** 30 December 2025  
**Task 38:** Mobile App API  
**Version:** 1.0  
**Commit:** 7a00da7

## Overview

REST API for mobile app access to the Staff Rota System. Provides endpoints for staff to view schedules, request leave, and manage shift swaps.

## Authentication

### Token Authentication

The API uses token-based authentication. Staff members must obtain a token and include it in the `Authorization` header:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Obtaining a Token

Tokens are created for users when needed. Contact system administrators to obtain your API token.

### Session Authentication

For web-based access, Django session authentication is also supported (already logged-in users).

## Base URL

```
/api/mobile/
```

## API Endpoints

### 1. Users

#### GET /api/mobile/users/
List all active users.

**Filters:**
- `role`: Filter by role ID
- `unit`: Filter by unit ID
- `team`: Filter by team (A, B, C)
- `is_active`: Filter by active status

**Search:** first_name, last_name, sap, email

**Response:**
```json
{
  "count": 50,
  "next": "http://example.com/api/mobile/users/?page=2",
  "previous": null,
  "results": [
    {
      "sap": "SAP001",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "phone_number": "01234567890",
      "role": 1,
      "role_name": "SCW",
      "unit": 1,
      "unit_name": "Pear",
      "team": "A",
      "shift_preference": "DAY_SENIOR",
      "is_active": true,
      "annual_leave_allowance": 28,
      "annual_leave_used": 10,
      "annual_leave_remaining": 18,
      "shifts_per_week": 3
    }
  ]
}
```

#### GET /api/mobile/users/{sap}/
Get specific user details.

#### GET /api/mobile/users/me/
Get current authenticated user's information.

**Response:** Same as individual user

---

### 2. Roles

#### GET /api/mobile/roles/
List all roles.

**Response:**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "name": "SCW",
      "is_management": false,
      "permission_level": "LIMITED"
    },
    {
      "id": 2,
      "name": "SSCW",
      "is_management": false,
      "permission_level": "MOST"
    }
  ]
}
```

---

### 3. Care Homes

#### GET /api/mobile/care-homes/
List all active care homes.

**Filters:**
- `name`: Filter by care home name
- `is_active`: Filter by active status

**Search:** name, location_address

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "name": "ORCHARD_GROVE",
      "bed_capacity": 60,
      "current_occupancy": 58,
      "occupancy_rate": 96.7,
      "location_address": "123 Main Street, Glasgow",
      "postcode": "G1 1AA",
      "main_phone": "0141 123 4567",
      "main_email": "orchard@example.com",
      "is_active": true,
      "home_manager": 5,
      "manager_name": "Jane Smith"
    }
  ]
}
```

---

### 4. Units

#### GET /api/mobile/units/
List all active units.

**Filters:**
- `care_home`: Filter by care home ID
- `is_active`: Filter by active status

**Search:** name, description

**Response:**
```json
{
  "count": 41,
  "results": [
    {
      "id": 1,
      "name": "OG_PEAR",
      "description": "Orchard Grove - Pear Unit",
      "care_home": 1,
      "care_home_name": "ORCHARD_GROVE",
      "is_active": true,
      "min_day_staff": 3,
      "ideal_day_staff": 4,
      "min_night_staff": 2,
      "ideal_night_staff": 3
    }
  ]
}
```

---

### 5. Shift Types

#### GET /api/mobile/shift-types/
List all active shift types.

**Filters:**
- `care_home`: Filter by care home ID
- `role`: Filter by role ID
- `is_active`: Filter by active status

**Search:** name

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "name": "Day - SCW",
      "start_time": "07:00:00",
      "end_time": "19:00:00",
      "care_home": 1,
      "care_home_name": "ORCHARD_GROVE",
      "role": 1,
      "role_name": "SCW",
      "is_active": true,
      "duration_hours": 12.0
    }
  ]
}
```

---

### 6. Shifts

#### GET /api/mobile/shifts/
List all shifts.

**Filters:**
- `user`: Filter by user SAP
- `unit`: Filter by unit ID
- `shift_type`: Filter by shift type ID
- `date`: Filter by specific date (YYYY-MM-DD)
- `status`: Filter by status (SCHEDULED, COMPLETED, CANCELLED)

**Search:** user__first_name, user__last_name

**Ordering:** date, status (default: -date)

**Response:**
```json
{
  "count": 500,
  "results": [
    {
      "id": 1,
      "user": "SAP001",
      "user_name": "John Doe",
      "shift_type": 1,
      "shift_type_name": "Day - SCW",
      "date": "2025-12-30",
      "unit": 1,
      "unit_name": "OG_PEAR",
      "care_home_name": "ORCHARD_GROVE",
      "status": "SCHEDULED",
      "shift_classification": "STANDARD",
      "shift_pattern": "PATTERN_A",
      "is_overtime": false,
      "created_at": "2025-12-01T10:00:00Z",
      "updated_at": "2025-12-01T10:00:00Z"
    }
  ]
}
```

#### GET /api/mobile/shifts/my_shifts/
Get shifts for the authenticated user.

**Query Parameters:**
- `start_date`: Filter from this date (YYYY-MM-DD)
- `end_date`: Filter until this date (YYYY-MM-DD)

**Response:** Same as shift list

#### GET /api/mobile/shifts/upcoming/
Get next 10 upcoming shifts for the authenticated user.

**Response:** Same as shift list (limited to 10)

---

### 7. Leave Requests

#### GET /api/mobile/leave-requests/
List all leave requests.

**Filters:**
- `user`: Filter by user SAP
- `leave_type`: Filter by type (ANNUAL, SICK, OTHER)
- `status`: Filter by status (PENDING, APPROVED, DENIED)

**Ordering:** start_date, created_at (default: -created_at)

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "user": "SAP001",
      "user_name": "John Doe",
      "leave_type": "ANNUAL",
      "start_date": "2026-01-15",
      "end_date": "2026-01-20",
      "days_requested": 4,
      "status": "PENDING",
      "reason": "Family holiday",
      "approved_by": null,
      "approved_by_name": null,
      "approval_date": null,
      "approval_notes": "",
      "created_at": "2025-12-15T10:00:00Z"
    }
  ]
}
```

#### POST /api/mobile/leave-requests/
Create a new leave request.

**Request Body:**
```json
{
  "leave_type": "ANNUAL",
  "start_date": "2026-02-01",
  "end_date": "2026-02-05",
  "days_requested": 3,
  "reason": "Personal time"
}
```

**Note:** `user` is automatically set to the authenticated user.

**Response:** Created leave request (201)

#### GET /api/mobile/leave-requests/my_requests/
Get leave requests for the authenticated user.

**Response:** Same as leave request list

#### POST /api/mobile/leave-requests/{id}/approve/
Approve a leave request (managers only).

**Permissions:** Requires `can_approve_leave` permission

**Request Body:**
```json
{
  "notes": "Approved - coverage confirmed"
}
```

**Response:** Updated leave request

#### POST /api/mobile/leave-requests/{id}/deny/
Deny a leave request (managers only).

**Permissions:** Requires `can_approve_leave` permission

**Request Body:**
```json
{
  "notes": "Denied - insufficient coverage"
}
```

**Response:** Updated leave request

---

### 8. Shift Swap Requests

#### GET /api/mobile/shift-swaps/
List all shift swap requests.

**Filters:**
- `requesting_user`: Filter by requesting user SAP
- `target_user`: Filter by target user SAP
- `status`: Filter by status (PENDING, AUTO_APPROVED, APPROVED, DENIED, CANCELLED)

**Ordering:** requested_at (default: -requested_at)

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": 1,
      "requesting_user": "SAP001",
      "requesting_user_name": "John Doe",
      "target_user": "SAP002",
      "target_user_name": "Jane Smith",
      "requesting_shift": 100,
      "requesting_shift_date": "2026-01-15",
      "target_shift": 101,
      "target_shift_date": "2026-01-16",
      "status": "PENDING",
      "requested_at": "2025-12-20T10:00:00Z",
      "processed_at": null,
      "processed_by": null,
      "automated_decision": false,
      "qualification_match_score": 95,
      "wdt_compliance_check": true
    }
  ]
}
```

#### POST /api/mobile/shift-swaps/
Create a new shift swap request.

**Request Body:**
```json
{
  "target_user": "SAP002",
  "requesting_shift": 100,
  "target_shift": 101
}
```

**Note:** `requesting_user` is automatically set to the authenticated user.

**Response:** Created swap request (201)

#### GET /api/mobile/shift-swaps/my_requests/
Get shift swap requests involving the authenticated user (as requester or target).

**Response:** Same as swap request list

#### POST /api/mobile/shift-swaps/{id}/approve/
Approve a shift swap request.

**Permissions:** Must be target user OR have management permissions

**Note:** Automatically performs the shift swap (swaps users on both shifts).

**Response:** Updated swap request with status APPROVED

#### POST /api/mobile/shift-swaps/{id}/deny/
Deny a shift swap request.

**Permissions:** Must be target user OR have management permissions

**Response:** Updated swap request with status DENIED

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://example.com/api/mobile/shifts/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Filtering and Search

### Filters

Use query parameters matching field names:
```
GET /api/mobile/shifts/?user=SAP001&status=SCHEDULED
```

### Search

Use the `search` parameter:
```
GET /api/mobile/users/?search=John
```

### Ordering

Use the `ordering` parameter:
```
GET /api/mobile/shifts/?ordering=-date
```

Prefix with `-` for descending order.

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": ["Error message"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "error": "You do not have permission to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Example Usage

### Python (requests)
```python
import requests

headers = {
    'Authorization': 'Token YOUR_TOKEN_HERE'
}

# Get my shifts
response = requests.get(
    'http://localhost:8000/api/mobile/shifts/my_shifts/',
    headers=headers
)
shifts = response.json()

# Create leave request
leave_data = {
    'leave_type': 'ANNUAL',
    'start_date': '2026-02-01',
    'end_date': '2026-02-05',
    'days_requested': 3,
    'reason': 'Holiday'
}
response = requests.post(
    'http://localhost:8000/api/mobile/leave-requests/',
    headers=headers,
    json=leave_data
)
```

### JavaScript (fetch)
```javascript
const headers = {
    'Authorization': 'Token YOUR_TOKEN_HERE',
    'Content-Type': 'application/json'
};

// Get upcoming shifts
fetch('/api/mobile/shifts/upcoming/', { headers })
    .then(response => response.json())
    .then(data => console.log(data));

// Create shift swap request
const swapData = {
    target_user: 'SAP002',
    requesting_shift: 100,
    target_shift: 101
};
fetch('/api/mobile/shift-swaps/', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify(swapData)
})
    .then(response => response.json())
    .then(data => console.log(data));
```

---

## Rate Limiting

No rate limiting is currently implemented. This may be added in future versions.

---

## Versioning

Current version: 1.0

The API is versioned through the URL path. Future versions will use `/api/v2/mobile/` etc.

---

## Support

For API support or to report issues:
- Email: support@staffrota.example.com
- GitHub: https://github.com/Dean-Sockalingum/staff-rota-system

---

## Changelog

### Version 1.0 (30 December 2025)
- Initial release
- 8 API endpoints: users, roles, care-homes, units, shift-types, shifts, leave-requests, shift-swaps
- Token authentication
- Filtering, search, and ordering support
- Pagination (20 items per page)
- Custom actions: /me, /my_shifts, /upcoming, /my_requests, approve, deny
