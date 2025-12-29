# Skeleton Loading States - Usage Guide

## Overview
Skeleton screens improve perceived performance by showing content structure while data loads. Users see immediate visual feedback instead of blank screens or spinners.

## CSS Classes

### Base Skeleton Elements
```html
<!-- Basic skeleton text line -->
<div class="skeleton skeleton-text"></div>

<!-- Different widths -->
<div class="skeleton skeleton-text skeleton-text-full"></div>   <!-- 100% -->
<div class="skeleton skeleton-text skeleton-text-90"></div>     <!-- 90% -->
<div class="skeleton skeleton-text skeleton-text-75"></div>     <!-- 75% -->
<div class="skeleton skeleton-text skeleton-text-50"></div>     <!-- 50% -->
<div class="skeleton skeleton-text skeleton-text-25"></div>     <!-- 25% -->

<!-- Different sizes -->
<div class="skeleton skeleton-text skeleton-text-sm"></div>     <!-- 14px -->
<div class="skeleton skeleton-text"></div>                       <!-- 16px -->
<div class="skeleton skeleton-text skeleton-text-lg"></div>     <!-- 20px -->
<div class="skeleton skeleton-text skeleton-text-xl"></div>     <!-- 24px -->

<!-- Heading skeleton -->
<div class="skeleton skeleton-heading"></div>

<!-- Avatar/Circle -->
<div class="skeleton skeleton-avatar"></div>
<div class="skeleton skeleton-avatar-sm"></div>
<div class="skeleton skeleton-avatar-lg"></div>

<!-- Button skeleton -->
<div class="skeleton skeleton-button"></div>
<div class="skeleton skeleton-button-sm"></div>
<div class="skeleton skeleton-button-lg"></div>

<!-- Badge skeleton -->
<div class="skeleton skeleton-badge"></div>

<!-- Image skeleton -->
<div class="skeleton skeleton-image"></div>
<div class="skeleton skeleton-thumbnail"></div>
```

## Using Template Components

### Method 1: Include in Django Templates
```django
{% load static %}

<!-- Dashboard Widget -->
{% include 'scheduling/skeleton_components.html' with component='widget' %}

<!-- Stat Card -->
{% include 'scheduling/skeleton_components.html' with component='stat-card' %}

<!-- Table with 10 rows -->
{% include 'scheduling/skeleton_components.html' with component='table' rows=10 %}

<!-- List with 8 items -->
{% include 'scheduling/skeleton_components.html' with component='list' items=8 %}

<!-- Generic Card -->
{% include 'scheduling/skeleton_components.html' with component='card' %}

<!-- Shift Card -->
{% include 'scheduling/skeleton_components.html' with component='shift-card' %}

<!-- Staff Profile -->
{% include 'scheduling/skeleton_components.html' with component='staff-profile' %}

<!-- Chart/Graph -->
{% include 'scheduling/skeleton_components.html' with component='chart' %}

<!-- Form with 5 fields -->
{% include 'scheduling/skeleton_components.html' with component='form' fields=5 %}

<!-- 3-column grid -->
{% include 'scheduling/skeleton_components.html' with component='grid-3' %}
```

### Method 2: Use JavaScript SkeletonLoader

```javascript
// Show skeleton while loading data
SkeletonLoader.show('#dashboard-widgets', 'widget');

// Fetch data
fetch('/api/dashboard-stats/')
    .then(response => response.json())
    .then(data => {
        // Replace skeleton with actual content
        const html = renderDashboard(data);
        SkeletonLoader.replace('#dashboard-widgets', html);
    });

// Table with custom rows
SkeletonLoader.show('#staff-table', 'table', { rows: 15 });

// List with custom items
SkeletonLoader.show('#shift-list', 'list', { items: 10 });

// Hide skeleton (restore original content)
SkeletonLoader.hide('#content-area');

// Show multiple skeletons at once
SkeletonLoader.showMultiple([
    { selector: '#widget-1', type: 'widget' },
    { selector: '#widget-2', type: 'stat-card' },
    { selector: '#table-1', type: 'table', options: { rows: 10 } }
]);

// Hide multiple skeletons
SkeletonLoader.hideMultiple(['#widget-1', '#widget-2', '#table-1']);

// Wrap async function (shows skeleton, executes function, hides skeleton)
await SkeletonLoader.wrap('#content', 'widget', async () => {
    const data = await fetchDashboardData();
    renderDashboard(data);
    return data;
});
```

