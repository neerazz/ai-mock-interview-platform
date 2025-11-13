"""
Validation script for evaluation page structure (Task 13.1).

This script validates that the evaluation page structure is correctly implemented
with proper layout, header, sections, and navigation.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def validate_evaluation_page_structure():
    """Validate evaluation page structure implementation."""
    print("=" * 80)
    print("VALIDATION: Evaluation Page Structure (Task 13.1)")
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
    
    # Test 2: Check if file can be imported
    print("\nTest 2: Checking if evaluation module can be imported...")
    try:
        from ui.pages.evaluation import render_evaluation_page
        print("✅ PASS: evaluation module imports successfully")
        results.append(True)
    except ImportError as e:
        print(f"❌ FAIL: Cannot import evaluation module: {e}")
        results.append(False)
        return results
    
    # Test 3: Check if render_evaluation_page function exists
    print("\nTest 3: Checking if render_evaluation_page function exists...")
    try:
        from ui.pages.evaluation import render_evaluation_page
        if callable(render_evaluation_page):
            print("✅ PASS: render_evaluation_page function exists and is callable")
            results.append(True)
        else:
            print("❌ FAIL: render_evaluation_page is not callable")
            results.append(False)
    except Exception as e:
        print(f"❌ FAIL: Error checking render_evaluation_page: {e}")
        results.append(False)
    
    # Test 4: Check if helper functions exist
    print("\nTest 4: Checking if helper functions exist...")
    try:
        from ui.pages.evaluation import (
            render_empty_state,
            render_generate_evaluation_prompt,
            render_loading_state,
            render_evaluation_report,
            render_navigation_section
        )
        print("✅ PASS: All helper functions exist")
        results.append(True)
    except ImportError as e:
        print(f"❌ FAIL: Missing helper functions: {e}")
        results.append(False)
    
    # Test 5: Check if main.py is updated
    print("\nTest 5: Checking if main.py imports evaluation page...")
    try:
        with open("src/main.py", "r") as f:
            main_content = f.read()
            if "from src.ui.pages.evaluation import render_evaluation_page" in main_content:
                print("✅ PASS: main.py imports evaluation page")
                results.append(True)
            else:
                print("❌ FAIL: main.py does not import evaluation page")
                results.append(False)
    except Exception as e:
        print(f"❌ FAIL: Error checking main.py: {e}")
        results.append(False)
    
    # Test 6: Check if main.py calls render_evaluation_page
    print("\nTest 6: Checking if main.py calls render_evaluation_page...")
    try:
        with open("src/main.py", "r") as f:
            main_content = f.read()
            if 'render_evaluation_page(' in main_content:
                print("✅ PASS: main.py calls render_evaluation_page")
                results.append(True)
            else:
                print("❌ FAIL: main.py does not call render_evaluation_page")
                results.append(False)
    except Exception as e:
        print(f"❌ FAIL: Error checking main.py: {e}")
        results.append(False)
    
    # Test 7: Check file structure and content
    print("\nTest 7: Checking evaluation.py content structure...")
    try:
        with open(evaluation_file, "r") as f:
            content = f.read()
            
            checks = [
                ("Page header with title", 'st.title("📊 Interview Evaluation")' in content),
                ("Empty state handling", 'render_empty_state()' in content),
                ("Navigation section", 'render_navigation_section()' in content),
                ("Session ID check", 'st.session_state.get("current_session_id")' in content),
                ("Evaluation report display", 'render_evaluation_report(evaluation_report)' in content),
                ("Navigation to setup", 'st.session_state.current_page = "setup"' in content),
                ("Navigation to history", 'st.session_state.current_page = "history"' in content),
            ]
            
            all_passed = True
            for check_name, check_result in checks:
                if check_result:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ❌ {check_name}")
                    all_passed = False
            
            if all_passed:
                print("✅ PASS: All content structure checks passed")
                results.append(True)
            else:
                print("❌ FAIL: Some content structure checks failed")
                results.append(False)
    except Exception as e:
        print(f"❌ FAIL: Error checking file content: {e}")
        results.append(False)
    
    # Test 8: Check docstrings
    print("\nTest 8: Checking if functions have proper docstrings...")
    try:
        with open(evaluation_file, "r") as f:
            content = f.read()
            
            required_docstrings = [
                'render_evaluation_page',
                'render_empty_state',
                'render_generate_evaluation_prompt',
                'render_loading_state',
                'render_evaluation_report',
                'render_navigation_section'
            ]
            
            all_have_docstrings = True
            for func_name in required_docstrings:
                # Simple check: function definition followed by docstring
                if f'def {func_name}' in content:
                    # Check if there's a docstring after the function
                    func_pos = content.find(f'def {func_name}')
                    next_section = content[func_pos:func_pos+500]
                    if '"""' in next_section:
                        print(f"  ✅ {func_name} has docstring")
                    else:
                        print(f"  ❌ {func_name} missing docstring")
                        all_have_docstrings = False
            
            if all_have_docstrings:
                print("✅ PASS: All functions have docstrings")
                results.append(True)
            else:
                print("❌ FAIL: Some functions missing docstrings")
                results.append(False)
    except Exception as e:
        print(f"❌ FAIL: Error checking docstrings: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - Task 13.1 implementation is complete!")
        return True
    else:
        print(f"❌ SOME TESTS FAILED - {total - passed} test(s) need attention")
        return False


if __name__ == "__main__":
    success = validate_evaluation_page_structure()
    sys.exit(0 if success else 1)
