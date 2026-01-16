"""
Test Home-Specific AI Assistant Queries
========================================

Validates the enhanced AI Assistant can handle:
1. Home-specific performance queries
2. Quality audit queries
3. Comparison queries across all homes
4. Natural language pattern matching
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
django.setup()

from django.utils import timezone
from scheduling.views import (
    normalize_home_name, 
    get_home_performance, 
    compare_homes,
    _process_home_performance_query
)

def test_home_name_normalization():
    """Test natural language home name variations"""
    print("\n" + "="*70)
    print("TEST 1: Home Name Normalization")
    print("="*70)
    
    test_queries = [
        ("Show me Orchard Grove's performance", "orchard grove"),
        ("How is OG doing?", "orchard grove"),
        ("Quality audit for Victoria Gardens", "victoria gardens"),
        ("Hawthorn House occupancy", "hawthorn house"),
        ("Meadowburn agency spend", "meadowburn"),
        ("Riverside staffing today", "riverside"),
    ]
    
    for query, expected in test_queries:
        result = normalize_home_name(query)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{query}' → {result} (expected: {expected})")
    
    return True

def test_get_home_performance():
    """Test retrieving performance data for a specific home"""
    print("\n" + "="*70)
    print("TEST 2: Get Home Performance Data")
    print("="*70)
    
    home_name = "Orchard Grove"
    print(f"\nRetrieving performance data for: {home_name}")
    
    perf = get_home_performance(home_name)
    
    if perf:
        print(f"\n✅ Successfully retrieved data for {perf['display_name']}")
        print(f"\n📊 Occupancy:")
        print(f"   - Residents: {perf['occupancy']['residents']}/{perf['occupancy']['beds']}")
        print(f"   - Rate: {perf['occupancy']['rate']:.1f}%")
        
        print(f"\n👥 Staffing (Today):")
        print(f"   - Total Shifts: {perf['staffing_today']['total_shifts']}")
        print(f"   - Day/Night: {perf['staffing_today']['day_shifts']}/{perf['staffing_today']['night_shifts']}")
        print(f"   - Unfilled: {perf['staffing_today']['unfilled']}")
        
        print(f"\n⭐ Quality (30 Days):")
        print(f"   - Total Incidents: {perf['quality_30d']['total_incidents']}")
        print(f"   - Major Harm: {perf['quality_30d']['major_harm']}")
        print(f"   - CI Notifications: {perf['quality_30d']['ci_notifications']}")
        
        print(f"\n💰 Fiscal Status (This Month):")
        print(f"   - Agency: {perf['fiscal_status']['agency_percentage']:.1f}% ({perf['fiscal_status']['agency_shifts']} shifts)")
        print(f"   - Overtime: {perf['fiscal_status']['overtime_percentage']:.1f}% ({perf['fiscal_status']['overtime_shifts']} shifts)")
        
        print(f"\n📋 Care Plan Compliance:")
        print(f"   - Total Plans: {perf['care_plans']['total_plans']}")
        print(f"   - Compliance Rate: {perf['care_plans']['compliance_rate']:.1f}%")
        print(f"   - Overdue Reviews: {perf['care_plans']['overdue_reviews']}")
        
        return True
    else:
        print(f"\n❌ Failed to retrieve data for {home_name}")
        return False

def test_compare_homes():
    """Test comparing all homes across different metrics"""
    print("\n" + "="*70)
    print("TEST 3: Compare All Homes")
    print("="*70)
    
    metrics = ['overall', 'quality', 'compliance', 'occupancy', 'fiscal']
    
    for metric in metrics:
        print(f"\n📊 Comparison by: {metric.upper()}")
        comparison = compare_homes(metric)
        
        if comparison:
            print(f"   Found {len(comparison)} homes:")
            for i, home in enumerate(comparison[:3], 1):  # Show top 3
                print(f"   {i}. {home['display_name']}")
                print(f"      - Occupancy: {home['occupancy']['rate']:.1f}%")
                print(f"      - Incidents: {home['quality_30d']['total_incidents']}")
                print(f"      - Compliance: {home['care_plans']['compliance_rate']:.1f}%")
        else:
            print("   ❌ No data returned")
    
    return True

def test_query_processing():
    """Test full query processing with natural language"""
    print("\n" + "="*70)
    print("TEST 4: Full Query Processing")
    print("="*70)
    
    test_queries = [
        "Show me Orchard Grove's performance",
        "Quality audit for Victoria Gardens",
        "Compare all homes",
        "Which home has best compliance?",
        "How is Hawthorn House doing?",
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        result = _process_home_performance_query(query)
        
        if result:
            print(f"   ✅ Processed successfully")
            print(f"   - Category: {result.get('category', 'N/A')}")
            print(f"   - Answer length: {len(result.get('answer', ''))} characters")
            print(f"   - Related actions: {len(result.get('related', []))}")
            
            # Show first 200 chars of answer
            answer_preview = result.get('answer', '')[:200].replace('\n', ' ')
            print(f"   - Preview: {answer_preview}...")
        else:
            print(f"   ⚠️  Not processed (may not match home patterns)")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🤖 AI ASSISTANT HOME QUERY TESTING")
    print("="*70)
    print(f"Testing enhanced chatbot capabilities for Head of Service queries")
    print(f"Date: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Home Name Normalization", test_home_name_normalization),
        ("Get Home Performance", test_get_home_performance),
        ("Compare Homes", test_compare_homes),
        ("Query Processing", test_query_processing),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Chatbot is ready for Head of Service queries.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
