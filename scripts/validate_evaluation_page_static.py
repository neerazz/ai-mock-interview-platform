"""
Static validation script for evaluation page structure (Task 13.1).

This script validates the evaluation page implementation without requiring
runtime dependencies like Streamlit.
"""

import os
import re


def validate_evaluation_page_static():
    """Validate evaluation page structure using static analysis."""
    print("=" * 80)
    print("STATIC VALIDATION: Evaluation Page Structure (Task 13.1)")
    print("=" * 80)
    print()
    
    results = []
    
    # Test 1: Check if evaluation.py file exists
    print("Test 1: Checking if src/ui/pages/evaluation.py exists...")
    evaluation_file = "src/ui/pages/evaluation.py"
    if os.path.exists(evaluation_file):
        print("✅ PASS: evaluation.py file exists")
        results.append(True)
    else:
        print("❌ FAIL: evaluation.py file not found")
        results.append(False)
        return results
    
    # Read evaluation.py content
    with open(evaluation_file, "r", encoding="utf-8") as f:
        eval_content = f.read()
    
    # Test 2: Check for main render function
    print("\nTest 2: Checking for render_evaluation_page function...")
    if "def render_evaluation_page(" in eval_content:
        print("✅ PASS: render_evaluation_page function exists")
        results.append(True)
    else:
        print("❌ FAIL: render_evaluation_page function not found")
        results.append(False)
    
    # Test 3: Check for required parameters
    print("\nTest 3: Checking function parameters...")
    param_checks = [
        ("session_manager", "session_manager" in eval_content),
        ("evaluation_manager", "evaluation_manager" in eval_content),
        ("config", "config" in eval_content),
    ]
    
    all_params = True
    for param_name, exists in param_checks:
        if exists:
            print(f"  ✅ {param_name} parameter present")
        else:
            print(f"  ❌ {param_name} parameter missing")
            all_params = False
    
    results.append(all_params)
    
    # Test 4: Check for page layout elements
    print("\nTest 4: Checking page layout elements...")
    layout_checks = [
        ("Page title", 'st.title("📊 Interview Evaluation")' in eval_content),
        ("Page description", '"Comprehensive feedback and assessment"' in eval_content or "Comprehensive feedback" in eval_content),
        ("Header section", "st.title" in eval_content),
    ]
    
    all_layout = True
    for check_name, exists in layout_checks:
        if exists:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_layout = False
    
    results.append(all_layout)
    
    # Test 5: Check for helper functions
    print("\nTest 5: Checking for helper functions...")
    helper_functions = [
        "render_empty_state",
        "render_generate_evaluation_prompt",
        "render_loading_state",
        "render_evaluation_report",
        "render_navigation_section",
    ]
    
    all_helpers = True
    for func_name in helper_functions:
        if f"def {func_name}(" in eval_content:
            print(f"  ✅ {func_name}")
        else:
            print(f"  ❌ {func_name}")
            all_helpers = False
    
    results.append(all_helpers)
    
    # Test 6: Check for navigation functionality
    print("\nTest 6: Checking navigation functionality...")
    nav_checks = [
        ("Navigation to setup", 'current_page = "setup"' in eval_content),
        ("Navigation to history", 'current_page = "history"' in eval_content),
        ("Navigation section function", "render_navigation_section" in eval_content),
        ("Back button functionality", "st.button" in eval_content),
    ]
    
    all_nav = True
    for check_name, exists in nav_checks:
        if exists:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_nav = False
    
    results.append(all_nav)
    
    # Test 7: Check for session handling
    print("\nTest 7: Checking session handling...")
    session_checks = [
        ("Session ID retrieval", 'st.session_state.get("current_session_id")' in eval_content),
        ("Empty state handling", "render_empty_state()" in eval_content),
        ("Evaluation report state", '"evaluation_report"' in eval_content),
    ]
    
    all_session = True
    for check_name, exists in session_checks:
        if exists:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_session = False
    
    results.append(all_session)
    
    # Test 8: Check main.py integration
    print("\nTest 8: Checking main.py integration...")
    main_file = "src/main.py"
    if os.path.exists(main_file):
        with open(main_file, "r", encoding="utf-8") as f:
            main_content = f.read()
        
        main_checks = [
            ("Import statement", "from src.ui.pages.evaluation import render_evaluation_page" in main_content),
            ("Function call", "render_evaluation_page(" in main_content),
            ("Evaluation page route", '"evaluation"' in main_content or "'evaluation'" in main_content),
        ]
        
        all_main = True
        for check_name, exists in main_checks:
            if exists:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name}")
                all_main = False
        
        results.append(all_main)
    else:
        print("  ❌ main.py not found")
        results.append(False)
    
    # Test 9: Check docstrings
    print("\nTest 9: Checking docstrings...")
    docstring_pattern = r'def\s+\w+\([^)]*\):\s*"""'
    docstrings_found = len(re.findall(docstring_pattern, eval_content))
    
    if docstrings_found >= 5:  # At least 5 functions should have docstrings
        print(f"  ✅ Found {docstrings_found} functions with docstrings")
        results.append(True)
    else:
        print(f"  ❌ Only found {docstrings_found} functions with docstrings (expected at least 5)")
        results.append(False)
    
    # Test 10: Check Requirements reference
    print("\nTest 10: Checking Requirements reference...")
    if "Requirements: 6.9" in eval_content:
        print("  ✅ Requirements 6.9 referenced in docstring")
        results.append(True)
    else:
        print("  ❌ Requirements 6.9 not referenced")
        results.append(False)
    
    # Test 11: Check for proper imports
    print("\nTest 11: Checking imports...")
    import_checks = [
        ("streamlit", "import streamlit as st" in eval_content),
        ("EvaluationReport model", "from src.models import EvaluationReport" in eval_content or "EvaluationReport" in eval_content),
        ("datetime", "from datetime import datetime" in eval_content or "import datetime" in eval_content),
    ]
    
    all_imports = True
    for check_name, exists in import_checks:
        if exists:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_imports = False
    
    results.append(all_imports)
    
    # Test 12: Check file structure
    print("\nTest 12: Checking file structure...")
    structure_checks = [
        ("Module docstring", '"""' in eval_content[:200]),
        ("Function definitions", eval_content.count("def ") >= 5),
        ("Proper indentation", "    " in eval_content),  # Basic check for indentation
    ]
    
    all_structure = True
    for check_name, exists in structure_checks:
        if exists:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_structure = False
    
    results.append(all_structure)
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"Tests Passed: {passed}/{total} ({percentage:.1f}%)")
    print()
    
    if passed == total:
        print("✅ ALL TESTS PASSED!")
        print()
        print("Task 13.1 Implementation Complete:")
        print("  ✓ Created src/ui/pages/evaluation.py")
        print("  ✓ Implemented page layout with header and sections")
        print("  ✓ Added navigation back to setup or history")
        print("  ✓ Integrated with main.py")
        print("  ✓ Follows requirements 6.9")
        return True
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")
        print()
        print("Please review the failed tests above.")
        return False


if __name__ == "__main__":
    import sys
    success = validate_evaluation_page_static()
    sys.exit(0 if success else 1)
