# Staff Login & Leave Request - Quick Reference

## Staff Login Credentials

**All Staff:**
- Username: Your SAP number (e.g., 000544, 000003, 000690)
- Password: `password123`

**Example:**
```
SAP: 000544
Password: password123
```

---

## How to Request Leave (Staff)

1. **Login** at `/login/` with your SAP and password
2. **Navigate** to "Request Leave" or `/request-leave/`
3. **Fill in the form:**
   - Start Date: First day of leave
   - End Date: Last day of leave
   - Leave Type: Usually "Annual Leave"
   - Reason: Optional but helpful
4. **Submit** - System will process automatically

---

## Auto-Approval Rules

Your leave will be **automatically approved** if:
- ✅ Request is for annual/personal/training leave
- ✅ Request is 14 days or less
- ✅ Request is NOT during Christmas period (Dec 11 - Jan 8)
- ✅ Less than 2 other staff are off on those dates
- ✅ Staffing levels stay above 17 staff on duty

Your leave will go to **manual review** if:
- ⚠ Request is during Christmas blackout period
- ⚠ Request is more than 14 days
- ⚠ Would cause staffing to drop below minimum
- ⚠ More than 2 staff already off on requested dates

---

## Checking Your Leave Balance

**From Staff Dashboard** (`/my-rota/`):
- View total entitlement
- See hours/days used
- Check hours/days remaining
- View pending requests
- See leave history

**Typical Entitlements:**
- 35-hour staff: 196 hours = 16.81 days
- 24-hour staff: 196 hours = 16.33 days
- Management: 196 hours = 28 days

---

## Manager Leave Approval

**Dashboard:** `/leave-approvals/`

**Actions:**
- ✅ **Approve** - Green button next to request
- ❌ **Deny** - Red button next to request
- 🔍 **Filter** - By status (pending/approved/manual review)
- 📊 **Stats** - See auto-approval statistics

**Status Types:**
- **Pending**: Awaiting auto-approval check
- **Manual Review**: Needs your approval (flagged by system)
- **Approved**: Already approved (auto or manual)
- **Denied**: Rejected

---

## Common Scenarios

### Scenario 1: Quick Weekend Break
```
Request: 2 days (Friday + Monday) in March
Result: ✅ AUTO-APPROVED
Reason: Within all limits, no conflicts
```

### Scenario 2: Summer Holiday
```
Request: 10 days in July
Result: ✅ AUTO-APPROVED (if staffing OK)
Reason: Under 14-day limit
```

### Scenario 3: Long Holiday
```
Request: 20 days in August
Result: ⚠ MANUAL REVIEW
Reason: Over 14-day limit - needs manager approval
```

### Scenario 4: Christmas Leave
```
Request: 5 days Dec 22-26
Result: ⚠ MANUAL REVIEW
Reason: During blackout period (Dec 11 - Jan 8)
Purpose: Ensures fair distribution of Christmas leave
```

### Scenario 5: Staffing Conflict
```
Request: 3 days when 2 staff already approved
Result: ⚠ MANUAL REVIEW
Reason: Would exceed concurrent leave limit
```

---

## Troubleshooting

### Can't Login?
1. Check SAP number is correct (no spaces)
2. Confirm password is exactly `password123` (lowercase)
3. Try different browser
4. Contact manager if still failing

### Leave Not Showing?
1. Refresh the page
2. Check "Leave History" section
3. Look in "Pending Requests"
4. Check with manager if missing

### Balance Incorrect?
1. Balance updates when leave is approved
2. Pending requests show separately
3. Check transaction history
4. Contact HR if discrepancy persists

---

## Key URLs

| Page | URL | Who Can Access |
|------|-----|---------------|
| Login | `/login/` | Everyone |
| Staff Dashboard | `/my-rota/` | All staff |
| Request Leave | `/request-leave/` | All staff |
| Manager Dashboard | `/dashboard/` | Managers only |
| Leave Approvals | `/leave-approvals/` | Managers only |
| Home Dashboard | `/home/` | All (filtered by home) |

---

## Leave Balance Calculations

**How hours are deducted:**

**Shift Workers (35hr contract):**
- 1 day = 11.66 hours
- 5 days = 58.30 hours
- 10 days = 116.60 hours

**Shift Workers (24hr contract):**
- 1 day = 12.00 hours
- 5 days = 60.00 hours
- 10 days = 120.00 hours

**Management (7hr days):**
- 1 day = 7.00 hours
- 5 days = 35.00 hours
- 10 days = 70.00 hours

---

## Support Contacts

**Login Issues:**
- Contact your line manager
- Email: IT Support

**Leave Balance Questions:**
- Contact HR
- Check with Operations Manager

**System Errors:**
- Screenshot the error
- Note what you were doing
- Report to manager

---

## Important Dates

**Christmas Blackout Period:**
- December 11, 2025 → January 8, 2026
- All leave requests during this period require manual review
- Purpose: Ensure fair distribution of Christmas leave across all staff
- Manager approval needed for fairness

**Leave Year:**
- Starts: April 1, 2025
- Ends: March 31, 2026
- Unused leave may carry over (check policy)
- Use-by date for carryover: September 30, 2026

---

## Quick Tips

✅ **DO:**
- Request leave as early as possible
- Check your balance before requesting
- Add a reason for your request (helps managers)
- Check if colleagues are already off
- Request long holidays well in advance

❌ **DON'T:**
- Leave requests until last minute
- Request more days than you have
- Assume auto-approval for Christmas period
- Forget to check your pending requests
- Submit duplicate requests

---

**Last Updated:** December 20, 2025  
**System Version:** Production v1.0  
**For full details:** See `LOGIN_AND_LEAVE_SYSTEM_VERIFICATION.md`
