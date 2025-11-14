# API Reference

This section provides detailed API documentation for all major components of the AI Mock Interview Platform.

## Core Components

### Session Manager

The central orchestrator for interview sessions.

[View Session Manager API →](session-manager.md)

### AI Interviewer

LLM-powered interview question generation and response analysis.

[View AI Interviewer API →](ai-interviewer.md)

### Communication Manager

Multi-modal communication handling (audio, video, whiteboard, screen share).

[View Communication Manager API →](communication-manager.md)

### Evaluation Manager

Interview performance analysis and feedback generation.

[View Evaluation Manager API →](evaluation-manager.md)

### Resume Manager

Resume parsing and analysis for personalized interviews.

[View Resume Manager API →](resume-manager.md)

## Infrastructure Components

### Data Store

PostgreSQL-based data persistence layer.

[View Data Store API →](data-store.md)

### File Storage

Local filesystem storage for media files.

[View File Storage API →](file-storage.md)

### Logging Manager

Comprehensive logging system with multiple outputs.

[View Logging Manager API →](logging-manager.md)

## Data Models

### Session

```python
@dataclass
class Session:
    id: str
    user_id: str
    status: SessionStatus
    config: SessionConfig
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
```

### SessionConfig

```python
@dataclass
class SessionConfig:
    enabled_modes: List[CommunicationMode]
    ai_provider: str
    ai_model: str
    max_tokens: int
    token_warning_threshold: float
```

### Evaluation

```python
@dataclass
class Evaluation:
    session_id: str
    overall_score: float
    competency_scores: Dict[str, float]
    strengths: List[str]
    areas_for_improvement: List[str]
    improvement_plan: ImprovementPlan
    detailed_feedback: str
    created_at: datetime
```

## Enumerations

### SessionStatus

```python
class SessionStatus(Enum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
```

### CommunicationMode

```python
class CommunicationMode(Enum):
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    WHITEBOARD = "whiteboard"
    SCREEN_SHARE = "screen_share"
```

## Exception Hierarchy

```
InterviewPlatformError
├── ConfigurationError
├── SessionError
│   ├── SessionNotFoundError
│   ├── InvalidStateError
│   └── SessionExpiredError
├── DataStoreError
│   ├── DatabaseError
│   └── ConnectionError
├── AIProviderError
│   ├── TokenLimitError
│   └── APIError
└── CommunicationError
    ├── AudioError
    ├── VideoError
    └── WhiteboardError
```

## Usage Examples

### Creating a Session

```python
from src.session import SessionManager
from src.models import SessionConfig, CommunicationMode

# Create session manager
session_manager = SessionManager(
    data_store=data_store,
    ai_interviewer=ai_interviewer,
    evaluation_manager=evaluation_manager,
    communication_manager=communication_manager,
    logger=logger
)

# Configure session
config = SessionConfig(
    enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
    ai_provider="openai",
    ai_model="gpt-4",
    max_tokens=50000,
    token_warning_threshold=0.8
)

# Create session
session = session_manager.create_session(config)
print(f"Session created: {session.id}")
```

### Processing Responses

```python
from src.ai import AIInterviewer

# Initialize AI interviewer
ai_interviewer = AIInterviewer(
    provider=openai_provider,
    token_tracker=token_tracker,
    logger=logger
)

# Process response
response = ai_interviewer.process_response(
    session_id=session.id,
    response="I would design a distributed system with...",
    whiteboard_image=snapshot_bytes
)

print(f"AI: {response.message}")
print(f"Tokens used: {response.tokens_used}")
```

### Generating Evaluation

```python
from src.evaluation import EvaluationManager

# Initialize evaluation manager
evaluation_manager = EvaluationManager(
    data_store=data_store,
    logger=logger
)

# Generate evaluation
evaluation = evaluation_manager.evaluate_session(session.id)

print(f"Overall Score: {evaluation.overall_score}/10")
for competency, score in evaluation.competency_scores.items():
    print(f"{competency}: {score}/10")
```

## Type Definitions

For complete type definitions, see the [models module](https://github.com/yourusername/ai-mock-interview-platform/blob/main/src/models.py).

## Related Documentation

- [Architecture Overview](../architecture.md)
- [Developer Setup](../developer-setup.md)
- [Contributing Guide](../contributing.md)
