"""
Test script to demonstrate logging integration with database operations.
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import get_config
from src.log_manager import LoggingManager
from src.database.data_store import PostgresDataStore
from src.models import Session, SessionConfig, SessionStatus, CommunicationMode, Message

def test_database_with_logging():
    """Test database operations with integrated logging."""
    
    print("Testing Database Operations with Logging Integration")
    print("=" * 60)
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = get_config()
        
        # Initialize logging manager
        print("2. Initializing logging manager...")
        logger = LoggingManager(config.logging)
        
        logger.info(
            component="TestScript",
            operation="test_start",
            message="Starting database integration test",
        )
        
        # Initialize database with logger
        print("3. Initializing database connection with logging...")
        data_store = PostgresDataStore(
            host=config.database.host,
            port=config.database.port,
            database=config.database.database,
            user=config.database.user,
            password=config.database.password,
            min_connections=1,
            max_connections=5,
            logger=logger,
        )
        
        # Set data store for database logging handler
        logger.set_data_store(data_store)
        
        # Test health check
        print("4. Testing database health check...")
        is_healthy = data_store.health_check()
        print(f"   Database health: {'✓ Healthy' if is_healthy else '✗ Unhealthy'}")
        
        if not is_healthy:
            print("\n⚠ Database is not available. Make sure Docker containers are running.")
            print("   Run: docker-compose up -d")
            return
        
        # Create a test session
        print("\n5. Creating test session...")
        session_id = str(uuid4())
        session = Session(
            id=session_id,
            user_id="test_user",
            created_at=datetime.now(),
            ended_at=None,
            status=SessionStatus.ACTIVE,
            config=SessionConfig(
                enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
                ai_provider="openai",
                ai_model="gpt-4",
            ),
            metadata={"test": True},
        )
        
        data_store.save_session(session)
        print(f"   ✓ Session created: {session_id}")
        
        # Save a conversation message
        print("6. Saving conversation message...")
        message = Message(
            role="interviewer",
            content="Hello! Let's start the interview.",
            timestamp=datetime.now(),
        )
        data_store.save_conversation(session_id, message)
        print("   ✓ Message saved")
        
        # Retrieve conversation history
        print("7. Retrieving conversation history...")
        messages = data_store.get_conversation_history(session_id)
        print(f"   ✓ Retrieved {len(messages)} message(s)")
        
        # Test error logging
        print("\n8. Testing error logging...")
        try:
            # Intentionally cause an error
            raise ValueError("Test error for logging demonstration")
        except Exception as e:
            logger.log_error(
                component="TestScript",
                operation="test_error",
                error=e,
                session_id=session_id,
                context={"test_context": "This is a test error"},
            )
            print("   ✓ Error logged successfully")
        
        # Close database connection
        print("\n9. Closing database connection...")
        data_store.close()
        
        logger.info(
            component="TestScript",
            operation="test_complete",
            message="Database integration test completed successfully",
            session_id=session_id,
        )
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("\nCheck the following for logs:")
        print("  - Console output (above)")
        print("  - logs/interview_platform.log (file)")
        print("  - audit_logs table in database")
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_database_with_logging()
