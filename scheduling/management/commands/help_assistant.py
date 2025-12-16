"""
AI Help Assistant - Interactive Chatbot for Staff Rota System

Provides intelligent, context-aware help and guidance for users.
Answers questions about:
- How to perform tasks
- Where to find features
- Troubleshooting issues
- System documentation
- Best practices

Usage:
    python3 manage.py help_assistant
    python3 manage.py help_assistant --query "How do I add a new staff member?"
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import json
from datetime import datetime


class HelpAssistant:
    """AI-powered help assistant with comprehensive knowledge base"""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_history = []
        
    def _load_knowledge_base(self):
        """Load comprehensive knowledge base about the system"""
        return {
            # Quick actions and commands
            'commands': {
                'add_staff': {
                    'question': ['add staff', 'new employee', 'onboard', 'create user', 'add new staff', 'add staff member', 'new staff'],
                    'answer': """
To add a new staff member, you have 3 options:

**1. Quick Onboarding (FASTEST - 5 seconds)**
```bash
python3 manage.py onboard_staff \\
  --sap STAFF001 \\
  --name "Jane Smith" \\
  --role SCW \\
  --unit ROSE \\
  --team A \\
  --hours 35 \\
  --start-date 2025-12-01
```

**2. CSV Bulk Import**
```bash
# Edit quick_onboard_template.csv with your staff
python3 manage.py import_staff_csv quick_onboard_template.csv
```

**3. Admin Panel**
- Go to http://127.0.0.1:8000/admin/scheduling/user/
- Click "Add User" button
- Fill in required fields

See: QUICK_ONBOARDING_GUIDE.md for detailed instructions.
""",
                    'related': ['import_staff', 'staff_management', 'csv_import']
                },
                
                'generate_rota': {
                    'question': ['generate rota', 'create schedule', 'make roster', 'schedule shifts'],
                    'answer': """
To generate rotas/schedules:

**Generate 6-week roster:**
```bash
python3 manage.py generate_six_week_roster \\
  --start-date 2025-12-01 \\
  --weeks 6
```

**Generate supernumerary (management) shifts:**
```bash
python3 manage.py generate_supernumerary_shifts \\
  --start-date 2025-12-01 \\
  --weeks 6
```

**Clear and regenerate:**
```bash
python3 manage.py wipe_roster_data
python3 manage.py generate_six_week_roster --start-date 2025-12-01
```

The system automatically:
- Assigns shifts based on team rotation
- Respects contracted hours
- Follows 3-week patterns
- Balances workload across teams
""",
                    'related': ['shifts', 'scheduling', 'roster_management']
                },
                
                'start_server': {
                    'question': ['start server', 'run application', 'launch system', 'access website'],
                    'answer': """
To start the Staff Rota System:

```bash
cd rotasystems
python3 manage.py runserver
```

Then access:
- **Main Application**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin

To stop the server: Press Ctrl+C

**Run on different port:**
```bash
python3 manage.py runserver 8080
```

**Make accessible on network:**
```bash
python3 manage.py runserver 0.0.0.0:8000
```
""",
                    'related': ['deployment', 'access', 'login']
                },
                
                'setup': {
                    'question': ['first time', 'initial setup', 'getting started', 'installation'],
                    'answer': """
**First-time setup is easy!**

Use the interactive setup wizard:
```bash
cd rotasystems
python3 manage.py setup_wizard
```

This will guide you through:
1. ✓ Creating admin account
2. ✓ Setting up roles and units
3. ✓ Configuring shift types
4. ✓ Importing staff (optional)
5. ✓ Generating initial rotas (optional)

**Quick setup (uses defaults):**
```bash
python3 manage.py setup_wizard --quick
```

See: FIRST_TIME_SETUP.md for detailed instructions.
""",
                    'related': ['wizard', 'configuration', 'admin']
                },
                
                'annual_leave': {
                    'question': ['annual leave', 'holiday', 'vacation', 'time off', 'leave request'],
                    'answer': """
**Annual Leave Management:**

**Request leave (as staff member):**
1. Login to http://127.0.0.1:8000
2. Go to "Annual Leave" section
3. Click "Request Leave"
4. Select dates and submit

