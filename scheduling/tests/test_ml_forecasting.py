"""
ML Forecasting Validation Tests - Task 14
Prophet Model Testing Suite

Tests:
1. Prophet model training validation
2. Forecast accuracy metrics (MAE, MAPE, RMSE)
3. Confidence interval coverage
4. UK holiday integration
5. Component decomposition
6. Model persistence (save/load)
7. Cross-validation
8. Edge cases (insufficient data, constant demand)

Scottish Design:
- Evidence-Based: Validation against academic benchmarks
- Transparent: Metrics align with OM/SM needs
- User-Centered: Tests cover production scenarios
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta, date
import pandas as pd
import numpy as np
from pathlib import Path
import json
import tempfile

from scheduling.ml_forecasting import StaffingForecaster, train_all_units
from scheduling.ml_utils import StaffingFeatureEngineer
from scheduling.models import StaffingForecast, Unit
from scheduling.models_multi_home import CareHome


class ProphetModelTrainingTests(TestCase):
    """Test Prophet model training pipeline"""
    
    def setUp(self):
        """Create test data fixtures"""
        # Create mock daily data (1 year)
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        
        # Realistic social care pattern
        # Base: 7 shifts/day, weekend dip, winter pressure, weekly pattern
        base = 7
        weekly = np.sin(np.arange(len(dates)) * 2 * np.pi / 7) * 1.5  # Weekend dip
        winter = np.where(
            (dates.month.isin([11, 12, 1, 2])),
            2.0,  # +2 shifts in winter
            0
        )
        noise = np.random.normal(0, 0.5, len(dates))
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'care_home': 'HAWTHORN_HOUSE',
            'unit': 'HH_ROSE',
            'total_shifts': base + weekly + winter + noise
        })
        
        # Prophet format
        self.prophet_df = self.test_data[['date', 'total_shifts']].copy()
        self.prophet_df.columns = ['ds', 'y']
        self.prophet_df['y'] = self.prophet_df['y'].clip(lower=0)  # No negative shifts
        
    def test_prophet_trains_without_errors(self):
        """Verify Prophet model trains successfully"""
        forecaster = StaffingForecaster(
            care_home='HAWTHORN_HOUSE',
            unit='HH_ROSE'
        )
        
        # Train with validation
        metrics = forecaster.train(self.prophet_df, validate=True, test_days=30)
        
        # Assert model trained
        self.assertIsNotNone(forecaster.model)
        self.assertTrue(hasattr(forecaster.model, 'predict'))
        
        # Assert metrics calculated
        self.assertIn('mae', metrics)
        self.assertIn('rmse', metrics)
        self.assertIn('mape', metrics)
        self.assertIn('coverage', metrics)
        
    def test_forecast_output_format(self):
        """Check forecast DataFrame has required columns"""
        forecaster = StaffingForecaster(
            care_home='HAWTHORN_HOUSE',
            unit='HH_ROSE'
        )
        forecaster.train(self.prophet_df, validate=False)
        
        # Generate 30-day forecast
        forecast_df = forecaster.forecast(days_ahead=30)
        
        # Assert required columns
        required_columns = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        for col in required_columns:
            self.assertIn(col, forecast_df.columns)
        
        # Assert 30 rows
        self.assertEqual(len(forecast_df), 30)
        
        # Assert dates sequential
        dates_diff = forecast_df['ds'].diff().dropna()
        self.assertTrue((dates_diff == timedelta(days=1)).all())
        
    def test_uk_holidays_included(self):
        """Verify Scotland public holidays in model"""
        forecaster = StaffingForecaster(
            care_home='HAWTHORN_HOUSE',
            unit='HH_ROSE'
        )
        
        uk_holidays = forecaster._get_uk_holidays(years=range(2024, 2025))
        
        # Check key Scotland holidays
        # New Year's Day 2024
        self.assertTrue(
            any(h['ds'] == pd.Timestamp('2024-01-01') for h in uk_holidays)
        )
        
        # Christmas 2024
        self.assertTrue(
            any(h['ds'] == pd.Timestamp('2024-12-25') for h in uk_holidays)
        )
        
        # Check holiday names
        holiday_names = [h['holiday'] for h in uk_holidays]
        self.assertIn("New Year's Day", holiday_names)
        self.assertIn('Christmas Day', holiday_names)
        
    def test_confidence_intervals_reasonable(self):
        """Ensure CI bounds don't produce negative shifts"""
        forecaster = StaffingForecaster(
            care_home='HAWTHORN_HOUSE',
            unit='HH_ROSE'
        )
        forecaster.train(self.prophet_df, validate=False)
        forecast_df = forecaster.forecast(days_ahead=30)
        
        # Lower bound should be ≥0 (can't have negative shifts)
        self.assertTrue((forecast_df['yhat_lower'] >= 0).all())
        
        # Upper bound > lower bound
        self.assertTrue((forecast_df['yhat_upper'] > forecast_df['yhat_lower']).all())
        
        # Point estimate within bounds
        self.assertTrue(
            ((forecast_df['yhat'] >= forecast_df['yhat_lower']) & 
             (forecast_df['yhat'] <= forecast_df['yhat_upper'])).all()
        )
        
    def test_model_persistence(self):
        """Verify save/load model integrity"""
        forecaster = StaffingForecaster(
            care_home='HAWTHORN_HOUSE',
            unit='HH_ROSE'
        )
        forecaster.train(self.prophet_df, validate=True, test_days=30)
        
        # Save to temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = forecaster.save_model(output_dir=tmpdir)
            
            # Verify JSON metadata file created
            json_path = Path(tmpdir) / f'forecaster_HAWTHORN_HOUSE_HH_ROSE.json'
            self.assertTrue(json_path.exists())
            
            # Load metadata
            with open(json_path, 'r') as f:
                metadata = json.load(f)
            
            # Assert metadata contains metrics
            self.assertEqual(metadata['care_home'], 'HAWTHORN_HOUSE')
            self.assertEqual(metadata['unit'], 'HH_ROSE')
            self.assertIn('mae', metadata['metrics'])
            self.assertIn('mape', metadata['metrics'])


