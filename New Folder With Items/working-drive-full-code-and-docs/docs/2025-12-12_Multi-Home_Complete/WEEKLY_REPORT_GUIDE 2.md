# Weekly Monday Morning Management Report

## Overview

The weekly management report is a comprehensive automated report that runs every Monday morning at 7:00 AM, covering all significant events from the previous weekend (Friday-Sunday).

## What's Included

The report provides a complete overview of:

1. **Sickness Absences**
   - All staff off sick during the weekend period
   - Status of each sickness record
   - Total working days sick
   - Reason for absence
   - Expected return dates

2. **Weekend Shift Coverage & Overtime**
   - Total shifts worked over the weekend
   - Estimated hours worked
   - Potential overtime (staff working 3+ shifts)
   - Detailed breakdown by staff member, unit, and shift type

3. **Agency Staff Usage**
   - Number of agency shifts used
   - Unique agency staff members
   - Estimated cost (£350 per shift)
   - Breakdown by agency worker and unit

4. **Incidents & Serious Events**
   - All incidents reported during the weekend
   - Deaths (if any)
   - Hospital admissions
   - Care Inspectorate notifications required
   - Breakdown by severity and type
   - Detailed incident information including reference numbers

## Running the Report Manually

### Basic Usage
```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py generate_weekly_report
```

### Save to File
```bash
python3 manage.py generate_weekly_report --save
```
This saves a JSON file to `/tmp/weekly_report_YYYYMMDD.json`

### Generate for Specific Date
```bash
python3 manage.py generate_weekly_report --date 2025-12-08
```
(Must be a Monday)

### Email Report (Future Feature)
```bash
python3 manage.py generate_weekly_report --email
```
*Note: Email functionality is planned for future implementation*

## Automated Scheduling

### Installation

Run the installation script to set up automatic Monday morning reports:

```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
./install_weekly_report.sh
```

This will:
- Create a cron job to run every Monday at 7:00 AM
- Set up logging to `logs/weekly_report.log`
- Run a test report to verify everything works

### Cron Schedule

The report runs automatically:
- **When**: Every Monday at 7:00 AM
- **Coverage**: Previous Friday 00:00 to Sunday 23:59
- **Output**: Console output + JSON file + Log file

### Viewing Logs

```bash
# View recent log entries
tail -f /Users/deansockalingum/Staff\ Rota/rotasystems/logs/weekly_report.log

# View full log
cat /Users/deansockalingum/Staff\ Rota/rotasystems/logs/weekly_report.log
```

### Managing the Cron Job

**View current crontab:**
```bash
crontab -l
```

**Edit crontab:**
```bash
crontab -e
```

**Remove the weekly report cron job:**
```bash
crontab -e
# Then delete the line containing 'generate_weekly_report'
```

## Report Output

### Terminal Output

The terminal displays a formatted, color-coded report:
- ✓ Green checkmarks for sections with no issues
- ⚠ Yellow warnings for potential concerns
- ⚠ Red alerts for critical events (deaths, high severity incidents)

### JSON File Output

Location: `/tmp/weekly_report_YYYYMMDD.json`

Structure:
```json
{
  "report_date": "2025-12-08T07:00:00+00:00",
  "period_start": "2025-12-05T00:00:00+00:00",
  "period_end": "2025-12-07T23:59:59.999999+00:00",
  "sickness": {
    "total_staff_off_sick": 0,
    "records": []
  },
  "overtime": {
    "total_weekend_shifts": 179,
    "estimated_hours": 2237.5,
    "potential_overtime_shifts": 81,
    "shifts": []
  },
  "agency_staff": {
    "total_agency_shifts": 0,
    "unique_agency_staff": 0,
    "estimated_cost": 0,
    "staff_usage": {}
  },
  "incidents": {
    "total_incidents": 0,
    "hospital_admissions": 0,
    "deaths": 0,
    "care_inspectorate_notifications": 0,
    "all_incidents": []
  }
}
```

## Key Metrics Explained

### Sickness Tracking
- **Status**: OPEN, AWAITING_FIT_NOTE, RETURNED, CLOSED
- **Total Days**: Working days absent (Mon-Fri)
- Reports any staff who were sick at any point during the weekend

### Overtime Calculation
- **Standard**: Weekend shifts are analyzed for overtime patterns
- **Threshold**: Staff working 3+ shifts in a weekend flagged as potential overtime
- **Hours**: Based on 12.5-hour standard shift length

### Agency Staff Detection
Agency staff are identified by:
- SAP number starting with 'AGY' or 'AGENCY'
- Role name containing 'AGENCY'
- Cost estimated at £350 per shift

### Incident Severity Levels
- **Death**: Requires immediate Care Inspectorate notification
- **Major Harm**: Hospitalization, requires Care Inspectorate notification
- **Moderate Harm**: Medical intervention required
- **Low Harm**: Minor injury
- **No Harm**: Near miss

### Care Inspectorate Notifications

Automatic notification is required for:
- Deaths
- Major harm incidents
- Suspected abuse (physical, psychological, financial, neglect, sexual)
- Allegations against staff
- Infection outbreaks

## Using Report Data

### For Management Review
1. **Monday Morning**: Review the automated report in your email/logs
2. **Priority Actions**: Address any deaths, Care Inspectorate notifications, or high-severity incidents first
3. **Resource Planning**: Review overtime and agency usage for cost control
4. **Sickness Patterns**: Identify any concerning absence patterns

### For Compliance Audits
- JSON files provide a complete audit trail
- Can be archived for regulatory inspection
- Includes all required Care Inspectorate data points

### For Financial Planning
- Agency costs clearly identified
- Overtime hours quantified
- Weekend staffing levels documented

## Troubleshooting

### Report Not Running Automatically

1. Check cron is configured:
   ```bash
   crontab -l | grep weekly_report
   ```

2. Check log file for errors:
   ```bash
   cat /Users/deansockalingum/Staff\ Rota/rotasystems/logs/weekly_report.log
   ```

3. Re-run installation:
   ```bash
   ./install_weekly_report.sh
   ```

### Report Shows Unexpected Data

**Sickness not showing:**
- Check `SicknessRecord` model has correct dates
- Verify `actual_last_working_day` or `estimated_return_to_work` fields

**Overtime calculation issues:**
- System calculates based on 3+ shifts in weekend
- Review shift records in admin for accuracy

**Agency staff not detected:**
- Verify agency staff SAP numbers start with 'AGY' or 'AGENCY'
- Or ensure role name contains 'AGENCY'

### Missing Dependencies

If you see import errors:
```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
pip3 install -r requirements.txt
```

## Future Enhancements

Planned features:
- ✉️ **Email Distribution**: Automatic email to management team
- 📊 **PDF Generation**: Formatted PDF report attached to email
- 📈 **Trend Analysis**: Week-over-week comparisons
- 🔔 **SMS Alerts**: Urgent notifications for critical incidents
- 💾 **Database Storage**: Archive reports in database for historical analysis
- 📱 **Mobile App**: Push notifications to management mobile devices

## Support

For issues or questions:
1. Check this documentation
2. Review logs in `logs/weekly_report.log`
3. Test manually with `python3 manage.py generate_weekly_report`
4. Contact system administrator

## Related Documentation

- [Manager Dashboard Guide](AI_ASSISTANT_GUIDE.md)
- [Incident Reporting](COMPLIANCE_WEB_FORMS_COMPLETE.md)
- [Sickness Management](STAFF_RECORDS_IMPLEMENTATION.md)
- [Scheduled Tasks](SCHEDULED_TASKS_SETUP.md)
