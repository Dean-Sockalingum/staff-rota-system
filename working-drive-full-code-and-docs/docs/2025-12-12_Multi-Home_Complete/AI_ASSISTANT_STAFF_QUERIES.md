# AI Assistant - Staff Management Queries

## 🎯 Overview

The AI Assistant chatbot has been enhanced with intelligent staff management capabilities. Management can now ask natural language questions about staff members and get instant, formatted responses.

---

## ✨ New Capabilities

### 1. **Check Leave Balances** 📊

Ask about any staff member's remaining annual leave:

**Example Queries:**
```
• "How much leave does ADMIN001 have?"
• "ADMIN001 leave remaining"
• "Check leave for John Smith"
• "What's Sarah's leave balance?"
```

**Response Includes:**
- Remaining leave (hours and days)
- Full breakdown (total, used, pending, available)
- Urgency level (🔴 High / 🟡 Medium / 🟢 Low)
- Quick action links

**Sample Response:**
```
📊 Leave Balance for John Smith (STAFF001)

Remaining Leave: 150.0 hours (12.9 days)

Full Breakdown:
• Total Entitlement: 297.5 hours
• Used: 147.5 hours
• Pending Approval: 0.0 hours
• Available: 150.0 hours (12.9 days)

Urgency Level: 🟡 MODERATE
⚠️ Staff should book leave soon!

Quick Actions:
• View Staff File
• View Leave History  
• Annual Leave Report
```

---

### 2. **Search for Staff** 🔍

Find staff members by name or SAP ID:

**Example Queries:**
```
• "Search for John"
• "Find staff Smith"
• "Who is ADMIN001?"
• "Locate Sarah Jones"
```

**Response Includes:**
- Staff name and SAP ID
- Role and unit
- Up to 10 matching results

**Sample Response:**
```
🔍 Search Results for 'John':

• John Smith (STAFF001) - SCW, ROSE Unit
• John Williams (STAFF025) - SCA, TULIP Unit
• Johnny Brown (STAFF102) - SSCW, LILY Unit
```

---

### 3. **Open Staff Files** 👤

View detailed staff profiles:

**Example Queries:**
```
• "Open staff file for ADMIN001"
• "Show John Smith's profile"
• "View STAFF001's record"
• "ADMIN001's file"
```

**Response Includes:**
- SAP ID, email, role, unit, team
- Contracted hours
- Quick links to:
  - Full profile (admin)
  - Leave balance checker
  - Shift history
  - Sickness records

**Sample Response:**
```
👤 Staff Profile: John Smith

Basic Information:
• SAP ID: STAFF001
• Email: john.smith@facility.com
• Role: SCW
• Unit: ROSE
• Team: A
• Contracted Hours: 24/week

Quick Links:
• View Full Profile
• Check Leave Balance
• View Shift History
• View Sickness Records

What would you like to know about John?
```

---

## 🚀 How to Use

### **Web Interface**

1. Click the **AI Assistant** button (bottom right of screen)
2. Type your question naturally
3. Get instant formatted response
4. Click suggested related topics or links

### **Example Workflow**

**Scenario:** Manager wants to check if staff member can take leave

```
Manager: "How much leave does STAFF025 have?"
AI: Shows 5.2 days remaining, urgency HIGH

Manager: "Open staff file for STAFF025"
AI: Shows full profile with contact details and links

Manager: "Search for staff in ROSE unit"
AI: Lists all ROSE unit staff members
```

---

## 📝 Supported Query Patterns

### **Leave Balance Queries**

| Pattern | Example |
|---------|---------|
| `How much leave does X have?` | How much leave does ADMIN001 have? |
| `X leave remaining` | STAFF001 leave remaining |
| `Check leave for X` | Check leave for John Smith |
| `X leave balance` | Sarah's leave balance |

### **Search Queries**

| Pattern | Example |
|---------|---------|
| `Search for X` | Search for John |
| `Find staff X` | Find staff Smith |
| `Who is X?` | Who is ADMIN001? |
| `Locate X` | Locate Sarah Jones |

### **Profile Queries**

| Pattern | Example |
|---------|---------|
| `Open staff file for X` | Open staff file for ADMIN001 |
| `Show X's profile` | Show John's profile |
| `View X's record` | View STAFF001's record |
| `X's file` | ADMIN001's file |

---

## 🎨 Response Features

### **Leave Balance Responses**

✅ **Color-coded urgency levels:**
- 🔴 **HIGH**: Less than 5 days remaining
- 🟡 **MEDIUM**: 5-10 days remaining
- 🟢 **LOW**: More than 10 days remaining

✅ **Smart calculations:**
- Accounts for approved and pending leave
- Shows negative pending (rejected/cancelled)
- Converts hours to days correctly
  - 35hr staff: 11.66 hrs/day
  - 24hr staff: 12 hrs/day