**Approve/reject leave (as manager):**
1. Login to admin panel
2. Go to Staff Records → Annual Leave Transactions
3. Find pending requests
4. Approve or reject

**View leave balances:**
```bash
python3 manage.py shell -c "
from staff_records.models import AnnualLeaveEntitlement
for ent in AnnualLeaveEntitlement.objects.all()[:5]:
    print(f'{ent.profile.user.sap}: {ent.hours_remaining} hrs remaining')
"
```

**Entitlements:**
- 35hr staff: 297.5 hours (~25.5 days)
- 24hr staff: 204 hours (17 days)
- Pro-rated for mid-year starters

See: docs/staff_guidance/ANNUAL_LEAVE_GUIDE.md
""",
                    'related': ['leave_balance', 'entitlement', 'time_off']
                },
                
                'additional_staffing': {
                    'question': ['overtime', 'agency staff', 'additional staffing', 'agency company', 'agency shift', 'ot', 'add agency', 'track agency'],
                    'answer': """
**Additional Staffing Management (Overtime & Agency):**

**Add overtime shift:**
1. Go to Rota View: http://127.0.0.1:8000/rota-view/
2. Click "Add Shift" button
3. Select staff member
4. Classification: Choose "Overtime"
5. Shift Pattern: 08:00-20:00 OR 20:00-08:00 OR Custom
6. Submit

**Add agency staff shift:**
1. Go to Rota View
2. Click "Add Shift"
3. Classification: Choose "Agency Staff"
4. Select Agency Company (dropdown auto-loads 8 agencies)
5. Enter agency staff name
6. Hourly rate auto-fills (or edit if needed)
7. Submit

**Available Agencies:**
- ABC Healthcare Ltd (Day: £42, Night: £47.50)
- Care Response (Day: £42.50, Night: £48)
- CarePro Staffing Solutions (Day: £38.50, Night: £43)
- Elite Care Professionals (Day: £45, Night: £50)
- Newcross (Day: £39.50, Night: £44.50)
- REED (Day: £41, Night: £46)
- Rapid Response Healthcare (Day: £40, Night: £45)
- Staffscanner (Day: £40, Night: £45)

**View Reports:**

Daily report:
```bash
http://127.0.0.1:8000/api/reports/daily-additional-staffing/?date=2025-12-03
```

Weekly report (manual):
```bash
python3 manage.py send_weekly_staffing_report --dry-run
```

**Automated Weekly Reports:**
- Runs every Monday at 8:00 AM
- Covers previous week (Sunday-Saturday)
- Sent to all managers via email
- Shows OT hours, agency usage, costs by company
- Check logs: logs/weekly_staffing_report.log

**Shift Patterns:**
- Day (08:00-20:00): 12 hours
- Night (20:00-08:00): 12 hours
- Custom: Enter specific times (e.g., 10:00-18:00)

See: ADDITIONAL_STAFFING_COMPLETE.md for full documentation
""",
                    'related': ['add_shift', 'agency_reports', 'overtime_tracking', 'weekly_reports']
                },
                
                'care_plan_reviews': {
                    'question': ['care plan', 'review due', 'resident review', 'when is review', 'care plan review', 'review status', 'compliance review', 'overdue review'],
                    'answer': """
**Care Plan Review Management:**

**Check when a resident's review is due:**
Ask me: "When is [resident ID]'s review due?" or "Show review for [resident ID]"
Example: "When is DEM01's review due?"

**View all reviews:**
- Overview: http://127.0.0.1:8000/careplan/
- By Unit: http://127.0.0.1:8000/careplan/unit/DEMENTIA/
- Filter by status (Completed, Overdue, Due Soon, Upcoming)

**Complete a review:**
1. Go to unit view: http://127.0.0.1:8000/careplan/unit/[UNIT_NAME]/
2. Click "Complete Review" on resident card
3. Fill in:
   - Care Needs Assessment
   - Goals & Progress
   - Changes Required
   - Family Involvement
4. Save as Draft OR Submit for Approval
5. Manager approves → Next 6-month review auto-generated

