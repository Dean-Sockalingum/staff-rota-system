# Pattern Overview - Leave & Absence Management

## New Functionality Added (Jan 27, 2026)

The Pattern Overview now supports recording absences and leave directly from the 3-week rota view.

### Features

When you click on any shift cell in the Pattern Overview, the modal now offers:

#### **Units (Existing)**
- All active units from the selected care home
- Color-coded for easy identification
- Example: [GREEN] PRIMROSE, [ORANGE] SNOWDROP

#### **Absences/Leave (NEW)**
1. **📅 Annual Leave**
   - Marks shift as uncovered
   - Updates staff record
   - Notifies management (MEDIUM priority)
   - Displays as **A/L** on rota with green background

2. **🤒 Sickness**
   - Marks shift as uncovered
   - Creates/updates SicknessAbsence record
   - **Triggers automated workflow**:
     - Attempts reallocation to available staff
     - Sends OT offers if reallocation fails
     - Escalates to agency if needed
   - Notifies management (HIGH priority)
   - Displays as **SICK** on rota with red background

3. **⚠️ Unauthorised Leave**
   - Marks shift as uncovered
   - Creates URGENT notification for management
   - Flags for potential disciplinary action
   - Displays as **UNAUTH** on rota with orange background

### Automated Workflows Triggered

#### Sickness Workflow
When sickness is recorded:
1. **SicknessAbsence** record created in database
2. Shift marked as UNCOVERED
3. **Automated Cover Workflow** initiated:
   - Priority 1: Attempts staff reallocation (same home/unit)
   - Priority 2: Sends OT offers to qualified staff
   - Priority 3: Escalates to agency if no response
4. **Management Alerts**:
   - Head of Service notified
   - Cover request created
   - Real-time status tracking
5. **Staff Records Updated**:
   - Bradford Factor calculated
   - Sickness patterns tracked
   - Return-to-work triggers activated

#### Annual Leave
- Updates leave balance
- Notifies line manager
- Tracks against entitlement
- Displays on team calendar

#### Unauthorised Absence
- Creates urgent alert
- Flags for HR/management review
- Tracks for performance management
- Requires manager investigation

### How to Use

1. Navigate to **Pattern Overview** (Staff Management menu)
2. Select care home and filters
3. Click on any shift cell
4. In the modal:
   - Select **Annual Leave**, **Sickness**, or **Unauthorised Leave**
   - OR select a different unit to reassign
5. Click **Save Change**
6. System confirms action and triggers automation

### Visual Indicators

| Type | Display | Color | Background |
|------|---------|-------|------------|
| Annual Leave | A/L | White | Green (#2ecc71) |
| Sickness | SICK | White | Red (#e74c3c) |
| Unauthorised | UNAUTH | White | Orange (#e67e22) |
| Regular Unit | Unit Name | White | Position Color (1-9) |

### Management Benefits

1. **Real-time recording** - No need to switch pages
2. **Automated cover** - System handles staff reallocation
3. **Instant alerts** - Management notified immediately
4. **Audit trail** - All actions logged with timestamp
5. **Pattern analysis** - Sickness trends tracked automatically
6. **Compliance** - Bradford Factor, return-to-work triggers

### Integration with Existing Systems

- ✅ SicknessAbsence model (staff_records app)
- ✅ Workflow Orchestrator (automated reallocation)
- ✅ Notification system (management alerts)
- ✅ StaffingCoverRequest (OT offers, agency)
- ✅ ActivityLog (audit trail)
- ✅ Leave balance tracking

### Permissions

- **Requires**: `can_manage_rota` permission
- **Roles**: Operations Manager, Senior Management Team
- **Access**: Care home-specific (or all homes for SMT)

### API Endpoint

**POST** `/api/update-shift-unit/`

**Payload:**
```json
{
  "shift_id": 123,
  "unit_name": "LEAVE_SICK" | "LEAVE_ANNUAL" | "LEAVE_UNAUTHORISED" | "Bluebell"
}
```

**Response (Leave):**
```json
{
  "success": true,
  "message": "Sickness recorded for John Smith. Automated cover workflow triggered",
  "display_text": "SICK",
  "leave_type": "SICK"
}
```

**Response (Unit Change):**
```json
{
  "success": true,
  "message": "Shift updated to Primrose",
  "unit_name": "Primrose",
  "full_unit_name": "HAWTHORN_HOUSE_Primrose"
}
```

---

## Testing Instructions

1. Navigate to Pattern Overview
2. Select **Hawthorn House**
3. Click on a shift cell for any staff member
4. Select **Sickness** from dropdown
5. Save and verify:
   - Cell changes to red background with "SICK" text
   - Success message appears
   - Check Django admin for SicknessAbsence record
   - Check notifications for management alert
   - Verify automated workflow triggered (check logs)

---

**Last Updated:** January 27, 2026  
**Version:** 1.0  
**Status:** Production Ready
