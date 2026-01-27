# PostgreSQL Migration Guide
**Date:** 16 January 2026  
**Purpose:** Migrate from SQLite to PostgreSQL on demo.therota.co.uk

---

## Quick Migration Commands

SSH into the server and run these commands in sequence:

```bash
# 1. Check PostgreSQL is running
systemctl status postgresql

# If not running, start it:
systemctl start postgresql

# 2. Create PostgreSQL database and user
sudo -u postgres psql << 'EOF'
DROP DATABASE IF EXISTS staffrota_production;
DROP USER IF EXISTS staffrota_user;
CREATE USER staffrota_user WITH PASSWORD 'StaffRota2026!Secure';
CREATE DATABASE staffrota_production OWNER staffrota_user;
GRANT ALL PRIVILEGES ON DATABASE staffrota_production TO staffrota_user;
ALTER USER staffrota_user CREATEDB;
\q
EOF

# 3. Backup current SQLite database
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# 4. Export data from SQLite
source /home/staff-rota-system/venv/bin/activate
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude admin.logentry \
    --exclude sessions.session \
    --exclude axes.accessattempt \
    --exclude axes.accesslog \
    --exclude axes.accessfailurelog \
    --output /tmp/sqlite_export.json

echo "Export complete. File size:"
ls -lh /tmp/sqlite_export.json

# 5. Update .env file for PostgreSQL
cat > /home/staff-rota-system/.env << 'EOF'
DEBUG=False
SECRET_KEY=jik1jbcby9tkanpj82cgyqky1ir3mk5b2ea10rzzvppqk94qkg
ALLOWED_HOSTS=demo.therota.co.uk,159.65.18.80
CSRF_TRUSTED_ORIGINS=https://demo.therota.co.uk
SITE_URL=https://demo.therota.co.uk
DISABLE_ELASTICSEARCH=True
AXES_ENABLED=False

# PostgreSQL Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=staffrota_production
DB_USER=staffrota_user
DB_PASSWORD=StaffRota2026!Secure
DB_HOST=localhost
DB_PORT=5432
EOF

# 6. Run migrations on PostgreSQL
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
source /home/staff-rota-system/venv/bin/activate
python manage.py migrate

# 7. Load data into PostgreSQL
python manage.py loaddata /tmp/sqlite_export.json

# 8. Verify the migration
python manage.py shell << 'PYEOF'
from django.db import connection
from scheduling.models import User
print(f"Database engine: {connection.settings_dict['ENGINE']}")
print(f"Database name: {connection.settings_dict['NAME']}")
print(f"Total users: {User.objects.count()}")
print(f"Superusers: {User.objects.filter(is_superuser=True).count()}")
PYEOF

# 9. Restart the service
systemctl restart staffrota

# 10. Check service status
systemctl status staffrota --no-pager | head -20

# 11. Test the application
curl -I https://demo.therota.co.uk
```

---

## Verification Steps

After migration, verify everything works:

```bash
# Check database connection
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
source /home/staff-rota-system/venv/bin/activate
python manage.py dbshell

# In PostgreSQL prompt, run:
\dt  -- List all tables
SELECT COUNT(*) FROM scheduling_user;  -- Count users
\q   -- Exit

# Check application logs
journalctl -u staffrota -n 50 --no-pager

# Test login
curl -s https://demo.therota.co.uk/login/ | grep -i "login\|staff rota"
```

---

## Rollback (if needed)

If something goes wrong, rollback to SQLite:

```bash
# 1. Restore .env to use SQLite
cat > /home/staff-rota-system/.env << 'EOF'
DEBUG=False
SECRET_KEY=jik1jbcby9tkanpj82cgyqky1ir3mk5b2ea10rzzvppqk94qkg
ALLOWED_HOSTS=demo.therota.co.uk,159.65.18.80
CSRF_TRUSTED_ORIGINS=https://demo.therota.co.uk
SITE_URL=https://demo.therota.co.uk
DISABLE_ELASTICSEARCH=True
AXES_ENABLED=False
EOF

# 2. Restart service
systemctl restart staffrota
```

---

## Benefits of PostgreSQL Migration

✅ **Performance:** 10-100x faster for complex queries  
✅ **Concurrency:** Handle 100+ simultaneous users  
✅ **Reliability:** ACID compliance, data integrity  
✅ **Scalability:** Production-grade database  
✅ **Features:** Advanced querying, JSON support, full-text search  

---

## Database Credentials

**Save these securely:**
- Database: `staffrota_production`
- User: `staffrota_user`
- Password: `StaffRota2026!Secure`
- Host: `localhost`
- Port: `5432`

---

## Troubleshooting

### If dumpdata fails with "too large"
```bash
# Export in chunks by app
python manage.py dumpdata scheduling > /tmp/scheduling.json
python manage.py dumpdata staff_records > /tmp/staff_records.json
python manage.py dumpdata quality_audits > /tmp/quality_audits.json
# ... etc for each app

# Then load each file
python manage.py loaddata /tmp/scheduling.json
python manage.py loaddata /tmp/staff_records.json
# ... etc
```

### If PostgreSQL connection fails
```bash
# Check PostgreSQL is listening
sudo netstat -plnt | grep 5432

# Check pg_hba.conf allows local connections
sudo cat /etc/postgresql/*/main/pg_hba.conf | grep local

# Restart PostgreSQL
systemctl restart postgresql
```

### If loaddata fails with duplicate key errors
```bash
# Clear the PostgreSQL database and try again
sudo -u postgres psql -c "DROP DATABASE staffrota_production;"
sudo -u postgres psql -c "CREATE DATABASE staffrota_production OWNER staffrota_user;"
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
source /home/staff-rota-system/venv/bin/activate
python manage.py migrate
python manage.py loaddata /tmp/sqlite_export.json
```

---

**Ready to migrate? Just copy and paste the commands from the "Quick Migration Commands" section!**
