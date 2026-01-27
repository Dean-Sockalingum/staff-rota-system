"""
Import Prophet forecasts into database

Usage:
    python manage.py import_forecasts ml_data/forecasts/all_units_30day_forecast.csv
    
Features:
- Bulk insert for performance (1000 records at a time)
- Validation of care_home/unit existence
- Duplicate detection (unique_together constraint)
- Progress reporting

Scottish Design:
- Transparent: Clear progress reporting
- User-Centered: Simple command-line interface
- Evidence-Based: Validates against existing CareHome/Unit records
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from scheduling.models import StaffingForecast, CareHome, Unit
import pandas as pd
from datetime import datetime
import json
import os


class Command(BaseCommand):
    help = 'Import Prophet forecasts from CSV into StaffingForecast model'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to forecast CSV file (from train_all_units output)'
        )
        parser.add_argument(
            '--model-version',
            type=str,
            default='1.0',
            help='Model version identifier (default: 1.0)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Delete existing forecasts before importing'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk insert (default: 1000)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        model_version = options['model_version']
        clear_existing = options['clear_existing']
        batch_size = options['batch_size']
        
        self.stdout.write("=== Importing Prophet Forecasts ===\n")
        
        # Validate file exists
        if not os.path.exists(csv_file):
            raise CommandError(f"File not found: {csv_file}")
        
        # Load CSV
        self.stdout.write(f"Loading forecasts from {csv_file}...")
        df = pd.read_csv(csv_file)
        self.stdout.write(f"✓ Loaded {len(df):,} predictions\n")
        
        # Validate required columns
        required_cols = ['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'care_home', 'unit']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise CommandError(f"Missing required columns: {missing_cols}")
        
        # Optional component columns
        has_components = all(col in df.columns for col in ['trend', 'weekly', 'yearly'])
        
        # Parse dates
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Load model metadata (MAE, MAPE) if available
        metadata_by_unit = self._load_model_metadata()
        
        # Clear existing if requested
        if clear_existing:
            count = StaffingForecast.objects.filter(model_version=model_version).count()
            if count > 0:
                self.stdout.write(f"Deleting {count:,} existing forecasts (version={model_version})...")
                StaffingForecast.objects.filter(model_version=model_version).delete()
                self.stdout.write(self.style.SUCCESS("✓ Deleted\n"))
        
        # Cache CareHome and Unit lookups
        self.stdout.write("Caching CareHome and Unit lookups...")
        care_homes = {ch.name: ch for ch in CareHome.objects.all()}
        units = {u.name: u for u in Unit.objects.all()}
        self.stdout.write(f"✓ {len(care_homes)} care homes, {len(units)} units\n")
        
        # Prepare forecast objects
        self.stdout.write("Preparing forecast records...")
        forecasts = []
        skipped = 0
        
        for idx, row in df.iterrows():
            care_home_name = row['care_home']
            unit_name = row['unit']
            
            # Validate CareHome exists
            if care_home_name not in care_homes:
                self.stdout.write(self.style.WARNING(f"⚠ Skipping: CareHome '{care_home_name}' not found"))
                skipped += 1
                continue
            
            # Validate Unit exists
            if unit_name not in units:
                self.stdout.write(self.style.WARNING(f"⚠ Skipping: Unit '{unit_name}' not found"))
                skipped += 1
                continue
            
            # Get metadata for this unit
            metadata_key = (care_home_name, unit_name)
            metadata = metadata_by_unit.get(metadata_key, {})
            
            # Create forecast object
            forecast = StaffingForecast(
                care_home=care_homes[care_home_name],
                unit=units[unit_name],
                forecast_date=row['ds'].date(),
                predicted_shifts=round(row['yhat'], 2),
                confidence_lower=round(row['yhat_lower'], 2),
                confidence_upper=round(row['yhat_upper'], 2),
                model_version=model_version,
                mae=metadata.get('mae'),
                mape=metadata.get('mape'),
            )
            
            # Add components if available
            if has_components:
                forecast.trend_component = round(row['trend'], 2) if pd.notna(row['trend']) else None
                forecast.weekly_component = round(row['weekly'], 2) if pd.notna(row['weekly']) else None
                forecast.yearly_component = round(row['yearly'], 2) if pd.notna(row['yearly']) else None
            
            forecasts.append(forecast)
        
        total_records = len(forecasts)
        self.stdout.write(f"✓ Prepared {total_records:,} records")
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f"  (Skipped {skipped} due to missing CareHome/Unit)"))
        self.stdout.write("")
        
        # Bulk insert with batching
        self.stdout.write(f"Inserting forecasts (batch size: {batch_size})...")
        inserted = 0
        
        with transaction.atomic():
            for i in range(0, total_records, batch_size):
                batch = forecasts[i:i+batch_size]
                
                try:
                    StaffingForecast.objects.bulk_create(
                        batch,
                        ignore_conflicts=True  # Skip duplicates (unique_together)
                    )
                    inserted += len(batch)
                    
                    # Progress reporting
                    progress = (i + len(batch)) / total_records * 100
                    self.stdout.write(f"  Progress: {progress:.1f}% ({inserted:,}/{total_records:,})", ending='\r')
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"\n✗ Error in batch {i//batch_size + 1}: {e}"))
                    raise
        
        self.stdout.write("")  # New line after progress
        self.stdout.write(self.style.SUCCESS(f"✓ Inserted {inserted:,} forecasts"))
        
        # Summary statistics
        self._print_summary(model_version)
        
        self.stdout.write(self.style.SUCCESS("\n✅ Import complete!"))
    
    def _load_model_metadata(self):
        """
        Load model metadata (MAE, MAPE) from JSON files
        
        Returns:
            dict: {(care_home, unit): {'mae': X, 'mape': Y}}
        """
        metadata = {}
        metadata_dir = 'ml_data/models'
        
        if not os.path.exists(metadata_dir):
            return metadata
        
        for filename in os.listdir(metadata_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(metadata_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    
                    if 'care_home' in data and 'unit' in data and 'metrics' in data:
                        key = (data['care_home'], data['unit'])
                        metadata[key] = data['metrics']
            except Exception:
                continue  # Skip malformed files
        
        return metadata
    
    def _print_summary(self, model_version):
        """Print summary statistics of imported forecasts"""
        forecasts = StaffingForecast.objects.filter(model_version=model_version)
        
        if forecasts.count() == 0:
            return
        
        self.stdout.write("\n=== Import Summary ===")
        self.stdout.write(f"Model version: {model_version}")
        self.stdout.write(f"Total forecasts: {forecasts.count():,}")
        
        # Date range
        date_range = forecasts.aggregate(
            min_date=models.Min('forecast_date'),
            max_date=models.Max('forecast_date')
        )
        self.stdout.write(f"Date range: {date_range['min_date']} to {date_range['max_date']}")
        
        # Care homes and units
        care_homes = forecasts.values('care_home').distinct().count()
        units = forecasts.values('unit').distinct().count()
        self.stdout.write(f"Care homes: {care_homes}")
        self.stdout.write(f"Units: {units}")
        
        # Prediction statistics
        stats = forecasts.aggregate(
            avg_predicted=models.Avg('predicted_shifts'),
            min_predicted=models.Min('predicted_shifts'),
            max_predicted=models.Max('predicted_shifts'),
            avg_uncertainty=models.Avg(
                models.F('confidence_upper') - models.F('confidence_lower')
            )
        )
        
        self.stdout.write(f"\nPrediction Statistics:")
        self.stdout.write(f"  Average: {stats['avg_predicted']:.1f} shifts/day")
        self.stdout.write(f"  Range: {stats['min_predicted']:.1f} - {stats['max_predicted']:.1f}")
        self.stdout.write(f"  Avg uncertainty: ±{stats['avg_uncertainty']/2:.1f} shifts")
        
        # Model accuracy (if metadata available)
        with_metrics = forecasts.exclude(mae__isnull=True)
        if with_metrics.exists():
            accuracy = with_metrics.aggregate(
                avg_mae=models.Avg('mae'),
                avg_mape=models.Avg('mape')
            )
            self.stdout.write(f"\nModel Accuracy ({with_metrics.count()} units):")
            self.stdout.write(f"  Avg MAE: {accuracy['avg_mae']:.2f} shifts/day")
            self.stdout.write(f"  Avg MAPE: {accuracy['avg_mape']:.1f}%")


from django.db import models  # For aggregations in _print_summary
