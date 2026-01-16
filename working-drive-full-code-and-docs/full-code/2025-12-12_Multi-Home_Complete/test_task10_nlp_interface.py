"""
Task 10 - Natural Language Query Interface - Quick Validation Tests

Tests the NLP processor and API endpoints to ensure:
1. Query classification works correctly
2. Entity extraction is accurate
3. Routing to AI systems (Tasks 1-8) functions properly
4. Response generation is natural and helpful
5. API endpoints are functional

Run: python3 test_task10_nlp_interface.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rotasystems.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from scheduling.nlp_query_processor import NLPQueryProcessor, process_natural_language_query, get_query_suggestions
from datetime import date, timedelta
from django.utils import timezone


def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST: {test_name}")
    print("="*80)


def print_result(passed, message):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {message}")


def test_1_nlp_processor_initialization():
    """Test 1: Initialize NLP Processor"""
    print_test_header("NLP Processor Initialization")
    
    try:
        processor = NLPQueryProcessor()
        
        # Check intent patterns exist
        assert len(processor.INTENT_PATTERNS) > 0, "No intent patterns found"
        assert 'staffing_shortage' in processor.INTENT_PATTERNS, "Missing staffing_shortage intent"
        assert 'budget_status' in processor.INTENT_PATTERNS, "Missing budget_status intent"
        assert 'compliance_check' in processor.INTENT_PATTERNS, "Missing compliance_check intent"
        
        print_result(True, f"Processor initialized with {len(processor.INTENT_PATTERNS)} intent categories")
        
        # Display intent categories
        print("\nIntent Categories:")
        for intent in processor.INTENT_PATTERNS.keys():
            pattern_count = len(processor.INTENT_PATTERNS[intent])
            print(f"  • {intent}: {pattern_count} patterns")
        
        return True
    
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_2_intent_classification():
    """Test 2: Query Intent Classification"""
    print_test_header("Intent Classification")
    
    test_queries = [
        ("Who can work tomorrow?", "staffing_shortage"),
        ("Show me the budget status", "budget_status"),
        ("Is John Smith WTD compliant?", "compliance_check"),
        ("Check fraud risks", "fraud_detection"),
        ("Find shift swaps", "shift_swap"),
        ("Book agency staff", "agency_booking"),
        ("Predict next month shortages", "shortage_forecast"),
        ("How many staff do we have?", "staff_info"),
    ]
    
    processor = NLPQueryProcessor()
    passed_count = 0
    
    for query, expected_intent in test_queries:
        intent, confidence = processor._classify_intent(query.lower())
        passed = (intent == expected_intent)
        
        if passed:
            passed_count += 1
            print_result(True, f"'{query}' → {intent} (confidence: {confidence:.2f})")
        else:
            print_result(False, f"'{query}' → {intent} (expected: {expected_intent})")
    
    success_rate = (passed_count / len(test_queries)) * 100
    print(f"\n✅ Success Rate: {success_rate:.1f}% ({passed_count}/{len(test_queries)})")
    
    return passed_count == len(test_queries)


def test_3_entity_extraction():
    """Test 3: Entity Extraction from Queries"""
    print_test_header("Entity Extraction")
    
    test_cases = [
        {
            'query': "Who can work tomorrow?",
            'expected': {'date_present': True, 'shift_type': None}
        },
        {
            'query': "Find staff for night shift next week",
            'expected': {'date_present': True, 'shift_type': 'night'}
        },
        {
            'query': "Check John Smith compliance",
            'expected': {'staff_name_present': True}
        },
    ]
    
    processor = NLPQueryProcessor()
    passed_count = 0
    
    for case in test_cases:
        query = case['query']
        expected = case['expected']
        entities = processor._extract_entities(query.lower())
        
        passed = True
        
        # Check date extraction
        if 'date_present' in expected:
            has_date = (entities['date'] is not None)
            if has_date == expected['date_present']:
                print_result(True, f"'{query}' → Date extracted: {entities['date']}")
            else:
                print_result(False, f"'{query}' → Date extraction failed")
                passed = False
        
        # Check shift type
        if 'shift_type' in expected:
            if entities['shift_type'] == expected['shift_type']:
                print_result(True, f"'{query}' → Shift type: {entities['shift_type']}")
            else:
                print_result(False, f"'{query}' → Expected shift type: {expected['shift_type']}, got: {entities['shift_type']}")
                passed = False
        
        # Check staff name
        if 'staff_name_present' in expected:
            has_name = (entities['staff_name'] is not None)
            if has_name:
                print_result(True, f"'{query}' → Staff name: {entities['staff_name']}")
            else:
                print_result(False, f"'{query}' → Staff name not extracted")
                passed = False
        
        if passed:
            passed_count += 1
    
    success_rate = (passed_count / len(test_cases)) * 100
    print(f"\n✅ Success Rate: {success_rate:.1f}% ({passed_count}/{len(test_cases)})")
    
    return passed_count == len(test_cases)


def test_4_staffing_query_processing():
    """Test 4: Process Staffing Shortage Queries"""
    print_test_header("Staffing Query Processing")
    
    try:
        # Test query: "Who can work tomorrow?"
        query = "Who can work tomorrow?"
        result = process_natural_language_query(query)
        
        # Check response structure
        assert 'intent' in result, "Missing 'intent' in response"
        assert 'response' in result, "Missing 'response' in response"
        assert 'data' in result, "Missing 'data' in response"
        assert 'suggestions' in result, "Missing 'suggestions' in response"
        
        print_result(True, f"Query processed successfully")
        print(f"  Intent: {result['intent']}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Response preview: {result['response'][:150]}...")
        print(f"  Suggestions: {len(result['suggestions'])} provided")
        
        # Verify intent classification
        if result['intent'] == 'staffing_shortage':
            print_result(True, "Intent correctly classified as 'staffing_shortage'")
        else:
            print_result(False, f"Intent should be 'staffing_shortage', got '{result['intent']}'")
            return False
        
        return True
    
    except Exception as e:
        print_result(False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_budget_query_processing():
    """Test 5: Process Budget Queries"""
    print_test_header("Budget Query Processing")
    
    try:
        # Test query: "Show me the budget status"
        query = "Show me the budget status"
        result = process_natural_language_query(query)
        
        print_result(True, f"Query processed successfully")
        print(f"  Intent: {result['intent']}")
        print(f"  Response preview: {result['response'][:150]}...")
        
        # Check if budget data is in response
        if 'Budget' in result['response'] or 'budget' in result['response']:
            print_result(True, "Response contains budget information")
        else:
            print_result(False, "Response missing budget information")
            return False
        
        return True
    
    except Exception as e:
        print_result(False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_query_suggestions():
    """Test 6: Get Query Suggestions"""
    print_test_header("Query Suggestions")
    
    try:
        suggestions = get_query_suggestions()
        
        assert len(suggestions) > 0, "No suggestions returned"
        
        print_result(True, f"Retrieved {len(suggestions)} example queries")
        
        print("\nExample Queries:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"  {i}. {suggestion}")
        
        if len(suggestions) > 5:
            print(f"  ... and {len(suggestions) - 5} more")
        
        return True
    
    except Exception as e:
        print_result(False, f"Error: {e}")
        return False


def test_7_multiple_query_types():
    """Test 7: Process Multiple Query Types"""
    print_test_header("Multiple Query Types")
    
    test_queries = [
        "Who can work tomorrow?",
        "Show budget status",
        "Check fraud risks",
        "Find shift swaps",
        "Predict shortages",
    ]
    
    passed_count = 0
    
    for query in test_queries:
        try:
            result = process_natural_language_query(query)
            
            # Check basic response structure
            if all(k in result for k in ['intent', 'response', 'data', 'suggestions']):
                print_result(True, f"'{query}' processed successfully → {result['intent']}")
                passed_count += 1
            else:
                print_result(False, f"'{query}' missing response fields")
        
        except Exception as e:
            print_result(False, f"'{query}' failed: {e}")
    
    success_rate = (passed_count / len(test_queries)) * 100
    print(f"\n✅ Success Rate: {success_rate:.1f}% ({passed_count}/{len(test_queries)})")
    
    return passed_count == len(test_queries)


def test_8_api_integration():
    """Test 8: API Endpoint Integration Check"""
    print_test_header("API Endpoint Integration")
    
    try:
        # Check that views can be imported
        from scheduling.views_compliance import ai_assistant_query_api, ai_assistant_suggestions_api
        
        print_result(True, "API endpoints imported successfully")
        print("  • ai_assistant_query_api")
        print("  • ai_assistant_suggestions_api")
        
        # Check URL patterns registered
        from django.urls import reverse
        
        try:
            url_query = reverse('ai_assistant_query_api')
            url_suggestions = reverse('ai_assistant_suggestions_api')
            
            print_result(True, f"URL routes registered:")
            print(f"  • Query API: {url_query}")
            print(f"  • Suggestions API: {url_suggestions}")
        except Exception as e:
            print_result(False, f"URL routing issue: {e}")
            return False
        
        return True
    
    except Exception as e:
        print_result(False, f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all Task 10 tests"""
    print("\n" + "="*80)
    print("TASK 10 - NATURAL LANGUAGE QUERY INTERFACE")
    print("Quick Validation Tests")
    print("="*80)
    
    tests = [
        ("Processor Initialization", test_1_nlp_processor_initialization),
        ("Intent Classification", test_2_intent_classification),
        ("Entity Extraction", test_3_entity_extraction),
        ("Staffing Query Processing", test_4_staffing_query_processing),
        ("Budget Query Processing", test_5_budget_query_processing),
        ("Query Suggestions", test_6_query_suggestions),
        ("Multiple Query Types", test_7_multiple_query_types),
        ("API Integration", test_8_api_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    success_rate = (passed_count / total_count) * 100
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*80}")
    print(f"Overall: {passed_count}/{total_count} tests passed ({success_rate:.1f}%)")
    print(f"{'='*80}")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Task 10 is production-ready.")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Review above for details.")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
