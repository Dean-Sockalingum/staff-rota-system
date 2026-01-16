# SOP: Staff Onboarding

**Document ID:** SOP-001  
**Version:** 1.0  
**Effective Date:** December 2025  
**Review Date:** March 2026  
**Owner:** HR Manager

---

## Purpose

This SOP defines the process for adding new staff members to the Staff Rota Management System and setting up their profiles for immediate use.

## Scope

- Applies to all new permanent and temporary staff
- Covers quick onboarding, bulk import, and profile management
- Used by HR staff, administrators, and unit managers

## Responsibilities

| Role | Responsibility |
|------|----------------|
| **HR Manager** | Approve new starters, provide staff details |
| **System Administrator** | Add staff to system, assign permissions |
| **Unit Manager** | Verify unit assignment, provide induction |
| **New Staff Member** | Complete profile, update contact details |

---

## Process Overview

```
New Starter Approved → Add to System → Assign Permissions → Create Profile → Training → Go Live
```

**Time Required:** 5 seconds (quick onboarding) or 5 minutes (full profile setup)

---

## Procedure

### Method 1: Quick Onboarding (5-Second Setup) ⚡

**Use When:** Single staff member needs immediate access

**Steps:**

1. **Navigate to Quick Onboarding**
   - Log in to system at `http://[system-url]/`
   - Click **"Management"** in top navigation
   - Select **"Quick Onboarding"** from menu
   - **URL:** `/management/quick-onboarding/`

2. **Enter Staff Details**
   ```
   Required Fields:
   - First Name (e.g., "John")
   - Last Name (e.g., "Smith")
   - SAP Number (unique, e.g., "SAP001234")
   - Unit (select from dropdown: DEMENTIA, BLUE, ORANGE, etc.)
   - Role (select: Care Staff, Senior Carer, Unit Manager, etc.)
   ```

3. **Click "Add Staff Member"**
   - System generates username automatically (e.g., `jsmith`)
   - System creates temporary password: `ChangeMe123!`
   - Staff member appears in system immediately

4. **Record Credentials**
   - Note username and temporary password
   - Provide to new staff member via secure method
   - They MUST change password on first login

**Expected Result:**
- ✅ Staff member active in system within 5 seconds
- ✅ Can log in immediately
- ✅ Assigned to correct unit
- ✅ Basic permissions active

---

### Method 2: Bulk Staff Import

**Use When:** Adding multiple staff members (10+) at once

**Steps:**

1. **Prepare CSV File**
   - Download template: Click **"Download CSV Template"** in Quick Onboarding page
   - Open in Excel or Google Sheets
   - Fill in required columns:
     ```
     First Name, Last Name, SAP Number, Unit, Role, Email, Phone
     John, Smith, SAP001234, DEMENTIA, Care Staff, john.smith@email.com, 07700900123
     Jane, Doe, SAP001235, BLUE, Senior Carer, jane.doe@email.com, 07700900124
     ```

2. **Save as CSV**
   - File → Save As → CSV (Comma delimited)
   - Filename: `staff_import_DDMMYYYY.csv`

3. **Import to System**
   - Navigate to **Management → Quick Onboarding**
   - Click **"Bulk Import"** tab
   - Click **"Choose File"** and select your CSV
   - Click **"Preview Import"**
   - Review staff list for errors
   - Click **"Confirm Import"**

4. **Review Results**
   - System displays:
     - ✅ Successfully imported: X staff
     - ⚠️ Warnings: Duplicate SAP numbers
     - ❌ Errors: Missing required fields
   - Fix any errors and re-import if needed

5. **Export Credentials**
   - Click **"Export Login Details"**
   - Save PDF with all usernames and temporary passwords
   - Distribute securely to unit managers

**Expected Result:**
- ✅ All staff imported in one batch
- ✅ Usernames and passwords generated
- ✅ Ready for first login

---

### Method 3: Full Profile Setup

**Use When:** Need complete staff record with all details

**Steps:**

1. **Add Basic Information** (use Quick Onboarding first - see Method 1)

2. **Complete Extended Profile**
   - Navigate to **Management → Staff Records**
   - Search for new staff member (by name or SAP)
   - Click **"Edit Profile"**

3. **Add Contact Information**
   ```
   - Email address
   - Mobile phone number
   - Emergency contact name
   - Emergency contact number
   - Home address (optional)
   ```

