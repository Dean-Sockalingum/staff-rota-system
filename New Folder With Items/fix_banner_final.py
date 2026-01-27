import re

base_html = '/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/base.html'

with open(base_html, 'r') as f:
    content = f.read()

# Add CSS to ensure no container restrictions and improve navbar text contrast
css_addition = """
    <style>
        /* Force banners and navbar to true full width */
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            overflow-x: hidden !important;
            width: 100% !important;
        }
        
        /* Better navbar link contrast */
        .navbar-dark .navbar-nav .nav-link {
            color: #ffffff !important;
            font-weight: 500 !important;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
        }
        
        .navbar-dark .navbar-nav .nav-link:hover,
        .navbar-dark .navbar-nav .nav-link:focus {
            color: #ffeb3b !important;
            font-weight: 600 !important;
        }
        
        .navbar-dark .navbar-brand {
            color: #ffffff !important;
            font-weight: 700 !important;
            text-shadow: 2px 2px 3px rgba(0,0,0,0.4) !important;
        }
        
        /* Dropdown menu contrast */
        .navbar-dark .dropdown-menu {
            background-color: #0056b3 !important;
        }
        
        .navbar-dark .dropdown-item {
            color: #ffffff !important;
        }
        
        .navbar-dark .dropdown-item:hover {
            background-color: #003d82 !important;
            color: #ffeb3b !important;
        }
    </style>
"""

# Insert the CSS before </head>
content = content.replace('</head>', css_addition + '\n</head>')

# Fix body with inline style
content = re.sub(
    r'<body[^>]*>',
    '<body style="margin: 0 !important; padding: 0 !important; width: 100% !important; overflow-x: hidden !important;">',
    content
)

# Wrap banner and navbar in a container that breaks out of any constraints
wrapper_start = '<div style="width: 100%; margin: 0; padding: 0; position: relative;">'
wrapper_end = '</div>'

# Fix demo banner with absolute positioning
content = re.sub(
    r'<div class="alert alert-warning text-center mb-0" role="alert" style="[^"]*">',
    wrapper_start + '<div class="alert alert-warning text-center mb-0" role="alert" style="border-radius: 0; border: none; background-color: #ff6b00; color: #000000; font-weight: 800; padding: 10px; width: 100%; margin: 0; box-sizing: border-box;">',
    content
)

# Add closing wrapper after demo banner
content = re.sub(
    r'(DEMO MODE - All changes are isolated from production data\s*</div>)',
    r'\1' + wrapper_end,
    content
)

# Fix production banner
content = re.sub(
    r'<div class="alert alert-danger text-center mb-0" role="alert" style="[^"]*">',
    wrapper_start + '<div class="alert alert-danger text-center mb-0" role="alert" style="border-radius: 0; border: none; background-color: #dc3545; color: #ffffff; font-weight: 800; padding: 10px; width: 100%; margin: 0; box-sizing: border-box; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">',
    content
)

# Add closing wrapper after production banner
content = re.sub(
    r'(PRODUCTION MODE - Live data in use\s*</div>)',
    r'\1' + wrapper_end,
    content
)

# Fix navbar with proper full width
content = re.sub(
    r'<nav class="navbar navbar-expand-lg navbar-dark bg-primary" id="navigation" tabindex="-1"[^>]*>',
    '<nav class="navbar navbar-expand-lg navbar-dark" id="navigation" tabindex="-1" style="background-color: #0056b3 !important; width: 100%; margin: 0; padding: 12px 20px; box-sizing: border-box; position: relative;">',
    content
)

with open(base_html, 'w') as f:
    f.write(content)

print('✓ Fixed full-width banners and improved navbar contrast')
print('  - Banners now extend edge-to-edge')
print('  - Navbar links now white with better visibility')
print('  - Hover states use yellow highlight')
