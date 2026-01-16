# CI/CD Integration Guide

## Overview

This guide documents the continuous integration and deployment (CI/CD) pipeline for the Staff Rota ML-Enhanced Scheduling System.

## GitHub Actions Workflows

### 1. Continuous Integration (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Jobs:**

#### Test Job
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Python Version:** 3.11
- **Steps:**
  1. Code checkout
  2. Python setup with pip caching
  3. Install dependencies
  4. Linting (flake8)
  5. Database migrations
  6. Run full test suite with coverage
  7. Upload coverage to Codecov
  8. Prophet model integration tests
  9. Forecast monitoring tests
  10. Migration check

**Coverage Requirements:**
- Minimum: 80% code coverage
- Measured on `scheduling` app
- Fails build if below threshold

#### Security Job
- **Tools:**
  - `safety`: Dependency vulnerability scanning
  - `bandit`: Python security linting
- **Artifacts:** Security reports uploaded for review

#### Performance Job
- **Dependencies:** Requires test job to pass
- **Tests:**
  1. LP solver benchmarks (quick_benchmark)
  2. Load testing (quick_load_test)
  3. Response time validation (<1s threshold)
- **Failure Conditions:**
  - Average response time > 1s
  - Performance regression detected

---

### 2. Staging Deployment (`deploy-staging.yml`)

**Triggers:**
- Push to `develop` branch
- Manual workflow dispatch

**Environment:** `staging`

**Steps:**
1. Code checkout
2. Install dependencies
3. Run full test suite
4. Build deployment package (tar.gz)
5. Deploy to staging server
6. Run smoke tests
7. Notify deployment status

**Required Secrets:**
- `STAGING_HOST`: Staging server hostname
- `STAGING_USER`: SSH username
- `STAGING_SSH_KEY`: SSH private key
- `STAGING_URL`: Staging URL for smoke tests

**Deployment Package Contents:**
- `scheduling/` app
- `rotasystems/` settings
- `manage.py`
- `requirements.txt`

---

### 3. Production Deployment (`deploy-production.yml`)

**Triggers:**
- Push to `main` branch
- Version tags (v*)
- Manual workflow dispatch

**Environment:** `production` (requires manual approval)

**Steps:**
1. Code checkout
2. Install dependencies
3. Run **full test suite**
4. Run performance validation
5. Build production package
6. Create timestamped backup
7. Deploy to production
8. Run smoke tests
9. Warm up Prophet models
10. Monitor and notify

**Required Secrets:**
- `PRODUCTION_HOST`: Production server hostname
- `PRODUCTION_USER`: SSH username
- `PRODUCTION_SSH_KEY`: SSH private key
- `PRODUCTION_URL`: Production URL

**Critical Checks:**
- All tests must pass
- Performance validation (<1s avg response)
- Manual approval required

**Smoke Tests:**
- Health check endpoint
- Database connectivity
- Redis connectivity
- Prophet model loading
- Dashboard load time validation

---

### 4. Automated Model Retraining (`retrain-models.yml`)

**Triggers:**
- **Scheduled:** Every Sunday at 2 AM UTC
- Manual workflow dispatch

**Database:** PostgreSQL 15 (restored from production backup)

**Steps:**

#### 1. Environment Setup
- Checkout code
- Install dependencies
- Restore production database backup

#### 2. Drift Detection
```bash
python manage.py monitor_forecasts --no-email
```
- Checks MAPE degradation
- Detects forecast drift (KS test)
- Generates drift report

#### 3. Parallel Model Retraining
- Uses `ThreadPoolExecutor` with 4 workers
- Trains all unit models (365 days historical data)
- Logs training time per unit

**Expected Performance:**
- ~15s total (parallel)
- ~3s per unit average

#### 4. Model Validation
- Verifies all `.pkl` files exist
- Validates model structure
- Checks `predict()` method availability
- Fails if any model invalid

#### 5. Performance Metrics
- Calculates MAPE for each unit
- Compares to pre-retraining MAPE
- Logs performance changes

#### 6. Model Deployment
- Archives old models (timestamped)
- Uploads retrained models as artifacts
- Deploys to production server
- Clears forecast cache (Redis)

#### 7. Reporting
- Generates retraining report
- Uploads as artifact (90-day retention)
- Sends team notification

**Required Secrets:**
- `DATABASE_URL`: Production database connection
- `PRODUCTION_REDIS_URL`: Production Redis URL
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials

---

## Setup Instructions

### 1. Enable GitHub Actions

Navigate to repository **Settings → Actions → General**:
- ✅ Allow all actions and reusable workflows
- ✅ Read and write permissions for `GITHUB_TOKEN`

### 2. Configure Secrets

