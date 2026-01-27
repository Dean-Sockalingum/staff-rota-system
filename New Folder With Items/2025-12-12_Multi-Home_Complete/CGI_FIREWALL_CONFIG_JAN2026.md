# CGI Firewall & Network Configuration
## NHS Staff Rota Management System
**Version:** 1.0  
**Date:** January 7, 2026  
**Classification:** OFFICIAL-SENSITIVE

---

## 1. Executive Summary

**Purpose:** Define firewall rules, network segmentation, and VPN access for NHS Staff Rota System deployment in CGI Azure environment.

**Network Architecture:**
- **DMZ Placement:** Application tier in CGI DMZ (public internet → Azure App Gateway → Django app)
- **Database Tier:** Private subnet (no direct internet access, internal only)
- **Management Access:** VPN-only for HSCP IT staff and CGI support

**Key Security Controls:**
- Zero Trust network model (least privilege access)
- WAF (Web Application Firewall) on Azure Application Gateway
- Network Security Groups (NSGs) for micro-segmentation
- Site-to-Site VPN for HSCP office connectivity
- Point-to-Site VPN for remote CGI engineers

---

## 2. Network Architecture

### 2.1 Security Zones

```
┌─────────────────────────────────────────────────────────────────┐
│ INTERNET (Untrusted Zone)                                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                 ┌───────────▼──────────┐
                 │  Azure Front Door    │
                 │  + DDoS Protection   │
                 └───────────┬──────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│ PUBLIC DMZ (10.100.1.0/24)                                      │
│  ┌─────────────────────────────────────────────────┐            │
│  │ Azure Application Gateway + WAF                 │            │
│  │ - TLS termination                               │            │
│  │ - OWASP Top 10 protection                       │            │
│  │ - Rate limiting: 100 req/sec/IP                 │            │
│  └──────────────────┬──────────────────────────────┘            │
└─────────────────────┴─────────────────────────────────────────┬─┘
                      │                                         │
        ┌─────────────▼───────────┐          ┌─────────────────▼──────┐
        │ PRIVATE DMZ             │          │ MANAGEMENT VPN SUBNET  │
        │ (10.100.10.0/24)        │          │ (10.100.254.0/24)      │
        │                         │          │                        │
        │ Azure App Service:      │          │ VPN Gateway:           │
        │ - Django application    │          │ - Site-to-Site (HSCP)  │
        │ - 2 instances (HA)      │          │ - Point-to-Site (CGI)  │
        │ - Outbound: Azure       │          └────────────────────────┘
        │   services only         │                                   
        └────────┬────────────────┘                                   
                 │                                                     
    ┌────────────▼─────────────┐                                     
    │ DATA TIER (10.100.20.0/24)                                     
    │                                                                
    │ PostgreSQL Servers:                                            
    │ - Primary DB (UK South)                                        
    │ - Hot Standby (UK South)                                       
    │ - Warm Standby (UK West)                                       
    │                                                                
    │ Access:                                                        
    │ - App tier ONLY (port 5432)                                   
    │ - VPN for admin (SSH/5432)                                    
    │ - Replication between DCs                                     
    └────────────────────────────┘                                   
```

### 2.2 IP Address Allocation

| Subnet | CIDR | Purpose | Hosts |
|--------|------|---------|-------|
| Public DMZ | 10.100.1.0/24 | App Gateway, Load Balancers | 254 |
| Private DMZ | 10.100.10.0/24 | Application servers | 254 |
| Database Tier | 10.100.20.0/24 | PostgreSQL cluster | 254 |
| Redis/Cache | 10.100.30.0/24 | Redis cluster, session cache | 254 |
| Management | 10.100.254.0/24 | VPN gateway, jump boxes | 254 |
| DR Site (UK West) | 10.101.0.0/16 | Mirror of UK South subnets | 65,534 |

---

## 3. Firewall Rules

### 3.1 Inbound Rules (Internet → DMZ)

