#!/usr/bin/env python3

with open("/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/base.html", "r") as f:
    content = f.read()

# Add cache busting script before </body>
if "CACHE BUSTER" not in content:
    cache_bust_script = """
    <script>
    // CACHE BUSTER - Force reload on back/forward navigation
    (function() {
        window.addEventListener('pageshow', function(event) {
            if (event.persisted) {
                console.log('Page loaded from bfcache - reloading');
                window.location.reload();
            }
        });
        
        // Prevent caching on navigation
        window.addEventListener('beforeunload', function() {
            window.onpageshow = function(event) {
                if (event.persisted) {
                    window.location.reload();
                }
            };
        });
    })();
    </script>
</body>"""
    
    content = content.replace("</body>", cache_bust_script)
    print("Added cache busting JavaScript")
    
    with open("/home/staff-rota-system/2025-12-12_Multi-Home_Complete/scheduling/templates/scheduling/base.html", "w") as f:
        f.write(content)
else:
    print("Cache buster already present")
