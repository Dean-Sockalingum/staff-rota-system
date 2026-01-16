"""
Management command to switch between DEMO and PRODUCTION modes.

Usage:
    python3 manage.py set_mode demo    # Switch to demo mode
    python3 manage.py set_mode prod    # Switch to production mode
    python3 manage.py set_mode status  # Check current mode
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Switch between DEMO and PRODUCTION modes'

    def add_arguments(self, parser):
        parser.add_argument(
            'mode',
            type=str,
            choices=['demo', 'prod', 'production', 'status'],
            help='Mode to switch to: demo, prod, or status to check current mode'
        )

    def handle(self, *args, **options):
        mode = options['mode']
        base_dir = settings.BASE_DIR
        
        # Database file paths
        demo_db = base_dir / 'db_demo.sqlite3'
        prod_db = base_dir / 'db_production.sqlite3'
        active_db = base_dir / 'db.sqlite3'
        
        # Mode indicator file
        mode_file = base_dir / '.current_mode'
        
        if mode == 'status':
            self._show_status(mode_file, active_db, demo_db, prod_db)
            return
        
        if mode == 'demo':
            self._switch_to_demo(demo_db, active_db, mode_file, base_dir)
        elif mode in ['prod', 'production']:
            self._switch_to_production(prod_db, active_db, mode_file)

    def _show_status(self, mode_file, active_db, demo_db, prod_db):
        """Display current mode and database information."""
        if mode_file.exists():
            current_mode = mode_file.read_text().strip()
        else:
            current_mode = 'UNKNOWN'
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"  CURRENT MODE: {current_mode}"))
        self.stdout.write("="*60 + "\n")
        
        # Database sizes
        if active_db.exists():
            size_mb = active_db.stat().st_size / (1024 * 1024)
            self.stdout.write(f"Active DB:  {active_db.name} ({size_mb:.2f} MB)")
        
        if demo_db.exists():
            size_mb = demo_db.stat().st_size / (1024 * 1024)
            self.stdout.write(f"Demo DB:    {demo_db.name} ({size_mb:.2f} MB)")
        else:
            self.stdout.write(self.style.WARNING("Demo DB:    Not created yet"))
        
        if prod_db.exists():
            size_mb = prod_db.stat().st_size / (1024 * 1024)
            self.stdout.write(f"Prod DB:    {prod_db.name} ({size_mb:.2f} MB)")
        else:
            self.stdout.write(self.style.WARNING("Prod DB:    Not created yet"))
        
        self.stdout.write("\n" + "="*60 + "\n")

    def _switch_to_demo(self, demo_db, active_db, mode_file, base_dir):
        """Switch to DEMO mode."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("  SWITCHING TO DEMO MODE"))
        self.stdout.write("="*60 + "\n")
        
        # Create demo database if it doesn't exist
        if not demo_db.exists():
            if active_db.exists():
                self.stdout.write("Creating demo database from current data...")
                shutil.copy2(active_db, demo_db)
                self.stdout.write(self.style.SUCCESS("✓ Demo database created"))
            else:
                self.stdout.write(self.style.ERROR("✗ No database found to copy"))
                return
        
        # Backup current active database
        if active_db.exists():
            backup_path = base_dir / f'db_backup_{mode_file.read_text().strip() if mode_file.exists() else "unknown"}.sqlite3'
            shutil.copy2(active_db, backup_path)
            self.stdout.write(f"✓ Backed up current database to {backup_path.name}")
        
        # Switch to demo database
        shutil.copy2(demo_db, active_db)
        mode_file.write_text('DEMO')
        
        self.stdout.write(self.style.SUCCESS("\n✅ DEMO MODE ACTIVATED"))
        self.stdout.write("\nYou are now using the DEMO database.")
        self.stdout.write("All changes will be isolated from production data.")
        self.stdout.write(self.style.WARNING("\nTo reset demo data: python3 manage.py reset_demo"))
        self.stdout.write("="*60 + "\n")

    def _switch_to_production(self, prod_db, active_db, mode_file):
        """Switch to PRODUCTION mode."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.WARNING("  SWITCHING TO PRODUCTION MODE"))
        self.stdout.write("="*60 + "\n")
        
        # Check if production database exists
        if not prod_db.exists():
            if active_db.exists():
                self.stdout.write(self.style.WARNING("Creating production database from current data..."))
                response = input("This will set current database as production. Continue? (yes/no): ")
                if response.lower() != 'yes':
                    self.stdout.write(self.style.ERROR("Cancelled."))
                    return
                shutil.copy2(active_db, prod_db)
                self.stdout.write(self.style.SUCCESS("✓ Production database created"))
            else:
                self.stdout.write(self.style.ERROR("✗ No database found"))
                return
        
        # Final confirmation
        self.stdout.write(self.style.WARNING("\n⚠️  WARNING: You are switching to PRODUCTION mode."))
        self.stdout.write("All changes will affect LIVE data.")
        response = input("\nType 'PRODUCTION' to confirm: ")
        
        if response != 'PRODUCTION':
            self.stdout.write(self.style.ERROR("Cancelled."))
            return
        
        # Switch to production database
        shutil.copy2(prod_db, active_db)
        mode_file.write_text('PRODUCTION')
        
        self.stdout.write(self.style.SUCCESS("\n✅ PRODUCTION MODE ACTIVATED"))
        self.stdout.write(self.style.WARNING("\n⚠️  You are now using LIVE production data!"))
        self.stdout.write("="*60 + "\n")