| Priority | Name | Source | Destination | Protocol | Port | Action | Justification |
|----------|------|--------|-------------|----------|------|--------|---------------|
| 100 | HTTPS-Public | 0.0.0.0/0 | App Gateway Public IP | TCP | 443 | Allow | User access to web app |
| 110 | HTTP-Redirect | 0.0.0.0/0 | App Gateway Public IP | TCP | 80 | Allow | HTTP→HTTPS redirect |
| 900 | Deny-All-Inbound | 0.0.0.0/0 | 10.100.0.0/16 | Any | Any | Deny | Default deny |

**Notes:**
- DDoS protection enabled (Azure Front Door Standard)
- Rate limiting: 100 requests/sec per source IP (WAF policy)
- Geographic restrictions: UK, EU only (block all other regions)

### 3.2 Private DMZ → Data Tier

| Priority | Name | Source | Destination | Protocol | Port | Action | Justification |
|----------|------|--------|-------------|----------|------|--------|---------------|
| 200 | App-to-DB-Primary | 10.100.10.0/24 | 10.100.20.10/32 | TCP | 5432 | Allow | Django → PostgreSQL primary |
| 210 | App-to-DB-Standby | 10.100.10.0/24 | 10.100.20.11/32 | TCP | 5432 | Allow | Failover to hot standby |
| 220 | App-to-Redis | 10.100.10.0/24 | 10.100.30.0/24 | TCP | 6379 | Allow | Session cache, Celery |
| 900 | Deny-All | 10.100.10.0/24 | Any | Any | Any | Deny | Least privilege |

### 3.3 Database Replication (Primary ↔ Standby)

| Priority | Name | Source | Destination | Protocol | Port | Action | Justification |
|----------|------|--------|-------------|----------|------|--------|---------------|
| 300 | DB-Replication-Primary-Hot | 10.100.20.10/32 | 10.100.20.11/32 | TCP | 5432 | Allow | WAL streaming (hot standby) |
| 310 | DB-Replication-Primary-Warm | 10.100.20.10/32 | 10.101.20.10/32 | TCP | 5432 | Allow | WAL streaming (DR site) |
| 320 | DB-Replication-Reverse | 10.100.20.11/32, 10.101.20.10/32 | 10.100.20.10/32 | TCP | 5432 | Allow | Health checks, failback |

**Replication Traffic:** Encrypted with PostgreSQL SSL (TLS 1.3)

### 3.4 Management Access (VPN → Internal)

| Priority | Name | Source | Destination | Protocol | Port | Action | Justification |
|----------|------|--------|-------------|----------|------|--------|---------------|
| 400 | VPN-SSH-Servers | 10.100.254.0/24 | 10.100.10.0/24, 10.100.20.0/24 | TCP | 22 | Allow | Server management |
| 410 | VPN-PostgreSQL-Admin | 10.100.254.0/24 | 10.100.20.0/24 | TCP | 5432 | Allow | DB admin tasks |
| 420 | VPN-HTTPS-Admin | 10.100.254.0/24 | 10.100.10.0/24 | TCP | 443 | Allow | Django admin interface |
| 430 | VPN-Monitoring | 10.100.254.0/24 | 10.100.0.0/16 | TCP | 9090, 9100, 3000 | Allow | Prometheus, Grafana |
| 900 | Deny-All-VPN | 10.100.254.0/24 | Any | Any | Any | Deny | Least privilege |

### 3.5 Outbound Rules (DMZ → Internet)

