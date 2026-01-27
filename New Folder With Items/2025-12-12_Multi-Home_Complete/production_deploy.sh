#!/bin/bash
#
# Production Deployment Script - Staff Rota System
# Date: January 16, 2026
# Purpose: Automated production deployment with safety checks
#
# Usage: ./production_deploy.sh
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/home/staff-rota-system"
VENV_DIR="$APP_DIR/venv"
STATIC_DIR="/var/www/staff-rota/staticfiles"
MEDIA_DIR="/var/www/staff-rota/media"
LOGS_DIR="$APP_DIR/logs"
BACKUP_DIR="/home/backups/staff-rota"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check if running as correct user
    if [ "$EUID" -eq 0 ]; then
        print_error "Do not run this script as root. Use a regular user with sudo privileges."
        exit 1
    fi
    print_success "Running as non-root user"
    
    # Check if .env file exists
    if [ ! -f "$APP_DIR/.env" ]; then
        print_error ".env file not found at $APP_DIR/.env"
        print_info "Create it from .env.production.template and configure with production values"
        exit 1
    fi
    print_success ".env file found"
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found. Will create it."
        python3 -m venv "$VENV_DIR"
    fi
    print_success "Virtual environment ready"
    
    # Check PostgreSQL is running
    if ! sudo systemctl is-active --quiet postgresql; then
        print_error "PostgreSQL is not running"
        print_info "Start it with: sudo systemctl start postgresql"
        exit 1
    fi
    print_success "PostgreSQL is running"
    
    echo ""
}

create_directories() {
    print_header "Creating Required Directories"
    
    sudo mkdir -p "$STATIC_DIR"
    sudo mkdir -p "$MEDIA_DIR"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$BACKUP_DIR"
    
    # Set permissions
    sudo chown -R www-data:www-data "$STATIC_DIR"
    sudo chown -R www-data:www-data "$MEDIA_DIR"
    sudo chown -R $USER:$USER "$LOGS_DIR"
    
    print_success "Directories created and permissions set"
    echo ""
}

backup_database() {
    print_header "Backing Up Database"
    
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/db_pre_deploy_$DATE.sql"
    
    # Check if database exists
    if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw rotasystem; then
        sudo -u postgres pg_dump rotasystem > "$BACKUP_FILE"
        print_success "Database backed up to $BACKUP_FILE"
    else
        print_warning "Database 'rotasystem' not found - skipping backup"
    fi
    
    echo ""
}

install_dependencies() {
    print_header "Installing Python Dependencies"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn whitenoise django-environ
    
    print_success "Dependencies installed"
    echo ""
}

run_migrations() {
    print_header "Running Database Migrations"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    export DJANGO_SETTINGS_MODULE=rotasystems.settings_production
    
    python manage.py migrate --noinput
    
    print_success "Migrations completed"
    echo ""
}

collect_static_files() {
    print_header "Collecting Static Files"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    export DJANGO_SETTINGS_MODULE=rotasystems.settings_production
    
    python manage.py collectstatic --noinput
    
    # Set permissions
    sudo chown -R www-data:www-data "$STATIC_DIR"
    
    print_success "Static files collected"
    echo ""
}

create_cache_table() {
    print_header "Creating Cache Table"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    export DJANGO_SETTINGS_MODULE=rotasystems.settings_production
    
    python manage.py createcachetable 2>/dev/null || true
    
    print_success "Cache table ready"
    echo ""
}

run_deployment_checks() {
    print_header "Running Django Deployment Checks"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    export DJANGO_SETTINGS_MODULE=rotasystems.settings_production
    
    if python manage.py check --deploy; then
        print_success "Deployment checks passed"
    else
        print_warning "Some deployment checks failed - review above"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo ""
}

setup_supervisor() {
    print_header "Setting Up Supervisor"
    
    # Check if supervisor config exists
    if [ -f "/etc/supervisor/conf.d/staff-rota.conf" ]; then
        print_info "Supervisor config already exists"
    else
        print_info "Creating Supervisor configuration..."
        
        sudo tee /etc/supervisor/conf.d/staff-rota.conf > /dev/null <<EOF
[program:staff-rota]
directory=$APP_DIR
command=$VENV_DIR/bin/gunicorn rotasystems.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
user=www-data
autostart=true
autorestart=true
stdout_logfile=$LOGS_DIR/gunicorn.log
stderr_logfile=$LOGS_DIR/gunicorn_error.log
environment=DJANGO_SETTINGS_MODULE="rotasystems.settings_production"
EOF
        
        print_success "Supervisor config created"
    fi
    
    # Update supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    
    # Restart application
    print_info "Restarting application..."
    sudo supervisorctl restart staff-rota
    
    # Check status
    sleep 2
    if sudo supervisorctl status staff-rota | grep -q RUNNING; then
        print_success "Application is running"
    else
        print_error "Application failed to start. Check logs:"
        print_info "  tail -f $LOGS_DIR/gunicorn_error.log"
        exit 1
    fi
    
    echo ""
}

verify_deployment() {
    print_header "Verifying Deployment"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    export DJANGO_SETTINGS_MODULE=rotasystems.settings_production
    
    # Check database connectivity
    print_info "Testing database connection..."
    if python manage.py dbshell --command="SELECT 1;" &>/dev/null; then
        print_success "Database connection OK"
    else
        print_warning "Could not verify database connection"
    fi
    
    # Check static files
    if [ -f "$STATIC_DIR/admin/css/base.css" ]; then
        print_success "Static files accessible"
    else
        print_warning "Static files may not be properly collected"
    fi
    
    # Show application status
    python manage.py shell -c "
from scheduling.models import User, CareHome, Unit, Role, ShiftType
print('\\nDatabase Status:')
print(f'  Care Homes: {CareHome.objects.count()}')
print(f'  Units: {Unit.objects.count()}')
print(f'  Roles: {Role.objects.count()}')
print(f'  Shift Types: {ShiftType.objects.count()}')
print(f'  Users: {User.objects.count()}')
" 2>/dev/null || print_warning "Could not query database models"
    
    echo ""
}

print_summary() {
    print_header "Deployment Complete!"
    
    echo -e "${GREEN}Your Staff Rota System is now deployed!${NC}"
    echo ""
    echo "Next Steps:"
    echo "  1. Configure Nginx (see PRODUCTION_DEPLOYMENT_GUIDE.md)"
    echo "  2. Setup SSL with Let's Encrypt"
    echo "  3. Test login at your domain"
    echo "  4. Setup automated backups"
    echo ""
    echo "Monitoring:"
    echo "  Application logs: tail -f $LOGS_DIR/django.log"
    echo "  Gunicorn logs: tail -f $LOGS_DIR/gunicorn.log"
    echo "  Application status: sudo supervisorctl status staff-rota"
    echo ""
    echo "Management:"
    echo "  Restart app: sudo supervisorctl restart staff-rota"
    echo "  Stop app: sudo supervisorctl stop staff-rota"
    echo "  Start app: sudo supervisorctl start staff-rota"
    echo ""
    print_success "Deployment successful!"
}

# Main deployment flow
main() {
    echo ""
    print_header "Staff Rota System - Production Deployment"
    echo "Date: $(date)"
    echo "Working directory: $APP_DIR"
    echo ""
    
    read -p "Ready to deploy to production? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
    
    check_prerequisites
    create_directories
    backup_database
    install_dependencies
    run_migrations
    create_cache_table
    collect_static_files
    run_deployment_checks
    setup_supervisor
    verify_deployment
    print_summary
}

# Run main function
main
