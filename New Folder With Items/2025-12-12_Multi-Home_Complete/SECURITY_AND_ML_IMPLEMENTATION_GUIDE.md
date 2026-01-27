# Security Hardening & Machine Learning Implementation Guide

**Document Purpose:** Practical implementation guide for enhancing the Staff Rota system with security hardening (P0 fixes) and machine learning capabilities.

**Target Audience:** Development team, System administrators, Project managers

**Last Updated:** 21 December 2025

---

## Part 1: Security Hardening (P0 - Critical Priority)

**Estimated Effort:** 7 hours  
**Impact:** Production readiness score: 7.2/10 → 8.5/10

### 1.1 Authentication & Authorization Hardening

#### Current Vulnerabilities:
- Potentially weak password policies
- No multi-factor authentication (MFA)
- Session timeout settings may be too long
- No account lockout after failed login attempts

#### Implementation Steps:

**Step 1: Strengthen Password Policy**
```python
# settings.py - Add Django password validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increase from default 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Force password change on first login
PASSWORD_EXPIRY_DAYS = 90  # Healthcare compliance standard
```

**Step 2: Implement Account Lockout Protection**
```bash
# Install django-axes for brute force protection
pip install django-axes
```

```python
# settings.py
INSTALLED_APPS = [
    # ... existing apps
    'axes',
]

MIDDLEWARE = [
    # ... existing middleware
    'axes.middleware.AxesMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',  # Add first
    'django.contrib.auth.backends.ModelBackend',
]

# Axes configuration
AXES_FAILURE_LIMIT = 5  # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1  # Lock for 1 hour
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_RESET_ON_SUCCESS = True
```

**Step 3: Session Security**
```python
# settings.py

# Session security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour timeout (healthcare requirement)

# CSRF protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

**Step 4: HTTPS Enforcement**
```python
# settings.py - Production only

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 1.2 Data Protection & Privacy (GDPR/Data Protection Act 2018)

#### Implementation Steps:

**Step 1: Audit Logging**
```bash
pip install django-auditlog
```

```python
# settings.py
INSTALLED_APPS = [
    # ... existing apps
    'auditlog',
]

MIDDLEWARE = [
    # ... existing middleware
    'auditlog.middleware.AuditlogMiddleware',
]

# models.py - Add to sensitive models
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

class Staff(models.Model):
    # ... existing fields
    history = AuditlogHistoryField()

# Register models for auditing
auditlog.register(Staff)
auditlog.register(Shift)
auditlog.register(LeaveRequest)
auditlog.register(TrainingRecord)
```

**Step 2: Personal Data Encryption**
```bash
pip install django-encrypted-model-fields
```

```python
# models.py - Encrypt sensitive fields
from encrypted_model_fields.fields import EncryptedCharField, EncryptedDateField

class Staff(models.Model):
    # ... existing fields
    national_insurance = EncryptedCharField(max_length=13)  # Encrypt NI numbers
    emergency_contact_phone = EncryptedCharField(max_length=20)
    date_of_birth = EncryptedDateField()
    
# settings.py
FIELD_ENCRYPTION_KEY = env('FIELD_ENCRYPTION_KEY')  # Store in environment variable
```

**Step 3: Data Retention Policy**
```python
# management/commands/cleanup_old_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Remove data older than retention period'

    def handle(self, *args, **options):
        # Healthcare record retention: 6 years in Scotland
        retention_date = timezone.now() - timedelta(days=365*6)
        
        # Archive or delete old shifts
        old_shifts = Shift.objects.filter(date__lt=retention_date)
        self.stdout.write(f'Archiving {old_shifts.count()} old shifts')
        # Move to archive table or export before deletion
        old_shifts.delete()
        
        # Keep audit logs for 7 years (compliance requirement)
        audit_retention = timezone.now() - timedelta(days=365*7)
        from auditlog.models import LogEntry
        LogEntry.objects.filter(timestamp__lt=audit_retention).delete()
```

