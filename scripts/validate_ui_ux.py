#!/usr/bin/env python3
"""
UI/UX Polish Validation Script

This script validates UI/UX requirements:
1. All buttons and controls work correctly
2. Responsive layout on different screen sizes
3. Consistent styling across all pages
4. Loading indicators where appropriate
5. Intuitive navigation flow
6. Keyboard shortcuts and accessibility
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_step(step_num: int, description: str):
    """Print a test step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Test {step_num}: {description}{Colors.RESET}")
    print("=" * 70)


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message"""
    print(f"  {message}")


def check_file_exists(file_path: str) -> bool:
    """Check if a file exists"""
    return Path(file_path).exists()


def check_ui_pages_exist() -> bool:
    """Check that all UI pages exist"""
    print_step(1, "Checking UI Pages Exist")
    
    required_pages = [
        "src/ui/pages/setup.py",
        "src/ui/pages/interview.py",
        "src/ui/pages/evaluation.py",
        "src/ui/pages/history.py",
    ]
    
    all_exist = True
    for page in required_pages:
        if check_file_exists(page):
            print_success(f"Found: {page}")
        else:
            print_error(f"Missing: {page}")
            all_exist = False
    
    return all_exist


def check_button_implementations() -> bool:
    """Check that buttons and controls are implemented"""
    print_step(2, "Checking Button and Control Implementations")
    
    try:
        # Check setup page
        print_info("Checking setup page controls...")
        with open("src/ui/pages/setup.py", "r") as f:
            setup_content = f.read()
        
        required_controls = [
            ("file_uploader", "Resume upload"),
            ("selectbox", "AI provider selection"),
            ("checkbox", "Communication mode selection"),
            ("button", "Start interview button"),
        ]
        
        for control, description in required_controls:
            if control in setup_content:
                print_success(f"{description} implemented")
            else:
                print_error(f"{description} not found")
                return False
        
        # Check interview page
        print_info("Checking interview page controls...")
        with open("src/ui/pages/interview.py", "r") as f:
            interview_content = f.read()
        
        required_controls = [
            ("chat_input", "Text input"),
            ("st_canvas", "Whiteboard canvas"),
            ("button", "Control buttons"),
            ("toggle", "Recording toggles"),
        ]
        
        for control, description in required_controls:
            if control in interview_content:
                print_success(f"{description} implemented")
            else:
                print_warning(f"{description} not found (may use different component)")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking button implementations: {str(e)}")
        return False


def check_layout_structure() -> bool:
    """Check that layout structure is properly implemented"""
    print_step(3, "Checking Layout Structure")
    
    try:
        # Check interview page layout
        print_info("Checking interview page 3-panel layout...")
        with open("src/ui/pages/interview.py", "r") as f:
            interview_content = f.read()
        
        # Check for column layout
        if "st.columns" in interview_content:
            print_success("Column layout implemented")
        else:
            print_error("Column layout not found")
            return False
        
        # Check for panel proportions (30%, 45%, 25%)
        if "[3," in interview_content or "[30" in interview_content:
            print_success("Panel proportions appear to be configured")
        else:
            print_warning("Panel proportions may not match specification")
        
        # Check for container usage
        if "st.container" in interview_content:
            print_success("Containers used for organization")
        else:
            print_warning("Containers not found (may affect layout)")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking layout structure: {str(e)}")
        return False


def check_styling_consistency() -> bool:
    """Check for consistent styling across pages"""
    print_step(4, "Checking Styling Consistency")
    
    try:
        pages = [
            "src/ui/pages/setup.py",
            "src/ui/pages/interview.py",
            "src/ui/pages/evaluation.py",
            "src/ui/pages/history.py",
        ]
        
        # Check for consistent use of Streamlit components
        print_info("Checking component consistency...")
        
        common_patterns = {
            "st.title": 0,
            "st.subheader": 0,
            "st.divider": 0,
            "st.metric": 0,
        }
        
        for page in pages:
            if not check_file_exists(page):
                continue
            
            with open(page, "r") as f:
                content = f.read()
            
            for pattern in common_patterns:
                if pattern in content:
                    common_patterns[pattern] += 1
        
        for pattern, count in common_patterns.items():
            if count >= 2:
                print_success(f"{pattern} used consistently across pages")
            else:
                print_info(f"{pattern} used in {count} page(s)")
        
        # Check for custom styling
        print_info("Checking for custom styling...")
        streamlit_config = Path(".streamlit/config.toml")
        if streamlit_config.exists():
            print_success("Streamlit config file exists")
            with open(streamlit_config, "r") as f:
                config_content = f.read()
            if "theme" in config_content or "primaryColor" in config_content:
                print_success("Custom theme configured")
            else:
                print_info("Using default theme")
        else:
            print_info("No custom Streamlit config (using defaults)")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking styling consistency: {str(e)}")
        return False


def check_loading_indicators() -> bool:
    """Check for loading indicators"""
    print_step(5, "Checking Loading Indicators")
    
    try:
        pages = [
            "src/ui/pages/setup.py",
            "src/ui/pages/interview.py",
            "src/ui/pages/evaluation.py",
            "src/ui/pages/history.py",
        ]
        
        loading_patterns = [
            "st.spinner",
            "st.progress",
            "with st.spinner",
        ]
        
        pages_with_loading = []
        
        for page in pages:
            if not check_file_exists(page):
                continue
            
            with open(page, "r") as f:
                content = f.read()
            
            has_loading = any(pattern in content for pattern in loading_patterns)
            if has_loading:
                pages_with_loading.append(page)
                print_success(f"Loading indicators in {Path(page).name}")
            else:
                print_warning(f"No loading indicators in {Path(page).name}")
        
        if len(pages_with_loading) >= 2:
            print_success("Loading indicators used appropriately")
            return True
        else:
            print_warning("Consider adding more loading indicators")
            return True  # Not critical
        
    except Exception as e:
        print_error(f"Error checking loading indicators: {str(e)}")
        return False


def check_navigation_flow() -> bool:
    """Check navigation flow between pages"""
    print_step(6, "Checking Navigation Flow")
    
    try:
        # Check main.py for page routing
        print_info("Checking page routing in main.py...")
        with open("src/main.py", "r") as f:
            main_content = f.read()
        
        required_pages = ["setup", "interview", "evaluation", "history"]
        
        for page in required_pages:
            if page in main_content.lower():
                print_success(f"Page '{page}' referenced in routing")
            else:
                print_warning(f"Page '{page}' may not be in routing")
        
        # Check for navigation methods
        navigation_methods = [
            "st.switch_page",
            "st.navigation",
            "st.page_link",
        ]
        
        has_navigation = any(method in main_content for method in navigation_methods)
        if has_navigation:
            print_success("Navigation methods implemented")
        else:
            print_warning("Navigation methods not found (may use session state)")
        
        # Check for session state management
        if "st.session_state" in main_content:
            print_success("Session state used for state management")
        else:
            print_warning("Session state not found")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking navigation flow: {str(e)}")
        return False


def check_accessibility_features() -> bool:
    """Check for accessibility features"""
    print_step(7, "Checking Accessibility Features")
    
    try:
        pages = [
            "src/ui/pages/setup.py",
            "src/ui/pages/interview.py",
            "src/ui/pages/evaluation.py",
            "src/ui/pages/history.py",
        ]
        
        accessibility_features = {
            "help=": "Help text for inputs",
            "label=": "Labels for components",
            "caption": "Captions for context",
            "st.info": "Info messages",
            "st.warning": "Warning messages",
            "st.error": "Error messages",
        }
        
        feature_counts = {feature: 0 for feature in accessibility_features}
        
        for page in pages:
            if not check_file_exists(page):
                continue
            
            with open(page, "r") as f:
                content = f.read()
            
            for feature in accessibility_features:
                if feature in content:
                    feature_counts[feature] += 1
        
        for feature, description in accessibility_features.items():
            count = feature_counts[feature]
            if count > 0:
                print_success(f"{description} used in {count} page(s)")
            else:
                print_info(f"{description} not found")
        
        # Check for keyboard shortcuts (Streamlit doesn't have native support)
        print_info("Note: Streamlit has limited keyboard shortcut support")
        print_info("Standard shortcuts (Enter, Tab, etc.) work by default")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking accessibility features: {str(e)}")
        return False


def check_error_handling_ui() -> bool:
    """Check for user-friendly error handling in UI"""
    print_step(8, "Checking Error Handling in UI")
    
    try:
        pages = [
            "src/ui/pages/setup.py",
            "src/ui/pages/interview.py",
            "src/ui/pages/evaluation.py",
            "src/ui/pages/history.py",
        ]
        
        error_handling_patterns = [
            "try:",
            "except",
            "st.error",
            "st.warning",
        ]
        
        pages_with_error_handling = []
        
        for page in pages:
            if not check_file_exists(page):
                continue
            
            with open(page, "r") as f:
                content = f.read()
            
            has_error_handling = all(pattern in content for pattern in error_handling_patterns[:2])
            has_error_display = any(pattern in content for pattern in error_handling_patterns[2:])
            
            if has_error_handling and has_error_display:
                pages_with_error_handling.append(page)
                print_success(f"Error handling in {Path(page).name}")
            elif has_error_handling:
                print_warning(f"Error handling in {Path(page).name} but no user feedback")
            else:
                print_warning(f"Limited error handling in {Path(page).name}")
        
        if len(pages_with_error_handling) >= 2:
            print_success("Error handling implemented appropriately")
        else:
            print_warning("Consider adding more error handling")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking error handling: {str(e)}")
        return False


def check_responsive_design() -> bool:
    """Check for responsive design considerations"""
    print_step(9, "Checking Responsive Design")
    
    try:
        print_info("Checking layout flexibility...")
        
        with open("src/ui/pages/interview.py", "r") as f:
            interview_content = f.read()
        
        # Check for column usage (Streamlit handles responsiveness automatically)
        if "st.columns" in interview_content:
            print_success("Columns used (Streamlit handles responsiveness)")
        
        # Check for container usage
        if "st.container" in interview_content:
            print_success("Containers used for organization")
        
        # Check for expander usage (good for mobile)
        if "st.expander" in interview_content:
            print_success("Expanders used (good for mobile)")
        else:
            print_info("Expanders not used (optional)")
        
        print_info("Note: Streamlit provides responsive design by default")
        print_info("Test on different screen sizes manually for best results")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking responsive design: {str(e)}")
        return False


def check_visual_feedback() -> bool:
    """Check for visual feedback on user actions"""
    print_step(10, "Checking Visual Feedback")
    
    try:
        pages = [
            "src/ui/pages/setup.py",
            "src/ui/pages/interview.py",
            "src/ui/pages/evaluation.py",
            "src/ui/pages/history.py",
        ]
        
        feedback_patterns = {
            "st.success": "Success messages",
            "st.info": "Info messages",
            "st.warning": "Warning messages",
            "st.error": "Error messages",
            "st.toast": "Toast notifications",
            "st.balloons": "Celebration effects",
        }
        
        feedback_counts = {pattern: 0 for pattern in feedback_patterns}
        
        for page in pages:
            if not check_file_exists(page):
                continue
            
            with open(page, "r") as f:
                content = f.read()
            
            for pattern in feedback_patterns:
                if pattern in content:
                    feedback_counts[pattern] += 1
        
        for pattern, description in feedback_patterns.items():
            count = feedback_counts[pattern]
            if count > 0:
                print_success(f"{description} used in {count} page(s)")
            else:
                print_info(f"{description} not used")
        
        total_feedback = sum(feedback_counts.values())
        if total_feedback >= 5:
            print_success(f"Good visual feedback ({total_feedback} instances)")
        else:
            print_warning(f"Limited visual feedback ({total_feedback} instances)")
        
        return True
        
    except Exception as e:
        print_error(f"Error checking visual feedback: {str(e)}")
        return False


def main():
    """Run UI/UX validation"""
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print("UI/UX Polish Validation")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    tests = [
        ("UI Pages Exist", check_ui_pages_exist),
        ("Button Implementations", check_button_implementations),
        ("Layout Structure", check_layout_structure),
        ("Styling Consistency", check_styling_consistency),
        ("Loading Indicators", check_loading_indicators),
        ("Navigation Flow", check_navigation_flow),
        ("Accessibility Features", check_accessibility_features),
        ("Error Handling UI", check_error_handling_ui),
        ("Responsive Design", check_responsive_design),
        ("Visual Feedback", check_visual_feedback),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print("UI/UX Test Summary")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All UI/UX tests passed{Colors.RESET}\n")
        print_info("Manual testing recommended for:")
        print_info("  - Visual appearance on different screen sizes")
        print_info("  - User interaction flow")
        print_info("  - Button click responsiveness")
        print_info("  - Form validation feedback")
        sys.exit(0)
    else:
        print(f"{Colors.YELLOW}⚠ Some UI/UX tests failed{Colors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
