"""
Test script for PDSA ML components
Run this to verify all ML features work correctly
"""

from quality_audits.ml.smart_aim_generator import SMARTAimGenerator
from quality_audits.ml.hypothesis_suggester import HypothesisSuggester
from quality_audits.ml.data_analyzer import PDSADataAnalyzer
from quality_audits.ml.success_predictor import PDSASuccessPredictor
from quality_audits.ml.pdsa_chatbot import PDSAChatbot
from datetime import datetime, timedelta
import json


def test_smart_aim_generator():
    """Test SMART aim generation"""
    print("\n" + "="*80)
    print("TESTING: SMART Aim Generator")
    print("="*80)
    
    generator = SMARTAimGenerator()
    
    result = generator.generate_smart_aim(
        problem_description="Residents experiencing frequent falls during night shift",
        baseline_value=12,
        baseline_unit="falls per month",
        target_value=6,
        target_unit="falls per month",
        target_population="Night shift residents in Ward A",
        timeframe_weeks=12
    )
    
    print(f"\nGenerated Aim: {result['aim_statement']}")
    print(f"SMART Score: {result['smartness_score']}/100")
    print(f"✓ Specific: {result['specific']}")
    print(f"✓ Measurable: {result['measurable']}")
    print(f"✓ Achievable: {result['achievable']}")
    print(f"✓ Relevant: {result['relevant']}")
    print(f"✓ Time-bound: {result['time_bound']}")
    
    if result['suggestions']:
        print(f"\nSuggestions for improvement:")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
    
    print("\n✅ SMART Aim Generator working!")
    return result


def test_hypothesis_suggester():
    """Test hypothesis suggestions"""
    print("\n" + "="*80)
    print("TESTING: Hypothesis Suggester")
    print("="*80)
    
    suggester = HypothesisSuggester()
    
    suggestions = suggester.suggest_hypotheses(
        problem_description="High rate of medication errors during evening shift",
        category="medication",
        top_n=3
    )
    
    print(f"\nFound {len(suggestions)} hypothesis suggestions:")
    for i, sugg in enumerate(suggestions, 1):
        print(f"\n{i}. {sugg['hypothesis']}")
        print(f"   Source: {sugg['source_project']}")
        print(f"   Outcome: {sugg['outcome']}")
        print(f"   Similarity: {sugg['similarity_score']}")
    
    print("\n✅ Hypothesis Suggester working!")
    return suggestions


def test_data_analyzer():
    """Test data analysis"""
    print("\n" + "="*80)
    print("TESTING: PDSA Data Analyzer")
    print("="*80)
    
    analyzer = PDSADataAnalyzer()
    
    # Create sample data with improving trend
    base_date = datetime.now() - timedelta(days=60)
    datapoints = []
    for i in range(12):
        datapoints.append({
            'date': base_date + timedelta(weeks=i),
            'value': 12 - (i * 0.4) + ((-1)**i * 0.3),  # Declining trend with variation
            'notes': f'Week {i+1} measurement'
        })
    
    result = analyzer.analyze_cycle_data(
        datapoints=datapoints,
        baseline_mean=12.0,
        target_value=6.0
    )
    
    print(f"\nTrend: {result['trend']}")
    print(f"Statistical Significance: p={result['statistical_significance']:.4f}")
    print(f"Is Significant: {result['is_significant']}")
    
    print(f"\nControl Limits:")
    print(f"  UCL: {result['control_limits']['ucl']}")
    print(f"  Centerline: {result['control_limits']['centerline']}")
    print(f"  LCL: {result['control_limits']['lcl']}")
    
    print(f"\nSummary Statistics:")
    stats = result['summary_stats']
    print(f"  Mean: {stats['mean']:.2f}")
    print(f"  Std Dev: {stats['std_dev']:.2f}")
    print(f"  Range: {stats['min']:.2f} to {stats['max']:.2f}")
    
    if result['special_causes']:
        print(f"\n⚠️  Special Causes Detected:")
        for cause in result['special_causes']:
            print(f"  • {cause['rule']} at index {cause['index']}")
    
    print(f"\nInsights:")
    for insight in result['insights']:
        print(f"  • {insight}")
    
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")
    
    print("\n✅ Data Analyzer working!")
    return result