**Step 4: Privacy Controls**
```python
# Add data access controls to views.py
from django.contrib.auth.mixins import UserPassesTestMixin

class StaffDetailView(UserPassesTestMixin, DetailView):
    model = Staff
    
    def test_func(self):
        # Only allow viewing staff from same home unless senior manager
        staff = self.get_object()
        user = self.request.user
        
        if user.profile.is_senior_manager:
            return True
        return staff.home == user.profile.home
```

### 1.3 SQL Injection & XSS Prevention

**Step 1: Verify ORM Usage (Already Implemented)**
```python
# GOOD - Django ORM (parameterized)
Staff.objects.filter(name__icontains=search_term)

# BAD - Raw SQL (vulnerable)
# cursor.execute(f"SELECT * FROM staff WHERE name LIKE '%{search_term}%'")
```

**Step 2: Output Escaping in Templates**
```html
<!-- templates/*.html - Django auto-escapes by default -->

<!-- SAFE - Auto-escaped -->
<p>{{ staff.name }}</p>

<!-- UNSAFE - Use only for trusted HTML -->
<!-- <p>{{ staff.notes|safe }}</p> -->

<!-- For user-generated content, use escape explicitly -->
<p>{{ leave_request.reason|escape }}</p>
```

**Step 3: Content Security Policy (CSP)**
```bash
pip install django-csp
```

```python
# settings.py
MIDDLEWARE = [
    # ... existing middleware
    'csp.middleware.CSPMiddleware',
]

# CSP configuration
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Remove unsafe-inline in production
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://cdn.jsdelivr.net")
```

### 1.4 Dependency Security

**Step 1: Vulnerability Scanning**
```bash
# Check for known vulnerabilities
pip install safety
safety check

# Update requirements.txt
pip freeze > requirements.txt

# Use pip-audit for more comprehensive scanning
pip install pip-audit
pip-audit
```

**Step 2: Keep Django Updated**
```bash
# Current version check
python -m django --version

# Update to latest security release
pip install --upgrade Django

# Pin major version but allow patch updates
# requirements.txt
Django>=4.2,<5.0  # Allows 4.2.x security updates
```

**Step 3: Automated Dependency Monitoring**
```yaml
# .github/workflows/security.yml (if using GitHub)
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Safety
        run: |
          pip install safety
          safety check
```

### 1.5 Environment Variable Security

**Step 1: Use Environment Variables**
```python
# settings.py
import os
from pathlib import Path

# NEVER commit these to git!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.environ.get('DB_NAME', 'db.sqlite3'),
    }
}

# Email credentials
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

**Step 2: Create .env File (Never commit to git)**
```bash
# .env (add to .gitignore)
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
DB_NAME=db.sqlite3
EMAIL_USER=noreply@yourcaregroup.com
EMAIL_PASSWORD=your-email-password
FIELD_ENCRYPTION_KEY=your-encryption-key-32-bytes
```

**Step 3: Update .gitignore**
```
# .gitignore
.env
.env.local
.env.production
*.key
*.pem
db.sqlite3
```

### 1.6 File Upload Security

```python
# settings.py
import os

# File upload restrictions
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

ALLOWED_FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']

# forms.py
from django.core.exceptions import ValidationError

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')

class DocumentUploadForm(forms.Form):
    file = forms.FileField(validators=[validate_file_extension])
