#!/bin/bash
# PostgreSQL Backup Script for Staff Rota System
# Creates timestamped backups of the production database

BACKUP_DIR="/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items/backups"
DB_NAME="staff_rota_production"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/postgres_backup_${TIMESTAMP}.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create PostgreSQL backup
echo "Creating PostgreSQL backup..."
pg_dump -U deansockalingum -d "$DB_NAME" -F c -f "$BACKUP_FILE.custom"
pg_dump -U deansockalingum -d "$DB_NAME" > "$BACKUP_FILE"

# Compress the SQL file
gzip "$BACKUP_FILE"

echo "✓ Backup created: ${BACKUP_FILE}.gz"
echo "✓ Custom format: ${BACKUP_FILE}.custom"
ls -lh "${BACKUP_FILE}.gz" "${BACKUP_FILE}.custom"

# Keep only last 10 backups
cd "$BACKUP_DIR"
ls -t postgres_backup_*.gz | tail -n +11 | xargs rm -f 2>/dev/null
ls -t postgres_backup_*.custom | tail -n +11 | xargs rm -f 2>/dev/null

echo ""
echo "Backup complete!"
