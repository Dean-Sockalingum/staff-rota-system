#!/usr/bin/env python3
"""
Production Configuration Validator
Validates that all critical security and configuration settings are properly set
for production deployment.

Run this script BEFORE deploying to production:
    python3 validate_production_config.py
"""

import os
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text):
    """Print formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_pass(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_fail(message):
    """Print failure message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warn(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def load_env_file(file_path):
    """Load environment variables from .env file"""
    env_vars = {}
    if not os.path.exists(file_path):
        return env_vars
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


def validate_critical_settings(env_vars):
    """Validate critical security settings"""
    print_header("CRITICAL SECURITY SETTINGS")
    
    critical_passed = True
    
    # Check DEBUG mode
    debug = env_vars.get('DEBUG', 'True')
    if debug.lower() in ['false', '0', 'no']:
        print_pass(f"DEBUG mode disabled: {debug}")
    else:
        print_fail(f"DEBUG mode MUST be False in production. Current: {debug}")
        critical_passed = False
    
    # Check SECRET_KEY
    secret_key = env_vars.get('SECRET_KEY', '')
    if '<GENERATED_SECRET_KEY_HERE>' in secret_key or '<' in secret_key:
        print_fail("SECRET_KEY contains placeholder - must be replaced with generated key")
        critical_passed = False
    elif len(secret_key) < 50:
        print_fail(f"SECRET_KEY too short ({len(secret_key)} chars) - should be at least 50 characters")
        critical_passed = False
    elif secret_key == 'django-insecure-' or 'insecure' in secret_key.lower():
        print_fail("SECRET_KEY appears to be development key - must generate new production key")
        critical_passed = False
    else:
        print_pass(f"SECRET_KEY set ({len(secret_key)} characters)")
    
    # Check ALLOWED_HOSTS
    allowed_hosts = env_vars.get('ALLOWED_HOSTS', '')
    if '<YOUR_PRODUCTION_DOMAIN>' in allowed_hosts or '<' in allowed_hosts:
        print_fail("ALLOWED_HOSTS contains placeholders - must be set to actual domain(s)")
        critical_passed = False
    elif not allowed_hosts or allowed_hosts == '':
        print_fail("ALLOWED_HOSTS is empty - must include production domain")
        critical_passed = False
    else:
        hosts = allowed_hosts.split(',')
        print_pass(f"ALLOWED_HOSTS configured ({len(hosts)} host(s)): {', '.join(hosts)}")
    
    # Check CSRF_TRUSTED_ORIGINS
    csrf_origins = env_vars.get('CSRF_TRUSTED_ORIGINS', '')
    if '<YOUR_PRODUCTION_DOMAIN>' in csrf_origins or '<' in csrf_origins:
        print_fail("CSRF_TRUSTED_ORIGINS contains placeholders")
        critical_passed = False
    elif not csrf_origins or csrf_origins == '':
        print_warn("CSRF_TRUSTED_ORIGINS is empty - may cause CSRF validation issues")
    elif not all(origin.startswith('https://') for origin in csrf_origins.split(',')):
        print_fail("CSRF_TRUSTED_ORIGINS must use https:// protocol")
        critical_passed = False
    else:
        origins = csrf_origins.split(',')
        print_pass(f"CSRF_TRUSTED_ORIGINS configured ({len(origins)} origin(s))")
    
    return critical_passed


def validate_database_config(env_vars):
    """Validate database configuration"""
    print_header("DATABASE CONFIGURATION")
    
    db_passed = True
    
    db_engine = env_vars.get('DB_ENGINE', 'django.db.backends.sqlite3')
    
    if 'sqlite' in db_engine.lower():
        print_warn("Using SQLite - PostgreSQL recommended for production")
        db_name = env_vars.get('DB_NAME', '')
        if db_name:
            print_info(f"SQLite database: {db_name}")
    elif 'postgresql' in db_engine.lower():
        print_pass("Using PostgreSQL database engine")
        
        # Check PostgreSQL credentials
        db_name = env_vars.get('DB_NAME', '')
        db_user = env_vars.get('DB_USER', '')
        db_password = env_vars.get('DB_PASSWORD', '')
        db_host = env_vars.get('DB_HOST', 'localhost')
        db_port = env_vars.get('DB_PORT', '5432')
        
        if '<POSTGRES_USERNAME>' in db_user or '<' in db_user:
            print_fail("DB_USER contains placeholder")
            db_passed = False
        else:
            print_pass(f"Database user: {db_user}")
        
        if '<SECURE_POSTGRES_PASSWORD>' in db_password or '<' in db_password:
            print_fail("DB_PASSWORD contains placeholder")
            db_passed = False
        elif len(db_password) < 12:
            print_warn(f"Database password is short ({len(db_password)} chars) - recommend 16+ characters")
        else:
            print_pass("Database password configured")
        
        print_info(f"Database name: {db_name}")
        print_info(f"Database host: {db_host}:{db_port}")
    
    return db_passed


def validate_security_headers(env_vars):
    """Validate security headers and SSL settings"""
    print_header("SECURITY HEADERS & SSL")
    
    security_passed = True
    
    # Check session security
    session_secure = env_vars.get('SESSION_COOKIE_SECURE', 'False')
    if session_secure.lower() in ['true', '1', 'yes']:
        print_pass("SESSION_COOKIE_SECURE enabled")
    else:
        print_fail("SESSION_COOKIE_SECURE should be True")
        security_passed = False
    
    # Check CSRF security
    csrf_secure = env_vars.get('CSRF_COOKIE_SECURE', 'False')
    if csrf_secure.lower() in ['true', '1', 'yes']:
        print_pass("CSRF_COOKIE_SECURE enabled")
    else:
        print_fail("CSRF_COOKIE_SECURE should be True")
        security_passed = False
    
    # Check SSL redirect
    ssl_redirect = env_vars.get('SECURE_SSL_REDIRECT', 'False')
    if ssl_redirect.lower() in ['true', '1', 'yes']:
        print_pass("SECURE_SSL_REDIRECT enabled")
    else:
        print_warn("SECURE_SSL_REDIRECT not enabled - HTTP requests won't redirect to HTTPS")
    
    # Check HSTS
    hsts_seconds = env_vars.get('SECURE_HSTS_SECONDS', '0')
    try:
        hsts_value = int(hsts_seconds)
        if hsts_value >= 31536000:  # 1 year
            print_pass(f"SECURE_HSTS_SECONDS set to {hsts_value} (1 year)")
        elif hsts_value > 0:
            print_warn(f"SECURE_HSTS_SECONDS set to {hsts_value} - recommend 31536000 (1 year)")
        else:
            print_warn("SECURE_HSTS_SECONDS not set - HSTS not enabled")
    except ValueError:
        print_warn("SECURE_HSTS_SECONDS invalid value")
    
    return security_passed


def validate_email_config(env_vars):
    """Validate email configuration"""
    print_header("EMAIL CONFIGURATION")
    
    email_backend = env_vars.get('EMAIL_BACKEND', '')
    
    if 'console' in email_backend.lower():
        print_warn("Using console email backend - emails will print to console only")
        print_info("This is OK for testing, but configure SMTP for production notifications")
        return True
    elif 'smtp' in email_backend.lower():
        print_pass("Using SMTP email backend")
        
        email_host = env_vars.get('EMAIL_HOST', '')
        email_user = env_vars.get('EMAIL_HOST_USER', '')
        email_password = env_vars.get('EMAIL_HOST_PASSWORD', '')
        
        if '<HSCP_EMAIL_ADDRESS>' in email_user or '<' in email_user:
            print_warn("EMAIL_HOST_USER contains placeholder - configure when ready for email notifications")
        else:
            print_pass(f"Email user configured: {email_user}")
        
        if '<EMAIL_APP_PASSWORD>' in email_password or '<' in email_password:
            print_warn("EMAIL_HOST_PASSWORD contains placeholder")
        else:
            print_pass("Email password configured")
        
        if email_host:
            print_info(f"SMTP host: {email_host}")
    else:
        print_info("Email backend not configured - this is optional until HSCP/CGI approval")
    
    return True


def validate_static_media_paths(env_vars):
    """Validate static and media file paths"""
    print_header("STATIC & MEDIA FILES")
    
    paths_ok = True
    
    static_root = env_vars.get('STATIC_ROOT', '')
    media_root = env_vars.get('MEDIA_ROOT', '')
    
    if static_root:
        print_info(f"STATIC_ROOT: {static_root}")
        if os.path.exists(static_root):
            print_pass(f"Static files directory exists")
        else:
            print_warn(f"Static files directory does not exist yet - will be created during deployment")
    else:
        print_warn("STATIC_ROOT not configured")
    
    if media_root:
        print_info(f"MEDIA_ROOT: {media_root}")
        if os.path.exists(media_root):
            print_pass(f"Media files directory exists")
        else:
            print_warn(f"Media files directory does not exist yet - will be created during deployment")
    else:
        print_warn("MEDIA_ROOT not configured")
    
    return paths_ok


def validate_logging_config(env_vars):
    """Validate logging configuration"""
    print_header("LOGGING CONFIGURATION")
    
    log_level = env_vars.get('LOG_LEVEL', 'INFO')
    log_dir = env_vars.get('LOG_DIR', '')
    
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level.upper() in valid_levels:
        print_pass(f"Log level: {log_level}")
    else:
        print_warn(f"Invalid log level: {log_level} (should be one of {', '.join(valid_levels)})")
    
    if log_dir:
        print_info(f"Log directory: {log_dir}")
        if os.path.exists(log_dir):
            print_pass("Log directory exists")
        else:
            print_warn("Log directory does not exist yet - will be created during deployment")
    else:
        print_warn("LOG_DIR not configured - logs may not be persisted")
    
    return True


def main():
    """Main validation routine"""
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     PRODUCTION CONFIGURATION VALIDATOR                     ║")
    print("║     Staff Rota System - HSCP                               ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # Look for .env.production file
    env_file = Path('.env.production')
    if not env_file.exists():
        env_file = Path('.env')
        if not env_file.exists():
            print_fail("No .env.production or .env file found!")
            print_info("Create .env.production from .env.production.template")
            sys.exit(1)
        else:
            print_warn("Using .env file (should use .env.production for production)")
    else:
        print_pass(f"Using production environment file: {env_file}")
    
    # Load environment variables
    env_vars = load_env_file(str(env_file))
    print_info(f"Loaded {len(env_vars)} configuration variables\n")
    
    # Run validation checks
    results = {
        'critical': validate_critical_settings(env_vars),
        'database': validate_database_config(env_vars),
        'security': validate_security_headers(env_vars),
        'email': validate_email_config(env_vars),
        'static': validate_static_media_paths(env_vars),
        'logging': validate_logging_config(env_vars),
    }
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    critical_failed = not results['critical']
    has_warnings = not all(results.values())
    
    if critical_failed:
        print_fail("CRITICAL FAILURES - DO NOT DEPLOY TO PRODUCTION")
        print_info("Fix all critical security settings before deployment")
        sys.exit(1)
    elif has_warnings:
        print_warn("VALIDATION PASSED WITH WARNINGS")
        print_info("Review warnings above - some may be acceptable depending on deployment plan")
        print_info("All critical security settings are configured correctly")
        sys.exit(0)
    else:
        print_pass("ALL VALIDATION CHECKS PASSED")
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Configuration is ready for production deployment{Colors.END}\n")
        sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation cancelled by user{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}\n")
        sys.exit(1)