**Review Schedule:**
- New residents: 4 weeks after admission
- Existing residents: Every 6 months
- Auto-scheduled when previous review completed

**Generate compliance reports:**
Go to: http://127.0.0.1:8000/careplan/reports/
- Select date range
- Shows: completed vs overdue, on-time %, compliance rate
- Export to PDF/Excel

**Management Commands:**
```bash
# Ensure all residents have scheduled reviews
python3 manage.py generate_careplan_reviews

# View review statistics
python3 manage.py careplan_stats
```

**Current System Status:**
- 120 residents tracked
- 8 units (DEMENTIA, BLUE, ORANGE, GREEN, VIOLET, ROSE, GRAPE, PEACH)
- Auto-generates next review on completion
- Tracks overdue days for compliance

See: CAREPLAN_REVIEW_IMPLEMENTATION.md for full documentation
""",
                    'related': ['view_residents', 'compliance_reports', 'review_approval', 'manager_dashboard']
                },
                
                'view_rota': {
                    'question': ['view rota', 'see schedule', 'check shifts', 'my rota'],
                    'answer': """
**View the rota/schedule:**

**As staff member:**
1. Login at http://127.0.0.1:8000
2. Dashboard shows your upcoming shifts
3. Click "Full Rota" to see complete schedule

**As manager/admin:**
1. Login to admin panel
2. Go to Scheduling → Shifts
3. Filter by date, unit, team, or staff member

**Command line:**
```bash
python3 manage.py shell -c "
from scheduling.models import Shift
from datetime import date, timedelta

today = date.today()
week_end = today + timedelta(days=7)

shifts = Shift.objects.filter(
    date__gte=today,
    date__lte=week_end
).select_related('user', 'shift_type', 'unit')

for shift in shifts:
    print(f'{shift.date} - {shift.user.full_name} - {shift.shift_type.name}')
"
```
""",
                    'related': ['shifts', 'schedule', 'roster']
                },
                
                'backup': {
                    'question': ['backup', 'save data', 'export database', 'disaster recovery'],
                    'answer': """
**Create a backup:**

**Database backup:**
```bash
cd rotasystems
python3 manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
```

**SQLite database copy:**
```bash
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
```

**Restore from backup:**
```bash
# JSON backup
python3 manage.py loaddata backup_20251128.json

# SQLite backup
cp db_backup_20251128.sqlite3 db.sqlite3
```

**Automated daily backups:**
See: BACKUP_INSTRUCTIONS.md for automated backup setup.

**What's backed up:**
- All staff records
- Shift schedules
- Annual leave data
- User accounts
- System configuration
""",
                    'related': ['restore', 'disaster_recovery', 'data_export']
                },
            },
            
            # Where to find things
            'locations': {
                'admin_panel': {
                    'question': ['admin panel', 'where is admin', 'management interface'],
                    'answer': """
**Admin Panel Location:**
http://127.0.0.1:8000/admin

**Login with:**
- Username: Your SAP ID (e.g., ADMIN001)
- Password: Your admin password

**Main sections:**
- Scheduling: Shifts, Users, Roles, Units, Shift Types
- Staff Records: Staff Profiles, Annual Leave, Medical Certificates
- Leave Management: Leave Requests, Transactions

**First time?** Create admin account:
```bash
python3 manage.py createsuperuser
```
Or use the setup wizard:
```bash
python3 manage.py setup_wizard
```
""",
                    'related': ['login', 'access', 'permissions']
                },
                
                'documentation': {
                    'question': ['documentation', 'guides', 'manuals', 'help files'],
                    'answer': """
**Documentation Files:**

**Setup & Configuration:**
- FIRST_TIME_SETUP.md - Initial setup guide
- SETUP_WIZARD_GUIDE.md - Visual setup walkthrough
- SETUP_REFERENCE.md - Quick reference card
- CUSTOMIZATION_GUIDE.md - Customization options

**Staff Management:**
- QUICK_ONBOARDING_GUIDE.md - Add staff quickly
- STAFF_IMPORT_GUIDE.md - Bulk CSV import
- STAFF_IMPORT_COMPLETE.md - Import summary

