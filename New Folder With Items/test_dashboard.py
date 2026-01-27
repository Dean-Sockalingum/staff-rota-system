#!/usr/bin/env python
"""
Quick test of Module 7 Integrated Dashboard
Run with: python test_dashboard.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Now import the dashboard
print("Testing Module 7 Integrated Dashboard...")
print("=" * 60)

try:
    from performance_kpis import dashboard_integration
    print("✅ dashboard_integration module imported successfully")
    
    # Test that the function exists
    assert hasattr(dashboard_integration, 'integrated_dashboard'), "integrated_dashboard function not found"
    print("✅ integrated_dashboard function exists")
    
    # Test helper function
    assert hasattr(dashboard_integration, '_get_rag_status'), "_get_rag_status function not found"
    print("✅ _get_rag_status helper function exists")
    
    # Test RAG logic
    assert dashboard_integration._get_rag_status(85) == 'GREEN', "RAG logic failed for GREEN"
    assert dashboard_integration._get_rag_status(70) == 'AMBER', "RAG logic failed for AMBER"
    assert dashboard_integration._get_rag_status(50) == 'RED', "RAG logic failed for RED"
    print("✅ RAG status logic working correctly")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("Dashboard is ready to use at: /performance-kpis/integrated/")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