| Priority | Name | Source | Destination | Protocol | Port | Action | Justification |
|----------|------|--------|-------------|----------|------|--------|---------------|
| 500 | Azure-Services | 10.100.10.0/24 | AzureCloud.UKSouth | TCP | 443 | Allow | Azure Monitor, KeyVault, Blob |
| 510 | NTP-Time-Sync | 10.100.0.0/16 | 0.0.0.0/0 | UDP | 123 | Allow | Time synchronization |
| 520 | DNS-Resolution | 10.100.0.0/16 | 168.63.129.16/32 | UDP | 53 | Allow | Azure DNS |
| 530 | LDAP-CGI-AD | 10.100.10.0/24 | 10.200.0.10/32 | TCP | 389, 636 | Allow | CGI Active Directory |
| 540 | SAML-CGI-IdP | 10.100.10.0/24 | 10.200.0.20/32 | TCP | 443 | Allow | CGI SSO portal |
| 550 | SIEM-Splunk | 10.100.0.0/16 | 10.200.1.0/24 | TCP | 514, 8088 | Allow | CGI SIEM/SOC |
| 560 | Email-SMTP | 10.100.10.0/24 | 10.200.2.10/32 | TCP | 25, 587 | Allow | CGI mail relay |
| 900 | Deny-All-Outbound | 10.100.0.0/16 | 0.0.0.0/0 | Any | Any | Deny | Default deny |

**Note:** Replace `10.200.x.x` with actual CGI internal service IPs (to be provided by CGI networking team).

---

## 4. VPN Configuration

### 4.1 Site-to-Site VPN (HSCP Office → Azure)

**Purpose:** Connect HSCP IT office to Azure VNet for admin access

**Configuration:**
```yaml
VPN Type: Route-based (IKEv2)
Encryption: AES-256-GCM
Authentication: Pre-shared key (32-char minimum)
DH Group: DHGroup24 (2048-bit MODP)
Lifetime: 
  - Phase 1 (IKE): 28,800 seconds (8 hours)
  - Phase 2 (IPsec): 3,600 seconds (1 hour)
PFS: Enabled (DHGroup24)
Dead Peer Detection: 30 seconds

HSCP On-Premises:
  Public IP: [To be provided by HSCP]
  Local Subnet: 192.168.1.0/24
  VPN Device: Cisco ASA 5516-X or equivalent

Azure Side:
  Gateway: VpnGw2 SKU (supports 10 tunnels)
  Public IP: [Provisioned by CGI]
  Local Network Gateway: 10.100.0.0/16
```

**Routing:**
- Azure advertises: 10.100.0.0/16 (all internal subnets)
- HSCP advertises: 192.168.1.0/24 (office network)
- BGP: Not required (static routes)

### 4.2 Point-to-Site VPN (CGI Engineers)

**Purpose:** Remote access for CGI support engineers (24/7 P1/P2 support per SLA)

**Configuration:**
```yaml
VPN Type: OpenVPN (SSL-based)
Authentication: Azure AD + MFA mandatory
Client Certificate: Required (CGI PKI)
Address Pool: 10.100.254.128/25 (126 clients)
DNS Servers: 168.63.129.16 (Azure DNS)

Protocols:
  - OpenVPN (UDP 1194) - Primary
  - SSTP (TCP 443) - Fallback

Client Requirements:
  - Azure VPN Client (Windows/macOS/Linux)
  - CGI corporate device (MDM-enrolled)
  - MFA app (Microsoft Authenticator)
```

**Access Control:**
- Require Azure AD group membership: `CGI-NHS-Rota-Support`
- Session timeout: 8 hours (re-authenticate daily)
- Concurrent connections: Max 50 engineers
- Audit logging: All VPN sessions logged to SIEM

### 4.3 VPN Failover

**Primary Gateway:** UK South (vpn-gateway-uksouth-01)  
**Secondary Gateway:** UK West (vpn-gateway-ukwest-01)  
**Failover:** Automatic (120-second BGP convergence)

---

## 5. Network Security Groups (NSGs)

### 5.1 NSG: App-Tier-NSG

**Applied to:** Private DMZ subnet (10.100.10.0/24)