**Operations:**
- PRODUCTION_DEPLOYMENT.md - Deploy to production
- BACKUP_INSTRUCTIONS.md - Backup procedures
- EMAIL_SETUP_GUIDE.md - Email configuration

**For Staff:**
- docs/staff_guidance/ANNUAL_LEAVE_GUIDE.md
- docs/staff_guidance/SICKNESS_REPORTING_GUIDE.md
- docs/staff_guidance/STAFF_FAQ.md

**For Managers:**
- docs/staff_guidance/MANAGERS_ATTENDANCE_GUIDE.md
- docs/staff_guidance/MANAGER_RESOURCES_INDEX.md

View any file:
```bash
cat FIRST_TIME_SETUP.md
```
""",
                    'related': ['help', 'guides', 'reference']
                },
                
                'logs': {
                    'question': ['logs', 'errors', 'debug', 'troubleshooting'],
                    'answer': """
**System Logs:**

**Django development server logs:**
- Displayed in terminal where you ran `python3 manage.py runserver`

**Check for errors:**
```bash
python3 manage.py check
```

**View database queries (debug mode):**
```bash
python3 manage.py shell
>>> from django.db import connection
>>> print(connection.queries)
```

**Common log locations:**
- Development: Terminal output
- Production: /var/log/nginx/ and /var/log/gunicorn/

**Enable debug mode:**
Edit `rotasystems/settings.py`:
```python
DEBUG = True
```
(⚠️ Never use DEBUG=True in production!)
""",
                    'related': ['errors', 'debugging', 'troubleshooting']
                },
            },
            
            # Troubleshooting
            'troubleshooting': {
                'database_locked': {
                    'question': ['database locked', 'database is locked', 'sqlite busy'],
                    'answer': """
**Database Locked Error - Quick Fix:**

```bash
# 1. Stop the server
pkill -f "python3 manage.py runserver"

# 2. Wait 2 seconds
sleep 2

# 3. Try again
python3 manage.py runserver
```

**If still locked:**
```bash
# Check what's using the database
lsof db.sqlite3

# Kill the process (replace PID with actual process ID)
kill -9 <PID>
```

**Prevent in future:**
- Don't run multiple servers simultaneously
- Close database connections properly
- Consider PostgreSQL for production (no lock issues)

**Switch to PostgreSQL (production):**
See: PRODUCTION_DEPLOYMENT.md
""",
                    'related': ['errors', 'database', 'sqlite']
                },
                
                'import_errors': {
                    'question': ['module not found', 'import error', 'no module named'],
                    'answer': """
**Import/Module Not Found Errors:**

**Most common cause:** Missing dependencies

**Fix:**
```bash
pip3 install -r requirements.txt
```

**If that doesn't work:**
```bash
# Update pip
pip3 install --upgrade pip

# Install Django
pip3 install django

# Install all requirements individually
pip3 install django pillow python-dateutil reportlab
```

**Check what's installed:**
```bash
pip3 list
```

**Virtual environment issues:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# or
venv\\Scripts\\activate  # Windows

# Install requirements
pip install -r requirements.txt
```
""",
                    'related': ['dependencies', 'installation', 'python']
                },
                
                'permission_denied': {
                    'question': ['permission denied', 'access denied', 'forbidden', '403 error'],
                    'answer': """
**Permission Denied Errors:**

**Admin panel access:**
1. Ensure you have superuser account:
```bash
python3 manage.py createsuperuser
```

2. Or make existing user superuser:
```bash
python3 manage.py shell -c "
from scheduling.models import User
user = User.objects.get(sap='YOUR_SAP_ID')
user.is_superuser = True
user.is_staff = True
user.save()
"
```

**File permission errors:**
```bash
# Fix database file permissions
chmod 644 db.sqlite3

