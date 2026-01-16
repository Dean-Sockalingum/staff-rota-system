#!/usr/bin/env python3
"""
Fix CSRF_TRUSTED_ORIGINS in production settings
"""

settings_file = '/home/staff-rota-system/rotasystems/settings.py'

# Read the settings file
with open(settings_file, 'r') as f:
    content = f.read()

# Check if CSRF_TRUSTED_ORIGINS already exists
if 'CSRF_TRUSTED_ORIGINS' in content:
    print("CSRF_TRUSTED_ORIGINS already exists, updating...")
    # Replace existing
    import re
    content = re.sub(
        r'CSRF_TRUSTED_ORIGINS\s*=\s*\[.*?\]',
        "CSRF_TRUSTED_ORIGINS = ['https://demo.therota.co.uk', 'https://therota.co.uk']",
        content,
        flags=re.DOTALL
    )
else:
    print("Adding CSRF_TRUSTED_ORIGINS...")
    # Find ALLOWED_HOSTS and add after it
    if 'ALLOWED_HOSTS' in content:
        content = content.replace(
            'ALLOWED_HOSTS',
            'ALLOWED_HOSTS',
            1
        )
        # Find the line with ALLOWED_HOSTS and add after it
        lines = content.split('\n')
        new_lines = []
        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'ALLOWED_HOSTS' in line and '=' in line:
                # Add CSRF_TRUSTED_ORIGINS after ALLOWED_HOSTS
                new_lines.append('')
                new_lines.append('# CSRF Settings for production')
                new_lines.append("CSRF_TRUSTED_ORIGINS = ['https://demo.therota.co.uk', 'https://therota.co.uk']")
        content = '\n'.join(new_lines)

# Also ensure demo.therota.co.uk is in ALLOWED_HOSTS
if 'ALLOWED_HOSTS' in content and 'demo.therota.co.uk' not in content:
    print("Adding demo.therota.co.uk to ALLOWED_HOSTS...")
    import re
    # Find ALLOWED_HOSTS = [...] and add demo.therota.co.uk
    content = re.sub(
        r'(ALLOWED_HOSTS\s*=\s*\[)',
        r"\1'demo.therota.co.uk', 'therota.co.uk', ",
        content
    )

# Write back
with open(settings_file, 'w') as f:
    f.write(content)

print("✅ Settings updated successfully")
print("CSRF_TRUSTED_ORIGINS = ['https://demo.therota.co.uk', 'https://therota.co.uk']")
