# AI Assistant Reports - Quick Reference

## 🎯 Quick Query Examples

### Staffing
```
"How many staff do we have?"
"Show staffing levels"
"Total staff count"
```

### Sickness
```
"Who is off sick today?"
"Show me sickness this week"
"How many people are sick?"
```

### Incidents
```
"Show incidents today"
"Any accidents this week?"
"Incident summary"
```

### Shift Coverage
```
"What's the coverage today?"
"Who is working today?"
"Show me tomorrow's shifts"
```

### Leave Requests
```
"Show leave requests"
"Who has low leave balance?"
"Annual leave summary"
```

## 📊 Report Types & Triggers

| Report | Trigger Words | Time Modifiers |
|--------|--------------|----------------|
| Staffing | `staff`, `count`, `levels` | N/A |
| Sickness | `sick`, `sickness`, `absence` | `today`, `week`, `month` |
| Incidents | `incident`, `accident`, `fall` | `today`, `week`, `month` |
| Coverage | `coverage`, `shifts`, `working`, `rota` | `today`, `tomorrow`, date |
| Leave | `leave`, `holiday`, `vacation`, `balance` | N/A |

## ⏰ Time References

| Say This | Means |
|----------|-------|
| `today` / `now` | Current day |
| `tomorrow` | Next day |
| `this week` | Last 7 days |
| `this month` | Last 30 days |
| No time word | Default (7 days for most reports) |

## 📈 What Each Report Shows

### Staffing Summary
- ✅ Total active staff
- ✅ Breakdown by role
- ✅ Role counts

### Sickness Report
- ✅ Currently off sick
- ✅ Recent cases (timeframe)
- ✅ Staff names, SAP, days off
- ✅ Status (Open, Fit Note, etc.)

### Incident Report
- ✅ Total incidents
- ✅ Severity breakdown (Death, Major, Moderate, Low)
- ✅ Type breakdown (Falls, Medication, etc.)
- ✅ Care Inspectorate notifications
- ⚠️ Critical alerts

### Shift Coverage
- ✅ Total shifts scheduled
- ✅ Coverage by unit
- ✅ Day/Night breakdown
- ✅ Coverage by shift type

### Leave Summary
- ✅ Pending requests count
- ✅ Approved future leave
- ✅ Low balance alerts (<40hrs)
- ✅ Top 5 lowest balances

## 🚨 Critical Alerts

Reports automatically highlight:
- ☠️ **Deaths** → Immediate visual alert
- 🔴 **Major Harm** → Warning indicator  
- ⚠️ **CI Notifications** → Clear flagging
- 📉 **Low Leave Balance** → Staff list

## 💻 API Response Format

```json
{
  "answer": "Human-readable formatted report text",
  "related": ["Suggested", "Next", "Actions"],
  "category": "report",
  "report_type": "specific_type",
  "report_data": {
    "summary": "Text summary",
    "total": 123,
    "by_category": {...},
    "details": [...]
  }
}
```

## 🔧 Common Combinations

### Monday Morning Review
```
1. "Show me incidents this weekend"
2. "Who is sick today?"
3. "What's the coverage today?"
4. "Show leave requests"
```

### End of Month Check
```
1. "Incidents this month"
2. "Sickness this month"
3. "How many staff do we have?"
4. "Who has low leave balance?"
```

### Daily Quick Check
```
1. "Coverage today"
2. "Any incidents?"
3. "Who's sick?"
```

## ⚡ Pro Tips

1. **Be conversational** - "How many staff?" works just as well as "Total staff count"
2. **Use time words** - Add "today", "this week", "this month" for precision
3. **Check related topics** - AI suggests follow-up actions
4. **Export data** - Use `report_data` field for CSV/Excel export
5. **Follow critical alerts** - Always review highlighted warnings

## 📊 Data Export

All reports include `report_data` in JSON format:

```python
# Use this for:
- CSV/Excel export
- Custom dashboards
- Integration with other systems
- Visualizations
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| No data returned | Check database has records for that timeframe |
| Wrong timeframe | Be specific: "today" vs "this week" vs "this month" |
| Slow response | Reports query DB in real-time - normal for large datasets |
| Error message | Check server logs for details |

## 🌟 Example Conversations

**Quick Check:**
```
You: "Coverage today"
AI: [Shows 59 shifts across 8 units]

You: "Any incidents?"
AI: [Shows 1 incident in last 24 hours]
```

**Detailed Analysis:**
```
You: "Show me sickness this month"
AI: [Shows 15 cases, 5 currently off, breakdown]

You: "What about incidents?"
AI: [Shows 8 incidents, severity breakdown, CI alerts]
```

**Planning:**
```
You: "Coverage tomorrow"
AI: [Shows next day's shifts by unit]

You: "Show leave requests"
AI: [Shows 3 pending, 12 approved]
```

## 📚 Documentation

- **Full Guide**: [AI_ASSISTANT_REPORTS_GUIDE.md](AI_ASSISTANT_REPORTS_GUIDE.md)
- **AI Assistant**: [AI_ASSISTANT_GUIDE.md](AI_ASSISTANT_GUIDE.md)
- **Weekly Reports**: [WEEKLY_REPORT_GUIDE.md](WEEKLY_REPORT_GUIDE.md)
- **Dashboard**: [README.md](README.md)

---

**Quick Start:** Just ask! Try: *"How many staff do we have?"*