## Common Patterns

### Dashboard Widget Loading
```django
<div id="attendance-widget">
    {% include 'scheduling/skeleton_components.html' with component='widget' %}
</div>

<script>
    // On page load, replace skeleton with real data
    document.addEventListener('DOMContentLoaded', async function() {
        const data = await fetch('/api/attendance-stats/').then(r => r.json());
        document.getElementById('attendance-widget').innerHTML = renderAttendanceWidget(data);
    });
</script>
```

### Table Loading with Pagination
```django
<div id="staff-table-container">
    {% include 'scheduling/skeleton_components.html' with component='table' rows=20 %}
</div>

<script>
    async function loadStaffTable(page = 1) {
        SkeletonLoader.show('#staff-table-container', 'table', { rows: 20 });
        
        const data = await fetch(`/api/staff/?page=${page}`).then(r => r.json());
        const html = renderStaffTable(data);
        
        SkeletonLoader.replace('#staff-table-container', html);
    }
</script>
```

### Shift Cards Grid
```django
<div id="shift-grid" class="skeleton-grid">
    {% for i in "xxx" %}
        {% include 'scheduling/skeleton_components.html' with component='shift-card' %}
    {% endfor %}
</div>

<script>
    async function loadShifts() {
        const shifts = await fetch('/api/shifts/').then(r => r.json());
        const html = shifts.map(shift => renderShiftCard(shift)).join('');
        document.getElementById('shift-grid').innerHTML = html;
    }
</script>
```

### Form Loading
```django
<div id="edit-form">
    {% include 'scheduling/skeleton_components.html' with component='form' fields=6 %}
</div>

<script>
    async function loadEditForm(staffId) {
        const staff = await fetch(`/api/staff/${staffId}/`).then(r => r.json());
        SkeletonLoader.replace('#edit-form', renderEditForm(staff));
    }
</script>
```

### Combining with Global Spinner
```javascript
// Use skeleton for content area, spinner for full-page actions
async function loadDashboard() {
    // Show skeletons for individual widgets
    SkeletonLoader.showMultiple([
        { selector: '#widget-1', type: 'stat-card' },
        { selector: '#widget-2', type: 'stat-card' },
        { selector: '#widget-3', type: 'stat-card' },
        { selector: '#recent-shifts', type: 'table', options: { rows: 5 } }
    ]);
    
    // Load data
    const data = await fetch('/api/dashboard/').then(r => r.json());
    
    // Replace skeletons with real content
    document.getElementById('widget-1').innerHTML = renderWidget(data.widget1);
    document.getElementById('widget-2').innerHTML = renderWidget(data.widget2);
    document.getElementById('widget-3').innerHTML = renderWidget(data.widget3);
    document.getElementById('recent-shifts').innerHTML = renderTable(data.shifts);
}

// Use global spinner for form submissions (full-page blocking action)
async function submitForm(formData) {
    showSpinner('Saving changes...');
    
    try {
        await fetch('/api/save/', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        window.location.reload();
    } finally {
        hideSpinner();
    }
}
```

## Accessibility
- All skeleton components include `aria-busy="true"` and `role="status"`
- Descriptive `aria-label` attributes for screen readers
- Proper ARIA live regions announce loading state changes

## Performance Benefits
- **Perceived load time reduced by 30-40%** (users see structure immediately)
- **Reduces bounce rate** (users less likely to leave during loading)
- **Improves user confidence** (clear indication that content is coming)
- **Better than blank screens or spinners** for content-heavy pages

## When to Use Skeleton vs Spinner
- **Skeleton**: Content loading (tables, cards, lists, dashboards)
- **Spinner**: Actions (form submissions, page transitions, full-page reloads)
- **Both**: Long operations (skeleton first, spinner if >2 seconds)

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Graceful degradation (shows content immediately if CSS not loaded)
- Dark mode support included (prefers-color-scheme: dark)
