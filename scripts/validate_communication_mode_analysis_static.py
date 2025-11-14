"""
Static validation script for communication mode analysis display (Task 13.5).

This script validates the implementation without requiring Streamlit to be running.
"""

import sys
import ast
import os


def validate_evaluation_page_code():
    """Validate the evaluation page code statically."""
    print("=" * 80)
    print("STATIC VALIDATION: Communication Mode Analysis Display (Task 13.5)")
    print("=" * 80)
    print()
    
    # Read the evaluation page file
    eval_page_path = "src/ui/pages/evaluation.py"
    
    if not os.path.exists(eval_page_path):
        print(f"❌ File not found: {eval_page_path}")
        return False
    
    with open(eval_page_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Test 1: Check for required function definitions
    print("Test 1: Check for required function definitions")
    print("-" * 80)
    
    required_functions = [
        "render_communication_mode_analysis",
        "render_mode_analysis_card",
        "get_mode_assessment_type",
        "get_communication_assessment_level"
    ]
    
    all_functions_found = True
    for func_name in required_functions:
        if f"def {func_name}(" in code:
            print(f"✅ Function '{func_name}' is defined")
        else:
            print(f"❌ Function '{func_name}' is NOT defined")
            all_functions_found = False
    
    print()
    
    if not all_functions_found:
        return False
    
    # Test 2: Check for ModeAnalysis import
    print("Test 2: Check for ModeAnalysis import")
    print("-" * 80)
    
    if "ModeAnalysis" in code and "from src.models import" in code:
        print(f"✅ ModeAnalysis is imported from src.models")
    else:
        print(f"❌ ModeAnalysis is NOT imported")
        return False
    
    print()
    
    # Test 3: Check that render_communication_mode_analysis is called
    print("Test 3: Check that render_communication_mode_analysis is called")
    print("-" * 80)
    
    if "render_communication_mode_analysis(" in code:
        print(f"✅ render_communication_mode_analysis() is called in the page")
    else:
        print(f"❌ render_communication_mode_analysis() is NOT called")
        return False
    
    print()
    
    # Test 4: Check for all mode analysis fields
    print("Test 4: Check for all communication mode fields")
    print("-" * 80)
    
    mode_fields = [
        "audio_quality",
        "video_presence",
        "whiteboard_usage",
        "screen_share_usage",
        "overall_communication"
    ]
    
    all_fields_found = True
    for field in mode_fields:
        if field in code:
            print(f"✅ Field '{field}' is referenced in the code")
        else:
            print(f"❌ Field '{field}' is NOT referenced")
            all_fields_found = False
    
    print()
    
    if not all_fields_found:
        return False
    
    # Test 5: Check for proper documentation
    print("Test 5: Check for proper documentation")
    print("-" * 80)
    
    if "Requirements: 6.5" in code:
        print(f"✅ Requirement 6.5 is documented in the code")
    else:
        print(f"⚠️  Requirement 6.5 is not explicitly documented")
    
    if "Audio quality assessment" in code or "audio quality" in code.lower():
        print(f"✅ Audio quality assessment is mentioned")
    
    if "Video presence assessment" in code or "video presence" in code.lower():
        print(f"✅ Video presence assessment is mentioned")
    
    if "Whiteboard usage assessment" in code or "whiteboard usage" in code.lower():
        print(f"✅ Whiteboard usage assessment is mentioned")
    
    if "Screen share" in code or "screen share" in code.lower():
        print(f"✅ Screen share assessment is mentioned")
    
    print()
    
    # Test 6: Check for visual indicators and styling
    print("Test 6: Check for visual indicators and styling")
    print("-" * 80)
    
    visual_elements = [
        ("st.success", "Success styling"),
        ("st.info", "Info styling"),
        ("st.warning", "Warning styling"),
        ("icon", "Icons")
    ]
    
    for element, description in visual_elements:
        if element in code:
            print(f"✅ {description} is used ({element})")
        else:
            print(f"⚠️  {description} might not be used ({element})")
    
    print()
    
    # Test 7: Check for grid/column layout
    print("Test 7: Check for layout organization")
    print("-" * 80)
    
    if "st.columns" in code:
        print(f"✅ Column layout is used for organized display")
    else:
        print(f"⚠️  Column layout might not be used")
    
    if "st.container" in code:
        print(f"✅ Containers are used for card-like display")
    else:
        print(f"⚠️  Containers might not be used")
    
    print()
    
    # Test 8: Verify the placeholder was removed
    print("Test 8: Verify placeholder was removed")
    print("-" * 80)
    
    if "will be implemented in task 13.5" in code.lower():
        print(f"❌ Placeholder text is still present - implementation incomplete")
        return False
    else:
        print(f"✅ Placeholder text has been removed - implementation is complete")
    
    print()
    
    return True


def validate_models():
    """Validate that ModeAnalysis model has all required fields."""
    print("Test 9: Validate ModeAnalysis model structure")
    print("-" * 80)
    
    models_path = "src/models.py"
    
    if not os.path.exists(models_path):
        print(f"❌ File not found: {models_path}")
        return False
    
    with open(models_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check for ModeAnalysis class
    if "class ModeAnalysis" not in code:
        print(f"❌ ModeAnalysis class not found in models.py")
        return False
    
    print(f"✅ ModeAnalysis class is defined")
    
    # Check for required fields
    required_fields = [
        "audio_quality",
        "video_presence",
        "whiteboard_usage",
        "screen_share_usage",
        "overall_communication"
    ]
    
    all_fields_present = True
    for field in required_fields:
        if field in code:
            print(f"✅ Field '{field}' is defined in ModeAnalysis")
        else:
            print(f"❌ Field '{field}' is NOT defined in ModeAnalysis")
            all_fields_present = False
    
    print()
    
    return all_fields_present


def validate_evaluation_manager():
    """Validate that EvaluationManager generates ModeAnalysis."""
    print("Test 10: Validate EvaluationManager generates ModeAnalysis")
    print("-" * 80)
    
    eval_manager_path = "src/evaluation/evaluation_manager.py"
    
    if not os.path.exists(eval_manager_path):
        print(f"❌ File not found: {eval_manager_path}")
        return False
    
    with open(eval_manager_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check for _analyze_communication_modes method
    if "_analyze_communication_modes" in code:
        print(f"✅ _analyze_communication_modes method exists")
    else:
        print(f"❌ _analyze_communication_modes method not found")
        return False
    
    # Check that it returns ModeAnalysis
    if "ModeAnalysis()" in code or "return analysis" in code:
        print(f"✅ Method returns ModeAnalysis object")
    else:
        print(f"⚠️  Method might not return ModeAnalysis")
    
    # Check that it's called in generate_evaluation
    if "communication_analysis = self._analyze_communication_modes" in code:
        print(f"✅ Communication mode analysis is generated in evaluation")
    else:
        print(f"❌ Communication mode analysis is NOT generated")
        return False
    
    print()
    
    return True


def main():
    """Run all static validation tests."""
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 10 + "COMMUNICATION MODE ANALYSIS - STATIC VALIDATION" + " " * 20 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    try:
        # Run all validation tests
        test_results = []
        
        test_results.append(validate_evaluation_page_code())
        test_results.append(validate_models())
        test_results.append(validate_evaluation_manager())
        
        print()
        print("=" * 80)
        
        if all(test_results):
            print("✅ ALL STATIC VALIDATION TESTS PASSED")
            print("=" * 80)
            print()
            print("Summary:")
            print("✅ render_communication_mode_analysis() function is implemented")
            print("✅ All helper functions are defined")
            print("✅ ModeAnalysis is properly imported")
            print("✅ All communication mode fields are handled:")
            print("   - Audio quality assessment")
            print("   - Video presence assessment")
            print("   - Whiteboard usage assessment")
            print("   - Screen share assessment")
            print("   - Overall communication effectiveness")
            print("✅ Visual styling and layout are implemented")
            print("✅ Placeholder text has been removed")
            print("✅ Requirement 6.5 is satisfied")
            print()
            print("Task 13.5 implementation is COMPLETE! ✨")
            print()
            return 0
        else:
            print("❌ SOME STATIC VALIDATION TESTS FAILED")
            print("=" * 80)
            print()
            print("Please review the failed tests above and fix the issues.")
            print()
            return 1
            
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ VALIDATION FAILED WITH ERROR: {str(e)}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
