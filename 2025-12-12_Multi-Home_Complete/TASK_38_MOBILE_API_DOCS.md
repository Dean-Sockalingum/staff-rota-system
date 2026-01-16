# Task 38: Mobile App API Documentation

**Date:** December 30, 2025  
**Status:** ✅ COMPLETE  
**Components:** REST API with 9 resource endpoints

---

## Overview

The Mobile App API provides RESTful endpoints for mobile applications to access the Staff Rota System. All endpoints require authentication and return JSON responses.

**Base URL:** `http://127.0.0.1:8000/api/mobile/`

**Authentication:** Token-based authentication (Bearer token in Authorization header)

---

## Authentication

### Token Authentication

All API requests must include an authentication token in the header:

```http
Authorization: Token <your-auth-token>
```

### Obtaining a Token

Tokens are generated automatically when users are created. To get your token:

**Option 1: Django Admin**
1. Navigate to `/admin/authtoken/token/`
2. Find your user
3. Copy the token key

**Option 2: Django Shell**
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.get(username='your_username')
token, created = Token.objects.get_or_create(user=user)
print(token.key)
```

**Option 3: API Endpoint** (Future enhancement)
```http
POST /api/mobile/auth/login/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

---

## API Endpoints

### 1. Care Homes

**List Care Homes**
```http
GET /api/mobile/care-homes/
```

**Get Care Home Details**
```http
GET /api/mobile/care-homes/{id}/
```

**Response:**
```json
{
    "id": 1,
    "name": "orchard_grove",
    "display_name": "Orchard Grove",
    "address": "123 Main St",
    "phone_number": "0141 123 4567",
    "capacity": 50,
    "is_active": true
}
```

---

### 2. User Profiles

**List Profiles** (Managers only - filtered by care home)
```http
GET /api/mobile/profiles/
```

**Get My Profile**
```http
GET /api/mobile/profiles/me/
```

**Get Profile Details**
```http
GET /api/mobile/profiles/{id}/
```

**Search Profiles**
```http
GET /api/mobile/profiles/?search=john
```

**Response:**
```json
{
    "id": 1,
    "user": {
        "id": 5,
        "username": "000123",
        "email": "john.smith@example.com",
        "first_name": "John",
        "last_name": "Smith",
        "full_name": "John Smith",
        "role": "Care Worker"
    },
    "role": "Care Worker",
    "employee_number": "000123",
    "phone_number": "07700 900123",
    "care_home": 1,
    "care_home_name": "Orchard Grove",
    "hourly_rate": "12.50",
    "contract_hours": 37.5,
    "is_active": true,
    "skills_list": ["Medication Admin", "First Aid"],
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-12-30T14:20:00Z"
}
```

---

### 3. Shifts

