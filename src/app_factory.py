"""
Application factory for dependency injection and component initialization.

This module provides the create_app function that wires up all dependencies
and creates instances of all components with proper dependency injection.
"""

from src.config import get_config
from src.database.data_store import PostgresDataStore
from src.storage.file_storage import FileStorage
from src.log_manager.logging_manager import LoggingManager
from src.ai.token_tracker import TokenTracker
from src.resume.resume_manager import ResumeManager
from src.communication.communication_manager import CommunicationManager
from src.ai.ai_interviewer import AIInterviewer
from src.evaluation.evaluation_manager import EvaluationManager
from src.session.session_manager import SessionManager


def create_app(config_path: str = "config.yaml"):
    """
    Factory function to wire up dependencies and create application components.
    
    Args:
        config_path: Path to configuration YAML file
        
    Returns:
        Dictionary with all initialized components
    """
    # Load configuration
    config = get_config(config_path)
    
    # Create infrastructure components
    data_store = PostgresDataStore(
        host=config.database.host,
        port=config.database.port,
        database=config.database.database,
        user=config.database.user,
        password=config.database.password,
        pool_size=config.database.pool_size,
        max_overflow=config.database.max_overflow,
    )
    
    file_storage = FileStorage(
        data_dir=config.storage.data_dir,
        logger=None  # Will be set after logger is created
    )
    
    logger = LoggingManager(
        data_store=data_store,
        log_level=config.logging.level,
        log_dir=config.storage.logs_dir,
        console_output=config.logging.console_output,
        file_output=config.logging.file_output,
        database_output=config.logging.database_output,
    )
    
    # Update file_storage with logger
    file_storage.logger = logger
    
    token_tracker = TokenTracker(
        data_store=data_store,
        logger=logger
    )
    
    # Create domain components
    resume_manager = ResumeManager(
        data_store=data_store,
        config=config,
        logger=logger
    )
    
    communication_manager = CommunicationManager(
        file_storage=file_storage,
        logger=logger
    )
    
    ai_interviewer = AIInterviewer(
        config=config,
        token_tracker=token_tracker,
        logger=logger
    )
    
    evaluation_manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        file_storage=file_storage,
        logger=logger
    )
    
    # Create session manager with all dependencies
    session_manager = SessionManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        evaluation_manager=evaluation_manager,
        communication_manager=communication_manager,
        logger=logger
    )
    
    return {
        "config": config,
        "data_store": data_store,
        "file_storage": file_storage,
        "logger": logger,
        "token_tracker": token_tracker,
        "resume_manager": resume_manager,
        "communication_manager": communication_manager,
        "ai_interviewer": ai_interviewer,
        "evaluation_manager": evaluation_manager,
        "session_manager": session_manager,
    }
