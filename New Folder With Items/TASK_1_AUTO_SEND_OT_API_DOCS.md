# Task 1: Auto-Send OT Offers - API Documentation

**Feature**: Smart Staff Availability Matching System  
**Roadmap**: Phase 1, Task 1 of 17  
**Status**: ✅ Implemented (commit 88ccb7e)  
**Expected Impact**: 96% time reduction (15 minutes → 30 seconds)

---

## Overview

Automates overtime offer distribution by:
1. **Finding** top-ranked available staff using OvertimeRanker algorithm
2. **Sending** SMS/Email/App offers to top 3 candidates automatically
3. **Escalating** to agency after 30 minutes if no acceptance
4. **Tracking** all responses and batch status in real-time

---

## API Endpoints

### 1. Find OT Matches (Preview)

**Endpoint**: `POST /api/ot-matching/find-matches/`  
**Purpose**: Get ranked candidates WITHOUT sending offers (preview mode)  
**Authentication**: Required (manager or head of service)

**Request**:
```json
{
  "shift_id": 12345,
  "limit": 10
}
```

**Response**:
```json
{
  "shift": {
    "id": 12345,
    "date": "2025-12-28",
    "start_time": "07:00",
    "end_time": "19:00",
    "role": "Senior Carer",
    "home": "Orchard Grove"
  },
  "matches": [
    {
      "user_id": 789,
      "sap": "SAP123456",
      "name": "John Smith",
      "rank": 1,
      "score": 0.92,
      "ranking_factors": {
        "home_match": true,
        "role_qualified": true,
        "historical_acceptance": 0.85,
        "recency_score": 0.95,
        "overtime_preference": "HIGH"
      },
      "availability": "AVAILABLE",
      "contact": {
        "phone": "07700900123",
        "email": "john.smith@example.com"
      }
    },
    {
      "user_id": 234,
      "sap": "SAP654321",
      "name": "Jane Doe",
      "rank": 2,
      "score": 0.88,
      "ranking_factors": {
        "home_match": false,
        "role_qualified": true,
        "historical_acceptance": 0.90,
        "recency_score": 0.75,
        "overtime_preference": "MEDIUM"
      },
      "availability": "AVAILABLE",
      "contact": {
        "phone": "07700900456",
        "email": "jane.doe@example.com"
      }
    }
  ],
  "total_matches": 8
}
```

**Usage Example** (curl):
```bash
curl -X POST http://localhost:8000/api/ot-matching/find-matches/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "shift_id": 12345,
    "limit": 10
  }'
```

---

### 2. Send OT Offers (Auto-Send)

**Endpoint**: `POST /api/ot-matching/send-offers/`  
**Purpose**: Automatically send offers to top N ranked staff  
**Authentication**: Required (manager or head of service)

**Request**:
```json
{
  "shift_id": 12345,
  "max_offers": 3,
  "escalation_minutes": 30,
  "message": "Urgent: Senior Carer needed at Orchard Grove tomorrow"
}
```

**Response**:
```json
{
  "batch_id": "batch_abc123",
  "shift_id": 12345,
  "offers_sent": 3,
  "recipients": [
    {
      "user_id": 789,
      "name": "John Smith",
      "rank": 1,
      "channels": ["SMS", "EMAIL", "APP"],
      "offer_id": "offer_xyz001"
    },
    {
      "user_id": 234,
      "name": "Jane Doe",
      "rank": 2,
      "channels": ["SMS", "EMAIL"],
      "offer_id": "offer_xyz002"
    },
    {
      "user_id": 567,
      "name": "Bob Wilson",
      "rank": 3,
      "channels": ["SMS", "APP"],
      "offer_id": "offer_xyz003"
    }
  ],
  "escalation_at": "2025-12-28T14:30:00Z",
  "status": "PENDING"
}
```

**Usage Example** (curl):
```bash
curl -X POST http://localhost:8000/api/ot-matching/send-offers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "shift_id": 12345,
    "max_offers": 3,
    "escalation_minutes": 30,
    "message": "Urgent: Senior Carer needed tomorrow"
  }'
```

---

### 3. Get Batch Status

**Endpoint**: `GET /api/ot-matching/batch/{batch_id}/status/`  
**Purpose**: Track real-time status of offer batch  
**Authentication**: Required (manager or head of service)

