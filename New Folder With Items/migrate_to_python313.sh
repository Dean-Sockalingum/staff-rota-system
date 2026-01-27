#!/bin/bash

echo "🔧 Migrating to Python 3.13 (Django 4.2 compatible)"
echo "================================================="
echo ""

cd "/Users/deansockalingum/Desktop/Staff_Rota_Backups/New Folder With Items"

# Backup existing venv
echo "📦 Backing up existing venv..."
if [ -d "venv" ]; then
    mv venv venv_python314_backup
    echo "✓ Backed up to venv_python314_backup"
fi

# Create new venv with Python 3.13
echo ""
echo "🐍 Creating new virtual environment with Python 3.13..."
/opt/homebrew/bin/python3.13 -m venv venv

# Activate and install requirements
echo ""
echo "📚 Installing packages..."
source venv/bin/activate
pip install --upgrade pip

# Install from requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install core packages manually
    echo "Installing core Django packages..."
    pip install Django==4.2.27 \
                psycopg2-binary \
                djangorestframework \
                django-cors-headers \
                django-celery-beat \
                django-axes \
                django-auditlog \
                django-otp \
                celery \
                redis \
                pillow \
                python-dateutil \
                openpyxl \
                pandas \
                numpy \
                prophet \
                scikit-learn \
                django-csp
fi

echo ""
echo "✅ Migration complete!"
echo ""
echo "Python version:"
python --version
echo ""
echo "Django version:"
python -c "import django; print(django.VERSION)"
echo ""
echo "PostgreSQL adapter:"
python -c "import psycopg2; print(f'psycopg2 {psycopg2.__version__}')"
echo ""
echo "================================================="
echo "✓ Ready to run: python manage.py runserver"
echo "================================================="
