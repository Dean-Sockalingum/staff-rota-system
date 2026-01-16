# Chart.js Integration Guide

## Overview
Chart.js 4.4.1 is now integrated with the design system, providing beautiful, responsive charts with consistent styling.

## Quick Start

### Basic Line Chart
```javascript
// HTML
<canvas id="attendanceChart" width="400" height="200"></canvas>

// JavaScript
const data = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
        label: 'Staff Attendance',
        data: [85, 92, 88, 95, 90, 78, 82]
    }]
};

const chart = ChartHelpers.createLineChart('attendanceChart', data);
```

### Basic Bar Chart
```javascript
const data = {
    labels: ['VG', 'OG', 'MG', 'BG', 'SSCWN'],
    datasets: [{
        label: 'Shifts This Week',
        data: [45, 38, 52, 41, 35]
    }]
};

const chart = ChartHelpers.createBarChart('shiftsChart', data);
```

### Basic Doughnut Chart
```javascript
const data = {
    labels: ['Day Shift', 'Night Shift', 'Twilight'],
    datasets: [{
        data: [120, 85, 45]
    }]
};

const chart = ChartHelpers.createDoughnutChart('shiftTypeChart', data);
```

## ChartHelpers API

### Color Functions

```javascript
// Get color by index (cycles through palette)
ChartHelpers.getColor(0);           // Primary blue
ChartHelpers.getColor(1);           // Secondary green
ChartHelpers.getColor(2);           // Accent orange
ChartHelpers.getColor(0, 0.5);      // Primary blue at 50% opacity

// Get specific brand colors
ChartHelpers.getPrimary();          // #0066FF (default 500 shade)
ChartHelpers.getPrimary(300);       // Lighter blue
ChartHelpers.getPrimary(700, 0.8);  // Darker blue at 80% opacity

ChartHelpers.getSecondary();        // #00C853 (green)
ChartHelpers.getAccent();           // #FF6F00 (orange)

// Get gradient for backgrounds
const ctx = document.getElementById('myChart').getContext('2d');
const gradient = ChartHelpers.getGradient(ctx, '#0066FF', 0.2);
```

### Chart Creation Functions

#### createLineChart(canvasId, data, options)
Creates a line chart with:
- Smooth curved lines (tension: 0.4)
- Gradient fill backgrounds
- White points with colored borders
- Hover effects (larger points)
- Hidden x-axis grid
- Visible y-axis grid

```javascript
const chart = ChartHelpers.createLineChart('myChart', {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
        label: 'Attendance Rate',
        data: [85, 88, 92, 87, 90]
    }]
}, {
    // Additional Chart.js options
    plugins: {
        title: {
            display: true,
            text: 'Monthly Attendance'
        }
    }
});
```

#### createBarChart(canvasId, data, options)
Creates a bar chart with:
- Rounded corners (8px)
- 80% opacity fills
- Solid colored borders
- No x-axis grid
- Visible y-axis grid

```javascript
const chart = ChartHelpers.createBarChart('shiftsChart', {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    datasets: [
        {
            label: 'Day Shifts',
            data: [45, 48, 52, 50]
        },
        {
            label: 'Night Shifts',
            data: [30, 32, 35, 33]
        }
    ]
});
```

#### createDoughnutChart(canvasId, data, options)
Creates a doughnut chart with:
- 70% cutout (donut hole)
- Auto-colored segments
- Legend on right
- Hover offset effect

```javascript
const chart = ChartHelpers.createDoughnutChart('statusChart', {
    labels: ['Active', 'On Leave', 'Inactive'],
    datasets: [{
        data: [650, 45, 15]
    }]
});
```

#### destroyChart(chart)
Safely destroys a chart instance (call before recreating):

```javascript
let myChart = ChartHelpers.createLineChart('chart1', data);

// Later, when updating data:
ChartHelpers.destroyChart(myChart);
myChart = ChartHelpers.createLineChart('chart1', newData);
```

## Advanced Examples

### Multi-Dataset Line Chart
```javascript
const data = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
        {
            label: 'Planned Shifts',
            data: [120, 125, 130, 128, 135, 140],
            borderColor: ChartHelpers.getPrimary()
        },
        {
            label: 'Actual Shifts',
            data: [118, 122, 128, 125, 133, 138],
            borderColor: ChartHelpers.getSecondary()
        },
        {
            label: 'Overtime Shifts',
            data: [8, 12, 15, 10, 18, 20],
            borderColor: ChartHelpers.getAccent()
        }
    ]
};

const chart = ChartHelpers.createLineChart('shiftsComparison', data, {
    plugins: {
        title: {
            display: true,
            text: 'Shift Comparison (6 Months)',
            font: {
                size: 16,
                weight: 600
            }
        }
    },
    scales: {
        y: {
            title: {
                display: true,
                text: 'Number of Shifts'
            }
        }
    }
});
```

