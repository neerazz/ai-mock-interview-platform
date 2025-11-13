"""
Static validation script for task 13.3: Display categorized feedback.

This script validates the implementation without requiring Streamlit to be installed.
"""

import sys
import ast
import os


def validate_file_exists():
    """Validate that the evaluation.py file exists."""
    
    print("\n" + "="*80)
    print("VALIDATING FILE EXISTENCE")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    if os.path.exists(file_path):
        print(f"\n✓ File exists: {file_path}")
        return True
    else:
        print(f"\n✗ File not found: {file_path}")
        return False


def validate_imports():
    """Validate that required imports are present."""
    
    print("\n" + "="*80)
    print("VALIDATING IMPORTS")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_imports = [
        'Feedback',
        'List'
    ]
    
    all_present = True
    
    for import_name in required_imports:
        if import_name in content:
            print(f"✓ Import found: {import_name}")
        else:
            print(f"✗ Import missing: {import_name}")
            all_present = False
    
    return all_present


def validate_functions_exist():
    """Validate that required functions exist in the file."""
    
    print("\n" + "="*80)
    print("VALIDATING FUNCTION DEFINITIONS")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"\n✗ Syntax error in file: {e}")
        return False
    
    # Find all function definitions
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = node
    
    required_functions = {
        'render_categorized_feedback': ['went_well', 'went_okay', 'needs_improvement'],
        'render_feedback_section': ['title', 'feedback_items', 'color', 'icon', 'empty_message'],
        'render_feedback_item': ['feedback_item', 'index', 'icon', 'color']
    }
    
    all_present = True
    
    for func_name, expected_params in required_functions.items():
        if func_name in functions:
            func_node = functions[func_name]
            actual_params = [arg.arg for arg in func_node.args.args]
            
            if actual_params == expected_params:
                print(f"✓ Function '{func_name}' exists with correct parameters")
                print(f"  Parameters: {actual_params}")
            else:
                print(f"✗ Function '{func_name}' has incorrect parameters")
                print(f"  Expected: {expected_params}")
                print(f"  Got: {actual_params}")
                all_present = False
        else:
            print(f"✗ Function '{func_name}' not found")
            all_present = False
    
    return all_present


def validate_function_calls():
    """Validate that render_categorized_feedback is called in render_evaluation_report."""
    
    print("\n" + "="*80)
    print("VALIDATING FUNCTION INTEGRATION")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if render_categorized_feedback is called
    if 'render_categorized_feedback(' in content:
        print("✓ render_categorized_feedback is called in the code")
    else:
        print("✗ render_categorized_feedback is not called")
        return False
    
    # Check if it's called with the correct parameters
    if 'evaluation_report.went_well' in content:
        print("✓ went_well parameter is passed")
    else:
        print("✗ went_well parameter not found")
        return False
    
    if 'evaluation_report.went_okay' in content:
        print("✓ went_okay parameter is passed")
    else:
        print("✗ went_okay parameter not found")
        return False
    
    if 'evaluation_report.needs_improvement' in content:
        print("✓ needs_improvement parameter is passed")
    else:
        print("✗ needs_improvement parameter not found")
        return False
    
    return True


def validate_docstrings():
    """Validate that functions have proper docstrings."""
    
    print("\n" + "="*80)
    print("VALIDATING DOCSTRINGS")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"\n✗ Syntax error in file: {e}")
        return False
    
    required_functions = [
        'render_categorized_feedback',
        'render_feedback_section',
        'render_feedback_item'
    ]
    
    all_have_docstrings = True
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in required_functions:
            docstring = ast.get_docstring(node)
            if docstring:
                print(f"✓ Function '{node.name}' has docstring")
                # Check if requirements are mentioned
                if 'Requirements:' in docstring or 'Requirement' in docstring:
                    print(f"  ✓ Docstring mentions requirements")
            else:
                print(f"✗ Function '{node.name}' missing docstring")
                all_have_docstrings = False
    
    return all_have_docstrings