Go to **Settings → Secrets and variables → Actions**:

**Staging Secrets:**
```
STAGING_HOST=staging.yourcompany.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private-key>
STAGING_URL=https://staging.yourcompany.com
```

**Production Secrets:**
```
PRODUCTION_HOST=rota.yourcompany.com
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=<private-key>
PRODUCTION_URL=https://rota.yourcompany.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
PRODUCTION_REDIS_URL=redis://redis.yourcompany.com:6379/0
DB_NAME=rota_production
DB_USER=rota_admin
DB_PASSWORD=<secure-password>
```

### 3. Configure Environments

Create GitHub environments for approval gates:

**Settings → Environments → New environment:**

#### Staging Environment
- Name: `staging`
- Protection rules: None (auto-deploy)

#### Production Environment
- Name: `production`
- Protection rules:
  - ✅ Required reviewers (add senior team members)
  - ✅ Wait timer: 5 minutes
  - ⚠️ **Manual approval required before production deploy**

### 4. Branch Protection Rules

**Settings → Branches → Add rule:**

#### Main Branch Protection
- Branch name pattern: `main`
- Rules:
  - ✅ Require pull request reviews (1 reviewer)
  - ✅ Require status checks to pass:
    - `test`
    - `security`
    - `performance`
  - ✅ Require branches to be up to date
  - ✅ Require linear history
  - ✅ Do not allow bypassing

#### Develop Branch Protection
- Branch name pattern: `develop`
- Rules:
  - ✅ Require status checks: `test`
  - ✅ Allow force pushes (for rebasing)

---

## Workflow Execution

### Development Workflow

```mermaid
graph LR
    A[Feature Branch] --> B[Create PR to develop]
    B --> C[CI Tests Run]
    C --> D{Tests Pass?}
    D -->|No| E[Fix Issues]
    E --> B
    D -->|Yes| F[Merge to develop]
    F --> G[Auto-deploy to Staging]
```

### Production Release Workflow

```mermaid
graph LR
    A[develop branch] --> B[Create PR to main]
    B --> C[CI Tests + Performance]
    C --> D{All Checks Pass?}
    D -->|No| E[Fix Issues]
    E --> A
    D -->|Yes| F[Merge to main]
    F --> G[Request Approval]
    G --> H[Manual Review]
    H --> I{Approved?}
    I -->|No| J[Cancel Deploy]
    I -->|Yes| K[Deploy to Production]
    K --> L[Smoke Tests]
    L --> M[Warm Prophet Cache]
```

### Weekly Retraining Schedule

```
Sunday 2 AM UTC → Automated Retraining Workflow
├── Download production database
├── Check for model drift
├── Retrain all Prophet models (parallel)
├── Validate models
├── Deploy to production
├── Clear forecast cache
└── Send team report
```

---

## Monitoring and Alerts

### CI Failures

**When tests fail:**
1. Review GitHub Actions logs
2. Check specific failing test output
3. Run locally: `python manage.py test scheduling --noinput`
4. Fix issue and push

### Coverage Drops Below 80%

**Actions:**
1. Review coverage report in Codecov
2. Identify uncovered code paths
3. Add tests to increase coverage
4. Push updated tests

### Performance Regression

**Threshold:** Average response time > 1s

**Actions:**
1. Review performance test logs
2. Run local benchmarks: `quick_benchmark()`
3. Check for N+1 queries
4. Apply query optimizations
5. Re-run performance tests

### Deployment Failures

**Staging:**
1. Check deployment logs
2. Verify staging server connectivity
3. Review smoke test failures
4. Manual fix and re-deploy

**Production:**
1. **DO NOT PANIC** - automated rollback available
2. Review deployment logs
3. Check smoke test failures
4. If critical, initiate manual rollback
5. Investigate root cause in staging

### Model Retraining Failures

**Common Issues:**
1. **Database connection:** Verify `DATABASE_URL` secret
2. **Model validation fails:** Check for corrupt data
3. **Deployment fails:** Verify SSH credentials
4. **Cache clear fails:** Check Redis connectivity

**Recovery:**
1. Review retraining report artifact
2. Check drift_report.txt for issues
3. Manual retrain: `python manage.py train_all_models`
4. Re-run workflow manually

---

## Performance Benchmarks

### Expected CI Durations

| Job | Duration | Notes |
|-----|----------|-------|
| Test | 3-5 min | Includes full test suite |
| Security | 1-2 min | Dependency + code scans |
| Performance | 2-3 min | Quick benchmarks only |
| **Total CI** | **6-10 min** | Parallel execution |

### Deployment Durations

| Environment | Duration | Notes |
|-------------|----------|-------|
| Staging | 5-8 min | Auto-deploy on success |
| Production | 10-15 min | Includes approval wait |

