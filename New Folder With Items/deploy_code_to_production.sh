#!/usr/bin/expect -f
# Deploy all code files to production server
# This handles CODE deployment. Use replicate_demo_to_production.sh for DATA.

set timeout 300
set password "staffRota2026TQM"
set server "159.65.18.80"
set app_dir "/home/staff-rota-system"

# Color output
proc info {msg} { puts "\033\[1;34m\[INFO\] $msg\033\[0m" }
proc success {msg} { puts "\033\[1;32m\[SUCCESS\] $msg\033\[0m" }
proc error {msg} { puts "\033\[1;31m\[ERROR\] $msg\033\[0m" }

info "Starting code deployment to production..."

# Change to project directory
cd "2025-12-12_Multi-Home_Complete"

# 1. Upload all Python files in scheduling/
info "Uploading scheduling module files..."
spawn rsync -avz --exclude='__pycache__' --exclude='*.pyc' scheduling/ root@$server:$app_dir/scheduling/
expect {
    "password:" { send "$password\r" }
    timeout { error "Timeout uploading scheduling files"; exit 1 }
}
expect eof
success "Scheduling files uploaded"

# 2. Upload rotasystems configuration
info "Uploading rotasystems configuration..."
spawn rsync -avz --exclude='__pycache__' --exclude='*.pyc' rotasystems/ root@$server:$app_dir/rotasystems/
expect {
    "password:" { send "$password\r" }
    timeout { error "Timeout uploading rotasystems files"; exit 1 }
}
expect eof
success "Rotasystems files uploaded"

# 3. Upload requirements.txt
info "Uploading requirements.txt..."
spawn scp requirements.txt root@$server:$app_dir/
expect {
    "password:" { send "$password\r" }
    timeout { error "Timeout uploading requirements"; exit 1 }
}
expect eof
success "Requirements uploaded"

# 4. Upload manage.py
info "Uploading manage.py..."
spawn scp manage.py root@$server:$app_dir/
expect {
    "password:" { send "$password\r" }
    timeout { error "Timeout uploading manage.py"; exit 1 }
}
expect eof
success "Manage.py uploaded"

# 5. Install/update dependencies
info "Installing Python dependencies..."
spawn ssh root@$server
expect {
    "password:" { send "$password\r" }
    timeout { error "Timeout connecting to server"; exit 1 }
}

expect "# "
send "cd $app_dir\r"
expect "# "
send "source venv/bin/activate\r"
expect "# "
send "pip install -r requirements.txt --quiet\r"
expect "# " { success "Dependencies installed" }

# 6. Collect static files
info "Collecting static files..."
send "python manage.py collectstatic --noinput\r"
expect "# " { success "Static files collected" }

# 7. Run migrations
info "Running database migrations..."
send "python manage.py migrate\r"
expect "# " { success "Migrations complete" }

# 8. Restart Gunicorn
info "Restarting Gunicorn..."
send "pkill -f gunicorn\r"
expect "# "
sleep 2
send "cd $app_dir\r"
expect "# "
send "source venv/bin/activate\r"
expect "# "
send "nohup gunicorn --workers 3 --bind unix:$app_dir/staffrota.sock rotasystems.wsgi:application --log-file=$app_dir/logs/gunicorn.log --access-logfile=$app_dir/logs/gunicorn-access.log --error-logfile=$app_dir/logs/gunicorn-error.log --daemon\r"
expect "# " { success "Gunicorn restarted" }

# 9. Verify it's running
sleep 3
send "ps aux | grep gunicorn | grep -v grep\r"
expect "# "
send "exit\r"

success "\n========================================="
success "Code deployment complete!"
success "=========================================\n"
success "Next steps:"
info "1. Test: https://demo.therota.co.uk/compliance/audit-trail/"
info "2. Test: https://demo.therota.co.uk/compliance/training/management/"
info "3. If data needs updating, run: ./replicate_demo_to_production.sh"

expect eof
