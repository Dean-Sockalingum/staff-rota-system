#!/bin/bash
# Verify cache-prevention headers are being sent

echo "=== Cache Header Verification Tool ==="
echo ""
echo "Checking cache-control headers for demo.therota.co.uk..."
echo ""

echo "1. Testing /rota/ endpoint:"
echo "----------------------------"
curl -I -s https://demo.therota.co.uk/rota/ | grep -i -E "(cache|pragma|expires)"
echo ""

echo "2. Testing /manager-dashboard/ endpoint:"
echo "-----------------------------------------"
curl -I -s https://demo.therota.co.uk/manager-dashboard/ | grep -i -E "(cache|pragma|expires)"
echo ""

echo "3. Full headers for /rota/:"
echo "---------------------------"
curl -I -s https://demo.therota.co.uk/rota/
echo ""

echo "=== Analysis ==="
echo ""
echo "✅ GOOD SIGNS:"
echo "  - Cache-Control: no-cache, no-store, must-revalidate, max-age=0"
echo "  - Pragma: no-cache"
echo "  - Expires: 0"
echo ""
echo "❌ BAD SIGNS:"
echo "  - Cache-Control: public, max-age=3600"
echo "  - No Cache-Control header"
echo "  - cf-cache-status: HIT (Cloudflare is caching)"
echo ""
echo "If you see 'cf-cache-status: HIT', Cloudflare is still caching."
echo "Solution: Purge Cloudflare cache and set up Page Rules"
