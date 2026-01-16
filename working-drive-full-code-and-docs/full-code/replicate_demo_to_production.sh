#!/bin/bash
# Replicate Local Demo to Production
# This exports from local SQLite and imports to production PostgreSQL

echo "=========================================="
echo "REPLICATING LOCAL DEMO TO PRODUCTION"
echo "=========================================="
echo ""

# Step 1: Export from local demo
echo "Step 1: Exporting data from local demo..."
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

python3 manage.py dumpdata \
  scheduling.Role \
  scheduling.CareHome \
  scheduling.Unit \
  scheduling.ShiftType \
  scheduling.User \
  --indent 2 \
  --output /Users/deansockalingum/Desktop/Staff_Rota_Backups/demo_export.json

if [ $? -eq 0 ]; then
    echo "✓ Export complete"
    ls -lh /Users/deansockalingum/Desktop/Staff_Rota_Backups/demo_export.json
else
    echo "✗ Export failed"
    exit 1
fi

echo ""
echo "Step 2: Uploading to production..."
scp /Users/deansockalingum/Desktop/Staff_Rota_Backups/demo_export.json root@159.65.18.80:/home/staff-rota-system/

if [ $? -eq 0 ]; then
    echo "✓ Upload complete"
else
    echo "✗ Upload failed"
    exit 1
fi

echo ""
echo "Step 3: Clearing production database..."
ssh root@159.65.18.80 'cd /home/staff-rota-system && source venv/bin/activate && python manage.py shell -c "
from scheduling.models import User, Shift, CareHome, Unit, Role, ShiftType
print(\"Deleting all data...\")
User.objects.all().delete()
Shift.objects.all().delete()
Unit.objects.all().delete()
CareHome.objects.all().delete()
Role.objects.all().delete()
ShiftType.objects.all().delete()
print(\"✓ Database cleared\")
"'

echo ""
echo "Step 4: Importing data to production..."
ssh root@159.65.18.80 'cd /home/staff-rota-system && source venv/bin/activate && python manage.py loaddata demo_export.json'

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ REPLICATION COMPLETE!"
    echo "=========================================="
    echo ""
    echo "Verifying production database..."
    ssh root@159.65.18.80 'cd /home/staff-rota-system && source venv/bin/activate && python manage.py shell -c "
from scheduling.models import User, CareHome, Unit, Role, ShiftType
print(f\"Homes: {CareHome.objects.count()}\")
print(f\"Units: {Unit.objects.count()}\")
print(f\"Roles: {Role.objects.count()}\")
print(f\"Shift Types: {ShiftType.objects.count()}\")
print(f\"Users: {User.objects.count()}\")
print(f\"\")
print(f\"Login: SAP 000541 / Greenball99##\")
print(f\"URL: https://demo.therota.co.uk\")
"'
else
    echo "✗ Import failed"
    exit 1
fi
