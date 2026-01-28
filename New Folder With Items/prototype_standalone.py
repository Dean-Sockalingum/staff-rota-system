#!/usr/bin/env python
"""
Pattern Overview Prototype - STANDALONE VERSION (No Django)
Test concept for 12-week horizontal scrolling view with pure mock data

Usage:
    python prototype_standalone.py
    Then visit: http://127.0.0.1:5000/
"""

from datetime import datetime, timedelta
from flask import Flask, render_template_string

app = Flask(__name__)

# Mock data generation
def generate_mock_data(weeks=12, start_date=None):
    """Generate mock shift pattern data for testing
    
    Args:
        weeks: Number of weeks to generate (default 12)
        start_date: Optional start date. If None, uses current week's Sunday (rolling window)
    """
    
    # Create mock staff
    staff_list = [
        {
            'sap': f'90000{i}',
            'first_name': ['Alex', 'Jamie', 'Morgan', 'Taylor', 'Jordan', 'Casey', 'Riley', 'Drew', 'Sam', 'Quinn'][i],
            'last_name': ['Smith', 'Jones', 'Brown', 'Davis', 'Wilson', 'Miller', 'Moore', 'Taylor', 'Anderson', 'Thomas'][i],
            'role': 'Healthcare Assistant',
            'unit': 'Bluebell',
            'contracted_hours': 37.5
        }
        for i in range(10)
    ]
    
    # Calculate start date (rolling window by default)
    if start_date is None:
        # Get current date and find the Sunday of current week
        today = datetime.now().date()
        # Calculate days since Sunday (0=Monday, 6=Sunday in Python)
        days_since_sunday = (today.weekday() + 1) % 7
        # Get this week's Sunday
        start_date = today - timedelta(days=days_since_sunday)
    
    date_range = [start_date + timedelta(days=i) for i in range(weeks * 7)]
    
    # Create pattern data structure
    pattern_data = {
        'staff': [],
        'dates': date_range,
        'weeks': weeks,
        'start_date': start_date
    }
    
    # Pattern templates (repeating weekly patterns)
    # Pattern 1: 2 shifts per week, Pattern 2: 3 shifts per week
    patterns = [
        # Pattern 1: 2 Day shifts per week (Mon, Thu)
        {'Mon': 'D', 'Tue': '', 'Wed': '', 'Thu': 'D', 'Fri': '', 'Sat': '', 'Sun': ''},
        # Pattern 2: 3 Night shifts per week (Mon, Wed, Fri)
        {'Mon': 'N', 'Tue': '', 'Wed': 'N', 'Thu': '', 'Fri': 'N', 'Sat': '', 'Sun': ''},
    ]
    
    units = ['Bluebell', 'Primrose', 'Daffodil', 'Jasmine', 'Rose']
    
    # Build staff data with patterns
    for idx, staff in enumerate(staff_list):
        sap = staff['sap']
        name = f"{staff['first_name']} {staff['last_name']}"
        role = staff['role']
        unit = staff['unit']
        hours = staff['contracted_hours']
        
        # Select a pattern for this staff member (each gets ONLY D or N, not both)
        # Assign alternating: 0=D, 1=N, 2=D, 3=N, etc.
        pattern = patterns[idx % 2]
        
        # Generate shifts for all dates
        shifts = []
        for date_idx, date in enumerate(date_range):
            day_name = date.strftime('%a')
            
            # Add occasional leave (every 30 days, 1-2 day duration)
            if date_idx % 30 == 0 and date_idx > 0:
                shifts.append({
                    'date': date,
                    'type': 'leave',
                    'leave_type': 'ANNUAL',
                    'unit': None
                })
                continue
            
            # Skip if in leave period
            in_leave = False
            for prev in range(max(0, len(shifts) - 2), len(shifts)):
                if shifts[prev].get('type') == 'leave':
                    in_leave = True
                    break
            
            if in_leave:
                shifts.append({
                    'date': date,
                    'type': 'empty',
                    'unit': None
                })
                continue
            
            # Apply pattern
            shift_code = pattern.get(day_name, '')
            
            if shift_code:
                # Rotate through units every 2 weeks
                week_num = date_idx // 7
                unit_name = units[(idx + week_num // 2) % len(units)]
                
                shifts.append({
                    'date': date,
                    'type': 'shift',
                    'shift_code': shift_code,
                    'unit': unit_name
                })
            else:
                shifts.append({
                    'date': date,
                    'type': 'empty',
                    'unit': None
                })
        
        pattern_data['staff'].append({
            'sap': sap,
            'name': name,
            'role': role,
            'unit': unit,
            'contracted_hours': hours,
            'shifts': shifts
        })
    
    return pattern_data


# HTML Template
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pattern Overview Prototype - {{ data.weeks }} Weeks</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .header .info {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .controls {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .controls button {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            background: #667eea;
            color: white;
            cursor: pointer;
            font-size: 14px;
        }
        
        .controls button:hover {
            background: #5568d3;
        }
        
        .controls select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .pattern-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .pattern-grid {
            display: grid;
            grid-template-columns: 300px 1fr;
            height: calc(100vh - 280px);
            overflow: hidden;
        }
        
        .staff-column {
            background: #f8f9fa;
            border-right: 2px solid #dee2e6;
            overflow-y: auto;
            position: sticky;
            left: 0;
            z-index: 100;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }
        
        .dates-container {
            overflow-x: auto;
            overflow-y: auto;
            scroll-behavior: smooth;
        }
        
        .staff-header {
            background: #495057;
            color: white;
            padding: 8px 12px;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 50;
            display: flex;
            align-items: center;
            min-height: 60px;
            box-sizing: border-box;
        }
        
        .dates-header {
            background: #495057;
            color: white;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 50;
            height: auto;
        }
        
        .dates-header {
            display: flex;
            min-width: fit-content;
            position: sticky;
            top: 0;
            background: #495057;
            z-index: 50;
        }
        
        .day-header {
            min-width: 80px;
            width: 80px;
            flex-shrink: 0;
            text-align: center;
            padding: 8px 4px;
            border-right: 1px solid #6c757d;
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-height: 60px;
            box-sizing: border-box;
        }
        
        .day-header.week-start {
            border-left: 3px solid #ffc107;
            background: #343a40;
        }
        
        .week-label-inline {
            font-size: 9px;
            font-weight: bold;
            color: #ffc107;
            margin-bottom: 4px;
            text-transform: uppercase;
        }
        
        .day-name {
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .day-date {
            font-size: 10px;
            opacity: 0.9;
        }
        
        .staff-row {
            border-bottom: 1px solid #e9ecef;
            font-size: 10px;
            height: 60px;
            max-height: 60px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 0 8px;
            overflow: hidden;
            line-height: 1.2;
        }
        
        .staff-name {
            font-weight: 600;
            color: #2c3e50;
            font-size: 11px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 2px;
        }
        
        .staff-info {
            font-size: 9px;
            color: #6c757d;
            margin: 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.2;
        }
        
        .shifts-row {
            display: flex;
            border-bottom: 1px solid #e9ecef;
            height: 60px;
            align-items: center;
        }
        
        .shift-cell {
            min-width: 80px;
            width: 80px;
            height: 60px;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            border-right: 1px solid #e9ecef;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .shift-cell.week-start {
            border-left: 3px solid #ffc107;
        }
        
        .shift-cell:hover {
            transform: scale(1.05);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            z-index: 10;
        }
        
        .shift-cell.empty {
            background: white;
        }
        
        .shift-cell.leave {
            background: #c8e6c9;
            color: #2e7d32;
        }
        
        .shift-cell.sickness {
            background: #ffccbc;
            color: #d84315;
        }
        
        /* Modal Styles */
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 10% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 500px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }
        
        .modal-header h2 {
            margin: 0;
            color: #495057;
        }
        
        .close {
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #000;
        }
        
        .modal-body {
            margin: 20px 0;
        }
        
        .modal-option {
            padding: 15px;
            margin: 10px 0;
            border: 2px solid #e9ecef;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .modal-option:hover {
            background: #f8f9fa;
            border-color: #667eea;
        }
        
        .modal-option h3 {
            margin: 0 0 5px 0;
            color: #495057;
        }
        
        .modal-option p {
            margin: 0;
            color: #6c757d;
            font-size: 14px;
        }
        
        /* Unit colors (cycling) */
        .unit-bluebell { background: #e3f2fd; color: #1565c0; }
        .unit-primrose { background: #fff9c4; color: #f57f17; }
        .unit-daffodil { background: #fff3e0; color: #e65100; }
        .unit-jasmine { background: #f3e5f5; color: #6a1b9a; }
        .unit-rose { background: #fce4ec; color: #c2185b; }
        
        .week-boundary {
            border-left: 2px solid #495057;
        }
        
        .legend {
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #dee2e6;
            display: flex;
            gap: 20px;
            font-size: 12px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-box {
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }
        
        .scroll-indicator {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 12px;
            display: none;
        }
        
        .stats {
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .stat-card {
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 12px;
            opacity: 0.9;
        }
        
        /* Print Styles */
        @media print {
            body { background: white; }
            .controls, .legend, .stats { display: none !important; }
            .pattern-container { overflow: visible !important; }
            .dates-container { overflow: visible !important; }
            .staff-header, .dates-header { position: static !important; }
            .shift-cell, .staff-row { page-break-inside: avoid; }
        }
        
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔬 Pattern Overview Prototype (Standalone)</h1>
        <div class="info">
            Extended {{ data.weeks }}-week horizontal scrolling view with mock data
            <br>
            Testing: Sticky columns, smooth scrolling, performance with {{ data.dates|length }} days × {{ data.staff|length }} staff = {{ data.dates|length * data.staff|length }} cells
        </div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{{ data.weeks }}</div>
            <div class="stat-label">Weeks Displayed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ data.dates|length }}</div>
            <div class="stat-label">Total Days</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ data.staff|length }}</div>
            <div class="stat-label">Staff Members</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{{ data.dates|length * data.staff|length }}</div>
            <div class="stat-label">Total Cells Rendered</div>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="scrollToToday()">📅 Today</button>
        <button onclick="scrollToWeek('prev')">⬅️ Previous Week</button>
        <button onclick="scrollToWeek('next')">➡️ Next Week</button>
        <select onchange="jumpToWeek(this.value)">
            <option value="">Jump to Week...</option>
            {% for week_num in range(1, data.weeks + 1) %}
            <option value="{{ week_num }}">Week {{ week_num }}</option>
            {% endfor %}
        </select>
        <span style="margin: 0 15px; color: #6c757d;">|</span>
        <label for="startDate" style="font-size: 14px; color: #495057;">Start Date:</label>
        <input type="date" id="startDate" value="{{ data.start_date.strftime('%Y-%m-%d') }}" 
               onchange="changeStartDate(this.value)" 
               style="margin-left: 5px; padding: 5px 10px; border: 1px solid #ced4da; border-radius: 4px;">
        <button onclick="resetToCurrentWeek()" style="margin-left: 5px;">🔄 Current Week</button>
        <span style="margin: 0 15px; color: #6c757d;">|</span>
        <select id="shiftFilter" onchange="filterShifts(this.value)" style="margin-left: 5px;">
            <option value="all">All Shifts</option>
            <option value="D">Days Only</option>
            <option value="N">Nights Only</option>
        </select>
        <button onclick="printDailyAllocation()" style="margin-left: 10px;">🖨️ Print Daily Allocation</button>
        <span style="margin-left: auto; color: #6c757d; font-size: 14px;">
            Scroll Performance: <span id="fps">60</span> FPS
        </span>
    </div>
    
    <div class="pattern-container">
        <div class="pattern-grid">
            <!-- Sticky Staff Column -->
            <div class="staff-column">
                <div class="staff-header">
                    Staff Information
                </div>
                {% for staff in data.staff %}
                <div class="staff-row">
                    <div class="staff-name">{{ staff.name }}</div>
                    <div class="staff-info">{{ staff.sap }} | {{ staff.role }} | {{ staff.unit }}</div>
                </div>
                {% endfor %}
            </div>
            
            <!-- Scrollable Dates Column -->
            <div class="dates-container" id="datesContainer">
                <!-- Date Headers -->
                <div class="dates-header">
                    {% for date in data.dates %}
                        {% set week_num = (loop.index0 // 7) + 1 %}
                        {% set is_sunday = date.weekday() == 6 %}
                        {% set week_end_date = date + timedelta(days=6) %}
                        
                        <div class="day-header {% if is_sunday %}week-start{% endif %}">
                            {% if is_sunday %}
                                <div class="week-label-inline">Week {{ week_num }}</div>
                            {% endif %}
                            <span class="day-name">{{ date.strftime('%a') }}</span>
                            <span class="day-date">{{ date.strftime('%d %b') }}</span>
                        </div>
                    {% endfor %}
                </div>
                
                <!-- Shifts Grid -->
                {% for staff in data.staff %}
                <div class="shifts-row">
                    {% for shift in staff.shifts %}
                        {% set is_sunday = data.dates[loop.index0].weekday() == 6 %}
                        {% set week_class = 'week-start' if is_sunday else '' %}
                        
                        {% if shift.type == 'leave' %}
                            <div class="shift-cell leave {{ week_class }}" title="Annual Leave - {{ shift.date.strftime('%d %b %Y') }}">
                                A/L
                            </div>
                        {% elif shift.type == 'shift' %}
                            <div class="shift-cell shift unit-{{ shift.unit|lower }} {{ week_class }}" 
                                 onclick="openShiftModal('{{ staff.name }}', '{{ shift.date.strftime('%d %b %Y') }}', '{{ shift.shift_code }}', '{{ shift.unit }}', {{ loop.index0 }}, {{ loop.parent.loop.index0 }})"
                                 title="{{ shift.unit }} - {{ shift.shift_code }} - {{ shift.date.strftime('%d %b %Y') }} - Click to edit">
                                {{ shift.shift_code }}
                            </div>
                        {% else %}
                            <div class="shift-cell empty {{ week_class }}"></div>
                        {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-box unit-bluebell"></div>
                <span>Bluebell</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-primrose"></div>
                <span>Primrose</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-daffodil"></div>
                <span>Daffodil</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-jasmine"></div>
                <span>Jasmine</span>
            </div>
            <div class="legend-item">
                <div class="legend-box unit-rose"></div>
                <span>Rose</span>
            </div>
            <div class="legend-item">
                <div class="legend-box leave"></div>
                <span>Annual Leave</span>
            </div>
            <div class="legend-item">
                <div class="legend-box" style="background: #ffccbc;"></div>
                <span>Sickness</span>
            </div>
            <div class="legend-item">
                <span style="margin-left: auto; color: #6c757d; font-weight: bold;">D = Days (07:45-20:00) | N = Nights (19:45-08:00)</span>
            </div>
        </div>
    </div>
    
    <!-- Shift Edit Modal -->
    <div id="shiftModal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2>Edit Shift</h2>
                <span class="close" onclick="closeShiftModal()">&times;</span>
            </div>
            <div class="modal-body">
                <div id="modalStaffInfo" style="margin-bottom: 20px; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                    <strong id="modalStaffName"></strong><br>
                    <span id="modalShiftDate" style="color: #6c757d;"></span>
                </div>
                
                <div class="modal-option" onclick="changeToAnnualLeave()">
                    <h3>🌴 Annual Leave</h3>
                    <p>Convert this shift to annual leave</p>
                </div>
                
                <div class="modal-option" onclick="changeToSickness()">
                    <h3>🩹 Sickness</h3>
                    <p>Mark this shift as sickness absence</p>
                </div>
                
                <div class="modal-option">
                    <h3>🏥 Change Unit</h3>
                    <p>Assign to a different unit</p>
                    <select id="unitSelector" style="width: 100%; padding: 8px; margin-top: 10px; border: 1px solid #ced4da; border-radius: 4px;" onchange="changeUnit(this.value)">
                        <option value="">Select unit...</option>
                        <option value="Bluebell">Bluebell</option>
                        <option value="Primrose">Primrose</option>
                        <option value="Daffodil">Daffodil</option>
                        <option value="Jasmine">Jasmine</option>
                        <option value="Rose">Rose</option>
                    </select>
                </div>
            </div>
        </div>
    </div>
    
    <div class="scroll-indicator" id="scrollIndicator">
        Scrolling...
    </div>
    
    <script>
        const container = document.getElementById('datesContainer');
        const scrollIndicator = document.getElementById('scrollIndicator');
        let scrollTimeout;
        let lastScrollTime = Date.now();
        let frameCount = 0;
        
        // Show/hide scroll indicator
        container.addEventListener('scroll', () => {
            scrollIndicator.style.display = 'block';
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                scrollIndicator.style.display = 'none';
            }, 1000);
            
            // Update FPS counter
            frameCount++;
            const now = Date.now();
            if (now - lastScrollTime >= 1000) {
                document.getElementById('fps').textContent = frameCount;
                frameCount = 0;
                lastScrollTime = now;
            }
        });
        
        // Scroll to today (first day in prototype)
        function scrollToToday() {
            container.scrollLeft = 0;
        }
        
        // Scroll by week
        function scrollToWeek(direction) {
            const dayWidth = 80; // px (updated from 60)
            const weekWidth = dayWidth * 7;
            if (direction === 'prev') {
                container.scrollLeft -= weekWidth;
            } else {
                container.scrollLeft += weekWidth;
            }
        }
        
        // Jump to specific week
        function jumpToWeek(weekNum) {
            if (!weekNum) return;
            const dayWidth = 80; // px (updated from 60)
            const targetScroll = (weekNum - 1) * 7 * dayWidth;
            container.scrollTo({
                left: targetScroll,
                behavior: 'smooth'
            });
        }
        
        // Filter shifts by type (Days/Nights)
        function filterShifts(filterType) {
            const allRows = document.querySelectorAll('.shifts-row');
            const allStaffRows = document.querySelectorAll('.staff-row');
            
            allRows.forEach((row, index) => {
                const staffRow = allStaffRows[index];
                const shiftCells = row.querySelectorAll('.shift-cell.shift');
                
                // Check if this staff member has the filtered shift type
                let hasFilteredShift = false;
                shiftCells.forEach(cell => {
                    const shiftCode = cell.textContent.trim();
                    if (filterType === 'all' || shiftCode === filterType) {
                        hasFilteredShift = true;
                    }
                });
                
                // Show/hide staff row and shift row based on filter
                if (filterType === 'all' || hasFilteredShift) {
                    row.classList.remove('hidden');
                    staffRow.classList.remove('hidden');
                } else {
                    row.classList.add('hidden');
                    staffRow.classList.add('hidden');
                }
            });
        }
        
        // Print daily allocation sheet
        function printDailyAllocation() {
            const today = new Date();
            const dateStr = today.toLocaleDateString('en-GB', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            
            // Create print window
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Daily Allocation Sheet - ${dateStr}</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        h1 { text-align: center; margin-bottom: 30px; }
                        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                        th, td { border: 1px solid #333; padding: 10px; text-align: left; }
                        th { background: #667eea; color: white; }
                        .unit-bluebell { background: #e3f2fd; }
                        .unit-primrose { background: #fff9c4; }
                        .unit-daffodil { background: #fff3e0; }
                        .unit-jasmine { background: #f3e5f5; }
                        .unit-rose { background: #fce4ec; }
                        .shift-D { font-weight: bold; color: #1565c0; }
                        .shift-N { font-weight: bold; color: #6a1b9a; }
                    </style>
                </head>
                <body>
                    <h1>Daily Staff Allocation Sheet</h1>
                    <p><strong>Date:</strong> ${dateStr}</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Staff Name</th>
                                <th>SAP</th>
                                <th>Role</th>
                                <th>Shift Type</th>
                                <th>Unit Assignment</th>
                            </tr>
                        </thead>
                        <tbody>
            `);
            
            // Get all staff and their current shifts
            const staffRows = document.querySelectorAll('.staff-row');
            const shiftRows = document.querySelectorAll('.shifts-row');
            
            staffRows.forEach((staffRow, index) => {
                if (staffRow.classList.contains('hidden')) return;
                
                const name = staffRow.querySelector('.staff-name').textContent;
                const info = staffRow.querySelector('.staff-info').textContent;
                const [sap, role, unit] = info.split(' | ');
                
                // Find today's shift (just use first shift as example for demo)
                const shiftCells = shiftRows[index].querySelectorAll('.shift-cell.shift');
                if (shiftCells.length > 0) {
                    const firstShift = shiftCells[0];
                    const shiftType = firstShift.textContent.trim();
                    const shiftUnit = firstShift.title.split(' - ')[0];
                    const shiftTimes = shiftType === 'D' ? '07:45-20:00' : '19:45-08:00';
                    
                    printWindow.document.write(`
                        <tr>
                            <td>${name}</td>
                            <td>${sap}</td>
                            <td>${role}</td>
                            <td class="shift-${shiftType}">${shiftType === 'D' ? 'Days' : 'Nights'} (${shiftTimes})</td>
                            <td>${shiftUnit}</td>
                        </tr>
                    `);
                }
            });
            
            printWindow.document.write(`
                        </tbody>
                    </table>
                    <p style="margin-top: 30px; font-size: 12px; color: #666;">
                        <strong>Legend:</strong> D = Days (07:45-20:00) | N = Nights (19:45-08:00)
                    </p>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            printWindow.focus();
            
            // Wait for content to load, then print
            setTimeout(() => {
                printWindow.print();
            }, 250);
        }
        
        // Change start date and reload
        function changeStartDate(dateStr) {
            if (dateStr) {
                // Parse the date
                const selectedDate = new Date(dateStr + 'T00:00:00');
                
                // Find the Sunday of that week
                const dayOfWeek = selectedDate.getDay(); // 0=Sunday, 1=Monday, etc.
                const sunday = new Date(selectedDate);
                sunday.setDate(selectedDate.getDate() - dayOfWeek);
                
                // Format as YYYY-MM-DD
                const year = sunday.getFullYear();
                const month = String(sunday.getMonth() + 1).padStart(2, '0');
                const day = String(sunday.getDate()).padStart(2, '0');
                const sundayStr = `${year}-${month}-${day}`;
                
                // Reload with custom start date parameter
                window.location.href = `?start=${sundayStr}`;
            }
        }
        
        // Reset to current week (rolling window)
        function resetToCurrentWeek() {
            // Remove start parameter to use default rolling window
            window.location.href = window.location.pathname;
        }
        
        // Shift editing variables
        let currentEditingCell = null;
        let currentStaffIndex = null;
        let currentShiftIndex = null;
        
        // Open shift edit modal
        function openShiftModal(staffName, shiftDate, shiftCode, unit, shiftIndex, staffIndex) {
            currentStaffIndex = staffIndex;
            currentShiftIndex = shiftIndex;
            
            // Find and store the cell reference
            const rows = document.querySelectorAll('.shifts-row');
            const row = rows[staffIndex];
            const cells = row.querySelectorAll('.shift-cell');
            currentEditingCell = cells[shiftIndex];
            
            // Populate modal
            document.getElementById('modalStaffName').textContent = staffName;
            document.getElementById('modalShiftDate').textContent = shiftDate + ' - ' + shiftCode + ' shift';
            document.getElementById('unitSelector').value = unit;
            
            // Show modal
            document.getElementById('shiftModal').style.display = 'block';
        }
        
        // Close modal
        function closeShiftModal() {
            document.getElementById('shiftModal').style.display = 'none';
            currentEditingCell = null;
            currentStaffIndex = null;
            currentShiftIndex = null;
        }
        
        // Close modal when clicking outside
        window.onclick = function(event) {
            const modal = document.getElementById('shiftModal');
            if (event.target == modal) {
                closeShiftModal();
            }
        }
        
        // Change to annual leave
        function changeToAnnualLeave() {
            if (currentEditingCell) {
                currentEditingCell.className = 'shift-cell leave';
                if (currentEditingCell.classList.contains('week-start')) {
                    currentEditingCell.classList.add('week-start');
                }
                currentEditingCell.textContent = 'A/L';
                currentEditingCell.title = 'Annual Leave';
                currentEditingCell.onclick = null; // Remove click handler for leave
            }
            closeShiftModal();
        }
        
        // Change to sickness
        function changeToSickness() {
            if (currentEditingCell) {
                currentEditingCell.className = 'shift-cell sickness';
                if (currentEditingCell.classList.contains('week-start')) {
                    currentEditingCell.classList.add('week-start');
                }
                currentEditingCell.textContent = 'SICK';
                currentEditingCell.title = 'Sickness Absence';
                currentEditingCell.onclick = null; // Remove click handler for sickness
            }
            closeShiftModal();
        }
        
        // Change unit
        function changeUnit(newUnit) {
            if (currentEditingCell && newUnit) {
                // Remove old unit class
                currentEditingCell.classList.forEach(cls => {
                    if (cls.startsWith('unit-')) {
                        currentEditingCell.classList.remove(cls);
                    }
                });
                
                // Add new unit class
                currentEditingCell.classList.add('unit-' + newUnit.toLowerCase());
                
                // Update title
                const shiftCode = currentEditingCell.textContent.trim();
                const dateMatch = currentEditingCell.title.match(/\\d{2} \\w{3} \\d{4}/);
                const date = dateMatch ? dateMatch[0] : '';
                currentEditingCell.title = newUnit + ' - ' + shiftCode + ' - ' + date + ' - Click to edit';
                
                // Close modal
                closeShiftModal();
            }
        }
        
        // Performance monitoring
        console.log('Pattern Overview Prototype Loaded');
        console.log('Total cells:', {{ data.dates|length * data.staff|length }});
        console.log('Weeks:', {{ data.weeks }});
        console.log('Days:', {{ data.dates|length }});
        console.log('Staff:', {{ data.staff|length }});
        
        // Measure initial render time
        window.addEventListener('load', () => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render prototype with 12 weeks (rolling window by default)"""
    from datetime import timedelta as td
    from flask import request
    
    # Check if custom start date provided
    start_param = request.args.get('start')
    start_date = None
    
    if start_param:
        try:
            # Parse YYYY-MM-DD format
            start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
        except ValueError:
            pass  # Invalid date, use default rolling window
    
    data = generate_mock_data(weeks=12, start_date=start_date)
    return render_template_string(TEMPLATE, data=data, timedelta=td)

@app.route('/<int:weeks>')
def custom_weeks(weeks):
    """Render prototype with custom week count"""
    from datetime import timedelta as td
    from flask import request
    
    weeks = min(max(weeks, 3), 52)  # Clamp between 3 and 52
    
    # Check if custom start date provided
    start_param = request.args.get('start')
    start_date = None
    
    if start_param:
        try:
            start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    data = generate_mock_data(weeks=weeks, start_date=start_date)
    
    # Add warning for large week counts
    if weeks > 26:
        print(f"⚠️  WARNING: Rendering {weeks} weeks ({weeks * 7} days) may be slow!")
        print(f"   Total cells: {weeks * 7 * 10} - Consider using 12-26 weeks for better performance")
    
    return render_template_string(TEMPLATE, data=data, timedelta=td)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔬 PATTERN OVERVIEW PROTOTYPE SERVER (STANDALONE)")
    print("="*60)
    print("\n📍 Access the prototype at:")
    print("   http://127.0.0.1:5001/        - 12 weeks (default)")
    print("   http://127.0.0.1:5001/4       - 4 weeks")
    print("   http://127.0.0.1:5001/26      - 26 weeks (6 months)")
    print("   http://127.0.0.1:5001/52      - 52 weeks (1 year)")
    print("\n✨ Features to test:")
    print("   - Sticky staff column (stays visible while scrolling)")
    print("   - Smooth horizontal scrolling")
    print("   - Navigation buttons (Today, Prev Week, Next Week)")
    print("   - Week selector dropdown")
    print("   - FPS counter (scroll performance)")
    print("   - Hover effects on shift cells")
    print("   - Week boundaries (darker vertical lines)")
    print("\n⚙️  Mock data: 10 staff, 5 patterns, rotating units, annual leave")
    print("🔓 NO Django/AXES - Pure Flask on port 5001")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=False, port=5001, use_reloader=False, host='127.0.0.1')