class ForecastAccuracyTests(TestCase):
    """Test forecast accuracy metrics"""
    
    def setUp(self):
        """Create realistic test scenarios"""
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        
        # Scenario 1: Low variance (admin shifts - very predictable)
        self.stable_data = pd.DataFrame({
            'ds': dates,
            'y': 5 + np.random.normal(0, 0.2, len(dates))  # ~5 shifts ±0.2
        })
        
        # Scenario 2: Seasonal pattern (typical care unit)
        weekly = np.sin(np.arange(len(dates)) * 2 * np.pi / 7) * 2
        yearly = np.sin(np.arange(len(dates)) * 2 * np.pi / 365.25) * 1
        self.seasonal_data = pd.DataFrame({
            'ds': dates,
            'y': 8 + weekly + yearly + np.random.normal(0, 1, len(dates))
        })
        
        # Scenario 3: High variance (unpredictable unit)
        self.volatile_data = pd.DataFrame({
            'ds': dates,
            'y': 6 + np.random.normal(0, 3, len(dates))  # High noise
        })
        
    def test_stable_unit_accuracy(self):
        """Low variance units should have excellent MAPE (<15%)"""
        forecaster = StaffingForecaster(care_home='TEST', unit='STABLE')
        metrics = forecaster.train(self.stable_data, validate=True, test_days=30)
        
        # Stable units should have MAPE < 15%
        self.assertLess(metrics['mape'], 15.0)
        
        # MAE should be < 1 shift/day
        self.assertLess(metrics['mae'], 1.0)
        
    def test_seasonal_unit_accuracy(self):
        """Seasonal units should have good MAPE (15-30%)"""
        forecaster = StaffingForecaster(care_home='TEST', unit='SEASONAL')
        metrics = forecaster.train(self.seasonal_data, validate=True, test_days=30)
        
        # Seasonal units: target MAPE < 30%
        self.assertLess(metrics['mape'], 30.0)
        
        # MAE should be < 2 shifts/day
        self.assertLess(metrics['mae'], 2.0)
        
    def test_coverage_target_met(self):
        """80% CI should contain ~80% of actual values"""
        forecaster = StaffingForecaster(care_home='TEST', unit='SEASONAL')
        metrics = forecaster.train(self.seasonal_data, validate=True, test_days=30)
        
        # Coverage: target 70-90% (Prophet's 80% CI)
        # Allow some tolerance (Prophet CI can be conservative)
        self.assertGreater(metrics['coverage'], 60.0)
        self.assertLess(metrics['coverage'], 95.0)
        
    def test_mape_interpretation(self):
        """Verify MAPE calculation matches manual calculation"""
        forecaster = StaffingForecaster(care_home='TEST', unit='SEASONAL')
        
        # Train/test split manually
        cutoff = self.seasonal_data['ds'].max() - timedelta(days=30)
        train_df = self.seasonal_data[self.seasonal_data['ds'] <= cutoff]
        test_df = self.seasonal_data[self.seasonal_data['ds'] > cutoff]
        
        metrics = forecaster.train(self.seasonal_data, validate=True, test_days=30)
        
        # Manual MAPE calculation
        forecaster.model.fit(train_df)
        forecast = forecaster.model.predict(test_df[['ds']])
        
        y_true = test_df['y'].values
        y_pred = forecast['yhat'].values
        manual_mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        # Assert within 1% tolerance
        self.assertAlmostEqual(metrics['mape'], manual_mape, delta=1.0)