**List Shifts** (Filtered by user's care home)
```http
GET /api/mobile/shifts/
```

**Get My Shifts**
```http
GET /api/mobile/shifts/my_shifts/
```

**Get Upcoming Shifts** (Next 7 days)
```http
GET /api/mobile/shifts/upcoming/
```

**Filter Shifts**
```http
GET /api/mobile/shifts/?start_date=2025-12-01&end_date=2025-12-31&status=Scheduled
```

**Get Shift Details**
```http
GET /api/mobile/shifts/{id}/
```

**Create Shift** (Managers only)
```http
POST /api/mobile/shifts/
Content-Type: application/json

{
    "care_home": 1,
    "template": 3,
    "staff": 5,
    "date": "2025-12-31",
    "start_time": "07:00:00",
    "end_time": "15:00:00",
    "role": "Care Worker",
    "status": "Scheduled",
    "notes": "Bank holiday shift"
}
```

**Update Shift** (Managers only)
```http
PUT /api/mobile/shifts/{id}/
PATCH /api/mobile/shifts/{id}/
```

**Delete Shift** (Managers only)
```http
DELETE /api/mobile/shifts/{id}/
```

**Response:**
```json
{
    "id": 123,
    "care_home": 1,
    "care_home_name": "Orchard Grove",
    "template": 3,
    "template_name": "Early (7am-3pm)",
    "staff": 5,
    "staff_name": "John Smith",
    "date": "2025-12-31",
    "start_time": "07:00:00",
    "end_time": "15:00:00",
    "role": "Care Worker",
    "status": "Scheduled",
    "is_overtime": false,
    "is_agency": false,
    "notes": "Bank holiday shift",
    "duration_hours": 8.0,
    "created_at": "2025-12-25T10:00:00Z",
    "updated_at": "2025-12-25T10:00:00Z"
}
```

---

### 4. Shift Templates

**List Shift Templates**
```http
GET /api/mobile/shift-templates/
```

**Get Template Details**
```http
GET /api/mobile/shift-templates/{id}/
```

**Response:**
```json
{
    "id": 3,
    "name": "Early (7am-3pm)",
    "care_home": 1,
    "care_home_name": "Orchard Grove",
    "start_time": "07:00:00",
    "end_time": "15:00:00",
    "role": "Care Worker",
    "is_active": true
}
```

---

### 5. Staff Availability

**List Availability**
```http
GET /api/mobile/availability/
```

**Get My Availability**
```http
GET /api/mobile/availability/my_availability/
```

**Filter by Date Range**
```http
GET /api/mobile/availability/?start_date=2025-12-01&end_date=2025-12-31
```

**Submit Availability**
```http
POST /api/mobile/availability/
Content-Type: application/json

{
    "care_home": 1,
    "date": "2025-12-31",
    "is_available": true,
    "preferred_shift_type": "Early",
    "notes": "Prefer 7am start"
}
```

**Update Availability**
```http
PUT /api/mobile/availability/{id}/
PATCH /api/mobile/availability/{id}/
```

**Delete Availability**
```http
DELETE /api/mobile/availability/{id}/
```

**Response:**
```json
{
    "id": 45,
    "staff": 5,
    "staff_name": "John Smith",
    "care_home": 1,
    "care_home_name": "Orchard Grove",
    "date": "2025-12-31",
    "is_available": true,
    "preferred_shift_type": "Early",
    "notes": "Prefer 7am start",
    "created_at": "2025-12-20T10:00:00Z",
    "updated_at": "2025-12-20T10:00:00Z"
}
```

---

### 6. Leave Requests

**List Leave Requests**
```http
GET /api/mobile/leave-requests/
```

**Get My Requests**
```http
GET /api/mobile/leave-requests/my_requests/
```

**Filter by Status**
```http
GET /api/mobile/leave-requests/?status=Pending
```

**Get Request Details**
```http
GET /api/mobile/leave-requests/{id}/
```

**Submit Leave Request**
```http
POST /api/mobile/leave-requests/
Content-Type: application/json

{
    "start_date": "2025-12-24",
    "end_date": "2025-12-26",
    "leave_type": "Annual Leave",
    "reason": "Christmas holiday"
}
```

**Update Leave Request**
```http
PUT /api/mobile/leave-requests/{id}/
PATCH /api/mobile/leave-requests/{id}/
```

**Approve Leave Request** (Managers only)
```http
POST /api/mobile/leave-requests/{id}/approve/
Content-Type: application/json

{
    "notes": "Approved - enjoy your holiday"
}
```

**Reject Leave Request** (Managers only)
```http
POST /api/mobile/leave-requests/{id}/reject/
Content-Type: application/json

{
    "notes": "Already 3 staff on leave this week"
}
```

**Response:**
```json
{
    "id": 78,
    "staff": 5,
    "staff_name": "John Smith",
    "care_home": 1,
    "care_home_name": "Orchard Grove",
    "start_date": "2025-12-24",
    "end_date": "2025-12-26",
    "leave_type": "Annual Leave",
    "reason": "Christmas holiday",
    "status": "Approved",
    "approved_by": 2,
    "approved_by_name": "Jane Manager",
    "approval_date": "2025-12-15T14:30:00Z",
    "notes": "Approved - enjoy your holiday",
    "total_days": 3,
    "created_at": "2025-12-10T09:00:00Z",
    "updated_at": "2025-12-15T14:30:00Z"
}
```

---

### 7. Annual Leave Entitlements

**List Entitlements**
```http
GET /api/mobile/leave-entitlements/
```

**Get My Entitlement**
```http
GET /api/mobile/leave-entitlements/my_entitlement/
```

**Get Entitlement for Specific Year**
```http
GET /api/mobile/leave-entitlements/my_entitlement/?year=2025
```

**Response:**
```json
{
    "id": 12,
    "staff": 5,
    "staff_name": "John Smith",
    "care_home": 1,
    "care_home_name": "Orchard Grove",
    "year": 2025,
    "total_days": 28,
    "days_used": 14.5,
    "days_remaining": 15.5,
    "carried_over": 2,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-12-30T10:00:00Z"
}
```

---

### 8. Shift Swap Requests

**List Swap Requests**
```http
GET /api/mobile/shift-swaps/
```

**Filter by Status**
```http
GET /api/mobile/shift-swaps/?status=Pending
```

**Get Swap Details**
```http
GET /api/mobile/shift-swaps/{id}/
```

**Create Swap Request**
```http
POST /api/mobile/shift-swaps/
Content-Type: application/json

{
    "shift": 123,
    "to_staff": 8,
    "reason": "Doctor appointment"
}
```

**Approve Swap** (Managers only)
```http
POST /api/mobile/shift-swaps/{id}/approve/
Content-Type: application/json

{
    "notes": "Approved - both staff are qualified"
}
```

**Reject Swap** (Managers only)
```http
POST /api/mobile/shift-swaps/{id}/reject/
Content-Type: application/json

{
    "notes": "Recipient not qualified for this role"
}
```

**Response:**
```json
{
    "id": 34,
    "shift": 123,
    "shift_details": {
        "date": "2025-12-31",
        "start_time": "07:00:00",
        "end_time": "15:00:00",
        "care_home_name": "Orchard Grove"
    },
    "from_staff": 5,
    "from_staff_name": "John Smith",
    "to_staff": 8,
    "to_staff_name": "Sarah Jones",
    "reason": "Doctor appointment",
    "status": "Approved",
    "manager_approved": true,
    "manager_notes": "Approved - both staff are qualified",
    "created_at": "2025-12-20T10:00:00Z",
    "updated_at": "2025-12-21T14:00:00Z"
}
```

---

### 9. Skills

**List Skills**
```http
GET /api/mobile/skills/
```

**Get Skill Details**
```http
GET /api/mobile/skills/{id}/
```

**Response:**
```json
{
    "id": 3,
    "name": "Medication Administration",
    "description": "Qualified to administer medications",
    "is_required": true,
    "created_at": "2025-01-01T00:00:00Z"
}
```

---

## Pagination

All list endpoints support pagination:

```http
GET /api/mobile/shifts/?page=2
```

**Paginated Response:**
```json
{
    "count": 145,
    "next": "http://127.0.0.1:8000/api/mobile/shifts/?page=3",
    "previous": "http://127.0.0.1:8000/api/mobile/shifts/?page=1",
    "results": [
        { ... },
        { ... }
    ]
}
```

Default page size: 20 items

---

## Filtering & Search

**Search** (where available):
```http
GET /api/mobile/profiles/?search=john
GET /api/mobile/shifts/?search=care+worker
```

**Ordering:**
```http
GET /api/mobile/shifts/?ordering=-date
GET /api/mobile/profiles/?ordering=user__last_name
```

**Date Filtering:**
```http
GET /api/mobile/shifts/?start_date=2025-12-01&end_date=2025-12-31
GET /api/mobile/availability/?date=2025-12-31
```

---

## Error Responses

**401 Unauthorized** - Missing or invalid token:
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden** - Insufficient permissions:
```json
{
    "error": "Only managers can approve leave requests"
}
```

**404 Not Found** - Resource not found:
```json
{
    "detail": "Not found."
}
```

**400 Bad Request** - Validation error:
```json
{
    "start_date": ["This field is required."],
    "end_date": ["End date must be after start date."]
}
```

---

## Testing the API

### Using cURL

**Get shifts:**
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     http://127.0.0.1:8000/api/mobile/shifts/my_shifts/
```

**Submit availability:**
```bash
curl -X POST \
     -H "Authorization: Token YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"date": "2025-12-31", "is_available": true}' \
     http://127.0.0.1:8000/api/mobile/availability/
```

### Using Browsable API

Navigate to endpoints in browser while logged in:
```
http://127.0.0.1:8000/api/mobile/shifts/
http://127.0.0.1:8000/api/mobile/profiles/me/
http://127.0.0.1:8000/api/mobile/leave-requests/
```

---

## Permission Levels

| Endpoint | Staff | Manager | Admin |
|----------|-------|---------|-------|
| List care homes | ✅ | ✅ | ✅ |
| Get own profile | ✅ | ✅ | ✅ |
| List all profiles | ❌ | ✅ | ✅ |
| Get own shifts | ✅ | ✅ | ✅ |
| Create/edit shifts | ❌ | ✅ | ✅ |
| Submit availability | ✅ | ✅ | ✅ |
| Submit leave request | ✅ | ✅ | ✅ |
| Approve leave | ❌ | ✅ | ✅ |
| Request shift swap | ✅ | ✅ | ✅ |
| Approve shift swap | ❌ | ✅ | ✅ |

---

## Future Enhancements

- [ ] Custom login endpoint (`/api/mobile/auth/login/`)
- [ ] Token refresh mechanism
- [ ] Push notification registration
- [ ] Real-time updates (WebSocket)
- [ ] File upload (profile photos, documents)
- [ ] Bulk operations
- [ ] Advanced filtering with Django Filter Backend
- [ ] API versioning (`/api/v1/mobile/`)
- [ ] Rate limiting
- [ ] API analytics and monitoring

---

## Technical Implementation

**Frameworks:**
- Django REST Framework 3.16.1
- Token Authentication
- ViewSet-based architecture
- Automatic URL routing

**Files Created:**
- `scheduling/serializers.py` - Model serializers (216 lines)
- `scheduling/views_mobile_api.py` - API viewsets (558 lines)
- `scheduling/api_urls.py` - URL routing (28 lines)

**Configuration:**
- Added `rest_framework.authtoken` to INSTALLED_APPS
- Updated REST_FRAMEWORK settings with TokenAuthentication
- Added `/api/mobile/` to main URLs
- Enabled DRF browsable API at `/api-auth/`

---

## Status

✅ **COMPLETE** - All 9 resource endpoints implemented and ready for mobile app integration
