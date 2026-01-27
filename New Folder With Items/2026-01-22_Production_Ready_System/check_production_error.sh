#!/bin/bash
# Check production error by running Django shell command

echo "=========================================="
echo "CHECKING PRODUCTION ERROR"
echo "=========================================="
echo ""

ssh root@159.65.18.80 << 'ENDSSH'
cd /home/staff-rota-system
source venv/bin/activate

echo "Testing the training_compliance_dashboard view..."
python manage.py shell << 'PYTHON'
import sys
import traceback
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from scheduling.models import User

# Import the view
from scheduling.views_compliance import training_compliance_dashboard

# Create a fake request
factory = RequestFactory()
request = factory.get('/compliance/training/management/')

# Get a real user
try:
    user = User.objects.filter(is_active=True).first()
    if user:
        request.user = user
        print(f"Testing with user: {user.sap}")
    else:
        print("No active users found!")
        sys.exit(1)
except Exception as e:
    print(f"Error getting user: {e}")
    sys.exit(1)

# Try to call the view
try:
    response = training_compliance_dashboard(request)
    print(f"\n✓ View executed successfully!")
    print(f"Status code: {response.status_code}")
    if response.status_code == 500:
        print(f"\nResponse content:\n{response.content.decode('utf-8')[:1000]}")
except Exception as e:
    print(f"\n✗ View raised an exception:")
    print(f"Error: {str(e)}")
    print(f"\nFull traceback:")
    traceback.print_exc()
PYTHON

ENDSSH
