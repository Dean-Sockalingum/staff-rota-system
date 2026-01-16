# Task 3: Intelligent Shift Swap Auto-Approval - API Documentation

**Feature**: Auto-Approval System Replicating 73% Leave Auto-Approval Success  
**Roadmap**: Phase 1, Task 3 of 17  
**Status**: ✅ Implemented (commit 64d5acf)  
**Expected Impact**: 65% reduction in manager review time (20 min → 7 min/day)

---

## Overview

Transforms shift swap management through intelligent automation:
1. **5-Rule Validation** - Same role, qualifications, WDT, coverage, conflicts
2. **Instant Auto-Approval** - 60% of swaps approved in <1 second
3. **Instant Auto-Denial** - Invalid swaps denied with clear reasons
4. **Manual Review** - Edge cases escalated to manager with context
5. **Fair & Transparent** - Staff get immediate feedback, not 24hr wait

---

## Validation Rules (5 Checks)

### 1. Role Match (CRITICAL - Auto-Deny if Fails)
**Rule**: Both shifts must be the same role and grade  
**Example Pass**: SCW ↔ SCW  
**Example Fail**: SCW ↔ RN (skills mismatch)

**Auto-Denial Reason**:
```
"Role mismatch: SCW cannot swap with RN - skills mismatch"
```

---

### 2. Qualification Match (SCORING - Manual Review if <80%)
**Rule**: Both staff must be qualified for each other's units  
**Checks**:
- Unit access permissions
- Historical work at that location
- Training certifications

**Scoring** (0-100):
- User A qualified for User B's unit: +50 points
- User B qualified for User A's unit: +50 points
- **Threshold**: Must score ≥80 to auto-approve

**Manual Review Reason** (score 70):
```
"Qualification mismatch (score: 70/100) - requires manager review"
```

---

### 3. WDT Compliance (CRITICAL - Auto-Deny if Fails)
**Rule**: Neither staff can exceed 48hr weekly average (Working Time Directive)  
**Calculation**:
- Rolling 4-week period
- Total hours / 4 weeks ≤ 48hr/week

**Auto-Denial Reason**:
```
"WDT violation for Alice Smith: Swap would push to 52.3hr weekly average (limit: 48hr) - denied"
```

---

### 4. Coverage Maintained (CRITICAL - Auto-Deny if Fails)
**Rule**: Shift must still meet minimum staffing after swap  
**Checks**:
- Current staff count on each date
- Minimum staffing requirement for unit
- Projected staff count after swap

**Auto-Denial Reason**:
```
"Coverage risk on 2025-12-28: Would drop to 16 staff (minimum: 17) - denied"
```

---

### 5. No Conflicts (WARNING - Manual Review if Fails)
**Rule**: Neither staff has overlapping shifts or approved leave  
**Checks**:
- Existing shift assignments on swap dates
- Time overlap detection
- Approved leave requests

**Manual Review Reason**:
```
"Conflict for John Smith: Already assigned to 07:00-19:00 shift at Victoria Gardens"
```

---

## API Endpoints

### 1. Create Swap Request (with Auto-Validation)

**Endpoint**: `POST /api/shift-swaps/create/`  
**Purpose**: Submit shift swap request with instant validation  
**Authentication**: Required (staff or manager)

**Request**:
```json
{
  "requesting_user_id": 123,
  "target_user_id": 456,
  "requesting_shift_id": 789,
  "target_shift_id": 101,
  "reason": "Family commitment - need to swap weekend"
}
```

**Response (AUTO_APPROVED)**:
```json
{
  "swap_request_id": 999,
  "status": "AUTO_APPROVED",
  "automated_decision": true,
  "denial_reason": null,
  "message": "Swap auto-approved by system - shifts have been swapped",
  "validation_results": {
    "role_match": {
      "pass": true,
      "message": "Role match: Both shifts are Senior Carer"
    },
    "qualification_match": {
      "pass": true,
      "score": 100,
      "message": "Both staff qualified for swap locations (score: 100/100)"
    },
    "wdt_compliance": {
      "pass": true,
      "message": "WDT compliant: Both staff within 48hr weekly average"
    },
    "coverage_maintained": {
      "pass": true,
      "message": "Coverage maintained: Both dates meet minimum staffing"
    },
    "no_conflicts": {
      "pass": true,
      "message": "No conflicts: Neither staff has overlapping commitments"
    }
  },
  "created_at": "2025-12-28T10:00:00Z"
}
```