**Response**:
```json
{
  "batch_id": "batch_abc123",
  "shift": {
    "id": 12345,
    "date": "2025-12-28",
    "role": "Senior Carer",
    "home": "Orchard Grove"
  },
  "status": "PENDING",
  "created_at": "2025-12-28T14:00:00Z",
  "escalation_at": "2025-12-28T14:30:00Z",
  "time_remaining": "18 minutes",
  "offers": [
    {
      "offer_id": "offer_xyz001",
      "user": "John Smith (SAP123456)",
      "rank": 1,
      "status": "PENDING",
      "sent_at": "2025-12-28T14:00:05Z",
      "channels": ["SMS", "EMAIL", "APP"]
    },
    {
      "offer_id": "offer_xyz002",
      "user": "Jane Doe (SAP654321)",
      "rank": 2,
      "status": "DECLINED",
      "sent_at": "2025-12-28T14:00:06Z",
      "responded_at": "2025-12-28T14:05:00Z",
      "channels": ["SMS", "EMAIL"]
    },
    {
      "offer_id": "offer_xyz003",
      "user": "Bob Wilson (SAP789012)",
      "rank": 3,
      "status": "PENDING",
      "sent_at": "2025-12-28T14:00:07Z",
      "channels": ["SMS", "APP"]
    }
  ],
  "summary": {
    "total_offers": 3,
    "pending": 2,
    "accepted": 0,
    "declined": 1
  }
}
```

**Usage Example** (curl):
```bash
curl -X GET http://localhost:8000/api/ot-matching/batch/batch_abc123/status/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Staff Response Webhook

**Endpoint**: `POST /api/ot-matching/offer/{offer_id}/respond/`  
**Purpose**: Staff accepts or declines OT offer (webhook from SMS/Email/App)  
**Authentication**: Token-based (embedded in offer link)

**Request**:
```json
{
  "response": "ACCEPT"
}
```
or
```json
{
  "response": "DECLINE"
}
```

**Response (ACCEPT)**:
```json
{
  "status": "SUCCESS",
  "message": "Offer accepted - shift assigned to John Smith",
  "shift": {
    "id": 12345,
    "date": "2025-12-28",
    "start_time": "07:00",
    "end_time": "19:00",
    "role": "Senior Carer",
    "home": "Orchard Grove"
  },
  "assigned_to": "John Smith (SAP123456)",
  "batch_status": "FILLED"
}
```

**Response (DECLINE)**:
```json
{
  "status": "SUCCESS",
  "message": "Offer declined - checking other candidates",
  "batch_status": "PENDING",
  "remaining_offers": 2
}
```

**Usage Example** (curl):
```bash
# Accept offer
curl -X POST http://localhost:8000/api/ot-matching/offer/offer_xyz001/respond/ \
  -H "Content-Type: application/json" \
  -d '{"response": "ACCEPT"}'

# Decline offer
curl -X POST http://localhost:8000/api/ot-matching/offer/offer_xyz001/respond/ \
  -H "Content-Type: application/json" \
  -d '{"response": "DECLINE"}'
