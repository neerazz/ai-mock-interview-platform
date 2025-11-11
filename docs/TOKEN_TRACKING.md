# Token Tracking System

## Overview

The Token Tracking system provides comprehensive monitoring and cost estimation for AI API usage across interview sessions. It tracks token consumption, calculates costs based on provider-specific pricing, and provides detailed analytics.

## Implementation

### TokenTracker Class

Located in `src/ai/token_tracker.py`, the TokenTracker class provides:

- **Token Usage Recording**: Records input/output tokens for each AI API call
- **Cost Calculation**: Calculates estimated costs based on provider pricing models
- **Session Aggregation**: Aggregates token usage across an entire session
- **Operation Breakdown**: Provides usage breakdown by operation type (question_generation, response_analysis, evaluation)

### Key Features

1. **Multi-Provider Support**
   - OpenAI (GPT-4, GPT-4 Turbo, GPT-3.5 Turbo)
   - Anthropic (Claude 3 Opus, Sonnet, Haiku)
   - Fallback to default pricing for unknown providers

2. **Accurate Cost Estimation**
   - Provider-specific pricing per 1M tokens
   - Separate input/output token pricing
   - Precision to 6 decimal places

3. **Database Integration**
   - Persists all token usage records to PostgreSQL
   - Supports querying historical usage
   - Associates usage with sessions

4. **Operation Tracking**
   - Categorizes usage by operation type
   - Enables cost analysis by feature
   - Supports usage optimization

## Usage Example

```python
from src.ai.token_tracker import TokenTracker
from src.database.data_store import PostgresDataStore

# Initialize
db = PostgresDataStore(...)
tracker = TokenTracker(data_store=db)

# Record usage
usage = tracker.record_usage(
    session_id="session-123",
    provider="openai",
    model="gpt-4-turbo-preview",
    operation="question_generation",
    input_tokens=500,
    output_tokens=200
)

# Get session summary
session_usage = tracker.get_session_usage("session-123")
print(f"Total cost: ${session_usage.total_cost:.6f}")

# Get breakdown by operation
breakdown = tracker.get_usage_breakdown("session-123")
for operation, usage in breakdown.items():
    print(f"{operation}: {usage.total_tokens} tokens, ${usage.estimated_cost:.6f}")
```

## Pricing Table

Current pricing (as of 2024):

### OpenAI
- GPT-4 Turbo: $10/1M input, $30/1M output
- GPT-4: $30/1M input, $60/1M output
- GPT-3.5 Turbo: $0.50/1M input, $1.50/1M output

### Anthropic
- Claude 3 Opus: $15/1M input, $75/1M output
- Claude 3 Sonnet: $3/1M input, $15/1M output
- Claude 3 Haiku: $0.25/1M input, $1.25/1M output

## Database Schema

Token usage is stored in the `token_usage` table:

```sql
CREATE TABLE token_usage (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    estimated_cost DECIMAL(10,6) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
```

## Testing

Unit tests are provided in `test_token_tracker_unit.py` that verify:
- Cost calculation accuracy
- Session aggregation
- Operation breakdown
- Multi-provider support
- Unknown provider handling

Run tests with:
```bash
python test_token_tracker_unit.py
```

## Requirements Satisfied

This implementation satisfies the following requirements:

- **14.1**: Records input token count for each AI API call
- **14.2**: Records output token count for each response
- **14.3**: Calculates estimated cost based on provider pricing
- **14.4**: Stores token usage in database with session association
- **14.5**: Provides session usage summary
- **14.6**: Categorizes usage by operation type