| Priority | Name | Direction | Source | Destination | Protocol | Port | Action |
|----------|------|-----------|--------|-------------|----------|------|--------|
| 100 | Allow-App-Gateway | Inbound | 10.100.1.0/24 | 10.100.10.0/24 | TCP | 443, 8000 | Allow |
| 200 | Allow-VPN-SSH | Inbound | 10.100.254.0/24 | 10.100.10.0/24 | TCP | 22 | Allow |
| 210 | Allow-VPN-HTTPS | Inbound | 10.100.254.0/24 | 10.100.10.0/24 | TCP | 443 | Allow |
| 300 | Allow-DB-Response | Inbound | 10.100.20.0/24 | 10.100.10.0/24 | TCP | 1024-65535 | Allow |
| 900 | Deny-All-Inbound | Inbound | Any | Any | Any | Any | Deny |
| 1000 | Allow-DB-Access | Outbound | 10.100.10.0/24 | 10.100.20.0/24 | TCP | 5432 | Allow |
| 1010 | Allow-Redis | Outbound | 10.100.10.0/24 | 10.100.30.0/24 | TCP | 6379 | Allow |
| 1020 | Allow-Azure-Services | Outbound | 10.100.10.0/24 | AzureCloud | TCP | 443 | Allow |
| 1030 | Allow-CGI-Services | Outbound | 10.100.10.0/24 | 10.200.0.0/16 | TCP | 389, 443, 514, 8088 | Allow |
| 4000 | Deny-All-Outbound | Outbound | Any | Any | Any | Any | Deny |

### 5.2 NSG: Database-Tier-NSG

**Applied to:** Database subnet (10.100.20.0/24)

| Priority | Name | Direction | Source | Destination | Protocol | Port | Action |
|----------|------|-----------|--------|-------------|----------|------|--------|
| 100 | Allow-App-Tier | Inbound | 10.100.10.0/24 | 10.100.20.0/24 | TCP | 5432 | Allow |
| 110 | Allow-DB-Replication | Inbound | 10.100.20.0/24, 10.101.20.0/24 | 10.100.20.0/24 | TCP | 5432 | Allow |
| 120 | Allow-VPN-Admin | Inbound | 10.100.254.0/24 | 10.100.20.0/24 | TCP | 22, 5432 | Allow |
| 900 | Deny-All-Inbound | Inbound | Any | Any | Any | Any | Deny |
| 1000 | Allow-Replication-Out | Outbound | 10.100.20.0/24 | 10.100.20.0/24, 10.101.20.0/24 | TCP | 5432 | Allow |
| 1010 | Allow-Monitoring | Outbound | 10.100.20.0/24 | 10.100.254.0/24 | TCP | 9100 | Allow |
| 4000 | Deny-All-Outbound | Outbound | Any | Any | Any | Any | Deny |

---

## 6. Web Application Firewall (WAF)

### 6.1 WAF Policy

**Provider:** Azure Application Gateway WAF v2  
**Rule Set:** OWASP ModSecurity Core Rule Set 3.2  
**Mode:** Prevention (block malicious requests)

**Custom Rules:**

| Priority | Name | Condition | Action | Justification |
|----------|------|-----------|--------|---------------|
| 10 | Rate-Limit-Global | Request count > 100/min per IP | Block (429) | DDoS protection |
| 20 | Rate-Limit-Login | POST to /login > 5/min per IP | Block (429) | Brute force protection |
| 30 | GeoBlock-Non-UK-EU | Country not in [UK, EU] | Block (403) | Reduce attack surface |
| 40 | Block-Suspicious-UA | User-Agent matches bot patterns | Block (403) | Scanner detection |
| 50 | Allow-Monitoring-Probe | Source IP = 10.100.254.0/24 | Allow | Health checks bypass WAF |

**OWASP Top 10 Protection:**
- SQL Injection (Score threshold: 5)
- Cross-Site Scripting (XSS)
- Local File Inclusion (LFI)
- Remote File Inclusion (RFI)
- Remote Code Execution (RCE)
- Protocol anomalies
- Session fixation

**Logging:** All blocked requests logged to Azure Log Analytics (90-day retention) + forwarded to CGI SIEM

---

## 7. DDoS Protection

**Tier:** Azure DDoS Protection Standard  
**Coverage:** All public IPs (App Gateway, VPN Gateway)

**Protection Levels:**
- **Volumetric attacks:** Up to 2 Tbps mitigation
- **Protocol attacks:** SYN flood, UDP flood, ACK flood
- **Application attacks:** HTTP flood, Slowloris (mitigated by WAF)

