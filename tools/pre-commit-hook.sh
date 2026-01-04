#!/bin/sh
#
# Pre-commit hook to check API authentication decorators
# Install: cp tools/pre-commit-hook.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
#

echo "🔍 Checking API authentication decorators..."

# Run the checker in strict mode
python3 tools/check_api_decorators.py --strict

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ API decorator check failed!"
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

echo "✅ All API endpoints are properly secured!"
exit 0
