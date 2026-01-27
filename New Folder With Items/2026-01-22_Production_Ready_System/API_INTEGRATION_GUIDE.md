# Integration API Documentation

**Version:** v1  
**Base URL:** `/api/v1/integration/`  
**Authentication:** API Key or OAuth Bearer Token

## Overview

The Integration API provides programmatic access to the Staff Rota System for third-party integrations including HR systems, payroll processors, and analytics platforms.

## Authentication

### Option 1: API Key

Include your API key in the request header:

```http
X-API-Key: sk_your_api_key_here
```

### Option 2: OAuth 2.0 Bearer Token

**Step 1: Get Token**

```http
POST /api/v1/integration/auth/token
Content-Type: application/json

{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "grant_type": "client_credentials",
  "scope": ["staff:read", "shifts:read", "payroll:export"]
}
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "refresh_token": "refresh_token_here",
  "scope": ["staff:read", "shifts:read"]
}
```

**Step 2: Use Token**

```http
Authorization: Bearer eyJhbGc...
```

## Rate Limiting

Default rate limits per client:
- **60 requests per minute**
- **1,000 requests per hour**
- **10,000 requests per day**

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit-Minute: 60
X-RateLimit-Limit-Hour: 1000
X-RateLimit-Limit-Day: 10000
```

**429 Response when exceeded:**
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "window": "minute",
  "limit": 60,
  "current": 61,
  "reset_in_seconds": 45
}
```

## Available Scopes

| Scope | Description |
|-------|-------------|
| `staff:read` | Read staff member data |
| `staff:write` | Create/update staff members |
| `shifts:read` | Read shift data |
| `shifts:write` | Create/update shifts |
| `leave:read` | Read leave requests |
| `leave:approve` | Approve/reject leave |
| `payroll:export` | Export payroll data |
| `webhooks:manage` | Create/manage webhooks |

## Endpoints

### System Information

#### Get API Info
```http
GET /api/v1/integration/info
```

**Response:**
```json
{
  "api_version": "v1",
  "client": {
    "id": "client_123",
    "name": "HR System Integration",
    "type": "HR System",
    "organization": "Example Corp"
  },
  "rate_limits": {
    "per_minute": 60,
    "per_hour": 1000,
    "per_day": 10000
  },
  "statistics": {
    "total_requests": 15234,
    "successful_requests": 15102,
    "failed_requests": 132,
    "success_rate": 99.13
  }
}
```

---

### Staff Endpoints

#### List Staff Members

```http
GET /api/v1/integration/staff?page=1&per_page=50&unit_id=5&active=true
```

**Query Parameters:**
- `unit_id` (optional): Filter by unit
- `role` (optional): Filter by role name
- `active` (optional): `true` or `false`
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Results per page (max: 100, default: 50)

