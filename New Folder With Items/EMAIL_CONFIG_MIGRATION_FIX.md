# Email Configuration Migration Fix

## Issue
Foreign key constraint error when running migrations for email_config app.

## Quick Fix

Run this command to fix the database and apply email_config migrations:

```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete

# Option 1: Disable foreign key checks temporarily
python3 manage.py shell << EOF
from django.db import connection
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys=OFF;")
connection.close()
EOF

# Then run migrations
python3 manage.py migrate email_config

# Re-enable foreign keys
python3 manage.py shell << EOF
from django.db import connection
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys=ON;")
connection.close()
EOF
```

## Alternative: Fresh Migration

If above doesn't work, create email_config table directly:

```bash
python3 manage.py dbshell << EOF
CREATE TABLE IF NOT EXISTS "email_config_emailconfiguration" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "provider" varchar(20) NOT NULL,
    "host" varchar(255) NOT NULL,
    "port" integer NOT NULL,
    "use_tls" bool NOT NULL,
    "use_ssl" bool NOT NULL,
    "username" varchar(254) NOT NULL,
    "password" varchar(512) NOT NULL,
    "from_email" varchar(254) NOT NULL,
    "is_active" bool NOT NULL,
    "created_at" datetime NOT NULL,
    "updated_at" datetime NOT NULL,
    "last_test_date" datetime NULL,
    "last_test_status" varchar(20) NULL,
    "last_test_message" text NULL
);
EOF

# Then mark migration as applied
python3 manage.py migrate email_config --fake
```

## Verify

After fixing, verify email configuration is accessible:

```bash
# Access admin UI
# Navigate to: http://127.0.0.1:8000/admin/email_config/emailconfiguration/
# You should see "Email configurations" section
```

## Test

1. Log in to Django admin: http://127.0.0.1:8000/admin/
2. Click "Email Configurations"
3. Click "Add Email Configuration"
4. Select provider (Gmail, SendGrid, Microsoft 365, Custom)
5. Fill in details
6. Save
7. Use "Test Email Configuration" action to verify
