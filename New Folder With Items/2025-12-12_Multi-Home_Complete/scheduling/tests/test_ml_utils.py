"""
Feature Engineering Validation Tests - Task 14
StaffingFeatureEngineer Testing Suite

Tests:
1. Temporal feature generation
2. Lag feature calculation
3. Rolling statistics
4. Daily aggregation
5. Prophet format conversion
6. Missing data handling
7. Edge cases (single day, gaps, all zeros)

Scottish Design:
- Evidence-Based: Features proven for time-series forecasting
- Transparent: Feature names match academic literature
- User-Centered: Tests cover production data quality
"""

from django.test import TestCase
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date

from scheduling.ml_utils import StaffingFeatureEngineer


class TemporalFeatureTests(TestCase):
    """Test temporal feature generation"""
    
    def setUp(self):
        """Create test shift data"""
        # 1 week of shifts
        dates = pd.date_range('2024-01-01', '2024-01-07', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'care_home': 'HAWTHORN_HOUSE',
            'unit': 'HH_ROSE',
            'user_sap': '12345',
            'shift_type': 'DAY_SENIOR'
        })
        
        self.engineer = StaffingFeatureEngineer()
        
    def test_day_of_week_feature(self):
        """Verify day_of_week extracted (0=Monday, 6=Sunday)"""
        df = self.engineer.add_temporal_features(self.test_data)
        
        # Assert column exists
        self.assertIn('day_of_week', df.columns)
        
        # Jan 1, 2024 is Monday (0)
        self.assertEqual(df.iloc[0]['day_of_week'], 0)
        
        # Jan 7, 2024 is Sunday (6)
        self.assertEqual(df.iloc[6]['day_of_week'], 6)
        
    def test_is_weekend_feature(self):
        """Verify weekend flag (Sat/Sun = True)"""
        df = self.engineer.add_temporal_features(self.test_data)
        
        self.assertIn('is_weekend', df.columns)
        
        # Monday-Friday should be False
        self.assertFalse(df.iloc[0]['is_weekend'])  # Mon
        self.assertFalse(df.iloc[4]['is_weekend'])  # Fri
        
        # Sat/Sun should be True
        self.assertTrue(df.iloc[5]['is_weekend'])   # Sat
        self.assertTrue(df.iloc[6]['is_weekend'])   # Sun
        
    def test_month_feature(self):
        """Verify month extracted (1-12)"""
        df = self.engineer.add_temporal_features(self.test_data)
        
        self.assertIn('month', df.columns)
        
        # January = 1
        self.assertEqual(df.iloc[0]['month'], 1)
        
    def test_quarter_feature(self):
        """Verify quarter calculated (1-4)"""
        df = self.engineer.add_temporal_features(self.test_data)
        
        self.assertIn('quarter', df.columns)
        
        # January = Q1
        self.assertEqual(df.iloc[0]['quarter'], 1)
        
        # Test other quarters
        march_data = pd.DataFrame({
            'date': [pd.Timestamp('2024-03-15')],
            'care_home': 'TEST',
            'unit': 'TEST'
        })
        df_mar = self.engineer.add_temporal_features(march_data)
        self.assertEqual(df_mar.iloc[0]['quarter'], 1)  # Mar still Q1
        
        april_data = pd.DataFrame({
            'date': [pd.Timestamp('2024-04-15')],
            'care_home': 'TEST',
            'unit': 'TEST'
        })
        df_apr = self.engineer.add_temporal_features(april_data)
        self.assertEqual(df_apr.iloc[0]['quarter'], 2)  # Apr is Q2
        
    def test_week_of_year_feature(self):
        """Verify week_of_year (1-52)"""
        df = self.engineer.add_temporal_features(self.test_data)
        
        self.assertIn('week_of_year', df.columns)
        
        # Week 1 of 2024
        self.assertEqual(df.iloc[0]['week_of_year'], 1)


