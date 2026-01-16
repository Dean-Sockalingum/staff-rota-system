# AI Assistant - Enhanced Report Generation & Interpretation

## Overview

The AI Assistant chatbot now has **advanced report generation and interpretation capabilities**. Ask natural language questions and get instant, intelligent reports with analysis.

## 🚀 New Capabilities

### 1. **Instant Report Generation**
Ask questions in natural language and receive structured reports:

| Ask About | Example Questions | Report Type |
|-----------|------------------|-------------|
| **Staffing** | "How many staff do we have?"<br>"Show me staffing levels"<br>"Total staff count" | Staffing Summary |
| **Sickness** | "Who is off sick today?"<br>"Show me sickness absences"<br>"How many people are sick?" | Sickness Report |
| **Incidents** | "Show me recent incidents"<br>"Any accidents this week?"<br>"Incident summary" | Incident Report |
| **Coverage** | "What's the coverage today?"<br>"Who is working today?"<br>"Show me today's shifts" | Shift Coverage |
| **Leave** | "Show leave requests"<br>"Annual leave summary"<br>"Who has low leave balance?" | Leave Summary |

### 2. **Intelligent Time Interpretation**
The AI understands time references:
- **"today"** / **"now"** → Current day's data
- **"this week"** → Last 7 days
- **"this month"** → Last 30 days
- **"tomorrow"** → Next day's schedule

Examples:
- "Show me incidents today" → Last 24 hours
- "Who is sick this week?" → Last 7 days
- "Coverage tomorrow" → Next day's shifts

### 3. **Contextual Analysis**
Reports include:
- ✅ **Summary**: Key insights in plain English
- 📊 **Breakdowns**: Detailed data by category
- ⚠️ **Alerts**: Critical issues highlighted
- 🔗 **Related Topics**: Suggested follow-up actions

## 📋 Report Types

### Staffing Summary Report

**Trigger Words:** `staff count`, `how many staff`, `staffing levels`, `total staff`

**What You Get:**
- Total active staff count
- Breakdown by role (SCW, SSCW, SCA, etc.)
- Summary statement

**Example Query:**
```
"How many staff do we have?"
```

**Response:**
```
Staffing Summary

You currently have 160 active staff members across 5 different roles.

Breakdown by Role:
• Senior Care Worker (SSCW): 3
• Care Worker (SCW): 120
• Senior Care Assistant (SCA): 25
• Operations Manager (OM): 2
• Service Manager (SM): 1
```

---

### Sickness Report

**Trigger Words:** `sickness`, `sick`, `absence`, `off sick`, `who is sick`

**What You Get:**
- Current staff off sick
- Recent sickness cases (configurable timeframe)
- Active cases with details (name, days off, status)
- Summary with totals

**Example Queries:**
```
"Who is off sick today?"
"Show me sickness this week"
"How many people are sick?"
```

**Response:**
```
Sickness Report

Currently 3 staff off sick. 5 new sickness records in the last 7 days.

Currently Off Sick:
• Jane Smith (SCW1001) - 2 days - Open
• John Doe (SCW1045) - 5 days - Awaiting Fit Note
• Mary Jones (SSCW0012) - 1 days - Open
```

---

### Incident Report

**Trigger Words:** `incident`, `accidents`, `falls`, `injury`, `injuries`

**What You Get:**
- Total incidents in timeframe
- Breakdown by severity (Death, Major Harm, etc.)
- Breakdown by type (Falls, Medication Errors, etc.)
- Care Inspectorate notifications required
- Critical alerts for deaths/major harm

**Example Queries:**
```
"Show me incidents this week"
"Any accidents today?"
"Incident summary for the month"
```

**Response:**
```
Incident Report

5 total incidents in the last 7 days. 1 require Care Inspectorate notification.

By Severity:
• 🔴 Major Harm: 1
• 🟠 Moderate Harm: 2
• 🟡 Low Harm: 2

⚠️ 1 incidents require Care Inspectorate notification
```

---

### Shift Coverage Report

**Trigger Words:** `coverage`, `shifts today`, `who is working`, `rota today`, `schedule`

**What You Get:**
- Total shifts scheduled
- Coverage by unit (day/night breakdown)
- Coverage by shift type
- Date-specific summary

**Example Queries:**
```
"What's the coverage today?"
"Who is working today?"
"Show me tomorrow's shifts"
```

**Response:**
```
Shift Coverage

On Monday, 02 December 2025: 59 shifts scheduled across 8 units.

Coverage by Unit:
• Dementia Unit: Day 7 | Night 7
• Blue Unit: Day 7 | Night 7
• Orange Unit: Day 7 | Night 7
• Green Unit: Day 7 | Night 7
• Violet Unit: Day 7 | Night 7
• Rose Unit: Day 7 | Night 7
• Grape Unit: Day 7 | Night 7
• Peach Unit: Day 7 | Night 7
```

---

### Leave Summary Report

**Trigger Words:** `annual leave`, `holiday`, `vacation`, `leave requests`, `leave balance`

**What You Get:**
- Pending leave requests count
- Approved future leave bookings
- Staff with low leave balance (<40 hours)
- Top 5 staff with lowest balances

**Example Queries:**
```
"Show leave requests"
"Who has low leave balance?"
"Annual leave summary"
```

**Response:**
```
Leave Summary

3 pending leave requests. 12 approved future leave bookings. 8 staff with low leave balance.

Staff with Low Leave Balance (<40 hours):
• Jane Smith: 35.5 hours remaining
• John Doe: 28.0 hours remaining
• Mary Jones: 15.5 hours remaining
```

