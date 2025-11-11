"""
Simple test script to verify logging system functionality.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import LoggingConfig
from src.log_manager import LoggingManager

def test_logging_manager():
    """Test LoggingManager with different log levels and handlers."""
    
    print("Testing LoggingManager...")
    print("-" * 50)
    
    # Create logging configuration
    config = LoggingConfig(
        level="DEBUG",
        format="json",
        console_output=True,
        file_output=True,
        database_output=False,  # Disable DB logging for this test
        max_file_size_mb=10,
        backup_count=5,
    )
    
    # Initialize logging manager
    logger = LoggingManager(config)
    
    # Test different log levels
    print("\n1. Testing DEBUG level:")
    logger.debug(
        component="TestComponent",
        operation="test_operation",
        message="This is a debug message",
        metadata={"test_key": "test_value"},
    )
    
    print("\n2. Testing INFO level:")
    logger.info(
        component="TestComponent",
        operation="test_operation",
        message="This is an info message",
        session_id="test-session-123",
        metadata={"user": "test_user"},
    )
    
    print("\n3. Testing WARNING level:")
    logger.warning(
        component="TestComponent",
        operation="test_operation",
        message="This is a warning message",
        session_id="test-session-123",
    )
    
    print("\n4. Testing ERROR level:")
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.error(
            component="TestComponent",
            operation="test_operation",
            message="This is an error message",
            session_id="test-session-123",
            exc_info=e,
        )
    
    print("\n5. Testing CRITICAL level:")
    logger.critical(
        component="TestComponent",
        operation="test_operation",
        message="This is a critical message",
        session_id="test-session-123",
    )
    
    print("\n6. Testing API call logging:")
    logger.log_api_call(
        provider="OpenAI",
        endpoint="/v1/chat/completions",
        request_data={"model": "gpt-4", "messages": ["test"]},
        response_data={"choices": [{"message": {"content": "response"}}]},
        duration_ms=1234.56,
        session_id="test-session-123",
    )
    
    print("\n7. Testing error logging with context:")
    try:
        raise RuntimeError("Test runtime error")
    except Exception as e:
        logger.log_error(
            component="TestComponent",
            operation="test_operation",
            error=e,
            session_id="test-session-123",
            context={"additional_info": "Some context"},
        )
    
    print("\n" + "-" * 50)
    print("Logging tests completed!")
    print(f"Check logs/interview_platform.log for file output")

if __name__ == "__main__":
    test_logging_manager()
