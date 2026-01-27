import re

base_html = '/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/base.html'

with open(base_html, 'r') as f:
    content = f.read()

# Fix body tag to remove default margins
content = re.sub(
    r'<body>',
    '<body style="margin: 0; padding: 0;">',
    content
)

# Fix demo mode banner - better contrast and full width
content = re.sub(
    r'<div class="alert alert-warning text-center mb-0" role="alert" style="[^"]+">',
    '<div class="alert alert-warning text-center mb-0" role="alert" style="border-radius: 0; border: none; background-color: #ff6b00; color: #000000; font-weight: 800; padding: 10px; width: 100vw; margin: 0; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; text-shadow: none;">',
    content
)

# Fix production mode banner - better contrast and full width
content = re.sub(
    r'<div class="alert alert-danger text-center mb-0" role="alert" style="[^"]+">',
    '<div class="alert alert-danger text-center mb-0" role="alert" style="border-radius: 0; border: none; background-color: #dc3545; color: #ffffff; font-weight: 800; padding: 10px; width: 100vw; margin: 0; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">',
    content
)

# Fix navbar to full width with better styling
content = re.sub(
    r'<nav class="navbar navbar-expand-lg navbar-dark bg-primary" id="navigation" tabindex="-1"[^>]*>',
    '<nav class="navbar navbar-expand-lg navbar-dark bg-primary" id="navigation" tabindex="-1" style="width: 100vw; margin: 0; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; padding-left: 15px; padding-right: 15px;">',
    content
)

with open(base_html, 'w') as f:
    f.write(content)

print('✓ Fixed banner contrast and full-width extension')
