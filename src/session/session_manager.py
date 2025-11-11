"""
Session Manager for orchestrating interview session lifecycle.

This module provides the SessionManager class that coordinates between
AI Interviewer, Evaluation Manager, and Communication Manager to manage
the complete interview session lifecycle.
"""

import uuid
from datetime import datetime
from typing import Optional, List

from src.models import (
    Session,
    SessionConfig,
    SessionStatus,
    SessionSummary,
    EvaluationReport,
    Message,
)
from src.exceptions import InterviewPlatformError


class SessionManager:
    """
    Manages interview session lifecycle and coordinates between components.
    
    The SessionManager orchestrates the complete interview workflow including
    session creation, initialization, state management, and evaluation generation.
    It coordinates between the AI Interviewer, Evaluation Manager, Communication
    Manager, and Data Store.
    
    Attributes:
        data_store: IDataStore instance for persistence
        ai_interviewer: AIInterviewer instance for conducting interviews
        evaluation_manager: EvaluationManager instance for generating evaluations
        communication_manager: CommunicationManager instance for handling I/O modes
        logger: Optional LoggingManager instance
    """

    def __init__(
        self,
        data_store,
        ai_interviewer,
        evaluation_manager,
        communication_manager,
        logger=None,
    ):
        """
        Initialize Session Manager with injected dependencies.
        
        Args:
            data_store: IDataStore instance for data persistence
            ai_interviewer: AIInterviewer instance for conducting interviews
            evaluation_manager: EvaluationManager instance for evaluations
            communication_manager: CommunicationManager instance for I/O modes
            logger: Optional LoggingManager instance
        """
        self.data_store = data_store
        self.ai_interviewer = ai_interviewer
        self.evaluation_manager = evaluation_manager
        self.communication_manager = communication_manager
        self.logger = logger
        
        # Track active session
        self._active_session_id: Optional[str] = None

        if self.logger:
            self.logger.info(
                component="SessionManager",
                operation="__init__",
                message="Session Manager initialized",
            )

    def create_session(self, config: SessionConfig) -> Session:
        """
        Create a new interview session with unique identifier.
        
        Creates a new session with a unique UUID, initializes it with the
        provided configuration, and stores it in the database.
        
        Args:
            config: SessionConfig with enabled modes, AI provider, and resume data
            
        Returns:
            Created Session object
            
        Raises:
            InterviewPlatformError: If session creation fails
        """
        if self.logger:
            self.logger.info(
                component="SessionManager",
                operation="create_session",
                message="Creating new interview session",
                metadata={
                    "ai_provider": config.ai_provider,
                    "ai_model": config.ai_model,
                    "enabled_modes": [mode.value for mode in config.enabled_modes],
                    "has_resume": config.resume_data is not None,
                },
            )

        try:
            # Generate unique session identifier
            session_id = str(uuid.uuid4())
            
            # Determine user_id from resume or generate one
            user_id = config.resume_data.user_id if config.resume_data else f"user_{session_id[:8]}"

            # Create session object
            session = Session(
                id=session_id,
                user_id=user_id,
                created_at=datetime.now(),
                ended_at=None,
                status=SessionStatus.ACTIVE,
                config=config,
                metadata={},
            )

            # Store session in database
            self.data_store.save_session(session)

            if self.logger:
                self.logger.info(
                    component="SessionManager",
                    operation="create_session",
                    message=f"Session {session_id} created successfully",
                    session_id=session_id,
                    user_id=user_id,
                )

            return session

        except Exception as e:
            error_msg = f"Failed to create session: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="create_session",
                    message=error_msg,
                    exc_info=e,
                )
            raise InterviewPlatformError(error_msg) from e

    def start_session(self, session_id: str) -> None:
        """
        Start an interview session and activate it.
        
        Initializes the AI Interviewer with system design context and resume data,
        enables configured communication modes, and marks the session as active.
        
        Args:
            session_id: Session identifier
            
        Raises:
            InterviewPlatformError: If session start fails
        """
        if self.logger:
            self.logger.info(
                component="SessionManager",
                operation="start_session",
                message=f"Starting session {session_id}",
                session_id=session_id,
            )

        try:
            # Retrieve session from database
            session = self.data_store.get_session(session_id)
            if not session:
                raise InterviewPlatformError(f"Session {session_id} not found")

            # Check if session is already active
            if session.status != SessionStatus.ACTIVE:
                raise InterviewPlatformError(
                    f"Cannot start session {session_id} with status {session.status.value}"
                )

            # Initialize AI Interviewer with session context and resume data
            self.ai_interviewer.initialize(
                session_id=session_id,
                resume_data=session.config.resume_data,
            )

            # Enable configured communication modes
            for mode in session.config.enabled_modes:
                self.communication_manager.enable_mode(mode)

            # Set as active session
            self._active_session_id = session_id

            # Start the interview (generate opening question)
            opening_response = self.ai_interviewer.start_interview()

            # Save opening message to conversation history
            opening_message = Message(
                role="interviewer",
                content=opening_response.content,
                timestamp=datetime.now(),
                metadata={},
            )
            self.data_store.save_conversation(session_id, opening_message)

            if self.logger:
                self.logger.info(
                    component="SessionManager",
                    operation="start_session",
                    message=f"Session {session_id} started successfully",
                    session_id=session_id,
                    metadata={
                        "enabled_modes": [mode.value for mode in session.config.enabled_modes],
                    },
                )

        except Exception as e:
            error_msg = f"Failed to start session {session_id}: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="start_session",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e,
                )
            raise InterviewPlatformError(error_msg) from e

    def end_session(self, session_id: str) -> EvaluationReport:
        """
        End an interview session and generate evaluation.
        
        Stops accepting new inputs, marks the session as completed,
        triggers evaluation generation, and saves the complete session recording.
        
        Args:
            session_id: Session identifier
            
        Returns:
            EvaluationReport for the completed session
            
        Raises:
            InterviewPlatformError: If session end fails
        """
        if self.logger:
            self.logger.info(
                component="SessionManager",
                operation="end_session",
                message=f"Ending session {session_id}",
                session_id=session_id,
            )

        try:
            # Retrieve session from database
            session = self.data_store.get_session(session_id)
            if not session:
                raise InterviewPlatformError(f"Session {session_id} not found")

            # Check if session is active
            if session.status != SessionStatus.ACTIVE:
                raise InterviewPlatformError(
                    f"Cannot end session {session_id} with status {session.status.value}"
                )

            # Mark session as completed
            session.status = SessionStatus.COMPLETED
            session.ended_at = datetime.now()
            self.data_store.save_session(session)

            # Clear active session
            if self._active_session_id == session_id:
                self._active_session_id = None

            # Disable all communication modes
            for mode in self.communication_manager.get_enabled_modes():
                self.communication_manager.disable_mode(mode)

            # Generate evaluation report
            evaluation = self.evaluation_manager.generate_evaluation(session_id)

            if self.logger:
                self.logger.info(
                    component="SessionManager",
                    operation="end_session",
                    message=f"Session {session_id} ended successfully",
                    session_id=session_id,
                    metadata={
                        "overall_score": evaluation.overall_score,
                        "duration_minutes": (
                            (session.ended_at - session.created_at).total_seconds() / 60
                            if session.ended_at
                            else 0
                        ),
                    },
                )

            return evaluation

        except Exception as e:
            error_msg = f"Failed to end session {session_id}: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="end_session",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e,
                )
            raise InterviewPlatformError(error_msg) from e

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object if found, None otherwise
        """
        if self.logger:
            self.logger.debug(
                component="SessionManager",
                operation="get_session",
                message=f"Retrieving session {session_id}",
                session_id=session_id,
            )

        try:
            session = self.data_store.get_session(session_id)
            return session

        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="get_session",
                    message=f"Failed to retrieve session {session_id}",
                    session_id=session_id,
                    exc_info=e,
                )
            return None

    def list_sessions(
        self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[SessionSummary]:
        """
        List sessions with pagination.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of session summaries
        """
        if self.logger:
            self.logger.debug(
                component="SessionManager",
                operation="list_sessions",
                message="Listing sessions",
                metadata={
                    "user_id": user_id,
                    "limit": limit,
                    "offset": offset,
                },
            )

        try:
            sessions = self.data_store.list_sessions(
                user_id=user_id, limit=limit, offset=offset
            )

            if self.logger:
                self.logger.debug(
                    component="SessionManager",
                    operation="list_sessions",
                    message=f"Retrieved {len(sessions)} sessions",
                    metadata={"count": len(sessions)},
                )

            return sessions

        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="list_sessions",
                    message="Failed to list sessions",
                    exc_info=e,
                )
            return []

    def get_active_session(self) -> Optional[Session]:
        """
        Get the currently active session.
        
        Returns:
            Active Session object if one exists, None otherwise
        """
        if self._active_session_id:
            return self.get_session(self._active_session_id)
        return None

    def pause_session(self, session_id: str) -> None:
        """
        Pause an active session.
        
        Args:
            session_id: Session identifier
            
        Raises:
            InterviewPlatformError: If session pause fails
        """
        if self.logger:
            self.logger.info(
                component="SessionManager",
                operation="pause_session",
                message=f"Pausing session {session_id}",
                session_id=session_id,
            )

        try:
            # Retrieve session from database
            session = self.data_store.get_session(session_id)
            if not session:
                raise InterviewPlatformError(f"Session {session_id} not found")

            # Check if session is active
            if session.status != SessionStatus.ACTIVE:
                raise InterviewPlatformError(
                    f"Cannot pause session {session_id} with status {session.status.value}"
                )

            # Mark session as paused
            session.status = SessionStatus.PAUSED
            self.data_store.save_session(session)

            if self.logger:
                self.logger.info(
                    component="SessionManager",
                    operation="pause_session",
                    message=f"Session {session_id} paused successfully",
                    session_id=session_id,
                )

        except Exception as e:
            error_msg = f"Failed to pause session {session_id}: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="pause_session",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e,
                )
            raise InterviewPlatformError(error_msg) from e

    def resume_session(self, session_id: str) -> None:
        """
        Resume a paused session.
        
        Args:
            session_id: Session identifier
            
        Raises:
            InterviewPlatformError: If session resume fails
        """
        if self.logger:
            self.logger.info(
                component="SessionManager",
                operation="resume_session",
                message=f"Resuming session {session_id}",
                session_id=session_id,
            )

        try:
            # Retrieve session from database
            session = self.data_store.get_session(session_id)
            if not session:
                raise InterviewPlatformError(f"Session {session_id} not found")

            # Check if session is paused
            if session.status != SessionStatus.PAUSED:
                raise InterviewPlatformError(
                    f"Cannot resume session {session_id} with status {session.status.value}"
                )

            # Mark session as active
            session.status = SessionStatus.ACTIVE
            self.data_store.save_session(session)

            # Set as active session
            self._active_session_id = session_id

            if self.logger:
                self.logger.info(
                    component="SessionManager",
                    operation="resume_session",
                    message=f"Session {session_id} resumed successfully",
                    session_id=session_id,
                )

        except Exception as e:
            error_msg = f"Failed to resume session {session_id}: {str(e)}"
            if self.logger:
                self.logger.error(
                    component="SessionManager",
                    operation="resume_session",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e,
                )
            raise InterviewPlatformError(error_msg) from e
