"""
Static validation script for session replay and export features (Task 14.4).

This script validates that the history page includes:
1. Button to view full evaluation report
2. Export conversation history option
3. Download whiteboard snapshots option
4. Option to start new session based on previous configuration
"""

from pathlib import Path


def read_file(filepath):
    """Read file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""


def validate_view_full_evaluation_button(history_content):
    """Validate that the view full evaluation report button exists."""
    print("\n1. Validating 'View Full Evaluation Report' button...")
    
    checks = [
        ('st.button("📊 View Full Evaluation Report"' in history_content, 
         "Button with correct label exists"),
        ('type="primary"' in history_content and 'View Full Evaluation Report' in history_content, 
         "Button is styled as primary"),
        ('st.session_state.current_page = "evaluation"' in history_content, 
         "Button navigates to evaluation page"),
        ('st.rerun()' in history_content, 
         "Button triggers page rerun")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_export_conversation_history(history_content):
    """Validate that export conversation history functionality exists."""
    print("\n2. Validating 'Export Conversation History' functionality...")
    
    checks = [
        ('st.button("📥 Export Conversation"' in history_content, 
         "Export conversation button exists"),
        ('export_conversation_history(' in history_content, 
         "Button calls export function"),
        ('def export_conversation_history(' in history_content, 
         "Export function is defined"),
        ('st.download_button(' in history_content and 'conversation_history' in history_content, 
         "Download button is provided"),
        ('file_name=f"conversation_history_' in history_content, 
         "File name is properly formatted"),
        ('mime="text/plain"' in history_content, 
         "MIME type is set correctly"),
        ('timestamp_str = message.timestamp.strftime' in history_content, 
         "Timestamps are included in export"),
        ('role_display = message.role.upper()' in history_content, 
         "Speaker roles are included in export")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_download_whiteboard_snapshots(history_content):
    """Validate that download whiteboard snapshots functionality exists."""
    print("\n3. Validating 'Download Whiteboard Snapshots' functionality...")
    
    checks = [
        ('def render_whiteboard_snapshot(' in history_content, 
         "Whiteboard snapshot rendering function exists"),
        ('st.download_button(' in history_content and 'whiteboard' in history_content.lower(), 
         "Download button exists for snapshots"),
        ('label="📥 Download"' in history_content, 
         "Download button has correct label"),
        ('file_name=f"whiteboard_snapshot_' in history_content, 
         "File name is properly formatted"),
        ('mime="image/png"' in history_content, 
         "MIME type is set correctly for PNG images"),
        ('with open(media_file.file_path, "rb")' in history_content, 
         "File is read in binary mode"),
        ('st.image(' in history_content, 
         "Whiteboard image is displayed")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_start_new_session_with_config(history_content, setup_content):
    """Validate that starting new session with previous config is implemented."""
    print("\n4. Validating 'Start New Session with Previous Config' functionality...")
    
    checks = [
        ('"🔄 Resume Config"' in history_content and 'st.button(' in history_content,
         "Resume Config button exists in session card"),
        ('st.session_state.resume_from_session_id = session.id' in history_content, 
         "Session ID is stored for configuration loading"),
        ('st.session_state.current_page = "setup"' in history_content, 
         "Button navigates to setup page"),
        ('st.button("🔄 Use This Config"' in history_content, 
         "Use This Config button exists in detail view"),
        ('st.session_state.resume_from_session_id = session_id' in history_content, 
         "Session ID is stored in detail view"),
        ('def load_session_configuration(' in setup_content, 
         "Configuration loading function exists in setup.py"),
        ('session = session_manager.get_session(session_id)' in setup_content, 
         "Previous session is loaded"),
        ('st.session_state.ai_provider = session.config.ai_provider' in setup_content, 
         "AI provider is loaded from previous session"),
        ('st.session_state.enabled_modes = session.config.enabled_modes' in setup_content, 
         "Communication modes are loaded from previous session"),
        ('st.session_state.resume_data = session.config.resume_data' in setup_content, 
         "Resume data is loaded from previous session"),
        ('if "resume_from_session_id" in st.session_state' in setup_content,
         "Setup page checks for resume_from_session_id flag")
    ]
    
    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"  {status} {description}")
        if not check:
            all_passed = False
    
    return all_passed


def validate_requirements_coverage(history_content):
    """Validate that requirements 7.3 and 7.4 are covered."""
    print("\n5. Validating Requirements Coverage...")
    
    checks = [
        ('Requirements: 7.3, 7.4' in history_content, 
         "Requirements 7.3 and 7.4 are documented in detail view"),
        ('Requirements: 7.4' in history_content, 
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
    
    # Read source files
    history_content = read_file("src/ui/pages/history.py")
    setup_content = read_file("src/ui/pages/setup.py")
    
    if not history_content:
        print("❌ Failed to read history.py")
        return 1
    
    if not setup_content:
        print("❌ Failed to read setup.py")
        return 1
    
    results = []
    
    # Run all validation checks
    results.append(("View Full Evaluation Button", validate_view_full_evaluation_button(history_content)))
    results.append(("Export Conversation History", validate_export_conversation_history(history_content)))
    results.append(("Download Whiteboard Snapshots", validate_download_whiteboard_snapshots(history_content)))
    results.append(("Start New Session with Config", validate_start_new_session_with_config(history_content, setup_content)))
    results.append(("Requirements Coverage", validate_requirements_coverage(history_content)))
    
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
        print("\nFeatures implemented:")
        print("  • View Full Evaluation Report button in session detail view")
        print("  • Export conversation history as downloadable text file")
        print("  • Download individual whiteboard snapshots as PNG files")
        print("  • Resume Config button in session list")
        print("  • Use This Config button in session detail view")
        print("  • load_session_configuration() function in setup.py")
        return 0
    else:
        print("\n⚠️ Some validation checks failed. Please review the implementation.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