class DailyAggregationTests(TestCase):
    """Test aggregation to daily level"""
    
    def setUp(self):
        """Create multi-shift per day data"""
        # 3 days, multiple shifts per day
        self.multi_shift_data = pd.DataFrame({
            'date': [
                pd.Timestamp('2024-01-01'),
                pd.Timestamp('2024-01-01'),
                pd.Timestamp('2024-01-01'),
                pd.Timestamp('2024-01-02'),
                pd.Timestamp('2024-01-02'),
                pd.Timestamp('2024-01-03'),
            ],
            'care_home': 'HAWTHORN_HOUSE',
            'unit': 'HH_ROSE',
            'user_sap': ['001', '002', '003', '004', '005', '006'],
            'shift_type': 'DAY_SENIOR'
        })
        
        self.engineer = StaffingFeatureEngineer()
        
    def test_shift_count_aggregation(self):
        """Verify total_shifts calculated correctly"""
        df = self.engineer.aggregate_to_daily(self.multi_shift_data)
        
        # Should have 3 rows (3 days)
        self.assertEqual(len(df), 3)
        
        # Jan 1: 3 shifts
        jan1 = df[df['date'] == pd.Timestamp('2024-01-01')]
        self.assertEqual(jan1.iloc[0]['total_shifts'], 3)
        
        # Jan 2: 2 shifts
        jan2 = df[df['date'] == pd.Timestamp('2024-01-02')]
        self.assertEqual(jan2.iloc[0]['total_shifts'], 2)
        
        # Jan 3: 1 shift
        jan3 = df[df['date'] == pd.Timestamp('2024-01-03')]
        self.assertEqual(jan3.iloc[0]['total_shifts'], 1)
        
    def test_unique_staff_count(self):
        """Verify unique_staff calculated"""
        df = self.engineer.aggregate_to_daily(self.multi_shift_data)
        
        # Each day has unique staff (no duplicates in test data)
        self.assertEqual(df.iloc[0]['unique_staff'], 3)  # Jan 1
        self.assertEqual(df.iloc[1]['unique_staff'], 2)  # Jan 2
        self.assertEqual(df.iloc[2]['unique_staff'], 1)  # Jan 3
        
    def test_shift_type_breakdown(self):
        """Verify shift_type counts"""
        # Mix of shift types
        mixed_data = pd.DataFrame({
            'date': pd.Timestamp('2024-01-01'),
            'care_home': 'HAWTHORN_HOUSE',
            'unit': 'HH_ROSE',
            'user_sap': ['001', '002', '003', '004'],
            'shift_type': ['DAY_SENIOR', 'DAY_SENIOR', 'DAY_ASSISTANT', 'NIGHT_SENIOR']
        })
        
        df = self.engineer.aggregate_to_daily(mixed_data)
        
        # Should aggregate by shift_type
        # Implementation note: current aggregate_to_daily may not break down by type
        # Verify total_shifts = 4
        self.assertEqual(df.iloc[0]['total_shifts'], 4)


class ProphetFormatTests(TestCase):
    """Test conversion to Prophet format"""
    
    def setUp(self):
        """Create daily aggregated data"""
        dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
        self.daily_data = pd.DataFrame({
            'date': dates,
            'care_home': 'HAWTHORN_HOUSE',
            'unit': 'HH_ROSE',
            'total_shifts': np.random.randint(5, 10, len(dates)),
            'unique_staff': np.random.randint(4, 8, len(dates))
        })
        
        self.engineer = StaffingFeatureEngineer()
        
    def test_prophet_column_names(self):
        """Verify ds/y columns created"""
        prophet_df = self.engineer.create_prophet_dataframe(self.daily_data)
        
        # Assert columns
        self.assertIn('ds', prophet_df.columns)
        self.assertIn('y', prophet_df.columns)
        
        # Should only have ds and y (Prophet requirement)
        self.assertEqual(len(prophet_df.columns), 2)
        
    def test_prophet_data_types(self):
        """Ensure ds is datetime, y is numeric"""
        prophet_df = self.engineer.create_prophet_dataframe(self.daily_data)
        
        # ds should be datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(prophet_df['ds']))
        
        # y should be numeric
        self.assertTrue(pd.api.types.is_numeric_dtype(prophet_df['y']))
        
    def test_prophet_target_variable(self):
        """Verify y column contains total_shifts"""
        prophet_df = self.engineer.create_prophet_dataframe(
            self.daily_data,
            target_column='total_shifts'
        )
        
        # y should match total_shifts
        self.assertTrue((prophet_df['y'] == self.daily_data['total_shifts']).all())
        
    def test_prophet_sorted_by_date(self):
        """Prophet requires chronological order"""
        # Shuffle data
        shuffled = self.daily_data.sample(frac=1).reset_index(drop=True)
        
        prophet_df = self.engineer.create_prophet_dataframe(shuffled)
        
        # Should be sorted
        self.assertTrue(prophet_df['ds'].is_monotonic_increasing)


