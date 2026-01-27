#!/bin/bash
# Database Backup and Schema Documentation Script
# Created: January 19, 2026

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/staff-rota-system/backups"
PROJECT_DIR="/home/staff-rota-system/2025-12-12_Multi-Home_Complete"
VENV_PYTHON="/home/staff-rota-system/venv/bin/python"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "=========================================="
echo "DATABASE BACKUP & SCHEMA DOCUMENTATION"
echo "Timestamp: $TIMESTAMP"
echo "=========================================="

# 1. Django data backup (JSON format)
echo ""
echo "1. Creating Django data backup..."
cd $PROJECT_DIR
$VENV_PYTHON manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    -e contenttypes \
    -e auth.Permission \
    --indent 2 \
    > $BACKUP_DIR/data_backup_$TIMESTAMP.json

if [ $? -eq 0 ]; then
    SIZE=$(du -h $BACKUP_DIR/data_backup_$TIMESTAMP.json | cut -f1)
    echo "✓ Data backup created: $SIZE"
    echo "  Location: $BACKUP_DIR/data_backup_$TIMESTAMP.json"
else
    echo "✗ Data backup failed"
fi

# 2. Schema documentation
echo ""
echo "2. Documenting database schema..."
$VENV_PYTHON manage.py inspectdb > $BACKUP_DIR/schema_$TIMESTAMP.py

if [ $? -eq 0 ]; then
    echo "✓ Schema documented"
    echo "  Location: $BACKUP_DIR/schema_$TIMESTAMP.py"
else
    echo "✗ Schema documentation failed"
fi

# 3. Current migrations list
echo ""
echo "3. Listing current migrations..."
$VENV_PYTHON manage.py showmigrations > $BACKUP_DIR/migrations_$TIMESTAMP.txt

if [ $? -eq 0 ]; then
    echo "✓ Migrations listed"
    echo "  Location: $BACKUP_DIR/migrations_$TIMESTAMP.txt"
else
    echo "✗ Migration listing failed"
fi

# 4. Get database stats
echo ""
echo "4. Gathering database statistics..."
$VENV_PYTHON << PYEOF > $BACKUP_DIR/db_stats_$TIMESTAMP.txt
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import *
from django.contrib.auth.models import User

print("DATABASE STATISTICS")
print("=" * 60)
print(f"Users: {User.objects.count()}")
print(f"Care Homes: {CareHome.objects.count()}")
print(f"Units: {Unit.objects.count()}")
print(f"Shifts: {Shift.objects.count()}")
print(f"Training Courses: {TrainingCourse.objects.count()}")

# Check for shifts table structure
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='scheduling_shift' ORDER BY ordinal_position;")
print("\nSHIFT TABLE COLUMNS:")
print("-" * 60)
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")
PYEOF

if [ $? -eq 0 ]; then
    echo "✓ Statistics gathered"
    echo "  Location: $BACKUP_DIR/db_stats_$TIMESTAMP.txt"
    cat $BACKUP_DIR/db_stats_$TIMESTAMP.txt
else
    echo "✗ Statistics gathering failed"
fi

# 5. Create compressed archive
echo ""
echo "5. Creating compressed backup archive..."
cd $BACKUP_DIR
tar -czf backup_complete_$TIMESTAMP.tar.gz \
    data_backup_$TIMESTAMP.json \
    schema_$TIMESTAMP.py \
    migrations_$TIMESTAMP.txt \
    db_stats_$TIMESTAMP.txt

if [ $? -eq 0 ]; then
    SIZE=$(du -h backup_complete_$TIMESTAMP.tar.gz | cut -f1)
    echo "✓ Archive created: $SIZE"
    echo "  Location: $BACKUP_DIR/backup_complete_$TIMESTAMP.tar.gz"
fi

echo ""
echo "=========================================="
echo "BACKUP COMPLETE"
echo "=========================================="
echo "Backup directory: $BACKUP_DIR"
echo ""
ls -lh $BACKUP_DIR/*$TIMESTAMP*