✅ **Quick action links:**
- Direct links to staff records
- Leave history
- Annual leave reports

### **Search Responses**

✅ **Flexible matching:**
- Partial name matches
- Case-insensitive
- SAP ID search
- Searches first and last names

✅ **Comprehensive results:**
- Shows up to 10 matches
- Displays role and unit
- Suggests refinement if too many results

### **Profile Responses**

✅ **Complete information:**
- All basic details
- Contact information
- Assignment data

✅ **Integrated links:**
- Admin panel links
- Related queries
- Cross-references

---

## 🔒 Security & Permissions

### **Current Implementation**

- ⚠️ **No authentication required** (API endpoint)
- Anyone can query staff information
- Suitable for internal use only

### **Production Recommendations**

**Add authentication to the API:**

```python
# In views.py
@login_required
@csrf_exempt
def ai_assistant_api(request):
    # Check user permissions
    if not request.user.role.is_management:
        return JsonResponse({
            'error': 'Unauthorized'
        }, status=403)
    
    # ... existing code
```

**Restrict sensitive information:**

```python
# Hide emails for non-managers
if not request.user.role.is_management:
    answer = answer.replace(user.email, '[Hidden]')
```

---

## 🔧 Technical Details

### **Implementation**

**Location:** `scheduling/views.py`  
**Function:** `_process_staff_query(query)`  
**API Endpoint:** `/api/ai-assistant/`  
**Method:** POST

**Query Processing:**
1. Parse natural language query with regex patterns
2. Identify query type (leave/search/profile)
3. Look up staff by SAP or name
4. Retrieve relevant data from models
5. Format response with Markdown
6. Return JSON with answer and related topics

**Models Used:**
- `scheduling.models.User`
- `staff_records.models.StaffProfile`
- `staff_records.models.AnnualLeaveEntitlement`

### **Example API Call**

```javascript
fetch('/api/ai-assistant/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'How much leave does ADMIN001 have?'
    })
})
.then(response => response.json())
.then(data => {
    console.log(data.answer);      // Formatted response
    console.log(data.related);     // Related topics
    console.log(data.category);    // Query category
    console.log(data.data);        // Structured data
});
```

### **Response Structure**

```json
{
    "answer": "**📊 Leave Balance for...**",
    "related": ["Request Leave", "View All Staff"],
    "category": "staff_query",
    "data": {
        "sap": "ADMIN001",
        "name": "John Smith",
        "hours_remaining": 150.0,
        "days_remaining": 12.9
    }
}
```

---

## 📊 Use Cases

### **Daily Management Tasks**

1. **Quick Leave Checks**
   - Before approving leave requests
   - Checking if staff can take time off
   - Planning coverage

2. **Staff Lookup**
   - Finding contact details
   - Checking assignments
   - Verifying roles and units

3. **Record Access**
   - Quick access to full profiles
   - Viewing historical data
   - Checking sickness records

### **Decision Support**

- **Leave Planning:** Check who has leave to use
- **Coverage:** Find available staff in specific units
- **HR Queries:** Quick access to staff information

---

## 🎯 Future Enhancements

### **Planned Features**

- [ ] **Team-wide queries:** "Who in Team A has the most leave?"
- [ ] **Comparative queries:** "Compare leave balances for ROSE unit"
- [ ] **Predictive insights:** "Who needs to book leave soon?"
- [ ] **Bulk operations:** "Show all staff with less than 5 days leave"
- [ ] **Historical data:** "How much leave did X use last year?"
- [ ] **Sickness tracking:** "How many sick days does X have?"
- [ ] **Shift queries:** "When is X working next?"
- [ ] **Contact lookup:** "What's X's phone number?"

### **Advanced Features**

- [ ] Voice input support
- [ ] Export responses to CSV/PDF
- [ ] Email digest of queries
- [ ] Analytics on common questions
- [ ] Machine learning for better understanding
- [ ] Multi-language support

---

## 📚 Related Documentation

- **AI_ASSISTANT_GUIDE.md** - General AI assistant features
- **AI_ASSISTANT_WEB_INTEGRATION.md** - Web interface setup
- **ANNUAL_LEAVE_TRACKING.md** - Leave system documentation
- **STAFF_RECORDS_IMPLEMENTATION.md** - Staff profile details

---

## ✅ Summary

**The AI Assistant now provides:**
- ✅ Instant leave balance checks
- ✅ Smart staff search
- ✅ Quick access to staff profiles
- ✅ Natural language understanding
- ✅ Formatted, actionable responses
- ✅ Related topics and suggestions
- ✅ Direct links to full records

**Perfect for management to:**
- Answer staff questions quickly
- Make informed decisions
- Access information without navigating multiple screens
- Get contextual help and guidance

**Try it now:** Click the AI Assistant button and ask about any staff member! 🚀