### Model Retraining

| Phase | Duration | Notes |
|-------|----------|-------|
| Database restore | 2-5 min | Depends on DB size |
| Drift detection | 1 min | Quick MAPE check |
| Parallel training | 15-20 sec | 4 workers, 5 units |
| Validation | 30 sec | Load and verify models |
| Deployment | 2-3 min | Upload + cache clear |
| **Total** | **6-10 min** | Sunday 2 AM UTC |

---

## Troubleshooting

### "Coverage check failed: 78% < 80%"

**Solution:**
```bash
# Run coverage locally
coverage run --source='scheduling' manage.py test scheduling
coverage report
coverage html  # Open htmlcov/index.html to see gaps
```

Add tests for uncovered code paths.

### "Performance test failed: 1.2s > 1s"

**Solution:**
```bash
# Run local performance test
python -c "
from scheduling.load_testing import quick_load_test
results = quick_load_test()
print(results)
"
```

Check for:
- Missing database indexes
- N+1 queries (use Django Debug Toolbar)
- Uncached Prophet forecasts

### "Model retraining: 2/5 models invalid"

**Check:**
1. View retraining report artifact
2. Check for data quality issues in failing units
3. Verify adequate historical data (≥30 days)

**Fix:**
```python
# Investigate specific unit
from scheduling.prophet_integration import train_prophet_model
from scheduling.models import Unit

unit = Unit.objects.get(name='FAILING_UNIT')
model_path = train_prophet_model(unit, days=365)
```

### "Deployment: SSH connection refused"

**Verify:**
```bash
# Test SSH connection
ssh -i <key> $STAGING_USER@$STAGING_HOST

# Check secrets are set
# Settings → Secrets → Actions
```

---

## Maintenance

### Monthly Tasks

- [ ] Review Codecov trends
- [ ] Check security scan reports
- [ ] Review performance test trends
- [ ] Verify all workflows running successfully

### Quarterly Tasks

- [ ] Update Python dependencies: `pip list --outdated`
- [ ] Update GitHub Actions versions
- [ ] Review and optimize test suite duration
- [ ] Audit deployment process for improvements

### Annual Tasks

- [ ] Rotate SSH keys and secrets
- [ ] Review branch protection rules
- [ ] Update CI/CD documentation
- [ ] Performance baseline re-evaluation

---

## Best Practices

### 1. **Never Skip Tests**
- All PRs must pass CI before merging
- No exceptions for "urgent" fixes

### 2. **Manual Approval for Production**
- At least 1 senior team member must approve
- Review staging deployment logs first
- Verify smoke tests passed

### 3. **Monitor After Deployment**
- Watch logs for 30 minutes post-deploy
- Check error rates in monitoring dashboard
- Verify Prophet forecasts generating correctly

### 4. **Model Retraining Schedule**
- Runs automatically every Sunday
- Manual trigger available for urgent retraining
- Always review drift report before deployment

### 5. **Rollback Procedure**
- Keep last 3 production releases
- Rollback: Deploy previous release artifact
- Restore database from pre-deployment backup

---

## Contact and Support

**CI/CD Issues:**
- Review GitHub Actions logs first
- Check this documentation
- Contact DevOps team for infrastructure issues

**Model Retraining Issues:**
- Check retraining report artifacts
- Review forecast monitoring dashboard
- Contact ML team for model performance issues

---

## Appendix: Workflow Files

### File Locations
```
.github/
└── workflows/
    ├── ci.yml                  # Continuous Integration
    ├── deploy-staging.yml      # Staging Deployment
    ├── deploy-production.yml   # Production Deployment
    └── retrain-models.yml      # Weekly Model Retraining
```

### Artifacts Retention

| Artifact | Retention | Purpose |
|----------|-----------|---------|
| Security reports | 30 days | Audit trail |
| Prophet models | 90 days | Rollback capability |
| Retraining reports | 90 days | Performance tracking |
| Production releases | 90 days | Deployment rollback |

### Secrets Checklist

- [ ] `STAGING_HOST`
- [ ] `STAGING_USER`
- [ ] `STAGING_SSH_KEY`
- [ ] `STAGING_URL`
- [ ] `PRODUCTION_HOST`
- [ ] `PRODUCTION_USER`
- [ ] `PRODUCTION_SSH_KEY`
- [ ] `PRODUCTION_URL`
- [ ] `DATABASE_URL`
- [ ] `PRODUCTION_REDIS_URL`
- [ ] `DB_NAME`
- [ ] `DB_USER`
- [ ] `DB_PASSWORD`

---

**Document Version:** 1.0  
**Last Updated:** 21 December 2025  
**Next Review:** March 2026