**Telemetry:**
- Real-time metrics in Azure Monitor
- Attack alerts via email/SMS (P1 escalation)
- Post-attack reports (48-hour SLA)

---

## 8. DNS Configuration

### 8.1 Public DNS (External Users)

**Primary Domain:** `nhs-rota.hscp.scot.nhs.uk`  
**DNS Provider:** NHS Digital DNS (delegated to CGI)  
**TTL:** 300 seconds (5 minutes for quick failover)

**Records:**
```
nhs-rota.hscp.scot.nhs.uk.          A      51.xxx.xxx.xxx  (App Gateway Public IP)
www.nhs-rota.hscp.scot.nhs.uk.     CNAME  nhs-rota.hscp.scot.nhs.uk.
*.nhs-rota.hscp.scot.nhs.uk.       CNAME  nhs-rota.hscp.scot.nhs.uk.

;; DR Failover (manual DNS update)
nhs-rota.hscp.scot.nhs.uk.          A      51.yyy.yyy.yyy  (UK West App Gateway)
```

**Health Checks:**
- Endpoint: `https://nhs-rota.hscp.scot.nhs.uk/health/`
- Interval: 30 seconds
- Timeout: 10 seconds
- Unhealthy threshold: 3 consecutive failures
- Auto-failover: DNS updated by Azure Traffic Manager

### 8.2 Internal DNS (Private Zone)

**Zone:** `nhs-rota.internal.cgi.com`  
**Linked VNets:** UK South VNet, UK West VNet  
**Auto-registration:** Enabled for all VMs

**Records:**
```
db-primary.nhs-rota.internal.cgi.com.        A  10.100.20.10
db-hot-standby.nhs-rota.internal.cgi.com.    A  10.100.20.11
db-warm-standby.nhs-rota.internal.cgi.com.   A  10.101.20.10
redis-primary.nhs-rota.internal.cgi.com.     A  10.100.30.10
redis-replica.nhs-rota.internal.cgi.com.     A  10.100.30.11
```

---

## 9. SSL/TLS Configuration

### 9.1 Certificates

**Public Certificate:** NHS Digital Managed Certificate (DigiCert)  
**Validity:** 397 days (renewed annually)  
**SAN (Subject Alternative Names):**
- `nhs-rota.hscp.scot.nhs.uk`
- `www.nhs-rota.hscp.scot.nhs.uk`
- `*.nhs-rota.hscp.scot.nhs.uk`

**Private Certificate (Internal):** CGI PKI  
**Purpose:** Database replication, internal service communication

### 9.2 TLS Policy

**Protocol:** TLS 1.3 only (TLS 1.2 disabled from Feb 2026)  
**Cipher Suites (Ordered by preference):**
1. TLS_AES_256_GCM_SHA384
2. TLS_CHACHA20_POLY1305_SHA256
3. TLS_AES_128_GCM_SHA256

**Disabled:**
- TLS 1.0, 1.1 (deprecated)
- TLS 1.2 (phase-out Feb 2026 per NHS policy)
- 3DES, RC4, MD5 ciphers
- NULL ciphers

**HSTS (HTTP Strict Transport Security):**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Certificate Pinning:** Enabled for mobile clients (if developed)

---

## 10. Monitoring & Logging

### 10.1 Network Logs

**Log Sources:**
| Source | Log Type | Retention | Destination |
|--------|----------|-----------|-------------|
| NSG Flow Logs | Traffic flows (5-tuple) | 90 days | Azure Storage + SIEM |
| Application Gateway | Access logs, WAF logs | 90 days | Log Analytics + SIEM |
| VPN Gateway | Connection logs, metrics | 90 days | Log Analytics + SIEM |
| Azure Firewall | Threat intelligence, rules | 90 days | Log Analytics + SIEM |
| DNS Queries | Query logs (private zone) | 30 days | Log Analytics |

### 10.2 Alerts

**Critical Alerts (P1 - 15min response):**
- VPN tunnel down
- Database replication lag >30 seconds
- WAF blocking spike (>100 requests/min)
- DDoS attack detected
- NSG rule changes (audit)

