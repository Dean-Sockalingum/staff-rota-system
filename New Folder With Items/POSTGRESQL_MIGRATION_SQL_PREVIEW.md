# PostgreSQL Migration SQL Preview
## Date: January 19, 2026

### Migration 0060: Add is_overtime Field to Shift Model

**File:** `scheduling/migrations/0060_add_is_overtime_field.py`

**Expected PostgreSQL SQL:**
```sql
-- Add is_overtime field to scheduling_shift table
ALTER TABLE "scheduling_shift" 
ADD COLUMN "is_overtime" boolean DEFAULT false NOT NULL;

-- Create index for performance
CREATE INDEX "scheduling_shift_is_overtime_idx" 
ON "scheduling_shift" ("is_overtime");
```

**Impact:**
- Adds boolean field with default `false` to all existing shifts
- Creates index for faster overtime queries
- Zero data loss - all existing shifts default to `is_overtime=False`
- Required for rota health scoring overtime tracking

---

### Migration 0061: Create StaffCertification Table

**File:** `scheduling/migrations/0061_create_staffcertification_table.py`

**Expected PostgreSQL SQL:**
```sql
-- Create staff certification tracking table
CREATE TABLE "scheduling_staffcertification" (
    "id" bigserial NOT NULL PRIMARY KEY,
    "certification_type" varchar(50) NOT NULL,
    "certification_name" varchar(200) NOT NULL,
    "issue_date" date NOT NULL,
    "expiry_date" date NOT NULL,
    "renewal_date" date NULL,
    "issuing_body" varchar(200) NOT NULL,
    "certificate_number" varchar(100) NOT NULL,
    "status" varchar(20) NOT NULL,
    "certificate_file" varchar(100) NULL,
    "days_before_expiry_alert" integer NOT NULL,
    "alert_sent" boolean NOT NULL,
    "alert_sent_at" timestamp with time zone NULL,
    "notes" text NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL,
    "created_by_id" bigint NULL,
    "staff_member_id" bigint NOT NULL
);

-- Foreign key constraints
ALTER TABLE "scheduling_staffcertification" 
ADD CONSTRAINT "scheduling_staffce_created_by_id_8a7b3c9d_fk_scheduling_user_id" 
FOREIGN KEY ("created_by_id") 
REFERENCES "scheduling_user" ("id") 
ON DELETE SET NULL 
DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "scheduling_staffcertification" 
ADD CONSTRAINT "scheduling_staffce_staff_member_id_9f2e5d4c_fk_scheduling_user_id" 
FOREIGN KEY ("staff_member_id") 
REFERENCES "scheduling_user" ("id") 
ON DELETE CASCADE 
DEFERRABLE INITIALLY DEFERRED;

-- Performance indexes
CREATE INDEX "scheduling_staff_m_c7b21e_idx" 
ON "scheduling_staffcertification" ("staff_member_id", "expiry_date");

CREATE INDEX "scheduling_certif_a3d9f2_idx" 
ON "scheduling_staffcertification" ("certification_type", "status");

CREATE INDEX "scheduling_expiry_b8e4c1_idx" 
ON "scheduling_staffcertification" ("expiry_date", "status");

CREATE INDEX "scheduling_staffce_created_by_id_8a7b3c9d" 
ON "scheduling_staffcertification" ("created_by_id");

CREATE INDEX "scheduling_staffce_staff_member_id_9f2e5d4c" 
ON "scheduling_staffcertification" ("staff_member_id");
```

**Impact:**
- Creates complete table with all fields and constraints
- Zero data loss - new empty table
- Enables staff certification tracking
- Required for compliance dashboard full functionality

---

## Migration Order

1. **0060_add_is_overtime_field** - Must run first
2. **0061_create_staffcertification_table** - Depends on 0060

## Testing Commands

### On Development (PostgreSQL)
```bash
# Check migration status
python manage.py showmigrations scheduling

# Preview SQL without applying
python manage.py sqlmigrate scheduling 0060
python manage.py sqlmigrate scheduling 0061

# Apply migrations
python manage.py migrate scheduling

# Verify tables
python manage.py dbshell
\d scheduling_shift               -- Should show is_overtime field
\d scheduling_staffcertification  -- Should exist with all fields
\q
```

### On Production (PostgreSQL)
```bash
# SSH to production
ssh root@159.65.18.80

# Navigate to project
cd /home/staff-rota-system/2025-12-12_Multi-Home_Complete

# Activate virtualenv
source /home/staff-rota-system/venv/bin/activate

# Check migrations
python manage.py showmigrations scheduling

# Backup database first
pg_dump staffrota_production > backup_pre_migration_$(date +%Y%m%d).sql

# Apply migrations
python manage.py migrate scheduling

# Restart service
sudo systemctl restart staffrota

# Monitor logs
journalctl -u staffrota -f
```

---

## Rollback Plan

If migrations fail or cause issues:

### Development
```bash
# Rollback to previous migration
python manage.py migrate scheduling 0059

# Or restore from backup
dropdb staffrota_dev
createdb staffrota_dev
psql staffrota_dev < backup_pre_migration_YYYYMMDD.sql
```

### Production
```bash
# Stop service
sudo systemctl stop staffrota

# Rollback migrations
python manage.py migrate scheduling 0059

# Or restore database
sudo -u postgres psql -c "DROP DATABASE staffrota_production;"
sudo -u postgres psql -c "CREATE DATABASE staffrota_production;"
sudo -u postgres psql staffrota_production < backup_pre_migration_YYYYMMDD.sql

# Restart service
sudo systemctl start staffrota
```

---

## Verification Checklist

After applying migrations:

- [ ] No errors in migration output
- [ ] `is_overtime` field exists in `scheduling_shift` table
- [ ] `scheduling_staffcertification` table created
- [ ] All indexes created successfully
- [ ] Foreign keys established correctly
- [ ] Service restarts without errors
- [ ] Memory usage remains stable (~76MB)
- [ ] Compliance dashboard accessible
- [ ] Rota health scoring works

---

## Next Steps After Migration

1. **Re-enable overtime features** in `scheduling/utils_rota_health_scoring.py`
2. **Re-enable certification queries** in `scheduling/views.py`
3. **Test overtime tracking** functionality
4. **Test certification tracking** functionality
5. **Backfill is_overtime** from `shift_classification` if needed

---

*Generated: January 19, 2026*
*PostgreSQL Version: 14+*
*Django Version: 4.2.27*
