#!/bin/bash
# Execute backup on remote server
ssh root@159.65.18.80 'bash -s' << 'ENDSSH'
set -e
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/home/staff-rota-system/backups
PROJECT_DIR=/home/staff-rota-system/2025-12-12_Multi-Home_Complete
VENV_PYTHON=/home/staff-rota-system/venv/bin/python

mkdir -p $BACKUP_DIR
cd $PROJECT_DIR

echo "Step 1: Django data backup..."
$VENV_PYTHON manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > $BACKUP_DIR/data_backup_$TIMESTAMP.json 2>&1

echo "Step 2: Schema documentation..."
$VENV_PYTHON manage.py inspectdb > $BACKUP_DIR/schema_$TIMESTAMP.py 2>&1

echo "Step 3: Migration state..."
$VENV_PYTHON manage.py showmigrations > $BACKUP_DIR/migrations_$TIMESTAMP.txt 2>&1

echo "Step 4: Database statistics..."
$VENV_PYTHON manage.py shell << 'PYEOF' > $BACKUP_DIR/db_stats_$TIMESTAMP.txt 2>&1
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
    tables = cursor.fetchall()
    print(f"Total tables: {len(tables)}")
    for table in tables[:20]:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"{table[0]}: {count} rows")
        except:
            print(f"{table[0]}: ERROR")
    cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='scheduling_shift' ORDER BY ordinal_position")
    cols = cursor.fetchall()
    print("\nShift table columns:")
    for col in cols:
        print(f"  {col[0]}: {col[1]}")
PYEOF

echo "Step 5: Creating archive..."
cd $BACKUP_DIR
tar -czf backup_complete_$TIMESTAMP.tar.gz *.json *.py *.txt 2>/dev/null || true

echo "=== BACKUP COMPLETE ==="
ls -lh backup_complete_$TIMESTAMP.tar.gz 2>/dev/null || echo "Archive creation may have failed"
echo "Files created:"
ls -lh $BACKUP_DIR/*$TIMESTAMP* 2>/dev/null || echo "No timestamped files found"
ENDSSH
