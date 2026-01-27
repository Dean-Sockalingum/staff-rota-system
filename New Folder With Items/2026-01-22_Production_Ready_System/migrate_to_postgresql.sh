#!/bin/bash
# Migrate from SQLite to PostgreSQL for production

set -e

echo "🔄 Starting SQLite to PostgreSQL migration..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if PostgreSQL is running
if ! systemctl is-active --quiet postgresql; then
    echo -e "${YELLOW}Starting PostgreSQL...${NC}"
    systemctl start postgresql
fi

# Database configuration
DB_NAME="staffrota_production"
DB_USER="staffrota_user"
DB_PASSWORD="StaffRota2026!Secure"

echo -e "${GREEN}✅ Step 1: Creating PostgreSQL database and user${NC}"
sudo -u postgres psql << EOF
-- Drop database if exists (for clean migration)
DROP DATABASE IF EXISTS ${DB_NAME};
DROP USER IF EXISTS ${DB_USER};

-- Create user
CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';

-- Create database
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
ALTER USER ${DB_USER} CREATEDB;
EOF

echo -e "${GREEN}✅ Step 2: Backing up SQLite database${NC}"
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

echo -e "${GREEN}✅ Step 3: Updating .env configuration${NC}"
cat > /home/staff-rota-system/.env << EOF
DEBUG=False
SECRET_KEY=jik1jbcby9tkanpj82cgyqky1ir3mk5b2ea10rzzvppqk94qkg
ALLOWED_HOSTS=demo.therota.co.uk,159.65.18.80
CSRF_TRUSTED_ORIGINS=https://demo.therota.co.uk
SITE_URL=https://demo.therota.co.uk
DISABLE_ELASTICSEARCH=True
AXES_ENABLED=False

# PostgreSQL Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=localhost
DB_PORT=5432
EOF

echo -e "${GREEN}✅ Step 4: Dumping data from SQLite${NC}"
source /home/staff-rota-system/venv/bin/activate
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete
python manage.py dumpdata --natural-foreign --natural-primary \
    --exclude contenttypes --exclude auth.permission \
    --exclude admin.logentry --exclude sessions.session \
    --exclude axes.accessattempt --exclude axes.accesslog \
    --exclude axes.accessfailurelog \
    > /tmp/sqlite_dump.json

echo -e "${GREEN}✅ Step 5: Running PostgreSQL migrations${NC}"
python manage.py migrate --database=default

echo -e "${GREEN}✅ Step 6: Loading data into PostgreSQL${NC}"
python manage.py loaddata /tmp/sqlite_dump.json

echo -e "${GREEN}✅ Step 7: Restarting application service${NC}"
systemctl restart staffrota

echo -e "${GREEN}✅ Step 8: Verifying PostgreSQL connection${NC}"
python manage.py shell << 'PYEOF'
from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT count(*) FROM scheduling_user")
user_count = cursor.fetchone()[0]
print(f"✅ PostgreSQL connected successfully! Users in database: {user_count}")
PYEOF

echo ""
echo -e "${GREEN}🎉 Migration completed successfully!${NC}"
echo ""
echo "Database: PostgreSQL"
echo "Database name: ${DB_NAME}"
echo "User: ${DB_USER}"
echo "SQLite backup: db.sqlite3.backup_*"
echo ""
echo "You can now remove the SQLite backup files if everything works correctly."
