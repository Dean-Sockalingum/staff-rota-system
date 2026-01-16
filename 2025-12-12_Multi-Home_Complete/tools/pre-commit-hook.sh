#!/bin/sh
#
# Pre-commit hook to check API security (authentication + authorization)
# Install: cp tools/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#

echo "🔍 Running API security checks..."
echo ""

# Phase 2: Check authentication decorators
echo "Phase 2: Authentication..."
python3 tools/check_api_decorators.py --strict

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ API authentication check failed!"
    echo "   Some API endpoints are missing @api_login_required decorator."
    echo ""
    echo "   Options:"
    echo "   1. Run: python3 tools/check_api_decorators.py --fix"
    echo "   2. Manually add @api_login_required to missing endpoints"
    echo "   3. If this is an external integration API, update the checker whitelist"
    echo ""
    echo "   To bypass this check (not recommended): git commit --no-verify"
    exit 1
fi

echo "✅ Authentication check passed"
echo ""

# Phase 3: Check authorization/permissions (advisory only, doesn't block)
echo "Phase 3: Authorization..."
python3 tools/check_api_permissions.py

# Note: Permission check is advisory - we don't fail the commit
# This helps developers be aware of potential authorization gaps
echo ""
echo "✅ All security checks complete!"
exit 0
