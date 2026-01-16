"""
ML Feature Engineering Pipeline for Staffing Demand Forecasting

Scottish Design Principles:
- Evidence-Based: Features derived from care sector staffing research
- Transparency: Clear documentation of each feature's purpose
- Data Minimization: Only create features needed for forecasting
- User-Centered: Features align with OM/SM planning needs

This module transforms raw shift data into ML-ready features for:
1. Prophet demand forecasting (Task 9)
2. Shift optimization (Task 12)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import holidays


class StaffingFeatureEngineer:
    """
    Transform shift data into ML features for demand forecasting
    
    Features Created:
    - Temporal: day_of_week, month, week_of_year, is_weekend, is_holiday
    - Lag variables: shifts_previous_day, shifts_previous_week
    - Rolling averages: shifts_7day_avg, shifts_14day_avg, shifts_28day_avg
    - Occupancy indicators: resident_count, dependency_ratio
    - Seasonal: school_holidays, winter_pressure (Nov-Feb)
    """
    
    def __init__(self, country='UK', region='Scotland'):
        """
        Initialize feature engineer
        
        Args:
            country: Country for holiday calendar (default: UK)
            region: Region for local holidays (default: Scotland)
        """
        self.country = country
        self.region = region
        # UK holidays including Scotland-specific
        self.uk_holidays = holidays.country_holidays('GB', subdiv='SCT')
    
    def load_shift_data(self, csv_path):
        """
        Load exported shift data and prepare for feature engineering
        
        Args:
            csv_path: Path to CSV exported by export_shift_data command
            
        Returns:
            pd.DataFrame: Loaded and parsed shift data
        """
        df = pd.read_csv(csv_path)
        
        # Parse dates
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure numeric types
        df['shift_hours'] = pd.to_numeric(df['shift_hours'], errors='coerce')
        df['agency_rate'] = pd.to_numeric(df['agency_rate'], errors='coerce')
        
        print(f"Loaded {len(df):,} shifts from {df['date'].min()} to {df['date'].max()}")
        print(f"Care homes: {df['care_home'].nunique()}")
        print(f"Units: {df['unit'].nunique()}")
        
        return df
    
    def add_temporal_features(self, df):
        """
        Add time-based features for seasonality and trends
        
        Features:
        - day_of_week (0=Monday, 6=Sunday)
        - month (1-12)
        - week_of_year (1-53)
        - is_weekend (Saturday/Sunday)
        - is_holiday (UK public holidays)
        - quarter (Q1-Q4)
        """
        df = df.copy()
        
        # Handle empty dataframes
        if len(df) == 0:
            return df
        
        # Day of week (Prophet uses this automatically)
        df['dow'] = df['date'].dt.dayofweek
        df['day_of_week'] = df['dow']  # Alias for tests
        df['dow_name'] = df['date'].dt.day_name()
        
        # Month and seasonal indicators
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Weekend indicator (high dependency staffing)
        df['is_weekend'] = df['dow'].isin([5, 6]).astype(int)
        
        # UK holidays (potential understaffing risk)
        df['is_holiday'] = df['date'].apply(lambda x: x in self.uk_holidays).astype(int)
        
        # Winter pressure period (Nov-Feb: flu season, increased dependency)
        df['is_winter_pressure'] = df['month'].isin([11, 12, 1, 2]).astype(int)
        
        # School holidays (affects staff availability - carers with children)
        df['is_school_holiday'] = df['date'].apply(self._is_school_holiday).astype(int)
        
        print(f"✓ Added temporal features")
        print(f"  - Weekends: {df['is_weekend'].sum():,} ({df['is_weekend'].mean()*100:.1f}%)")
        print(f"  - Holidays: {df['is_holiday'].sum():,} ({df['is_holiday'].mean()*100:.1f}%)")
        
        return df
    
    def add_lag_features(self, df, lags=[1, 7, 14], target_col='total_shifts'):
        """
        Add lag variables for previous days/weeks demand
        
        Args:
            df: DataFrame with date and target column
            lags: List of lag periods (e.g., [1, 7, 14])
            target_col: Column to create lags for
            
        Features:
        - lag_1: Previous day value
        - lag_7: Same day last week
        - lag_14: Same day 2 weeks ago
        """
        df = df.copy()
        
        # Determine grouping columns
        group_cols = [col for col in ['care_home', 'unit'] if col in df.columns]
        
        if group_cols:
            df = df.sort_values(group_cols + ['date'])
        else:
            df = df.sort_values('date')
        
        # Create lag features
        for lag in lags:
            col_name = f'shifts_lag_{lag}'
            if group_cols:
                df[col_name] = df.groupby(group_cols)[target_col].shift(lag)
            else:
                df[col_name] = df[target_col].shift(lag)
        
        print(f"✓ Added lag features: {lags}")
        
        return df
    
    def add_rolling_features(self, df, windows=[7, 14], target_col='total_shifts'):
        """
        Add rolling average and std features for trend detection
        
        Args:
            df: DataFrame with shift data
            windows: List of rolling window sizes in days
            target_col: Column to calculate rolling stats for
            
        Features:
        - rolling_mean_7: 7-day rolling average
        - rolling_std_7: 7-day rolling std deviation
        - rolling_mean_14: 14-day rolling average
        """
        df = df.copy()
        
        # Determine grouping columns
        group_cols = [col for col in ['care_home', 'unit'] if col in df.columns]
        
        if group_cols:
            df = df.sort_values(group_cols + ['date'])
        else:
            df = df.sort_values('date')
        
        # Calculate rolling statistics
        for window in windows:
            mean_col = f'shifts_rolling_mean_{window}'
            std_col = f'shifts_rolling_std_{window}'
            
            if group_cols:
                df[mean_col] = df.groupby(group_cols)[target_col].transform(
                    lambda x: x.rolling(window=window, min_periods=window).mean()
                )
                df[std_col] = df.groupby(group_cols)[target_col].transform(
                    lambda x: x.rolling(window=window, min_periods=window).std()
                )
            else:
                df[mean_col] = df[target_col].rolling(window=window, min_periods=window).mean()
                df[std_col] = df[target_col].rolling(window=window, min_periods=window).std()
        
        print(f"✓ Added rolling statistics ({', '.join(map(str, windows))} day windows)")
        
        return df
    
    def aggregate_to_daily(self, df, group_by=None):
        """
        Aggregate shift-level data to daily staffing demand
        
        Returns one row per care_home/unit/date with:
        - total_shifts: Total shifts scheduled
        - total_hours: Total hours of coverage (if available)
        - regular_shifts: Non-overtime, non-agency (if available)
        - unique_staff: Number of unique staff members (if available)
        """
        df = df.copy()
        
        # Auto-detect grouping columns
        if group_by is None:
            group_by = [col for col in ['care_home', 'unit'] if col in df.columns]
            group_by.append('date')
        
        # Build aggregation dict based on available columns
        agg_dict = {}
        
        if 'shift_hours' in df.columns:
            agg_dict['shift_hours'] = 'sum'
        
        if 'user_sap' in df.columns:
            agg_dict['user_sap'] = ['count', 'nunique']
        elif 'staff_sap' in df.columns:
            agg_dict['staff_sap'] = ['count', 'nunique']
        
        if 'shift_classification' in df.columns:
            agg_dict['shift_classification'] = lambda x: (x == 'REGULAR').sum()
        
        if 'agency_rate' in df.columns:
            agg_dict['agency_rate'] = 'mean'
        
        # Perform aggregation
        if agg_dict:
            daily = df.groupby(group_by).agg(agg_dict).reset_index()
            daily.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in daily.columns]
            
            # Rename to standard column names
            rename_map = {}
            if 'shift_hours_sum' in daily.columns:
                rename_map['shift_hours_sum'] = 'total_hours'
            if 'user_sap_count' in daily.columns:
                rename_map['user_sap_count'] = 'total_shifts'
                rename_map['user_sap_nunique'] = 'unique_staff'
            elif 'staff_sap_count' in daily.columns:
                rename_map['staff_sap_count'] = 'total_shifts'
                rename_map['staff_sap_nunique'] = 'unique_staff'
            if 'shift_classification_<lambda>' in daily.columns:
                rename_map['shift_classification_<lambda>'] = 'regular_shifts'
            if 'agency_rate_mean' in daily.columns:
                rename_map['agency_rate_mean'] = 'avg_agency_rate'
            
            daily.rename(columns=rename_map, inplace=True)
        else:
            # Simple count if no columns available
            daily = df.groupby(group_by).size().reset_index(name='total_shifts')
        
        print(f"✓ Aggregated to daily level: {len(daily):,} rows")
        if 'date' in daily.columns:
            print(f"  - Date range: {daily['date'].min()} to {daily['date'].max()}")
        
        return daily
    
    def create_prophet_dataframe(self, daily_df, target_col=None, target_column=None, date_col='date'):
        """
        Convert to Prophet format (ds, y columns)
        
        Args:
            daily_df: Daily aggregated dataframe
            target_col: Column to forecast (default: total_shifts)
            target_column: Alias for target_col (for test compatibility)
            date_col: Date column name
            
        Returns:
            pd.DataFrame: Prophet-ready with 'ds' and 'y' columns, sorted by date
        """
        # Accept either parameter name
        if target_column is not None:
            target_col = target_column
        elif target_col is None:
            target_col = 'total_shifts'
        
        prophet_df = daily_df[[date_col, target_col]].copy()
        prophet_df.columns = ['ds', 'y']
        
        # Prophet requires chronological order
        prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
        
        print(f"✓ Created Prophet dataframe: {len(prophet_df)} observations")
        print(f"  - Target: {target_col}")
        print(f"  - Mean: {prophet_df['y'].mean():.1f}")
        print(f"  - Std: {prophet_df['y'].std():.1f}")
        
        return prophet_df
    
    def fill_missing_dates(self, df, date_col='date', fill_cols=None, start_date=None, end_date=None):
        """
        Fill missing dates in time series with zero values
        
        Args:
            df: DataFrame with date column
            date_col: Name of date column
            fill_cols: Columns to fill with 0 (default: ['total_shifts'])
            start_date: Override start date (default: df min)
            end_date: Override end date (default: df max)
            
        Returns:
            pd.DataFrame: DataFrame with all dates filled
        """
        df = df.copy()
        
        if len(df) == 0:
            return df
        
        # Determine grouping columns
        group_cols = [col for col in ['care_home', 'unit'] if col in df.columns]
        
        if fill_cols is None:
            fill_cols = ['total_shifts']
        
        if group_cols:
            # Fill missing dates for each group
            filled_dfs = []
            for group_vals, group_df in df.groupby(group_cols):
                # Create complete date range
                min_date = start_date if start_date is not None else group_df[date_col].min()
                max_date = end_date if end_date is not None else group_df[date_col].max()
                
                date_range = pd.date_range(start=min_date, end=max_date, freq='D')
                
                # Create full date dataframe
                full_dates = pd.DataFrame({date_col: date_range})
                
                # Add group identifiers
                for i, col in enumerate(group_cols):
                    full_dates[col] = group_vals if len(group_cols) == 1 else group_vals[i]
                
                # Merge and fill
                merged = full_dates.merge(group_df, on=group_cols + [date_col], how='left')
                for col in fill_cols:
                    if col in merged.columns:
                        merged[col] = merged[col].fillna(0)
                
                filled_dfs.append(merged)
            
            result = pd.concat(filled_dfs, ignore_index=True)
        else:
            # No grouping - simple date fill
            min_date = start_date if start_date is not None else df[date_col].min()
            max_date = end_date if end_date is not None else df[date_col].max()
            
            date_range = pd.date_range(start=min_date, end=max_date, freq='D')
            full_dates = pd.DataFrame({date_col: date_range})
            result = full_dates.merge(df, on=date_col, how='left')
            
            for col in fill_cols:
                if col in result.columns:
                    result[col] = result[col].fillna(0)
        
        print(f"✓ Filled missing dates: {len(result)} total rows ({len(result) - len(df)} added)")
        
        return result
    
    def _is_school_holiday(self, date):
        """
        Determine if date falls in UK school holidays
        
        Approximate UK school holidays (Scotland):
        - Christmas: 2 weeks around Dec 25
        - Easter: 2 weeks around Easter
        - Summer: July-August
        - October: 1 week mid-October
        - February: 1 week mid-February
        """
        month = date.month
        day = date.day
        
        # Christmas holidays (Dec 20 - Jan 5)
        if (month == 12 and day >= 20) or (month == 1 and day <= 5):
            return True
        
        # Summer holidays (July 1 - Aug 15)
        if month == 7 or (month == 8 and day <= 15):
            return True
        
        # October break (week of Oct 15)
        if month == 10 and 10 <= day <= 20:
            return True
        
        # February break (week of Feb 12)
        if month == 2 and 8 <= day <= 16:
            return True
        
        # Easter (approximate - 2 weeks around early April)
        if month == 4 and day <= 14:
            return True
        
        return False


def prepare_ml_dataset(csv_path, output_path=None, care_home=None, unit=None):
    """
    Complete pipeline: load → engineer features → aggregate → save
    
    Args:
        csv_path: Path to shift export CSV
        output_path: Where to save processed data (default: ml_data/prepared_{care_home}_{unit}.csv)
        care_home: Filter to specific care home (optional)
        unit: Filter to specific unit (optional)
        
    Returns:
        pd.DataFrame: ML-ready daily staffing data
    """
    print("=== Staffing Demand Feature Engineering ===\n")
    
    engineer = StaffingFeatureEngineer()
    
    # Load data
    df = engineer.load_shift_data(csv_path)
    
    # Filter if specified
    if care_home:
        df = df[df['care_home'] == care_home]
        print(f"Filtered to care home: {care_home}")
    
    if unit:
        df = df[df['unit'] == unit]
        print(f"Filtered to unit: {unit}")
    
    # Feature engineering
    print("\nEngineering features...")
    df = engineer.add_temporal_features(df)
    df = engineer.add_lag_features(df)
    df = engineer.add_rolling_features(df)
    
    # Aggregate to daily
    print("\nAggregating to daily demand...")
    daily = engineer.aggregate_to_daily(df)
    
    # Save if output path provided
    if output_path:
        daily.to_csv(output_path, index=False)
        print(f"\n✓ Saved to {output_path}")
        print(f"  File size: {pd.read_csv(output_path).memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    print("\n✅ Feature engineering complete!")
    return daily
