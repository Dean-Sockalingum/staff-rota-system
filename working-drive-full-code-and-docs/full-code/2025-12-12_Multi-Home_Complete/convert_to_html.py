#!/usr/bin/env python3
"""
Convert markdown letters to professional HTML format
"""
import markdown
import os

# HTML template with professional styling
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Calibri', 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            max-width: 850px;
            margin: 40px auto;
            padding: 20px 40px;
            color: #333;
            background-color: #f5f5f5;
        }}
        .letter-container {{
            background-color: white;
            padding: 60px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #1a5490;
            border-bottom: 3px solid #1a5490;
            padding-bottom: 10px;
            margin-bottom: 30px;
            font-size: 24px;
        }}
        h2 {{
            color: #2c6ba8;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 20px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #3d7db5;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        strong {{
            color: #1a5490;
        }}
        ul, ol {{
            margin-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #1a5490;
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .metadata {{
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 15px;
        }}
        .signature {{
            margin-top: 40px;
            font-weight: bold;
        }}
        hr {{
            border: none;
            border-top: 2px solid #e0e0e0;
            margin: 30px 0;
        }}
        .highlight {{
            background-color: #fff9e6;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        @media print {{
            body {{
                background-color: white;
                margin: 0;
                padding: 0;
            }}
            .letter-container {{
                box-shadow: none;
                padding: 40px;
            }}
        }}
    </style>
</head>
<body>
    <div class="letter-container">
        {content}
    </div>
</body>
</html>
"""

def convert_markdown_to_html(md_file, output_file):
    """Convert markdown file to HTML with professional styling"""
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Configure markdown with extensions
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'nl2br',
        'sane_lists'
    ])
    
    # Convert to HTML
    html_content = md.convert(md_content)
    
    # Extract title from first h1
    title = "Letter"
    if '<h1>' in html_content:
        title = html_content.split('<h1>')[1].split('</h1>')[0]
    
    # Create full HTML document
    full_html = HTML_TEMPLATE.format(
        title=title,
        content=html_content
    )
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"✅ Created: {output_file}")

if __name__ == "__main__":
    # Convert both letters
    convert_markdown_to_html(
        'LETTER_TO_HOS_ROBIN_WALLACE.md',
        'LETTER_TO_HOS_ROBIN_WALLACE.html'
    )
    
    convert_markdown_to_html(
        'LETTER_TO_HEAD_OF_PLANNING_LIAM_HERBERT.md',
        'LETTER_TO_HEAD_OF_PLANNING_LIAM_HERBERT.html'
    )
    
    print("\n✅ HTML conversion complete!")
    print("📧 Files ready for emailing:")
    print("   - LETTER_TO_HOS_ROBIN_WALLACE.html")
    print("   - LETTER_TO_HEAD_OF_PLANNING_LIAM_HERBERT.html")