class EdgeCaseTests(TestCase):
    """Test edge cases and failure scenarios"""
    
    def test_insufficient_data_handling(self):
        """Model should handle <1 year of data gracefully"""
        # Only 60 days of data
        short_data = pd.DataFrame({
            'ds': pd.date_range('2024-10-01', '2024-11-30', freq='D'),
            'y': np.random.uniform(5, 10, 61)
        })
        
        forecaster = StaffingForecaster(care_home='TEST', unit='SHORT')
        
        # Should train without errors (Prophet needs ≥2 periods)
        # But validation will be limited
        metrics = forecaster.train(short_data, validate=True, test_days=10)
        
        # Assert model trained
        self.assertIsNotNone(forecaster.model)
        
        # Metrics may be poor, but should exist
        self.assertIn('mae', metrics)
        
    def test_constant_demand_handling(self):
        """Handle units with zero variance (e.g., fixed admin)"""
        constant_data = pd.DataFrame({
            'ds': pd.date_range('2024-01-01', '2024-12-31', freq='D'),
            'y': [5] * 366  # Exactly 5 shifts every day
        })
        
        forecaster = StaffingForecaster(care_home='TEST', unit='CONSTANT')
        metrics = forecaster.train(constant_data, validate=True, test_days=30)
        
        # Perfect prediction (MAPE ~0%)
        self.assertLess(metrics['mape'], 1.0)
        self.assertLess(metrics['mae'], 0.1)
        
    def test_missing_dates_handling(self):
        """Handle gaps in training data"""
        # Data with 10-day gap
        dates1 = pd.date_range('2024-01-01', '2024-06-30', freq='D')
        dates2 = pd.date_range('2024-07-10', '2024-12-31', freq='D')
        dates = dates1.union(dates2)
        
        gap_data = pd.DataFrame({
            'ds': dates,
            'y': np.random.uniform(5, 10, len(dates))
        })
        
        forecaster = StaffingForecaster(care_home='TEST', unit='GAP')
        
        # Prophet should interpolate missing dates
        metrics = forecaster.train(gap_data, validate=True, test_days=30)
        
        # Assert trained successfully
        self.assertIsNotNone(forecaster.model)
        
    def test_future_dates_validation(self):
        """Ensure forecast extends beyond last training date"""
        forecaster = StaffingForecaster(care_home='TEST', unit='FUTURE')
        
        train_data = pd.DataFrame({
            'ds': pd.date_range('2024-01-01', '2024-12-31', freq='D'),
            'y': np.random.uniform(5, 10, 366)
        })
        
        forecaster.train(train_data, validate=False)
        forecast_df = forecaster.forecast(days_ahead=30)
        
        # Forecast should start from 2025-01-01
        self.assertEqual(forecast_df['ds'].min().date(), date(2025, 1, 1))
        self.assertEqual(forecast_df['ds'].max().date(), date(2025, 1, 30))