**Response (DENIED)**:
```json
{
  "swap_request_id": 999,
  "status": "DENIED",
  "automated_decision": true,
  "denial_reason": "Role mismatch: SCW cannot swap with RN - skills mismatch",
  "message": "Swap request denied - see denial reason",
  "validation_results": {
    "role_match": {
      "pass": false,
      "message": "Role mismatch: SCW cannot swap with RN - skills mismatch"
    },
    "qualification_match": {
      "pass": true,
      "score": 100,
      "message": "Both staff qualified for swap locations (score: 100/100)"
    },
    "wdt_compliance": {
      "pass": true,
      "message": "WDT compliant: Both staff within 48hr weekly average"
    },
    "coverage_maintained": {
      "pass": true,
      "message": "Coverage maintained: Both dates meet minimum staffing"
    },
    "no_conflicts": {
      "pass": true,
      "message": "No conflicts: Neither staff has overlapping commitments"
    }
  },
  "created_at": "2025-12-28T10:00:00Z"
}
```

**Response (MANUAL_REVIEW)**:
```json
{
  "swap_request_id": 999,
  "status": "MANUAL_REVIEW",
  "automated_decision": false,
  "denial_reason": null,
  "message": "Swap requires manager review - awaiting approval",
  "validation_results": {
    "role_match": {
      "pass": true,
      "message": "Role match: Both shifts are Senior Carer"
    },
    "qualification_match": {
      "pass": false,
      "score": 70,
      "message": "Qualification mismatch (score: 70/100) - requires manager review"
    },
    "wdt_compliance": {
      "pass": true,
      "message": "WDT compliant: Both staff within 48hr weekly average"
    },
    "coverage_maintained": {
      "pass": true,
      "message": "Coverage maintained: Both dates meet minimum staffing"
    },
    "no_conflicts": {
      "pass": true,
      "message": "No conflicts: Neither staff has overlapping commitments"
    }
  },
  "created_at": "2025-12-28T10:00:00Z"
}
```

**Usage Example** (curl):
```bash
curl -X POST http://localhost:8000/api/shift-swaps/create/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "requesting_user_id": 123,
    "target_user_id": 456,
    "requesting_shift_id": 789,
    "target_shift_id": 101,
    "reason": "Family commitment"
  }'
```

---

### 2. Get Swap Status

**Endpoint**: `GET /api/shift-swaps/{swap_request_id}/status/`  
**Purpose**: Get detailed status and validation results  
**Authentication**: Required (staff or manager)

**Response**:
```json
{
  "swap_request_id": 999,
  "status": "AUTO_APPROVED",
  "automated_decision": true,
  "requesting_user": {
    "id": 123,
    "name": "John Smith",
    "shift": {
      "id": 789,
      "date": "2025-12-28",
      "time": "07:00-19:00",
      "unit": "Orchard Grove",
      "role": "Senior Carer"
    }
  },
  "target_user": {
    "id": 456,
    "name": "Jane Doe",
    "shift": {
      "id": 101,
      "date": "2025-12-29",
      "time": "19:00-07:00",
      "unit": "Victoria Gardens",
      "role": "Senior Carer"
    }
  },
  "reason": "Family commitment",
  "created_at": "2025-12-28T10:00:00Z",
  "approval_date": "2025-12-28T10:00:05Z",
  "approval_notes": "Auto-approved by intelligent validation system",
  "approved_by": "System Auto-Approval",
  "qualification_score": 100.0,
  "wdt_compliant": true,
  "role_mismatch": false
}
```

**Usage Example** (curl):
```bash
curl -X GET http://localhost:8000/api/shift-swaps/999/status/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 3. List My Swaps

**Endpoint**: `GET /api/shift-swaps/my-swaps/`  
**Purpose**: List all swap requests for authenticated user  
**Authentication**: Required (staff or manager)

**Query Parameters**:
- `user_id` (required): User ID
- `status` (optional): Filter by status (AUTO_APPROVED, DENIED, etc.)
- `limit` (optional): Max results (default 20)

**Response**:
```json
{
  "swaps": [
    {
      "swap_request_id": 999,
      "status": "AUTO_APPROVED",
      "type": "REQUESTING",
      "partner": "Jane Doe",
      "my_shift": "28 Dec 07:00-19:00 at Orchard Grove",
      "their_shift": "29 Dec 19:00-07:00 at Victoria Gardens",
      "created_at": "2025-12-28T10:00:00Z",
      "automated": true,
      "denial_reason": null
    },
    {
      "swap_request_id": 998,
      "status": "DENIED",
      "type": "REQUESTING",
      "partner": "Bob Wilson",
      "my_shift": "30 Dec 07:00-19:00 at Orchard Grove",
      "their_shift": "31 Dec 19:00-07:00 at Elmwood",
      "created_at": "2025-12-27T14:00:00Z",
      "automated": true,
      "denial_reason": "WDT violation for Bob Wilson: Swap would push to 52.3hr weekly average (limit: 48hr) - denied"
    }
  ],
  "total": 2
}
```

**Usage Example** (curl):
```bash
# Get all swaps for user
curl -X GET "http://localhost:8000/api/shift-swaps/my-swaps/?user_id=123" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Filter by status
curl -X GET "http://localhost:8000/api/shift-swaps/my-swaps/?user_id=123&status=AUTO_APPROVED&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Manual Approve Swap

