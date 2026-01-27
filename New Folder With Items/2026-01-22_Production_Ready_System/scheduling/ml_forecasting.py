"""
Prophet-based Staffing Demand Forecasting

Scottish Design Principles:
- Evidence-Based: Prophet chosen for proven healthcare forecasting performance
- Transparent: Interpretable components (trend, seasonality, holidays)
- User-Centered: Confidence intervals for OM/SM risk assessment
- Participatory: Validation metrics align with planning needs

This module trains demand forecasters for:
1. 30-day rolling forecasts per care_home/unit
2. UK holiday effects on staffing
3. Seasonal patterns (winter pressure, school holidays)
4. Validation metrics (MAE, RMSE, MAPE)
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import holidays
from datetime import datetime, timedelta
from pathlib import Path
import json


class StaffingForecaster:
    """
    Train and deploy Prophet models for staffing demand forecasting
    
    Features:
    - Separate models per care_home/unit
    - UK holiday calendar (Scotland-specific)
    - Multiplicative seasonality (care demand scales with baseline)
    - Conservative changepoint detection (prevent overfitting)
    - 80% confidence intervals (Prophet default)
    """
    
    def __init__(self, care_home=None, unit=None):
        """
        Initialize forecaster for specific care_home/unit
        
        Args:
            care_home: CareHome name filter
            unit: Unit name filter
        """
        self.care_home = care_home
        self.unit = unit
        self.model = None
        self.train_metrics = {}
        self.uk_holidays = self._get_uk_holidays()
    
    def _get_uk_holidays(self, years=range(2024, 2028)):
        """
        Create UK holiday dataframe for Prophet
        
        Returns:
            pd.DataFrame: columns ['ds', 'holiday'] for Prophet
        """
        # Scotland-specific UK holidays
        uk = holidays.country_holidays('GB', subdiv='SCT', years=years)
        
        holiday_df = pd.DataFrame([
            {'ds': date, 'holiday': name}
            for date, name in uk.items()
        ])
        
        return holiday_df
    
    def prepare_training_data(self, daily_df):
        """
        Convert daily aggregated data to Prophet format
        
        Args:
            daily_df: Output from StaffingFeatureEngineer.aggregate_to_daily()
            
        Returns:
            pd.DataFrame: Prophet format (ds, y)
        """
        # Filter to care_home/unit if specified
        df = daily_df.copy()
        
        if self.care_home:
            df = df[df['care_home'] == self.care_home]
        
        if self.unit:
            df = df[df['unit'] == self.unit]
        
        # Prophet format
        prophet_df = df[['date', 'total_shifts']].copy()
        prophet_df.columns = ['ds', 'y']
        prophet_df = prophet_df.sort_values('ds')
        
        print(f"Training data: {len(prophet_df)} days")
        print(f"  Date range: {prophet_df['ds'].min()} to {prophet_df['ds'].max()}")
        print(f"  Mean: {prophet_df['y'].mean():.1f} shifts/day")
        print(f"  Std: {prophet_df['y'].std():.1f}")
        
        return prophet_df
    
    def train(self, prophet_df, validate=True, test_days=30):
        """
        Train Prophet model with UK holidays and seasonality
        
        Args:
            prophet_df: DataFrame with ds, y columns
            validate: Whether to perform train/test split
            test_days: Days to hold out for validation
            
        Returns:
            dict: Training metrics (MAE, RMSE, MAPE)
        """
        # Train/test split if validation requested
        if validate and len(prophet_df) > test_days:
            cutoff = prophet_df['ds'].max() - timedelta(days=test_days)
            train_df = prophet_df[prophet_df['ds'] <= cutoff].copy()
            test_df = prophet_df[prophet_df['ds'] > cutoff].copy()
            
            print(f"\nTrain/test split:")
            print(f"  Training: {len(train_df)} days (until {cutoff.date()})")
            print(f"  Testing: {len(test_df)} days ({test_days} day holdout)")
        else:
            train_df = prophet_df.copy()
            test_df = None
            print(f"\nTraining on full dataset: {len(train_df)} days")
        
        # Initialize Prophet model
        self.model = Prophet(
            yearly_seasonality=True,      # Annual cycles
            weekly_seasonality=True,       # Day-of-week patterns
            daily_seasonality=False,       # Not relevant for daily aggregates
            holidays=self.uk_holidays,     # UK public holidays
            seasonality_mode='multiplicative',  # Care demand scales with baseline
            changepoint_prior_scale=0.05,  # Conservative (prevent overfitting)
            interval_width=0.80            # 80% confidence intervals
        )
        
        # Add custom seasonalities
        # Winter pressure (Nov-Feb): increased dependency
        self.model.add_seasonality(
            name='winter_pressure',
            period=365.25,
            fourier_order=3,
            condition_name='is_winter'
        )
        
        # School holidays: reduced staff availability
        train_df['is_winter'] = train_df['ds'].dt.month.isin([11, 12, 1, 2])
        
        # Fit model
        print("\nTraining Prophet model...")
        self.model.fit(train_df)
        print("✓ Model trained")
        
        # Validate if test set exists
        if test_df is not None:
            test_df['is_winter'] = test_df['ds'].dt.month.isin([11, 12, 1, 2])
            
            # Generate predictions for test period
            forecast = self.model.predict(test_df[['ds', 'is_winter']])
            
            # Calculate metrics
            y_true = test_df['y'].values
            y_pred = forecast['yhat'].values
            
            mae = np.mean(np.abs(y_true - y_pred))
            rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
            mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            
            # Coverage (% of actual values within confidence interval)
            within_ci = (
                (y_true >= forecast['yhat_lower'].values) & 
                (y_true <= forecast['yhat_upper'].values)
            ).mean() * 100
            
            self.train_metrics = {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'coverage': within_ci,
                'test_days': test_days,
                'train_days': len(train_df)
            }
            
            print(f"\nValidation Metrics ({test_days}-day holdout):")
            print(f"  MAE:  {mae:.2f} shifts/day")
            print(f"  RMSE: {rmse:.2f} shifts/day")
            print(f"  MAPE: {mape:.1f}%")
            print(f"  Coverage: {within_ci:.1f}% (target: 80%)")
            
            # Interpretation
            avg_demand = train_df['y'].mean()
            print(f"\nInterpretation:")
            print(f"  Average demand: {avg_demand:.1f} shifts/day")
            print(f"  MAE as % of avg: {(mae/avg_demand)*100:.1f}%")
            
            if mape < 20:
                print(f"  ✅ Excellent accuracy (MAPE < 20%)")
            elif mape < 30:
                print(f"  ✓ Good accuracy (MAPE < 30%)")
            else:
                print(f"  ⚠ Moderate accuracy (MAPE >= 30%)")
        
        return self.train_metrics
    
    def forecast(self, days_ahead=30):
        """
        Generate future forecasts
        
        Args:
            days_ahead: Number of days to forecast ahead
            
        Returns:
            pd.DataFrame: Predictions with ds, yhat, yhat_lower, yhat_upper
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=days_ahead)
        future['is_winter'] = future['ds'].dt.month.isin([11, 12, 1, 2])
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Return only future predictions
        forecast_future = forecast[forecast['ds'] > self.model.history['ds'].max()]
        
        print(f"\nForecast for next {days_ahead} days:")
        print(f"  Date range: {forecast_future['ds'].min().date()} to {forecast_future['ds'].max().date()}")
        print(f"  Mean predicted: {forecast_future['yhat'].mean():.1f} shifts/day")
        print(f"  Range: {forecast_future['yhat'].min():.1f} - {forecast_future['yhat'].max():.1f}")
        
        return forecast_future[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend', 'weekly', 'yearly']]
    
    def get_component_importance(self):
        """
        Analyze which components contribute most to forecast
        
        Returns:
            dict: Component contributions (trend, weekly, yearly, holidays)
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        # Generate forecast for last 30 days
        last_30 = self.model.history.tail(30)
        last_30['is_winter'] = last_30['ds'].dt.month.isin([11, 12, 1, 2])
        forecast = self.model.predict(last_30)
        
        # Calculate variance contribution
        components = {}
        
        if 'trend' in forecast.columns:
            components['trend'] = forecast['trend'].std()
        
        if 'weekly' in forecast.columns:
            components['weekly'] = forecast['weekly'].std()
        
        if 'yearly' in forecast.columns:
            components['yearly'] = forecast['yearly'].std()
        
        if 'holidays' in forecast.columns:
            components['holidays'] = forecast['holidays'].std()
        
        # Normalize to percentages
        total_variance = sum(components.values())
        if total_variance > 0:
            components = {k: (v/total_variance)*100 for k, v in components.items()}
        
        return components
    
    def save_model(self, output_dir='ml_data/models'):
        """
        Save trained model to disk
        
        Args:
            output_dir: Directory to save model
        """
        if self.model is None:
            raise ValueError("No model to save. Call train() first.")
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Model filename
        filename = f"forecaster_{self.care_home}_{self.unit}.json"
        filepath = Path(output_dir) / filename
        
        # Save model
        import pickle
        with open(filepath.with_suffix('.pkl'), 'wb') as f:
            pickle.dump(self.model, f)
        
        # Save metadata
        metadata = {
            'care_home': self.care_home,
            'unit': self.unit,
            'trained_at': datetime.now().isoformat(),
            'metrics': self.train_metrics,
            'model_type': 'Prophet',
            'version': '1.0'
        }
        
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Model saved to {filepath}")
        print(f"  Metadata: {filepath}")
        print(f"  Weights: {filepath.with_suffix('.pkl')}")


def train_all_units(daily_df, output_dir='ml_data/forecasts', test_days=30):
    """
    Train separate forecasters for each care_home/unit combination
    
    Args:
        daily_df: Aggregated daily data from feature engineering
        output_dir: Where to save forecasts
        test_days: Days to hold out for validation
        
    Returns:
        dict: Results for each unit {(care_home, unit): metrics}
    """
    print("=== Training Forecasters for All Units ===\n")
    
    # Get unique care_home/unit combinations
    units = daily_df.groupby(['care_home', 'unit']).size().reset_index()[['care_home', 'unit']]
    
    print(f"Found {len(units)} care_home/unit combinations")
    print(f"  Care homes: {daily_df['care_home'].nunique()}")
    print(f"  Total units: {daily_df['unit'].nunique()}\n")
    
    results = {}
    forecasts_all = []
    
    for idx, row in units.iterrows():
        care_home = row['care_home']
        unit = row['unit']
        
        print(f"\n{'='*60}")
        print(f"Training: {care_home} / {unit} ({idx+1}/{len(units)})")
        print(f"{'='*60}")
        
        try:
            # Initialize forecaster
            forecaster = StaffingForecaster(care_home=care_home, unit=unit)
            
            # Prepare data
            prophet_df = forecaster.prepare_training_data(daily_df)
            
            # Skip if insufficient data
            if len(prophet_df) < test_days + 30:
                print(f"⚠ Skipping - insufficient data ({len(prophet_df)} days)")
                continue
            
            # Train
            metrics = forecaster.train(prophet_df, validate=True, test_days=test_days)
            
            # Forecast 30 days ahead
            forecast_df = forecaster.forecast(days_ahead=30)
            forecast_df['care_home'] = care_home
            forecast_df['unit'] = unit
            forecasts_all.append(forecast_df)
            
            # Component analysis
            components = forecaster.get_component_importance()
            print(f"\nComponent Importance:")
            for comp, pct in sorted(components.items(), key=lambda x: x[1], reverse=True):
                print(f"  {comp}: {pct:.1f}%")
            
            # Save model
            forecaster.save_model()
            
            # Store results
            results[(care_home, unit)] = {
                'metrics': metrics,
                'components': components,
                'forecast_mean': forecast_df['yhat'].mean()
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    # Save all forecasts
    if forecasts_all:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        all_forecasts = pd.concat(forecasts_all, ignore_index=True)
        output_path = Path(output_dir) / 'all_units_30day_forecast.csv'
        all_forecasts.to_csv(output_path, index=False)
        
        print(f"\n\n{'='*60}")
        print(f"✅ Training Complete!")
        print(f"{'='*60}")
        print(f"Models trained: {len(results)}/{len(units)}")
        print(f"All forecasts saved: {output_path}")
        print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    # Summary statistics
    if results:
        all_mae = [r['metrics']['mae'] for r in results.values() if 'mae' in r['metrics']]
        all_mape = [r['metrics']['mape'] for r in results.values() if 'mape' in r['metrics']]
        
        print(f"\nOverall Performance:")
        print(f"  Avg MAE: {np.mean(all_mae):.2f} shifts/day")
        print(f"  Avg MAPE: {np.mean(all_mape):.1f}%")
        print(f"  Best MAPE: {np.min(all_mape):.1f}%")
        print(f"  Worst MAPE: {np.max(all_mape):.1f}%")
    
    return results


def quick_forecast(care_home, unit, csv_path='ml_data/prepared_all_homes.csv', days_ahead=30):
    """
    Quick forecast for a single care_home/unit
    
    Args:
        care_home: CareHome name
        unit: Unit name
        csv_path: Path to prepared daily data
        days_ahead: Days to forecast
        
    Returns:
        pd.DataFrame: Forecast with confidence intervals
    """
    print(f"=== Quick Forecast: {care_home} / {unit} ===\n")
    
    # Load prepared data
    daily_df = pd.read_csv(csv_path)
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    
    # Initialize and train
    forecaster = StaffingForecaster(care_home=care_home, unit=unit)
    prophet_df = forecaster.prepare_training_data(daily_df)
    forecaster.train(prophet_df, validate=True, test_days=30)
    
    # Generate forecast
    forecast_df = forecaster.forecast(days_ahead=days_ahead)
    
    return forecast_df