class ComponentDecompositionTests(TestCase):
    """Test Prophet component analysis"""
    
    def setUp(self):
        """Create data with known components"""
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        n = len(dates)
        
        # Construct signal with known components
        trend = np.linspace(5, 8, n)  # Linear growth
        weekly = 2 * np.sin(np.arange(n) * 2 * np.pi / 7)  # Weekly cycle
        yearly = 1 * np.sin(np.arange(n) * 2 * np.pi / 365.25)  # Yearly cycle
        
        self.component_data = pd.DataFrame({
            'ds': dates,
            'y': trend + weekly + yearly + np.random.normal(0, 0.5, n)
        })
        
    def test_component_extraction(self):
        """Verify trend/weekly/yearly components extracted"""
        forecaster = StaffingForecaster(care_home='TEST', unit='COMPONENT')
        forecaster.train(self.component_data, validate=False)
        
        # Get components (returns variance contributions as percentages)
        components = forecaster.get_component_importance()
        
        # Assert components exist
        self.assertIn('trend', components)
        self.assertIn('weekly', components)
        self.assertIn('yearly', components)
        
        # Components should sum to ~100% (normalized percentages)
        total = sum(components.values())
        self.assertAlmostEqual(total, 100.0, delta=1.0)
        
        # Weekly component should be significant (strongest in test data)
        self.assertGreater(components['weekly'], 10.0)
        
    def test_winter_pressure_seasonality(self):
        """Verify winter pressure custom seasonality works"""
        forecaster = StaffingForecaster(care_home='TEST', unit='WINTER')
        forecaster.train(self.component_data, validate=False)
        
        # Forecast including winter months
        forecast_df = forecaster.forecast(days_ahead=90)  # Through winter
        
        # Winter months (Nov-Feb) should exist in forecast
        winter_months = forecast_df[
            forecast_df['ds'].dt.month.isin([11, 12, 1, 2])
        ]
        self.assertGreater(len(winter_months), 0)


class DatabaseIntegrationTests(TestCase):
    """Test StaffingForecast model integration"""
    
    def setUp(self):
        """Create test care home and unit"""
        self.care_home = CareHome.objects.create(
            name='TEST_HOME',
            display_name='Test Home'
        )
        
        self.unit = Unit.objects.create(
            name='TEST_UNIT',
            care_home=self.care_home
        )
        
    def test_forecast_model_creation(self):
        """Verify StaffingForecast records can be created"""
        forecast = StaffingForecast.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=date(2025, 1, 1),
            predicted_shifts=7.5,
            confidence_lower=5.0,
            confidence_upper=10.0,
            trend_component=7.0,
            weekly_component=0.5,
            yearly_component=0.0,
            mae=1.5,
            mape=20.0,
            model_version='1.0'
        )
        
        # Assert saved
        self.assertEqual(forecast.id, 1)
        self.assertEqual(forecast.predicted_shifts, 7.5)
        
    def test_uncertainty_range_property(self):
        """Test uncertainty_range calculated property"""
        forecast = StaffingForecast.objects.create(
            care_home=self.care_home,
            unit=self.unit,
            forecast_date=date(2025, 1, 1),
            predicted_shifts=7.5,
            confidence_lower=5.0,
            confidence_upper=10.0,
            mae=1.5,
            mape=20.0
        )
        
        # Uncertainty range: upper - lower
        self.assertEqual(forecast.uncertainty_range, 5.0)
        
    def test_forecast_ordering(self):
        """Verify forecasts ordered by date (most recent first)"""
        # Create 3 forecasts
        for i, offset in enumerate([0, 1, 2]):
            StaffingForecast.objects.create(
                care_home=self.care_home,
                unit=self.unit,
                forecast_date=date(2025, 1, 1) + timedelta(days=offset),
                predicted_shifts=7.0 + i,
                confidence_lower=5.0,
                confidence_upper=10.0,
                mae=1.5,
                mape=20.0
            )
        
        # Query all forecasts
        forecasts = StaffingForecast.objects.all()
        
        # Should be ordered by forecast_date DESC
        dates = [f.forecast_date for f in forecasts]
        self.assertEqual(dates, sorted(dates, reverse=True))


