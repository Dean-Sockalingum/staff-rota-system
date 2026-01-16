# Staff Rota System

A comprehensive Django-based staff scheduling and rota management system for care facilities.

## � ONE-CLICK DEMO ACCESS

**Check your Desktop** for 4 shortcuts to instantly demo the system:

- **📱 Start_Demo.command** ← Double-click this to launch demo in one click!
- **🔄 Switch_Mode.command** - Switch between DEMO and PRODUCTION modes
- **🛑 Stop_Server.command** - Stop the running server
- **♻️ Reset_Demo.command** - Reset demo data to clean state

**Quick start:** Double-click `Start_Demo.command` on your Desktop, then login with admin/admin

See: [QUICK_START_DEMO.md](QUICK_START_DEMO.md) for full guide

### Visual Mode Indicators
- 🟠 **Orange banner** = DEMO mode (safe for testing, training, demonstrations)
- 🔴 **Red banner** = PRODUCTION mode (live data, changes are permanent)

You'll always know which mode you're in!

## �🆘 Need Help? Ask the AI Assistant!

**New feature:** Built-in AI chatbot for instant help and guidance!

```bash
python3 manage.py help_assistant
```

Ask questions like:
- "How do I add a new staff member?"
- "Where is the admin panel?"
- "How do I generate a rota?"
- "Database is locked, what do I do?"

See: `AI_ASSISTANT_GUIDE.md` for full details.

## 🚀 Quick Start (First-Time Setup)

**New to the system?** Use the interactive setup wizard:

```bash
python3 manage.py setup_wizard
```

This guided wizard will:
- ✓ Create admin account
- ✓ Set up organizational structure (roles, units, shift types)
- ✓ Guide you through staff data import
- ✓ Help generate initial rotas

**For detailed setup instructions**, see:
- `FIRST_TIME_SETUP.md` - Comprehensive setup guide
- `SETUP_REFERENCE.md` - Quick reference card
- `SETUP_WIZARD_GUIDE.md` - Visual walkthrough

## Project Structure

A typical Django project has the following structure:

```
rotasystems/  <- This should be your project root folder in VS Code
├── manage.py
├── rotasystems/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── tests.py
└── requirements.txt
```

**Recommendation:** Open the parent folder `/Users/deansockalingum/Staff Rota/rotasystems` in VS Code to have a better overview of your project.

## Development Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

4.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

The application will be available at `http://127.0.0.1:8000`.
