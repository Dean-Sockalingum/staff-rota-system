# Tools Directory

Automated quality assurance and security enforcement tools for the Staff Rota System.

## 📋 Overview

This directory contains scripts and tools that automate code quality checks, security validation, and development workflows.

## 🔐 Security Enforcement

### check_api_decorators.py - Authentication (Phase 2)

Automated scanner that ensures all REST API endpoints have proper authentication decorators.

### check_api_permissions.py - Authorization (Phase 3)

Validates that API endpoints have appropriate permission checks beyond authentication.

**Quick Start:**
```bash
# Scan for missing decorators
python3 tools/check_api_decorators.py

# Auto-fix missing decorators
python3 tools/check_api_decorators.py --fix

# Strict mode for CI (exit 1 if issues found)
python3 tools/check_api_decorators.py --strict
```

**Features:**
- ✅ Scans all `path('api/...')` patterns in urls.py
- ✅ Verifies `@api_login_required` decorator presence
- ✅ Supports whitelist for OAuth/token-based endpoints
- ✅ Auto-fix capability to add missing decorators
- ✅ Detailed reporting by file and line number
- ✅ Exit codes for CI/CD integration

**Example Output:**
```
📊 Summary:
   Total API endpoints: 49
   ✅ Secured with @api_login_required: 41 (83.7%)
   🔐 Alternative auth (OAuth/tokens): 8 (16.3%)
   ⚠️  Missing decorator: 0 (0.0%)

✅ All API endpoints are properly secured!
```

**Documentation:** See `API_AUTH_PHASE2_COMPLETE_JAN4_2026.md`

**Quick Start (Phase 3 - Permissions):**
```bash
# Scan for missing permission checks
python3 tools/check_api_permissions.py

# Strict mode for CI (exit 1 if needs review)
python3 tools/check_api_permissions.py --strict
```

**Features:**
- ✅ Scans all API endpoints for authorization checks
- ✅ Detects: `is_management`, `can_approve_leave`, `can_manage_rota`, `is_superuser`
- ✅ Flags management actions without permission checks
- ✅ Identifies analytics/reporting endpoints needing review
- ✅ Detailed reporting by permission type

**Example Output:**
```
📊 Summary:
   Total API endpoints: 49
   ✅ With permission checks: 10 (20.4%)
   ⚠️  Need review: 8 (16.3%)
   ℹ️  No permissions needed: 29 (59.2%)

⚠️  ENDPOINTS NEEDING REVIEW:
   views_analytics.py:
      ❌ api_dashboard_summary (line 274)
         💡 Analytics endpoint - consider management-only access
```

### pre-commit-hook.sh

Git pre-commit hook that blocks commits with unauthenticated API endpoints.

**Installation:**
```bash
cp tools/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Behavior:**
- Runs automatically before every commit
- Executes `check_api_decorators.py --strict`
- Blocks commit if validation fails
- Provides clear error messages with fix instructions

**Bypass (not recommended):**
```bash
git commit --no-verify
```

## 📁 File Structure

```
tools/
├── README.md                       # This file
├── check_api_decorators.py         # API authentication validator (Phase 2)
├── check_api_permissions.py        # API authorization validator (Phase 3)
└── pre-commit-hook.sh              # Git pre-commit hook
```

## 🚀 CI/CD Integration

### GitHub Actions

Located at `.github/workflows/api-auth-check.yml`

**Triggers:**
- Pull requests modifying `scheduling/**/*.py`
- Pushes to `main` or `develop` branches

**Actions:**
- Runs `check_api_decorators.py --strict`
- Comments on PR if validation fails
- Prevents merge until all checks pass

## 🛠️ Development Workflow

### Adding New API Endpoint

1. **Create the endpoint:**
   ```python
   # In scheduling/views.py or other view file
   from .decorators_api import api_login_required
   
   @api_login_required
   @require_http_methods(["GET"])
   def my_new_api(request):
       return JsonResponse({'data': 'value'})
   ```

2. **Register in urls.py:**
   ```python
   path('api/my-endpoint/', views.my_new_api, name='my_new_api'),
   ```

3. **Validate before commit:**
   ```bash
   python3 tools/check_api_decorators.py
   ```

4. **Commit:**
   ```bash
   git add .
   git commit -m "Added new API endpoint"
   # Pre-commit hook runs automatically
   ```

### Auto-fix Workflow

If you forget to add the decorator:

```bash
# Create endpoint without decorator
# Add to urls.py
git add .