# Fix directory permissions
chmod 755 rotasystems
```

**Still having issues?**
Check user's permissions in admin panel:
http://127.0.0.1:8000/admin/scheduling/user/
""",
                    'related': ['access', 'permissions', 'admin']
                },
            },
            
            # Configuration
            'configuration': {
                'shift_times': {
                    'question': ['change shift times', 'modify shift hours', 'adjust shift'],
                    'answer': """
**Change Shift Times:**

**Via Admin Panel:**
1. Go to http://127.0.0.1:8000/admin/scheduling/shifttype/
2. Click on shift type (e.g., DAY_SENIOR)
3. Modify start_time and end_time
4. Click Save

**Via Command Line:**
```bash
python3 manage.py shell -c "
from scheduling.models import ShiftType
from datetime import time

# Change day shift to 07:00-19:00
day_shift = ShiftType.objects.get(name='DAY_SENIOR')
day_shift.start_time = time(7, 0)
day_shift.end_time = time(19, 0)
day_shift.hours = 12
day_shift.save()

print(f'Updated: {day_shift.name} now {day_shift.start_time}-{day_shift.end_time}')
"
```

**Create new shift type:**
See: CUSTOMIZATION_GUIDE.md section on "Adding Custom Shift Types"
""",
                    'related': ['shifts', 'customization', 'configuration']
                },
                
                'team_assignment': {
                    'question': ['change team', 'assign team', 'move staff to team'],
                    'answer': """
**Assign Staff to Teams:**

**Single staff member:**
```bash
python3 manage.py shell -c "
from scheduling.models import User

staff = User.objects.get(sap='STAFF001')
staff.team = 'B'  # Team A, B, or C
staff.save()
print(f'{staff.full_name} moved to Team {staff.team}')
"
```

**Bulk reassignment:**
```bash
python3 manage.py shell -c "
from scheduling.models import User