**High Alerts (P2 - 1hr response):**
- VPN connection failures >10/hour
- SSL certificate expiry <30 days
- Unusual traffic patterns (ML-based)
- Failed login attempts >50/hour

**Notification:** Email + SMS + PagerDuty (per SLA)

---

## 11. Implementation Checklist

### Phase 1: CGI Infrastructure Provisioning (Week 1)
- [ ] Provision Azure VNet (UK South + UK West)
- [ ] Create subnets with NSGs
- [ ] Deploy VPN gateways
- [ ] Configure private DNS zone
- [ ] Obtain SSL certificates (NHS Digital)

### Phase 2: Firewall Rules (Week 2)
- [ ] Configure NSG rules (App, DB, Management tiers)
- [ ] Deploy Azure Application Gateway + WAF
- [ ] Configure DDoS Protection Standard
- [ ] Set up route tables (user-defined routes)
- [ ] Enable NSG flow logs

### Phase 3: VPN Configuration (Week 3)
- [ ] Configure Site-to-Site VPN (HSCP office)
  - Coordinate with HSCP IT for on-prem VPN device config
  - Test connectivity, validate routing
- [ ] Configure Point-to-Site VPN (CGI engineers)
  - Create Azure AD group, assign users
  - Distribute VPN client profiles
- [ ] Test failover scenarios

### Phase 4: Testing & Validation (Week 4)
- [ ] Penetration test (external consultant)
- [ ] Load testing (500 concurrent users)
- [ ] Failover testing (VPN, database, app tier)
- [ ] DR drill (30-minute RTO target)
- [ ] Security audit (CGI InfoSec team)

### Phase 5: Production Cutover
- [ ] Update DNS records (5-minute TTL)
- [ ] Enable monitoring/alerting
- [ ] Handover to CGI NOC (24/7 monitoring)
- [ ] Document as-built configuration

---

## 12. CGI Coordination Requirements

### 12.1 Information Needed from CGI

| Item | Description | ETA |
|------|-------------|-----|
| CGI LDAP Server IPs | Active Directory server addresses | Week 1 |
| CGI SAML IdP Endpoint | SSO portal URL + IP | Week 1 |
| CGI SIEM Endpoints | Splunk receiver IPs + ports | Week 1 |
| CGI Mail Relay | SMTP server IP + port | Week 1 |
| VPN Gateway Public IPs | Azure VPN gateway addresses (provisioned by CGI) | Week 1 |
| Network IP Ranges | Confirm 10.100.0.0/16 doesn't conflict with CGI internal | Week 1 |
| PKI Certificates | CGI-signed certs for internal communication | Week 2 |
| Monitoring Integration | Azure Monitor workspace, SIEM onboarding | Week 2 |

### 12.2 HSCP Coordination

| Item | Description | ETA |
|------|-------------|-----|
| Office Public IP | HSCP office internet-facing IP for VPN | Week 2 |
| VPN Device Details | On-prem firewall/VPN model + version | Week 2 |
| Admin Contact List | IT staff requiring VPN access (names + emails) | Week 2 |
| Change Approval | HSCP CAB approval for VPN connection | Week 2 |

---

## 13. Security Hardening

### 13.1 Defense in Depth

**Layer 1: Internet Edge**
- Azure Front Door DDoS protection
- Geographic restrictions (UK/EU only)
- Rate limiting (WAF)

**Layer 2: Perimeter**
- Application Gateway WAF (OWASP rules)
- TLS 1.3 termination
- Bot detection

**Layer 3: Network**
- NSGs (micro-segmentation)
- Zero Trust (deny-all default)
- VPN-only admin access

**Layer 4: Application**
- Django authentication (@api_login_required)
- LDAP/SAML SSO
- Session management (Redis)

**Layer 5: Data**
- PostgreSQL SSL connections
- Encryption at rest (AES-256)
- PITR backups (immutable)

### 13.2 Compliance Controls

