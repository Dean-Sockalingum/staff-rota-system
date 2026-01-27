# Pattern Overview - Vacancy Management System

## Overview
A new Excel-style scrollable view that shows the 3-week rota patterns for all staff positions, allowing quick identification of vacancies and shift pattern preservation.

## Purpose
When a staff member leaves, this view allows you to:
- Mark their position as "VACANCY" 
- Preserve the exact shift pattern (role, hours, team, days worked)
- Quickly identify what type of position needs filling when recruiting

## Features

### Visual Layout
- **Horizontal scrolling table** - similar to your Excel file
- **Fixed left column** - shows staff details (Name, SAP, Role, Team, Hours/Week)
- **Date columns** - 21 days (3 weeks) from Jan 27 - Feb 16, 2026
- **Shift indicators**:
  - `D` = Day shift (blue)
  - `N` = Night shift (dark gray)
  - `M` = Management shift (purple)

### Filters
- **Care Home** - Filter by specific home or view all
- **Unit** - Filter by specific unit or view all

### Stats Summary
- Total Positions
- Total Vacancies
- Days Shown
- Number of Units

### Vacancy Management
- **"Mark Vacancy" button** next to each active staff member
- Clicking converts: "John Smith" → "VACANCY SCA" (preserves role)
- Shifts are preserved - you know exactly what pattern is needed
- Position becomes inactive (doesn't appear in normal staff lists)

## Access
URL: `http://127.0.0.1:8000/pattern-overview/`

Permissions: Requires `can_manage_rota` role permission

## Use Case Example

### Scenario: SCA Sarah leaves from Team A, Pear Unit

**Before resignation:**
```
Name: Sarah Jones
SAP: 10145
Role: SCA
Team: A
Hours: 36hrs/wk
Pattern: Wed, Fri, Sat (Week 1) | Sun, Wed, Thu (Week 2) | Mon, Tue, Wed (Week 3)
```

**After marking vacancy:**
```
Name: VACANCY SCA
SAP: 10145
Role: SCA
Team: A  
Hours: 36hrs/wk
Pattern: Wed, Fri, Sat (Week 1) | Sun, Wed, Thu (Week 2) | Mon, Tue, Wed (Week 3)
```

**Recruitment team can see:**
- Need: 36hr/week Social Care Assistant
- For: Pear Unit (SRD)
- Team: A (specific 3-week rotation)
- Days: Wed/Fri/Sat → Sun/Wed/Thu → Mon/Tue/Wed

This prevents accidentally hiring:
- Wrong grade (SCW instead of SCA)
- Wrong hours (24hr instead of 36hr)
- Wrong team (Team B when need Team A)

## Technical Details

### Files Created
1. **View**: `scheduling/views_pattern_overview.py`
   - `pattern_overview()` - Main view displaying the table
   - `toggle_vacancy_status()` - AJAX endpoint for marking vacancies

2. **Template**: `scheduling/templates/scheduling/pattern_overview.html`
   - Responsive scrolling table
   - Sticky columns and headers
   - Color-coded shift indicators

3. **URLs**: Added to `scheduling/urls.py`
   - `/pattern-overview/` - Main page
   - `/api/toggle-vacancy/` - AJAX vacancy toggle

### Database Impact
- Uses existing models: `User`, `Shift`, `Unit`, `CareHome`
- When marking vacancy:
  - `first_name` → "VACANCY"
  - `last_name` → Role name (e.g., "SCA")
  - `is_active` → False
  - All shifts preserved
  - All attributes (role, team, unit, sap) preserved

## Future Enhancements (Optional)

1. **Fill Vacancy Function**: 
   - Click "Fill Vacancy" to open form
   - Enter new staff details
   - Automatically assign to preserved shift pattern

2. **Export to Excel**:
   - Download current pattern view
   - Share with recruitment team

3. **Vacancy History**:
   - Track when position became vacant
   - Track how long vacant
   - Average time-to-fill metrics

4. **Pattern Templates**:
   - Save common patterns
   - Quick apply when creating new positions

5. **Date Range Selector**:
   - View different 3-week periods
   - See future vacancy planning

## Next Steps

As discussed, we created this as a **standalone page first** to:
1. Test the layout and functionality
2. Gather feedback on the design
3. Determine if it should replace the existing rota view or remain separate

### Decision Points:
- Keep both views (current rota + pattern overview)?
- Replace current rota with pattern overview?
- Merge features from both?
- Any additional fields needed (training status, probation period, etc.)?

## Testing Checklist
- [x] View loads without errors
- [x] Filters work (care home, unit)
- [x] Staff details display correctly
- [x] Shift patterns render properly
- [x] Sticky columns work on scroll
- [ ] "Mark Vacancy" button works (test this)
- [ ] Vacancy appears in red/italic
- [ ] Stats update correctly
- [ ] Different care homes show correct data
- [ ] Mobile responsiveness (future)

## Support
For issues or questions about this feature, check:
- Template: `scheduling/templates/scheduling/pattern_overview.html`
- View logic: `scheduling/views_pattern_overview.py`
- URL config: `scheduling/urls.py` (lines with pattern_overview)
