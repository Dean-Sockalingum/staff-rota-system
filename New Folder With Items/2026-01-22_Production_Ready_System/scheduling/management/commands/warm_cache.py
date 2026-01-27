"""
Management command to warm up application caches
Task 44: Performance Optimization
"""

from django.core.management.base import BaseCommand
from scheduling.cache_service import CacheService
from scheduling.models import CareHome
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Warm up application caches for improved performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--home',
            type=int,
            help='Specific home ID to warm cache for'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all caches before warming'
        )

    def handle(self, *args, **options):
        home_id = options.get('home')
        should_clear = options.get('clear', False)

        if should_clear:
            self.stdout.write(self.style.WARNING('Clearing all caches...'))
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✓ Caches cleared'))

        self.stdout.write(self.style.WARNING('Warming up caches...'))

        # Warm dashboard caches
        CacheService.warm_dashboard_cache(home_id=home_id)

        # Get stats
        stats = CacheService.get_cache_stats()

        self.stdout.write(self.style.SUCCESS('\n✓ Cache warming complete!\n'))
        self.stdout.write(self.style.SUCCESS(f'Total cached keys: {stats["total_keys"]}'))
        self.stdout.write(self.style.SUCCESS(f'Memory used: {stats["used_memory"]}'))
        self.stdout.write(self.style.SUCCESS(f'Hit rate: {stats["hit_rate"]:.2%}'))
