# CSV Template Instructions

## File Created: STAFF_BULK_UPLOAD_TEMPLATE.csv

This file is located at:
```
/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/STAFF_BULK_UPLOAD_TEMPLATE.csv
```

---

## How to Use This Template

### Step 1: Open the CSV File
- **Option A:** Double-click `STAFF_BULK_UPLOAD_TEMPLATE.csv` to open in Excel/Numbers
- **Option B:** Right-click → Open With → Excel/Numbers/Google Sheets

### Step 2: Edit the Template
Replace the example data with your actual staff information:

**Required Columns:**
1. **Home_Name** - Name of the care home (e.g., "RIVERSIDE", "VICTORIA_GARDENS")
2. **Unit_Name** - Unit within the home (e.g., "Unit_1", "Jasmine", "Management")
3. **SAP** - Unique staff ID number (e.g., 100001, 100002)
4. **First_Name** - Staff member's first name
5. **Last_Name** - Staff member's surname
6. **Role** - Staff role code (see below)
7. **Team** - Rotation team (A, B, C, or MGMT for management)
8. **Shift_Pattern** - Pattern_1, Pattern_2, or Pattern_3
9. **Hours_Per_Week** - 24, 35, or 37.5
10. **Password** - Initial login password (staff can change later)

---

## Role Codes

| Code | Full Name | Description |
|------|-----------|-------------|
| **OM** | Operations Manager | Senior management |
| **SM** | Service Manager | Senior management |
| **SSCW** | Senior Social Care Worker (Day) | Day supervisor |
| **SSCWN** | Senior Social Care Worker (Night) | Night supervisor |
| **SCW** | Social Care Worker (Day) | Day care staff |
| **SCWN** | Social Care Worker (Night) | Night care staff |
| **SCA** | Social Care Assistant (Day) | Day care assistant |
| **SCAN** | Social Care Assistant (Night) | Night care assistant |

---

## Shift Patterns

| Pattern | Contract Hours | Shifts per Week | Schedule Type |
|---------|---------------|-----------------|---------------|
| **Pattern_1** | 24 hours | 2 shifts | Night shifts (8pm-8am) |
| **Pattern_2** | 35 hours | 3 shifts | Day shifts (8am-8pm) |
| **Pattern_3** | Management | 5 days | Mon-Fri (9am-5pm) |

### 3-Week Rolling Rota

The system uses a **3-week rolling rota** with **Teams A, B, and C** for each unit.

#### Pattern_1 (24-hour contract - 2 shifts/week)
**Night shifts (8pm-8am), 6 shifts over 3 weeks:**

- **Team A:** Week 1 (Fri, Sat) | Week 2 (Sun, Thu) | Week 3 (Mon, Tue)
- **Team B:** Week 1 (Sun, Mon) | Week 2 (Fri, Sat) | Week 3 (Sun, Thu)
- **Team C:** Week 1 (Mon, Tue) | Week 2 (Fri, Sat) | Week 3 (Sun, Thu)

#### Pattern_2 (35-hour contract - 3 shifts/week)
**Day shifts (8am-8pm), 9 shifts over 3 weeks:**

- **Team A:** Week 1 (Wed, Fri, Sat) | Week 2 (Sun, Wed, Thu) | Week 3 (Mon, Tue, Wed)
- **Team B:** Week 1 (Sun, Mon, Tue) | Week 2 (Wed, Fri, Sat) | Week 3 (Sun, Wed, Thu)
- **Team C:** Week 1 (Mon, Tue, Wed) | Week 2 (Wed, Fri, Sat) | Week 3 (Sun, Tue, Wed)

#### Pattern_3 (Management)
**Monday to Friday, 9am-5pm every week:**
- Consistent schedule across all weeks
- No weekend or night shifts
- Team: MGMT (no rotation)

---

## Team Assignment Rules

- **Team A, B, C** - Care staff rotate on 3-week cycle with staggered schedules
- **Team MGMT** - Management staff (fixed Mon-Fri schedule)

**Key Points:**
- Each team works different days within the 3-week rotation
- This creates continuous coverage every day
- Spread staff evenly across teams (e.g., 6 staff = 2 per team)
- Each unit should have staff on all three teams for full coverage

---

## Example: Staffing One Unit (15 beds)

Per unit, you need 6 staff:

```csv
Home_Name,Unit_Name,SAP,First_Name,Last_Name,Role,Team,Shift_Pattern,Hours_Per_Week,Password
RIVERSIDE,Jasmine,200001,Alice,Cooper,SSCW,A,Pattern_2,35,Welcome123##
RIVERSIDE,Jasmine,200002,Bob,Martin,SSCWN,B,Pattern_2,35,Welcome123##
RIVERSIDE,Jasmine,200003,Carol,White,SCW,C,Pattern_2,35,Welcome123##
RIVERSIDE,Jasmine,200004,Daniel,Green,SCWN,A,Pattern_2,35,Welcome123##
RIVERSIDE,Jasmine,200005,Emily,Black,SCA,B,Pattern_1,24,Welcome123##
RIVERSIDE,Jasmine,200006,Frank,Grey,SCAN,C,Pattern_1,24,Welcome123##
```

---

## Recommended Staffing Numbers

### Large Home (120 beds, 8 care units):
- **Management:** 2 (1 OM + 1 SM)
- **Per Unit:** 6 staff × 8 units = 48 staff
- **Additional:** Variable based on needs
- **Total:** ~179 staff

### Medium Home (70 beds, 5 care units):
- **Management:** 2 (1 OM + 1 SM)
- **Per Unit:** 6 staff × 5 units = 30 staff
- **Additional:** Variable based on needs
- **Total:** ~98 staff

---

## Step 3: Save Your File

1. **Save As** new filename (e.g., "RIVERSIDE_STAFF_IMPORT.csv")
2. **Keep format:** CSV (Comma delimited)
3. **Verify:** Open saved file to check formatting

---

## Step 4: Upload to System

### Using Web Interface (Recommended):
1. Login as **Superuser** (SAP: 000541, Password: Greenball99##)
2. Navigate to **Admin** → **Bulk Import** or **Tools** → **Bulk Operations**
3. Select **"Import Staff from CSV"**
4. Upload your CSV file
5. Review preview of imported data
6. Confirm import

### Using Django Shell (Advanced):
```python
python manage.py shell
from your_import_script import import_staff_from_csv
import_staff_from_csv('path/to/your_file.csv')
```

---

## Common Mistakes to Avoid

❌ **Don't:**
- Use duplicate SAP numbers
- Mix different homes in same file without clear unit names
- Leave required fields empty
- Use special characters in names (except hyphens and apostrophes)
- Forget to include management staff

✅ **Do:**
- Start SAP numbers from a clear range (e.g., 200000-299999 for one home)
- Use consistent unit naming (e.g., "Unit_1" not "unit 1" or "Unit1")
- Include all required columns
- Test with small batch first (5-10 staff)
- Back up database before large imports

---

## Validation Checks

The system will check:
1. ✅ All SAP numbers are unique
2. ✅ Home and Unit names exist in system
3. ✅ Role codes are valid
4. ✅ Team assignments are valid (A, B, C, MGMT)
5. ✅ Shift patterns match hours/week
6. ✅ Required fields are not empty

---

## Quick Reference: Template Rows

**Management Row:**
```csv
NEW_HOME,Management,100001,Robert,Anderson,OM,MGMT,Pattern_3,37.5,Password123##
```

**Day Supervisor Row:**
```csv
NEW_HOME,Unit_1,100002,John,Smith,SSCW,A,Pattern_2,35,Password123##
```

**Night Supervisor Row:**
```csv
NEW_HOME,Unit_1,100003,Jane,Doe,SSCWN,B,Pattern_2,35,Password123##
```

**Care Staff Row (35 hours):**
```csv
NEW_HOME,Unit_1,100004,Mike,Jones,SCW,C,Pattern_2,35,Password123##
```

**Care Staff Row (24 hours):**
```csv
NEW_HOME,Unit_1,100005,Sarah,Brown,SCA,A,Pattern_1,24,Password123##
```

---

## File Location

**CSV File:** 
```
/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/STAFF_BULK_UPLOAD_TEMPLATE.csv
```

**Full Template Documentation:**
```
/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/STAFFING_SETUP_TEMPLATE.md
```

---

## Need Help?

- See **STAFFING_SETUP_TEMPLATE.md** for detailed staffing ratios
- See **QUICK_START_STAFFING_TEMPLATE.md** for navigation guide
- Check **TEMPLATE_DEMO** home in system for working example

The CSV file is ready to download and use! Just open it, replace the example data with your staff, and upload to the system.