### Stacked Bar Chart
```javascript
const data = {
    labels: ['VG', 'OG', 'MG', 'BG', 'SSCWN'],
    datasets: [
        {
            label: 'Day Shift',
            data: [25, 20, 30, 22, 18]
        },
        {
            label: 'Night Shift',
            data: [15, 12, 18, 14, 10]
        },
        {
            label: 'Twilight',
            data: [5, 6, 4, 5, 7]
        }
    ]
};

const chart = ChartHelpers.createBarChart('homeShifts', data, {
    plugins: {
        title: {
            display: true,
            text: 'Shifts by Home & Type'
        }
    },
    scales: {
        x: {
            stacked: true
        },
        y: {
            stacked: true,
            title: {
                display: true,
                text: 'Total Shifts'
            }
        }
    }
});
```

### Dynamic Chart with Skeleton Loading
```javascript
async function loadAttendanceChart() {
    // Show skeleton while loading
    SkeletonLoader.show('#chart-container', 'chart');
    
    try {
        // Fetch data
        const response = await fetch('/api/attendance-stats/');
        const data = await response.json();
        
        // Replace skeleton with chart
        document.getElementById('chart-container').innerHTML = 
            '<canvas id="attendanceChart" height="300"></canvas>';
        
        // Create chart
        const chart = ChartHelpers.createLineChart('attendanceChart', {
            labels: data.labels,
            datasets: [{
                label: 'Attendance Rate (%)',
                data: data.values
            }]
        });
    } catch (error) {
        console.error('Failed to load chart:', error);
        document.getElementById('chart-container').innerHTML = 
            '<div class="alert alert-danger">Failed to load chart</div>';
    }
}

// Load on page ready
document.addEventListener('DOMContentLoaded', loadAttendanceChart);
```

### Responsive Chart with Container
```html
<!-- HTML -->
<div class="card">
    <div class="card-header">
        <h5>Weekly Attendance</h5>
    </div>
    <div class="card-body">
        <div style="position: relative; height: 300px;">
            <canvas id="weeklyChart"></canvas>
        </div>
    </div>
</div>

<script>
// JavaScript
const chart = ChartHelpers.createLineChart('weeklyChart', data);
// Chart automatically resizes with container
</script>
```

## Color Palette

The design system provides these colors for charts:

1. **Primary Blue** (#0066FF) - Main brand color
2. **Secondary Green** (#00C853) - Success, positive metrics
3. **Accent Orange** (#FF6F00) - Warnings, attention items
4. **Info Blue** (#3B82F6) - Informational data
5. **Success Green** (#10B981) - Achievements
6. **Warning Yellow** (#F59E0B) - Caution items
7. **Danger Red** (#EF4444) - Critical issues
8. **Primary Light** (#66A3FF) - Secondary metrics
9. **Secondary Light** (#66DBA3) - Tertiary data
10. **Accent Light** (#FFB766) - Supplementary info

## Default Settings

All charts inherit these defaults:
- **Font**: Inter (matches design system)
- **Font Size**: 14px
- **Animation**: 750ms easeInOutQuart
- **Responsive**: True (resizes with container)
- **Legend**: Bottom position, point style icons
- **Tooltips**: Dark background, rounded corners, custom styling
- **Grid**: Light neutral lines on y-axis only

## Accessibility

- Charts use ARIA labels automatically
- Tooltips provide data on hover
- Legend allows keyboard navigation
- Screen reader compatible
- High contrast colors for visibility

## Performance Tips

1. **Destroy old charts** before creating new ones:
   ```javascript
   ChartHelpers.destroyChart(existingChart);
   newChart = ChartHelpers.createLineChart(...);
   ```

2. **Use skeleton loading** for better perceived performance
3. **Limit datasets** to 3-5 for readability
4. **Sample large datasets** (>100 points) to improve rendering
5. **Use `maintainAspectRatio: false`** for fixed-height containers

## Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Android)

## Documentation
- [Chart.js Official Docs](https://www.chartjs.org/docs/latest/)
- [Chart.js Examples](https://www.chartjs.org/docs/latest/samples/)
- Design system colors: See `design-system.css`
