# Logging System

The platform includes a comprehensive logging system for debugging, monitoring, and audit trails.

## Overview

The logging system provides:

- Multiple output destinations (console, file, database)
- Structured JSON format
- Context-aware logging
- Error tracking with stack traces

## Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors requiring immediate attention

## Log Destinations

### Console Logging

Human-readable format for development:

```
2024-01-15 10:30:45 [INFO] session_manager: Session created (session_id=abc123)
```

### File Logging

Rotating file logs in `logs/interview_platform.log`:

- Max size: 10MB per file
- Keeps 5 backup files
- JSON format for parsing

### Database Logging

Stored in `audit_logs` table for querying:

```sql
SELECT * FROM audit_logs 
WHERE session_id = 'abc123' 
ORDER BY timestamp DESC;
```

## Structured Logging

All logs include:

- Timestamp
- Level
- Component
- Operation
- Message
- Session ID (when available)
- User ID (when available)
- Metadata (custom fields)

Example JSON log:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "component": "session_manager",
  "operation": "create_session",
  "message": "Session created successfully",
  "session_id": "abc123",
  "metadata": {
    "enabled_modes": ["text", "whiteboard"],
    "ai_provider": "openai"
  }
}
```

## Usage

```python
# Log operation
logger.log_operation(
    level="INFO",
    component="session_manager",
    operation="create_session",
    message="Session created successfully",
    session_id=session.id,
    metadata={"enabled_modes": config.enabled_modes}
)

# Log error
try:
    result = risky_operation()
except Exception as e:
    logger.log_error(
        component="session_manager",
        operation="create_session",
        error=e,
        session_id=session.id
    )
```

## Configuration

Configure logging in `config.yaml`:

```yaml
logging:
  level: INFO
  console:
    enabled: true
    format: human
  file:
    enabled: true
    path: logs/interview_platform.log
    max_bytes: 10485760  # 10MB
    backup_count: 5
  database:
    enabled: true
    table: audit_logs
```

## Querying Logs

### From Database

```sql
-- Recent errors
SELECT * FROM audit_logs 
WHERE level = 'ERROR' 
ORDER BY timestamp DESC 
LIMIT 10;

-- Session activity
SELECT * FROM audit_logs 
WHERE session_id = 'abc123' 
ORDER BY timestamp;

-- Component errors
SELECT component, COUNT(*) as error_count
FROM audit_logs 
WHERE level = 'ERROR' 
GROUP BY component;
```

### From Files

```bash
# View recent logs
tail -f logs/interview_platform.log

# Search for errors
grep "ERROR" logs/interview_platform.log

# Parse JSON logs
cat logs/interview_platform.log | jq '.level == "ERROR"'
```

## Related Features

- [Token Tracking](token-tracking.md)
- [Architecture](../architecture.md)
