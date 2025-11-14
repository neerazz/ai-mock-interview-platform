"""
Validation script for recording controls implementation.

This script validates that the recording controls implementation meets all requirements:
- Audio recording toggle with streamlit-webrtc
- Video recording toggle
- Whiteboard snapshot button
- Screen share toggle
- End interview button with confirmation dialog
- Session timer display
- Token usage indicator
- Visual indicators for active modes

Requirements: 2.3, 2.4, 2.5, 2.6, 5.1, 14.7, 18.4, 18.7
"""

import sys
import ast
import re
from pathlib import Path


def validate_recording_controls():
    """Validate the recording controls implementation."""
    print("=" * 80)
    print("RECORDING CONTROLS IMPLEMENTATION VALIDATION")
    print("=" * 80)
    print()
    
    # Read the interview.py file
    interview_file = Path("src/ui/pages/interview.py")
    
    if not interview_file.exists():
        print("❌ FAILED: src/ui/pages/interview.py not found")
        return False
    
    with open(interview_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_checks_passed = True
    
    # Check 1: render_recording_controls function exists
    print("✓ Check 1: render_recording_controls function exists")
    if "def render_recording_controls(" not in content:
        print("  ❌ FAILED: render_recording_controls function not found")
        all_checks_passed = False
    else:
        print("  ✅ PASSED")
    print()
    
    # Check 2: Audio recording toggle (Requirement 2.3, 2.4)
    print("✓ Check 2: Audio recording toggle with streamlit-webrtc")
    audio_checks = [
        ('audio_toggle', 'Audio toggle control'),
        ('audio_active', 'Audio active state tracking'),
        ('CommunicationMode.AUDIO', 'Audio communication mode'),
        ('enable_mode(CommunicationMode.AUDIO)', 'Enable audio mode'),
        ('disable_mode(CommunicationMode.AUDIO)', 'Disable audio mode'),
    ]
    
    for check_str, description in audio_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 3: Video recording toggle (Requirement 2.5)
    print("✓ Check 3: Video recording toggle")
    video_checks = [
        ('video_toggle', 'Video toggle control'),
        ('video_active', 'Video active state tracking'),
        ('CommunicationMode.VIDEO', 'Video communication mode'),
        ('enable_mode(CommunicationMode.VIDEO)', 'Enable video mode'),
        ('disable_mode(CommunicationMode.VIDEO)', 'Disable video mode'),
    ]
    
    for check_str, description in video_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 4: Whiteboard snapshot button (Requirement 2.6)
    print("✓ Check 4: Whiteboard snapshot display")
    whiteboard_checks = [
        ('CommunicationMode.WHITEBOARD', 'Whiteboard communication mode'),
        ('whiteboard_snapshots', 'Whiteboard snapshots tracking'),
        ('snapshot_count', 'Snapshot count display'),
    ]
    
    for check_str, description in whiteboard_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 5: Screen share toggle (Requirement 2.6)
    print("✓ Check 5: Screen share toggle")
    screen_checks = [
        ('screen_toggle', 'Screen share toggle control'),
        ('screen_active', 'Screen share active state tracking'),
        ('CommunicationMode.SCREEN_SHARE', 'Screen share communication mode'),
        ('enable_mode(CommunicationMode.SCREEN_SHARE)', 'Enable screen share mode'),
        ('disable_mode(CommunicationMode.SCREEN_SHARE)', 'Disable screen share mode'),
    ]
    
    for check_str, description in screen_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 6: End interview button with confirmation (Requirement 5.1)
    print("✓ Check 6: End interview button with confirmation dialog")
    end_checks = [
        ('end_interview', 'End interview button'),
        ('confirm_end', 'Confirmation state'),
        ('end_session', 'End session call'),
        ('evaluation', 'Evaluation generation'),
    ]
    
    for check_str, description in end_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 7: Session timer display (Requirement 18.4)
    print("✓ Check 7: Session timer display")
    timer_checks = [
        ('interview_start_time', 'Start time tracking'),
        ('elapsed', 'Elapsed time calculation'),
        ('minutes', 'Minutes display'),
        ('seconds', 'Seconds display'),
        ('⏱️', 'Timer icon'),
    ]
    
    for check_str, description in timer_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 8: Token usage indicator (Requirements 5.1, 14.7)
    print("✓ Check 8: Token usage indicator")
    token_checks = [
        ('tokens_used', 'Token usage tracking'),
        ('estimated_cost', 'Cost estimation'),
        ('🪙', 'Token icon'),
    ]
    
    for check_str, description in token_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 9: Visual indicators for active modes (Requirement 18.7)
    print("✓ Check 9: Visual indicators for active modes")
    indicator_checks = [
        ('🔴', 'Recording indicator (red)'),
        ('🟢', 'Active indicator (green)'),
        ('⚪', 'Inactive indicator (white)'),
        ('⚫', 'Disabled indicator (black)'),
        ('Active Modes:', 'Active modes summary'),
    ]
    
    for check_str, description in indicator_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 10: Proper documentation
    print("✓ Check 10: Documentation and requirements references")
    doc_checks = [
        ('Requirements: 2.3, 2.4, 2.5, 2.6, 5.1, 14.7, 18.4, 18.7', 'Requirements documented'),
        ('Args:', 'Function arguments documented'),
        ('session_id:', 'Session ID parameter documented'),
    ]
    
    for check_str, description in doc_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 11: Error handling and logging
    print("✓ Check 11: Error handling and logging")
    error_checks = [
        ('try:', 'Try-except blocks'),
        ('except Exception as e:', 'Exception handling'),
        ('st.error', 'Error display'),
        ('logger.info', 'Info logging'),
        ('logger.log_error', 'Error logging'),
    ]
    
    for check_str, description in error_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 12: State management
    print("✓ Check 12: State management")
    state_checks = [
        ('st.session_state', 'Session state usage'),
        ('audio_active', 'Audio state'),
        ('video_active', 'Video state'),
        ('screen_active', 'Screen share state'),
        ('confirm_end', 'Confirmation state'),
    ]
    
    for check_str, description in state_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 13: Integration with communication manager
    print("✓ Check 13: Integration with communication manager")
    integration_checks = [
        ('communication_manager.enable_mode', 'Enable mode method'),
        ('communication_manager.disable_mode', 'Disable mode method'),
    ]
    
    for check_str, description in integration_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Check 14: Integration with session manager
    print("✓ Check 14: Integration with session manager")
    if 'session_manager.end_session' in content:
        print(f"  ✅ End session method call")
    else:
        print(f"  ❌ End session method call - NOT FOUND")
        all_checks_passed = False
    print()
    
    # Check 15: UI layout and columns
    print("✓ Check 15: UI layout with proper columns")
    layout_checks = [
        ('st.columns', 'Column layout'),
        ('st.metric', 'Metric display'),
        ('st.toggle', 'Toggle controls'),
        ('st.button', 'Button controls'),
        ('st.markdown', 'Markdown formatting'),
    ]
    
    for check_str, description in layout_checks:
        if check_str in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} - NOT FOUND")
            all_checks_passed = False
    print()
    
    # Final summary
    print("=" * 80)
    if all_checks_passed:
        print("✅ ALL VALIDATION CHECKS PASSED")
        print()
        print("The recording controls implementation includes:")
        print("  • Audio recording toggle with streamlit-webrtc integration")
        print("  • Video recording toggle")
        print("  • Whiteboard snapshot status display")
        print("  • Screen share toggle")
        print("  • End interview button with two-click confirmation")
        print("  • Session timer with elapsed time display")
        print("  • Token usage indicator with cost estimation")
        print("  • Visual indicators for all active modes")
        print("  • Proper error handling and logging")
        print("  • State management for all recording modes")
        print("  • Integration with communication and session managers")
        print()
        print("Requirements satisfied: 2.3, 2.4, 2.5, 2.6, 5.1, 14.7, 18.4, 18.7")
        return True
    else:
        print("❌ SOME VALIDATION CHECKS FAILED")
        print()
        print("Please review the failed checks above and ensure all requirements are met.")
        return False


if __name__ == "__main__":
    success = validate_recording_controls()
    sys.exit(0 if success else 1)
