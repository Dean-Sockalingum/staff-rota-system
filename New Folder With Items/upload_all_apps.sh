#!/usr/bin/expect -f
# Upload all missing Django apps to production

set timeout 600
set password "staffRota2026TQM"
set server "159.65.18.80"
set app_dir "/home/staff-rota-system"

proc info {msg} { puts "\033\[1;34m\[INFO\] $msg\033\[0m" }
proc success {msg} { puts "\033\[1;32m\[SUCCESS\] $msg\033\[0m" }

cd "2025-12-12_Multi-Home_Complete"

# Upload all Django app directories
set apps {quality_audits policies_procedures incident_safety staff_records staff_guidance training_competency risk_management document_management experience_feedback performance_kpis docs tools}

foreach app $apps {
    info "Uploading $app..."
    spawn rsync -avz --exclude='__pycache__' --exclude='*.pyc' $app/ root@$server:$app_dir/$app/
    expect {
        "password:" { send "$password\r" }
        timeout { puts "Timeout uploading $app"; continue }
    }
    expect eof
    success "$app uploaded"
}

info "All Django apps uploaded successfully!"
