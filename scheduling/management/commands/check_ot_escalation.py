"""
Management command to check OT offer batches for escalation.
Should be run every minute via cron or Django-Q.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from scheduling.models_automated_workflow import OvertimeOfferBatch
from scheduling.services_ot_offers import OvertimeOfferService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check pending OT offer batches for escalation to agency'
    
    def handle(self, *args, **options):
        """
        Find all PENDING batches and check if they should be escalated.
        """
        pending_batches = OvertimeOfferBatch.objects.filter(status='PENDING')
        
        escalated_count = 0
        for batch in pending_batches:
            if OvertimeOfferService.check_escalation(batch.id):
                escalated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'Escalated batch {batch.id} for shift {batch.shift.id}'
                    )
                )
        
        if escalated_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Escalated {escalated_count} batches to agency'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Checked {pending_batches.count()} batches - no escalation needed'
                )
            )
