"""
Logging manager with multiple handlers for comprehensive system logging.

This module provides the LoggingManager class that handles logging to console,
rotating files, and database with structured JSON format.
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Dict, Any

from src.config import LoggingConfig
from src.models import LogEntry


class DatabaseLogHandler(logging.Handler):
    """
    Custom logging handler that writes logs to database.
    
    This handler stores log entries in the audit_logs table for
    querying and analysis.
    """

    def __init__(self, data_store=None):
        """
        Initialize database log handler.
        
        Args:
            data_store: IDataStore instance for database operations
        """
        super().__init__()
        self.data_store = data_store

    def set_data_store(self, data_store):
        """
        Set the data store instance.
        
        Args:
            data_store: IDataStore instance
        """
        self.data_store = data_store

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to database.
        
        Args:
            record: Log record to emit
        """
        if not self.data_store:
            return

        try:
            # Extract session_id and user_id from record if available
            session_id = getattr(record, "session_id", None)
            user_id = getattr(record, "user_id", None)
            component = getattr(record, "component", record.name)
            operation = getattr(record, "operation", "")
            metadata = getattr(record, "metadata", {})

            # Get stack trace if exception info is available
            stack_trace = None
            if record.exc_info:
                stack_trace = "".join(traceback.format_exception(*record.exc_info))

            # Create log entry
            log_entry = LogEntry(
                timestamp=datetime.fromtimestamp(record.created),
                level=record.levelname,
                component=component,
                operation=operation,
                message=record.getMessage(),
                session_id=session_id,
                user_id=user_id,
                metadata=metadata,
                stack_trace=stack_trace,
            )

            # Save to database
            self.data_store.save_audit_log(log_entry)

        except Exception:
            # Silently fail to avoid logging errors causing application failures
            self.handleError(record)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.
    
    This formatter creates machine-readable logs with consistent structure
    for log aggregation and analysis.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON-formatted log string
        """
        # Build base log structure
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "component": getattr(record, "component", record.name),
            "operation": getattr(record, "operation", ""),
            "message": record.getMessage(),
        }

        # Add optional fields if present
        if hasattr(record, "session_id") and record.session_id:
            log_data["session_id"] = record.session_id

        if hasattr(record, "user_id") and record.user_id:
            log_data["user_id"] = record.user_id

        if hasattr(record, "metadata") and record.metadata:
            log_data["metadata"] = record.metadata

        # Add exception info if present
        if record.exc_info:
            log_data["stack_trace"] = "".join(
                traceback.format_exception(*record.exc_info)
            )

        return json.dumps(log_data)


class LoggingManager:
    """
    Comprehensive logging manager with multiple handlers.
    
    Features:
    - Console output for real-time monitoring
    - Rotating file handler with size/time limits
    - Database handler for audit logs
    - Structured JSON logging format
    - Configurable log levels
    - Context-aware logging with session_id
    
    Attributes:
        logger: Root logger instance
        config: Logging configuration
        db_handler: Database log handler
    """

    def __init__(self, config: LoggingConfig, data_store=None):
        """
        Initialize logging manager with configuration.
        
        Args:
            config: LoggingConfig with logging settings
            data_store: Optional IDataStore instance for database logging
        """
        self.config = config
        self.logger = logging.getLogger("interview_platform")
        self.logger.setLevel(getattr(logging, config.level))
        self.logger.propagate = False

        # Clear any existing handlers
        self.logger.handlers.clear()

        # Create handlers based on configuration
        if config.console_output:
            self._add_console_handler()

        if config.file_output:
            self._add_file_handler()

        self.db_handler = None
        if config.database_output:
            self.db_handler = self._add_database_handler(data_store)

    def _add_console_handler(self) -> None:
        """Add console handler for real-time output."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.config.level))

        if self.config.format == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            # Standard text format
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def _add_file_handler(self) -> None:
        """Add rotating file handler with size/time limits."""
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create rotating file handler
        log_file = log_dir / "interview_platform.log"
        max_bytes = self.config.max_file_size_mb * 1024 * 1024  # Convert MB to bytes

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=self.config.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, self.config.level))

        if self.config.format == "json":
            file_handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _add_database_handler(self, data_store=None) -> DatabaseLogHandler:
        """
        Add database handler for audit logs.
        
        Args:
            data_store: Optional IDataStore instance
            
        Returns:
            DatabaseLogHandler instance
        """
        db_handler = DatabaseLogHandler(data_store)
        db_handler.setLevel(getattr(logging, self.config.level))
        self.logger.addHandler(db_handler)
        return db_handler

    def set_data_store(self, data_store) -> None:
        """
        Set data store for database logging.
        
        Args:
            data_store: IDataStore instance
        """
        if self.db_handler:
            self.db_handler.set_data_store(data_store)

    def log_operation(
        self,
        level: str,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
    ) -> None:
        """
        Log an operation with structured context.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            component: Component name generating the log
            operation: Operation being performed
            message: Log message
            session_id: Optional session identifier
            user_id: Optional user identifier
            metadata: Optional additional metadata
            exc_info: Optional exception information
        """
        log_level = getattr(logging, level.upper(), logging.INFO)

        # Create log record with extra context
        extra = {
            "component": component,
            "operation": operation,
            "session_id": session_id,
            "user_id": user_id,
            "metadata": metadata or {},
        }

        self.logger.log(
            log_level, message, extra=extra, exc_info=exc_info if exc_info else None
        )

    def log_error(
        self,
        component: str,
        operation: str,
        error: Exception,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log an error with full stack trace and context.
        
        Args:
            component: Component name where error occurred
            operation: Operation that failed
            error: Exception instance
            session_id: Optional session identifier
            user_id: Optional user identifier
            context: Optional additional context
        """
        self.log_operation(
            level="ERROR",
            component=component,
            operation=operation,
            message=f"Error: {str(error)}",
            session_id=session_id,
            user_id=user_id,
            metadata=context or {},
            exc_info=error,
        )

    def log_api_call(
        self,
        provider: str,
        endpoint: str,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        duration_ms: float,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Log an API call with request/response details and timing.
        
        Args:
            provider: API provider name
            endpoint: API endpoint
            request_data: Request data (sanitized)
            response_data: Response data (sanitized)
            duration_ms: Request duration in milliseconds
            session_id: Optional session identifier
            user_id: Optional user identifier
        """
        metadata = {
            "provider": provider,
            "endpoint": endpoint,
            "request_data": request_data,
            "response_data": response_data,
            "duration_ms": duration_ms,
        }

        self.log_operation(
            level="INFO",
            component="APIClient",
            operation="api_call",
            message=f"API call to {provider}/{endpoint} completed in {duration_ms:.2f}ms",
            session_id=session_id,
            user_id=user_id,
            metadata=metadata,
        )

    def debug(
        self,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log debug message."""
        self.log_operation(
            level="DEBUG",
            component=component,
            operation=operation,
            message=message,
            session_id=session_id,
            metadata=metadata,
        )

    def info(
        self,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log info message."""
        self.log_operation(
            level="INFO",
            component=component,
            operation=operation,
            message=message,
            session_id=session_id,
            metadata=metadata,
        )

    def warning(
        self,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log warning message."""
        self.log_operation(
            level="WARNING",
            component=component,
            operation=operation,
            message=message,
            session_id=session_id,
            metadata=metadata,
        )

    def error(
        self,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
    ) -> None:
        """Log error message."""
        self.log_operation(
            level="ERROR",
            component=component,
            operation=operation,
            message=message,
            session_id=session_id,
            metadata=metadata,
            exc_info=exc_info,
        )

    def critical(
        self,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exc_info: Optional[Exception] = None,
    ) -> None:
        """Log critical message."""
        self.log_operation(
            level="CRITICAL",
            component=component,
            operation=operation,
            message=message,
            session_id=session_id,
            metadata=metadata,
            exc_info=exc_info,
        )