```

---

## Auto-Escalation System

### Cron Job: `check_ot_escalation`

**Schedule**: Every minute (via cron)  
**Command**: `python manage.py check_ot_escalation`  
**Purpose**: Monitor pending batches and escalate to agency on timeout

**Escalation Triggers**:
1. **Timeout**: 30 minutes elapsed with no acceptance
2. **All Declined**: All staff declined offers

**Escalation Actions**:
1. Creates `AgencyRequest` with shift details
2. Sets batch status to `ESCALATED`
3. Sends notification to manager
4. Emails configured agencies (if Task 2 complete)

**Crontab Entry**:
```cron
* * * * * cd /path/to/staff_rota && /usr/bin/python3 manage.py check_ot_escalation >> /var/log/ot_escalation.log 2>&1
```

**Manual Test**:
```bash
python manage.py check_ot_escalation
```

---

## Integration with Existing Systems

### OvertimeRanker Algorithm

The auto-send system uses the existing **OvertimeRanker** class (5-factor ranking):

1. **Home Match** (30% weight): Staff familiar with the home
2. **Role Qualification** (25% weight): Qualified for the specific role
3. **Historical Acceptance** (20% weight): Past OT acceptance rate
4. **Recency Score** (15% weight): Last time offered OT (fairness)
5. **Overtime Preference** (10% weight): HIGH/MEDIUM/LOW preference

**Algorithm**: `OvertimeRanker.rank_candidates(shift_id, limit=10)`

### Multi-Channel Notifications

**Channels Used**:
- **SMS**: Via Twilio integration (instantaneous)
- **Email**: Via SendGrid (HTML template with accept/decline buttons)
- **App**: Push notification via Firebase Cloud Messaging

**Template Variables**:
```python
{
    "staff_name": "John",
    "shift_date": "Saturday 28 December",
    "shift_time": "07:00 - 19:00",
    "role": "Senior Carer",
    "home": "Orchard Grove",
    "accept_url": "https://rota.example.com/api/ot-matching/offer/xyz001/respond/?response=ACCEPT",
    "decline_url": "https://rota.example.com/api/ot-matching/offer/xyz001/respond/?response=DECLINE"
}
```

---

## Workflow Example

### Scenario: Shift Coverage Needed

1. **Manager Action**: POST to `/api/ot-matching/send-offers/` with `shift_id=12345`

2. **System Response**:
   - Finds top 3 staff using OvertimeRanker
   - Creates `OvertimeOfferBatch` (batch_abc123)
   - Sends SMS/Email/App to John (rank 1), Jane (rank 2), Bob (rank 3)
   - Returns batch details with 30-min countdown

3. **Staff Action** (within 5 minutes):
   - Jane receives SMS: "OT available tomorrow 07:00-19:00 at Orchard Grove. Accept: [link]"
   - Jane clicks "Decline" link
   - System receives POST to `/api/ot-matching/offer/offer_xyz002/respond/` with `DECLINE`

4. **System Update**:
   - Marks Jane's offer as DECLINED
   - Batch still PENDING (John and Bob haven't responded)
   - Manager sees live update via GET `/api/ot-matching/batch/batch_abc123/status/`

5. **Staff Action** (15 minutes later):
   - John receives SMS and Email
   - John clicks "Accept" link in email
   - System receives POST to `/api/ot-matching/offer/offer_xyz001/respond/` with `ACCEPT`

6. **System Auto-Assignment**:
   - Assigns shift to John Smith
   - Updates Shift.user = John
   - Sets batch status to FILLED
   - Cancels remaining offers (Bob's offer withdrawn)
   - Sends confirmation SMS/Email to John
   - Notifies manager: "Shift filled by John Smith"

7. **Alternative: No Response**:
   - 30 minutes elapse with no acceptance
   - Cron job `check_ot_escalation` runs
   - Detects timeout on batch_abc123
   - Creates `AgencyRequest` automatically
   - Sets batch status to ESCALATED
   - Emails manager: "No staff available - escalated to agency"

---

## Error Handling

### Common Errors

**400 Bad Request**:
```json
{
  "error": "Invalid shift_id",
  "details": "Shift 99999 does not exist"
}
```

**404 Not Found**:
```json
{
  "error": "Batch not found",
  "batch_id": "batch_invalid"
}
```

**409 Conflict**:
```json
{
  "error": "Shift already filled",
  "shift_id": 12345,
  "assigned_to": "Jane Doe"
}
```

**500 Internal Server Error**:
```json
{
  "error": "SMS delivery failed",
  "details": "Twilio API timeout",
  "retry": true
}
```

---

## Testing Checklist

- [ ] **Find Matches**: GET ranked candidates without sending
- [ ] **Send Offers**: Create batch and send to top 3 staff
- [ ] **Multi-Channel**: Verify SMS + Email + App all send
- [ ] **Accept Response**: Staff clicks accept → shift assigned
- [ ] **Decline Response**: Staff clicks decline → batch stays pending
- [ ] **Timeout Escalation**: Wait 30 min → agency request created
- [ ] **All Declined Escalation**: 3 declines → immediate agency request
- [ ] **Batch Status**: Real-time tracking shows correct state
- [ ] **Duplicate Prevention**: Can't send offers for already-filled shift
- [ ] **Cron Job**: `check_ot_escalation` runs without errors

---

## Performance Metrics

**Expected Outcomes**:
- **Manager Time**: 15 minutes → 30 seconds (96% reduction)
- **Missed Coverage**: 100% → 0% (auto-escalation guarantee)
- **Staff Satisfaction**: ↑ (instant OT opportunities)
- **Fair Distribution**: AI ranking ensures equity

**Monitoring**:
- Track batch response times (avg time to acceptance)
- Track escalation rate (% batches escalated to agency)
- Track staff acceptance rates by ranking factor
- Track manager usage (API calls per day)

---

## Next Steps

1. **Testing**: Complete checklist above
2. **Monitoring**: Add Sentry alerts for API errors
3. **Optimization**: Tune OvertimeRanker weights based on acceptance data
4. **Phase 1 Completion**: Move to Task 2 (Enhanced Agency Coordination)

---

**Status**: ✅ Ready for production testing  
**Commit**: 88ccb7e  
**Files**: 735 lines across 3 new files  
**Documentation**: Complete  
**Next**: Task 2 - Multi-Agency Blast Emails
