#!/bin/bash
#
# Email Configuration Setup Script
# This script helps you configure production email settings securely
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║        Staff Rota - Email Configuration Setup             ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect shell config file
SHELL_CONFIG=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -f "$HOME/.bash_profile" ]; then
    SHELL_CONFIG="$HOME/.bash_profile"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    echo -e "${RED}Error: Could not find shell configuration file${NC}"
    echo "Please manually add environment variables to your shell config"
    exit 1
fi

echo -e "${CYAN}Shell configuration file: ${SHELL_CONFIG}${NC}"
echo ""

# Check current email configuration
echo -e "${BLUE}Current Email Configuration:${NC}"
if [ -z "$EMAIL_HOST" ]; then
    echo -e "  Mode: ${YELLOW}Console/Testing${NC} (emails print to terminal)"
else
    echo -e "  Mode: ${GREEN}Production SMTP${NC}"
    echo "  Host: $EMAIL_HOST"
    echo "  Port: ${EMAIL_PORT:-587}"
    echo "  User: $EMAIL_USER"
    echo "  From: ${DEFAULT_FROM_EMAIL:-Not set}"
fi
echo ""

# Menu
echo -e "${BLUE}What would you like to do?${NC}"
echo "  1) Configure Gmail SMTP"
echo "  2) Configure Office 365 SMTP"
echo "  3) Configure Custom SMTP"
echo "  4) Switch to Console/Testing mode (disable SMTP)"
echo "  5) Test current email configuration"
echo "  6) View current settings"
echo "  7) Exit"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}═══ Gmail SMTP Configuration ═══${NC}"
        echo ""
        echo -e "${YELLOW}Before continuing:${NC}"
        echo "1. Go to: https://myaccount.google.com/apppasswords"
        echo "2. Generate an App Password (16-character password)"
        echo "3. Have your Gmail address ready"
        echo ""
        read -p "Press Enter when ready..."
        echo ""
        
        read -p "Gmail address: " gmail_user
        read -s -p "App password (16 chars): " gmail_pass
        echo ""
        read -p "From name [Staff Rota System]: " from_name
        from_name=${from_name:-Staff Rota System}
        
        # Add to shell config
        echo "" >> "$SHELL_CONFIG"
        echo "# Staff Rota Email Configuration (Gmail)" >> "$SHELL_CONFIG"
        echo "export EMAIL_HOST=\"smtp.gmail.com\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_PORT=\"587\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_USE_TLS=\"True\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_USER=\"$gmail_user\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_PASSWORD=\"$gmail_pass\"" >> "$SHELL_CONFIG"
        echo "export DEFAULT_FROM_EMAIL=\"$from_name <$gmail_user>\"" >> "$SHELL_CONFIG"
        
        # Set for current session
        export EMAIL_HOST="smtp.gmail.com"
        export EMAIL_PORT="587"
        export EMAIL_USE_TLS="True"
        export EMAIL_USER="$gmail_user"
        export EMAIL_PASSWORD="$gmail_pass"
        export DEFAULT_FROM_EMAIL="$from_name <$gmail_user>"
        
        echo ""
        echo -e "${GREEN}✅ Gmail SMTP configured!${NC}"
        echo ""
        echo -e "${YELLOW}Important:${NC} Run this command to apply changes:"
        echo -e "  ${CYAN}source $SHELL_CONFIG${NC}"
        ;;
    
    2)
        echo ""
        echo -e "${GREEN}═══ Office 365 SMTP Configuration ═══${NC}"
        echo ""
        
        read -p "Office 365 email: " o365_user
        read -s -p "Password: " o365_pass
        echo ""
        read -p "From name [Staff Rota System]: " from_name
        from_name=${from_name:-Staff Rota System}
        
        # Add to shell config
        echo "" >> "$SHELL_CONFIG"
        echo "# Staff Rota Email Configuration (Office 365)" >> "$SHELL_CONFIG"
        echo "export EMAIL_HOST=\"smtp.office365.com\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_PORT=\"587\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_USE_TLS=\"True\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_USER=\"$o365_user\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_PASSWORD=\"$o365_pass\"" >> "$SHELL_CONFIG"
        echo "export DEFAULT_FROM_EMAIL=\"$from_name <$o365_user>\"" >> "$SHELL_CONFIG"
        
        # Set for current session
        export EMAIL_HOST="smtp.office365.com"
        export EMAIL_PORT="587"
        export EMAIL_USE_TLS="True"
        export EMAIL_USER="$o365_user"
        export EMAIL_PASSWORD="$o365_pass"
        export DEFAULT_FROM_EMAIL="$from_name <$o365_user>"
        
        echo ""
        echo -e "${GREEN}✅ Office 365 SMTP configured!${NC}"
        echo ""
        echo -e "${YELLOW}Important:${NC} Run this command to apply changes:"
        echo -e "  ${CYAN}source $SHELL_CONFIG${NC}"
        ;;
    
    3)
        echo ""
        echo -e "${GREEN}═══ Custom SMTP Configuration ═══${NC}"
        echo ""
        
        read -p "SMTP host: " smtp_host
        read -p "SMTP port [587]: " smtp_port
        smtp_port=${smtp_port:-587}
        read -p "Use TLS? [Y/n]: " use_tls
        use_tls=${use_tls:-Y}
        if [[ $use_tls == [yY] || $use_tls == [yY][eE][sS] ]]; then
            use_tls="True"
        else
            use_tls="False"
        fi
        read -p "Email address: " email_user
        read -s -p "Password: " email_pass
        echo ""
        read -p "From name [Staff Rota System]: " from_name
        from_name=${from_name:-Staff Rota System}
        
        # Add to shell config
        echo "" >> "$SHELL_CONFIG"
        echo "# Staff Rota Email Configuration (Custom SMTP)" >> "$SHELL_CONFIG"
        echo "export EMAIL_HOST=\"$smtp_host\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_PORT=\"$smtp_port\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_USE_TLS=\"$use_tls\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_USER=\"$email_user\"" >> "$SHELL_CONFIG"
        echo "export EMAIL_PASSWORD=\"$email_pass\"" >> "$SHELL_CONFIG"
        echo "export DEFAULT_FROM_EMAIL=\"$from_name <$email_user>\"" >> "$SHELL_CONFIG"
        
        # Set for current session
        export EMAIL_HOST="$smtp_host"
        export EMAIL_PORT="$smtp_port"
        export EMAIL_USE_TLS="$use_tls"
        export EMAIL_USER="$email_user"
        export EMAIL_PASSWORD="$email_pass"
        export DEFAULT_FROM_EMAIL="$from_name <$email_user>"
        
        echo ""
        echo -e "${GREEN}✅ Custom SMTP configured!${NC}"
        echo ""
        echo -e "${YELLOW}Important:${NC} Run this command to apply changes:"
        echo -e "  ${CYAN}source $SHELL_CONFIG${NC}"
        ;;
    
    4)
        echo ""
        echo -e "${YELLOW}Switching to Console/Testing mode...${NC}"
        
        # Comment out email vars in shell config
        if grep -q "EMAIL_HOST=" "$SHELL_CONFIG" 2>/dev/null; then
            # Create backup
            cp "$SHELL_CONFIG" "${SHELL_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Comment out email configuration
            sed -i.tmp 's/^export EMAIL_HOST=/#export EMAIL_HOST=/' "$SHELL_CONFIG"
            sed -i.tmp 's/^export EMAIL_PORT=/#export EMAIL_PORT=/' "$SHELL_CONFIG"
            sed -i.tmp 's/^export EMAIL_USE_TLS=/#export EMAIL_USE_TLS=/' "$SHELL_CONFIG"
            sed -i.tmp 's/^export EMAIL_USER=/#export EMAIL_USER=/' "$SHELL_CONFIG"
            sed -i.tmp 's/^export EMAIL_PASSWORD=/#export EMAIL_PASSWORD=/' "$SHELL_CONFIG"
            sed -i.tmp 's/^export DEFAULT_FROM_EMAIL=/#export DEFAULT_FROM_EMAIL=/' "$SHELL_CONFIG"
            rm -f "${SHELL_CONFIG}.tmp"
            
            # Unset for current session
            unset EMAIL_HOST EMAIL_PORT EMAIL_USE_TLS EMAIL_USER EMAIL_PASSWORD DEFAULT_FROM_EMAIL
            
            echo -e "${GREEN}✅ Switched to console mode${NC}"
            echo "Emails will now print to terminal instead of sending"
            echo ""
            echo -e "${YELLOW}Important:${NC} Run this command to apply changes:"
            echo -e "  ${CYAN}source $SHELL_CONFIG${NC}"
        else
            echo "Already in console mode (no EMAIL_HOST configured)"
        fi
        ;;
    
    5)
        echo ""
        echo -e "${GREEN}Testing email configuration...${NC}"
        echo ""
        
        cd "/Users/deansockalingum/Staff Rota/rotasystems"
        
        if [ -z "$EMAIL_HOST" ]; then
            echo -e "${YELLOW}Console mode active${NC} - Running dry-run test"
            python3 manage.py send_leave_reminders --specific-staff ADMIN001 --dry-run
        else
            echo -e "${GREEN}SMTP mode active${NC} - Sending test email to ADMIN001"
            echo ""
            read -p "Send real test email? (y/N): " confirm
            if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
                python3 manage.py send_leave_reminders --specific-staff ADMIN001
                echo ""
                echo -e "${GREEN}✅ Test email sent!${NC}"
                echo "Check ADMIN001's inbox"
            else
                echo "Test cancelled"
            fi
        fi
        ;;
    
    6)
        echo ""
        echo -e "${GREEN}Current Email Settings:${NC}"
        echo ""
        echo "EMAIL_HOST:           ${EMAIL_HOST:-[Not set - Console mode]}"
        echo "EMAIL_PORT:           ${EMAIL_PORT:-[Not set]}"
        echo "EMAIL_USE_TLS:        ${EMAIL_USE_TLS:-[Not set]}"
        echo "EMAIL_USER:           ${EMAIL_USER:-[Not set]}"
        echo "EMAIL_PASSWORD:       ${EMAIL_PASSWORD:+[Set - Hidden]}"
        echo "DEFAULT_FROM_EMAIL:   ${DEFAULT_FROM_EMAIL:-[Not set]}"
        echo ""
        
        if [ -z "$EMAIL_HOST" ]; then
            echo -e "${YELLOW}Mode: Console/Testing${NC}"
            echo "Emails will print to terminal"
        else
            echo -e "${GREEN}Mode: Production SMTP${NC}"
            echo "Emails will be sent via SMTP"
        fi
        ;;
    
    7)
        echo "Exiting..."
        exit 0
        ;;
    
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo ""