# Move all Team A to Team B
moved = User.objects.filter(team='A').update(team='B')
print(f'Moved {moved} staff members to Team B')
"
```

**Via Admin Panel:**
1. Go to http://127.0.0.1:8000/admin/scheduling/user/
2. Find staff member
3. Edit and change 'Team' field
4. Save

**Teams in the system:**
- Team A: Works specific rotation days
- Team B: Works specific rotation days
- Team C: Works specific rotation days
(3-week rotating pattern)
""",
                    'related': ['staff', 'teams', 'assignment']
                },
            },
        }
    
    def find_answer(self, query):
        """Find the best answer for the user's question"""
        query_lower = query.lower()
        
        # Search through all categories
        for category, items in self.knowledge_base.items():
            for key, data in items.items():
                # Check if query matches any question patterns
                for pattern in data.get('question', []):
                    if pattern in query_lower:
                        return {
                            'answer': data['answer'].strip(),
                            'related': data.get('related', []),
                            'category': category
                        }
        
        # No match found
        return None
    
    def get_related_topics(self, topic_keys):
        """Get related topic suggestions"""
        suggestions = []
        for category, items in self.knowledge_base.items():
            for key, data in items.items():
                if key in topic_keys:
                    suggestions.append({
                        'topic': key.replace('_', ' ').title(),
                        'description': data['question'][0]
                    })
        return suggestions


class Command(BaseCommand):
    help = 'Interactive AI help assistant for the Staff Rota System'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            help='Ask a specific question (non-interactive mode)'
        )
        parser.add_argument(
            '--list-topics',
            action='store_true',
            help='List all available help topics'
        )
    
    def handle(self, *args, **options):
        assistant = HelpAssistant()
        
        # List topics mode
        if options.get('list_topics'):
            self.list_all_topics(assistant)
            return
        
        # Single query mode
        if options.get('query'):
            self.answer_query(assistant, options['query'])
            return
        
        # Interactive mode
        self.interactive_mode(assistant)
    
    def list_all_topics(self, assistant):
        """List all available help topics"""
        self.stdout.write(self.style.SUCCESS('\n📚 Available Help Topics:\n'))
        
        for category, items in assistant.knowledge_base.items():
            self.stdout.write(self.style.HTTP_INFO(f'\n{category.upper().replace("_", " ")}:'))
            for key, data in items.items():
                topic = key.replace('_', ' ').title()
                keywords = ', '.join(data['question'][:2])
                self.stdout.write(f'  • {topic}')
                self.stdout.write(f'    Keywords: {keywords}')
        
        self.stdout.write(self.style.SUCCESS('\n\nTo get help on any topic, ask:'))
        self.stdout.write('  python3 manage.py help_assistant --query "your question"')
        self.stdout.write('  python3 manage.py help_assistant  (for interactive mode)\n')
    
    def answer_query(self, assistant, query):
        """Answer a single query and exit"""
        result = assistant.find_answer(query)
        
        if result:
            self.stdout.write(self.style.SUCCESS(f'\n📖 Answer:\n'))
            self.stdout.write(result['answer'])
            
            if result.get('related'):
                self.stdout.write(self.style.HTTP_INFO('\n\n🔗 Related topics:'))
                related = assistant.get_related_topics(result['related'])
                for topic in related:
                    self.stdout.write(f"  • {topic['topic']}")
        else:
            self.suggest_alternatives(query)
    
    def interactive_mode(self, assistant):
        """Start interactive chat session"""
        self.print_welcome()
        
        while True:
            try:
                # Get user input
                self.stdout.write('')  # Blank line
                query = input('💬 You: ').strip()
                
                if not query:
                    continue
                
                # Check for exit commands
                if query.lower() in ['exit', 'quit', 'bye', 'q']:
                    self.stdout.write(self.style.SUCCESS('\n👋 Goodbye! Happy scheduling!\n'))
                    break
                
                # Check for help
                if query.lower() in ['help', 'topics', 'list']:
                    self.list_all_topics(assistant)
                    continue
                
                # Find answer
                self.stdout.write('')  # Blank line
                result = assistant.find_answer(query)
                
                if result:
                    self.stdout.write(self.style.SUCCESS('🤖 Assistant:'))
                    self.stdout.write(result['answer'])
                    
                    if result.get('related'):
                        self.stdout.write(self.style.HTTP_INFO('\n🔗 You might also want to know about:'))
                        related = assistant.get_related_topics(result['related'])
                        for i, topic in enumerate(related, 1):
                            self.stdout.write(f"  {i}. {topic['topic']}")
                else:
                    self.suggest_alternatives(query)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('\n\n👋 Goodbye! Happy scheduling!\n'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
    
    def print_welcome(self):
        """Print welcome message"""
        welcome = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          🤖 STAFF ROTA ASSISTANT - AI HELP SYSTEM 🤖         ║
║                                                               ║
║  I'm your interactive help assistant! Ask me anything about: ║
║                                                               ║
║    • How to add staff or generate rotas                      ║
║    • Where to find features or settings                      ║
║    • Troubleshooting errors or issues                        ║
║    • Configuration and customization                         ║
║    • Best practices and tips                                 ║
║                                                               ║
║  Type 'help' to see all topics, 'exit' to quit              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        self.stdout.write(self.style.SUCCESS(welcome))
        
        # Show example questions
        self.stdout.write(self.style.HTTP_INFO('💡 Example questions you can ask:\n'))
        examples = [
            "How do I add a new staff member?",
            "Where is the admin panel?",
            "How do I generate a rota?",
            "Database is locked, what do I do?",
            "How do I change shift times?",
            "Where are the documentation files?",
        ]
        for example in examples:
            self.stdout.write(f'  • "{example}"')
    
    def suggest_alternatives(self, query):
        """Suggest alternatives when no match is found"""
        self.stdout.write(self.style.WARNING('\n🤔 I don\'t have a specific answer for that.'))
        self.stdout.write('\n💡 Here are some things I can help with:\n')
        
        suggestions = [
            "Adding or importing staff members",
            "Generating and managing rotas",
            "Setting up the system for first time",
            "Managing annual leave and time off",
            "Troubleshooting common errors",
            "Customizing shifts and teams",
            "Backup and restore procedures",
            "Accessing admin panel and documentation",
        ]
        
        for suggestion in suggestions:
            self.stdout.write(f'  • {suggestion}')
        
        self.stdout.write(self.style.HTTP_INFO('\n📚 Type "help" to see all available topics.'))
        self.stdout.write('Or try rephrasing your question with keywords like:')
        self.stdout.write('  "how to...", "where is...", "fix...", "change..."')
