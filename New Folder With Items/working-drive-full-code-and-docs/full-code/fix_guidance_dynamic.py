#!/usr/bin/env python3
"""
Update staff_guidance view to dynamically load all markdown files
"""

# Read the views.py file
with open('/home/staff-rota-system/scheduling/views.py', 'r') as f:
    lines = f.readlines()

# Find the staff_guidance function and replace the hardcoded list
in_guidance_function = False
in_guidance_docs_list = False
skip_until_close_bracket = False
output_lines = []
indent = '    '

for i, line in enumerate(lines):
    if 'def staff_guidance(request):' in line:
        in_guidance_function = True
        output_lines.append(line)
        continue
    
    if in_guidance_function and 'guidance_docs = [' in line:
        # Replace the entire hardcoded list with dynamic file scanning
        output_lines.append(f'{indent}# Dynamically load all markdown files from docs/staff_guidance\n')
        output_lines.append(f'{indent}guidance_docs = []\n')
        output_lines.append(f'{indent}if docs_path.exists():\n')
        output_lines.append(f'{indent}    for md_file in sorted(docs_path.glob("*.md")):\n')
        output_lines.append(f'{indent}        filename = md_file.stem\n')
        output_lines.append(f'{indent}        # Create title from filename\n')
        output_lines.append(f'{indent}        title = filename.replace("_", " ").title()\n')
        output_lines.append(f'{indent}        slug = filename.lower().replace("_", "-")\n')
        output_lines.append(f'{indent}        \n')
        output_lines.append(f'{indent}        # Determine category based on filename\n')
        output_lines.append(f'{indent}        if any(word in filename.upper() for word in ["MANAGER", "SOP", "CHECKLIST"]):\n')
        output_lines.append(f'{indent}            category = "manager"\n')
        output_lines.append(f'{indent}            icon = "fa-user-tie"\n')
        output_lines.append(f'{indent}        elif "CARE_INSPECTORATE" in filename.upper():\n')
        output_lines.append(f'{indent}            category = "compliance"\n')
        output_lines.append(f'{indent}            icon = "fa-clipboard-check"\n')
        output_lines.append(f'{indent}        else:\n')
        output_lines.append(f'{indent}            category = "staff"\n')
        output_lines.append(f'{indent}            icon = "fa-book"\n')
        output_lines.append(f'{indent}        \n')
        output_lines.append(f'{indent}        guidance_docs.append({{\n')
        output_lines.append(f'{indent}            "title": title,\n')
        output_lines.append(f'{indent}            "slug": slug,\n')
        output_lines.append(f'{indent}            "description": f"{{title}} documentation",\n')
        output_lines.append(f'{indent}            "file": md_file,\n')
        output_lines.append(f'{indent}            "category": category,\n')
        output_lines.append(f'{indent}            "icon": icon,\n')
        output_lines.append(f'{indent}        }})\n')
        output_lines.append(f'{indent}\n')
        
        skip_until_close_bracket = True
        continue
    
    if skip_until_close_bracket:
        # Skip all lines until we find the closing bracket of the guidance_docs list
        if line.strip() == ']':
            skip_until_close_bracket = False
        continue
    
    output_lines.append(line)

# Write back
with open('/home/staff-rota-system/scheduling/views.py', 'w') as f:
    f.writelines(output_lines)

print("✅ Updated staff_guidance view to dynamically load all markdown files")
