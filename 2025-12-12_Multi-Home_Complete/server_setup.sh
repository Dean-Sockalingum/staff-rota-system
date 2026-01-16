#!/bin/bash
#
# Staff Rota System - Automated Server Setup Script
# Version: 1.0
# Last Updated: December 28, 2025
#
# This script automates the initial server setup for both staging and production environments.
# Run this script on a fresh Ubuntu 20.04+ server.
#
# Usage:
#   sudo ./server_setup.sh staging
#   sudo ./server_setup.sh production
#

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.14"
ENVIRONMENT="${1:-staging}"  # staging or production

if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo -e "${RED}Error: Environment must be 'staging' or 'production'${NC}"
    echo "Usage: sudo ./server_setup.sh [staging|production]"
    exit 1
fi

APP_NAME="staff-rota-${ENVIRONMENT}"
DEPLOY_USER="deploy-user"
APP_DIR="/var/www/${APP_NAME}"
LOG_DIR="/var/log/${APP_NAME}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Staff Rota System - Server Setup${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}========================================${NC}"

# Update system
echo -e "${YELLOW}[1/10] Updating system packages...${NC}"
apt update && apt upgrade -y

# Install Python 3.14
echo -e "${YELLOW}[2/10] Installing Python ${PYTHON_VERSION}...${NC}"
add-apt-repository ppa:deadsnakes/ppa -y
apt update
apt install -y \
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev

# Install system dependencies
echo -e "${YELLOW}[3/10] Installing system dependencies...${NC}"
apt install -y \
    nginx \
    supervisor \
    git \
    build-essential \
    libpq-dev \
    sqlite3 \
    curl \
    ufw \
    fail2ban \
    certbot \
    python3-certbot-nginx

# Create deployment user
echo -e "${YELLOW}[4/10] Creating deployment user...${NC}"
if ! id "$DEPLOY_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$DEPLOY_USER"
    usermod -aG www-data "$DEPLOY_USER"
    echo -e "${GREEN}Created user: ${DEPLOY_USER}${NC}"
else
    echo -e "${YELLOW}User ${DEPLOY_USER} already exists${NC}"
fi

# Create application directory
echo -e "${YELLOW}[5/10] Setting up application directory...${NC}"
mkdir -p "$APP_DIR"
chown "$DEPLOY_USER:www-data" "$APP_DIR"
chmod 755 "$APP_DIR"

# Create log directory
mkdir -p "$LOG_DIR"
chown "$DEPLOY_USER:www-data" "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Create virtual environment
echo -e "${YELLOW}[6/10] Creating Python virtual environment...${NC}"
su - "$DEPLOY_USER" -c "cd $APP_DIR && python${PYTHON_VERSION} -m venv venv"

# Install gunicorn
echo -e "${YELLOW}[7/10] Installing gunicorn...${NC}"
su - "$DEPLOY_USER" -c "$APP_DIR/venv/bin/pip install gunicorn"

# Create systemd service
echo -e "${YELLOW}[8/10] Creating systemd service...${NC}"
cat > "/etc/systemd/system/${APP_NAME}.service" << EOF
[Unit]
Description=Staff Rota System - ${ENVIRONMENT^}
After=network.target

[Service]
Type=notify
User=$DEPLOY_USER
Group=www-data
WorkingDirectory=$APP_DIR/current
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn \\
    --workers 3 \\
    --bind unix:$APP_DIR/staff-rota.sock \\
    --access-logfile $LOG_DIR/access.log \\
    --error-logfile $LOG_DIR/error.log \\
    --timeout 120 \\
    rotasystems.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${APP_NAME}.service"

# Configure Nginx
echo -e "${YELLOW}[9/10] Configuring Nginx...${NC}"

# Prompt for domain
read -p "Enter domain name for ${ENVIRONMENT} (e.g., ${ENVIRONMENT}.yourdomain.com): " DOMAIN_NAME