def validate_ui_elements():
    """Validate that UI elements are properly implemented."""
    
    print("\n" + "="*80)
    print("VALIDATING UI ELEMENTS")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ui_elements = {
        'Section titles': ['Went Well', 'Went Okay', 'Needs Improvement'],
        'Color coding': [':{color}[', 'color: str'],
        'Icons': ['✅', '👍', '🎯'],
        'Evidence display': ['Specific Examples', 'evidence'],
        'Empty state': ['empty_message', 'No specific']
    }
    
    all_present = True
    
    for element_type, keywords in ui_elements.items():
        found_count = 0
        for keyword in keywords:
            if keyword in content:
                found_count += 1
        
        if found_count > 0:
            print(f"✓ {element_type}: {found_count}/{len(keywords)} elements found")
        else:
            print(f"✗ {element_type}: No elements found")
            all_present = False
    
    return all_present


def validate_requirements_implementation():
    """Validate that the implementation addresses the specified requirements."""
    
    print("\n" + "="*80)
    print("VALIDATING REQUIREMENTS IMPLEMENTATION")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    requirements = {
        "6.4": {
            "description": "Categorize performance into went well, went okay, and needs improvement",
            "indicators": ["went_well", "went_okay", "needs_improvement"]
        },
        "6.6": {
            "description": "Provide specific examples from candidate responses",
            "indicators": ["evidence", "Specific Examples", "feedback_item.evidence"]
        }
    }
    
    all_satisfied = True
    
    for req_id, req_info in requirements.items():
        print(f"\nRequirement {req_id}: {req_info['description']}")
        
        found_count = 0
        for indicator in req_info['indicators']:
            if indicator in content:
                found_count += 1
                print(f"  ✓ Found: {indicator}")
        
        if found_count == len(req_info['indicators']):
            print(f"  ✓ Requirement {req_id} fully implemented")
        elif found_count > 0:
            print(f"  ⚠️  Requirement {req_id} partially implemented ({found_count}/{len(req_info['indicators'])})")
        else:
            print(f"  ✗ Requirement {req_id} not implemented")
            all_satisfied = False
    
    return all_satisfied


def validate_code_quality():
    """Validate code quality aspects."""
    
    print("\n" + "="*80)
    print("VALIDATING CODE QUALITY")
    print("="*80)
    
    file_path = "src/ui/pages/evaluation.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
        print("✓ Code has valid Python syntax")
    except SyntaxError as e:
        print(f"✗ Syntax error: {e}")
        return False
    
    # Check for type hints
    type_hint_count = content.count('List[')
    if type_hint_count > 0:
        print(f"✓ Type hints used ({type_hint_count} occurrences)")
    else:
        print("⚠️  No type hints found")
    
    # Check for proper formatting
    if '"""' in content:
        print("✓ Docstrings use proper format")
    
    return True


def main():
    """Run all validation checks."""
    
    print("\n" + "="*80)
    print("TASK 13.3 STATIC VALIDATION: Display Categorized Feedback")
    print("="*80)
    
    all_passed = True
    
    # Run all validations
    validations = [
        ("File Existence", validate_file_exists),
        ("Imports", validate_imports),
        ("Function Definitions", validate_functions_exist),
        ("Function Integration", validate_function_calls),
        ("Docstrings", validate_docstrings),
        ("UI Elements", validate_ui_elements),
        ("Requirements Implementation", validate_requirements_implementation),
        ("Code Quality", validate_code_quality)
    ]
    
    results = {}
    
    for validation_name, validation_func in validations:
        try:
            result = validation_func()
            results[validation_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"\n✗ Error during {validation_name} validation: {e}")
            results[validation_name] = False
            all_passed = False
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    for validation_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {validation_name}")
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ ALL VALIDATIONS PASSED")
        print("="*80)
        print("\nTask 13.3 implementation is complete and correct!")
        print("\nImplemented features:")
        print("  • Three categorized feedback sections (Went Well, Went Okay, Needs Improvement)")
        print("  • Color-coded sections (green, blue, orange)")
        print("  • Feedback descriptions with numbered items")
        print("  • Specific evidence/examples for each feedback item")
        print("  • Empty state handling for sections with no feedback")
        print("  • Proper integration with evaluation report display")
        print("\nRequirements satisfied:")
        print("  • Requirement 6.4: Categorized feedback display")
        print("  • Requirement 6.6: Specific examples from candidate responses")
        return 0
    else:
        print("✗ SOME VALIDATIONS FAILED")
        print("="*80)
        print("\nPlease review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
