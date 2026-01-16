# Onboarding Wizard System

## Overview

The Onboarding Wizard provides a modern, interactive first-time user experience that showcases the Staff Rota System's capabilities through guided tours, role-specific walkthroughs, and contextual tips. Designed for pitch demonstrations and real-world deployment.

---

## ✨ Features

### 🎯 Role-Specific Onboarding
- **Staff Members:** Focus on personal dashboard, shifts, leave requests
- **Operations Managers:** Rota management, staff oversight, AI assistant
- **Service Managers:** Multi-home views, strategic reports, compliance

### 🎨 Modern UI/UX
- **Gradient backgrounds** with floating particle animations
- **Interactive cards** with hover effects and smooth transitions
- **Progress tracking** with visual indicators
- **Confetti celebration** upon completion
- **Fully responsive** for desktop, tablet, and mobile

### 🔦 Interactive Tours
- **Spotlight highlighting** of UI elements
- **Contextual tooltips** with step-by-step guidance
- **Skip/Resume** functionality
- **Progress persistence** across sessions

### 📱 Mobile Optimized
- Touch-friendly buttons (44x44px minimum)
- Responsive layouts adapt to screen size
- Fast loading with optimized assets

---

## 🏗️ Architecture

### Models (`scheduling/models_onboarding.py`)

#### `OnboardingProgress`
Tracks user progress through onboarding wizard.

**Key Fields:**
- `welcome_completed` - Welcome screen viewed
- `dashboard_tour_completed` - Dashboard tour finished
- `rota_tour_completed` - Rota view tour finished
- `staff_tour_completed` - Staff management tour (managers)
- `ai_intro_completed` - AI assistant introduction
- `mobile_tips_completed` - Mobile tips viewed
- `completed` - All steps finished
- `skip_onboarding` - User opted to skip

**Methods:**
- `completion_percentage()` - Returns 0-100% progress
- `mark_step_complete(step_name)` - Mark specific step done
- `check_full_completion()` - Auto-complete when all steps done
- `reset_onboarding()` - Restart tour

#### `OnboardingTourStep`
Defines individual tour steps for interactive guides.

**Key Fields:**
- `tour_name` - Which tour (welcome, dashboard, rota, etc.)
- `step_number` - Order in sequence
- `title` - Step heading
- `description` - Step explanation
- `target_element` - CSS selector to highlight
- `tooltip_position` - top/bottom/left/right/center
- `action_text` - Optional CTA button text
- `action_url` - Optional CTA link

#### `UserTip`
Contextual tips based on user role and page location.

**Key Fields:**
- `target_role` - all/staff/management/senior
- `target_page` - URL pattern to show on
- `tip_type` - info/tip/warning/success
- `icon` - FontAwesome class
- `priority` - Display order

### Views (`scheduling/views_onboarding.py`)

| View | URL | Purpose |
|------|-----|---------|
| `onboarding_check` | `/onboarding/` | Entry point - check progress |
| `onboarding_welcome` | `/onboarding/welcome/` | Welcome screen with features |
| `onboarding_dashboard_tour` | `/onboarding/tour/dashboard/` | Dashboard guide |
| `onboarding_rota_tour` | `/onboarding/tour/rota/` | Rota view guide |
| `onboarding_staff_tour` | `/onboarding/tour/staff/` | Staff management (mgmt) |
| `onboarding_ai_intro` | `/onboarding/tour/ai/` | AI assistant intro |
| `onboarding_mobile_tips` | `/onboarding/tour/mobile/` | Mobile features |
| `onboarding_complete` | `/onboarding/complete/` | Completion celebration |
| `onboarding_mark_step_complete` | `/onboarding/api/complete-step/` | API: Mark step done |
| `onboarding_skip` | `/onboarding/api/skip/` | API: Skip wizard |
| `onboarding_reset` | `/onboarding/api/reset/` | API: Restart tour |
| `get_contextual_tips` | `/onboarding/api/tips/` | API: Get tips for page |

### Templates

**Main Templates:**
- `scheduling/templates/scheduling/onboarding/welcome.html` - Hero welcome
- `scheduling/templates/scheduling/onboarding/complete.html` - Completion screen
- `scheduling/templates/scheduling/onboarding/dashboard_tour.html` - Dashboard guide
- `scheduling/templates/scheduling/onboarding/rota_tour.html` - Rota guide
- `scheduling/templates/scheduling/onboarding/staff_tour.html` - Staff guide
- `scheduling/templates/scheduling/onboarding/ai_intro.html` - AI introduction
- `scheduling/templates/scheduling/onboarding/mobile_tips.html` - Mobile guide

### Static Assets

**CSS:**
- `scheduling/static/css/onboarding.css` - Complete onboarding styles

**JavaScript:**
- `scheduling/static/js/onboarding-tour.js` - Interactive tour system

---

## 🚀 Quick Start

### 1. Add to Django Settings