**NHS Data Security & Protection Toolkit:**
- ✅ Network segmentation (Requirement 6.2)
- ✅ Encryption in transit (Requirement 7.1)
- ✅ Access control (VPN + MFA) (Requirement 5.1)
- ✅ Audit logging (Requirement 8.1)

**Cyber Essentials Plus:**
- ✅ Firewall configuration
- ✅ Secure configuration (TLS 1.3)
- ✅ User access control (VPN + AAD)
- ✅ Malware protection (WAF)
- ✅ Patch management (Azure auto-update)

---

## 14. Troubleshooting

### Issue: VPN Connection Fails

**Symptoms:** Cannot connect to Point-to-Site VPN

**Diagnosis:**
```bash
# Test VPN gateway reachability
ping vpn-gateway-uksouth-01.azurevpngw.net

# Check Azure AD auth
az login
az account show

# Verify client certificate
certutil -store -user My | findstr "CGI"
```

**Resolution:**
1. Verify Azure AD group membership (`CGI-NHS-Rota-Support`)
2. Check MFA enrollment (Microsoft Authenticator)
3. Re-download VPN profile from Azure Portal
4. Contact CGI helpdesk if persistent (P2 incident)

### Issue: Database Connection Timeout

**Symptoms:** Django app cannot connect to PostgreSQL

**Diagnosis:**
```python
# Test from app server
telnet 10.100.20.10 5432

# Check NSG rules
az network nsg rule list --resource-group rg-nhs-rota-prod --nsg-name App-Tier-NSG

# Verify DNS resolution
nslookup db-primary.nhs-rota.internal.cgi.com
```

**Resolution:**
1. Confirm NSG allows 10.100.10.0/24 → 10.100.20.0/24 TCP/5432
2. Check PostgreSQL pg_hba.conf (allow app subnet)
3. Verify SSL certificate (Django DATABASE_OPTIONS)
4. Review PostgreSQL logs for connection errors

### Issue: WAF Blocking Legitimate Requests

**Symptoms:** Users receiving 403 Forbidden errors

**Diagnosis:**
```bash
# Check WAF logs (last 1 hour)
az monitor log-analytics query \
  --workspace cgi-nhs-rota-logs \
  --analytics-query "AzureDiagnostics | where Category == 'ApplicationGatewayFirewallLog' | where TimeGenerated > ago(1h)"
```

**Resolution:**
1. Identify false positive rule (OWASP CRS ID in logs)
2. Create WAF exception for specific URL pattern
3. Test with user to confirm resolution
4. Document exception in change log

---

## 15. Cost Estimation

| Component | SKU | Monthly Cost (£) | Annual Cost (£) |
|-----------|-----|------------------|-----------------|
| VPN Gateway | VpnGw2 | £220 | £2,640 |
| Application Gateway v2 | Standard_v2 (2 instances) | £180 | £2,160 |
| DDoS Protection Standard | Standard | £2,200 | £26,400 |
| NSG Flow Logs | Storage (90 days, 100GB) | £3 | £36 |
| Log Analytics | 10GB ingestion/day | £150 | £1,800 |
| **Total Network Costs** | | **£2,753** | **£33,036** |

**Note:** Excludes compute (App Service, PostgreSQL) and bandwidth costs (covered in SLA budget).

---

## 16. Next Steps

**Immediate Actions (Week 1):**
1. CGI provision Azure VNet and subnets
2. HSCP provide office public IP for VPN
3. CGI InfoSec review and approve firewall rules
4. Obtain NHS Digital SSL certificate

**Week 2-3:**
5. Configure VPN gateways (Site-to-Site + Point-to-Site)
6. Deploy Application Gateway + WAF
7. Test HSCP office connectivity
8. CGI engineer VPN access validation

**Week 4 (Go-Live):**
9. Production cutover (DNS update)
10. Enable 24/7 monitoring (CGI NOC)
11. Handover to BAU support team

---

**Document Owner:** CGI Network Engineering Team  
**Approvers:** HSCP IT Manager, CGI Service Manager  
**Review Cycle:** Quarterly (or after security incidents)
