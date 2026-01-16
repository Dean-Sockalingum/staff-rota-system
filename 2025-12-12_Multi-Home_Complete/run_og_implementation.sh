#!/bin/bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 << 'EOF'
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

# Now run the implementation
exec(open('implement_og_exact_pattern.py').read())
EOF