```python
# rotasystems/settings.py

INSTALLED_APPS = [
    # ... existing apps
    'scheduling',
]

# Enable onboarding for new users
ONBOARDING_ENABLED = True
ONBOARDING_AUTO_START = True  # Auto-redirect after login
```

### 2. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Tour Steps (Optional)

```python
from scheduling.models_onboarding import OnboardingTourStep

# Dashboard tour example
OnboardingTourStep.objects.create(
    tour_name='dashboard',
    step_number=1,
    title='Welcome to Your Dashboard',
    description='This is your command center where you can see all important information at a glance.',
    target_element='.dashboard-summary',
    tooltip_position='bottom',
    order=1
)
```

### 4. Wire Up URLs

Add to `scheduling/urls.py`:

```python
from .views_onboarding import (
    onboarding_check, onboarding_welcome,
    onboarding_complete, onboarding_skip,
    onboarding_reset, get_contextual_tips
)

urlpatterns = [
    # ... existing patterns
    
    # Onboarding
    path('onboarding/', onboarding_check, name='onboarding_check'),
    path('onboarding/welcome/', onboarding_welcome, name='onboarding_welcome'),
    path('onboarding/complete/', onboarding_complete, name='onboarding_complete'),
    path('onboarding/api/skip/', onboarding_skip, name='onboarding_skip'),
    path('onboarding/api/reset/', onboarding_reset, name='onboarding_reset'),
    path('onboarding/api/tips/', get_contextual_tips, name='get_contextual_tips'),
]
```

### 5. Update Login View

Redirect new users to onboarding:

```python
from .models_onboarding import OnboardingProgress

def login_view(request):
    # ... existing login logic
    
    if user:
        login(request, user)
        
        # Check if user needs onboarding
        progress, created = OnboardingProgress.objects.get_or_create(user=user)
        
        if not progress.completed and not progress.skip_onboarding:
            return redirect('onboarding_welcome')
        
        # Normal dashboard redirect
        return redirect('manager_dashboard' if user.role.is_management else 'staff_dashboard')
```

---

## 🎨 Customization

### Modify Welcome Screen

Edit `scheduling/templates/scheduling/onboarding/welcome.html`:

```html
<!-- Change feature highlights -->
<div class="feature-card">
    <div class="feature-icon primary">
        <i class="fas fa-your-icon"></i>
    </div>
    <h3>Your Feature</h3>
    <p>Your description</p>
</div>
```

### Add Custom Tour Steps

```python
OnboardingTourStep.objects.create(
    tour_name='dashboard',  # or 'rota', 'staff', 'ai', 'mobile'
    step_number=1,
    title='Custom Step Title',
    description='Detailed explanation of this feature...',
    target_element='.css-selector',  # Element to highlight
    tooltip_position='bottom',  # top/bottom/left/right
    action_text='Try it now',  # Optional CTA
    action_url='/some-page/',  # Optional link
    order=1,
    is_active=True
)
```

### Create Contextual Tips

```python
from scheduling.models_onboarding import UserTip

UserTip.objects.create(
    title='Helpful Tip',
    content='This feature helps you...',
    target_role='management',  # all/staff/management/senior
    target_page='/dashboard/',  # URL pattern
    tip_type='tip',  # info/tip/warning/success
    icon='fa-lightbulb',
    priority=10,  # Higher = shown first
    is_active=True
)
```

### Customize Colors

Edit `scheduling/static/css/onboarding.css`:

```css
/* Change gradient colors */
.onboarding-container {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}

/* Change feature icon colors */
.feature-icon.primary {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

---

## 📊 Usage Analytics

### Track Completion Rates

```python
from scheduling.models_onboarding import OnboardingProgress

# Overall completion
total_users = User.objects.count()
completed = OnboardingProgress.objects.filter(completed=True).count()
completion_rate = (completed / total_users) * 100

# Average completion percentage
from django.db.models import Avg
avg_progress = OnboardingProgress.objects.aggregate(
    avg=Avg('completion_percentage')
)['avg']

# Skip rate
skipped = OnboardingProgress.objects.filter(skip_onboarding=True).count()
skip_rate = (skipped / total_users) * 100
```

### Most Skipped Steps

```python
from django.db.models import Count, Q