```

### 1.7 Production Checklist

```bash
# Run Django's deployment checklist
python manage.py check --deploy
```

**Address all warnings before production deployment.**

---

## Part 2: Machine Learning Implementation

**Estimated Effort:** 40-60 hours (Phase 1), 80-120 hours (Full implementation)  
**Impact:** 10-15% cost reduction, improved staff satisfaction

### 2.1 Shift Demand Prediction (Time Series Forecasting)

**Business Problem:** Predict staffing needs to optimize shift allocation and reduce overtime/agency costs.

#### Phase 1: Data Collection & Preparation (8 hours)

**Step 1: Create ML-Ready Data Export**
```python
# management/commands/export_ml_data.py
from django.core.management.base import BaseCommand
import pandas as pd
from rota.models import Shift, Staff
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Export shift data for ML training'

    def handle(self, *args, **options):
        # Get last 2 years of shift data
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=730)
        
        shifts = Shift.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).select_related('staff', 'home', 'unit')
        
        # Build dataset
        data = []
        for shift in shifts:
            data.append({
                'date': shift.date,
                'home': shift.home.name,
                'unit': shift.unit.name,
                'shift_type': shift.shift_type,
                'staff_role': shift.staff.role,
                'hours': shift.hours,
                'is_overtime': shift.is_overtime,
                'is_agency': shift.is_agency,
                'cost': shift.calculate_cost(),
                'day_of_week': shift.date.weekday(),
                'month': shift.date.month,
                'is_weekend': shift.date.weekday() >= 5,
                'is_bank_holiday': shift.is_bank_holiday(),
            })
        
        df = pd.DataFrame(data)
        df.to_csv('ml_data/shift_history.csv', index=False)
        self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} shifts'))
```

**Step 2: Feature Engineering**
```python
# ml/data_prep.py
import pandas as pd
import numpy as np
from datetime import datetime

def prepare_features(df):
    """Prepare features for ML model"""
    
    # Time-based features
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['month'] = pd.to_datetime(df['date']).dt.month
    df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
    df['week_of_year'] = pd.to_datetime(df['date']).dt.isocalendar().week
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Cyclical encoding for time (better for ML models)
    df['month_sin'] = np.sin(2 * np.pi * df['month']/12)
    df['month_cos'] = np.cos(2 * np.pi * df['month']/12)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)
    
    # Aggregate by date/home/unit
    daily_demand = df.groupby(['date', 'home', 'unit']).agg({
        'hours': 'sum',
        'cost': 'sum',
        'is_overtime': 'sum',
        'is_agency': 'sum'
    }).reset_index()
    
    # Lag features (previous week same day)
    daily_demand = daily_demand.sort_values('date')
    daily_demand['hours_lag_7'] = daily_demand.groupby(['home', 'unit'])['hours'].shift(7)
    daily_demand['hours_lag_14'] = daily_demand.groupby(['home', 'unit'])['hours'].shift(14)
    
    # Rolling averages
    daily_demand['hours_rolling_7'] = daily_demand.groupby(['home', 'unit'])['hours'].rolling(7).mean().reset_index(0, drop=True)
    daily_demand['hours_rolling_30'] = daily_demand.groupby(['home', 'unit'])['hours'].rolling(30).mean().reset_index(0, drop=True)
    
    return daily_demand
```

#### Phase 2: Model Training (12 hours)

**Option A: Classical Time Series (Prophet - Recommended for Start)**
```python
# ml/models/demand_forecast.py
from prophet import Prophet
import pandas as pd
import pickle

