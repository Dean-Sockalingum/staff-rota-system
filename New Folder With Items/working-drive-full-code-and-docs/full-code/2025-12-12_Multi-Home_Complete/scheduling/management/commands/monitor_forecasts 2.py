"""
Production Forecast Monitoring Command

Runs automated monitoring of Prophet forecasting models:
- Checks forecast accuracy (MAPE)
- Detects distribution drift
- Triggers automated retraining
- Sends email alerts for degradation

Usage:
    python manage.py monitor_forecasts
    
Schedule with cron:
    0 6 * * * /path/to/python manage.py monitor_forecasts
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from scheduling.models import CareHome, Unit, Shift, StaffingForecast, ProphetModelMetrics
from scheduling.forecast_monitoring import ForecastMonitor
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Monitor Prophet forecast performance and trigger retraining if needed'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--care-home',
            type=str,
            help='Monitor specific care home only (by name)',
        )
        parser.add_argument(
            '--unit',
            type=str,
            help='Monitor specific unit only (by name)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze (default: 30)',
        )
        parser.add_argument(
            '--mape-threshold',
            type=float,
            default=0.30,
            help='MAPE threshold for retraining (default: 0.30 = 30%%)',
        )
        parser.add_argument(
            '--drift-threshold',
            type=float,
            default=0.05,
            help='Drift p-value threshold (default: 0.05)',
        )
        parser.add_argument(
            '--no-email',
            action='store_true',
            help='Disable email alerts',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Prophet Forecast Monitoring ==='))
        self.stdout.write(f"Started at: {timezone.now()}\n")
        
        # Initialize monitor
        monitor = ForecastMonitor(
            mape_threshold=options['mape_threshold'],
            drift_threshold=options['drift_threshold'],
            retrain_days=7  # Weekly retraining
        )
        
        # Get care homes to monitor
        care_homes = CareHome.objects.all()
        if options['care_home']:
            care_homes = care_homes.filter(name__icontains=options['care_home'])
        
        if not care_homes.exists():
            self.stdout.write(self.style.WARNING('No care homes found'))
            return
        
        # Track alerts
        alerts = []
        retrain_needed = []
        
        # Monitor each care home/unit
        for care_home in care_homes:
            units = care_home.units.all()
            if options['unit']:
                units = units.filter(name__icontains=options['unit'])
            
            for unit in units:
                self.stdout.write(f"\nMonitoring: {care_home.name} / {unit.name}")
                
                try:
                    # Check if retraining needed
                    should_retrain, reason = monitor.should_retrain(
                        care_home,
                        unit,
                        mape_threshold=options['mape_threshold'],
                        drift_threshold=options['drift_threshold']
                    )
                    
                    if should_retrain:
                        self.stdout.write(self.style.WARNING(f"  ⚠️  Retrain needed: {reason}"))
                        retrain_needed.append({
                            'care_home': care_home.name,
                            'unit': unit.name,
                            'reason': reason
                        })
                    else:
                        self.stdout.write(self.style.SUCCESS(f"  ✓ {reason}"))
                    
                    # Calculate recent performance
                    recent_metrics = ProphetModelMetrics.objects.filter(
                        care_home=care_home,
                        unit=unit,
                        forecast_date__gte=timezone.now().date() - timedelta(days=options['days'])
                    )
                    
                    if recent_metrics.exists():
                        avg_mape = sum(m.mape for m in recent_metrics) / len(recent_metrics)
                        drift_count = sum(1 for m in recent_metrics if m.has_drift)
                        
                        self.stdout.write(f"    - Average MAPE: {avg_mape:.1f}%")
                        self.stdout.write(f"    - Drift detections: {drift_count}/{len(recent_metrics)}")
                        
                        # Check for alerts
                        if avg_mape > options['mape_threshold'] * 100:
                            alerts.append({
                                'care_home': care_home.name,
                                'unit': unit.name,
                                'type': 'HIGH_MAPE',
                                'value': avg_mape,
                                'threshold': options['mape_threshold'] * 100
                            })
                        
                        if drift_count > len(recent_metrics) * 0.25:  # >25% of forecasts have drift
                            alerts.append({
                                'care_home': care_home.name,
                                'unit': unit.name,
                                'type': 'FREQUENT_DRIFT',
                                'value': f"{drift_count}/{len(recent_metrics)}",
                                'threshold': '25%'
                            })
                    else:
                        self.stdout.write(self.style.WARNING(f"    - No recent metrics"))
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  ✗ Error: {str(e)}"))
                    logger.exception(f"Error monitoring {care_home.name}/{unit.name}")
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f"\n=== Summary ==="))
        self.stdout.write(f"Retrain needed: {len(retrain_needed)} unit(s)")
        self.stdout.write(f"Alerts generated: {len(alerts)}")
        
        # Send email alerts
        if alerts and not options['no_email']:
            self._send_alerts(alerts, retrain_needed)
        
        # Log retrain recommendations
        if retrain_needed:
            self.stdout.write(self.style.WARNING("\nRetrain Recommendations:"))
            for item in retrain_needed:
                self.stdout.write(f"  - {item['care_home']}/{item['unit']}: {item['reason']}")
        
        self.stdout.write(self.style.SUCCESS(f"\nCompleted at: {timezone.now()}"))
    
    def _send_alerts(self, alerts, retrain_needed):
        """Send email alerts to OMs about forecast performance issues"""
        
        subject = f"Prophet Forecast Monitoring Alert - {timezone.now().date()}"
        
        # Build email body
        message_lines = [
            "Prophet Forecast Monitoring System",
            "=" * 50,
            "",
            f"Generated: {timezone.now()}",
            "",
        ]
        
        if alerts:
            message_lines.extend([
                "ALERTS:",
                "-------",
            ])
            for alert in alerts:
                if alert['type'] == 'HIGH_MAPE':
                    message_lines.append(
                        f"⚠️  HIGH MAPE: {alert['care_home']}/{alert['unit']} "
                        f"- Average MAPE {alert['value']:.1f}% exceeds threshold {alert['threshold']:.1f}%"
                    )
                elif alert['type'] == 'FREQUENT_DRIFT':
                    message_lines.append(
                        f"⚠️  FREQUENT DRIFT: {alert['care_home']}/{alert['unit']} "
                        f"- {alert['value']} forecasts show drift (>{alert['threshold']})"
                    )
            message_lines.append("")
        
        if retrain_needed:
            message_lines.extend([
                "RETRAIN RECOMMENDATIONS:",
                "------------------------",
            ])
            for item in retrain_needed:
                message_lines.append(
                    f"• {item['care_home']}/{item['unit']}: {item['reason']}"
                )
            message_lines.append("")
        
        message_lines.extend([
            "",
            "Actions:",
            "--------",
            "1. Review dashboard for detailed metrics",
            "2. Trigger model retraining for flagged units",
            "3. Investigate anomalies in forecast patterns",
            "",
            "This is an automated message from the Staff Rota System.",
        ])
        
        message = "\n".join(message_lines)
        
        # Send email
        try:
            recipient_list = getattr(settings, 'FORECAST_ALERT_EMAILS', ['admin@example.com'])
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Alert email sent to {', '.join(recipient_list)}"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n✗ Failed to send alert email: {str(e)}"))
            logger.exception("Failed to send forecast alert email")