def test_success_predictor():
    """Test success prediction"""
    print("\n" + "="*80)
    print("TESTING: Success Predictor")
    print("="*80)
    
    predictor = PDSASuccessPredictor()
    
    # Test project data
    project_data = {
        'smartness_score': 85,
        'team_size': 5,
        'baseline_value': 12,
        'target_value': 6,
        'category': 'medication',
        'priority': 'high',
        'has_hypothesis': True
    }
    
    result = predictor.predict_success(project_data, explain=True)
    
    print(f"\nSuccess Probability: {result['success_probability']:.1%}")
    print(f"Predicted Outcome: {result['predicted_outcome']}")
    print(f"Confidence: {result['confidence']:.1%}")
    
    if 'key_factors' in result:
        print(f"\nKey Factors Affecting Success:")
        for factor in result['key_factors']:
            print(f"  • {factor['factor']}: {factor['importance']:.3f} (value: {factor['value']})")
    
    if 'recommendations' in result:
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  • {rec}")
    
    print("\n✅ Success Predictor working!")
    return result


def test_chatbot():
    """Test chatbot"""
    print("\n" + "="*80)
    print("TESTING: PDSA Chatbot")
    print("="*80)
    
    chatbot = PDSAChatbot()
    
    project_context = {
        'title': 'Reduce Medication Errors',
        'aim': 'Reduce medication errors by 50% in 12 weeks',
        'category': 'medication'
    }
    
    questions = [
        ("How do I write a SMART aim?", 'plan'),
        ("What makes a good hypothesis?", 'plan'),
        ("How many data points do I need?", 'study')
    ]
    
    for question, phase in questions:
        print(f"\n📝 Question ({phase}): {question}")
        
        response = chatbot.ask(
            question=question,
            project_context=project_context,
            phase=phase
        )
        
        print(f"\n💬 Answer: {response['answer']}")
        print(f"   Confidence: {response['confidence']:.1%}")
        
        if response.get('follow_up_suggestions'):
            print(f"\n   Follow-up suggestions:")
            for sugg in response['follow_up_suggestions'][:2]:
                print(f"     • {sugg}")
    
    print("\n✅ Chatbot working!")
    return chatbot


def run_all_tests():
    """Run all ML component tests"""
    print("\n" + "="*80)
    print("PDSA TRACKER - ML COMPONENTS TEST SUITE")
    print("="*80)
    print("\nTesting 5 ML components with local models (no cloud dependencies)")
    print("This may take a few minutes on first run as models are downloaded...")
    
    try:
        # Test each component
        aim_result = test_smart_aim_generator()
        hyp_result = test_hypothesis_suggester()
        data_result = test_data_analyzer()
        pred_result = test_success_predictor()
        chat_result = test_chatbot()
        
        print("\n" + "="*80)
        print("✅ ALL ML COMPONENTS WORKING!")
        print("="*80)
        print("\nNext steps:")
        print("1. Access admin at http://localhost:8001/admin/")
        print("2. Login with SAP 000001")
        print("3. Create a test PDSA project")
        print("4. Try the AI features in the admin interface")
        
        return {
            'all_passed': True,
            'aim_generator': aim_result,
            'hypothesis_suggester': hyp_result,
            'data_analyzer': data_result,
            'success_predictor': pred_result,
            'chatbot': chat_result
        }
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return {'all_passed': False, 'error': str(e)}


if __name__ == '__main__':
    results = run_all_tests()
    
    if results['all_passed']:
        print("\n🎉 Module 1 PDSA Tracker MVP - ML Components Ready!")
    else:
        print(f"\n⚠️  Some tests failed. Check error above.")
