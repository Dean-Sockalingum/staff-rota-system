# Checkpoint — Jan 30, 2026 (Deploy Env + Host Alignment)

Summary:
- Added WSGI startup log to emit key settings (DEBUG, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS) at service initialization for easier verification in production logs.
- Guided creation of systemd override to enforce environment:
  - DJANGO_SETTINGS_MODULE=rotasystems.settings
  - ALLOWED_HOSTS=therota.co.uk,www.therota.co.uk,demo.therota.co.uk,localhost,127.0.0.1,192.168.1.125
  - CSRF_TRUSTED_ORIGINS=https://therota.co.uk,https://www.therota.co.uk,https://demo.therota.co.uk
- Restarted service and verified environment via `systemctl show` and `manage.py` prints (on server).
- Retested via UNIX socket and Cloudflare path; working towards eliminating DisallowedHost for www.

Next Morning Tasks:
1) Verify startup log entries in /var/log/rota/django.log right after restart.
2) Re-run direct origin tests:
   - UNIX socket: `curl -s --unix-socket /home/staff-rota-system/staffrota.sock http://localhost/login/ -H "Host: www.therota.co.uk" -I`
   - Origin bypass: `curl -I https://www.therota.co.uk --resolve www.therota.co.uk:443:<ORIGIN_IP>`
3) If DisallowedHost persists, compare service WorkingDirectory to the folder containing patched settings (ensure REQUIRED_HOSTS/REQUIRED_CSRF_ORIGINS present in active settings).
4) If origin is clean but Cloudflare still 400, purge Cloudflare cache or enable dev mode briefly and retest.

Artifacts:
- File updated: rotasystems/wsgi.py
- Log target: /var/log/rota/django.log (and gunicorn stdout if logging misconfigured)

Safe Rollback:
- Remove the new WSGI logging block if needed; no behavior change to app runtime.
