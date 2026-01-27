#!/bin/bash
# Production Health Check Script for demo.therota.co.uk
# Run this from DigitalOcean Console after SSH login
# Date: 27 January 2026

echo "=========================================="
echo "PRODUCTION HEALTH CHECK - demo.therota.co.uk"
echo "=========================================="
echo ""

# 1. System Information
echo "1. SYSTEM INFORMATION"
echo "--------------------"
uname -a
uptime
echo ""

# 2. Disk Space
echo "2. DISK SPACE"
echo "-------------"
df -h | grep -E "Filesystem|/$|/var|/home"
echo ""

# 3. Memory Usage
echo "3. MEMORY USAGE"
echo "---------------"
free -h
echo ""

# 4. Find Django Project
echo "4. LOCATING DJANGO PROJECT"
echo "--------------------------"
echo "Searching for manage.py..."
find /home /var/www /opt -name "manage.py" -type f 2>/dev/null | grep -v venv | head -5
echo ""

# 5. Active Python Processes
echo "5. PYTHON PROCESSES"
echo "-------------------"
ps aux | grep python | grep -v grep | head -10
echo ""

# 6. Web Server Status
echo "6. WEB SERVER STATUS"
echo "--------------------"
echo "Checking Nginx..."
systemctl status nginx --no-pager -l | head -15
echo ""
echo "Checking Gunicorn/uWSGI..."
ps aux | grep -E "gunicorn|uwsgi" | grep -v grep
echo ""

# 7. Database Status  
echo "7. DATABASE STATUS"
echo "------------------"
systemctl status postgresql --no-pager -l | head -15
echo ""

# 8. Recent Logs (Last 20 lines)
echo "8. RECENT LOGS"
echo "--------------"
echo "Django logs:"
tail -20 /var/log/django/*.log 2>/dev/null || echo "No Django logs found in /var/log/django/"
echo ""
echo "Nginx error log:"
tail -20 /var/log/nginx/error.log 2>/dev/null || echo "No Nginx error logs"
echo ""

# 9. Port Listeners
echo "9. LISTENING PORTS"
echo "------------------"
netstat -tuln | grep -E "LISTEN|:80|:443|:8000|:5432" || ss -tuln | grep -E "LISTEN|:80|:443|:8000|:5432"
echo ""

# 10. Django Check Commands (need to CD to project first)
echo "10. DJANGO HEALTH (requires project path)"
echo "-----------------------------------------"
echo "After finding your Django project above, run these commands:"
echo "  cd /path/to/your/project"
echo "  source venv/bin/activate"
echo "  python manage.py check"
echo "  python manage.py showmigrations"
echo ""

echo "=========================================="
echo "HEALTH CHECK COMPLETE"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "1. Note your Django project path from section 4"
echo "2. CD to that directory"
echo "3. Run Django-specific checks"
echo "4. Test database connection"