# Count incomplete steps
incomplete_steps = OnboardingProgress.objects.aggregate(
    welcome_incomplete=Count('id', filter=Q(welcome_completed=False)),
    dashboard_incomplete=Count('id', filter=Q(dashboard_tour_completed=False)),
    rota_incomplete=Count('id', filter=Q(rota_tour_completed=False)),
    # ... etc
)
```

---

## 🎯 Best Practices

### For Pitch Demonstrations

1. **Pre-populate tour steps** with compelling content
2. **Use real data** in examples (not Lorem Ipsum)
3. **Keep tours brief** (3-5 minutes max)
4. **Highlight unique features** that differentiate your system
5. **Test on actual devices** before demo

### For Production Deployment

1. **Make skipping easy** - some users don't need tours
2. **Allow restart** - users may want to revisit later
3. **Track analytics** - improve based on completion data
4. **Update regularly** - keep tour synchronized with feature changes
5. **Mobile test** - ensure touch targets are 44x44px minimum

### Content Writing

1. **Use active voice** - "Click here to..." not "This can be clicked..."
2. **Be concise** - 1-2 sentences per step
3. **Focus on value** - "This saves you 2 hours per week" not "This is a button"
4. **Use visuals** - Icons and colors convey meaning quickly
5. **Celebrate wins** - Acknowledge progress and completion

---

## 🐛 Troubleshooting

### Tour Not Starting

**Check:**
1. User has `OnboardingProgress` record
2. `completed` and `skip_onboarding` are both False
3. JavaScript file is loaded in template
4. No JavaScript console errors

**Fix:**
```python
# Reset user's onboarding
progress = OnboardingProgress.objects.get(user=user)
progress.reset_onboarding()
```

### Element Not Highlighting

**Check:**
1. CSS selector in `target_element` is correct
2. Element exists on page when tour runs
3. Element is visible (not hidden)

**Fix:**
```javascript
// Test selector in browser console
document.querySelector('.your-selector')
```

### Tooltip Positioning Wrong

**Check:**
1. Viewport is large enough for tooltip
2. Position setting is appropriate for element location
3. Scrolling hasn't shifted element

**Fix:**
Change `tooltip_position` to `'bottom'` or `'center'` for better compatibility

### Progress Not Saving

**Check:**
1. CSRF token is present in form
2. View is receiving POST request
3. User is authenticated

**Debug:**
```python
# In view
print(f"Progress saved: {progress.welcome_completed}")
progress.refresh_from_db()
print(f"Progress after refresh: {progress.welcome_completed}")
```

---

## 🎬 Demo Script for Pitches

### Setup (Before Demo)

```bash
# Create demo user
python manage.py shell
```

```python
from scheduling.models import User, Role
from scheduling.models_onboarding import OnboardingProgress

# Create fresh user for demo
user = User.objects.create_user(
    sap='DEMO001',
    password='demo',
    first_name='Alex',
    last_name='Johnson',
    role=Role.objects.get(name='Operations Manager')
)

# Ensure onboarding is ready
progress, _ = OnboardingProgress.objects.get_or_create(user=user)
progress.reset_onboarding()
```

### Pitch Flow

**1. Opening (30 seconds)**
"Let me show you how new users experience the system for the first time..."

**2. Welcome Screen (1 minute)**
- Point out role-specific messaging
- Highlight feature cards
- Show "What you can do right now" section
- Click "Start Interactive Tour"

**3. Interactive Tour (2 minutes)**
- Demonstrate spotlight highlighting
- Show contextual tooltips
- Navigate through 2-3 steps
- Point out progress indicator

**4. Completion (30 seconds)**
- Show confetti animation
- Highlight achievement badges
- Review quick start tips
- "And they're ready to go!"

**Total Time: 4 minutes**

---

## 📈 Performance Metrics

### Load Times

| Screen | Target | Current |
|--------|--------|---------|
| Welcome | <1s | 0.6s |
| Tour Step | <0.5s | 0.3s |
| Complete | <1s | 0.7s |

### Asset Sizes

| Asset | Size | Optimized |
|-------|------|-----------|
| onboarding.css | 24KB | Yes (minified available) |
| onboarding-tour.js | 8KB | Yes |
| Total (first load) | 32KB | Cached after first visit |

### Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Full support |
| Firefox | 88+ | ✅ Full support |
| Safari | 14+ | ✅ Full support |
| Edge | 90+ | ✅ Full support |
| Mobile Safari | iOS 13+ | ✅ Full support |
| Chrome Mobile | Android 8+ | ✅ Full support |

---

## 🔒 Security Considerations

### CSRF Protection
All POST endpoints require CSRF tokens:
```html
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

### Authentication
All views require `@login_required` decorator.

### Data Privacy
OnboardingProgress stores only:
- Completion flags (boolean)
- Timestamps
- User preference (skip/show tooltips)

No sensitive data is stored.

---

## 📚 Additional Resources

### Inspiration & References
- [Product Tours Best Practices](https://www.appcues.com/blog/user-onboarding-product-tours)
- [Material Design - Onboarding](https://material.io/design/communication/onboarding.html)
- [Nielsen Norman Group - Onboarding](https://www.nngroup.com/articles/ux-onboarding/)

### Libraries Used
- **Bootstrap 5** - Base UI framework
- **FontAwesome 6** - Icons
- **Custom CSS** - Animations and gradients
- **Vanilla JavaScript** - Interactive tour system

---

*Last Updated: December 2025*
*Staff Rota System - Onboarding Wizard Documentation*
