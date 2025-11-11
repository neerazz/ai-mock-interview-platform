# AI Interviewer Agent Documentation

## Overview

The AI Interviewer Agent is a core component of the AI Mock Interview Platform that conducts system design interviews using LangChain and large language models (LLMs). It provides intelligent question generation, response analysis, and adaptive difficulty adjustment.

## Architecture

### Class: `AIInterviewer`

Located in `src/ai/ai_interviewer.py`

The AIInterviewer class manages the interview conversation flow, generates questions, analyzes responses, and provides contextual follow-ups.

### Key Features

1. **Multi-Provider Support**
   - OpenAI GPT-4 and GPT-4 Turbo
   - Anthropic Claude 3 (Opus, Sonnet, Haiku)
   - Easy to extend for additional providers

2. **Resume-Aware Problem Generation**
   - Tailors problems to candidate's experience level (junior/mid/senior/staff)
   - Considers domain expertise (backend, distributed systems, cloud, etc.)
   - Adjusts difficulty based on years of experience

3. **Intelligent Response Processing**
   - Analyzes candidate responses for completeness and clarity
   - Generates contextually relevant follow-up questions
   - Asks clarifying questions for ambiguous responses
   - Covers key system design topics (scalability, reliability, trade-offs)

4. **Conversation Memory Management**
   - Uses LangChain's ConversationBufferMemory
   - Maintains full conversation history
   - Provides context for follow-up questions

5. **Token Tracking**
   - Tracks all API calls with input/output tokens
   - Calculates estimated costs per operation
   - Integrates with TokenTracker for session-level analytics

6. **Retry Logic with Exponential Backoff**
   - Automatically retries failed API calls (max 3 attempts)
   - Exponential backoff: 1s, 2s, 4s delays
   - Handles transient API failures gracefully

7. **Comprehensive Logging**
   - Logs all operations with structured context
   - Includes session_id for traceability
   - Tracks performance metrics (duration, token usage)

## Usage

### Initialization

```python
from src.ai.ai_interviewer import AIInterviewer
from src.ai.token_tracker import TokenTracker
from src.log_manager.logging_manager import LoggingManager

# Create dependencies
token_tracker = TokenTracker(data_store=data_store, logger=logger)
logger = LoggingManager(config=logging_config, data_store=data_store)

# Initialize interviewer
interviewer = AIInterviewer(
    provider="openai",
    model="gpt-4-turbo-preview",
    api_key="your-api-key",
    token_tracker=token_tracker,
    temperature=0.7,
    max_tokens=2000,
    logger=logger
)
```

### Starting an Interview

```python
# Initialize for a session
interviewer.initialize(
    session_id="session_123",
    resume_data=resume_data  # Optional
)

# Start the interview
response = interviewer.start_interview()
print(response.content)  # Opening question
print(f"Tokens used: {response.token_usage.total_tokens}")
print(f"Cost: ${response.token_usage.estimated_cost:.4f}")
```

### Processing Candidate Responses

```python
# Process candidate's response
candidate_response = "I would use a load balancer to distribute traffic..."
response = interviewer.process_response(candidate_response)
print(response.content)  # Follow-up question
```

### Resume-Aware Problem Generation

```python
# Generate problem based on resume
problem = interviewer.generate_problem(resume_data)
print(problem)
```

### Asking Clarifying Questions

```python
# When response is ambiguous
ambiguous_response = "I would just handle it."
response = interviewer.ask_clarifying_question(ambiguous_response)
print(response.content)  # Clarifying question
```

### Adapting Difficulty

```python
# Adjust difficulty based on performance
performance_indicators = {
    "response_quality": "high",
    "depth_of_understanding": "deep",
    "technical_accuracy": "accurate"
}
interviewer.adapt_difficulty(performance_indicators)
```

### Whiteboard Analysis

```python
# Analyze whiteboard diagram (placeholder implementation)
whiteboard_image = load_image_bytes("whiteboard.png")
analysis = interviewer.analyze_whiteboard(whiteboard_image)
print(f"Components: {analysis.components_identified}")
print(f"Relationships: {analysis.relationships}")
print(f"Missing: {analysis.missing_elements}")
```

## API Reference

### Constructor

```python
AIInterviewer(
    provider: str,
    model: str,
    api_key: str,
    token_tracker: TokenTracker,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    logger = None
)
```

