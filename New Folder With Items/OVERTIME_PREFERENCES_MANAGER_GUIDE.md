# Overtime Preferences - Manager Guide

## Overview
The Overtime Preferences system allows managers to track which staff members are willing to work overtime shifts, along with their availability, preferences, and contact details.

## Accessing the System

### Option 1: Manager Dashboard Navigation
1. Log in with your manager credentials
2. Click on **"Overtime Preferences"** in the top navigation menu
3. You'll see the full list of staff overtime preferences

### Option 2: Direct URL
Navigate to: `http://127.0.0.1:8000/management/overtime/preferences/`

## Features

### 1. Overview Dashboard
The main page shows:
- **Statistics Cards**:
  - Number of staff available for OT
  - Total preferences recorded
  - Staff without preferences
  - Overall availability rate

- **Filter Options**:
  - Search by staff name or SAP number
  - Filter by care home
  - Filter by availability status

### 2. Staff Preference List
Each staff member's row displays:
- **Staff Details**: Name, SAP number, role, home unit
- **Availability Status**: Available/Unavailable badge
- **Willing to Work At**: Care homes they'll cover
- **Shift Preferences**: Early/Late/Night shifts, Weekdays/Weekends
- **Contact Info**: Preferred contact method and phone number
- **Performance**: Acceptance rate and shifts worked
- **Actions**: Edit or Delete buttons

### 3. Adding New Preferences

**Step-by-Step:**

1. Click **"Add New Preference"** button (top right)
2. Select a staff member from the dropdown (only shows staff without existing preferences)
3. Fill in the following details:

   **Overtime Availability**
   - Toggle switch to mark if staff is available for OT

   **Willing to Work At**
   - Check boxes for each care home they'll cover
   - Options: Hawthorn House, Meadowburn, Orchard Grove, Riverside, Victoria Gardens

   **Shift Type Preferences**
   - ☀️ Early Shifts
   - ☁️ Late Shifts
   - 🌙 Night Shifts

   **Day Preferences**
   - 📅 Weekdays (Mon-Fri)
   - 📆 Weekends (Sat-Sun)

   **Contact Information**
   - Phone Number (e.g., 07700 900000)
   - Preferred Contact Method:
     - Phone Call
     - Text Message
     - Email
     - WhatsApp

   **Constraints**
   - Max Hours Per Week (optional - leave blank for no limit)
   - Minimum Notice Required (default: 24 hours)

   **Additional Notes**
   - Any special requirements, restrictions, or preferences

4. Click **"Save Preference"**

### 4. Editing Existing Preferences

1. Find the staff member in the list
2. Click the **Edit** button (pencil icon)
3. Update any fields as needed
4. The form also shows:
   - Performance statistics
   - Acceptance rate
   - Total shifts worked
   - Last contacted date
5. Click **"Save Preference"**

### 5. Deleting Preferences

1. Find the staff member in the list
2. Click the **Delete** button (trash icon)
3. Confirm the deletion when prompted

## How to Use for Overtime Coverage

### When You Need Overtime Coverage:

1. **Access the Preferences List**
   - Go to Overtime Preferences
   - Filter by:
     - The specific care home needing coverage
     - Availability status (show only "Available for OT")

2. **Check Shift Preferences**
   - Look at the shift type icons:
     - ☀️ = willing to do early shifts
     - ☁️ = willing to do late shifts
     - 🌙 = willing to do night shifts

3. **Contact Staff**
   - Use the listed phone number
   - Contact via their preferred method (phone/text/email/WhatsApp)
   - Respect their minimum notice hours

4. **Track Performance**
   - The system automatically tracks:
     - How many times each staff member has been contacted
     - Their acceptance rate
     - Total overtime shifts worked
   - This helps identify reliable staff for future requests

## Best Practices

### For Accurate Data
- ✅ Update preferences when staff circumstances change
- ✅ Add phone numbers for all willing staff
- ✅ Note staff preferences for contact method
- ✅ Record any constraints (max hours, notice period)
- ✅ Use the notes field for important details

### For Efficient Coverage
- ✅ Filter by care home first to see who can cover that location
- ✅ Check shift type compatibility before contacting
- ✅ Respect minimum notice hours to improve acceptance rates
- ✅ Contact staff with higher acceptance rates first
- ✅ Keep track of who's worked recent OT to distribute fairly

### For Data Quality
- ✅ Regularly review staff without preferences
- ✅ Encourage all staff to provide their OT preferences
- ✅ Update contact information when staff notify you of changes
- ✅ Delete preferences for staff who have left

## Example Scenarios

### Scenario 1: Need Night Shift Coverage at Meadowburn
1. Go to Overtime Preferences
2. Set filters:
   - Care Home: Meadowburn
   - Availability: Available for OT
3. Click "Filter"
4. Look for staff with 🌙 (night shift) icon
5. Contact them using their preferred method
6. Note the minimum notice they require

### Scenario 2: Weekend Coverage Needed
1. Access the preferences list
2. Filter by availability
3. Look for staff with 📆 (weekends) icon
4. Sort by acceptance rate (visible in Performance column)
5. Contact most reliable staff first

### Scenario 3: Adding New Staff Member
1. Click "Add New Preference"
2. Select: "John Smith (SAP: 12345) - Care Assistant"
3. Set availability: ✓ Available for overtime
4. Willing to work at: ✓ Orchard Grove, ✓ Hawthorn House
5. Shifts: ✓ Early, ✓ Late
6. Days: ✓ Weekdays, ✓ Weekends
7. Phone: 07700 123456
8. Contact method: Text Message
9. Max hours per week: 48
10. Min notice: 24 hours
11. Notes: "Prefers morning shifts but flexible"
12. Save

## Troubleshooting

### Can't Find a Staff Member in Add New?
- They may already have a preference - check the main list
- They may be marked as management role
- They may be inactive in the system

### Contact Details Not Showing?
- Edit the preference and add phone number
- Verify staff member's contact info is up to date

### Performance Stats Not Updating?
- These update when overtime requests are tracked in the system
- Manual contacts won't update statistics

## Quick Reference URLs

- **Main List**: `/management/overtime/preferences/`
- **Add New**: `/management/overtime/preferences/add/`
- **Edit**: `/management/overtime/preferences/edit/{id}/`

## Support

For technical issues or questions about the overtime preferences system, contact your system administrator or IT support.

---

**Last Updated**: 27 December 2025  
**Version**: 1.0  
**Module**: Overtime Preferences Management
