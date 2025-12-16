# Weekly Management Report - Quick Reference

## 📅 Schedule
**Every Monday at 7:00 AM** - Automatic report covering Friday-Sunday

## 🎯 Quick Commands

### Run Report Now
```bash
cd /Users/deansockalingum/Staff\ Rota/rotasystems
python3 manage.py generate_weekly_report
```

### Save Report to File
```bash
python3 manage.py generate_weekly_report --save
```

### Check Last Report
```bash
cat /tmp/weekly_report_$(date +%Y%m%d).json | python3 -m json.tool | less
```

### View Logs
```bash
tail -f logs/weekly_report.log
```

## 📊 Report Sections

| Section | What It Shows | Key Metrics |
|---------|---------------|-------------|
| **Sickness** | Staff off sick over weekend | Count, days, reasons |
| **Overtime** | Weekend shift coverage | Hours, potential OT shifts |
| **Agency** | External staff usage | Cost (£350/shift), count |
| **Incidents** | All reported events | Severity, CI notifications |

## 🚨 Priority Alerts

Look for these in your Monday report:

- ☠️ **Deaths** - Immediate CI notification required
- 🏥 **Hospital Admissions** - Major harm incidents
- 📢 **Care Inspectorate Notifications** - Regulatory reporting needed
- 💰 **High Agency Costs** - Budget impact
- 🔴 **High Severity Incidents** - Urgent review required

## 📁 File Locations

| File | Location |
|------|----------|
| Report JSON | `/tmp/weekly_report_YYYYMMDD.json` |
| Logs | `/Users/deansockalingum/Staff Rota/rotasystems/logs/weekly_report.log` |
| Command | `manage.py generate_weekly_report` |
| Install Script | `install_weekly_report.sh` |

## ⚙️ Cron Job

```bash
# View cron jobs
crontab -l

# Edit cron jobs  
crontab -e

# Current schedule: Every Monday at 7:00 AM
0 7 * * 1 cd /path/to/rotasystems && python3 manage.py generate_weekly_report --save --email
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Report not running | Check `crontab -l` and logs |
| No sickness data | Verify SicknessRecord dates |
| Agency not detected | Check SAP starts with 'AGY' |
| Missing incidents | Confirm incident_date in range |

## 📞 Quick Help

```bash
# Get help on command options
python3 manage.py generate_weekly_report --help

# Test without waiting for Monday
python3 manage.py generate_weekly_report --date 2025-12-08

# Reinstall cron job
./install_weekly_report.sh
```

## 📈 Key Numbers

- **Standard Shift**: 12.5 hours
- **Agency Cost**: £350 per shift
- **Overtime Threshold**: 3+ shifts in weekend
- **Working Days**: Mon-Fri (for sickness calculation)

## 🎨 Report Colors

- ✓ **Green** = All clear, no issues
- ⚠️ **Yellow** = Warning, review needed
- 🔴 **Red** = Critical, immediate action required
