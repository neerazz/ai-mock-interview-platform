# Logging System Documentation

## Overview

The AI Mock Interview Platform includes a comprehensive logging system that provides multiple output handlers for debugging, monitoring, and audit trails.

## Features

- **Multiple Handlers**: Console, rotating file, and database logging
- **Structured JSON Format**: Machine-readable logs for aggregation and analysis
- **Configurable Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context-Aware**: Includes session_id and user_id when available
- **Error Tracking**: Full stack traces with contextual information
- **API Call Logging**: Request/response details with timing metrics

## Architecture

### Components

1. **LoggingManager**: Main logging interface
2. **DatabaseLogHandler**: Custom handler for database audit logs
3. **JSONFormatter**: Structured JSON log formatting
4. **RotatingFileHandler**: File logging with size/time limits

### Log Destinations

1. **Console**: Real-time output during development
2. **File**: Rotating log files in `logs/interview_platform.log`
3. **Database**: Structured logs in `audit_logs` table

## Configuration

Configure logging in `config.yaml`:

```yaml
logging:
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "json"               # json or text
  console_output: true         # Enable console logging
  file_output: true            # Enable file logging
  database_output: true        # Enable database logging
  max_file_size_mb: 10        # Max file size before rotation
  backup_count: 5             # Number of backup files to keep
```

## Usage

### Basic Initialization

```python
from src.config import get_config
from src.log_manager import LoggingManager

# Load configuration
config = get_config()

# Initialize logging manager
logger = LoggingManager(config.logging)
```

### Logging Operations

```python
# Info message
logger.info(
    component="SessionManager",
    operation="create_session",
    message="Creating new interview session",
    session_id="session-123",
    metadata={"user_id": "user-456"}
)

# Debug message
logger.debug(
    component="AIInterviewer",
    operation="generate_question",
    message="Generating interview question",
    session_id="session-123"
)

# Warning message
logger.warning(
    component="CommunicationManager",
    operation="enable_audio",
    message="Audio device not found, using default",
    session_id="session-123"
)

# Error with exception
try:
    # Some operation
    pass
except Exception as e:
    logger.error(
        component="DataStore",
        operation="save_session",
        message="Failed to save session",
        session_id="session-123",
        exc_info=e
    )
```

### Logging Errors with Context

```python
try:
    # Some operation that might fail
    result = risky_operation()
except Exception as e:
    logger.log_error(
        component="FileStorage",
        operation="save_audio",
        error=e,
        session_id="session-123",
        context={
            "file_path": "/path/to/file",
            "file_size": 1024000
        }
    )
```

### Logging API Calls

```python
import time

start_time = time.time()
response = api_client.call(request_data)
duration_ms = (time.time() - start_time) * 1000

logger.log_api_call(
    provider="OpenAI",
    endpoint="/v1/chat/completions",
    request_data={"model": "gpt-4", "messages": [...]},
    response_data={"choices": [...]},
    duration_ms=duration_ms,
    session_id="session-123"
)
```

## Integration with Database

To enable database logging, set the data store after initialization:

```python
from src.database.data_store import PostgresDataStore

# Initialize data store with logger
data_store = PostgresDataStore(
    host="localhost",
    port=5432,
    database="interview_platform",
    user="interview_user",
    password="password",
    logger=logger
)

# Set data store for database logging
logger.set_data_store(data_store)
```

## Log Format

### JSON Format (Default)

```json
{
  "timestamp": "2025-11-10T14:30:00.123Z",
  "level": "INFO",
  "component": "SessionManager",
  "operation": "create_session",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Session created successfully",
  "metadata": {
    "user_id": "user-123",
    "duration_minutes": 45
  }
}
```

### Error Log with Stack Trace

```json
{
  "timestamp": "2025-11-10T14:30:00.123Z",
  "level": "ERROR",
  "component": "AIInterviewer",
  "operation": "process_response",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Failed to process candidate response",
  "metadata": {
    "response_length": 250
  },
  "stack_trace": "Traceback (most recent call last):\n  File \"...\", line 42, in process_response\n    ...\nValueError: Invalid response format\n"
}
```

## Database Schema

Logs are stored in the `audit_logs` table:

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    session_id UUID,
    user_id VARCHAR(100),
    message TEXT NOT NULL,
    stack_trace TEXT,
    metadata JSONB DEFAULT '{}'::jsonb
);
```

## Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Critical events that may cause the application to abort

### 2. Include Context

Always include `session_id` when available:

```python
logger.info(
    component="Component",
    operation="operation",
    message="Message",
    session_id=session_id  # Always include when available
)
```

### 3. Add Metadata

Include relevant metadata for debugging:

```python
logger.info(
    component="FileStorage",
    operation="save_file",
    message="File saved successfully",
    session_id=session_id,
    metadata={
        "file_type": "audio",
        "file_size_bytes": 1024000,
        "duration_seconds": 45
    }
)
```

### 4. Log Errors with Full Context

```python
try:
    operation()
except Exception as e:
    logger.log_error(
        component="Component",
        operation="operation",
        error=e,
        session_id=session_id,
        context={
            "input_data": input_data,
            "state": current_state
        }
    )
```

### 5. Sanitize Sensitive Data

Never log sensitive information like API keys, passwords, or PII:

```python
# BAD
logger.info(
    component="Config",
    operation="load",
    message="Configuration loaded",
    metadata={"api_key": config.api_key}  # Don't do this!
)

# GOOD
logger.info(
    component="Config",
    operation="load",
    message="Configuration loaded",
    metadata={"api_key_present": bool(config.api_key)}
)
```

## Querying Logs

### From Database

```sql
-- Get all errors for a session
SELECT timestamp, component, operation, message, stack_trace
FROM audit_logs
WHERE session_id = '550e8400-e29b-41d4-a716-446655440000'
  AND level = 'ERROR'
ORDER BY timestamp DESC;

-- Get logs by component
SELECT timestamp, level, operation, message
FROM audit_logs
WHERE component = 'AIInterviewer'
ORDER BY timestamp DESC
LIMIT 100;

-- Get error summary
SELECT component, operation, COUNT(*) as error_count
FROM audit_logs
WHERE level = 'ERROR'
  AND timestamp > NOW() - INTERVAL '1 day'
GROUP BY component, operation
ORDER BY error_count DESC;
```

### From Log Files

```bash
# View recent logs
tail -f logs/interview_platform.log

# Search for errors
grep '"level": "ERROR"' logs/interview_platform.log

# Search by session
grep '"session_id": "session-123"' logs/interview_platform.log

# Pretty print JSON logs
cat logs/interview_platform.log | jq '.'
```

## Troubleshooting

### Logs Not Appearing in Database

1. Check database connection:
   ```python
   is_healthy = data_store.health_check()
   ```

2. Verify data store is set:
   ```python
   logger.set_data_store(data_store)
   ```

3. Check database_output configuration:
   ```yaml
   logging:
     database_output: true
   ```

### Log Files Not Rotating

1. Check file size configuration:
   ```yaml
   logging:
     max_file_size_mb: 10
     backup_count: 5
   ```

2. Verify logs directory permissions:
   ```bash
   ls -la logs/
   ```

### Performance Issues

If logging impacts performance:

1. Reduce log level:
   ```yaml
   logging:
     level: "WARNING"  # Only warnings and errors
   ```

2. Disable database logging for high-frequency operations:
   ```yaml
   logging:
     database_output: false
   ```

3. Increase file rotation size:
   ```yaml
   logging:
     max_file_size_mb: 50
   ```

## Examples

See `test_logging.py` and `test_logging_integration.py` for complete examples.