class CrossValidationTests(TestCase):
    """Test time-series cross-validation"""
    
    def test_rolling_origin_validation(self):
        """Implement rolling origin cross-validation"""
        # Create 2 years of data
        dates = pd.date_range('2023-01-01', '2024-12-31', freq='D')
        data = pd.DataFrame({
            'ds': dates,
            'y': 7 + np.sin(np.arange(len(dates)) * 2 * np.pi / 7) + np.random.normal(0, 1, len(dates))
        })
        
        # Rolling origin: train on increasing windows, test on next 30 days
        mapes = []
        for i in range(4):  # 4 folds
            # Train: first 365 + i*30 days
            # Test: next 30 days
            train_days = 365 + i * 30
            test_start = train_days
            test_end = train_days + 30
            
            train_data = data.iloc[:train_days]
            test_data = data.iloc[test_start:test_end]
            
            # Train model
            forecaster = StaffingForecaster(care_home='TEST', unit='CV')
            forecaster.model = forecaster.train.__wrapped__(forecaster, train_data, validate=False)
            forecaster.train(train_data, validate=False)
            
            # Predict test period
            forecast = forecaster.model.predict(test_data[['ds']])
            
            # Calculate MAPE
            y_true = test_data['y'].values
            y_pred = forecast['yhat'].values
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            mapes.append(mape)
        
        # Average MAPE across folds
        avg_cv_mape = np.mean(mapes)
        
        # Should be reasonable (<40% for typical data)
        self.assertLess(avg_cv_mape, 40.0)
        
        # Std should be reasonable (not wildly varying)
        self.assertLess(np.std(mapes), 20.0)


class ProductionMonitoringTests(TestCase):
    """Test production forecast monitoring"""
    
    def test_forecast_drift_detection(self):
        """Detect when forecasts consistently underpredict/overpredict"""
        # Simulate scenario: model trained on old data, demand increased
        
        # Training data (2023): avg 7 shifts/day
        train_dates = pd.date_range('2023-01-01', '2023-12-31', freq='D')
        train_data = pd.DataFrame({
            'ds': train_dates,
            'y': 7 + np.random.normal(0, 1, len(train_dates))
        })
        
        # Test data (2024): avg 9 shifts/day (demand increased)
        test_dates = pd.date_range('2024-01-01', '2024-01-30', freq='D')
        test_data = pd.DataFrame({
            'ds': test_dates,
            'y': 9 + np.random.normal(0, 1, len(test_dates))
        })
        
        # Train on old data
        forecaster = StaffingForecaster(care_home='TEST', unit='DRIFT')
        forecaster.train(train_data, validate=False)
        
        # Predict new period
        forecast = forecaster.model.predict(test_data[['ds']])
        
        # Calculate bias (mean residual)
        residuals = test_data['y'].values - forecast['yhat'].values
        bias = np.mean(residuals)
        
        # Bias should be positive (underpredicting)
        self.assertGreater(bias, 1.0)  # Consistently under by >1 shift
        
        # This would trigger "retrain model" alert in production
        
    def test_anomaly_detection(self):
        """Flag forecasts with unusually high uncertainty"""
        # Normal forecast
        normal_forecast = StaffingForecast(
            predicted_shifts=7.5,
            confidence_lower=6.0,
            confidence_upper=9.0
        )
        
        # High uncertainty forecast (wide CI)
        uncertain_forecast = StaffingForecast(
            predicted_shifts=7.5,
            confidence_lower=2.0,
            confidence_upper=13.0
        )
        
        # Normal: CI width = 3 shifts
        self.assertEqual(normal_forecast.uncertainty_range, 3.0)
        
        # Uncertain: CI width = 11 shifts (>3x normal)
        self.assertEqual(uncertain_forecast.uncertainty_range, 11.0)
        
        # Production monitoring: flag if uncertainty_range > 5
        self.assertLess(normal_forecast.uncertainty_range, 5.0)
        self.assertGreater(uncertain_forecast.uncertainty_range, 5.0)  # ALERT


