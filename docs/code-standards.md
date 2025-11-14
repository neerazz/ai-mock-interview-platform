# Code Standards

This document outlines the coding standards and best practices for the AI Mock Interview Platform.

## Python Style Guide

### PEP 8 Compliance

Follow [PEP 8](https://pep8.org/) with these specifics:

- **Indentation**: 4 spaces (no tabs)
- **Line Length**: 88 characters (Black default)
- **Blank Lines**: 2 between top-level definitions, 1 between methods
- **Imports**: Grouped and sorted (stdlib, third-party, local)

### Naming Conventions

```python
# Variables and functions: snake_case
user_name = "John"
def calculate_score():
    pass

# Classes: PascalCase
class SessionManager:
    pass

# Constants: UPPER_CASE
MAX_TOKENS = 50000
DEFAULT_PROVIDER = "openai"

# Private members: _leading_underscore
def _internal_helper():
    pass
```

## Type Hints

### Always Use Type Hints

```python
from typing import Optional, List, Dict

def process_response(
    session_id: str,
    response: str,
    whiteboard_image: Optional[bytes] = None
) -> InterviewResponse:
    pass
```

### Complex Types

```python
from typing import Union, Callable, TypeVar

T = TypeVar('T')

def get_or_default(
    value: Optional[T],
    default: T
) -> T:
    return value if value is not None else default
```

## Docstrings

### Google Style

```python
def create_session(self, config: SessionConfig) -> Session:
    """Create a new interview session.
    
    This method creates a new session with the provided configuration,
    initializes all required components, and persists the session to
    the database.
    
    Args:
        config: Session configuration including enabled communication
            modes, AI provider selection, and token budget settings.
        
    Returns:
        A Session object with a unique identifier and CREATED status.
        
    Raises:
        ConfigurationError: If the configuration is invalid or incomplete.
        DataStoreError: If the database operation fails.
        
    Example:
        >>> config = SessionConfig(
        ...     enabled_modes=[CommunicationMode.TEXT],
        ...     ai_provider="openai"
        ... )
        >>> session = manager.create_session(config)
        >>> print(session.id)
        '550e8400-e29b-41d4-a716-446655440000'
    """
    pass
```

## Error Handling

### Use Specific Exceptions

```python
# Good
try:
    session = self.data_store.get_session(session_id)
except SessionNotFoundError:
    raise
except DatabaseError as e:
    raise DataStoreError(f"Failed to retrieve session: {e}") from e

# Bad
try:
    session = self.data_store.get_session(session_id)
except Exception:
    pass
```

### Always Log Errors

```python
try:
    result = risky_operation()
except OperationError as e:
    self.logger.error(
        "operation_failed",
        operation="risky_operation",
        error=str(e),
        session_id=session_id
    )
    raise
```

## SOLID Principles

### Single Responsibility

Each class should have one clear purpose:

```python
# Good: Focused responsibility
class SessionManager:
    """Manages interview session lifecycle."""
    pass

class DataStore:
    """Handles data persistence."""
    pass

# Bad: Multiple responsibilities
class SessionManagerAndDataStore:
    """Manages sessions AND handles persistence."""
    pass
```

### Dependency Injection

Always inject dependencies:

```python
# Good
class SessionManager:
    def __init__(
        self,
        data_store: DataStore,
        ai_interviewer: AIInterviewer
    ):
        self.data_store = data_store
        self.ai_interviewer = ai_interviewer

# Bad
class SessionManager:
    def __init__(self):
        self.data_store = PostgresDataStore()  # Hard-coded dependency
```

## Code Organization

### File Structure

```python
# 1. Module docstring
"""Session management module.

This module provides the SessionManager class for orchestrating
interview sessions.
"""

# 2. Imports (grouped and sorted)
import logging
from typing import Optional

from langchain import LLMChain

from src.models import Session
from src.database import DataStore

# 3. Constants
MAX_SESSION_DURATION = 7200  # 2 hours

# 4. Classes and functions
class SessionManager:
    pass
```

### Keep Functions Small

```python
# Good: Small, focused function
def validate_config(config: SessionConfig) -> None:
    """Validate session configuration."""
    if not config.enabled_modes:
        raise ConfigurationError("At least one mode must be enabled")
    if not config.ai_provider:
        raise ConfigurationError("AI provider must be specified")

# Bad: Large, complex function
def create_and_start_session_with_validation_and_logging(config):
    # 100+ lines of mixed concerns
    pass
```

## Testing Standards

### Test Structure

```python
def test_create_session_with_valid_config():
    """Test session creation with valid configuration."""
    # Arrange
    mock_data_store = Mock(spec=DataStore)
    session_manager = SessionManager(data_store=mock_data_store)
    config = SessionConfig(enabled_modes=[CommunicationMode.TEXT])
    
    # Act
    session = session_manager.create_session(config)
    
    # Assert
    assert session.id is not None
    assert session.status == SessionStatus.CREATED
    mock_data_store.save_session.assert_called_once()
```

### Test Naming

```python
# Good: Descriptive test names
def test_create_session_with_invalid_config_raises_error():
    pass

def test_end_session_generates_evaluation():
    pass

# Bad: Vague test names
def test_session():
    pass

def test_1():
    pass
```

## Performance Guidelines

### Use Appropriate Data Structures

```python
# Good: O(1) lookup
user_sessions = {user_id: session for user_id, session in sessions}
session = user_sessions.get(user_id)

# Bad: O(n) lookup
session = next(s for s in sessions if s.user_id == user_id)
```

### Avoid Premature Optimization

```python
# Good: Clear and correct
def calculate_score(scores: List[float]) -> float:
    return sum(scores) / len(scores)

# Bad: Premature optimization
def calculate_score(scores: List[float]) -> float:
    # Complex optimization that's hard to read
    pass
```

## Security Guidelines

### Never Log Sensitive Data

```python
# Good
self.logger.info("User authenticated", user_id=user.id)

# Bad
self.logger.info("User authenticated", password=user.password)
```

### Validate Input

```python
def process_response(self, response: str) -> None:
    """Process user response."""
    if not response or len(response) > 10000:
        raise ValueError("Invalid response length")
    
    # Process response
    pass
```

## Documentation Standards

### README Files

Every module should have a README explaining:
- Purpose
- Key components
- Usage examples
- Dependencies

### Code Comments

```python
# Good: Explain WHY, not WHAT
# Use exponential backoff to handle transient network errors
retry_delay = 2 ** attempt

# Bad: Explain obvious code
# Increment counter by 1
counter += 1
```

## Git Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Tests
- `chore`: Maintenance

### Examples

```
feat(ai): add Claude 3 support

Implement Anthropic Claude 3 provider with streaming support.
Add configuration options for model selection.

Closes #123
```

## Tools and Automation

### Pre-commit Hooks

Required checks:
- Black (formatting)
- Ruff (linting)
- mypy (type checking)
- isort (import sorting)

### CI/CD Pipeline

All PRs must pass:
- Unit tests
- Integration tests
- Code coverage (80%+)
- Type checking
- Linting

## Related Documents

- [Contributing Guide](contributing.md)
- [Developer Setup](developer-setup.md)
- [Architecture](architecture.md)
