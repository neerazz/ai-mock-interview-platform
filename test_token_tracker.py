"""
Integration test for TokenTracker functionality.

This test verifies that the TokenTracker can record usage, calculate costs,
and retrieve session summaries correctly.
"""

import os
from datetime import datetime

from src.ai.token_tracker import TokenTracker
from src.database.data_store import PostgresDataStore
from src.models import Session, SessionConfig, SessionStatus, CommunicationMode


def test_token_tracker():
    """Test TokenTracker basic functionality."""
    print("Testing TokenTracker...")

    # Initialize database connection
    db = PostgresDataStore(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "interview_platform"),
        user=os.getenv("DB_USER", "interview_user"),
        password=os.getenv("DB_PASSWORD", ""),
    )

    # Check database health
    if not db.health_check():
        print("❌ Database health check failed")
        return False

    print("✓ Database connection established")

    # Create a test session
    session_id = "test-session-token-tracker"
    session = Session(
        id=session_id,
        user_id="test-user",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=SessionConfig(
            enabled_modes=[CommunicationMode.TEXT],
            ai_provider="openai",
            ai_model="gpt-4-turbo-preview",
        ),
    )

    try:
        # Save test session
        db.save_session(session)
        print(f"✓ Test session created: {session_id}")

        # Initialize TokenTracker
        tracker = TokenTracker(data_store=db)
        print("✓ TokenTracker initialized")

        # Test 1: Record token usage for question generation
        usage1 = tracker.record_usage(
            session_id=session_id,
            provider="openai",
            model="gpt-4-turbo-preview",
            operation="question_generation",
            input_tokens=500,
            output_tokens=200,
        )
        print(f"✓ Recorded usage 1: {usage1.total_tokens} tokens, ${usage1.estimated_cost:.6f}")

        # Test 2: Record token usage for response analysis
        usage2 = tracker.record_usage(
            session_id=session_id,
            provider="openai",
            model="gpt-4-turbo-preview",
            operation="response_analysis",
            input_tokens=800,
            output_tokens=300,
        )
        print(f"✓ Recorded usage 2: {usage2.total_tokens} tokens, ${usage2.estimated_cost:.6f}")

        # Test 3: Record token usage for evaluation
        usage3 = tracker.record_usage(
            session_id=session_id,
            provider="openai",
            model="gpt-4-turbo-preview",
            operation="evaluation",
            input_tokens=1500,
            output_tokens=800,
        )
        print(f"✓ Recorded usage 3: {usage3.total_tokens} tokens, ${usage3.estimated_cost:.6f}")

        # Test 4: Get session usage summary
        session_usage = tracker.get_session_usage(session_id)
        print(f"\n✓ Session Usage Summary:")
        print(f"  Total Input Tokens: {session_usage.total_input_tokens}")
        print(f"  Total Output Tokens: {session_usage.total_output_tokens}")
        print(f"  Total Tokens: {session_usage.total_tokens}")
        print(f"  Total Cost: ${session_usage.total_cost:.6f}")

        # Verify totals
        expected_total_tokens = 700 + 1100 + 2300
        if session_usage.total_tokens != expected_total_tokens:
            print(f"❌ Total tokens mismatch: expected {expected_total_tokens}, got {session_usage.total_tokens}")
            return False

        # Test 5: Get usage breakdown by operation
        breakdown = tracker.get_usage_breakdown(session_id)
        print(f"\n✓ Usage Breakdown by Operation:")
        for operation, usage in breakdown.items():
            print(f"  {operation}: {usage.total_tokens} tokens, ${usage.estimated_cost:.6f}")

        # Verify breakdown
        if len(breakdown) != 3:
            print(f"❌ Expected 3 operations, got {len(breakdown)}")
            return False

        # Test 6: Get total cost
        total_cost = tracker.get_total_cost(session_id)
        print(f"\n✓ Total Cost: ${total_cost:.6f}")

        if total_cost != session_usage.total_cost:
            print(f"❌ Total cost mismatch")
            return False

        # Test 7: Test with Anthropic provider
        usage4 = tracker.record_usage(
            session_id=session_id,
            provider="anthropic",
            model="claude-3-opus-20240229",
            operation="question_generation",
            input_tokens=600,
            output_tokens=250,
        )
        print(f"\n✓ Recorded Anthropic usage: {usage4.total_tokens} tokens, ${usage4.estimated_cost:.6f}")

        # Test 8: Test with unknown provider (should use default pricing)
        usage5 = tracker.record_usage(
            session_id=session_id,
            provider="unknown_provider",
            model="unknown_model",
            operation="test",
            input_tokens=100,
            output_tokens=50,
        )
        print(f"✓ Recorded unknown provider usage: {usage5.total_tokens} tokens, ${usage5.estimated_cost:.6f}")

        print("\n✅ All TokenTracker tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        db.close()


if __name__ == "__main__":
    success = test_token_tracker()
    exit(0 if success else 1)