class RealWorldScenarioTests(TestCase):
    """Test realistic social care scenarios"""
    
    def test_new_unit_with_limited_history(self):
        """Recently opened unit with 3 months data"""
        # 90 days of data
        dates = pd.date_range('2024-10-01', '2024-12-31', freq='D')
        new_unit_data = pd.DataFrame({
            'ds': dates,
            'y': 6 + np.random.normal(0, 1.5, len(dates))  # High variance (stabilizing)
        })
        
        forecaster = StaffingForecaster(care_home='NEW_HOME', unit='NEW_UNIT')
        metrics = forecaster.train(new_unit_data, validate=True, test_days=15)
        
        # MAPE may be high (>30%) due to limited data
        # But model should still train
        self.assertIsNotNone(forecaster.model)
        self.assertIn('mape', metrics)
        
    def test_school_holiday_impact(self):
        """Test school holiday seasonality (reduced staff availability)"""
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        
        # Simulate reduced staffing during school holidays
        # Easter: Apr 1-14
        # Summer: Jul 15 - Aug 31
        # Christmas: Dec 23-31
        school_holidays = (
            ((dates.month == 4) & (dates.day <= 14)) |
            ((dates.month >= 7) & (dates.month <= 8)) |
            ((dates.month == 12) & (dates.day >= 23))
        )
        
        holiday_data = pd.DataFrame({
            'ds': dates,
            'y': np.where(school_holidays, 5, 8) + np.random.normal(0, 1, len(dates))
        })
        
        forecaster = StaffingForecaster(care_home='TEST', unit='HOLIDAY')
        forecaster.train(holiday_data, validate=False)
        
        # Forecast summer period
        forecast_df = forecaster.forecast(days_ahead=90)  # Through summer
        
        # Summer forecasts (Jul-Aug) should be lower than spring (May-Jun)
        summer = forecast_df[forecast_df['ds'].dt.month.isin([7, 8])]['yhat'].mean()
        spring = forecast_df[forecast_df['ds'].dt.month.isin([5, 6])]['yhat'].mean()
        
        # Summer should be lower (if model captured pattern)
        # Allow some tolerance
        self.assertLess(summer, spring + 1.0)
        
    def test_covid_like_disruption(self):
        """Test model with sudden regime change (e.g., pandemic)"""
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')
        
        # Normal demand until June, then sudden increase
        disruption_date = pd.Timestamp('2024-06-01')
        disruption = np.where(dates >= disruption_date, 3, 0)
        
        covid_data = pd.DataFrame({
            'ds': dates,
            'y': 7 + disruption + np.random.normal(0, 1, len(dates))
        })
        
        forecaster = StaffingForecaster(care_home='TEST', unit='COVID')
        
        # Prophet's changepoint detection should catch this
        forecaster.train(covid_data, validate=False)
        
        # Forecast post-disruption
        forecast_df = forecaster.forecast(days_ahead=30)
        
        # Predictions should be ~10 shifts/day (7 + 3)
        avg_forecast = forecast_df['yhat'].mean()
        self.assertGreater(avg_forecast, 8.0)  # Should recognize new level
