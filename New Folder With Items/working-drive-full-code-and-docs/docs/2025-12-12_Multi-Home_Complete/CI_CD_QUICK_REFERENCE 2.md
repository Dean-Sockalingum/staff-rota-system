# CI/CD Integration - Quick Reference

## 🚀 Quick Start

### Run Tests Locally
```bash
# Full test suite
python manage.py test scheduling --noinput

# With coverage
coverage run --source='scheduling' manage.py test scheduling
coverage report --fail-under=80
```

### Run Performance Tests
```bash
# Quick load test (10 users, 10s)
python -c "from scheduling.load_testing import quick_load_test; quick_load_test()"

# Benchmarks
python -c "from scheduling.performance_benchmarks import quick_benchmark; quick_benchmark()"
```

---

## 📋 Workflow Triggers

| Workflow | Trigger | Environment |
|----------|---------|-------------|
| **CI** | Push/PR to `main`/`develop` | Test |
| **Staging** | Push to `develop` | Staging |
| **Production** | Push to `main` (manual approval) | Production |
| **Retraining** | Every Sunday 2 AM UTC | Production |

---

## ✅ Pre-Deployment Checklist

### Before Merging to `develop` (Staging Deploy)
- [ ] All tests pass locally
- [ ] Coverage ≥ 80%
- [ ] No linting errors (`flake8`)
- [ ] Performance tests pass (<1s avg)
- [ ] PR reviewed and approved

### Before Merging to `main` (Production Deploy)
- [ ] Staging deployment successful
- [ ] Staging smoke tests passed
- [ ] Performance validated in staging
- [ ] Database migrations tested
- [ ] Rollback plan prepared
- [ ] Team notified of deployment window

---

## 🔧 Common Commands

### Coverage Check
```bash
coverage run --source='scheduling' manage.py test scheduling
coverage report
coverage html  # Open htmlcov/index.html
```

### Linting
```bash
flake8 scheduling/ --max-line-length=127
```

### Migration Check
```bash
python manage.py makemigrations --check --dry-run
```

### Model Retraining (Manual)
```bash
python manage.py train_all_models
python manage.py monitor_forecasts
```

---

## 📊 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | ≥80% | Varies |
| Avg Response Time | <1s | 777ms ✓ |
| Dashboard Load | <500ms | 180ms ✓ |
| Concurrent Users | 100+ | 300+ ✓ |
| Requests/Second | ≥50 | 115 ✓ |

---

## 🚨 Troubleshooting

### Tests Failing
```bash
# Run specific test
python manage.py test scheduling.tests.test_prophet_integration

# Verbose output
python manage.py test scheduling --verbosity=2
```

### Coverage Below 80%
1. Run `coverage html`
2. Open `htmlcov/index.html`
3. Find uncovered lines (red highlighting)
4. Add tests for those code paths

### Performance Regression
1. Run `quick_load_test()` locally
2. Check for N+1 queries
3. Verify database indexes applied
4. Check Redis cache hit rate

### Deployment Failed
1. Check GitHub Actions logs
2. Review error messages
3. Test SSH connectivity
4. Verify secrets configured

---

## 📝 Workflow Status Badges

Add to README.md:
```markdown
![CI](https://github.com/yourusername/staff-rota/workflows/CI%20Pipeline/badge.svg)
![Coverage](https://codecov.io/gh/yourusername/staff-rota/branch/main/graph/badge.svg)
```

---

## 🔑 Required Secrets

### Staging
- `STAGING_HOST`, `STAGING_USER`, `STAGING_SSH_KEY`, `STAGING_URL`

### Production
- `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY`, `PRODUCTION_URL`
- `DATABASE_URL`, `PRODUCTION_REDIS_URL`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`

**Setup:** Settings → Secrets and variables → Actions → New repository secret

---

## 📅 Weekly Schedule

**Every Sunday 2 AM UTC:**
- Automated model retraining
- Performance metrics calculated
- Models deployed to production
- Forecast cache cleared
- Team report sent

---

## 🆘 Emergency Procedures

### Rollback Production
1. Go to Actions → Deploy to Production → Latest successful run
2. Download `production-release` artifact
3. SSH to production server
4. Deploy previous release
5. Restart application

### Force Model Retrain
1. Go to Actions → Automated Model Retraining
2. Click "Run workflow" → Run workflow
3. Monitor progress
4. Check retraining report artifact

---

## 📞 Support Contacts

**CI/CD Issues:** DevOps Team  
**Model Performance:** ML Team  
**Security Scans:** Security Team  

---

**Last Updated:** 21 December 2025