4. **Employment Details**
   ```
   - Start date
   - Contract type (Permanent/Temporary/Agency)
   - Contract hours per week
   - Hourly rate (if applicable)
   - Annual leave entitlement
   - Probation end date (if applicable)
   ```

5. **Training & Compliance**
   ```
   - DBS check date and number
   - DBS renewal date (3 years from check)
   - Mandatory training completed (tick boxes)
   - Induction completion date
   - Supervision schedule
   ```

6. **System Permissions**
   - Tick permissions based on role:
     - **Care Staff:** View rota, request leave, swap shifts, view residents
     - **Senior Carer:** All care staff + approve shift swaps
     - **Unit Manager:** All + manage unit rota, approve leave, additional staffing
     - **Administrator:** Full system access

7. **Save Profile**
   - Click **"Save Changes"**
   - System confirms: "Profile updated successfully"

**Expected Result:**
- ✅ Complete staff record
- ✅ Compliance tracking active
- ✅ Full system access configured

---

## First Login Process (For New Staff)

**What New Staff Must Do:**

1. **Receive Login Details**
   - Username (e.g., `jsmith`)
   - Temporary password: `ChangeMe123!`
   - System URL: `http://[system-url]/`

2. **First Login**
   - Go to system URL
   - Enter username and temporary password
   - Click **"Login"**

3. **Change Password**
   - System forces password change
   - New password must contain:
     - At least 8 characters
     - One uppercase letter
     - One lowercase letter
     - One number
     - One special character (!@£$%^&*)
   - Enter new password twice
   - Click **"Change Password"**

4. **Complete Welcome Wizard**
   - Update contact details
   - Upload profile photo (optional)
   - Set notification preferences
   - Review rota
   - Click **"Finish Setup"**

5. **System Tour**
   - AI Assistant launches automatically
   - Shows key features:
     - "This is your rota calendar"
     - "Here's how to request annual leave"
     - "Your profile is here"
   - Click **"Next"** through tour
   - Click **"Get Started"**

**Expected Result:**
- ✅ Password changed successfully
- ✅ Profile personalized
- ✅ Ready to use system

---

## Common Scenarios

### Scenario 1: Emergency Cover Staff

**Situation:** Agency staff member needs immediate access for tonight's shift

**Action:**
1. Use Quick Onboarding (5-second method)
2. Enter minimal details:
   - Name, SAP (or temp ID like "TEMP001"), Unit, Role
3. Generate credentials
4. Text username/password to staff member
5. Staff can log in from mobile phone immediately

**Time:** Less than 2 minutes from approval to access

---

### Scenario 2: Graduate Cohort (25 New Staff)

**Situation:** 25 newly qualified nurses starting on same date

**Action:**
1. Prepare CSV with all 25 staff details
2. Use Bulk Import
3. Assign all to "New Starters" team initially
4. Export credentials PDF
5. Print and include in welcome packs
6. Reassign to units after induction week

**Time:** 15 minutes for full import and setup

---

### Scenario 3: Staff Transfer Between Units

**Situation:** Existing staff member transferring from BLUE to ORANGE unit

**Action:**
1. Navigate to Staff Records
2. Search for staff member
3. Edit profile
4. Change **Unit** from BLUE to ORANGE
5. Save changes
6. Staff member automatically sees ORANGE unit rota
7. No new login required - change is immediate

**Time:** 30 seconds

---

### Scenario 4: Temporary Role Upgrade

**Situation:** Care Staff promoted to Acting Unit Manager for 3 months

**Action:**
1. Edit staff profile
2. Add **Secondary Role:** "Unit Manager"
3. Set **Role End Date:** [3 months from today]
4. Grant Unit Manager permissions (temporary)
5. System automatically revokes permissions on end date
6. Email notification sent to staff confirming upgrade

**Time:** 2 minutes

---

## Verification & Quality Checks

**After Adding Staff, Verify:**

- [ ] Staff member appears in Staff Records search
- [ ] Assigned to correct unit (check unit rota)
- [ ] SAP number is unique (no duplicates)
- [ ] Can log in with provided credentials
- [ ] Password change works on first login
- [ ] Correct permissions for role (test key functions)
- [ ] Appears in correct team lists
- [ ] Email notifications working (if email provided)

