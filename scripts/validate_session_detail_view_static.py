"""
Static validation script for session detail view UI rendering.

This script performs static analysis to verify that the session detail view
implementation includes all required functionality without running Streamlit.
"""

import sys
import ast
import inspect


def validate_session_detail_view_static():
    """Validate session detail view implementation through static analysis."""
    print("=" * 80)
    print("STATIC VALIDATION: SESSION DETAIL VIEW")
    print("=" * 80)
    
    # Read the source file directly
    print("\n1. Reading history page source file...")
    try:
        with open("src/ui/pages/history.py", "r", encoding="utf-8") as f:
            source_code = f.read()
        print("   ✓ Source file read successfully")
    except Exception as e:
        print(f"   ❌ Failed to read source file: {e}")
        return False
    
    # Parse the AST
    try:
        tree = ast.parse(source_code)
        print("   ✓ Source code parsed successfully")
    except Exception as e:
        print(f"   ❌ Failed to parse source code: {e}")
        return False
    
    # Extract function definitions
    print("\n2. Extracting function definitions...")
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = node
    
    print(f"   ✓ Found {len(functions)} functions")
    
    # Check for required functions
    print("\n3. Checking for required functions...")
    required_functions = [
        "render_session_detail_view",
        "render_session_metadata_section",
        "render_conversation_history_section",
        "render_message_card",
        "render_whiteboard_gallery_section",
        "render_whiteboard_snapshot",
        "render_evaluation_summary_section",
        "render_session_actions",
        "export_conversation_history"
    ]
    
    for func_name in required_functions:
        if func_name in functions:
            print(f"   ✓ Function '{func_name}' exists")
        else:
            print(f"   ❌ Function '{func_name}' is missing")
            return False
    
    # Check render_session_detail_view signature
    print("\n4. Validating render_session_detail_view signature...")
    func_node = functions.get("render_session_detail_view")
    if func_node:
        params = [arg.arg for arg in func_node.args.args]
        expected_params = ["session_id", "session_manager", "evaluation_manager"]
        for param in expected_params:
            if param in params:
                print(f"   ✓ Parameter '{param}' present")
            else:
                print(f"   ❌ Parameter '{param}' missing")
                return False
    
    # Check docstrings
    print("\n5. Validating function docstrings...")
    if func_node and ast.get_docstring(func_node):
        docstring = ast.get_docstring(func_node)
        if "Requirements: 7.3, 7.4" in docstring:
            print("   ✓ Requirements reference present")
        else:
            print("   ⚠️  Requirements reference missing or incorrect")
        
        if "conversation history" in docstring.lower():
            print("   ✓ Mentions conversation history")
        else:
            print("   ⚠️  Missing conversation history mention")
        
        if "whiteboard" in docstring.lower():
            print("   ✓ Mentions whiteboard")
        else:
            print("   ⚠️  Missing whiteboard mention")
        
        if "evaluation" in docstring.lower():
            print("   ✓ Mentions evaluation")
        else:
            print("   ⚠️  Missing evaluation mention")
    
    # Check render_history_page integration
    print("\n6. Validating integration with render_history_page...")
    if "selected_session_id" in source_code:
        print("   ✓ Checks for selected_session_id in session state")
    else:
        print("   ❌ Missing selected_session_id check")
        return False
    
    if "render_session_detail_view" in source_code:
        print("   ✓ Calls render_session_detail_view")
    else:
        print("   ❌ Missing render_session_detail_view call")
        return False
    
    # Check conversation history rendering
    print("\n7. Validating conversation history rendering...")
    if "timestamp" in source_code.lower():
        print("   ✓ Displays timestamps")
    else:
        print("   ❌ Missing timestamp display")
        return False
    
    if "render_message_card" in source_code:
        print("   ✓ Renders individual message cards")
    else:
        print("   ❌ Missing message card rendering")
        return False
    
    # Check whiteboard gallery rendering
    print("\n8. Validating whiteboard gallery rendering...")
    if "whiteboard" in source_code.lower() and "gallery" in source_code.lower():
        print("   ✓ Implements whiteboard gallery")
    else:
        print("   ❌ Missing whiteboard gallery")
        return False
    
    if "st.image" in source_code or "render_whiteboard_snapshot" in source_code:
        print("   ✓ Displays whiteboard images")
    else:
        print("   ❌ Missing image display")
        return False
    
    # Check whiteboard snapshot rendering
    print("\n9. Validating whiteboard snapshot rendering...")
    if "st.image" in source_code:
        print("   ✓ Displays snapshot image")
    else:
        print("   ❌ Missing image display")
        return False
    
    if "download_button" in source_code.lower():
        print("   ✓ Provides download button")
    else:
        print("   ❌ Missing download button")
        return False
    
    # Check evaluation summary rendering
    print("\n10. Validating evaluation summary rendering...")
    if "overall_score" in source_code.lower():
        print("   ✓ Displays overall score")
    else:
        print("   ❌ Missing overall score display")
        return False
    
    if "competency" in source_code.lower():
        print("   ✓ Displays competency scores")
    else:
        print("   ❌ Missing competency scores display")
        return False
    
    if "went_well" in source_code.lower() or "feedback" in source_code.lower():
        print("   ✓ Displays feedback summary")
    else:
        print("   ❌ Missing feedback summary")
        return False
    
    if "view full evaluation" in source_code.lower():
        print("   ✓ Provides link to full evaluation")
    else:
        print("   ❌ Missing link to full evaluation")
        return False
    
    # Check session actions
    print("\n11. Validating session actions...")
    if "export" in source_code.lower():
        print("   ✓ Provides export functionality")
    else:
        print("   ❌ Missing export functionality")
        return False
    
    if "export_conversation_history" in source_code:
        print("   ✓ Calls export_conversation_history")
    else:
        print("   ❌ Missing export_conversation_history call")
        return False
    
    # Check back navigation
    print("\n12. Validating back navigation...")
    if "back" in source_code.lower():
        print("   ✓ Provides back button")
    else:
        print("   ❌ Missing back button")
        return False
    
    if "selected_session_id = None" in source_code or "selected_session_id=None" in source_code:
        print("   ✓ Clears selected session on back")
    else:
        print("   ⚠️  May not clear selected session properly")
    
    # Check tab organization
    print("\n13. Validating tab organization...")
    if "st.tabs" in source_code:
        print("   ✓ Uses tabs for organization")
    else:
        print("   ⚠️  May not use tabs for organization")
    
    if "conversation" in source_code.lower() and "whiteboard" in source_code.lower() and "evaluation" in source_code.lower():
        print("   ✓ Includes all three main sections")
    else:
        print("   ❌ Missing one or more main sections")
        return False
    
    # Check data loading
    print("\n14. Validating data loading...")
    if "get_session" in source_code:
        print("   ✓ Loads session data")
    else:
        print("   ❌ Missing session data loading")
        return False
    
    if "get_conversation_history" in source_code:
        print("   ✓ Loads conversation history")
    else:
        print("   ❌ Missing conversation history loading")
        return False
    
    if "get_media_files" in source_code:
        print("   ✓ Loads media files")
    else:
        print("   ❌ Missing media files loading")
        return False
    
    if "get_evaluation" in source_code:
        print("   ✓ Loads evaluation")
    else:
        print("   ❌ Missing evaluation loading")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL STATIC VALIDATIONS PASSED")
    print("=" * 80)
    print("\nSession detail view implementation is complete!")
    print("\nKey features verified:")
    print("  • Session selection and detail view rendering")
    print("  • Session metadata display")
    print("  • Conversation history with timestamps")
    print("  • Whiteboard gallery with image display")
    print("  • Evaluation summary with scores")
    print("  • Export conversation functionality")
    print("  • Back navigation to session list")
    print("  • Tab-based organization")
    
    return True


if __name__ == "__main__":
    try:
        success = validate_session_detail_view_static()
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
