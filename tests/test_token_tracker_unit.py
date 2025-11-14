"""
Unit test for TokenTracker functionality without database dependency.

This test verifies the TokenTracker's cost calculation and aggregation logic
using a mock data store.
"""

from datetime import datetime
from typing import List

from src.ai.token_tracker import TokenTracker, PROVIDER_PRICING
from src.models import TokenUsage


class MockDataStore:
    """Mock data store for testing."""

    def __init__(self):
        self.token_usage_records = {}

    def save_token_usage(self, session_id: str, token_usage: TokenUsage) -> None:
        """Save token usage to in-memory storage."""
        if session_id not in self.token_usage_records:
            self.token_usage_records[session_id] = []
        self.token_usage_records[session_id].append(token_usage)

    def get_token_usage(self, session_id: str) -> List[TokenUsage]:
        """Retrieve token usage from in-memory storage."""
        return self.token_usage_records.get(session_id, [])


def test_token_tracker_unit():
    """Test TokenTracker core functionality with mock data store."""
    print("Testing TokenTracker (Unit Tests)...")

    # Initialize mock data store
    mock_db = MockDataStore()
    tracker = TokenTracker(data_store=mock_db)
    print("✓ TokenTracker initialized with mock data store")

    session_id = "test-session-unit"

    # Test 1: Record usage and verify cost calculation for OpenAI GPT-4 Turbo
    print("\nTest 1: OpenAI GPT-4 Turbo cost calculation")
    usage1 = tracker.record_usage(
        session_id=session_id,
        provider="openai",
        model="gpt-4-turbo-preview",
        operation="question_generation",
        input_tokens=1_000_000,  # 1M tokens for easy calculation
        output_tokens=1_000_000,  # 1M tokens
    )
    # Expected: $10 (input) + $30 (output) = $40
    expected_cost1 = 40.0
    print(f"  Input: 1M tokens, Output: 1M tokens")
    print(f"  Expected cost: ${expected_cost1:.2f}")
    print(f"  Actual cost: ${usage1.estimated_cost:.2f}")
    assert abs(usage1.estimated_cost - expected_cost1) < 0.01, f"Cost mismatch: expected ${expected_cost1}, got ${usage1.estimated_cost}"
    print("  ✓ Cost calculation correct")

    # Test 2: Record usage for Anthropic Claude
    print("\nTest 2: Anthropic Claude cost calculation")
    usage2 = tracker.record_usage(
        session_id=session_id,
        provider="anthropic",
        model="claude-3-opus-20240229",
        operation="response_analysis",
        input_tokens=500_000,  # 0.5M tokens
        output_tokens=500_000,  # 0.5M tokens
    )
    # Expected: $15 * 0.5 (input) + $75 * 0.5 (output) = $7.5 + $37.5 = $45
    expected_cost2 = 45.0
    print(f"  Input: 500K tokens, Output: 500K tokens")
    print(f"  Expected cost: ${expected_cost2:.2f}")
    print(f"  Actual cost: ${usage2.estimated_cost:.2f}")
    assert abs(usage2.estimated_cost - expected_cost2) < 0.01, f"Cost mismatch: expected ${expected_cost2}, got ${usage2.estimated_cost}"
    print("  ✓ Cost calculation correct")

    # Test 3: Small token counts
    print("\nTest 3: Small token counts")
    usage3 = tracker.record_usage(
        session_id=session_id,
        provider="openai",
        model="gpt-4-turbo-preview",
        operation="evaluation",
        input_tokens=500,
        output_tokens=200,
    )
    # Expected: (500/1M * $10) + (200/1M * $30) = $0.005 + $0.006 = $0.011
    expected_cost3 = 0.011
    print(f"  Input: 500 tokens, Output: 200 tokens")
    print(f"  Expected cost: ${expected_cost3:.6f}")
    print(f"  Actual cost: ${usage3.estimated_cost:.6f}")
    assert abs(usage3.estimated_cost - expected_cost3) < 0.000001, f"Cost mismatch: expected ${expected_cost3}, got ${usage3.estimated_cost}"
    print("  ✓ Cost calculation correct")

    # Test 4: Get session usage summary
    print("\nTest 4: Session usage summary")
    session_usage = tracker.get_session_usage(session_id)
    expected_total_tokens = 2_000_000 + 1_000_000 + 700
    expected_total_cost = expected_cost1 + expected_cost2 + expected_cost3
    print(f"  Total tokens: {session_usage.total_tokens:,}")
    print(f"  Expected: {expected_total_tokens:,}")
    assert session_usage.total_tokens == expected_total_tokens, f"Total tokens mismatch"
    print(f"  Total cost: ${session_usage.total_cost:.6f}")
    print(f"  Expected: ${expected_total_cost:.6f}")
    assert abs(session_usage.total_cost - expected_total_cost) < 0.000001, f"Total cost mismatch"
    print("  ✓ Session summary correct")

    # Test 5: Usage breakdown by operation
    print("\nTest 5: Usage breakdown by operation")
    breakdown = tracker.get_usage_breakdown(session_id)
    print(f"  Number of operations: {len(breakdown)}")
    assert len(breakdown) == 3, f"Expected 3 operations, got {len(breakdown)}"
    
    operations = ["question_generation", "response_analysis", "evaluation"]
    for op in operations:
        assert op in breakdown, f"Operation '{op}' not found in breakdown"
        print(f"  ✓ {op}: {breakdown[op].total_tokens:,} tokens, ${breakdown[op].estimated_cost:.6f}")

    # Test 6: Get total cost
    print("\nTest 6: Get total cost")
    total_cost = tracker.get_total_cost(session_id)
    print(f"  Total cost: ${total_cost:.6f}")
    assert abs(total_cost - expected_total_cost) < 0.000001, f"Total cost mismatch"
    print("  ✓ Total cost correct")

    # Test 7: Unknown provider (should use default pricing)
    print("\nTest 7: Unknown provider handling")
    usage4 = tracker.record_usage(
        session_id=session_id,
        provider="unknown_provider",
        model="unknown_model",
        operation="test",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
    )
    # Should use default: $10 (input) + $30 (output) = $40
    expected_cost4 = 40.0
    print(f"  Input: 1M tokens, Output: 1M tokens")
    print(f"  Expected cost (default): ${expected_cost4:.2f}")
    print(f"  Actual cost: ${usage4.estimated_cost:.2f}")
    assert abs(usage4.estimated_cost - expected_cost4) < 0.01, f"Cost mismatch for unknown provider"
    print("  ✓ Default pricing applied correctly")

    # Test 8: Verify pricing table completeness
    print("\nTest 8: Verify pricing table")
    assert "openai" in PROVIDER_PRICING, "OpenAI not in pricing table"
    assert "anthropic" in PROVIDER_PRICING, "Anthropic not in pricing table"
    assert "gpt-4-turbo-preview" in PROVIDER_PRICING["openai"], "GPT-4 Turbo not in OpenAI pricing"
    assert "claude-3-opus-20240229" in PROVIDER_PRICING["anthropic"], "Claude 3 Opus not in Anthropic pricing"
    print("  ✓ Pricing table complete")

    # Test 9: Multiple operations of same type (aggregation)
    print("\nTest 9: Multiple operations of same type")
    session_id2 = "test-session-aggregation"
    tracker.record_usage(
        session_id=session_id2,
        provider="openai",
        model="gpt-4-turbo-preview",
        operation="question_generation",
        input_tokens=100,
        output_tokens=50,
    )
    tracker.record_usage(
        session_id=session_id2,
        provider="openai",
        model="gpt-4-turbo-preview",
        operation="question_generation",
        input_tokens=200,
        output_tokens=100,
    )
    breakdown2 = tracker.get_usage_breakdown(session_id2)
    assert len(breakdown2) == 1, "Should have 1 operation type"
    assert breakdown2["question_generation"].input_tokens == 300, "Input tokens not aggregated correctly"
    assert breakdown2["question_generation"].output_tokens == 150, "Output tokens not aggregated correctly"
    print(f"  ✓ Aggregation correct: {breakdown2['question_generation'].total_tokens} total tokens")

    print("\n✅ All TokenTracker unit tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_token_tracker_unit()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