**Response:**
```json
{
  "data": [
    {
      "sap": "SCA1001",
      "first_name": "John",
      "last_name": "Smith",
      "full_name": "John Smith",
      "email": "john.smith@example.com",
      "phone_number": "+441234567890",
      "role": "Senior Care Assistant",
      "unit": {
        "id": 5,
        "name": "Orchard Grove Unit"
      },
      "team": "A",
      "shift_preference": "DAY",
      "is_active": true,
      "annual_leave_allowance": 28,
      "annual_leave_used": 12,
      "annual_leave_remaining": 16,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_count": 145,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### Get Staff Member

```http
GET /api/v1/integration/staff/{sap}
```

**Response:**
```json
{
  "data": {
    "sap": "SCA1001",
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "role": {
      "name": "Senior Care Assistant",
      "shift_duration_hours": 12.5,
      "shifts_per_week": 3
    },
    "unit": {
      "id": 5,
      "name": "Orchard Grove Unit",
      "care_home": "Riverside Care Home"
    },
    "annual_leave": {
      "allowance": 28,
      "used": 12,
      "remaining": 16,
      "year_start": "2025-01-01"
    }
  }
}
```

---

### Shift Endpoints

#### List Shifts

```http
GET /api/v1/integration/shifts?start_date=2025-01-01&end_date=2025-01-31&unit_id=5
```

**Query Parameters:**
- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD
- `unit_id` (optional): Filter by unit
- `user_sap` (optional): Filter by staff member
- `status` (optional): PUBLISHED, CONFIRMED, COMPLETED, CANCELLED
- `page` (optional): Page number
- `per_page` (optional): Results per page (max: 100)

**Response:**
```json
{
  "data": [
    {
      "id": 12345,
      "date": "2025-01-15",
      "start_time": "07:30:00",
      "end_time": "20:00:00",
      "duration_hours": 12.5,
      "status": "COMPLETED",
      "is_overtime": false,
      "is_agency": false,
      "staff": {
        "sap": "SCA1001",
        "full_name": "John Smith"
      },
      "unit": {
        "id": 5,
        "name": "Orchard Grove Unit",
        "care_home": "Riverside Care Home"
      },
      "notes": "",
      "created_at": "2024-12-01T09:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_count": 450
  }
}
```

---

### Leave Request Endpoints

#### List Leave Requests

```http
GET /api/v1/integration/leave-requests?user_sap=SCA1001&status=APPROVED
```

**Query Parameters:**
- `user_sap` (optional): Filter by staff member
- `status` (optional): PENDING, APPROVED, REJECTED
- `start_date` (optional): Filter from date
- `page` (optional): Page number
- `per_page` (optional): Results per page

**Response:**
```json
{
  "data": [
    {
      "id": 789,
      "user": {
        "sap": "SCA1001",
        "full_name": "John Smith"
      },
      "leave_type": "ANNUAL",
      "start_date": "2025-02-10",
      "end_date": "2025-02-14",
      "days_requested": 5,
      "status": "APPROVED",
      "reason": "Family holiday",
      "approved_by": {
        "sap": "ADMIN001",
        "full_name": "Jane Manager"
      },
      "approved_at": "2025-01-20T14:30:00Z",
      "created_at": "2025-01-18T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total_count": 23
  }
}
```

---

### Payroll Endpoints

#### Export Payroll Data

```http
POST /api/v1/integration/payroll/export
Content-Type: application/json

{
  "start_date": "2025-01-01",
  "end_date": "2025-01-31",
  "format": "json",
  "unit_id": 5
}
```

**Request Body:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `format` (optional): `json` or `csv` (default: json)
- `unit_id` (optional): Filter by unit

**JSON Response:**
```json
{
  "period": {
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "data": [
    {
      "user__sap": "SCA1001",
      "user__first_name": "John",
      "user__last_name": "Smith",
      "total_hours": 150.0,
      "regular_hours": 137.5,
      "overtime_hours": 12.5,
      "shift_count": 12
    }
  ],
  "summary": {
    "total_staff": 45,
    "total_hours": 5625.0,
    "total_overtime": 312.5
  }
}
```

**CSV Response:**
```csv
SAP,First Name,Last Name,Total Hours,Regular Hours,Overtime Hours,Shift Count
SCA1001,John,Smith,150.0,137.5,12.5,12
```

---

### Webhook Endpoints

#### Create Webhook

```http
POST /api/v1/integration/webhooks
Content-Type: application/json

{
  "url": "https://your-system.com/webhook",
  "event_types": ["shift.created", "shift.updated", "leave.approved"],
  "max_retries": 3,
  "retry_delay_seconds": 60
}
```

**Request Body:**
- `url` (required): Webhook endpoint URL
- `event_types` (required): Array of event types to subscribe to
- `max_retries` (optional): Max retry attempts (default: 3)
- `retry_delay_seconds` (optional): Delay between retries (default: 60)

**Response:**
```json
{
  "data": {
    "id": 123,
    "url": "https://your-system.com/webhook",
    "event_types": ["shift.created", "shift.updated"],
    "secret": "whsec_abc123...",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z"
  }
}
```

**Note:** The `secret` is only shown once upon creation. Use it to verify webhook signatures.

#### Webhook Event Types

| Event | Trigger |
|-------|---------|
| `shift.created` | New shift created |
| `shift.updated` | Shift modified |
| `shift.deleted` | Shift deleted |
| `leave.requested` | Leave request submitted |
| `leave.approved` | Leave request approved |
| `leave.rejected` | Leave request rejected |
| `staff.created` | New staff member added |
| `staff.updated` | Staff member updated |
| `swap.requested` | Shift swap requested |
| `swap.approved` | Shift swap approved |
| `all` | Subscribe to all events |

#### Webhook Payload Example

```json
{
  "event_id": "evt_abc123",
  "event_type": "shift.created",
  "timestamp": "2025-01-15T14:30:00Z",
  "data": {
    "id": 12345,
    "date": "2025-01-20",
    "start_time": "07:30:00",
    "end_time": "20:00:00",
    "staff": {
      "sap": "SCA1001",
      "full_name": "John Smith"
    },
    "unit": {
      "id": 5,
      "name": "Orchard Grove Unit"
    }
  }
}
```

**Signature Verification:**

Webhooks include a signature header for verification:

```http
X-Webhook-Signature: sha256=abc123...
```

To verify:
```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Status | Code | Description |
|--------|------|-------------|
| 400 | `INVALID_REQUEST` | Malformed request |
| 401 | `AUTH_REQUIRED` | Authentication required |
| 401 | `INVALID_API_KEY` | Invalid API key |
| 401 | `TOKEN_EXPIRED` | Access token expired |
| 403 | `INSUFFICIENT_SCOPE` | Missing required permissions |
| 403 | `IP_NOT_ALLOWED` | IP not whitelisted |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `SERVER_ERROR` | Internal server error |

---

## Best Practices

1. **Use pagination** - Always paginate large result sets
2. **Cache responses** - Implement client-side caching
3. **Handle rate limits** - Implement exponential backoff
4. **Verify webhooks** - Always verify webhook signatures
5. **Use HTTPS** - Never send credentials over HTTP
6. **Store secrets securely** - Never hardcode API keys
7. **Monitor usage** - Check `/info` endpoint for statistics

---

## Support

For API support or to request a new client:
- Email: api-support@example.com
- Documentation: https://docs.staffrota.com/api
- Status: https://status.staffrota.com

---

**Last Updated:** 30 December 2025  
**Version:** 1.0.0