**Parameters:**
- `provider`: AI provider name ("openai" or "anthropic")
- `model`: Model name (e.g., "gpt-4-turbo-preview", "claude-3-opus-20240229")
- `api_key`: API key for the provider
- `token_tracker`: TokenTracker instance for usage monitoring
- `temperature`: Sampling temperature (0-2), default 0.7
- `max_tokens`: Maximum tokens per response, default 2000
- `logger`: Optional LoggingManager instance

**Raises:**
- `AIProviderError`: If provider initialization fails

### Methods

#### `initialize(session_id: str, resume_data: Optional[ResumeData] = None) -> None`

Initialize interviewer for a new session.

**Parameters:**
- `session_id`: Session identifier
- `resume_data`: Optional resume data for context-aware questions

#### `start_interview() -> InterviewResponse`

Start the interview with an opening question.

**Returns:**
- `InterviewResponse` with opening question and token usage

**Raises:**
- `AIProviderError`: If question generation fails

#### `process_response(candidate_response: str, whiteboard_image: Optional[bytes] = None) -> InterviewResponse`

Process candidate response and generate follow-up question.

**Parameters:**
- `candidate_response`: Candidate's text response
- `whiteboard_image`: Optional whiteboard image for analysis

**Returns:**
- `InterviewResponse` with follow-up question and token usage

**Raises:**
- `AIProviderError`: If response processing fails

#### `generate_problem(resume_data: ResumeData) -> str`

Generate a system design problem tailored to candidate's resume.

**Parameters:**
- `resume_data`: Candidate's resume data

**Returns:**
- Problem statement string

**Raises:**
- `AIProviderError`: If problem generation fails

#### `analyze_whiteboard(whiteboard_image: bytes) -> WhiteboardAnalysis`

Analyze whiteboard diagram using vision-enabled LLM.

**Parameters:**
- `whiteboard_image`: Whiteboard image as bytes

**Returns:**
- `WhiteboardAnalysis` with identified elements

**Raises:**
- `AIProviderError`: If whiteboard analysis fails

**Note:** Currently returns placeholder data. Full implementation requires vision-enabled models.

#### `ask_clarifying_question(ambiguous_response: str) -> InterviewResponse`

Generate a clarifying question for an ambiguous response.

**Parameters:**
- `ambiguous_response`: The candidate's ambiguous response

**Returns:**
- `InterviewResponse` with clarifying question and token usage

**Raises:**
- `AIProviderError`: If question generation fails

#### `adapt_difficulty(performance_indicators: Dict[str, Any]) -> None`

Adapt question difficulty based on candidate performance.

**Parameters:**
- `performance_indicators`: Dictionary with performance metrics
  - `response_quality`: "high", "medium", "low"
  - `depth_of_understanding`: "deep", "moderate", "shallow"
  - `technical_accuracy`: "accurate", "mostly_accurate", "inaccurate"

#### `generate_followup(context: ConversationContext) -> InterviewResponse`

Generate a follow-up question based on conversation context.

**Parameters:**
- `context`: Conversation context with messages and metadata

**Returns:**
- `InterviewResponse` with follow-up question and token usage

**Raises:**
- `AIProviderError`: If follow-up generation fails

#### `get_conversation_history() -> List[Message]`

Get the conversation history from memory.

**Returns:**
- List of Message objects representing the conversation

#### `clear_memory() -> None`

Clear conversation memory.

## System Prompt

The AI Interviewer uses a carefully crafted system prompt that defines its role and behavior:

```
You are an expert technical interviewer conducting a system design interview. 
Your role is to:
1. Ask thoughtful, probing questions about system architecture and design
2. Evaluate the candidate's understanding of scalability, reliability, and trade-offs
3. Provide constructive follow-up questions based on their responses
4. Adapt the difficulty based on the candidate's experience level
5. Focus on real-world scenarios and practical considerations

Guidelines:
- Be professional and encouraging
- Ask one question at a time
- Listen carefully to responses before asking follow-ups
- Cover key topics: scalability, reliability, data consistency, trade-offs, monitoring
- Ask clarifying questions when responses are ambiguous
- Probe deeper into design decisions and their implications

Remember: You are evaluating their thought process, not just the final solution.
```

## Resume-Aware Problem Generation

The interviewer generates problems tailored to the candidate's background:

### Experience Level Mapping

- **Junior (0-2 years)**: Focus on basic system components and simple scaling
- **Mid (3-5 years)**: Include distributed systems concepts and trade-offs
- **Senior (6-10 years)**: Complex systems with multiple services and data consistency
- **Staff (10+ years)**: Large-scale systems with organizational and technical challenges

### Domain Expertise Consideration