**Weekly Audit (HR Manager):**
- Review all new starters from past week
- Confirm all profiles complete
- Check training compliance recorded
- Verify DBS details entered
- Ensure probation end dates set

---

## Troubleshooting

### Issue: "SAP number already exists"

**Cause:** Duplicate SAP number or staff member already in system

**Solution:**
1. Search for existing staff member
2. If duplicate: Update existing record instead
3. If left organization: Mark as inactive first, then create new record
4. If error: Use different SAP number or add suffix (e.g., SAP001234-2)

---

### Issue: "Username already taken"

**Cause:** Another staff member with same name (e.g., two "J. Smith")

**Solution:**
1. System auto-generates alternative: `jsmith2`
2. Or manually set username: `john.smith` or `j.smith1`
3. Inform staff member of their specific username

---

### Issue: Staff can't log in with provided credentials

**Cause:** Password mistyped, account not active, or caps lock

**Solution:**
1. Verify username spelling (case-sensitive)
2. Check caps lock is OFF
3. If still failing: Reset password
   - Navigate to Staff Records → Find staff → Click "Reset Password"
   - New temporary password generated
   - Provide to staff member
4. Ensure account status is "Active" not "Pending"

---

### Issue: Staff member doesn't see their unit's rota

**Cause:** Not assigned to correct unit

**Solution:**
1. Edit staff profile
2. Verify **Unit** field matches their work unit
3. Save changes
4. Ask staff to refresh browser (Ctrl+F5)
5. Rota should now display

---

### Issue: Bulk import fails with errors

**Cause:** CSV format incorrect or missing required fields

**Solution:**
1. Download fresh template
2. Check all required columns present: First Name, Last Name, SAP, Unit, Role
3. Ensure no blank rows in middle of data
4. Check for special characters (remove apostrophes, quotes)
5. Save as CSV UTF-8 format
6. Try importing just first 5 rows as test
7. If errors persist, contact System Administrator

---

## Data Protection & Security

### Personal Data Handling

**Staff records contain personal data protected under GDPR:**

- ✅ **DO:** Only access staff records when needed for your role
- ✅ **DO:** Keep login credentials secure and confidential
- ✅ **DO:** Shred printed credential lists after distribution
- ✅ **DO:** Log out when finished
- ❌ **DON'T:** Share credentials via email (use secure method)
- ❌ **DON'T:** Leave staff lists on display
- ❌ **DON'T:** Export data unnecessarily

**Data Retention:**
- Active staff: Retained indefinitely while employed
- Leavers: Retained for 7 years then deleted
- Audit logs: Retained for 7 years

---

## Related Procedures

- [SOP: Shift Management](SOP_SHIFT_MANAGEMENT.md) - Assigning staff to rotas
- [SOP: System Maintenance](SOP_SYSTEM_MAINTENANCE.md) - User access management
- Staff Offboarding Procedure (when staff leave)

---

## Management Commands

### Generate Staff Report

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py staff_report
```

**Output:** List of all active staff with SAP numbers, units, and roles

---

### Bulk Password Reset

```bash
python3 manage.py reset_passwords --unit DEMENTIA
```

**Use When:** Security breach or mass password reset needed

---

## Training Requirements

**Before performing staff onboarding, complete:**

- [ ] System login and navigation
- [ ] Understanding user roles and permissions
- [ ] GDPR data protection awareness
- [ ] This SOP (read and understood)
- [ ] Supervised practice with test accounts

**Competency Sign-Off:** HR Manager or System Administrator

---

## Key Performance Indicators (KPIs)

**We measure onboarding effectiveness:**

| Metric | Target | How Measured |
|--------|--------|--------------|
| **Onboarding Time** | <5 seconds (quick) | System timer |
| **Profile Completeness** | 100% within 48 hours | Weekly audit |
| **First Login Success** | >95% | Support ticket analysis |
| **Training Compliance** | 100% within 2 weeks | Training matrix |
| **Credential Security** | Zero breaches | Audit logs |

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Dec 2025 | Initial SOP creation | System Admin |

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **HR Manager** | | | |
| **Operations Director** | | | |
| **Data Protection Officer** | | | |

---

**For support with staff onboarding, contact:**
- **Email:** hr@[organization].com
- **Phone:** [Insert number]
- **AI Assistant:** Ask "How do I add a new staff member?"

**Next SOP:** [Shift Management](SOP_SHIFT_MANAGEMENT.md)
