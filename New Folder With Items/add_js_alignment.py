import re

template_path = '/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/rota_view.html'

with open(template_path, 'r') as f:
    content = f.read()

# JavaScript to add right before </body>
alignment_js = '''<script>
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const calendarDays = document.querySelectorAll('.calendar-day');
        let maxManagementHeight = 0;
        let maxSscwHeight = 0;
        
        calendarDays.forEach(day => {
            const mgmtSection = day.querySelector('.management-section');
            const sscwSection = day.querySelector('.duty-sscw-section');
            if (mgmtSection) maxManagementHeight = Math.max(maxManagementHeight, mgmtSection.scrollHeight);
            if (sscwSection) maxSscwHeight = Math.max(maxSscwHeight, sscwSection.scrollHeight);
        });
        
        calendarDays.forEach(day => {
            const mgmtSection = day.querySelector('.management-section');
            const sscwSection = day.querySelector('.duty-sscw-section');
            if (mgmtSection && maxManagementHeight > 0) mgmtSection.style.minHeight = Math.max(maxManagementHeight, 50) + 'px';
            if (sscwSection && maxSscwHeight > 0) sscwSection.style.minHeight = Math.max(maxSscwHeight, 50) + 'px';
        });
    }, 100);
});
</script>'''

if '</body>' in content:
    content = content.replace('</body>', alignment_js + '\n</body>')
    print("✓ Added JavaScript-based alignment fix before </body>")
    with open(template_path, 'w') as f:
        f.write(content)
    print("✓ JavaScript alignment solution applied (client-side only, safe)")
else:
    print("✗ Could not find </body> tag")