Problems are tailored to the candidate's domain expertise:
- Backend: API design, database optimization, caching strategies
- Distributed Systems: Consistency models, partitioning, replication
- Cloud: Cloud-native architectures, serverless, container orchestration
- Frontend: Client-side architecture, state management, performance optimization

## Error Handling

The AI Interviewer implements comprehensive error handling:

1. **Retry Logic**: Automatic retry with exponential backoff for transient failures
2. **Graceful Degradation**: Falls back to default behavior when optional features fail
3. **Detailed Logging**: All errors logged with full context and stack traces
4. **Custom Exceptions**: Uses `AIProviderError` for provider-specific errors

## Token Tracking

All API calls are tracked for cost monitoring:

```python
# Token usage is automatically recorded
response = interviewer.process_response(candidate_response)

# Access token usage
print(f"Input tokens: {response.token_usage.input_tokens}")
print(f"Output tokens: {response.token_usage.output_tokens}")
print(f"Total tokens: {response.token_usage.total_tokens}")
print(f"Estimated cost: ${response.token_usage.estimated_cost:.6f}")

# Get session-level usage
session_usage = token_tracker.get_session_usage(session_id)
print(f"Total session cost: ${session_usage.total_cost:.2f}")
```

## Performance Considerations

- **Response Time**: Typically 1-3 seconds per API call
- **Token Limits**: Configurable max_tokens parameter (default 2000)
- **Memory Management**: Conversation history stored in memory (consider truncation for long sessions)
- **Retry Delays**: 1s, 2s, 4s exponential backoff (max 3 attempts)

## Future Enhancements

1. **Vision API Integration**: Full whiteboard analysis using GPT-4 Vision or Claude 3
2. **Streaming Responses**: Real-time response streaming for better UX
3. **Multi-turn Planning**: Advanced conversation planning for complex topics
4. **Performance Metrics**: Real-time performance assessment during interview
5. **Custom Prompts**: User-configurable system prompts for different interview styles

## Dependencies

- `langchain`: Core LangChain framework
- `langchain-openai`: OpenAI integration
- `langchain-anthropic`: Anthropic integration
- `openai`: OpenAI Python client
- `anthropic`: Anthropic Python client

## Testing

See `test_ai_interviewer.py` for comprehensive unit tests covering:
- Initialization with different providers
- Session management
- Problem generation
- Response processing
- Clarifying questions
- Difficulty adaptation
- Whiteboard analysis
- Conversation history management

## Related Components

- **TokenTracker** (`src/ai/token_tracker.py`): Token usage tracking and cost estimation
- **LoggingManager** (`src/log_manager/logging_manager.py`): Comprehensive logging
- **ResumeManager** (`src/resume/resume_manager.py`): Resume parsing and analysis
- **Models** (`src/models.py`): Data models for interview components

## Example: Complete Interview Flow

```python
# Initialize components
interviewer = AIInterviewer(
    provider="openai",
    model="gpt-4-turbo-preview",
    api_key=api_key,
    token_tracker=token_tracker,
    logger=logger
)

# Start session
interviewer.initialize(session_id, resume_data)
opening = interviewer.start_interview()
print(f"Interviewer: {opening.content}")

# Interview loop
while not session_ended:
    # Get candidate response
    candidate_response = get_user_input()
    
    # Process response
    response = interviewer.process_response(candidate_response)
    print(f"Interviewer: {response.content}")
    
    # Track tokens
    print(f"Tokens: {response.token_usage.total_tokens}, Cost: ${response.token_usage.estimated_cost:.4f}")
    
    # Optionally adapt difficulty
    if should_adapt_difficulty():
        performance = assess_performance(candidate_response)
        interviewer.adapt_difficulty(performance)

# Get conversation history
history = interviewer.get_conversation_history()
save_conversation(history)
```

## Troubleshooting

### Issue: API Rate Limits

**Solution**: The retry logic handles rate limits automatically. If persistent, consider:
- Reducing request frequency
- Using a different model tier
- Implementing request queuing

### Issue: High Token Usage

**Solution**:
- Reduce `max_tokens` parameter
- Truncate conversation history for long sessions
- Use cheaper models for non-critical operations

### Issue: Slow Response Times

**Solution**:
- Use faster models (e.g., GPT-3.5 Turbo instead of GPT-4)
- Reduce `max_tokens` parameter
- Implement response streaming (future enhancement)

### Issue: Memory Growth

**Solution**:
- Call `clear_memory()` periodically for very long sessions
- Implement conversation history truncation
- Consider using ConversationSummaryMemory for long sessions

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Review the test suite for usage examples
3. Consult the design document for architecture details
4. Check token usage and costs in the database
