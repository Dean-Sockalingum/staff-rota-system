# 🔐 GitHub Secrets Configuration Guide

**Quick reference for setting up GitHub Actions secrets for automated deployment.**

---

## 📍 Access GitHub Secrets

1. Go to: https://github.com/Dean-Sockalingum/staff-rota-system
2. Click **Settings** (top navigation)
3. In left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret**

---

## 🔑 Required Secrets

### Staging Environment

#### `STAGING_HOST`
**Description:** Hostname or IP address of your staging server  
**Example:**
```
staging.staffrota.example.com
```
or
```
192.168.1.100
```

---

#### `STAGING_USER`
**Description:** SSH username for deployment  
**Recommended:** Create dedicated deployment user  
**Example:**
```
deploy-user
```

**Setup on server:**
```bash
sudo useradd -m -s /bin/bash deploy-user
sudo usermod -aG www-data deploy-user
```

---

#### `STAGING_SSH_KEY`
**Description:** Private SSH key for authentication (full key including headers)

**Generate new key pair:**
```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-staging" -f ~/.ssh/github_staging

# View private key (copy this to STAGING_SSH_KEY secret)
cat ~/.ssh/github_staging

# View public key (add to server)
cat ~/.ssh/github_staging.pub
```

**Expected format:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
... (multiple lines) ...
-----END OPENSSH PRIVATE KEY-----
```

**Add public key to server:**
```bash
# SSH to your staging server
ssh your-user@staging-server

# Switch to deploy user
sudo su - deploy-user

# Add public key
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3Nza... github-actions-staging" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

**Test SSH connection:**
```bash
# From your local machine
ssh -i ~/.ssh/github_staging deploy-user@staging-server
```

---

#### `STAGING_PATH`
**Description:** Deployment directory on staging server  
**Example:**
```
/var/www/staff-rota-staging
```

**Setup on server:**
```bash
sudo mkdir -p /var/www/staff-rota-staging
sudo chown deploy-user:www-data /var/www/staff-rota-staging
```

---

#### `STAGING_URL`
**Description:** Full URL of staging environment (for smoke tests)  
**Example:**
```
https://staging.staffrota.example.com
```
or
```
http://staging.staffrota.example.com
```
*(Use http if SSL not yet configured)*

---

### Production Environment

#### `PROD_HOST`
**Description:** Production server hostname or IP  
**Example:**
```
staffrota.example.com
```

---

#### `PROD_USER`
**Description:** SSH username for production deployment  
**Example:**
```
deploy-user
```

---

#### `PROD_SSH_KEY`
**Description:** Production SSH private key

**Generate separate key for production:**
```bash
ssh-keygen -t ed25519 -C "github-actions-production" -f ~/.ssh/github_production
cat ~/.ssh/github_production  # Copy to PROD_SSH_KEY
cat ~/.ssh/github_production.pub  # Add to production server
```

⚠️ **Use different SSH keys for staging and production!**

---

#### `PROD_PATH`
**Description:** Production deployment directory  
**Example:**
```
/var/www/staff-rota-production
```

---

#### `PROD_URL`
**Description:** Production URL  
**Example:**
```
https://staffrota.example.com
```

---

## ✅ Verification Checklist

After adding all secrets:

### Staging Secrets
- [ ] `STAGING_HOST` - Server hostname/IP
- [ ] `STAGING_USER` - SSH username (deploy-user)
- [ ] `STAGING_SSH_KEY` - Complete private key with headers
- [ ] `STAGING_PATH` - Deployment directory (/var/www/staff-rota-staging)
- [ ] `STAGING_URL` - Full staging URL with protocol

### Production Secrets
- [ ] `PROD_HOST` - Production hostname/IP
- [ ] `PROD_USER` - SSH username (deploy-user)
- [ ] `PROD_SSH_KEY` - Complete private key (different from staging!)
- [ ] `PROD_PATH` - Production directory (/var/www/staff-rota-production)
- [ ] `PROD_URL` - Full production URL with protocol

---

## 🧪 Test Deployment

### Test Staging Deployment

1. Make a small change to code
2. Commit and push to `main` branch:
   ```bash
   git add .
   git commit -m "Test staging deployment"
   git push origin main
   ```
3. Go to GitHub → **Actions** tab
4. Watch deployment workflow run
5. Check for green checkmark ✅

### Test Production Deployment

1. Create and push a tag:
   ```bash
   git tag -a v1.0.0 -m "First production deployment"
   git push origin v1.0.0
   ```
2. Go to GitHub → **Actions** tab
3. Watch production deployment workflow
4. Verify production site is updated

---

## 🔧 Troubleshooting

### "Permission denied (publickey)"

**Issue:** SSH authentication failing

**Solutions:**
1. Verify private key is complete (includes headers)
2. Ensure no extra spaces/newlines in secret value
3. Check public key added to server's authorized_keys
4. Verify file permissions on server:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

### "No such file or directory"

**Issue:** Deployment path doesn't exist

**Solution:**
```bash
# On server
sudo mkdir -p /var/www/staff-rota-staging
sudo chown deploy-user:www-data /var/www/staff-rota-staging
```

### Workflow fails at "Deploy to staging server"

**Issue:** Various deployment issues

**Debug steps:**
1. Check GitHub Actions logs for specific error
2. SSH to server manually to test:
   ```bash
   ssh -i ~/.ssh/github_staging deploy-user@staging-server
   ```
3. Verify server setup completed (run server_setup.sh)
4. Check server logs:
   ```bash
   sudo journalctl -u staff-rota-staging -n 50
   ```

### Smoke tests failing

**Issue:** Application not responding

**Solutions:**
1. Check if application started:
   ```bash
   sudo systemctl status staff-rota-staging
   ```
2. Restart if needed:
   ```bash
   sudo systemctl restart staff-rota-staging
   ```
3. Check nginx:
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```
4. Verify URL in STAGING_URL secret matches nginx config

---

## 🔒 Security Best Practices

1. **Separate Keys:** Use different SSH keys for staging and production
2. **Key Rotation:** Rotate SSH keys every 90 days
3. **Least Privilege:** Deploy user should only have necessary permissions
4. **Audit Logs:** Regularly review GitHub Actions logs
5. **Secret Scanning:** Enable GitHub secret scanning
6. **2FA:** Enable two-factor authentication on GitHub account
7. **Branch Protection:** Protect main branch, require PR reviews

---

## 📚 Additional Resources

- [GitHub Actions Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [SSH Key Generation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Server Setup Script](./server_setup.sh)

---

**Last Updated:** December 28, 2025  
**Version:** 1.0
