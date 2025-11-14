# Session Manager

The Session Manager is the central orchestrator of the AI Mock Interview Platform, coordinating the interview lifecycle and managing interactions between all major components.

## Overview

The Session Manager handles:

- Creating and configuring interview sessions
- Starting and ending sessions
- Managing session state transitions
- Coordinating between AI Interviewer, Communication Manager, and Evaluation Manager
- Persisting session data

## Architecture

```python
class SessionManager:
    def __init__(
        self,
        data_store: DataStore,
        ai_interviewer: AIInterviewer,
        evaluation_manager: EvaluationManager,
        communication_manager: CommunicationManager,
        logger: LoggingManager
    ):
        self.data_store = data_store
        self.ai_interviewer = ai_interviewer
        self.evaluation_manager = evaluation_manager
        self.communication_manager = communication_manager
        self.logger = logger
```

## Key Methods

### create_session

Creates a new interview session with the specified configuration.

```python
def create_session(self, config: SessionConfig) -> Session:
    """Create a new interview session.
    
    Args:
        config: Session configuration including enabled modes and AI provider
        
    Returns:
        Created session with unique identifier
        
    Raises:
        ConfigurationError: If configuration is invalid
        DataStoreError: If database operation fails
    """
```

### start_session

Starts an interview session and enables communication modes.

```python
def start_session(self, session_id: str) -> None:
    """Start an interview session.
    
    Args:
        session_id: Unique session identifier
        
    Raises:
        SessionNotFoundError: If session doesn't exist
        InvalidStateError: If session is not in CREATED state
    """
```

### end_session

Ends an interview session and generates evaluation.

```python
def end_session(self, session_id: str) -> Evaluation:
    """End session and generate evaluation.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Evaluation report with scores and feedback
        
    Raises:
        SessionNotFoundError: If session doesn't exist
        InvalidStateError: If session is not in ACTIVE state
    """
```

## State Machine

Sessions progress through the following states:

```
[CREATED] → start_session() → [ACTIVE]
[ACTIVE] → end_session() → [COMPLETED]
[ACTIVE] → pause_session() → [PAUSED]
[PAUSED] → resume_session() → [ACTIVE]
```

## Usage Example

```python
# Create session manager with dependencies
session_manager = SessionManager(
    data_store=postgres_data_store,
    ai_interviewer=ai_interviewer,
    evaluation_manager=evaluation_manager,
    communication_manager=communication_manager,
    logger=logging_manager
)

# Create new session
config = SessionConfig(
    enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
    ai_provider="openai",
    ai_model="gpt-4"
)
session = session_manager.create_session(config)

# Start session
session_manager.start_session(session.id)

# ... interview interaction ...

# End session and get evaluation
evaluation = session_manager.end_session(session.id)
```

## Error Handling

The Session Manager handles various error scenarios:

- **Configuration errors**: Invalid session configuration
- **State errors**: Invalid state transitions
- **Database errors**: Data persistence failures
- **Component errors**: Failures in dependent components

All errors are logged with full context for debugging.

## Testing

The Session Manager is designed for testability with dependency injection:

```python
def test_create_session():
    # Arrange
    mock_data_store = Mock(spec=DataStore)
    mock_ai_interviewer = Mock(spec=AIInterviewer)
    session_manager = SessionManager(
        data_store=mock_data_store,
        ai_interviewer=mock_ai_interviewer,
        # ... other mocks
    )
    
    # Act
    session = session_manager.create_session(config)
    
    # Assert
    assert session.id is not None
    mock_data_store.save_session.assert_called_once()
```

## Related Components

- [AI Interviewer](ai-interviewer.md)
- [Communication Manager](communication-manager.md)
- [Evaluation Manager](evaluation-manager.md)
