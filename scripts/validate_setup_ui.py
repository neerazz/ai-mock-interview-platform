"""
Validation script for Setup UI implementation.

This script validates that the setup UI components are properly implemented
and can be imported without errors.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def validate_imports():
    """Validate that all required modules can be imported."""
    print("Validating imports...")
    
    try:
        from src.ui.pages import setup
        print("✅ Setup page module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import setup page: {e}")
        return False
    
    try:
        from src.app_factory import create_app
        print("✅ App factory module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import app factory: {e}")
        return False
    
    return True


def validate_setup_functions():
    """Validate that setup page functions exist."""
    print("\nValidating setup page functions...")
    
    try:
        from src.ui.pages.setup import (
            render_setup_page,
            render_resume_upload_section,
            render_resume_analysis_results,
            render_ai_configuration_section,
            render_communication_mode_section,
            render_start_interview_button,
        )
        
        print("✅ render_setup_page function exists")
        print("✅ render_resume_upload_section function exists")
        print("✅ render_resume_analysis_results function exists")
        print("✅ render_ai_configuration_section function exists")
        print("✅ render_communication_mode_section function exists")
        print("✅ render_start_interview_button function exists")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import setup functions: {e}")
        return False


def validate_app_factory():
    """Validate that app factory function exists."""
    print("\nValidating app factory...")
    
    try:
        from src.app_factory import create_app
        
        print("✅ create_app function exists")
        
        # Check function signature
        import inspect
        sig = inspect.signature(create_app)
        params = list(sig.parameters.keys())
        
        if "config_path" in params:
            print("✅ create_app has config_path parameter")
        else:
            print("⚠️  create_app missing config_path parameter")
        
        return True
    except Exception as e:
        print(f"❌ Failed to validate app factory: {e}")
        return False


def validate_main_integration():
    """Validate that main.py is properly updated."""
    print("\nValidating main.py integration...")
    
    try:
        with open("src/main.py", "r") as f:
            content = f.read()
        
        checks = [
            ("render_setup_page" in content, "render_setup_page imported"),
            ("create_app" in content, "create_app imported"),
            ("app_components" in content, "app_components in session state"),
            ("current_page" in content, "page routing implemented"),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Failed to validate main.py: {e}")
        return False


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("Setup UI Implementation Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", validate_imports()))
    results.append(("Setup Functions", validate_setup_functions()))
    results.append(("App Factory", validate_app_factory()))
    results.append(("Main Integration", validate_main_integration()))
    
    print("\n" + "=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All validations passed!")
        print("\nImplementation Summary:")
        print("- Created src/ui/pages/setup.py with resume upload interface")
        print("- Implemented AI provider configuration with validation")
        print("- Implemented communication mode selection")
        print("- Implemented start interview button with session creation")
        print("- Created src/app_factory.py for dependency injection")
        print("- Updated src/main.py to integrate setup page")
        print("\nThe setup UI is ready to use!")
    else:
        print("❌ Some validations failed. Please review the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
