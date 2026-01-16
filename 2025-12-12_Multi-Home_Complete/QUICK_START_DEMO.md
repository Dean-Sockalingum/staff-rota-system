# 🚀 ONE-CLICK DEMO & PRODUCTION ACCESS

## Your Desktop Shortcuts (Ready to Use!)

Check your **Desktop** - you now have 4 clickable shortcuts:

### 📱 **Start_Demo.command** ← DOUBLE-CLICK THIS!
**One-click demo launch!**
- Switches to demo mode automatically
- Starts the server at http://127.0.0.1:8000
- Shows login credentials (admin/admin)
- Safe for testing - won't affect production

### 🔄 **Switch_Mode.command**
Switch between DEMO and PRODUCTION
- Interactive menu
- Safety confirmations
- View current status

### 🛑 **Stop_Server.command**
Stop the running server
- Quick shutdown
- Use when finished testing

### ♻️ **Reset_Demo.command**
Reset demo to clean state
- Fresh demo data
- Use after testing changes

---

## HOW TO USE

### For Demonstrations (Recommended)
1. **Double-click** `Start_Demo.command` on your Desktop
2. Browser opens to http://127.0.0.1:8000
3. Login with: **admin** / **admin**
4. **Orange banner** confirms DEMO mode
5. Test freely - changes won't affect production!

### To Stop
Press **Ctrl+C** in terminal OR double-click `Stop_Server.command`

### To Reset Demo Data
Double-click `Reset_Demo.command` - demo returns to clean state

### To Switch to Production (When Ready)
1. Double-click `Switch_Mode.command`
2. Select option **2** (Production mode)
3. Type **"PRODUCTION"** to confirm
4. **Red banner** confirms PRODUCTION mode
5. Now using live data!

---

## VISUAL INDICATORS

### When in DEMO Mode:
```
🟠 Orange banner: "DEMO MODE - All changes are isolated"
🟠 Orange "DEMO" badge next to "Staff Rota System"
```

### When in PRODUCTION Mode:
```
🔴 Red banner: "PRODUCTION MODE - Live data in use"
🔴 Red "LIVE" badge next to "Staff Rota System"
```

**You'll always know which mode you're in!**

---

## TYPICAL WORKFLOW

### Before Go-Live (Testing Phase)
1. Double-click **Start_Demo.command**
2. Test all features
3. Demo to stakeholders
4. Double-click **Reset_Demo.command** to start fresh
5. Repeat as needed

### When Ready for Production
1. Double-click **Switch_Mode.command**
2. Choose option 2 (Production)
3. Type "PRODUCTION"
4. Announce to staff: system is LIVE

### After Go-Live
- Keep using **Start_Demo.command** for testing new features
- Use **Switch_Mode.command** to switch between modes
- DEMO stays available for training

---

## LOGIN CREDENTIALS

### Demo Mode
- Username: **admin**
- Password: **admin**

### Production Mode
- Use real staff credentials
- See NEXT_STEPS.md for user account setup

---

## WHAT'S SAFE TO DO?

### ✅ ALWAYS SAFE (in Demo Mode)
- Create/delete shifts
- Request leave
- Approve/reject requests
- Test all features
- Make mistakes
- Show to stakeholders

### ⚠️ USE WITH CARE (in Production Mode)
- All changes are permanent
- Staff will see changes
- Affects real schedules
- No "undo" button

---

## QUICK TIPS

💡 **Want to show the project to someone?**
→ Just double-click **Start_Demo.command**!

💡 **Finished testing and want fresh data?**
→ Double-click **Reset_Demo.command**

💡 **Not sure which mode you're in?**
→ Look for the orange (DEMO) or red (PRODUCTION) banner at the top

💡 **Server won't start?**
→ Double-click **Stop_Server.command** first, then try again

💡 **Made changes in demo and want to keep them?**
→ Changes are saved in demo database until you reset

---

## FILES EXPLAINED

Your system now has:
- **db.sqlite3** - Active database (currently in use)
- **db_demo.sqlite3** - Demo database (safe testing)
- **db_production.sqlite3** - Production database (live data)
- **.current_mode** - Tracks which mode you're in

When you switch modes, `db.sqlite3` points to the right database.

---

## TROUBLESHOOTING

### "Nothing happens when I double-click"
Right-click the .command file → Open → Click "Open" again

### "Terminal shows error"
Make sure you're in demo mode:
```bash
cd /Users/deansockalingum/Desktop/Staff_Rota_Backups/2025-12-12_Multi-Home_Complete
python3 manage.py set_mode status
```

### "Can't tell which mode I'm in"
Look at the banner at the top of any page:
- Orange = DEMO
- Red = PRODUCTION

### "Want to go back to production"
Double-click **Switch_Mode.command** → Choose option 2

---

## RECOMMENDED: Test It Now!

1. **Double-click** `Start_Demo.command` on your Desktop
2. **Wait** for terminal to show: "Starting development server..."
3. **Open browser** to: http://127.0.0.1:8000
4. **Login:** admin / admin
5. **Look for** orange "DEMO MODE" banner at top
6. **Test** creating a shift or requesting leave
7. **Press** Ctrl+C in terminal to stop
8. **Double-click** `Reset_Demo.command` to reset data

---

## SUMMARY

**🎯 Your Goal:** Easily demo the system without affecting production

**✅ Solution:** Double-click `Start_Demo.command` on your Desktop

**🔄 Switch modes:** Double-click `Switch_Mode.command`

**♻️ Reset demo:** Double-click `Reset_Demo.command`

**🛑 Stop server:** Double-click `Stop_Server.command` OR press Ctrl+C

**👀 Visual indicators:** Orange banner = DEMO, Red banner = PRODUCTION

**📖 Full guide:** See DEMO_PRODUCTION_MODE_GUIDE.md for details

---

**You're all set! The system is ready to demo.** 🚀