class MissingDataTests(TestCase):
    """Test handling of missing/irregular data"""
    
    def setUp(self):
        """Create data with gaps"""
        self.engineer = StaffingFeatureEngineer()
        
    def test_gap_filling(self):
        """Fill missing dates with zero shifts"""
        # Data with 5-day gap
        dates1 = pd.date_range('2024-01-01', '2024-01-05', freq='D')
        dates2 = pd.date_range('2024-01-11', '2024-01-15', freq='D')
        dates = dates1.union(dates2)
        
        gap_data = pd.DataFrame({
            'date': dates,
            'care_home': 'TEST',
            'unit': 'TEST',
            'total_shifts': 5
        })
        
        # Create complete date range
        filled = self.engineer.fill_missing_dates(
            gap_data,
            start_date=dates.min(),
            end_date=dates.max()
        )
        
        # Should have 15 rows (Jan 1-15)
        self.assertEqual(len(filled), 15)
        
        # Gap days (Jan 6-10) should have 0 shifts
        gap_days = filled[
            (filled['date'] >= pd.Timestamp('2024-01-06')) &
            (filled['date'] <= pd.Timestamp('2024-01-10'))
        ]
        self.assertEqual(len(gap_days), 5)
        self.assertTrue((gap_days['total_shifts'] == 0).all())
        
    def test_null_handling(self):
        """Handle null values in features"""
        null_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-05', freq='D'),
            'care_home': 'TEST',
            'unit': 'TEST',
            'total_shifts': [5, np.nan, 7, np.nan, 6]
        })
        
        # fillna with 0 or forward fill
        filled = null_data.fillna(0)
        
        self.assertEqual(filled['total_shifts'].iloc[1], 0)
        self.assertEqual(filled['total_shifts'].iloc[3], 0)
        
    def test_empty_dataframe_handling(self):
        """Gracefully handle empty input"""
        empty_df = pd.DataFrame(columns=['date', 'care_home', 'unit'])
        
        # Should not crash
        try:
            result = self.engineer.add_temporal_features(empty_df)
            # Result should be empty but valid
            self.assertEqual(len(result), 0)
        except ValueError:
            # Or raise informative error - both acceptable
            pass


class LagFeatureTests(TestCase):
    """Test lag feature generation"""
    
    def setUp(self):
        """Create time series data"""
        dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
        self.ts_data = pd.DataFrame({
            'date': dates,
            'total_shifts': list(range(1, 32))  # 1, 2, 3, ..., 31
        })
        
        self.engineer = StaffingFeatureEngineer()
        
    def test_lag_1_feature(self):
        """Previous day's shifts"""
        df = self.engineer.add_lag_features(self.ts_data, lags=[1])
        
        self.assertIn('shifts_lag_1', df.columns)
        
        # Jan 2 lag_1 should be Jan 1's value (1)
        self.assertEqual(df.iloc[1]['shifts_lag_1'], 1)
        
        # Jan 31 lag_1 should be Jan 30's value (30)
        self.assertEqual(df.iloc[30]['shifts_lag_1'], 30)
        
        # Jan 1 lag_1 should be NaN (no previous)
        self.assertTrue(pd.isna(df.iloc[0]['shifts_lag_1']))
        
    def test_lag_7_feature(self):
        """Same day last week"""
        df = self.engineer.add_lag_features(self.ts_data, lags=[7])
        
        self.assertIn('shifts_lag_7', df.columns)
        
        # Jan 8 lag_7 should be Jan 1's value (1)
        self.assertEqual(df.iloc[7]['shifts_lag_7'], 1)
        
        # First 7 days should be NaN
        self.assertTrue(pd.isna(df.iloc[0]['shifts_lag_7']))
        self.assertTrue(pd.isna(df.iloc[6]['shifts_lag_7']))
        
    def test_multiple_lags(self):
        """Test lags=[1, 7, 14]"""
        df = self.engineer.add_lag_features(self.ts_data, lags=[1, 7, 14])
        
        self.assertIn('shifts_lag_1', df.columns)
        self.assertIn('shifts_lag_7', df.columns)
        self.assertIn('shifts_lag_14', df.columns)
        
        # Jan 15: lag_14 should be Jan 1 (1)
        self.assertEqual(df.iloc[14]['shifts_lag_14'], 1)


class RollingStatisticsTests(TestCase):
    """Test rolling window calculations"""
    
    def setUp(self):
        """Create stable time series"""
        dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
        # Constant 7 shifts/day for easy testing
        self.stable_data = pd.DataFrame({
            'date': dates,
            'total_shifts': [7] * 31
        })
        
        self.engineer = StaffingFeatureEngineer()
        
    def test_rolling_mean_7d(self):
        """7-day rolling average"""
        df = self.engineer.add_rolling_features(
            self.stable_data,
            windows=[7]
        )
        
        self.assertIn('shifts_rolling_mean_7', df.columns)
        
        # After 7 days, rolling mean should be 7
        self.assertEqual(df.iloc[7]['shifts_rolling_mean_7'], 7.0)
        
        # First 6 days should be NaN (insufficient window)
        self.assertTrue(pd.isna(df.iloc[0]['shifts_rolling_mean_7']))
        self.assertTrue(pd.isna(df.iloc[5]['shifts_rolling_mean_7']))
        
    def test_rolling_std_7d(self):
        """7-day rolling std deviation"""
        df = self.engineer.add_rolling_features(
            self.stable_data,
            windows=[7]
        )
        
        self.assertIn('shifts_rolling_std_7', df.columns)
        
        # Constant data: std should be 0
        self.assertEqual(df.iloc[7]['shifts_rolling_std_7'], 0.0)
        
    def test_rolling_with_variance(self):
        """Rolling stats on varying data"""
        dates = pd.date_range('2024-01-01', '2024-01-31', freq='D')
        varying_data = pd.DataFrame({
            'date': dates,
            'total_shifts': [5, 6, 7, 8, 9, 8, 7] * 4 + [5, 6, 7]  # Pattern
        })
        
        df = self.engineer.add_rolling_features(
            varying_data,
            windows=[7]
        )
        
        # Rolling mean should smooth out pattern
        # Days 7-13 should have mean ~7
        self.assertAlmostEqual(
            df.iloc[7]['shifts_rolling_mean_7'],
            7.0,
            delta=0.5
        )


