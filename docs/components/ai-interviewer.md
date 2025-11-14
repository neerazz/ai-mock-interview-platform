# AI Interviewer

The AI Interviewer component generates interview questions and analyzes candidate responses using Large Language Models (LLMs).

## Overview

Powered by OpenAI GPT-4 or Anthropic Claude, the AI Interviewer:

- Generates initial interview problems based on resume
- Analyzes candidate responses
- Generates contextual follow-up questions
- Maintains conversation history
- Tracks token usage

## Key Features

### Resume-Aware Problem Generation

The AI analyzes the candidate's resume to generate appropriate problems:

```python
def generate_initial_problem(self, resume_data: ResumeData) -> str:
    """Generate interview problem based on resume.
    
    Considers:
    - Experience level (junior, mid, senior, staff)
    - Domain expertise (e.g., e-commerce, fintech, social media)
    - Technical skills
    - Past projects
    """
```

### Context-Aware Response Analysis

The AI maintains full conversation context including:

- Previous questions and answers
- Whiteboard snapshots
- Clarifying questions asked
- Discussion depth

### Multi-Provider Support

Supports multiple LLM providers through LangChain:

- OpenAI GPT-4 (default)
- Anthropic Claude
- Easy to add new providers

## Usage Example

```python
# Initialize AI Interviewer
ai_interviewer = AIInterviewer(
    provider=OpenAIProvider(api_key=config.openai_api_key),
    token_tracker=TokenTracker(),
    logger=logging_manager
)

# Generate initial problem
problem = ai_interviewer.generate_initial_problem(resume_data)

# Process candidate response
response = ai_interviewer.process_response(
    session_id=session.id,
    response="I would design a distributed system with...",
    whiteboard_image=snapshot_bytes
)
```

## Token Tracking

The AI Interviewer tracks token usage for cost monitoring:

- Input tokens
- Output tokens
- Total cost
- Budget warnings

See [Token Tracking](../features/token-tracking.md) for details.

## Related Components

- [Session Manager](session-manager.md)
- [Evaluation Manager](evaluation-manager.md)
- [Token Tracking](../features/token-tracking.md)
