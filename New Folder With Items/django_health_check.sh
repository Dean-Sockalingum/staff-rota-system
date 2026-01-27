# Django Production Health Check Commands
# Run these AFTER activating your virtualenv on production

# ===== STEP 1: Find and Navigate to Project =====
# Find Django project
find /home /var/www /opt -name "manage.py" -type f 2>/dev/null | grep -v venv

# CD to project directory (replace with actual path found above)
cd /path/to/your/django/project
source venv/bin/activate

# ===== STEP 2: Django System Checks =====
echo "=== Django System Check ==="
python manage.py check --deploy

echo -e "\n=== Migration Status ==="
python manage.py showmigrations | tail -30

# ===== STEP 3: Database Health =====
echo -e "\n=== Database Connection Test ==="
python manage.py shell <<EOF
import django
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection: OK")
except Exception as e:
    print(f"❌ Database error: {e}")
EOF

# ===== STEP 4: Production Data Counts =====
echo -e "\n=== Production Data Summary ==="
python manage.py shell <<EOF
from scheduling.models import User, Shift, Unit, CareHome
from scheduling.models_multi_home import CareHome as MultiHomeCareHome
from incident_safety.models import IncidentReport, SafetyActionPlan
from datetime import datetime, timedelta

print(f"Staff (Users): {User.objects.count()}")
print(f"Care Homes: {MultiHomeCareHome.objects.count()}")
print(f"Units: {Unit.objects.filter(is_active=True).count()}")
print(f"Shifts (last 30 days): {Shift.objects.filter(date__gte=datetime.now()-timedelta(days=30)).count()}")
print(f"Incidents (total): {IncidentReport.objects.count()}")
print(f"Safety Action Plans: {SafetyActionPlan.objects.count()}")
EOF

# ===== STEP 5: Recent Errors Check =====
echo -e "\n=== Recent Errors (if any) ==="
python manage.py shell <<EOF
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType

recent_errors = LogEntry.objects.filter(
    action_time__gte=datetime.now() - timedelta(days=7)
).order_by('-action_time')[:10]

if recent_errors:
    for entry in recent_errors:
        print(f"{entry.action_time}: {entry.action_flag} - {entry.object_repr}")
else:
    print("No admin log entries in last 7 days")
EOF

# ===== STEP 6: Active Sessions =====
echo -e "\n=== Active User Sessions ==="
python manage.py shell <<EOF
from django.contrib.sessions.models import Session
from datetime import datetime

active_sessions = Session.objects.filter(expire_date__gte=datetime.now()).count()
print(f"Active sessions: {active_sessions}")
EOF

# ===== STEP 7: Check Static Files =====
echo -e "\n=== Static Files Check ==="
python manage.py collectstatic --noinput --dry-run | tail -5

# ===== STEP 8: Django Version =====
echo -e "\n=== Django Version ==="
python -c "import django; print(f'Django version: {django.get_version()}')"

# ===== STEP 9: Installed Apps Status =====
echo -e "\n=== Installed Apps ==="
python manage.py shell <<EOF
from django.conf import settings
print("Custom apps:")
for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        print(f"  - {app}")
EOF

# ===== STEP 10: Database Size (PostgreSQL) =====
echo -e "\n=== Database Size ==="
psql -U staffrota_user -d staffrota_production -c "\
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'staffrota_production';"

echo -e "\n=========================================="
echo "Django Health Check Complete"
echo "=========================================="
