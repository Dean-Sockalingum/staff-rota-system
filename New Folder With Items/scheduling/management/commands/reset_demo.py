"""
Management command to reset DEMO database to clean state.

Usage:
    python3 manage.py reset_demo           # Reset to original demo data
    python3 manage.py reset_demo --fresh   # Create completely fresh demo data
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import shutil
from pathlib import Path


class Command(BaseCommand):
    help = 'Reset DEMO database to clean state'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fresh',
            action='store_true',
            help='Create fresh demo data from production backup'
        )

    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        
        # Check current mode
        mode_file = base_dir / '.current_mode'
        if mode_file.exists():
            current_mode = mode_file.read_text().strip()
            if current_mode != 'DEMO':
                self.stdout.write(self.style.ERROR("\n✗ Cannot reset: Not in DEMO mode"))
                self.stdout.write(f"Current mode: {current_mode}")
                self.stdout.write("\nSwitch to demo mode first: python3 manage.py set_mode demo\n")
                return
        else:
            self.stdout.write(self.style.WARNING("\n⚠️  Mode unknown. Proceeding with caution...\n"))
        
        demo_db = base_dir / 'db_demo.sqlite3'
        active_db = base_dir / 'db.sqlite3'
        prod_db = base_dir / 'db_production.sqlite3'
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("  RESET DEMO DATABASE"))
        self.stdout.write("="*60 + "\n")
        
        if options['fresh']:
            # Create fresh demo from production backup
            if prod_db.exists():
                self.stdout.write("Creating fresh demo data from production backup...")
                shutil.copy2(prod_db, demo_db)
                shutil.copy2(prod_db, active_db)
                self.stdout.write(self.style.SUCCESS("✓ Fresh demo database created from production backup"))
            else:
                self.stdout.write(self.style.ERROR("✗ No production backup found"))
                return
        else:
            # Reset to original demo data
            if demo_db.exists():
                # Create a snapshot before resetting
                snapshot = base_dir / f'db_demo_snapshot_{Path(demo_db).stat().st_mtime:.0f}.sqlite3'
                shutil.copy2(active_db, snapshot)
                self.stdout.write(f"✓ Created snapshot: {snapshot.name}")
                
                # Reset to clean demo state
                shutil.copy2(demo_db, active_db)
                self.stdout.write(self.style.SUCCESS("✓ Demo database reset to clean state"))
            else:
                self.stdout.write(self.style.ERROR("✗ Demo database not found"))
                return
        
        self.stdout.write(self.style.SUCCESS("\n✅ DEMO DATABASE RESET COMPLETE"))
        self.stdout.write("All demo data has been restored to clean state.")
        self.stdout.write("="*60 + "\n")
