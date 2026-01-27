#!/usr/bin/env python3
"""
Generate simple placeholder PWA icons for Staff Rota System
This creates basic colored squares with text until proper icons are designed.
Requires: Pillow (pip install Pillow)
"""

import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install Pillow")
    exit(1)

# Icon configuration
ICON_COLOR = "#0066FF"  # Primary brand color
TEXT_COLOR = "#FFFFFF"  # White text
ICON_TEXT = "SR"  # Staff Rota

# Icon sizes to generate
ICON_SIZES = [
    72, 96, 120, 128, 144, 152, 180, 192, 384, 512
]

# Output directory
SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "scheduling" / "static" / "images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_icon(size, text, bg_color, text_color, output_path):
    """Create a simple square icon with text"""
    # Create image with background color
    img = Image.new('RGB', (size, size), hex_to_rgb(bg_color))
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        # Try different font sizes based on icon size
        font_size = int(size * 0.4)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.4))
        except:
            font = ImageFont.load_default()
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text
    x = (size - text_width) / 2
    y = (size - text_height) / 2
    
    # Draw text
    draw.text((x, y), text, fill=hex_to_rgb(text_color), font=font)
    
    # Save image
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ Created {output_path.name} ({size}x{size})")

def create_favicon_ico():
    """Create multi-size .ico file"""
    sizes = [16, 32, 48]
    images = []
    
    for size in sizes:
        img = Image.new('RGB', (size, size), hex_to_rgb(ICON_COLOR))
        draw = ImageDraw.Draw(img)
        
        # For small sizes, just use a solid color or simple shape
        # Drawing text at 16x16 is not readable
        if size >= 32:
            try:
                font_size = int(size * 0.5)
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                bbox = draw.textbbox((0, 0), ICON_TEXT, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (size - text_width) / 2
                y = (size - text_height) / 2
                draw.text((x, y), ICON_TEXT, fill=hex_to_rgb(TEXT_COLOR), font=font)
            except:
                pass
        
        images.append(img)
    
    # Save as multi-size ICO
    output_path = OUTPUT_DIR / "favicon.ico"
    images[0].save(output_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"✓ Created favicon.ico (multi-size)")

def main():
    print("Generating PWA placeholder icons...")
    print(f"Output directory: {OUTPUT_DIR}")
    print("")
    
    # Generate all icon sizes
    for size in ICON_SIZES:
        filename = f"icon-{size}x{size}.png"
        output_path = OUTPUT_DIR / filename
        create_icon(size, ICON_TEXT, ICON_COLOR, TEXT_COLOR, output_path)
    
    # Create favicon PNG sizes
    for size in [16, 32]:
        filename = f"favicon-{size}x{size}.png"
        output_path = OUTPUT_DIR / filename
        create_icon(size, "" if size < 32 else ICON_TEXT, ICON_COLOR, TEXT_COLOR, output_path)
    
    # Create multi-size favicon.ico
    create_favicon_ico()
    
    # Create placeholder shortcut icons (same as main icons for now)
    shortcuts = ['rota', 'leave', 'dashboard']
    for shortcut in shortcuts:
        filename = f"shortcut-{shortcut}.png"
        output_path = OUTPUT_DIR / filename
        create_icon(96, ICON_TEXT, ICON_COLOR, TEXT_COLOR, output_path)
    
    print("")
    print("✓ All placeholder icons generated successfully!")
    print("")
    print("NEXT STEPS:")
    print("1. Replace these placeholder icons with professionally designed ones")
    print("2. Test PWA installation on Chrome/Android and Safari/iOS")
    print("3. Run Lighthouse audit to verify PWA criteria")
    print("")
    print("See docs/PWA_ICON_REQUIREMENTS.md for design guidelines")

if __name__ == "__main__":
    main()