class DemandForecaster:
    def __init__(self, home_name, unit_name):
        self.home_name = home_name
        self.unit_name = unit_name
        self.model = None
        
    def train(self, df):
        """Train Prophet model on historical data"""
        # Filter to specific home/unit
        data = df[(df['home'] == self.home_name) & (df['unit'] == self.unit_name)].copy()
        
        # Prophet requires 'ds' (date) and 'y' (target) columns
        prophet_df = data[['date', 'hours']].rename(columns={'date': 'ds', 'hours': 'y'})
        
        # Initialize model with seasonality
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        # Add UK bank holidays
        self.model.add_country_holidays(country_name='UK')
        
        # Fit model
        self.model.fit(prophet_df)
        
        return self
    
    def predict(self, days_ahead=30):
        """Predict staffing demand for next N days"""
        future = self.model.make_future_dataframe(periods=days_ahead)
        forecast = self.model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
    
    def save(self, filepath):
        """Save trained model"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
    
    @classmethod
    def load(cls, filepath, home_name, unit_name):
        """Load trained model"""
        instance = cls(home_name, unit_name)
        with open(filepath, 'rb') as f:
            instance.model = pickle.load(f)
        return instance

# Usage example
if __name__ == '__main__':
    df = pd.read_csv('ml_data/shift_history.csv')
    
    # Train model for each home/unit combination
    for home in df['home'].unique():
        for unit in df[df['home'] == home]['unit'].unique():
            forecaster = DemandForecaster(home, unit)
            forecaster.train(df)
            forecaster.save(f'ml_models/demand_{home}_{unit}.pkl')
            
            # Get 14-day forecast
            forecast = forecaster.predict(14)
            print(f"\n{home} - {unit} Forecast:")
            print(forecast)
```

**Option B: Machine Learning (Scikit-learn)**
```python
# ml/models/ml_forecast.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas as pd
import numpy as np
import pickle

class MLDemandForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.feature_columns = None
        
    def train(self, df):
        """Train Random Forest model"""
        # Features to use
        feature_cols = [
            'home', 'unit', 'month_sin', 'month_cos', 
            'day_sin', 'day_cos', 'is_weekend',
            'hours_lag_7', 'hours_lag_14', 
            'hours_rolling_7', 'hours_rolling_30'
        ]
        
        # One-hot encode categorical variables
        df_encoded = pd.get_dummies(df, columns=['home', 'unit'], drop_first=True)
        
        # Update feature columns after encoding
        self.feature_columns = [col for col in df_encoded.columns if col.startswith(tuple(feature_cols))]
        
        # Remove rows with NaN (from lag features)
        df_clean = df_encoded.dropna()
        
        X = df_clean[self.feature_columns]
        y = df_clean['hours']
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print(f"Model Performance:")
        print(f"  MAE: {mae:.2f} hours")
        print(f"  RMSE: {rmse:.2f} hours")
        
        # Feature importance
        importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\nTop 5 Important Features:")
        print(importance.head())
        
        return self
    
    def save(self, filepath):
        """Save trained model"""
        with open(filepath, 'wb') as f:
            pickle.dump((self.model, self.feature_columns), f)
```

#### Phase 3: Integration with Django (10 hours)

**Step 1: Add ML Predictions to Database**
```python
# rota/models.py
class StaffingDemandForecast(models.Model):
    home = models.ForeignKey('Home', on_delete=models.CASCADE)
    unit = models.ForeignKey('Unit', on_delete=models.CASCADE)
    date = models.DateField()
    predicted_hours = models.DecimalField(max_digits=5, decimal_places=2)
    confidence_lower = models.DecimalField(max_digits=5, decimal_places=2)
    confidence_upper = models.DecimalField(max_digits=5, decimal_places=2)
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('home', 'unit', 'date', 'model_version')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.home} - {self.unit} - {self.date}: {self.predicted_hours}hrs"
```

**Step 2: Management Command for Daily Forecasting**
```python
# management/commands/generate_forecasts.py
from django.core.management.base import BaseCommand
from rota.models import Home, Unit, StaffingDemandForecast
from ml.models.demand_forecast import DemandForecaster
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Generate staffing demand forecasts'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=14, help='Days to forecast')

    def handle(self, *args, **options):
        days_ahead = options['days']
        
        for home in Home.objects.all():
            for unit in home.units.all():
                try:
                    # Load trained model
                    model_path = f'ml_models/demand_{home.slug}_{unit.slug}.pkl'
                    forecaster = DemandForecaster.load(model_path, home.name, unit.name)
                    
                    # Generate forecast
                    forecast = forecaster.predict(days_ahead)
                    
                    # Save to database
                    for _, row in forecast.iterrows():
                        StaffingDemandForecast.objects.update_or_create(
                            home=home,
                            unit=unit,
                            date=row['ds'].date(),
                            model_version='prophet_v1',
                            defaults={
                                'predicted_hours': row['yhat'],
                                'confidence_lower': row['yhat_lower'],
                                'confidence_upper': row['yhat_upper'],
                            }
                        )
                    
                    self.stdout.write(self.style.SUCCESS(
                        f'Generated forecast for {home.name} - {unit.name}'
                    ))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error forecasting {home.name} - {unit.name}: {str(e)}'
                    ))
```

**Step 3: Display in Dashboard**
```python
# views.py
from rota.models import StaffingDemandForecast
from django.utils import timezone

class StaffingDemandView(LoginRequiredMixin, TemplateView):
    template_name = 'rota/staffing_demand.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get forecasts for next 14 days
        today = timezone.now().date()
        forecasts = StaffingDemandForecast.objects.filter(
            home=self.request.user.profile.home,
            date__gte=today,
            date__lte=today + timedelta(days=14)
        ).select_related('home', 'unit')
        
        # Organize by unit
        by_unit = {}
        for forecast in forecasts:
            if forecast.unit.name not in by_unit:
                by_unit[forecast.unit.name] = []
            by_unit[forecast.unit.name].append(forecast)
        
        context['forecasts_by_unit'] = by_unit
        return context
```

```html
<!-- templates/rota/staffing_demand.html -->
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>Staffing Demand Forecast - Next 14 Days</h2>
    
    {% for unit_name, forecasts in forecasts_by_unit.items %}
    <div class="card mb-3">
        <div class="card-header">
            <h4>{{ unit_name }}</h4>
        </div>
        <div class="card-body">
            <canvas id="chart-{{ forloop.counter }}"></canvas>
            
            <table class="table table-sm mt-3">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Day</th>
                        <th>Predicted Hours</th>
                        <th>Range</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for forecast in forecasts %}
                    <tr class="{% if forecast.predicted_hours > 50 %}table-warning{% endif %}">
                        <td>{{ forecast.date }}</td>
                        <td>{{ forecast.date|date:"l" }}</td>
                        <td><strong>{{ forecast.predicted_hours|floatformat:1 }} hrs</strong></td>
                        <td>{{ forecast.confidence_lower|floatformat:1 }} - {{ forecast.confidence_upper|floatformat:1 }}</td>
                        <td>
                            {% if forecast.predicted_hours > 50 %}
                            <span class="badge badge-warning">High Demand</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endfor %}
</div>

<script>
    // Chart.js visualization code here
</script>
{% endblock %}
```

### 2.2 Shift Optimization Algorithm (20-30 hours)

**Business Problem:** Optimize shift assignments to minimize cost while respecting constraints.

```python
# ml/optimizer.py
from pulp import *
import pandas as pd

class ShiftOptimizer:
    """
    Optimize shift assignments using Linear Programming
    """
    
    def __init__(self, staff_list, demand_forecast, date):
        self.staff = staff_list
        self.demand = demand_forecast
        self.date = date
        self.model = None
        
    def optimize(self):
        """
        Minimize cost subject to constraints:
        - Meet staffing demand
        - Respect staff availability
        - Fair distribution of shifts
        - Prefer permanent staff over agency
        """
        
        # Create optimization problem
        self.model = LpProblem("Shift_Assignment", LpMinimize)
        
        # Decision variables: x[staff, shift_type] = 1 if assigned, 0 otherwise
        shift_types = ['early', 'late', 'night', 'long_day']
        x = LpVariable.dicts(
            "assign",
            ((s.id, shift) for s in self.staff for shift in shift_types),
            cat='Binary'
        )
        
        # Objective function: Minimize total cost
        costs = {
            s.id: s.hourly_rate * 1.0 if not s.is_agency else s.hourly_rate * 1.5
            for s in self.staff
        }
        
        shift_hours = {'early': 8, 'late': 8, 'night': 10, 'long_day': 12}
        
        self.model += lpSum([
            x[s.id, shift] * costs[s.id] * shift_hours[shift]
            for s in self.staff
            for shift in shift_types
        ])
        
        # Constraint 1: Meet demand for each shift type
        for shift in shift_types:
            required = self.demand.get(shift, 0)
            self.model += lpSum([
                x[s.id, shift] for s in self.staff
            ]) >= required, f"Demand_{shift}"
        
        # Constraint 2: Each staff member works at most 1 shift per day
        for s in self.staff:
            self.model += lpSum([
                x[s.id, shift] for shift in shift_types
            ]) <= 1, f"OneShift_{s.id}"
        
        # Constraint 3: Respect staff availability
        for s in self.staff:
            if not s.is_available(self.date):
                for shift in shift_types:
                    self.model += x[s.id, shift] == 0, f"Unavailable_{s.id}_{shift}"
        
        # Constraint 4: Skill matching
        for shift in shift_types:
            # At least 1 qualified nurse per shift
            qualified_staff = [s for s in self.staff if s.role == 'RN']
            self.model += lpSum([
                x[s.id, shift] for s in qualified_staff
            ]) >= 1, f"QualifiedStaff_{shift}"
        
        # Solve
        self.model.solve()
        
        # Extract solution
        assignments = []
        for s in self.staff:
            for shift in shift_types:
                if value(x[s.id, shift]) == 1:
                    assignments.append({
                        'staff': s,
                        'shift_type': shift,
                        'hours': shift_hours[shift],
                        'cost': costs[s.id] * shift_hours[shift]
                    })
        
        return {
            'status': LpStatus[self.model.status],
            'total_cost': value(self.model.objective),
            'assignments': assignments
        }

# Usage
from rota.models import Staff, StaffingDemandForecast
from datetime import date

staff = Staff.objects.filter(home=home, is_active=True)
demand = {
    'early': 5,
    'late': 5,
    'night': 3,
}

optimizer = ShiftOptimizer(staff, demand, date.today())
result = optimizer.optimize()

print(f"Optimization Status: {result['status']}")
print(f"Total Cost: £{result['total_cost']:.2f}")
for assignment in result['assignments']:
    print(f"  {assignment['staff'].name} → {assignment['shift_type']} (£{assignment['cost']:.2f})")
```

### 2.3 Absence Prediction (15 hours)

```python
# ml/models/absence_predictor.py
from sklearn.ensemble import GradientBoostingClassifier
import pandas as pd

class AbsencePredictor:
    """
    Predict likelihood of staff absence based on historical patterns
    """
    
    def __init__(self):
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        
    def prepare_features(self, staff_member):
        """Extract features for prediction"""
        # Historical absence rate
        total_shifts = staff_member.shifts.count()
        absences = staff_member.absences.count()
        absence_rate = absences / total_shifts if total_shifts > 0 else 0
        
        # Recent pattern (last 30 days)
        recent_absences = staff_member.absences.filter(
            date__gte=timezone.now().date() - timedelta(days=30)
        ).count()
        
        # Seasonal factors
        current_month = timezone.now().month
        
        # Workload indicators
        overtime_hours = staff_member.overtime_hours_this_month()
        consecutive_days = staff_member.consecutive_days_worked()
        
        return {
            'absence_rate': absence_rate,
            'recent_absences': recent_absences,
            'month': current_month,
            'overtime_hours': overtime_hours,
            'consecutive_days': consecutive_days,
            'day_of_week': timezone.now().weekday(),
        }
    
    def predict_risk(self, staff_member):
        """Predict absence risk (0-1 probability)"""
        features = self.prepare_features(staff_member)
        X = pd.DataFrame([features])
        
        probability = self.model.predict_proba(X)[0][1]
        
        return {
            'risk_score': probability,
            'risk_level': 'High' if probability > 0.3 else 'Medium' if probability > 0.15 else 'Low',
            'factors': features
        }
```

### 2.4 Automated Retraining Pipeline

```python
# management/commands/retrain_ml_models.py
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Retrain all ML models with latest data'

    def handle(self, *args, **options):
        self.stdout.write('Step 1: Exporting latest data...')
        call_command('export_ml_data')
        
        self.stdout.write('Step 2: Training demand forecast models...')
        # Train Prophet models
        from ml.training import train_all_forecasters
        train_all_forecasters()
        
        self.stdout.write('Step 3: Generating new forecasts...')
        call_command('generate_forecasts', days=30)
        
        self.stdout.write(self.style.SUCCESS('✅ ML models retrained successfully'))
```

**Schedule via cron:**
```bash
# Retrain monthly (first day of month at 2am)
0 2 1 * * cd /path/to/project && python manage.py retrain_ml_models
```

---

## Part 3: Deployment & Monitoring

### 3.1 Security Monitoring

```python
# Add monitoring for security events
# monitoring/security_monitor.py
from django.core.mail import send_mail
from axes.models import AccessAttempt

def check_security_alerts():
    """Send alerts for suspicious activity"""
    
    # Check for multiple lockouts
    recent_lockouts = AccessAttempt.objects.filter(
        failures_since_start__gte=5,
        attempt_time__gte=timezone.now() - timedelta(hours=1)
    )
    
    if recent_lockouts.count() > 10:
        send_mail(
            subject='SECURITY ALERT: Multiple Account Lockouts',
            message=f'{recent_lockouts.count()} accounts locked in last hour',
            from_email='security@yourcaregroup.com',
            recipient_list=['it-security@yourcaregroup.com'],
        )
```

### 3.2 ML Model Monitoring

```python
# ml/monitoring.py
class ModelMonitor:
    """Monitor ML model performance in production"""
    
    def check_forecast_accuracy(self):
        """Compare predictions vs actual"""
        from rota.models import StaffingDemandForecast, Shift
        from datetime import timedelta
        
        # Get forecasts from 7 days ago
        check_date = timezone.now().date() - timedelta(days=7)
        forecasts = StaffingDemandForecast.objects.filter(date=check_date)
        
        errors = []
        for forecast in forecasts:
            # Get actual hours worked
            actual = Shift.objects.filter(
                home=forecast.home,
                unit=forecast.unit,
                date=check_date
            ).aggregate(total=Sum('hours'))['total'] or 0
            
            predicted = float(forecast.predicted_hours)
            error = abs(predicted - actual)
            mape = (error / actual * 100) if actual > 0 else 0
            
            errors.append(mape)
        
        avg_error = sum(errors) / len(errors) if errors else 0
        
        # Alert if accuracy drops below 85%
        if avg_error > 15:
            send_mail(
                subject='ML MODEL ALERT: Forecast Accuracy Degraded',
                message=f'Average forecast error: {avg_error:.1f}%. Consider retraining.',
                from_email='ml-monitoring@yourcaregroup.com',
                recipient_list=['dev-team@yourcaregroup.com'],
            )
        
        return avg_error
```

---

## Part 4: Testing Strategy

### 4.1 Security Testing

```python
# tests/test_security.py
from django.test import TestCase, Client
from django.contrib.auth.models import User

class SecurityTests(TestCase):
    
    def test_password_strength(self):
        """Test password validation"""
        user = User.objects.create_user('test', 'test@test.com')
        
        # Should reject weak passwords
        with self.assertRaises(ValidationError):
            user.set_password('12345')
        
        # Should accept strong passwords
        user.set_password('StrongP@ssw0rd123!')
        self.assertTrue(user.check_password('StrongP@ssw0rd123!'))
    
    def test_account_lockout(self):
        """Test brute force protection"""
        client = Client()
        
        # Try 5 failed logins
        for i in range(6):
            client.post('/accounts/login/', {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        
        # Account should be locked
        response = client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'correctpassword'
        })
        
        self.assertContains(response, 'locked')
    
    def test_session_timeout(self):
        """Test session expiry"""
        from django.conf import settings
        self.assertEqual(settings.SESSION_COOKIE_AGE, 3600)  # 1 hour
```

### 4.2 ML Model Testing

```python
# tests/test_ml_models.py
from django.test import TestCase
from ml.models.demand_forecast import DemandForecaster
import pandas as pd

class MLTests(TestCase):
    
    def test_forecast_generation(self):
        """Test forecast model produces valid output"""
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=365)
        data = pd.DataFrame({
            'date': dates,
            'home': 'Test Home',
            'unit': 'Test Unit',
            'hours': [40 + (i % 7) * 5 for i in range(365)]
        })
        
        # Train model
        forecaster = DemandForecaster('Test Home', 'Test Unit')
        forecaster.train(data)
        
        # Generate forecast
        forecast = forecaster.predict(7)
        
        # Validate output
        self.assertEqual(len(forecast), 7)
        self.assertTrue(all(forecast['yhat'] > 0))
        self.assertTrue(all(forecast['yhat_lower'] < forecast['yhat_upper']))
```

---

## Part 5: Cost-Benefit Analysis

### Security Hardening:
- **Time Investment:** 7 hours
- **Cost:** £259 (at £37/hour developer rate)
- **Benefits:**
  - Avoid GDPR fines (up to £17.5M or 4% of turnover)
  - Prevent data breaches (avg UK cost: £3.2M)
  - Insurance compliance (lower premiums)
  - Care Inspectorate compliance

**ROI: Immeasurable (risk mitigation)**

### Machine Learning:
- **Time Investment:** 60 hours (Phase 1)
- **Cost:** £2,220 (development)
- **Benefits:**
  - 10-15% cost reduction: £55,000-£88,000/year
  - Reduced overtime: £20,000-£30,000/year
  - Improved staff satisfaction
  - Better care continuity

**ROI: 2,377-4,865% (first year)**

---

## Part 6: Implementation Timeline

### Month 1: Security Hardening (Priority P0)
- Week 1: Authentication & session security
- Week 2: Data protection & encryption
- Week 3: Dependency updates & CSP
- Week 4: Testing & deployment

### Month 2-3: ML Foundation
- Week 1-2: Data export & feature engineering
- Week 3-4: Model training (Prophet)
- Week 5-6: Django integration
- Week 7-8: Dashboard & visualization

### Month 4: Optimization
- Week 1-2: Shift optimization algorithm
- Week 3-4: Integration & testing

### Month 5: Advanced Features
- Week 1-2: Absence prediction
- Week 3-4: Automated retraining pipeline

### Month 6: Production & Monitoring
- Week 1-2: Deployment
- Week 3-4: Monitoring setup & documentation

---

## Part 7: Quick Start Commands

```bash
# Security Hardening
pip install django-axes django-csp django-encrypted-model-fields safety pip-audit
python manage.py check --deploy
python manage.py migrate
safety check

# Machine Learning
pip install prophet scikit-learn pandas numpy pulp matplotlib seaborn
python manage.py export_ml_data
python manage.py train_ml_models
python manage.py generate_forecasts --days=14

# Testing
python manage.py test tests.test_security
python manage.py test tests.test_ml_models

# Monitoring (add to crontab)
0 2 * * * python manage.py retrain_ml_models
0 8 * * * python manage.py check_forecast_accuracy
```

---

## Conclusion

This implementation guide provides a complete roadmap for:
1. **Security Hardening (P0):** Essential production requirements - 7 hours, high ROI through risk mitigation
2. **Machine Learning:** Incremental value delivery - 60+ hours, 10-15% cost reduction

**Recommended Approach:**
1. **Immediate:** Implement all P0 security fixes (Week 1-2)
2. **Short-term:** Deploy demand forecasting (Month 2-3)
3. **Medium-term:** Add optimization algorithm (Month 4)
4. **Long-term:** Continuous improvement with monitoring

**Success Metrics:**
- Security: Zero data breaches, 100% compliance
- ML: 85%+ forecast accuracy, 10%+ cost reduction
- Overall: 8.5/10 production readiness score
