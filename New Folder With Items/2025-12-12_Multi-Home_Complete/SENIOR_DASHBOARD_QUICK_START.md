# Quick Start: Date Range Filtering

## Accessing Date Filters

The date range filter bar appears at the top of the Senior Management Dashboard, just below the header.

```
┌─────────────────────────────────────────────────────────────────────┐
│  🏥 Senior Management Dashboard                                      │
│  Multi-Home Oversight • Sunday, December 15, 2025 at 11:52 AM      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  Start Date        End Date         [📊 Apply Filter]  [🔄 Reset]   │
│  [2025-12-15▼]    [2025-12-15▼]    [📥 Export CSV]                 │
│                                                                       │
│  Showing data from: December 15, 2025 to December 15, 2025 (1 days) │
└─────────────────────────────────────────────────────────────────────┘
```

## Example Queries

### 1. View Last Week's Data
```
Start Date: 2025-12-08
End Date:   2025-12-15
Click: "Apply Filter"
```

**Result**: Dashboard shows 7 days of data
- Staffing coverage for the week
- Total shifts worked: ~448 shifts (64/day × 7 days)
- Weekly fiscal spending
- All leave requests from that week

### 2. View Full Month (December)
```
Start Date: 2025-12-01
End Date:   2025-12-31
Click: "Apply Filter"
```

**Result**: Dashboard shows full month
- Monthly staffing trends
- Total budget utilization
- 1,984 shifts (64/day × 31 days)
- Complete month-end reporting data

### 3. Export Custom Range
```
Start Date: 2025-11-30
End Date:   2025-12-15
Click: "Export CSV"
```

**Result**: Downloads CSV file
- Filename: `senior_dashboard_2025-11-30_2025-12-15.csv`
- Contains: 16 days of detailed data
- All homes, all shifts, all metrics
- Ready for Excel/Google Sheets analysis

## What Gets Filtered?

### ✅ Sections That Use Date Range:

1. **Staffing Coverage**
   - Shows total shifts in the range
   - Calculates required shifts for all days
   - Updates coverage percentages

2. **Fiscal Summary** 
   - Agency spend across the range
   - Overtime costs for the period
   - Budget utilization calculations

3. **Alerts & Actions**
   - Leave requests in the range
   - Reallocations during the period
   - Critical alerts for those dates

4. **Quality Metrics**
   - Incident counts
   - Training completion
   - Compliance scores

5. **Detailed Export**
   - Every shift between the dates
   - Staff assignments
   - Full audit trail

### ℹ️ Sections That Don't Change:

1. **Home Overview**
   - Current occupancy (real-time snapshot)
   - Bed capacity (static configuration)
   - Unit counts (current state)

*These show current state regardless of date range selected*

## Direct URL Examples

You can bookmark or share these URLs:

### Today Only (Default)
```
http://127.0.0.1:8000/senior-dashboard/
```

### This Week
```
http://127.0.0.1:8000/senior-dashboard/?start_date=2025-12-08&end_date=2025-12-15
```

### This Month
```
http://127.0.0.1:8000/senior-dashboard/?start_date=2025-12-01&end_date=2025-12-31
```

### Last Quarter (Oct-Dec)
```
http://127.0.0.1:8000/senior-dashboard/?start_date=2025-10-01&end_date=2025-12-31
```

### Full Year (2025)
```
http://127.0.0.1:8000/senior-dashboard/?start_date=2025-01-01&end_date=2025-12-31
```

## Export Examples

### Weekly Report (Monday Morning)
```
Start Date: Previous Monday
End Date:   Previous Sunday
Click: "Export CSV"
Use: Weekly management meeting
```

### Month-End Financial
```
Start Date: First of month
End Date:   Last of month  
Click: "Export CSV"
Use: Finance department review
```

### Quarterly Board Report
```
Start Date: Quarter start (e.g., 2025-10-01)
End Date:   Quarter end (e.g., 2025-12-31)
Click: "Export CSV"
Use: Board presentation preparation
```

## Understanding the Numbers

### Example Interpretation

**Date Range**: December 1-15, 2025 (15 days)

**Staffing Section Shows:**
```
Home: Orchard Grove
Day Shifts Actual:   480
Day Shifts Required: 540  (36 staff/day × 15 days)
Day Coverage:        88.9%
Status:              ⚠️ WARNING
```

**What This Means:**
- 60 day shifts are unfilled over the 15-day period
- Averaging 4 unfilled shifts per day
- Coverage is below 90% threshold
- Action required to improve staffing

### Reading the CSV Export

The CSV contains multiple sections:

```csv
Senior Management Dashboard Report
Generated:,2025-12-15 11:52:34
Date Range:,2025-12-01 to 2025-12-31

HOME OVERVIEW
Home,Current Occupancy,Bed Capacity,Occupancy Rate %,Active Units,Location
Orchard Grove,120,120,100.0,9,Edinburgh EH10 5HF

STAFFING COVERAGE
Home,Day Shifts Actual,Day Shifts Required,Day Coverage %,...
Orchard Grove,480,540,88.9,...

DETAILED SHIFT DATA
Date,Home,Unit,Staff Name,Staff SAP,Shift Type,Classification,Status,...
2025-12-01,Orchard Grove,Unit 1,Ailsa Kelly,10000,DAY,REGULAR,SCHEDULED,...
2025-12-01,Orchard Grove,Unit 1,Angus MacKenzie,10001,DAY,REGULAR,CONFIRMED,...
...
```

## Tips for Best Results

1. **Start with Today**: Get familiar with the default view first
2. **Use Week View**: Great for quick weekly reviews (7 days)
3. **Month View for Finance**: Best for budget discussions
4. **Export Before Meetings**: Download CSV the day before
5. **Bookmark Frequent Ranges**: Save commonly used date ranges
6. **Compare Periods**: Export two different months and compare in Excel

## Troubleshooting

**Q: Date filter shows no data**
A: Check that your date range includes dates where shifts exist. Current data runs from Nov 30, 2025 to Nov 28, 2026.

**Q: Coverage percentages seem wrong**
A: Remember the formula multiplies daily requirements by days in range. A 7-day view shows 7× the daily requirement.

**Q: Export button not working**
A: Check your browser's pop-up blocker. The CSV downloads as a file.

**Q: Can I filter by specific home?**
A: Not yet - this filters all homes simultaneously. Individual home filtering is planned for a future update.

---

**Need help?** The senior dashboard is designed to be intuitive. Try different date ranges to see how the data changes!
