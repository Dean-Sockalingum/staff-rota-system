# DEMO & PRODUCTION MODE SYSTEM

## Quick Reference

### **Option 1: One-Click Demo Start** (Recommended for demos)
```bash
./demo_start.sh
```
This will:
- Switch to DEMO mode automatically
- Start the development server
- Show login credentials
- Display system at http://127.0.0.1:8000

Login: admin / admin

---

### **Option 2: Manual Mode Switching**
```bash
./switch_mode.sh
```
Interactive menu to:
1. Switch to DEMO mode
2. Switch to PRODUCTION mode
3. Reset DEMO data
4. Check current status

---

## What is DEMO Mode?

**DEMO Mode** uses a separate database (`db_demo.sqlite3`) that is completely isolated from your production data. 

✅ **Safe for:**
- Testing new features
- Training staff
- Demonstrating to stakeholders
- Making mistakes without consequences

🔄 **Reset anytime:**
```bash
python3 manage.py reset_demo
```

---

## What is PRODUCTION Mode?

**PRODUCTION Mode** uses your live database (`db_production.sqlite3`) with real data.

⚠️ **USE WITH CAUTION:**
- All changes affect real schedules
- All data is permanent
- Staff will see these changes

---

## Visual Indicators

When you log in, you'll see:

**DEMO MODE:**
- 🟠 Orange banner at top: "DEMO MODE - All changes are isolated"
- 🟠 Orange "DEMO" badge next to system name

**PRODUCTION MODE:**
- 🔴 Red banner at top: "PRODUCTION MODE - Live data in use"
- 🔴 Red "LIVE" badge next to system name

---

## Command Reference

### Switch to DEMO mode
```bash
python3 manage.py set_mode demo
```

### Switch to PRODUCTION mode
```bash
python3 manage.py set_mode prod
```

### Check current mode
```bash
python3 manage.py set_mode status
```

### Reset DEMO data to clean state
```bash
python3 manage.py reset_demo
```

### Reset DEMO data from production backup
```bash
python3 manage.py reset_demo --fresh
```

---

## How It Works

### Database Files
- `db.sqlite3` - Active database (points to either demo or production)
- `db_demo.sqlite3` - Demo/testing database
- `db_production.sqlite3` - Production/live database
- `.current_mode` - Stores current mode (DEMO or PRODUCTION)

### Mode Switching
When you switch modes, the system:
1. Backs up the current active database
2. Copies the selected database to `db.sqlite3`
3. Updates the mode indicator
4. Shows confirmation

### Safety Features
- ✅ Always creates backups before switching
- ✅ Requires typing "PRODUCTION" to confirm production switch
- ✅ Visual indicators in all pages
- ✅ Separate databases prevent data mixing
- ✅ Easy demo reset without affecting production

---

## Recommended Workflow

### Before Go-Live (Current Phase)
1. **Start in DEMO mode:**
   ```bash
   ./demo_start.sh
   ```

2. **Test everything:**
   - Create shifts
   - Request leave
   - Swap shifts
   - Run reports
   - Test all features

3. **Reset and test again:**
   ```bash
   python3 manage.py reset_demo
   ```

4. **Demo to stakeholders:**
   - Show them the system works
   - Get feedback
   - Make adjustments in demo mode

### When Ready for Production
1. **Prepare production database:**
   - Ensure all data is correct
   - Verify staff accounts
   - Check shift patterns

2. **Switch to production:**
   ```bash
   ./switch_mode.sh
   # Select option 2 (Production mode)
   # Type "PRODUCTION" to confirm
   ```

3. **Announce to staff:**
   - System is now live
   - Changes are permanent
   - Provide login details

### After Go-Live
1. **Keep DEMO available** for:
   - Training new managers
   - Testing new features
   - Experimenting safely

2. **Switch back to DEMO when needed:**
   ```bash
   python3 manage.py set_mode demo
   ```

3. **Update DEMO data occasionally:**
   ```bash
   python3 manage.py reset_demo --fresh
   ```
   This copies current production data to demo for realistic testing.

---

## Desktop Shortcuts (macOS)

You can create desktop shortcuts for easy access:

### Create "Start Demo" Shortcut
1. Open TextEdit
2. Paste this code:
   ```applescript
   #!/bin/bash
   cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
   ./demo_start.sh
   ```
3. Save as: `Start_Demo.command` on your Desktop
4. In Terminal: `chmod +x ~/Desktop/Start_Demo.command`
5. Double-click to launch demo!

### Create "Switch Mode" Shortcut
1. Open TextEdit
2. Paste this code:
   ```applescript
   #!/bin/bash
   cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
   ./switch_mode.sh
   ```
3. Save as: `Switch_Mode.command` on your Desktop
4. In Terminal: `chmod +x ~/Desktop/Switch_Mode.command`

---

## Troubleshooting

### "No database found"
```bash
# Copy current database to demo
cp db.sqlite3 db_demo.sqlite3
python3 manage.py set_mode demo
```

### "Can't switch - server is running"
```bash
# Stop the server first (Ctrl+C in terminal)
# Then switch modes
```

### "Lost track of which mode I'm in"
```bash
python3 manage.py set_mode status
```

### "Want to start completely fresh"
```bash
# This resets demo to clean state
python3 manage.py reset_demo
```

---

## Security Notes

🔒 **DEMO mode is NOT for:**
- Internet/public access
- Sensitive testing (still uses real staff names)
- Permanent storage

🔒 **PRODUCTION mode requires:**
- Strong passwords
- DEBUG=False in settings
- HTTPS enabled
- Regular backups

---

## Summary

**For Demos/Testing:** `./demo_start.sh` ← Just use this!

**For Production:** `./switch_mode.sh` → Select Production → Type "PRODUCTION"

**To Reset Demo:** `python3 manage.py reset_demo`

**Visual indicators** always show which mode you're in.

**Completely safe** - demo and production data never mix.
