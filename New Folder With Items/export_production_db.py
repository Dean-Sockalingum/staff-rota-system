#!/usr/bin/env python3
"""
Export data directly from the production database at demo.therota.co.uk
"""
import psycopg2
import json
from datetime import date, datetime

# Production database credentials
DB_CONFIG = {
    'dbname': 'staffrota_production',
    'user': 'staffrota_user',
    'password': 'StaffRota2026Secure',
    'host': 'demo.therota.co.uk',  # Or the actual hostname
    'port': 5432
}

def date_converter(o):
    """Convert date objects to strings for JSON serialization"""
    if isinstance(o, (date, datetime)):
        return o.isoformat()
    return str(o)

print('='*80)
print('CONNECTING TO PRODUCTION DATABASE')
print('='*80)

try:
    # Connect to production database
    print(f'\n🔌 Connecting to {DB_CONFIG["host"]}...')
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    print('✅ Connected successfully!')
    
    # Export data
    export_data = []
    
    # 1. Care Homes
    print('\n📥 Exporting Care Homes...')
    cur.execute('SELECT * FROM scheduling_carehome')
    columns = [desc[0] for desc in cur.description]
    for row in cur.fetchall():
        export_data.append({
            'model': 'scheduling.carehome',
            'pk': row[0],
            'fields': dict(zip(columns[1:], row[1:]))
        })
    print(f'✅ Exported {len([d for d in export_data if d["model"] == "scheduling.carehome"])} care homes')
    
    # 2. Units
    print('📥 Exporting Units...')
    cur.execute('SELECT * FROM scheduling_unit')
    columns = [desc[0] for desc in cur.description]
    for row in cur.fetchall():
        export_data.append({
            'model': 'scheduling.unit',
            'pk': row[0],
            'fields': dict(zip(columns[1:], row[1:]))
        })
    print(f'✅ Exported {len([d for d in export_data if d["model"] == "scheduling.unit"])} units')
    
    # 3. Roles
    print('📥 Exporting Roles...')
    cur.execute('SELECT * FROM scheduling_role')
    columns = [desc[0] for desc in cur.description]
    for row in cur.fetchall():
        export_data.append({
            'model': 'scheduling.role',
            'pk': row[0],
            'fields': dict(zip(columns[1:], row[1:]))
        })
    print(f'✅ Exported {len([d for d in export_data if d["model"] == "scheduling.role"])} roles')
    
    # 4. Shift Types
    print('📥 Exporting Shift Types...')
    cur.execute('SELECT * FROM scheduling_shifttype')
    columns = [desc[0] for desc in cur.description]
    for row in cur.fetchall():
        export_data.append({
            'model': 'scheduling.shifttype',
            'pk': row[0],
            'fields': dict(zip(columns[1:], row[1:]))
        })
    print(f'✅ Exported {len([d for d in export_data if d["model"] == "scheduling.shifttype"])} shift types')
    
    # 5. Users (Staff) - Get Orchard Grove staff only
    print('📥 Exporting Orchard Grove Staff...')
    cur.execute('''
        SELECT u.* FROM scheduling_user u
        JOIN scheduling_unit un ON u.unit_id = un.id
        JOIN scheduling_carehome h ON un.care_home_id = h.id
        WHERE h.name = 'ORCHARD_GROVE'
        ORDER BY u.sap
    ''')
    columns = [desc[0] for desc in cur.description]
    og_user_count = 0
    for row in cur.fetchall():
        sap = row[columns.index('sap')]
        export_data.append({
            'model': 'scheduling.user',
            'pk': sap,
            'fields': dict(zip(columns[1:], row[1:]))
        })
        og_user_count += 1
    print(f'✅ Exported {og_user_count} Orchard Grove staff')
    
    # Check SAP number format
    users = [d for d in export_data if d['model'] == 'scheduling.user']
    if users:
        sample_saps = [u['pk'] for u in users[:5]]
        print(f'\n📋 Sample SAP numbers: {sample_saps}')
        max_sap_len = max(len(str(u['pk'])) for u in users)
        print(f'📏 Max SAP length: {max_sap_len} characters')
        long_saps = [u['pk'] for u in users if len(str(u['pk'])) > 6]
        if long_saps:
            print(f'⚠️  WARNING: {len(long_saps)} SAP numbers longer than 6 characters:')
            for sap in long_saps[:10]:
                print(f'    {sap}')
    
    # 6. Shifts - Get Orchard Grove shifts only
    print('\n📥 Exporting Orchard Grove Shifts...')
    cur.execute('''
        SELECT s.* FROM scheduling_shift s
        JOIN scheduling_user u ON s.user_id = u.sap
        JOIN scheduling_unit un ON u.unit_id = un.id
        JOIN scheduling_carehome h ON un.care_home_id = h.id
        WHERE h.name = 'ORCHARD_GROVE'
        ORDER BY s.date, u.sap
    ''')
    columns = [desc[0] for desc in cur.description]
    shift_count = 0
    for row in cur.fetchall():
        export_data.append({
            'model': 'scheduling.shift',
            'pk': row[0],
            'fields': dict(zip(columns[1:], row[1:]))
        })
        shift_count += 1
        if shift_count % 10000 == 0:
            print(f'  Progress: {shift_count:,} shifts...')
    
    print(f'✅ Exported {shift_count:,} Orchard Grove shifts')
    
    # Close connection
    cur.close()
    conn.close()
    
    # Save to file
    output_file = 'production_orchard_grove_export.json'
    print(f'\n💾 Saving to {output_file}...')
    with open(output_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=date_converter)
    
    print('='*80)
    print('✅ EXPORT COMPLETE!')
    print('='*80)
    print(f'\n📊 EXPORTED DATA:')
    print(f'  • Care Homes: {len([d for d in export_data if d["model"] == "scheduling.carehome"])}')
    print(f'  • Units: {len([d for d in export_data if d["model"] == "scheduling.unit"])}')
    print(f'  • Roles: {len([d for d in export_data if d["model"] == "scheduling.role"])}')
    print(f'  • Shift Types: {len([d for d in export_data if d["model"] == "scheduling.shifttype"])}')
    print(f'  • Orchard Grove Staff: {og_user_count}')
    print(f'  • Orchard Grove Shifts: {shift_count:,}')
    print(f'\n📁 File saved: {output_file}')
    print('\nYou can now import this data using the import script.')
    
except psycopg2.Error as e:
    print(f'\n❌ Database connection error: {e}')
    print('\nPlease verify:')
    print('  1. Database host/IP address is correct')
    print('  2. Database is accessible from your network')
    print('  3. Credentials are correct')
    print('  4. PostgreSQL port 5432 is open')
except Exception as e:
    print(f'\n❌ Error: {e}')
    import traceback
    traceback.print_exc()
