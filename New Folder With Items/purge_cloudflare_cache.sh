#!/bin/bash
# Purge Cloudflare cache for the rota system

# Cloudflare API credentials (you need to fill these in)
CLOUDFLARE_ZONE_ID=""  # Your Cloudflare Zone ID
CLOUDFLARE_API_TOKEN=""  # Your Cloudflare API Token with Cache Purge permission

echo "=== Cloudflare Cache Purge Tool ==="
echo ""

if [ -z "$CLOUDFLARE_ZONE_ID" ] || [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo "ERROR: Cloudflare credentials not configured!"
    echo ""
    echo "To purge Cloudflare cache manually:"
    echo "1. Log in to Cloudflare Dashboard: https://dash.cloudflare.com"
    echo "2. Select your domain (therota.co.uk)"
    echo "3. Go to Caching > Configuration"
    echo "4. Click 'Purge Everything' button"
    echo ""
    echo "OR purge specific URLs:"
    echo "1. Go to Caching > Configuration"
    echo "2. Click 'Custom Purge'"
    echo "3. Add these URLs:"
    echo "   - https://demo.therota.co.uk/rota/"
    echo "   - https://demo.therota.co.uk/manager-dashboard/"
    echo "4. Click 'Purge'"
    exit 1
fi

# Purge entire cache for the zone
echo "Purging all Cloudflare cache for demo.therota.co.uk..."
curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
     -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
     -H "Content-Type: application/json" \
     --data '{"purge_everything":true}'

echo ""
echo "Cache purge request sent!"
echo ""
echo "Next steps:"
echo "1. Wait 30 seconds for cache to clear"
echo "2. Hard refresh your browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)"
echo "3. Test the rota view"
