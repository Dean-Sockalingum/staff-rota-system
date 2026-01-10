# Executive Analytics Dashboard Enhancement
**Date:** January 1, 2026  
**Task:** Enhanced executive analytics chart with day/night shift breakdown and per-home staffing visibility

## User Requirement
> "in this exec chart it would be better to have more of a breakdown by shift day or night and which home requires staffing"

## Implementation Summary

### 1. Enhanced Data Collection (`executive_summary_service.py`)

**Modified Function:** `ExecutiveSummaryService.get_trend_analysis()`

**New Data Points Added:**
- **Day shift metrics:**
  - `day_fill_rate`: Fill rate for DAY, EARLY, LATE, LONG_DAY shifts
  - `day_shifts_total`: Total number of day shifts
  
- **Night shift metrics:**
  - `night_fill_rate`: Fill rate for NIGHT shifts  
  - `night_shifts_total`: Total number of night shifts

- **Per-home breakdown** (when viewing all homes):
  - Home name
  - Overall fill rate
  - Day shift fill rate
  - Night shift fill rate
  - Total shifts, day shifts, night shifts
  - Number of vacancies

**Data Structure:**
```python
{
    'week_start': date,
    'week_end': date,
    'total_shifts': 460,
    'fill_rate': 92.3,
    'day_fill_rate': 95.2,  # NEW
    'night_fill_rate': 87.5,  # NEW
    'day_shifts_total': 300,  # NEW
    'night_shifts_total': 160,  # NEW
    'agency_rate': 8.2,
    'cost': 55200.0,
    'homes': [  # NEW
        {
            'name': 'Hawthorn House',
            'fill_rate': 94.0,
            'day_fill_rate': 96.0,
            'night_fill_rate': 90.0,
            'total_shifts': 92,
            'day_shifts': 60,
            'night_shifts': 32,
            'vacancies': 5
        },
        // ... more homes
    ]
}
```

### 2. Enhanced Chart Visualization (`executive_summary_dashboard.html`)

**Chart Improvements:**

1. **Multiple Dataset Lines:**
   - Green line: Overall Fill Rate (existing)
   - **Blue line: Day Shifts Fill Rate** (NEW)
   - **Purple line: Night Shifts Fill Rate** (NEW)
   - Orange line: Agency Rate (existing)

2. **Enhanced Tooltips:**
   - Shows total shifts breakdown (day vs night)
   - **Displays per-home staffing data** sorted by urgency
   - **Status icons:**
     - ⚠️ Red: Fill rate < 85% (critical)
     - ⚡ Yellow: Fill rate 85-95% (needs attention)
     - ✓ Green: Fill rate ≥ 95% (good)
   - Shows vacancies per home
   - Displays day/night fill rates for each home

3. **Current Week Staffing Status Panel:**
   - Added visual section below trend chart
   - Shows all care homes sorted by urgency (lowest fill rate first)
   - Split progress bars:
     - Left side: Day shift fill rate (blue)
     - Right side: Night shift fill rate (purple)
   - Displays overall fill rate and vacancy count
   - Color-coded status indicators

**Example Tooltip Output:**
```
Hawthorn House: 94%
Total Shifts: 460
Day Shifts: 300 | Night Shifts: 160

--- Staffing by Care Home ---
⚠️ Riverside: 82%
  Day: 85% | Night: 78% (18 vacancies)
⚡ Victoria Gardens: 88%
  Day: 90% | Night: 85% (12 vacancies)
✓ Hawthorn House: 94%
  Day: 96% | Night: 90% (6 vacancies)
✓ Meadowburn: 96%
  Day: 97% | Night: 94% (4 vacancies)
✓ Orchard Grove: 98%
  Day: 99% | Night: 96% (2 vacancies)
```

## Benefits

### For Executives:
1. **Immediate visibility** into day vs night staffing patterns
2. **Quick identification** of homes with critical staffing needs
3. **Trend analysis** across multiple dimensions (time, shift type, location)
4. **Prioritized action list** - homes sorted by urgency

### For Decision-Making:
1. **Resource allocation:** See which homes need day vs night staff
2. **Trend spotting:** Identify if night shifts consistently underperform
3. **Budget planning:** Understand agency usage patterns by shift type
4. **Strategic hiring:** Target recruitment based on specific gaps

## Technical Details

**Files Modified:**
1. `scheduling/executive_summary_service.py` (lines 192-243)
   - Enhanced `get_trend_analysis()` method
   - Added day/night shift filtering
   - Added per-home data collection

2. `scheduling/templates/scheduling/executive_summary_dashboard.html`
   - Lines 415-427: Added chart legend and staffing status panel
   - Lines 488-536: Enhanced chart with 3 datasets (overall, day, night)
   - Lines 545-595: Enhanced tooltips with home-specific data
   - Lines 657-725: Added JavaScript to render current week staffing bars

**Database Queries:**
- Uses existing `Shift` model
- Filters by shift type names: `['DAY', 'EARLY', 'LATE', 'LONG_DAY']` for day, `['NIGHT']` for night
- No database schema changes required

**Performance:**
- Minimal impact: Adds 2-3 extra queries per week analyzed (day shifts, night shifts, per-home)
- For 12-week trend: ~24-36 additional queries
- Queries are simple filters, no complex joins

## Testing Recommendations

1. **View with all homes selected** (default):
   - Verify 4 lines appear in chart (overall, day, night, agency)
   - Check tooltip shows all 5 homes with day/night breakdown
   - Confirm staffing status panel shows all homes sorted by fill rate

2. **View with single home selected:**
   - Verify 4 lines still appear
   - Check tooltip shows total shifts breakdown
   - Confirm staffing status panel shows "No per-home data" message

3. **Check edge cases:**
   - Week with 100% fill rate
   - Week with very low fill rate (<80%)
   - Week with no night shifts
   - Week with no data

## Future Enhancements

1. **Interactive filtering:** Click on a home in the status panel to filter the chart
2. **Comparison mode:** Select 2 homes to compare side-by-side
3. **Alerts:** Automatic notifications when home fill rate drops below threshold
4. **Export:** Include day/night breakdown in PDF export
5. **Mobile optimization:** Make status bars responsive for smaller screens

## Deployment Notes

- No database migrations required
- No new dependencies
- Backwards compatible (works with existing data)
- Can be deployed immediately to production

---
**Status:** ✅ Complete and ready for testing
