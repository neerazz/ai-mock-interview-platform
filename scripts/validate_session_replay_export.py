"""
Validation script for session replay and export features (Task 14.4).

This script validates that the history page includes:
1. Button to view full evaluation report
2. Export conversation history option
3. Download whiteboard snapshots option
4. Option to start new session based on previous configuration
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ui.pages.history import (
    render_session_detail_view,
    render_evaluation_summary_section,
    render_session_actions,
    export_conversation_history,
    render_whiteboard_snapshot
)
from src.ui.pages.setup import load_session_configuration

import inspect


def validate_view_full_evaluation_button():
    """Validate that the view full evaluation report button exists."""
    print("\n1. Validating 'View Full Evaluation Report' button...")
    
    # Check render_evaluation_summary_section function
    source = inspect.getsource(render_evaluation_summary_section)
    
    checks = [
        ('st.button("📊 View Full Evaluation Report"' in source, 
         "Button with correct label exists"),
        ('type="primary"' in source, 
         "Button is styled as primary"),
        ('st.session_state.current_page = "evaluation"' in source, 
         "Button navigates to evaluation page"),
        ('st.rerun()' in source, 
         "Button triggers page rerun")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_export_conversation_history():
    """Validate that export conversation history functionality exists."""
    print("\n2. Validating 'Export Conversation History' functionality...")
    
    # Check render_session_actions function
    actions_source = inspect.getsource(render_session_actions)
    export_source = inspect.getsource(export_conversation_history)
    
    checks = [
        ('st.button("📥 Export Conversation"' in actions_source, 
         "Export conversation button exists"),
        ('export_conversation_history(' in actions_source, 
         "Button calls export function"),
        ('st.download_button(' in export_source, 
         "Download button is provided"),
        ('file_name=f"conversation_history_' in export_source, 
         "File name is properly formatted"),
        ('mime="text/plain"' in export_source, 
         "MIME type is set correctly"),
        ('timestamp_str = message.timestamp.strftime' in export_source, 
         "Timestamps are included in export"),
        ('role_display = message.role.upper()' in export_source, 
         "Speaker roles are included in export")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_download_whiteboard_snapshots():
    """Validate that download whiteboard snapshots functionality exists."""
    print("\n3. Validating 'Download Whiteboard Snapshots' functionality...")
    
    # Check render_whiteboard_snapshot function
    source = inspect.getsource(render_whiteboard_snapshot)
    
    checks = [
        ('st.download_button(' in source, 
         "Download button exists for each snapshot"),
        ('label="📥 Download"' in source, 
         "Download button has correct label"),
        ('file_name=f"whiteboard_snapshot_' in source, 
         "File name is properly formatted"),
        ('mime="image/png"' in source, 
         "MIME type is set correctly for PNG images"),
        ('with open(media_file.file_path, "rb")' in source, 
         "File is read in binary mode"),
        ('st.image(' in source, 
         "Whiteboard image is displayed before download")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_start_new_session_with_config():
    """Validate that starting new session with previous config is implemented."""
    print("\n4. Validating 'Start New Session with Previous Config' functionality...")
    
    # Check render_session_actions and render_session_card functions
    from src.ui.pages.history import render_session_card
    
    card_source = inspect.getsource(render_session_card)
    actions_source = inspect.getsource(render_session_actions)
    setup_source = inspect.getsource(load_session_configuration)
    
    checks = [
        ('st.button(\n        "🔄 Resume Config"' in card_source or 
         'st.button(\n            "🔄 Resume Config"' in card_source,
         "Resume Config button exists in session card"),
        ('st.session_state.resume_from_session_id = session.id' in card_source, 
         "Session ID is stored for configuration loading"),
        ('st.session_state.current_page = "setup"' in card_source, 
         "Button navigates to setup page"),
        ('st.button("🔄 Use This Config"' in actions_source, 
         "Use This Config button exists in detail view"),
        ('st.session_state.resume_from_session_id = session_id' in actions_source, 
         "Session ID is stored in detail view"),
        ('def load_session_configuration(' in setup_source, 
         "Configuration loading function exists"),
        ('session = session_manager.get_session(session_id)' in setup_source, 
         "Previous session is loaded"),
        ('st.session_state.ai_provider = session.config.ai_provider' in setup_source, 
         "AI provider is loaded from previous session"),
        ('st.session_state.enabled_modes = session.config.enabled_modes' in setup_source, 
         "Communication modes are loaded from previous session"),
        ('st.session_state.resume_data = session.config.resume_data' in setup_source, 
         "Resume data is loaded from previous session")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_requirements_coverage():
    """Validate that requirements 7.3 and 7.4 are covered."""
    print("\n5. Validating Requirements Coverage...")
    
    # Check that requirement comments are present
    from src.ui.pages.history import render_session_detail_view
    
    detail_source = inspect.getsource(render_session_detail_view)
    actions_source = inspect.getsource(render_session_actions)
    
    checks = [
        ('Requirements: 7.3, 7.4' in detail_source, 
         "Requirements 7.3 and 7.4 are documented in detail view"),
        ('Requirements: 7.4' in actions_source, 
         "Requirement 7.4 is documented in actions section")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def main():
    """Run all validation checks."""
    print("=" * 80)
    print("TASK 14.4 VALIDATION: Session Replay and Export Features")
    print("=" * 80)
    
    results = []
    
    # Run all validation checks
    results.append(("View Full Evaluation Button", validate_view_full_evaluation_button()))
    results.append(("Export Conversation History", validate_export_conversation_history()))
    results.append(("Download Whiteboard Snapshots", validate_download_whiteboard_snapshots()))
    results.append(("Start New Session with Config", validate_start_new_session_with_config()))
    results.append(("Requirements Coverage", validate_requirements_coverage()))
    
    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for feature, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {feature}")
        if not passed:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n🎉 All validation checks passed!")
        print("\nTask 14.4 Implementation Complete:")
        print("  ✅ Button to view full evaluation report")
        print("  ✅ Export conversation history option")
        print("  ✅ Download whiteboard snapshots option")
        print("  ✅ Option to start new session based on previous configuration")
        return 0
    else:
        print("\n⚠️ Some validation checks failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
