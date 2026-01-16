# Senior Dashboard Date Range Filtering Guide

## Overview
The Senior Management Dashboard now supports flexible date range filtering for all reports and metrics. This allows you to analyze data for any period, from a single day to a full year.

## Features

### 1. Date Range Selection
- **Start Date**: Select the beginning date for your report
- **End Date**: Select the ending date for your report
- **Default**: Both dates default to today

### 2. Quick Actions
- **Apply Filter**: Updates all dashboard metrics for the selected date range
- **Reset**: Returns to default view (today only)
- **Export CSV**: Downloads comprehensive report for the date range

## How to Use

### Basic Date Filtering

1. **Navigate to the Senior Dashboard**
   ```
   http://127.0.0.1:8000/senior-dashboard/
   ```

2. **Select Your Date Range**
   - Click on the "Start Date" field and choose a date
   - Click on the "End Date" field and choose a date
   - Click "📊 Apply Filter"

3. **View Updated Data**
   - All sections update to show data for your selected range:
     - Home Overview (occupancy remains current snapshot)
     - Staffing Coverage (aggregated across date range)
     - Fiscal Summary (totals for the period)
     - Alerts & Actions (filtered by date range)
     - Quality Metrics (calculated for the period)

### URL Parameters
You can also use URL parameters to set date ranges directly:

```
http://127.0.0.1:8000/senior-dashboard/?start_date=2025-12-01&end_date=2025-12-31
```

**Parameters:**
- `start_date` - Format: YYYY-MM-DD
- `end_date` - Format: YYYY-MM-DD

## Exporting Reports

### CSV Export
Click the "📥 Export CSV" button to download a comprehensive report containing:

1. **Metadata Section**
   - Report generation timestamp
   - Date range covered
   - Organization details

2. **Home Overview**
   - Occupancy rates
   - Bed capacity
   - Unit counts
   - Locations

3. **Staffing Coverage**
   - Day shift actual vs required
   - Night shift actual vs required
   - Coverage percentages
   - Status indicators

4. **Fiscal Summary**
   - Agency budget and spend
   - Overtime budget and spend
   - Utilization percentages
   - Total budget vs actual

5. **Detailed Shift Data**
   - Every shift in the date range
   - Staff assignments
   - Shift types and classifications
   - Time details

### Export File Naming
Files are automatically named with the date range:
```
senior_dashboard_2025-12-01_2025-12-31.csv
```

## Common Use Cases

### Daily Operations Review
- **Date Range**: Today only (default)
- **Purpose**: Monitor current day staffing and immediate alerts
- **Frequency**: Multiple times per day

### Weekly Management Review
- **Date Range**: Last 7 days
- **Example**: `start_date=2025-12-08&end_date=2025-12-15`
- **Purpose**: Weekly performance review
- **Frequency**: Monday mornings

### Monthly Financial Analysis
- **Date Range**: Full calendar month
- **Example**: `start_date=2025-12-01&end_date=2025-12-31`
- **Purpose**: Budget utilization review
- **Frequency**: End of each month

### Quarterly Board Reports
- **Date Range**: 3 months (e.g., Q4: Oct-Dec)
- **Example**: `start_date=2025-10-01&end_date=2025-12-31`
- **Purpose**: Executive board presentations
- **Frequency**: Quarterly

### Annual Compliance Audit
- **Date Range**: Full year
- **Example**: `start_date=2025-01-01&end_date=2025-12-31`
- **Purpose**: Annual regulatory compliance
- **Frequency**: Annually

### Custom Investigation
- **Date Range**: Any specific period
- **Purpose**: Investigate specific incidents or trends
- **Frequency**: As needed

## Data Interpretation

### Staffing Coverage Calculations
When viewing multi-day ranges:
- **Required shifts** = (Daily requirement × Number of days in range)
- **Actual shifts** = Total shifts worked in the range
- **Coverage %** = (Actual / Required) × 100

Example:
- 3 care homes × 7 days = 21 home-days
- 8 staff required per day per home
- Required = 21 × 8 = 168 shifts
- If 160 actual shifts = 95.2% coverage

### Fiscal Data
- Budget figures remain monthly (standard budgets)
- Spend figures accumulate across the date range
- Utilization shows: (Range spend / Monthly budget) × 100
  - Values >100% indicate over-budget for the period

### Status Indicators
- **GOOD** (Green): ≥100% coverage
- **WARNING** (Amber): 80-99% coverage
- **CRITICAL** (Red): <80% coverage

## Tips & Best Practices

### 1. Performance Considerations
- Larger date ranges (>90 days) may take longer to load
- Export function is optimized for any range
- Consider breaking very long periods into quarters for faster analysis

### 2. Data Accuracy
- Ensure shifts are properly categorized (REGULAR, OVERTIME, AGENCY)
- Staff assignments must be complete for accurate reporting
- Agency shifts identified by `user__isnull=True`

### 3. Sharing Reports
- Export CSV files can be opened in Excel, Google Sheets
- URL with parameters can be shared with other managers
- Bookmarks can be created for common date ranges

### 4. Troubleshooting
- **No data showing**: Check date range doesn't extend beyond available data
- **Unexpected totals**: Verify shift classifications in database
- **Export not downloading**: Check browser pop-up blocker settings

## Technical Details

### API Endpoints
- **Dashboard**: `/senior-dashboard/`
- **Export**: `/senior-dashboard/export/`

### Query Parameters
| Parameter | Type | Format | Default | Description |
|-----------|------|--------|---------|-------------|
| start_date | string | YYYY-MM-DD | Today | Start of date range |
| end_date | string | YYYY-MM-DD | Today | End of date range |
| format | string | csv | csv | Export format (future: pdf, xlsx) |

### Data Filtering
All queries automatically filter by:
- `date__gte=start_date` (greater than or equal)
- `date__lte=end_date` (less than or equal)
- Active units only (`is_active=True`)
- Valid shift statuses (`SCHEDULED`, `CONFIRMED`)

## Future Enhancements (Planned)

- **Preset Ranges**: Quick buttons for "Last 7 Days", "This Month", "This Quarter"
- **Comparison Mode**: Compare two date ranges side-by-side
- **PDF Export**: Formatted PDF reports with charts
- **Email Scheduling**: Auto-email reports on schedule
- **Custom Metrics**: User-defined KPIs and thresholds
- **Chart Visualizations**: Graphical trends within dashboard

## Support

For questions or issues with date filtering:
1. Check this guide for common solutions
2. Verify date formats (YYYY-MM-DD)
3. Ensure you have senior management permissions
4. Contact system administrator if problems persist

---

**Last Updated**: December 15, 2025
**Version**: 1.0
**Applies To**: Multi-Home Staff Rota System v2.0
