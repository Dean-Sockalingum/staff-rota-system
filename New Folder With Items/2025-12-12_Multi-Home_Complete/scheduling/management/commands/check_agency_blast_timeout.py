"""
Management command to check agency blast timeouts
Run via cron every 5 minutes to monitor pending blast batches
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

from scheduling.models_automated_workflow import AgencyBlastBatch
from scheduling.services_agency_coordination import AgencyCoordinationService


class Command(BaseCommand):
    help = 'Check for agency blast batches that have timed out'
    
    def handle(self, *args, **options):
        """
        Find all PENDING/PARTIAL blasts past deadline and escalate
        """
        
        now = timezone.now()
        
        # Find timed-out blasts
        timed_out_blasts = AgencyBlastBatch.objects.filter(
            Q(status='PENDING') | Q(status='PARTIAL'),
            response_deadline__lte=now
        )
        
        if not timed_out_blasts.exists():
            self.stdout.write(
                self.style.SUCCESS('No timed-out blasts found')
            )
            return
        
        self.stdout.write(
            f'Found {timed_out_blasts.count()} timed-out blast(s)'
        )
        
        for blast in timed_out_blasts:
            try:
                AgencyCoordinationService.check_blast_timeout(blast.id)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Processed timeout for blast {blast.id} '
                        f'(shift {blast.agency_request.shift.id})'
                    )
                )
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to process blast {blast.id}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted: {timed_out_blasts.count()} blast(s) processed'
            )
        )
