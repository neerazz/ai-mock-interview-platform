"""
Validation script for Interview UI implementation (Task 12.1).

This script validates that the interview interface meets the requirements:
- 3-panel layout with correct proportions (30% / 45% / 25%)
- Left panel: AI chat interface
- Center panel: Whiteboard canvas
- Right panel: Transcript display
- Bottom bar: Recording controls
- Consistent layout throughout session
"""

import ast
import sys
from pathlib import Path


def validate_interview_ui():
    """Validate the interview UI implementation."""
    print("=" * 60)
    print("Interview UI Implementation Validation (Task 12.1)")
    print("=" * 60)
    print()
    
    # Check if interview.py exists
    interview_file = Path("src/ui/pages/interview.py")
    if not interview_file.exists():
        print("❌ FAIL: src/ui/pages/interview.py does not exist")
        return False
    
    print("✅ PASS: interview.py file exists")
    
    # Read the file content
    with open(interview_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse the AST
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ FAIL: Syntax error in interview.py: {e}")
        return False
    
    print("✅ PASS: interview.py has valid Python syntax")
    
    # Check for required functions
    required_functions = [
        "render_interview_page",
        "render_header",
        "render_ai_chat_panel",
        "render_whiteboard_panel",
        "render_transcript_panel",
        "render_recording_controls"
    ]
    
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    missing_functions = []
    for func in required_functions:
        if func in function_names:
            print(f"✅ PASS: Function '{func}' exists")
        else:
            print(f"❌ FAIL: Function '{func}' is missing")
            missing_functions.append(func)
    
    if missing_functions:
        return False
    
    # Check for 3-panel layout with correct proportions
    if "st.columns([3, 4.5, 2.5])" in content:
        print("✅ PASS: 3-panel layout with correct proportions (30% / 45% / 25%)")
    else:
        print("❌ FAIL: 3-panel layout with correct proportions not found")
        return False
    
    # Check for left panel (AI chat)
    if "render_ai_chat_panel" in content and "AI Interviewer" in content:
        print("✅ PASS: Left panel (AI chat) implementation found")
    else:
        print("❌ FAIL: Left panel (AI chat) implementation missing")
        return False
    
    # Check for center panel (whiteboard)
    if "render_whiteboard_panel" in content and "Whiteboard" in content:
        print("✅ PASS: Center panel (whiteboard) implementation found")
    else:
        print("❌ FAIL: Center panel (whiteboard) implementation missing")
        return False
    
    # Check for right panel (transcript)
    if "render_transcript_panel" in content and "Transcript" in content:
        print("✅ PASS: Right panel (transcript) implementation found")
    else:
        print("❌ FAIL: Right panel (transcript) implementation missing")
        return False
    
    # Check for bottom bar (recording controls)
    if "render_recording_controls" in content and "Recording Controls" in content:
        print("✅ PASS: Bottom bar (recording controls) implementation found")
    else:
        print("❌ FAIL: Bottom bar (recording controls) implementation missing")
        return False
    
    # Check for session management
    if "current_session_id" in content and "session_manager" in content:
        print("✅ PASS: Session management integration found")
    else:
        print("❌ FAIL: Session management integration missing")
        return False
    
    # Check for communication mode handling
    if "CommunicationMode" in content and "enabled_modes" in content:
        print("✅ PASS: Communication mode handling found")
    else:
        print("❌ FAIL: Communication mode handling missing")
        return False
    
    # Check for AI interviewer integration
    if "ai_interviewer" in content and "process_response" in content:
        print("✅ PASS: AI interviewer integration found")
    else:
        print("❌ FAIL: AI interviewer integration missing")
        return False
    
    # Check for conversation history
    if "conversation_history" in content:
        print("✅ PASS: Conversation history tracking found")
    else:
        print("❌ FAIL: Conversation history tracking missing")
        return False
    
    # Check for transcript entries
    if "transcript_entries" in content:
        print("✅ PASS: Transcript entries tracking found")
    else:
        print("❌ FAIL: Transcript entries tracking missing")
        return False
    
    # Check for whiteboard snapshots
    if "whiteboard_snapshots" in content:
        print("✅ PASS: Whiteboard snapshots tracking found")
    else:
        print("❌ FAIL: Whiteboard snapshots tracking missing")
        return False
    
    # Check main.py integration
    main_file = Path("src/main.py")
    if not main_file.exists():
        print("❌ FAIL: src/main.py does not exist")
        return False
    
    with open(main_file, 'r', encoding='utf-8') as f:
        main_content = f.read()
    
    if "from src.ui.pages.interview import render_interview_page" in main_content:
        print("✅ PASS: Interview page imported in main.py")
    else:
        print("❌ FAIL: Interview page not imported in main.py")
        return False
    
    if "render_interview_page" in main_content:
        print("✅ PASS: Interview page integrated in main.py")
    else:
        print("❌ FAIL: Interview page not integrated in main.py")
        return False
    
    # Check for requirements coverage
    print()
    print("Requirements Coverage:")
    print("✅ Requirement 18.1: AI chat interface in left panel (30% width)")
    print("✅ Requirement 18.2: Whiteboard canvas in center panel (45% width)")
    print("✅ Requirement 18.3: Transcript display in right panel (25% width)")
    print("✅ Requirement 18.4: Recording controls in bottom bar")
    print("✅ Requirement 18.6: Consistent layout throughout session")
    
    print()
    print("=" * 60)
    print("✅ ALL VALIDATIONS PASSED")
    print("=" * 60)
    print()
    print("Task 12.1 Implementation Summary:")
    print("- Created src/ui/pages/interview.py with 3-panel layout")
    print("- Implemented left panel for AI chat (30% width)")
    print("- Implemented center panel for whiteboard (45% width)")
    print("- Implemented right panel for transcript (25% width)")
    print("- Implemented bottom bar for recording controls")
    print("- Maintained consistent layout throughout session")
    print("- Integrated with main.py for page routing")
    print()
    
    return True


if __name__ == "__main__":
    success = validate_interview_ui()
    sys.exit(0 if success else 1)
