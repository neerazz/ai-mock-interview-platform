# Session Manager

The Session Manager orchestrates the complete interview session lifecycle, coordinating between the AI Interviewer, Evaluation Manager, Communication Manager, and Data Store.

## Overview

The `SessionManager` class is responsible for:
- Creating new interview sessions with unique identifiers
- Starting sessions and initializing all components
- Managing session state transitions (active, paused, completed)
- Ending sessions and triggering evaluation generation
- Retrieving session information and history

## Architecture

The Session Manager follows the dependency injection pattern, receiving all dependencies through its constructor:

```python
session_manager = SessionManager(
    data_store=data_store,
    ai_interviewer=ai_interviewer,
    evaluation_manager=evaluation_manager,
    communication_manager=communication_manager,
    logger=logger
)
```

## Key Features

### 1. Session Creation

Creates a new interview session with a unique UUID identifier:

```python
config = SessionConfig(
    enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
    ai_provider="openai",
    ai_model="gpt-4",
    resume_data=resume_data,
    duration_minutes=45
)

session = session_manager.create_session(config)
```

**Features:**
- Generates unique session ID using UUID
- Extracts user_id from resume data or generates one
- Stores session metadata in database
- Returns Session object with all details

### 2. Session Start

Starts an interview session and initializes all components:

```python
session_manager.start_session(session_id)
```

**What happens:**
1. Retrieves session from database
2. Initializes AI Interviewer with session context and resume data
3. Enables configured communication modes
4. Generates opening question from AI Interviewer
5. Saves opening message to conversation history
6. Sets session as active

### 3. Session End

Ends an interview session and generates evaluation:

```python
evaluation = session_manager.end_session(session_id)
```

**What happens:**
1. Retrieves session from database
2. Marks session as completed with end timestamp
3. Clears active session
4. Disables all communication modes
5. Triggers evaluation generation
6. Returns EvaluationReport

### 4. Session State Management

The Session Manager supports three session states:

- **ACTIVE**: Session is currently running
- **PAUSED**: Session is temporarily paused
- **COMPLETED**: Session has ended

```python
# Pause a session
session_manager.pause_session(session_id)

# Resume a paused session
session_manager.resume_session(session_id)
```

### 5. Session Retrieval

Retrieve session information:

```python
# Get specific session
session = session_manager.get_session(session_id)

# Get active session
active_session = session_manager.get_active_session()

# List sessions with pagination
sessions = session_manager.list_sessions(
    user_id="user_123",
    limit=50,
    offset=0
)
```

## Session Lifecycle

```
┌─────────────────┐
│  Create Session │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Start Session  │
│  - Initialize AI│
│  - Enable modes │
│  - Open question│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Active Session  │◄──┐
│  - Conversation │   │
│  - Whiteboard   │   │
│  - Recording    │   │
└────────┬────────┘   │
         │            │
         │  ┌─────────┴────────┐
         │  │  Pause/Resume    │
         │  └──────────────────┘
         │
         ▼
┌─────────────────┐
│   End Session   │
│  - Mark complete│
│  - Disable modes│
│  - Generate eval│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Completed    │
└─────────────────┘
```

## Integration with Other Components

### AI Interviewer Integration

The Session Manager initializes the AI Interviewer with:
- Session ID for tracking
- Resume data for context-aware questions
- System design interview context

```python
ai_interviewer.initialize(
    session_id=session_id,
    resume_data=resume_data
)
```

### Communication Manager Integration

The Session Manager:
- Enables communication modes based on session configuration
- Disables all modes when session ends
- Tracks which modes are active

```python
for mode in session.config.enabled_modes:
    communication_manager.enable_mode(mode)
```

### Evaluation Manager Integration

The Session Manager triggers evaluation generation when a session ends:

```python
evaluation = evaluation_manager.generate_evaluation(session_id)
```

### Data Store Integration

The Session Manager persists:
- Session metadata (creation time, status, configuration)
- Conversation messages
- Session state transitions

## Error Handling

The Session Manager raises `InterviewPlatformError` for:
- Session not found
- Invalid state transitions (e.g., ending a completed session)
- Component initialization failures
- Database operation failures

All errors are logged with full context for debugging.

## Logging

The Session Manager logs:
- Session creation with configuration details
- Session start with enabled modes
- Session end with duration and score
- State transitions (pause/resume)
- All errors with stack traces

Example log entry:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "component": "SessionManager",
  "operation": "start_session",
  "message": "Session abc-123 started successfully",
  "session_id": "abc-123",
  "metadata": {
    "enabled_modes": ["text", "whiteboard"]
  }
}
```

## Usage Example

Complete workflow example:

```python
from src.session.session_manager import SessionManager
from src.models import SessionConfig, CommunicationMode

# Create session manager (with injected dependencies)
session_manager = SessionManager(
    data_store=data_store,
    ai_interviewer=ai_interviewer,
    evaluation_manager=evaluation_manager,
    communication_manager=communication_manager,
    logger=logger
)

# Create session configuration
config = SessionConfig(
    enabled_modes=[
        CommunicationMode.TEXT,
        CommunicationMode.WHITEBOARD,
        CommunicationMode.AUDIO
    ],
    ai_provider="openai",
    ai_model="gpt-4",
    resume_data=resume_data,
    duration_minutes=45
)

# Create new session
session = session_manager.create_session(config)
print(f"Created session: {session.id}")

# Start the session
session_manager.start_session(session.id)
print("Session started - interview in progress")

# ... interview happens here ...

# End the session
evaluation = session_manager.end_session(session.id)
print(f"Session ended - Overall score: {evaluation.overall_score}")

# View session history
sessions = session_manager.list_sessions(user_id=session.user_id)
for s in sessions:
    print(f"Session {s.id}: {s.overall_score}/100")
```

## Testing

The Session Manager includes comprehensive unit tests covering:
- Session creation with and without resume data
- Session start with component initialization
- Session end with evaluation generation
- State transitions (pause/resume)
- Session retrieval and listing
- Error handling for invalid operations

Run tests:
```bash
python -m pytest test_session_manager.py -v
```

## Requirements Mapping

The Session Manager implementation satisfies the following requirements:

- **Requirement 1.1**: Provides interface to initiate new interview sessions
- **Requirement 1.2**: Creates unique session identifiers using UUID
- **Requirement 1.3**: Initializes AI Interviewer with system design context
- **Requirement 1.4**: Stores session metadata in database
- **Requirement 5.1**: Provides control to end interview sessions
- **Requirement 5.2**: Stops accepting inputs when session ends
- **Requirement 5.3**: Triggers evaluation generation on session end
- **Requirement 5.4**: Saves complete session recording
- **Requirement 5.5**: Marks session as completed in database
- **Requirement 7.1**: Provides interface to list completed sessions
- **Requirement 7.2**: Displays session metadata (date, duration, score)
- **Requirement 7.5**: Orders sessions by date with most recent first

## Future Enhancements

Potential improvements for future versions:

1. **Session Templates**: Pre-configured session templates for different interview types
2. **Session Scheduling**: Schedule sessions for future times
3. **Session Sharing**: Share session recordings with others
4. **Session Analytics**: Aggregate analytics across multiple sessions
5. **Session Export**: Export session data in various formats
6. **Session Replay**: Replay sessions with timeline controls