**Endpoint**: `POST /api/shift-swaps/{swap_request_id}/manual-approve/`  
**Purpose**: Manager manually approves swap (override validation)  
**Authentication**: Required (manager only)

**Request**:
```json
{
  "approved_by_user_id": 789,
  "notes": "Approved despite minor qualification gap - staff has covered this unit before"
}
```

**Response**:
```json
{
  "status": "APPROVED",
  "message": "Swap manually approved",
  "approved_by": "Sarah Johnson",
  "approval_date": "2025-12-28T14:30:00Z",
  "notes": "Approved despite minor qualification gap - staff has covered this unit before"
}
```

**Usage Example** (curl):
```bash
curl -X POST http://localhost:8000/api/shift-swaps/999/manual-approve/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "approved_by_user_id": 789,
    "notes": "Approved - operational need"
  }'
```

---

### 5. Deny Swap

**Endpoint**: `POST /api/shift-swaps/{swap_request_id}/deny/`  
**Purpose**: Manager denies swap request  
**Authentication**: Required (manager only)

**Request**:
```json
{
  "denied_by_user_id": 789,
  "reason": "Operational requirements - cannot approve at this time"
}
```

**Response**:
```json
{
  "status": "DENIED",
  "message": "Swap request denied",
  "denied_by": "Sarah Johnson",
  "denial_reason": "Operational requirements - cannot approve at this time"
}
```

**Usage Example** (curl):
```bash
curl -X POST http://localhost:8000/api/shift-swaps/999/deny/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "denied_by_user_id": 789,
    "reason": "Operational requirements"
  }'
```

---

## Workflow Examples

### Scenario 1: Perfect Match - Auto-Approved

**10:00 - John submits swap request**
```bash
POST /api/shift-swaps/create/
{
  "requesting_user_id": 123,  # John Smith (SCW)
  "target_user_id": 456,      # Jane Doe (SCW)
  "requesting_shift_id": 789, # 28 Dec 07:00-19:00 at Orchard Grove
  "target_shift_id": 101,     # 29 Dec 19:00-07:00 at Orchard Grove
  "reason": "Family commitment"
}
```

**10:00:01 - System validates (5 checks)**
1. ✅ Role Match: Both SCW
2. ✅ Qualification: Both scored 100 (work at Orchard Grove)
3. ✅ WDT: John 42hr avg, Jane 38hr avg (both <48hr)
4. ✅ Coverage: 28 Dec has 18 staff (min 17), 29 Dec has 19 staff (min 17)
5. ✅ No Conflicts: Neither has overlapping shifts/leave

**10:00:02 - AUTO_APPROVED**
- Swap executed automatically
- Shifts reassigned: John → 29 Dec, Jane → 28 Dec
- Both users receive instant email: "✅ Shift Swap Auto-Approved"

**Total Time**: **2 seconds** (vs 24hr manual approval)

---

### Scenario 2: WDT Violation - Auto-Denied

**14:00 - Alice submits swap request**
```bash
POST /api/shift-swaps/create/
{
  "requesting_user_id": 234,  # Alice Brown (SCW)
  "target_user_id": 567,      # Bob Wilson (SCW)
  "requesting_shift_id": 890, # 30 Dec 07:00-19:00
  "target_shift_id": 111,     # 31 Dec 07:00-19:00
  "reason": "Want New Year's Eve off"
}
```

**14:00:01 - System validates**
1. ✅ Role Match: Both SCW
2. ✅ Qualification: Both scored 100
3. ❌ **WDT: Bob has 47hr avg, swap would push to 52.3hr** (VIOLATION)
4. ✅ Coverage: Both dates OK
5. ✅ No Conflicts: None detected

**14:00:02 - DENIED (Critical Failure)**
- Status: DENIED
- Reason: "WDT violation for Bob Wilson: Swap would push to 52.3hr weekly average (limit: 48hr) - denied"
- Alice receives instant email with clear explanation

**Total Time**: **2 seconds** (instant feedback, not 24hr wait)

---

### Scenario 3: Qualification Gap - Manual Review

**16:00 - Chris submits swap request**
```bash
POST /api/shift-swaps/create/
{
  "requesting_user_id": 345,  # Chris Davis (SCW)
  "target_user_id": 678,      # Diana Evans (SCW)
  "requesting_shift_id": 222, # 05 Jan 07:00-19:00 at Orchard Grove
  "target_shift_id": 333,     # 06 Jan 19:00-07:00 at Elmwood
  "reason": "Childcare issues"
}
```

