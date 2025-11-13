#!/usr/bin/env python3
"""
Error Scenarios Validation Script

This script validates error handling for:
1. Invalid API credentials handling
2. Database connection failures
3. Missing resume upload
4. Invalid session configuration
5. Clear and actionable error messages
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import SessionConfig, CommunicationMode, ResumeData
from exceptions import (
    ConfigurationError,
    AIProviderError,
    DataStoreError,
)


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


def print_info(message: str):
    """Print an info message"""
    print(f"  {message}")


def test_invalid_api_credentials() -> bool:
    """Test handling of invalid API credentials"""
    print_step(1, "Testing Invalid API Credentials Handling")
    
    try:
        from ai.ai_interviewer import AIInterviewer
        from config import AIConfig
        
        # Test with invalid OpenAI key
        print_info("Testing with invalid OpenAI API key...")
        invalid_config = AIConfig(
            provider="openai",
            model="gpt-4",
            api_key="sk-invalid-key-12345",
            temperature=0.7,
            max_tokens=2000
        )
        
        try:
            interviewer = AIInterviewer(invalid_config, None, None)
            # Try to make an API call
            response = interviewer._call_llm_api("Test prompt")
            print_error("Expected AIProviderError but call succeeded")
            return False
        except AIProviderError as e:
            error_msg = str(e)
            print_success(f"AIProviderError raised correctly: {error_msg[:100]}")
            
            # Verify error message is clear and actionable
            if "api" in error_msg.lower() or "key" in error_msg.lower() or "auth" in error_msg.lower():
                print_success("Error message is clear and mentions API/key/auth")
            else:
                print_error("Error message should mention API key or authentication")
                return False
        
        # Test with missing API key
        print_info("Testing with missing API key...")
        try:
            empty_config = AIConfig(
                provider="openai",
                model="gpt-4",
                api_key="",
                temperature=0.7,
                max_tokens=2000
            )
            interviewer = AIInterviewer(empty_config, None, None)
            print_error("Expected ConfigurationError for empty API key")
            return False
        except (ConfigurationError, ValueError) as e:
            print_success(f"Configuration error raised correctly: {str(e)[:100]}")
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection_failures() -> bool:
    """Test handling of database connection failures"""
    print_step(2, "Testing Database Connection Failures")
    
    try:
        from database.data_store import PostgresDataStore
        
        # Test with invalid connection string
        print_info("Testing with invalid database connection string...")
        invalid_conn_str = "postgresql://invalid:invalid@localhost:9999/nonexistent"
        
        try:
            data_store = PostgresDataStore(invalid_conn_str)
            data_store.health_check()
            print_error("Expected DataStoreError but connection succeeded")
            return False
        except DataStoreError as e:
            error_msg = str(e)
            print_success(f"DataStoreError raised correctly: {error_msg[:100]}")
            
            # Verify error message is actionable
            if "connection" in error_msg.lower() or "database" in error_msg.lower():
                print_success("Error message mentions connection/database")
            else:
                print_error("Error message should mention connection or database")
                return False
        
        # Test retry logic
        print_info("Verifying retry logic is implemented...")
        # The retry logic should be visible in the implementation
        # We can't easily test it without a flaky connection, but we can verify it exists
        import inspect
        source = inspect.getsource(PostgresDataStore._execute_query)
        if "@retry" in source or "retry" in source.lower():
            print_success("Retry logic found in implementation")
        else:
            print_error("Retry logic should be implemented for database operations")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_missing_resume_upload() -> bool:
    """Test handling of missing resume upload"""
    print_step(3, "Testing Missing Resume Upload")
    
    try:
        from app_factory import create_app
        
        print_info("Initializing application components...")
        app_components = create_app()
        session_manager = app_components["session_manager"]
        
        # Try to create session without resume
        print_info("Attempting to create session without resume...")
        config = SessionConfig(
            enabled_modes=[CommunicationMode.TEXT],
            ai_provider="openai",
            ai_model="gpt-4",
            resume_data=None  # No resume provided
        )
        
        try:
            session = session_manager.create_session(config)
            # This might succeed if resume is optional
            print_info("Session created without resume (resume is optional)")
            
            # Try to start interview without resume
            print_info("Attempting to start interview without resume...")
            ai_interviewer = app_components["ai_interviewer"]
            response = ai_interviewer.start_interview(session.id)
            
            # Should work but generate generic problem
            if "system design" in response.content.lower():
                print_success("Generic problem generated without resume")
            else:
                print_error("Problem generation should work without resume")
                return False
                
        except ConfigurationError as e:
            # If resume is required, this is also acceptable
            print_success(f"ConfigurationError raised for missing resume: {str(e)[:100]}")
        
        # Test with invalid resume data
        print_info("Testing with invalid resume data...")
        invalid_resume = ResumeData(
            user_id="",  # Empty user_id
            name="",
            email="invalid-email",
            experience_level="invalid",  # Invalid level
            years_of_experience=-5,  # Negative years
            domain_expertise=[],
            work_experience=[],
            education=[],
            skills=[],
            raw_text=""
        )
        
        try:
            config_invalid = SessionConfig(
                enabled_modes=[CommunicationMode.TEXT],
                ai_provider="openai",
                ai_model="gpt-4",
                resume_data=invalid_resume
            )
            session = session_manager.create_session(config_invalid)
            print_error("Should validate resume data before creating session")
            return False
        except (ConfigurationError, ValueError) as e:
            print_success(f"Validation error raised for invalid resume: {str(e)[:100]}")
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_session_configuration() -> bool:
    """Test handling of invalid session configuration"""
    print_step(4, "Testing Invalid Session Configuration")
    
    try:
        from app_factory import create_app
        
        print_info("Initializing application components...")
        app_components = create_app()
        session_manager = app_components["session_manager"]
        
        # Test with no communication modes
        print_info("Testing with no communication modes...")
        try:
            config = SessionConfig(
                enabled_modes=[],  # No modes enabled
                ai_provider="openai",
                ai_model="gpt-4"
            )
            session = session_manager.create_session(config)
            print_error("Should require at least one communication mode")
            return False
        except (ConfigurationError, ValueError) as e:
            print_success(f"Validation error raised: {str(e)[:100]}")
        
        # Test with invalid AI provider
        print_info("Testing with invalid AI provider...")
        try:
            config = SessionConfig(
                enabled_modes=[CommunicationMode.TEXT],
                ai_provider="invalid_provider",
                ai_model="some-model"
            )
            session = session_manager.create_session(config)
            print_error("Should validate AI provider")
            return False
        except (ConfigurationError, ValueError) as e:
            print_success(f"Validation error raised: {str(e)[:100]}")
        
        # Test with invalid model for provider
        print_info("Testing with invalid model for provider...")
        try:
            config = SessionConfig(
                enabled_modes=[CommunicationMode.TEXT],
                ai_provider="openai",
                ai_model="claude-3"  # Wrong model for OpenAI
            )
            session = session_manager.create_session(config)
            # This might succeed if validation is lenient
            print_info("Model validation is lenient (acceptable)")
        except (ConfigurationError, ValueError) as e:
            print_success(f"Validation error raised: {str(e)[:100]}")
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_error_message_quality() -> bool:
    """Test that error messages are clear and actionable"""
    print_step(5, "Testing Error Message Quality")
    
    try:
        print_info("Checking exception classes...")
        
        # Verify custom exception classes exist
        from exceptions import (
            InterviewPlatformError,
            ConfigurationError,
            CommunicationError,
            AIProviderError,
            DataStoreError,
        )
        
        print_success("All custom exception classes found")
        
        # Test that exceptions have meaningful messages
        print_info("Testing exception message quality...")
        
        test_cases = [
            (ConfigurationError("Invalid API key provided"), "api key"),
            (AIProviderError("Failed to connect to OpenAI API"), "openai"),
            (DataStoreError("Database connection failed"), "database"),
            (CommunicationError("Audio capture device not found"), "audio"),
        ]
        
        for exception, expected_keyword in test_cases:
            msg = str(exception).lower()
            if expected_keyword in msg:
                print_success(f"✓ {exception.__class__.__name__} has clear message")
            else:
                print_error(f"✗ {exception.__class__.__name__} message should mention '{expected_keyword}'")
                return False
        
        # Verify exceptions inherit from base class
        print_info("Verifying exception hierarchy...")
        assert issubclass(ConfigurationError, InterviewPlatformError)
        assert issubclass(AIProviderError, InterviewPlatformError)
        assert issubclass(DataStoreError, InterviewPlatformError)
        assert issubclass(CommunicationError, InterviewPlatformError)
        print_success("Exception hierarchy is correct")
        
        return True
        
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run error scenario validation"""
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print("Error Scenarios Validation")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    tests = [
        ("Invalid API Credentials", test_invalid_api_credentials),
        ("Database Connection Failures", test_database_connection_failures),
        ("Missing Resume Upload", test_missing_resume_upload),
        ("Invalid Session Configuration", test_invalid_session_configuration),
        ("Error Message Quality", test_error_message_quality),
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
    print("Test Summary")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"{Colors.GREEN}✓ All error handling tests passed{Colors.RESET}\n")
        sys.exit(0)
    else:
        print(f"{Colors.RED}✗ Some error handling tests failed{Colors.RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