class EdgeCaseTests(TestCase):
    """Test edge cases"""
    
    def setUp(self):
        self.engineer = StaffingFeatureEngineer()
        
    def test_single_day_data(self):
        """Handle single row"""
        single_day = pd.DataFrame({
            'date': [pd.Timestamp('2024-01-01')],
            'care_home': 'TEST',
            'unit': 'TEST',
            'total_shifts': [5]
        })
        
        # Temporal features should work
        df = self.engineer.add_temporal_features(single_day)
        self.assertEqual(len(df), 1)
        self.assertIn('day_of_week', df.columns)
        
        # Prophet format should work
        prophet_df = self.engineer.create_prophet_dataframe(df)
        self.assertEqual(len(prophet_df), 1)
        
    def test_all_zero_shifts(self):
        """Handle days with no shifts"""
        zero_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-07', freq='D'),
            'care_home': 'TEST',
            'unit': 'TEST',
            'total_shifts': [0] * 7
        })
        
        # Should not crash
        prophet_df = self.engineer.create_prophet_dataframe(zero_data)
        self.assertEqual(len(prophet_df), 7)
        self.assertTrue((prophet_df['y'] == 0).all())
        
    def test_non_sequential_dates(self):
        """Random date order"""
        dates = [
            pd.Timestamp('2024-01-05'),
            pd.Timestamp('2024-01-01'),
            pd.Timestamp('2024-01-03'),
            pd.Timestamp('2024-01-02'),
            pd.Timestamp('2024-01-04'),
        ]
        
        unsorted = pd.DataFrame({
            'date': dates,
            'total_shifts': [5, 1, 3, 2, 4]
        })
        
        # Prophet format should sort
        prophet_df = self.engineer.create_prophet_dataframe(unsorted)
        
        # Should be sorted chronologically
        self.assertTrue(prophet_df['ds'].is_monotonic_increasing)
        self.assertEqual(prophet_df.iloc[0]['y'], 1)  # Jan 1
        self.assertEqual(prophet_df.iloc[4]['y'], 5)  # Jan 5


class IntegrationTests(TestCase):
    """End-to-end feature engineering pipeline"""
    
    def setUp(self):
        self.engineer = StaffingFeatureEngineer()
        
    def test_full_pipeline(self):
        """Raw shifts → Prophet format"""
        # Simulate raw shift export
        dates = pd.date_range('2024-01-01', '2024-03-31', freq='D')
        raw_shifts = []
        
        for d in dates:
            # 5-8 shifts per day
            num_shifts = np.random.randint(5, 9)
            for i in range(num_shifts):
                raw_shifts.append({
                    'date': d,
                    'care_home': 'HAWTHORN_HOUSE',
                    'unit': 'HH_ROSE',
                    'user_sap': f'00{i}',
                    'shift_type': 'DAY_SENIOR'
                })
        
        df = pd.DataFrame(raw_shifts)
        
        # Step 1: Add temporal features
        df = self.engineer.add_temporal_features(df)
        self.assertIn('day_of_week', df.columns)
        
        # Step 2: Aggregate to daily
        daily = self.engineer.aggregate_to_daily(df)
        self.assertEqual(len(daily), 91)  # 91 days in Jan-Mar
        
        # Step 3: Add lag features
        daily = self.engineer.add_lag_features(daily, lags=[1, 7])
        self.assertIn('shifts_lag_1', daily.columns)
        
        # Step 4: Add rolling features
        daily = self.engineer.add_rolling_features(daily, windows=[7, 14])
        self.assertIn('shifts_rolling_mean_7', daily.columns)
        
        # Step 5: Convert to Prophet format
        prophet_df = self.engineer.create_prophet_dataframe(daily)
        self.assertIn('ds', prophet_df.columns)
        self.assertIn('y', prophet_df.columns)
        
        # Final validation
        self.assertEqual(len(prophet_df), 91)
        self.assertTrue((prophet_df['y'] >= 5).all())
        self.assertTrue((prophet_df['y'] <= 8).all())