## 🎯 How to Use

### Via Web Interface

1. Navigate to the AI Assistant chatbot on your dashboard
2. Type your question in natural language
3. Press Enter or click Send
4. Receive instant structured report

### Example Conversation

```
You: "How many staff do we have?"
AI: [Staffing Summary Report]

You: "Who is sick today?"
AI: [Sickness Report for today]

You: "Show me incidents this week"
AI: [Incident Report for last 7 days]

You: "What's the coverage tomorrow?"
AI: [Shift Coverage for next day]
```

### API Usage

**Endpoint:** `POST /api/ai-assistant/`

**Request:**
```json
{
  "query": "How many staff do we have?"
}
```

**Response:**
```json
{
  "answer": "Staffing Summary\n\nYou currently have 160 active staff...",
  "related": ["View Dashboard", "Generate Report", "Export Data"],
  "category": "report",
  "report_type": "staffing_summary",
  "report_data": {
    "total": 160,
    "by_role": {
      "Senior Care Worker (SSCW)": 3,
      "Care Worker (SCW)": 120,
      ...
    },
    "summary": "You currently have 160 active staff members across 5 different roles."
  }
}
```

## 💡 Advanced Features

### Structured Data Export

All reports include `report_data` in the response - perfect for:
- Exporting to CSV/Excel
- Building dashboards
- Integration with other systems
- Custom visualizations

### Context-Aware Responses

The AI remembers context within a conversation:
```
You: "Show me sickness"
AI: [Sickness Report]

You: "What about last month?"
AI: [Sickness Report for 30 days]  // AI understood context
```

### Critical Alerts

High-priority issues are automatically highlighted:
- ☠️ **Deaths**: Immediate visual alert
- 🔴 **Major Harm**: Warning indicator
- ⚠️ **Care Inspectorate Notifications**: Clear flagging

## 🔧 Customization

### Adding New Report Types

Edit `/Users/deansockalingum/Staff Rota/rotasystems/scheduling/views/ai_assistant_api.py`:

```python
@staticmethod
def generate_custom_report():
    """Your custom report logic"""
    # Query database
    data = YourModel.objects.filter(...)
    
    return {
        'summary': 'Your summary here',
        'data': {...}
    }

# Add to interpret_query():
if 'your trigger words' in query_lower:
    return {
        'type': 'custom_report',
        'data': ReportGenerator.generate_custom_report()
    }
```

### Modifying Timeframes

Default timeframes can be adjusted in `interpret_query()`:
```python
days = 7  # Default week
if 'month' in query_lower:
    days = 30
elif 'quarter' in query_lower:
    days = 90
```

## 📊 Report Data Structure

All reports follow this structure:

```python
{
    'type': 'report_type_name',
    'data': {
        'summary': str,          # Human-readable summary
        '[specific_fields]': ..., # Report-specific data
        'total': int,            # Usually included
        'by_[category]': dict,   # Breakdowns
    }
}
```

## 🆘 Troubleshooting

### Reports Not Generating

**Check server logs:**
```bash
# View Django output
# Look for errors when you ask a question
```

**Test API directly:**
```bash
curl -X POST http://127.0.0.1:8000/api/ai-assistant/ \
  -H "Content-Type: application/json" \
  -d '{"query": "How many staff?"}'
```

### Incorrect Data

**Verify database:**
```bash
python3 manage.py shell -c "
from scheduling.models import User
print(f'Staff count: {User.objects.filter(is_staff=False, is_active=True).count()}')
"
```

### Slow Response

Reports query the database in real-time. For large datasets:
- Add database indexes
- Cache frequent queries
- Use background task queue (Celery)

## 🚀 Future Enhancements

Planned features:
- 📈 **Trend Analysis**: "Show me sickness trends over 6 months"
- 📊 **Comparative Reports**: "Compare this week to last week"
- 💾 **Saved Reports**: "Save this as my Monday morning report"
- 📧 **Email Reports**: "Email me the weekly summary"
- 📱 **Mobile Optimized**: Better formatting for mobile
- 🗣️ **Voice Queries**: "Alexa, ask Staff Rota how many staff are sick"
- 🤖 **Predictive Analytics**: "Predict next month's sickness rates"
- 📅 **Scheduled Reports**: "Send me sickness report every Monday"

## 📚 Related Documentation

- [AI Assistant Guide](AI_ASSISTANT_GUIDE.md)
- [Weekly Report Guide](WEEKLY_REPORT_GUIDE.md)
- [Manager Dashboard](README.md)
- [API Documentation](API_REFERENCE.md)

## 🎓 Best Practices

1. **Be Specific**: "Show me incidents today" is better than just "incidents"
2. **Use Natural Language**: The AI understands conversational queries
3. **Explore Time References**: Try "today", "this week", "last month"
4. **Check Critical Alerts**: Always review highlighted warnings
5. **Follow Related Topics**: Use suggested next steps
6. **Export Data**: Use the `report_data` field for further analysis

## 💬 Example Use Cases

### Monday Morning Review
```
"Show me incidents this weekend"
"Who is sick today?"
"What's the coverage for today?"
"Show leave requests"
```

### End of Month Analysis
```
"Incidents this month"
"Sickness this month"
"How many staff do we have?"
"Who has low leave balance?"
```

### Quick Check-ins
```
"Coverage tomorrow"
"Any major incidents?"
"Who's off sick?"
```

---

**Need Help?** Ask the AI Assistant: "What can you help me with?"