**16:00:01 - System validates**
1. ✅ Role Match: Both SCW
2. ⚠️ **Qualification: Chris scored 50 (never worked at Elmwood), Diana scored 100** → Total 75/100 (below 80 threshold)
3. ✅ WDT: Both compliant
4. ✅ Coverage: Both dates OK
5. ✅ No Conflicts: None detected

**16:00:02 - MANUAL_REVIEW**
- Status: MANUAL_REVIEW
- Manager receives notification with context
- Chris receives email: "⏳ Shift Swap Awaiting Manager Review"

**16:30 - Manager reviews**
- Manager logs in, sees: "Chris has never worked at Elmwood - verify qualification"
- Manager checks: Chris completed orientation at Elmwood last month
- Manager approves with note: "Completed Elmwood orientation 3 weeks ago"

**16:31 - APPROVED**
- Swap executed
- Both users receive email: "✅ Shift Swap Approved by Manager"

**Total Time**: **31 minutes** (vs 24hr+ manual review)

---

## Error Handling

### Common Errors

**400 Bad Request - Missing Fields**:
```json
{
  "error": "Missing required fields: requesting_user_id, target_user_id, requesting_shift_id, target_shift_id"
}
```

**404 Not Found - Invalid User**:
```json
{
  "error": "Invalid user ID"
}
```

**404 Not Found - Invalid Shift**:
```json
{
  "error": "Invalid shift ID"
}
```

**400 Bad Request - Cannot Approve**:
```json
{
  "error": "Cannot manually approve swap with status: AUTO_APPROVED"
}
```

**400 Bad Request - Cannot Deny Approved**:
```json
{
  "error": "Cannot deny approved swap"
}
```

---

## Testing Checklist

- [ ] **Auto-Approve**: Create perfect match swap → verify instant approval
- [ ] **Auto-Deny (Role)**: SCW swaps with RN → verify instant denial
- [ ] **Auto-Deny (WDT)**: Create swap violating 48hr limit → verify denial
- [ ] **Auto-Deny (Coverage)**: Create swap dropping below min staff → verify denial
- [ ] **Manual Review**: Create swap with 70% qualification score → verify MANUAL_REVIEW
- [ ] **Manual Approve**: Manager approves manual review swap → verify execution
- [ ] **Manual Deny**: Manager denies swap → verify denial
- [ ] **List My Swaps**: Verify user sees all their swaps (requested + target)
- [ ] **Get Status**: Verify detailed validation results returned
- [ ] **Email Notifications**: Verify emails sent for all status changes

---

## Performance Metrics

**Expected Outcomes**:
- **Auto-Approval Rate**: 60% (14 of 24 daily swaps)
- **Auto-Denial Rate**: 15% (4 of 24 daily swaps)
- **Manual Review Rate**: 25% (6 of 24 daily swaps)
- **Manager Time**: 20 min/day → 7 min/day (65% reduction)
- **Staff Wait Time**: 24 hours → 2 seconds (99.998% reduction)
- **Staff Satisfaction**: ↑ (instant feedback, clear reasons)

**Monitoring Dashboards**:
- Track auto-approval rate by rule (which rules fail most?)
- Track manual review override rate (managers approve vs deny)
- Track average response time (should be <3 seconds)
- Track staff satisfaction surveys (before/after comparison)

---

## Database Schema

### ShiftSwapRequest Model (Extended)
```python
{
  'id': 999,
  'requesting_user': ForeignKey(User),
  'target_user': ForeignKey(User),
  'requesting_shift': ForeignKey(Shift),
  'target_shift': ForeignKey(Shift),
  'reason': TextField,
  'status': 'PENDING|AUTO_APPROVED|MANUAL_REVIEW|APPROVED|DENIED|CANCELLED',
  
  # Approval workflow
  'target_user_approved': Boolean,
  'management_approved': Boolean,
  'approved_by': ForeignKey(User, null=True),
  'approval_date': DateTime(null=True),
  'approval_notes': TextField(null=True),
  
  # Auto-approval fields (Task 3)
  'automated_decision': Boolean,
  'qualification_match_score': Decimal(0-100),
  'wdt_compliance_check': Boolean,
  'role_mismatch': Boolean,
  'denial_reason': TextField(null=True),
  
  'created_at': DateTime,
  'updated_at': DateTime
}
```

---

## Next Steps

1. **Testing**: Complete checklist above
2. **Monitoring**: Add analytics dashboard for auto-approval metrics
3. **Optimization**: Tune qualification threshold based on manual override data
4. **Phase 1 Completion**: Complete Tasks 1-3 end-to-end testing (Task 4)

---

**Status**: ✅ Ready for production testing  
**Commit**: 64d5acf  
**Files**: 1,180 lines across 2 new files  
**Documentation**: Complete  
**Next**: Task 4 - Phase 1 Testing & Documentation (consolidate all 3 features)
