# TODO List - January 5, 2026

## High Priority (Quick Wins)

### 1. Fix CareHome test data field mismatches
**Impact:** 40+ tests
**Effort:** 30 minutes
**Status:** Not started

40+ tests failing with ERROR due to `CareHome.objects.create(address='...')` using wrong field names. Need to update test factories in:
- `test_task56_compliance_widgets.py`
- `test_task59_leave_calendar.py`

Update to match actual CareHome model fields. This is the largest batch of fixable errors.

### 2. Fix Task 55 Activity Feed template issues
**Impact:** 4 tests
**Effort:** 15 minutes
**Status:** Not started

4 ERROR tests in `test_task55_activity_feed` views failing with template not found or template syntax errors. Create missing templates or verify template paths for:
- `activity_feed_api`
- `activity_feed_authenticated` views

### 3. Create Feature Readiness Matrix
**Impact:** User deliverable
**Effort:** 20 minutes
**Status:** Not started

User requested item 3: Document feature-by-feature production readiness. Include:
- Core features (90%+)
- New features Tasks 55-59 (40-75%)
- URLs (100%)
- AI Assistant
- Analytics

Format as markdown table showing what works vs what tests indicate.

## Medium Priority

### 4. Fix test_ai_assistant_leave_balance failure
**Impact:** 1 test
**Effort:** 45 minutes (complex)
**Status:** Not started

Single test failing - `_process_leave_balance_query` returning None (not finding Alice Smith). Investigate:
- Database isolation issue
- Fuzzy matching threshold in AI Assistant leave balance query processing

### 5. Re-enable scheduling/urls.py main URL file
**Impact:** Complete URL infrastructure
**Effort:** 2-3 hours
**Status:** Not started

Currently using minimal URL files (`urls_activity.py`, `urls_compliance.py`, `urls_calendar.py`) to avoid import cascade. Fix 60+ broken imports across view files:
- analytics classes
- elasticsearch_dsl
- permissions module
- etc.

This will enable the full 741-line `urls.py` file.

### 6. Re-implement manager_required decorator
**Impact:** Security enhancement
**Effort:** 30 minutes
**Status:** Not started

`views_activity.py` line 257 commented out `@manager_required` decorator (doesn't exist). Need to:
- Create decorator OR
- Use existing role-checking mechanism to restore manager-only access control for `manage_activity_widgets` view

## Lower Priority

### 7. Review remaining 8 test failures
**Impact:** 8 tests
**Effort:** 1-2 hours
**Status:** Not started

8 tests marked as FAIL (not ERROR). Review:
- Actual logic bugs vs test expectation mismatches
- These are distinct from the 69 import/configuration errors

### 8. Address AI Assistant API security review
**Impact:** Security hardening
**Effort:** 30 minutes
**Status:** Not started

Security scan flagged 4 AI Assistant endpoints needing review:
- `ai_assistant_api`
- `ai_assistant_suggestions_api`
- `ai_assistant_feedback_api`
- `ai_assistant_analytics_api`

Currently have `@api_login_required` but may need additional permission checks (`is_management`, etc.).

### 9. Install optional WeasyPrint for PDF export
**Impact:** PDF export functionality
**Effort:** 10 minutes
**Status:** Not started

WeasyPrint module missing (warnings in makemigrations output). Optional dependency for PDF report generation in `views_cost_analysis.py`. Install if PDF export functionality needed.

### 10. Run full test suite after fixes
**Impact:** Validation
**Effort:** 15 minutes
**Status:** Not started

After completing items 1-2, re-run pytest to validate improvements. Expected:
- 230-250 passing tests (80-87%)
- <20 errors
- Similar failures

Document final production readiness percentage.

---

## Current Status Summary

**Test Suite:** 286 total tests
- ✅ 190 passing (66.4%)
- ❌ 8 failures (2.8%)
- ⚠️ 69 errors (24.1%)
- ⏭️ 16 skipped (5.6%)

**URL Infrastructure:** ✅ 100% (Tasks 55, 56, 59 wired)

**Backup Status:** ✅ All 4 locations synced to commit de997e3

**Academic Paper:** ✅ Current in both MD and RTF formats

**Estimated Impact of Items 1-3:**
- Could improve passing rate from 66.4% → 80%+
- Reduce errors from 69 → ~25
- Clear production readiness documentation
