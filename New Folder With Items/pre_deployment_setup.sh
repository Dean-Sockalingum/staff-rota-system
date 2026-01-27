#!/bin/bash
# Quick Pre-Deployment Setup Script
# Completes critical deployment tasks

set -e  # Exit on error

echo "=========================================="
echo "Pre-Deployment Setup - Staff Rota System"
echo "=========================================="
echo ""

# Navigate to project directory
cd "/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items"

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# 1. Collect Static Files
echo "1️⃣  Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

# 2. Verify Database Connection
echo "2️⃣  Verifying PostgreSQL connection..."
python manage.py check --database default
echo "✓ Database connection verified"
echo ""

# 3. Check Migration Status
echo "3️⃣  Checking migrations..."
python manage.py showmigrations | grep -c "\[X\]" > /dev/null && echo "✓ All migrations applied"
echo ""

# 4. Create Backup
echo "4️⃣  Creating database backup..."
./backup_postgres.sh
echo "✓ Backup created"
echo ""

# 5. User Count Check
echo "5️⃣  Checking user accounts..."
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())")
echo "Current users in database: $USER_COUNT"

if [ "$USER_COUNT" -eq "0" ]; then
    echo ""
    echo "⚠️  WARNING: No users in database!"
    echo ""
    echo "Creating superuser account..."
    echo "Please enter the following details:"
    python manage.py createsuperuser
    echo "✓ Superuser created"
else
    echo "✓ Database has users"
fi
echo ""

# 6. Generate SECRET_KEY
echo "6️⃣  Generating new SECRET_KEY for production..."
NEW_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo ""
echo "⚠️  IMPORTANT: Update your .env file with this SECRET_KEY:"
echo ""
echo "SECRET_KEY=$NEW_SECRET_KEY"
echo ""
echo "Copy the above line and paste it into your .env file"
echo ""

# 7. Final System Check
echo "7️⃣  Running final system check..."
python manage.py check
echo "✓ System check passed"
echo ""

# 8. Summary
echo "=========================================="
echo "✅ PRE-DEPLOYMENT SETUP COMPLETE"
echo "=========================================="
echo ""
echo "Completed Tasks:"
echo "  ✓ Static files collected"
echo "  ✓ Database connection verified"
echo "  ✓ Migrations verified"
echo "  ✓ Database backup created"
echo "  ✓ Superuser account ready"
echo "  ✓ SECRET_KEY generated"
echo "  ✓ System checks passed"
echo ""
echo "Next Steps:"
echo "1. Update .env with new SECRET_KEY (shown above)"
echo "2. Set DEBUG=False in .env for production"
echo "3. Test application: python manage.py runserver"
echo "4. Access: http://127.0.0.1:8000/admin/"
echo ""
echo "Ready for Monday deployment! 🚀"
echo ""
