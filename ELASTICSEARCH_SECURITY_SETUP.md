# Elasticsearch Security Configuration Guide
**Created:** January 8, 2026  
**Priority:** Critical (Security)

## Current Status
⚠️ **WARNING**: Elasticsearch is currently running WITHOUT authentication enabled!

```
WARNING: Elasticsearch built-in security features are not enabled.
Without authentication, your cluster could be accessible to anyone.
```

## Quick Fix for Development/Demo

### Option 1: Enable Basic Authentication (Recommended)

1. **Edit Elasticsearch configuration** (`/etc/elasticsearch/elasticsearch.yml` or `config/elasticsearch.yml`):

```yaml
# Enable X-Pack security
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true

# Network settings
network.host: localhost
http.port: 9200
```

2. **Set built-in user passwords**:

```bash
# For Elasticsearch 8.x+
cd /usr/share/elasticsearch/bin
./elasticsearch-setup-passwords interactive

# Or auto-generate passwords:
./elasticsearch-setup-passwords auto
```

3. **Create dedicated user for the application**:

```bash
# Using Elasticsearch API (after setting up superuser password)
curl -X POST "localhost:9200/_security/user/rota_search" \
  -u elastic:YOUR_ELASTIC_PASSWORD \
  -H 'Content-Type: application/json' \
  -d '{
    "password" : "SECURE_PASSWORD_HERE",
    "roles" : [ "superuser" ],
    "full_name" : "Rota Search User"
  }'
```

4. **Update `.env.production`**:

Already configured in `.env.production`:
```bash
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_USER=rota_search
ELASTICSEARCH_PASSWORD=SECURE_PASSWORD_HERE
```

### Option 2: Bind to localhost only (Less Secure)

If you're only running Elasticsearch locally for development:

1. **Edit Elasticsearch config**:
```yaml
network.host: 127.0.0.1
```

2. **Restart Elasticsearch**:
```bash
# macOS (Homebrew)
brew services restart elasticsearch

# Linux (systemd)
sudo systemctl restart elasticsearch

# Linux (service)
sudo service elasticsearch restart
```

## Testing Elasticsearch Connection

### Without Authentication (Current State):
```bash
curl http://localhost:9200
```

### With Authentication:
```bash
curl -u rota_search:YOUR_PASSWORD http://localhost:9200
```

### Test from Django:
```bash
python3 manage.py shell
```
```python
from django.conf import settings
from elasticsearch import Elasticsearch

# Get credentials from settings
es_config = settings.ELASTICSEARCH_DSL['default']
print(f"ES URL: {es_config['hosts']}")
print(f"ES Auth: {es_config.get('http_auth', 'None')}")

# Test connection
es = Elasticsearch(**es_config)
print(es.info())
```

## For Production Deployment

### Enable Full Security Stack:

1. **Generate certificates for TLS**:
```bash
./bin/elasticsearch-certutil ca
./bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12
```

2. **Configure TLS in elasticsearch.yml**:
```yaml
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: elastic-certificates.p12
xpack.security.transport.ssl.truststore.path: elastic-certificates.p12

xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: elastic-certificates.p12
```

3. **Update Django settings** to use HTTPS:
```python
# In .env.production
ELASTICSEARCH_URL=https://localhost:9200
```

## Verification Checklist

- [ ] Elasticsearch requires authentication (test with: `curl http://localhost:9200`)
- [ ] Application can connect with credentials
- [ ] Search functionality works in the application
- [ ] No unauthorized access possible
- [ ] Elasticsearch bound to localhost or protected by firewall

## Quick Command Reference

```bash
# Check if Elasticsearch is running
curl http://localhost:9200

# Check Elasticsearch status with auth
curl -u username:password http://localhost:9200/_cluster/health

# View Elasticsearch logs (macOS Homebrew)
tail -f /opt/homebrew/var/log/elasticsearch.log

# View Elasticsearch logs (Linux)
sudo tail -f /var/log/elasticsearch/elasticsearch.log

# Restart Elasticsearch (macOS)
brew services restart elasticsearch

# Restart Elasticsearch (Linux)
sudo systemctl restart elasticsearch
```

## Important Notes

1. **Development vs Production**:
   - Development: Basic auth is sufficient
   - Production: Use TLS/SSL encryption + authentication

2. **Password Security**:
   - Never commit passwords to version control
   - Use strong, unique passwords
   - Store in `.env.production` (already added to .gitignore)

3. **Network Security**:
   - Bind to localhost for single-server setup
   - Use firewall rules for multi-server setup
   - Consider VPN for cross-site Elasticsearch clusters

## Next Steps

1. Choose authentication method (Option 1 recommended)
2. Configure Elasticsearch
3. Update credentials in `.env.production`
4. Test connection
5. Verify search functionality works
6. Run security check: `python3 manage.py check --deploy`