# Run auto-fix
python3 tools/check_api_decorators.py --fix

# Verify changes
git diff

# Commit
git commit -m "Added new API endpoint with auto-applied decorator"
```

## 🔒 Security Guidelines

### When to Use `@api_login_required`

Use for **internal APIs** accessed by authenticated users:
- Dashboard data APIs
- User preference APIs
- AI assistant endpoints
- Reporting APIs
- Admin functions

**Example:**
```python
@api_login_required
def staff_performance_api(request):
    # User is guaranteed authenticated
    return JsonResponse({'performance': get_staff_data(request.user)})
```

### When to Use OAuth/Token Auth

Use for **external integrations** accessed by third-party systems:
- Payroll export APIs
- HR system integrations
- Mobile app backends
- Webhook endpoints

**Example:**
```python
@require_api_scope('staff:read')
@csrf_exempt
def api_list_staff(request):
    # Token-based authentication
    return JsonResponse({'staff': get_all_staff()})
```

Add these to whitelist in `check_api_decorators.py`.

## 📊 Current Coverage

As of January 4, 2026:

| Category | Count | Percentage |
|----------|-------|------------|
| Session Auth (`@api_login_required`) | 41 | 83.7% |
| OAuth/Token Auth (whitelisted) | 8 | 16.3% |
| Unauthenticated | 0 | 0.0% |
| **Total Endpoints** | **49** | **100%** |

**Files Secured:**
- `views.py` (15 endpoints)
- `views_week6.py` (8 endpoints)
- `views_compliance.py` (4 endpoints)
- `views_analytics.py` (4 endpoints)
- `views_onboarding.py` (4 endpoints)
- `views_ot_intelligence.py` (2 endpoints)
- `views_report_builder.py` (2 endpoints)
- `ai_recommendations.py` (2 endpoints)
- `views_2fa.py` (1 endpoint)
- `views_ai_assistant.py` (1 endpoint)

## 🐛 Troubleshooting

**Q: "Function not found" error**  
A: The endpoint is in `urls.py` but the function doesn't exist. Check for typos or missing imports.

**Q: Pre-commit hook not running**  
A: Ensure it's executable: `chmod +x .git/hooks/pre-commit`

**Q: False positive (endpoint has auth but checker says missing)**  
A: Check decorator name exactly matches `@api_login_required`. Alternative auth should be whitelisted.

**Q: How to disable temporarily?**  
A: Use `git commit --no-verify` to bypass pre-commit hook (use sparingly).

## 🔄 Maintenance

### Updating Whitelist

To exempt an OAuth/token endpoint from requiring `@api_login_required`:

```python
# In tools/check_api_decorators.py, line ~20
WHITELIST_ALTERNATIVE_AUTH = {
    # Existing entries...
    'my_oauth_endpoint',  # Reason: External partner API
}
```

### Adding New Checks

The checker is extensible. Future enhancements:
- Permission level validation
- CSRF protection checks
- Rate limiting verification
- API documentation generation

## 📚 Related Documentation

- **Phase 1 Complete:** `API_AUTH_MIGRATION_COMPLETE_JAN3_2026.md`
- **Phase 2 Complete:** `API_AUTH_PHASE2_COMPLETE_JAN4_2026.md`
- **Decorator Source:** `scheduling/decorators_api.py`

## 🎯 Quick Commands

```bash
# Check all endpoints
python3 tools/check_api_decorators.py

# Fix missing decorators
python3 tools/check_api_decorators.py --fix

# CI mode (exit 1 if issues)
python3 tools/check_api_decorators.py --strict

# Install pre-commit hook
cp tools/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

# Test pre-commit hook
git commit --dry-run

# View detailed report
python3 tools/check_api_decorators.py | less
```

## ✅ Success Criteria

Your API security is solid when:
- ✅ `check_api_decorators.py` reports 0 missing decorators
- ✅ Pre-commit hook is installed and executable
- ✅ GitHub Actions workflow is active
- ✅ All team members aware of workflow
- ✅ Whitelist documented with reasons

---

**Last Updated:** January 4, 2026  
**Status:** Production Ready ✅  
**Coverage:** 100% (49/49 endpoints)
