# Staff Rota System - Complete Feature Index
## Comprehensive Guide for Stakeholders

**Last Updated:** December 3, 2025  
**Version:** 2.0  
**System:** Django 5.2.7 | Python 3.14.0

---

## 📋 Table of Contents

1. [Core Scheduling & Rota Management](#core-scheduling--rota-management)
2. [Staff Management & Records](#staff-management--records)
3. [Annual Leave System](#annual-leave-system)
4. [Additional Staffing (Overtime & Agency)](#additional-staffing-overtime--agency)
5. [Care Plan Review System](#care-plan-review-system)
6. [Care Inspectorate Compliance](#care-inspectorate-compliance)
7. [Reporting & Analytics](#reporting--analytics)
8. [AI Assistant](#ai-assistant)
9. [Audit & Data Security](#audit--data-security)
10. [Management Commands](#management-commands)
11. [Integration & Automation](#integration--automation)

---

## 🗓️ Core Scheduling & Rota Management

### Shift Management
- **Create Shifts**: Add regular, overtime, and agency shifts
- **Edit Shifts**: Modify existing shift details (time, staff, unit)
- **Delete Shifts**: Remove shifts with audit trail
- **Shift Patterns**: Day (08:00-20:00), Night (20:00-08:00), Custom times
- **Shift Types**: Regular, Overtime, Agency Staff, Training, Leave
- **Multi-Unit Support**: 8 units (DEMENTIA, BLUE, ORANGE, GREEN, VIOLET, ROSE, GRAPE, PEACH)

### Rota Viewing
- **Calendar View**: Visual weekly/monthly rota display
- **Staff View**: Individual staff member's schedule
- **Unit View**: All staff in a specific unit
- **Team View**: Team A/B shift assignments
- **Print Rota**: Export to PDF/print
- **Mobile Responsive**: View on tablets/phones

### Shift Management Features
- **Shift Swaps**: Request and approve shift swaps between staff
- **Staff Reallocation**: Move staff between units temporarily
- **Shift Coverage Analysis**: Identify gaps and overstaffing
- **Shift Conflicts**: Automatic detection of double-booking
- **Team Assignment**: Assign staff to Team A or Team B

**Access Points:**
- Rota View: `http://127.0.0.1:8000/rota-view/`
- Add Shift: `http://127.0.0.1:8000/add-shift/`
- Edit Shift: `http://127.0.0.1:8000/edit-shift/`

---

## 👥 Staff Management & Records

### Staff Onboarding
- **Quick Onboarding**: 5-second staff creation via command
- **Bulk Import**: Import multiple staff from CSV
- **Staff Profiles**: Complete employee records with photos
- **Role Assignment**: 8 roles (SSCW, SSCWN, SCW, SCWA, ADMIN, MANAGER, SUPPORT, TEMP)
- **Unit Assignment**: Primary unit allocation
- **Team Assignment**: Team A/B allocation
- **Contract Hours**: Track full-time/part-time hours

### Staff Records
- **Personal Information**: Contact details, emergency contacts
- **Sickness Records**: Track absence with return-to-work interviews
- **Training Records**: Mandatory and optional training tracking
- **Supervision Records**: 1-to-1 supervision documentation
- **Induction Progress**: New starter induction checklist
- **DBS & Certifications**: Document expiry tracking
- **Performance Reviews**: Annual appraisal records

### Staff Search & Management
- **Search by Name**: Find staff quickly
- **Search by SAP**: Lookup by employee ID
- **Search by Unit**: View all staff in unit
- **Search by Role**: Filter by job role
- **Active/Inactive**: Toggle staff status
- **Staff Dashboard**: Individual staff view with all records

**Access Points:**
- Staff Management: `http://127.0.0.1:8000/staff-management/`
- Add Staff: `http://127.0.0.1:8000/add-staff/`
- Staff Profile: `http://127.0.0.1:8000/staff-records/{SAP}/`
- Quick Onboarding Command: `python3 manage.py onboard_staff`

---

## 🏖️ Annual Leave System

### Leave Management
- **Request Leave**: Staff submit leave requests
- **Manager Approval**: Multi-level approval workflow
- **Leave Balance**: Real-time hours/days remaining
- **Leave Calendar**: Visual leave planner
- **Leave Clashes**: Automatic clash detection
- **Leave History**: View past leave taken
- **Leave Cancellation**: Cancel approved leave with workflow

### Leave Entitlements
- **Automatic Calculation**: Based on contract hours and start date
- **Pro-Rata Calculation**: For mid-year starters
- **Carry Over**: Handle unused leave from previous year
- **Leave Year**: April 1st - March 31st cycle
- **Multiple Leave Types**: Annual, Sick, Compassionate, Study

### Leave Reporting
- **Individual Balance**: Check staff member's leave
- **Team Leave Report**: View all staff leave balances
- **Low Balance Alerts**: Identify staff who need to use leave
- **Leave Usage Targets**: Track against expected usage by date
- **Annual Leave Report**: Comprehensive year-end report
- **Export to Excel**: Download leave data

### Leave Usage Targets (NEW)
- **Target Tracking**: Monitor leave usage against expected rate
- **Visual Dashboard**: Red/Amber/Green status indicators
- **Week-by-Week Analysis**: Compare actual vs expected usage
- **Team Overview**: See all staff at a glance
- **Filter by Unit**: View specific unit's performance
- **Variance Tracking**: Days ahead/behind schedule

**Access Points:**
- Request Leave: `http://127.0.0.1:8000/request-leave/`
- Leave Approvals: `http://127.0.0.1:8000/leave-approvals/`
- Leave Report: `http://127.0.0.1:8000/reports/annual-leave/`
- Leave Usage Targets: `http://127.0.0.1:8000/reports/leave-targets/`

---

## 💼 Additional Staffing (Overtime & Agency)

### Overtime Management
- **Overtime Shifts**: Track additional hours worked
- **Overtime Rates**: Configurable pay rates
- **Overtime Approval**: Manager authorization
- **Overtime Reports**: Daily/weekly summaries
- **Staff Overtime History**: Individual tracking

### Agency Staff Management
- **8 Agency Companies**: Pre-configured suppliers
  - ABC Healthcare Ltd (£42/£47.50)
  - Care Response (£42.50/£48)
  - CarePro Staffing Solutions (£38.50/£43)
  - Elite Care Professionals (£45/£50)
  - Newcross (£39.50/£44.50)
  - REED (£41/£46)
  - Rapid Response Healthcare (£40/£45)
  - Staffscanner (£40/£45)
- **Agency Shift Tracking**: Record agency staff usage
- **Automatic Rate Calculation**: Day/night rates auto-fill
- **Agency Cost Tracking**: Monitor spending per company
- **Agency Staff Names**: Track individual agency workers

### Additional Staffing Reports
- **Daily Report**: View single day's overtime and agency usage
- **Weekly Report**: Automated Monday morning report
- **Cost Analysis**: Breakdown by company and shift type
- **Email Notifications**: Automated reports to managers
- **API Endpoints**: Integration-ready data access

**Access Points:**
- Add Overtime: `http://127.0.0.1:8000/rota-view/` → Add Shift → Overtime
- Add Agency: `http://127.0.0.1:8000/rota-view/` → Add Shift → Agency
- Daily Report: `http://127.0.0.1:8000/api/reports/daily-additional-staffing/`
- Weekly Report Command: `python3 manage.py send_weekly_staffing_report`

---

## 🏥 Care Plan Review System

### Resident Management
- **120 Residents**: Track all residents across 8 units
- **Resident Profiles**: Personal information, admission dates
- **Room Assignments**: 15 rooms per unit
- **Keyworker Assignment**: Dedicated care staff
- **Unit Manager Oversight**: SSCW/SSCWN supervision
- **Resident IDs**: Auto-generated (DEM01, BLU15, etc.)
- **Discharge Tracking**: Record discharge dates and reasons

### Care Plan Reviews
- **Review Types**:
  - Initial Review (4 weeks after admission)
  - 6-Monthly Reviews (ongoing)
  - Unscheduled Reviews (ad-hoc)
- **Review Workflow**:
  - Upcoming → Due Soon → Overdue
  - In Progress → Pending Approval → Completed
- **Auto-Scheduling**: Next review auto-generated on completion
- **Review Forms**: Structured sections for documentation
- **Manager Approval**: Required before completion
- **Document Upload**: Attach supporting documents

### Review Content Sections
- **Care Needs Assessment**: Current care requirements
- **Goals & Progress**: Progress towards care objectives
- **Changes Required**: Modifications to care plan
- **Family Involvement**: Family contact and input

### Review Monitoring
- **Color-Coded Status**: Visual indicators (Green/Yellow/Red)
- **Days Overdue Tracking**: Automatic calculation
- **Compliance Flags**: Identify non-compliant reviews
- **Alert System**: Notifications for upcoming/overdue reviews
- **Unit Dashboard**: See all residents in a unit
- **Overview Dashboard**: Organization-wide view

### Review Reports
- **Compliance Report**: On-time vs overdue analysis
- **Date Range Selection**: Custom reporting periods
- **Unit Filtering**: Unit-specific compliance
- **Export Options**: Print/PDF export
- **Performance Metrics**: Average days late, completion rates

**Access Points:**
- Care Plan Overview: `http://127.0.0.1:8000/careplan/`
- Unit View: `http://127.0.0.1:8000/careplan/unit/{UNIT}/`
- Complete Review: `http://127.0.0.1:8000/careplan/review/{ID}/`
- Compliance Report: `http://127.0.0.1:8000/careplan/reports/`
- Generate Reviews: `python3 manage.py generate_careplan_reviews`

---

## 📊 Care Inspectorate Compliance

### Training Matrix
- **Mandatory Training**: Track required training courses
- **Training Expiry**: Automatic expiry date tracking
- **Training Records**: Upload certificates
- **Training Reports**: Organization-wide compliance view
- **Training Gaps**: Identify missing training
- **Email Reminders**: Automatic expiry notifications

### Supervision Records
- **1-to-1 Supervision**: Regular staff supervision tracking
- **Supervision Frequency**: Monthly/quarterly tracking
- **Digital Signatures**: Electronic sign-off by both parties
- **Supervision Templates**: Structured discussion points
- **Supervision Reports**: Compliance monitoring
- **Overdue Supervision Alerts**: Identify missed sessions

### Induction Checklists
- **New Starter Induction**: 12-week induction program
- **Progress Tracking**: Weekly milestone monitoring
- **Manager Sign-Off**: Approval workflow
- **Induction Reports**: View all new starters
- **Completion Status**: Visual progress indicators

### Incident Reporting
- **Incident Types**: Falls, medication errors, behavioral, safeguarding, death
- **Severity Levels**: Low, medium, high
- **Care Inspectorate Notification**: Flag for reporting requirement
- **Incident Investigation**: Track investigation progress
- **Incident Reports**: Management oversight
- **Reference Numbers**: Auto-generated tracking

**Access Points:**
- Training Dashboard: `http://127.0.0.1:8000/compliance/training/`
- Supervision Records: `http://127.0.0.1:8000/compliance/supervision/`
- Induction Progress: `http://127.0.0.1:8000/compliance/induction/`
- Report Incident: `http://127.0.0.1:8000/compliance/incident/report/`

---

## 📈 Reporting & Analytics

### Dashboard Reports
- **Manager Dashboard**: Key metrics and alerts
- **Staff Dashboard**: Personal overview for staff
- **Unit Dashboard**: Unit-specific performance
- **Reports Dashboard**: Central reporting hub

### Operational Reports
- **Shift Coverage Report**: Identify gaps in coverage
- **Staff Hours Report**: Total hours by staff/unit/period
- **Overtime Analysis**: Overtime usage and costs
- **Agency Usage Report**: Agency spending analysis
- **Sickness Report**: Absence tracking and trends

### Compliance Reports
- **Annual Leave Report**: Leave balances and usage
- **Leave Usage Targets**: Progress tracking
- **Training Compliance**: Training matrix status
- **Supervision Compliance**: 1-to-1 completion rates
- **Care Plan Compliance**: Review completion status
- **Incident Reports**: Incident tracking and trends

### Export Options
- **PDF Export**: Professional formatted reports
- **Excel Export**: Data for further analysis
- **Print**: Direct printing capability
- **Email Reports**: Automated distribution
- **API Access**: Integration with other systems

**Access Points:**
- Reports Dashboard: `http://127.0.0.1:8000/reports-dashboard/`
- Manager Dashboard: `http://127.0.0.1:8000/manager-dashboard/`

---

## 🤖 AI Assistant

### Conversational Help
- **Natural Language Queries**: Ask questions in plain English
- **Context-Aware Responses**: Understands user intent
- **Quick Answers**: Instant help without searching documentation
- **Step-by-Step Guidance**: Detailed instructions for tasks
- **Related Topics**: Suggestions for further reading

### Knowledge Areas
- **Staff Queries**: "How much leave does ADMIN001 have?"
- **Care Plan Queries**: "When is DEM01 review due?"
- **System Navigation**: "How do I add a new staff member?"
- **Report Generation**: "Show me shift coverage report"
- **Troubleshooting**: "Why can't I approve this leave request?"
- **Best Practices**: "What's the best way to handle overtime?"

### Supported Query Types
- **Staff Leave Balance**: Check individual leave remaining
- **Resident Review Status**: Check care plan review dates
- **How-To Questions**: Learn system procedures
- **Quick Actions**: Direct links to relevant pages
- **System Status**: Current statistics and metrics

### AI Features
- **Smart Search**: Finds relevant documentation
- **Learning System**: Improves over time
- **Multi-Topic Coverage**: 20+ help topics
- **Example Queries**: Suggests common questions
- **Interactive Chat**: Conversational interface

**Access Points:**
- AI Assistant: Available on all pages with chat icon
- API Endpoint: `http://127.0.0.1:8000/api/ai-assistant/`
- Command Line: `python3 manage.py help_assistant`

---

## 🔒 Audit & Data Security

### Audit Trail
- **Data Change Log**: Track all data modifications
- **User Actions**: Who changed what and when
- **Before/After Values**: See what was changed
- **IP Address Logging**: Security tracking
- **Compliance Violations**: Automatic flagging
- **Searchable Logs**: Find specific changes

### System Access Logs
- **Login Tracking**: All login attempts
- **Session Management**: Active user sessions
- **Access Attempts**: Failed login monitoring
- **User Activity**: Page views and actions
- **Security Events**: Suspicious activity alerts

### Data Protection
- **Password Encryption**: Secure password storage
- **Role-Based Access**: Permissions by job role
- **Data Encryption**: Sensitive data protection
- **Backup System**: Regular automated backups
- **GDPR Compliance**: Data protection compliance
- **Audit Reports**: Compliance documentation

### Compliance Violations
- **Automatic Detection**: Rule-based violation flagging
- **Violation Types**: Leave, shift, training compliance
- **Severity Levels**: Low, medium, high, critical
- **Resolution Tracking**: Track violation resolution
- **Compliance Reports**: Management oversight

**Access Points:**
- Audit Dashboard: `http://127.0.0.1:8000/audit/`
- Data Change Log: `http://127.0.0.1:8000/audit/data-changes/`
- Access Logs: `http://127.0.0.1:8000/audit/access-logs/`
- Violations: `http://127.0.0.1:8000/audit/violations/`

---

## ⚙️ Management Commands

### Staff Management Commands
```bash
# Quick staff onboarding
python3 manage.py onboard_staff --sap STAFF001 --name "Jane Smith" --role SCW --unit ROSE

# Import multiple staff from CSV
python3 manage.py import_staff staff_data.csv

# Fix duplicate names
python3 manage.py fix_duplicate_names

# Restructure staff records
python3 manage.py restructure_staff
```

### Care Plan Commands
```bash
# Generate review schedules for all residents
python3 manage.py generate_careplan_reviews

# Import resident and review data
python3 manage.py import_careplan_data careplan_data.csv

# Update review statuses (run daily)
python3 manage.py update_careplan_status
```

### Reporting Commands
```bash
# Send weekly staffing report (automated)
python3 manage.py send_weekly_staffing_report

# Generate annual leave report
python3 manage.py annual_leave_report --year 2025

# Care plan statistics
python3 manage.py careplan_stats
```

### System Maintenance Commands
```bash
# Database check
python3 manage.py check

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Collect static files
python3 manage.py collectstatic
```

### Help & Documentation
```bash
# Interactive AI assistant
python3 manage.py help_assistant

# Show all available commands
python3 manage.py help
```

---

## 🔄 Integration & Automation

### Automated Processes
- **Weekly Staffing Report**: Runs every Monday 8:00 AM
- **Leave Balance Calculations**: Real-time updates
- **Review Status Updates**: Daily automatic updates
- **Training Expiry Alerts**: Weekly checks
- **Supervision Reminders**: Monthly notifications

### API Endpoints
- **Agency Companies API**: `/api/agency-companies/`
- **Daily Staffing Report API**: `/api/reports/daily-additional-staffing/`
- **Weekly Staffing Report API**: `/api/reports/weekly-additional-staffing/`
- **AI Assistant API**: `/api/ai-assistant/`

### Email Notifications
- **Leave Request Notifications**: To managers
- **Leave Approval Notifications**: To staff
- **Weekly Staffing Reports**: To all managers
- **Training Expiry Alerts**: To staff and managers
- **Overdue Review Alerts**: To keyworkers and managers

### Scheduled Tasks (Cron)
- **Weekly Reports**: Monday 8:00 AM
- **Daily Status Updates**: Daily 8:00 AM
- **Backup Tasks**: Daily 2:00 AM
- **Email Queues**: Every 15 minutes

### Data Import/Export
- **CSV Import**: Staff, residents, reviews
- **Excel Export**: Reports and data
- **PDF Export**: Professional documents
- **Backup/Restore**: Full system backup

---

## 📱 User Interfaces

### Staff Portal
- **Personal Dashboard**: View own shifts and leave
- **Request Leave**: Submit leave requests
- **View Rota**: See personal schedule
- **Training Records**: View own training
- **Update Profile**: Manage personal details

### Manager Portal
- **Manager Dashboard**: Key metrics and alerts
- **Approve Leave**: Review and approve requests
- **Staff Management**: Add/edit staff records
- **Rota Management**: Create and edit shifts
- **Reports Access**: All reports and analytics
- **Compliance Oversight**: Monitor compliance

### Admin Portal
- **System Configuration**: Settings and preferences
- **User Management**: Create and manage users
- **Audit Access**: Full audit trail access
- **Backup Management**: System backups
- **Integration Settings**: API and email configuration

### Mobile Responsive
- **Tablet Optimized**: Works on iPads
- **Phone Accessible**: Mobile-friendly views
- **Touch-Friendly**: Easy navigation
- **Offline Capability**: Limited offline access

---

## 🎯 System Statistics (Current)

### Staff & Users
- **Total Staff**: 100+ active users
- **Units**: 8 care units
- **Roles**: 8 different job roles
- **Teams**: Team A and Team B

### Care Plan Reviews
- **Residents**: 120 active residents
- **Reviews Tracked**: 120+ reviews
- **Compliance Rate**: Real-time tracking
- **Overdue Reviews**: Monitored daily

### Additional Staffing
- **Agency Companies**: 8 active suppliers
- **Overtime Tracking**: Weekly reporting
- **Cost Monitoring**: Real-time totals
- **Automated Reports**: Weekly distribution

### Annual Leave
- **Leave Requests**: Unlimited tracking
- **Approval Workflow**: Multi-level
- **Balance Tracking**: Real-time calculation
- **Carry Over**: Automatic handling

---

## 📚 Documentation Resources

### User Guides (in `/docs/staff_guidance/`)
- **New Starter Guide**: For new employees
- **Annual Leave Guide**: Leave request process
- **Sickness Reporting Guide**: How to report absence
- **Leave Usage Targets Guide**: Understanding targets
- **Staff FAQ**: Frequently asked questions

### Manager Guides
- **Manager Attendance Guide**: Managing attendance
- **Absence Interview Guide**: Conducting RTW interviews
- **OH Referral Guide**: Occupational health referrals
- **Disability & MH Guide**: Supporting staff
- **Menopause Guide**: Workplace support
- **Reasonable Adjustments**: Implementation guide

### Care Inspectorate Compliance
- **Incident Report Template**: Standard form
- **Induction Checklist**: 12-week program
- **Supervision Record Template**: 1-to-1 template
- **Training Matrix**: Required training list

### Technical Documentation
- **Implementation Plans**: Feature specifications
- **API Documentation**: Integration guides
- **Customization Guide**: System customization
- **Backup Instructions**: System backup procedures

### Quick Reference Guides
- **Additional Staffing Quick Ref**: Overtime/agency guide
- **Care Plan Quick Ref**: Review system overview
- **Customization Quick Ref**: Custom features
- **AI Assistant Quick Start**: Using the chatbot

---

## 🚀 Quick Start for Stakeholders

### For Care Home Managers
1. **View Dashboard**: See key metrics at a glance
2. **Check Compliance**: Monitor care plan reviews and training
3. **Approve Leave**: Process pending leave requests
4. **Review Reports**: Access weekly staffing and compliance reports
5. **Monitor Costs**: Track overtime and agency spending

### For Unit Managers
1. **Manage Unit Rota**: Create and edit shifts for your unit
2. **Track Reviews**: Monitor care plan review compliance
3. **Staff Oversight**: View your team's leave and training
4. **Approve Requests**: Handle leave and shift swap requests
5. **Unit Reports**: Generate unit-specific reports

### For Care Staff
1. **View Schedule**: Check your upcoming shifts
2. **Request Leave**: Submit leave requests
3. **Complete Reviews**: Fill in care plan reviews
4. **Update Records**: Maintain training and supervision records
5. **View Own Data**: Access personal information

### For Administrators
1. **User Management**: Add and manage system users
2. **System Config**: Configure settings and preferences
3. **Audit Access**: Review system activity logs
4. **Backup Management**: Ensure data is backed up
5. **Support Users**: Help staff with system issues

---

## 💡 Key Benefits

### Efficiency
- ✅ **5-second staff onboarding** (vs 15 minutes manual)
- ✅ **Automated weekly reports** (saves 2 hours/week)
- ✅ **Real-time leave balances** (no manual calculations)
- ✅ **Auto-scheduled reviews** (ensures compliance)

### Compliance
- ✅ **Care Inspectorate ready** (all requirements met)
- ✅ **Audit trail** (complete change history)
- ✅ **Compliance tracking** (automatic monitoring)
- ✅ **Documentation** (comprehensive records)

### Cost Control
- ✅ **Overtime tracking** (monitor additional costs)
- ✅ **Agency cost analysis** (compare suppliers)
- ✅ **Leave planning** (reduce last-minute cover)
- ✅ **Shift optimization** (minimize overstaffing)

### Quality of Care
- ✅ **Care plan compliance** (timely reviews)
- ✅ **Keyworker accountability** (clear ownership)
- ✅ **Family involvement** (documented engagement)
- ✅ **Continuous improvement** (tracked goals and progress)

---

## 📞 Support & Training

### Available Support
- **AI Assistant**: 24/7 chatbot help
- **User Guides**: Comprehensive documentation
- **Video Tutorials**: Step-by-step videos (planned)
- **Email Support**: Technical assistance
- **Phone Support**: Urgent issues

### Training Options
- **New User Onboarding**: 1-hour introduction
- **Manager Training**: 2-hour advanced features
- **Admin Training**: 3-hour system configuration
- **Refresher Training**: Quarterly updates
- **Custom Training**: Role-specific sessions

---

## 🔮 Roadmap & Future Features

### Planned Enhancements
- Manager Dashboard for Care Plan Reviews
- Email Alert System for Overdue Reviews
- Mobile App for Staff
- Advanced Analytics Dashboard
- Integration with Payroll Systems
- Resident Family Portal
- Medication Administration Records (MAR)
- Quality Assurance Module

---

## 📝 Version History

**Version 2.0** (December 2025)
- Added Care Plan Review System
- Added AI Assistant Care Plan Queries
- Added Compliance Reporting
- Enhanced Additional Staffing Reports

**Version 1.5** (November 2025)
- Added Additional Staffing (Overtime & Agency)
- Added Leave Usage Targets
- Added 8 Agency Companies
- Automated Weekly Staffing Reports

**Version 1.0** (October 2025)
- Core Scheduling System
- Staff Management
- Annual Leave System
- Care Inspectorate Compliance
- Audit & Data Security

---

## 📄 System Requirements

### Server Requirements
- **OS**: Linux/macOS/Windows
- **Python**: 3.14.0 or higher
- **Django**: 5.2.7
- **Database**: SQLite (production: PostgreSQL recommended)
- **Memory**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum

### Client Requirements
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Screen**: 1024x768 minimum resolution
- **Internet**: Broadband connection
- **Device**: Desktop, tablet, or smartphone

---

**Document Maintained By:** System Administrator  
**Contact:** admin@staffrotasystem.com  
**Last Review:** December 3, 2025  
**Next Review:** March 3, 2026

---

*This system is designed to support care home operations and ensure compliance with Care Inspectorate Scotland requirements. All features are built with GDPR compliance and data security as top priorities.*