cat > "/etc/nginx/sites-available/${APP_NAME}" << EOF
server {
    listen 80;
    server_name ${DOMAIN_NAME};

    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect to HTTPS (will be enabled after SSL setup)
    # return 301 https://\$server_name\$request_uri;

    # Temporary HTTP access
    client_max_body_size 10M;

    location /static/ {
        alias $APP_DIR/current/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias $APP_DIR/current/media/;
        expires 7d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/staff-rota.sock;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_redirect off;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
EOF

# Enable Nginx site
ln -sf "/etc/nginx/sites-available/${APP_NAME}" "/etc/nginx/sites-enabled/"
nginx -t
systemctl reload nginx

# Configure firewall
echo -e "${YELLOW}[10/10] Configuring firewall...${NC}"
ufw allow OpenSSH
ufw allow 'Nginx Full'
echo "y" | ufw enable

# Setup fail2ban
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Setup log rotation
cat > "/etc/logrotate.d/${APP_NAME}" << EOF
$LOG_DIR/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 $DEPLOY_USER www-data
    sharedscripts
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF

# Create deployment script
cat > "$APP_DIR/deploy.sh" << 'DEPLOYSCRIPT'
#!/bin/bash
set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
APP_DIR=$(dirname "$0")
RELEASE_DIR="$APP_DIR/releases/$TIMESTAMP"

echo "🚀 Starting deployment..."

# Create release directory
mkdir -p "$RELEASE_DIR"
echo "✓ Created release directory: $RELEASE_DIR"

# Extract uploaded package
if [ -f "$APP_DIR/staging-release.tar.gz" ]; then
    tar -xzf "$APP_DIR/staging-release.tar.gz" -C "$RELEASE_DIR"
    echo "✓ Extracted release package"
elif [ -f "$APP_DIR/production-release.tar.gz" ]; then
    tar -xzf "$APP_DIR/production-release.tar.gz" -C "$RELEASE_DIR"
    echo "✓ Extracted release package"
else
    echo "❌ No release package found"
    exit 1
fi

# Backup current version
if [ -L "$APP_DIR/current" ]; then
    CURRENT_TARGET=$(readlink -f "$APP_DIR/current")
    cp -r "$CURRENT_TARGET" "$APP_DIR/backup_$TIMESTAMP"
    echo "✓ Backed up current version"
fi

# Update symlink
ln -sfn "$RELEASE_DIR" "$APP_DIR/current"
echo "✓ Updated symlink to new release"

# Activate virtual environment and install dependencies
source "$APP_DIR/venv/bin/activate"
cd "$APP_DIR/current"

pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Installed dependencies"

# Run migrations
python manage.py migrate --noinput
echo "✓ Applied database migrations"

# Collect static files
python manage.py collectstatic --noinput
echo "✓ Collected static files"

# Restart application
sudo systemctl restart staff-rota-staging || sudo systemctl restart staff-rota-production
echo "✓ Restarted application"

# Cleanup old releases (keep last 5)
cd "$APP_DIR/releases"
ls -t | tail -n +6 | xargs -r rm -rf
echo "✓ Cleaned up old releases"

echo "✅ Deployment complete!"
DEPLOYSCRIPT

chmod +x "$APP_DIR/deploy.sh"
chown "$DEPLOY_USER:www-data" "$APP_DIR/deploy.sh"

# Setup SSH for deployment user
echo -e "${YELLOW}Setting up SSH for ${DEPLOY_USER}...${NC}"
su - "$DEPLOY_USER" -c "mkdir -p ~/.ssh && chmod 700 ~/.ssh && touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server setup complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add GitHub Actions SSH public key to /home/${DEPLOY_USER}/.ssh/authorized_keys"
echo "2. Setup SSL certificate:"
echo "   sudo certbot --nginx -d ${DOMAIN_NAME}"
echo "3. Create .env file in ${APP_DIR}/current/ with configuration"
echo "4. Update Nginx config to enable HTTPS redirect"
echo "5. Test deployment from GitHub Actions"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  sudo systemctl status ${APP_NAME}     # Check service status"
echo "  sudo journalctl -u ${APP_NAME} -f     # View logs"
echo "  sudo systemctl restart ${APP_NAME}    # Restart application"
echo "  sudo nginx -t                          # Test Nginx config"
echo "  sudo systemctl reload nginx            # Reload Nginx"
echo ""
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}App Directory: ${APP_DIR}${NC}"
echo -e "${GREEN}Deploy User: ${DEPLOY_USER}${NC}"
echo -e "${GREEN}Domain: ${DOMAIN_NAME}${NC}"
