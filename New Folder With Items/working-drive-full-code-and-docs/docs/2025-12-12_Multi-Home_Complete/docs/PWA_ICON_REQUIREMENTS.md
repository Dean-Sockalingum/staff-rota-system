# PWA Icon Requirements

This document outlines the icon files needed for the Progressive Web App (PWA) functionality.

## Required Icon Sizes

All icons should be placed in `scheduling/static/images/` directory.

### PWA Icons (Android/Chrome)
- `icon-72x72.png` - Android Launcher (72x72px)
- `icon-96x96.png` - Android Launcher (96x96px)
- `icon-128x128.png` - Android Launcher (128x128px)
- `icon-144x144.png` - Android Launcher (144x144px)
- `icon-152x152.png` - Android Launcher (152x152px)
- **`icon-192x192.png`** - **REQUIRED** - Minimum size for PWA (192x192px)
- `icon-384x384.png` - Recommended for higher DPI (384x384px)
- **`icon-512x512.png`** - **REQUIRED** - Maximum size for PWA (512x512px)

### iOS Icons (Apple Touch Icons)
- `icon-120x120.png` - iPhone (120x120px)
- `icon-144x144.png` - iPad Retina (144x144px)
- `icon-152x152.png` - iPad Retina (152x152px)
- `icon-180x180.png` - iPhone X/11/12/13/14 (180x180px)

### Favicons (Browser Tab Icons)
- `favicon.ico` - Standard favicon (16x16, 32x32, 48x48 multi-size ICO)
- `favicon-16x16.png` - Small favicon (16x16px)
- `favicon-32x32.png` - Standard favicon (32x32px)

### Shortcut Icons (Optional - for PWA shortcuts)
- `shortcut-rota.png` - Rota shortcut icon (96x96px)
- `shortcut-leave.png` - Leave request shortcut icon (96x96px)
- `shortcut-dashboard.png` - Dashboard shortcut icon (96x96px)

### Screenshot Images (Optional - for PWA install preview)
- `screenshot-mobile-1.png` - Mobile screenshot (540x720px)
- `screenshot-mobile-2.png` - Mobile screenshot (540x720px)
- `screenshot-desktop-1.png` - Desktop screenshot (1280x720px)

## Design Guidelines

### Icon Design
- **Background**: Use the primary brand color (#0066FF) or white
- **Logo/Symbol**: Should be a simple, recognizable representation
  - Suggested: Calendar icon with "SR" or "STAFF" text
  - Alternative: Stylized calendar grid with staff silhouette
- **Safe Zone**: Keep important content within 80% of the icon area (40% margin from edges)
- **Maskable Icons**: For 192x192 and 512x512, ensure the icon works when circular or rounded-square masked

### Color Scheme
- **Primary**: #0066FF (Blue) - From design system
- **Secondary**: #00C853 (Green) - From design system
- **Accent**: #FF6F00 (Orange) - From design system
- **Background**: #FFFFFF (White)
- **Text**: #1F2937 (Dark Gray)

## Quick Generation with ImageMagick (if available)

If you have ImageMagick installed, you can generate all sizes from a single 512x512 source:

```bash
# Navigate to static/images directory
cd scheduling/static/images/

# Generate all PWA icon sizes (assuming you have source-icon-512.png)
convert source-icon-512.png -resize 72x72 icon-72x72.png
convert source-icon-512.png -resize 96x96 icon-96x96.png
convert source-icon-512.png -resize 128x128 icon-128x128.png
convert source-icon-512.png -resize 144x144 icon-144x144.png
convert source-icon-512.png -resize 152x152 icon-152x152.png
convert source-icon-512.png -resize 192x192 icon-192x192.png
convert source-icon-512.png -resize 384x384 icon-384x384.png
cp source-icon-512.png icon-512x512.png

# Generate iOS icons
convert source-icon-512.png -resize 120x120 icon-120x120.png
convert source-icon-512.png -resize 180x180 icon-180x180.png

# Generate favicons
convert source-icon-512.png -resize 32x32 favicon-32x32.png
convert source-icon-512.png -resize 16x16 favicon-16x16.png
```

## Online Icon Generators (Recommended)

If you don't have design tools, use these free online generators:

1. **PWA Manifest Generator** - https://www.simicart.com/manifest-generator.html/
   - Upload a 512x512 image
   - Generates all sizes + manifest.json
   
2. **Favicon.io** - https://favicon.io/
   - Create from text, image, or emoji
   - Generates favicon.ico and PNG sizes

3. **RealFaviconGenerator** - https://realfavicongenerator.net/
   - Comprehensive favicon generator
   - Generates all platform icons

## Temporary Placeholder Icons

Until custom icons are created, you can use placeholder icons:

1. Create a simple colored square with text:
   - Blue background (#0066FF)
   - White "SR" or calendar emoji 📅
   
2. Use browser default (no icons) - PWA will still work but installation UX will be degraded

## Testing PWA Installation

After adding icons:

1. **Chrome DevTools**:
   - Open DevTools (F12)
   - Go to "Application" tab
   - Check "Manifest" section for icon validation
   - Look for warnings about missing icons

2. **Lighthouse Audit**:
   - Run Lighthouse PWA audit
   - Check for "Installable" criteria
   - Minimum: 192x192 and 512x512 icons required

3. **Mobile Testing**:
   - Chrome Android: "Add to Home Screen" option should appear
   - iOS Safari: "Add to Home Screen" from share menu
   - Check that icon appears correctly on home screen

## Current Status

✅ Manifest file created: `scheduling/static/manifest.json`
✅ Manifest linked in base.html
⏳ **Action Required**: Create icon files (minimum 192x192 and 512x512)
⏳ **Action Required**: Place icons in `scheduling/static/images/` directory

## Next Steps (Task 13 - Service Worker)

After icons are in place, implement the service worker for offline support and full PWA functionality.
