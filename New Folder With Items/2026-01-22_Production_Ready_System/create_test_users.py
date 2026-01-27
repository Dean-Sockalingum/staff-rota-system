#!/usr/bin/env python
"""
Create test users for senior leadership roles (HOS, IDI, SM, OM)
Run with: ./venv/bin/python create_test_users.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from scheduling.models import User, Role, Unit

def create_test_users():
    """Create test users for each senior leadership role"""
    
    print("\n" + "="*60)
    print("Creating Test Users for Senior Leadership Roles")
    print("="*60 + "\n")
    
    # Define test users with their details
    test_users = [
        {
            'sap': '900001',
            'first_name': 'Helen',
            'last_name': 'Morrison',
            'email': 'helen.morrison@test.glasgowcc.gov.uk',
            'role_name': 'HOS',
            'password': 'TestHOS123!',
        },
        {
            'sap': '900002',
            'first_name': 'David',
            'last_name': 'Chen',
            'email': 'david.chen@test.glasgowcc.gov.uk',
            'role_name': 'IDI',
            'password': 'TestIDI123!',
        },
        {
            'sap': '900003',
            'first_name': 'Sarah',
            'last_name': 'MacLeod',
            'email': 'sarah.macleod@test.glasgowcc.gov.uk',
            'role_name': 'SM',
            'password': 'TestSM123!',
        },
        {
            'sap': '900004',
            'first_name': 'James',
            'last_name': 'Patterson',
            'email': 'james.patterson@test.glasgowcc.gov.uk',
            'role_name': 'SM',
            'password': 'TestSM123!',
        },
        {
            'sap': '900005',
            'first_name': 'Rachel',
            'last_name': 'Foster',
            'email': 'rachel.foster@test.glasgowcc.gov.uk',
            'role_name': 'OM',
            'password': 'TestOM123!',
        },
        {
            'sap': '900006',
            'first_name': 'Michael',
            'last_name': 'Johnson',
            'email': 'michael.johnson@test.glasgowcc.gov.uk',
            'role_name': 'OM',
            'password': 'TestOM123!',
        },
    ]
    
    created_users = []
    updated_users = []
    errors = []
    
    for user_data in test_users:
        try:
            # Get the role
            role = Role.objects.get(name=user_data['role_name'])
            
            # Check if user already exists
            try:
                user = User.objects.get(sap=user_data['sap'])
                # Update existing user
                user.first_name = user_data['first_name']
                user.last_name = user_data['last_name']
                user.email = user_data['email']
                user.role = role
                user.is_active = True
                user.is_staff = True
                user.set_password(user_data['password'])
                user.save()
                updated_users.append(user)
                print(f"🔄 Updated: {user.full_name} ({user.sap})")
                print(f"   Role: {role.name} - {role.description}")
                print(f"   Email: {user.email}")
                print(f"   Password: {user_data['password']}")
                print()
            except User.DoesNotExist:
                # Create new user
                user = User(
                    sap=user_data['sap'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    email=user_data['email'],
                    role=role,
                    is_active=True,
                    is_staff=True,
                )
                user.set_password(user_data['password'])
                user.save()
                created_users.append(user)
                print(f"✅ Created: {user.full_name} ({user.sap})")
                print(f"   Role: {role.name} - {role.description}")
                print(f"   Email: {user.email}")
                print(f"   Password: {user_data['password']}")
                print(f"   Permissions: SMT={role.is_senior_management_team}, Management={role.is_management}")
                print()
                
        except Role.DoesNotExist:
            error_msg = f"❌ Role '{user_data['role_name']}' not found for {user_data['first_name']} {user_data['last_name']}"
            errors.append(error_msg)
            print(error_msg)
            print()
        except Exception as e:
            error_msg = f"❌ Error creating {user_data['first_name']} {user_data['last_name']}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
            print()
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"✅ Users Created: {len(created_users)}")
    print(f"🔄 Users Updated: {len(updated_users)}")
    print(f"❌ Errors: {len(errors)}")
    print()
    
    if created_users or updated_users:
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS")
        print("="*60)
        
        all_users = created_users + updated_users
        for user_data in test_users:
            print(f"\n{user_data['first_name']} {user_data['last_name']} ({user_data['role_name']}):")
            print(f"  SAP: {user_data['sap']}")
            print(f"  Password: {user_data['password']}")
        
        print("\n" + "="*60)
        print("TESTING INSTRUCTIONS")
        print("="*60)
        print("""
1. Start the development server:
   ./venv/bin/python manage.py runserver

2. Navigate to: http://localhost:8000/login

3. Test each user by logging in with their SAP number and password

4. Verify each role can access:
   - Executive Dashboard
   - All 5 care homes
   - CI Integration features
   - Service Improvement Plans
   - Budget tracking
   - All reports and analytics

5. Expected access for HOS, IDI, SM, OM:
   ✅ Portfolio-wide view of all homes
   ✅ Executive/Strategic Dashboard
   ✅ Full rota management
   ✅ Leave approval
   ✅ Budget forecasting
   ✅ CI reports for all homes
   ✅ Improvement plan creation/viewing
   ✅ AI Assistant
   ✅ All analytics and reports
        """)
    
    if errors:
        print("\n" + "="*60)
        print("ERRORS")
        print("="*60)
        for error in errors:
            print(error)
    
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    print("\nRun this command to verify all roles:")
    print("./venv/bin/python manage.py shell -c \"from scheduling.models import User; users = User.objects.filter(sap__startswith='900'); [print(f'{u.sap}: {u.full_name} - {u.role.name if u.role else \"No Role\"} (SMT={u.role.is_senior_management_team if u.role else False})') for u in users]\"")
    print()

if __name__ == '__main__':
    create_test_users()
