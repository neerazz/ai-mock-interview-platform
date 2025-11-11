"""
Custom exception classes for the AI Mock Interview Platform.

This module defines all custom exceptions used throughout the application
for specific error handling scenarios.
"""


class InterviewPlatformError(Exception):
    """Base exception for all platform errors."""
    pass


class ConfigurationError(InterviewPlatformError):
    """Raised when configuration is invalid or missing."""
    pass


class CommunicationError(InterviewPlatformError):
    """Raised when communication mode fails."""
    pass


class AIProviderError(InterviewPlatformError):
    """Raised when AI provider encounters an error."""
    pass


class DataStoreError(InterviewPlatformError):
    """Raised when database operations fail."""
    pass


class FileStorageError(InterviewPlatformError):
    """Raised when file storage operations fail."""
    pass


class ValidationError(InterviewPlatformError):
    """Raised when input validation fails."""
    pass
