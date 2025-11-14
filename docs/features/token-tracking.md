# Token Tracking

The Token Tracking feature monitors AI API usage to help manage costs and prevent budget overruns.

## Overview

Token tracking provides:

- Real-time token usage monitoring
- Cost estimation
- Budget warnings
- Historical usage data

## How It Works

### Token Counting

The system tracks:

- **Input tokens**: Prompt and context sent to AI
- **Output tokens**: AI-generated responses
- **Total tokens**: Sum of input and output

### Cost Calculation

Costs are calculated based on provider pricing:

**OpenAI GPT-4:**
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

**Anthropic Claude:**
- Input: $0.015 per 1K tokens
- Output: $0.075 per 1K tokens

### Budget Management

Set a token budget per session:

```python
config = SessionConfig(
    max_tokens=50000,  # 50K token budget
    token_warning_threshold=0.8  # Warn at 80%
)
```

## UI Indicators

### Progress Bar

Visual indicator showing:
- Green: < 70% used
- Yellow: 70-90% used
- Red: > 90% used

### Token Counter

Displays: `12,450 / 50,000 tokens ($0.85)`

### Warnings

- **80% threshold**: "Approaching token budget limit"
- **100% threshold**: "Token budget exceeded"

## Historical Data

View token usage across sessions:

- Total tokens used
- Total cost
- Average per session
- Trends over time

## Configuration

Set default budgets in `config.yaml`:

```yaml
token_tracking:
  default_budget: 50000
  warning_threshold: 0.8
  track_by_component: true
```

## API Reference

```python
class TokenTracker:
    def track_usage(
        self,
        session_id: str,
        input_tokens: int,
        output_tokens: int,
        provider: str,
        model: str
    ) -> TokenUsage
    
    def get_session_usage(self, session_id: str) -> TokenUsage
    
    def check_budget(self, session_id: str) -> BudgetStatus
```

## Related Features

- [AI Interviewer](../components/ai-interviewer.md)
- [Logging](logging.md)
