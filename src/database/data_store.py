"""
Database connection and data store implementation.

This module provides the IDataStore interface and PostgresDataStore implementation
for database operations with connection pooling, health checks, and retry logic.
"""

import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any
import psycopg2
from psycopg2 import pool, OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor

from src.models import (
    Session,
    Message,
    EvaluationReport,
    MediaFile,
    SessionSummary,
    TokenUsage,
    LogEntry,
    ResumeData,
)
from src.exceptions import DataStoreError


class IDataStore(ABC):
    """
    Abstract interface for data storage operations.
    
    This interface enables easy migration from local PostgreSQL to cloud databases
    by providing a consistent API for all data operations.
    """

    @abstractmethod
    def initialize_schema(self) -> None:
        """Initialize database schema if it doesn't exist."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check database health and connectivity.
        
        Returns:
            True if database is healthy, False otherwise
        """
        pass

    @abstractmethod
    def save_session(self, session: Session) -> None:
        """
        Save or update a session.
        
        Args:
            session: Session object to save
        """
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session object if found, None otherwise
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def save_conversation(self, session_id: str, message: Message) -> None:
        """
        Save a conversation message.
        
        Args:
            session_id: Session identifier
            message: Message object to save
        """
        pass

    @abstractmethod
    def get_conversation_history(self, session_id: str) -> List[Message]:
        """
        Retrieve all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages ordered by timestamp
        """
        pass

    @abstractmethod
    def save_evaluation(self, evaluation: EvaluationReport) -> None:
        """
        Save an evaluation report.
        
        Args:
            evaluation: EvaluationReport object to save
        """
        pass

    @abstractmethod
    def get_evaluation(self, session_id: str) -> Optional[EvaluationReport]:
        """
        Retrieve evaluation for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            EvaluationReport if found, None otherwise
        """
        pass

    @abstractmethod
    def save_media_reference(self, session_id: str, media: MediaFile) -> None:
        """
        Save media file reference.
        
        Args:
            session_id: Session identifier
            media: MediaFile object to save
        """
        pass

    @abstractmethod
    def get_media_files(self, session_id: str) -> List[MediaFile]:
        """
        Retrieve all media files for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of media file references
        """
        pass

    @abstractmethod
    def save_resume(self, resume_data: ResumeData) -> None:
        """
        Save resume data.
        
        Args:
            resume_data: ResumeData object to save
        """
        pass

    @abstractmethod
    def get_resume(self, user_id: str) -> Optional[ResumeData]:
        """
        Retrieve resume data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            ResumeData if found, None otherwise
        """
        pass

    @abstractmethod
    def save_token_usage(self, session_id: str, token_usage: TokenUsage) -> None:
        """
        Save token usage record.
        
        Args:
            session_id: Session identifier
            token_usage: TokenUsage object to save
        """
        pass

    @abstractmethod
    def get_token_usage(self, session_id: str) -> List[TokenUsage]:
        """
        Retrieve all token usage records for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of token usage records
        """
        pass

    @abstractmethod
    def save_audit_log(self, log_entry: LogEntry) -> None:
        """
        Save audit log entry.
        
        Args:
            log_entry: LogEntry object to save
        """
        pass


class PostgresDataStore(IDataStore):
    """
    PostgreSQL implementation of data store with connection pooling and retry logic.
    
    Features:
    - Connection pooling for efficient resource usage
    - Health check functionality
    - Retry logic with exponential backoff for transient failures
    - Parameterized queries for SQL injection prevention
    """

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
        min_connections: int = 1,
        max_connections: int = 10,
        logger=None,
    ):
        """
        Initialize PostgreSQL data store with connection pooling.
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
            min_connections: Minimum connections in pool
            max_connections: Maximum connections in pool
            logger: Optional LoggingManager instance
        """
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
        }
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool: Optional[pool.SimpleConnectionPool] = None
        self.logger = logger
        self._initialize_pool()

    def _initialize_pool(self) -> None:
        """Initialize connection pool with retry logic."""
        max_retries = 3
        retry_delay = 1

        if self.logger:
            self.logger.info(
                component="PostgresDataStore",
                operation="initialize_pool",
                message="Initializing database connection pool",
                metadata={
                    "host": self.connection_params["host"],
                    "database": self.connection_params["database"],
                    "min_connections": self.min_connections,
                    "max_connections": self.max_connections,
                },
            )

        for attempt in range(max_retries):
            try:
                self.pool = pool.SimpleConnectionPool(
                    self.min_connections,
                    self.max_connections,
                    **self.connection_params,
                )
                if self.logger:
                    self.logger.info(
                        component="PostgresDataStore",
                        operation="initialize_pool",
                        message="Database connection pool initialized successfully",
                    )
                return
            except (OperationalError, InterfaceError) as e:
                if self.logger:
                    self.logger.warning(
                        component="PostgresDataStore",
                        operation="initialize_pool",
                        message=f"Connection pool initialization attempt {attempt + 1} failed",
                        metadata={"attempt": attempt + 1, "error": str(e)},
                    )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    error_msg = f"Failed to initialize database connection pool after {max_retries} attempts: {e}"
                    if self.logger:
                        self.logger.error(
                            component="PostgresDataStore",
                            operation="initialize_pool",
                            message=error_msg,
                            exc_info=e,
                        )
                    raise DataStoreError(error_msg)

    @contextmanager
    def _get_connection(self):
        """
        Get database connection from pool with retry logic.
        
        Yields:
            Database connection
            
        Raises:
            DataStoreError: If connection cannot be obtained after retries
        """
        max_retries = 3
        retry_delay = 1
        conn = None

        for attempt in range(max_retries):
            try:
                conn = self.pool.getconn()
                yield conn
                conn.commit()
                if self.logger:
                    self.logger.debug(
                        component="PostgresDataStore",
                        operation="get_connection",
                        message="Database operation completed successfully",
                    )
                return
            except (OperationalError, InterfaceError) as e:
                if conn:
                    conn.rollback()
                if self.logger:
                    self.logger.warning(
                        component="PostgresDataStore",
                        operation="get_connection",
                        message=f"Database connection attempt {attempt + 1} failed",
                        metadata={"attempt": attempt + 1, "error": str(e)},
                    )
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    error_msg = f"Database operation failed after {max_retries} attempts: {e}"
                    if self.logger:
                        self.logger.error(
                            component="PostgresDataStore",
                            operation="get_connection",
                            message=error_msg,
                            exc_info=e,
                        )
                    raise DataStoreError(error_msg)
            except Exception as e:
                if conn:
                    conn.rollback()
                if self.logger:
                    self.logger.error(
                        component="PostgresDataStore",
                        operation="get_connection",
                        message=f"Database operation failed: {str(e)}",
                        exc_info=e,
                    )
                raise DataStoreError(f"Database operation failed: {str(e)}")
            finally:
                if conn:
                    self.pool.putconn(conn)

    def initialize_schema(self) -> None:
        """Initialize database schema if it doesn't exist."""
        # Schema initialization is handled by init.sql in Docker setup
        # This method is a placeholder for future migration support
        pass

    def health_check(self) -> bool:
        """
        Check database health and connectivity.
        
        Returns:
            True if database is healthy, False otherwise
        """
        try:
            if self.logger:
                self.logger.debug(
                    component="PostgresDataStore",
                    operation="health_check",
                    message="Performing database health check",
                )
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    is_healthy = result is not None and result[0] == 1
                    if self.logger:
                        self.logger.info(
                            component="PostgresDataStore",
                            operation="health_check",
                            message=f"Database health check {'passed' if is_healthy else 'failed'}",
                        )
                    return is_healthy
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="PostgresDataStore",
                    operation="health_check",
                    message="Database health check failed",
                    exc_info=e,
                )
            return False

    def save_session(self, session: Session) -> None:
        """Save or update a session."""
        if self.logger:
            self.logger.info(
                component="PostgresDataStore",
                operation="save_session",
                message=f"Saving session {session.id}",
                session_id=session.id,
                user_id=session.user_id,
                metadata={"status": session.status.value},
            )
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO sessions (
                            id, user_id, created_at, ended_at, status,
                            enabled_modes, ai_provider, ai_model, metadata
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            ended_at = EXCLUDED.ended_at,
                            status = EXCLUDED.status,
                            metadata = EXCLUDED.metadata
                        """,
                        (
                            session.id,
                            session.user_id,
                            session.created_at,
                            session.ended_at,
                            session.status.value,
                            psycopg2.extras.Json(
                                [mode.value for mode in session.config.enabled_modes]
                            ),
                            session.config.ai_provider,
                            session.config.ai_model,
                            psycopg2.extras.Json(session.metadata),
                        ),
                    )
            if self.logger:
                self.logger.info(
                    component="PostgresDataStore",
                    operation="save_session",
                    message=f"Session {session.id} saved successfully",
                    session_id=session.id,
                )
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="PostgresDataStore",
                    operation="save_session",
                    message=f"Failed to save session {session.id}",
                    session_id=session.id,
                    exc_info=e,
                )
            raise

    def get_session(self, session_id: str) -> Optional[Session]:
        """Retrieve a session by ID."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT id, user_id, created_at, ended_at, status,
                           enabled_modes, ai_provider, ai_model, metadata
                    FROM sessions
                    WHERE id = %s
                    """,
                    (session_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None

                from src.models import SessionConfig, SessionStatus, CommunicationMode

                config = SessionConfig(
                    enabled_modes=[
                        CommunicationMode(mode) for mode in row["enabled_modes"]
                    ],
                    ai_provider=row["ai_provider"],
                    ai_model=row["ai_model"],
                )

                return Session(
                    id=row["id"],
                    user_id=row["user_id"],
                    created_at=row["created_at"],
                    ended_at=row["ended_at"],
                    status=SessionStatus(row["status"]),
                    config=config,
                    metadata=row["metadata"] or {},
                )

    def list_sessions(
        self, user_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[SessionSummary]:
        """List sessions with pagination."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if user_id:
                    cur.execute(
                        """
                        SELECT s.id, s.user_id, s.created_at, s.ended_at, s.status,
                               e.overall_score,
                               EXTRACT(EPOCH FROM (s.ended_at - s.created_at))/60 as duration_minutes
                        FROM sessions s
                        LEFT JOIN evaluations e ON s.id = e.session_id
                        WHERE s.user_id = %s
                        ORDER BY s.created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (user_id, limit, offset),
                    )
                else:
                    cur.execute(
                        """
                        SELECT s.id, s.user_id, s.created_at, s.ended_at, s.status,
                               e.overall_score,
                               EXTRACT(EPOCH FROM (s.ended_at - s.created_at))/60 as duration_minutes
                        FROM sessions s
                        LEFT JOIN evaluations e ON s.id = e.session_id
                        ORDER BY s.created_at DESC
                        LIMIT %s OFFSET %s
                        """,
                        (limit, offset),
                    )

                rows = cur.fetchall()
                from src.models import SessionStatus

                return [
                    SessionSummary(
                        id=row["id"],
                        user_id=row["user_id"],
                        created_at=row["created_at"],
                        duration_minutes=int(row["duration_minutes"])
                        if row["duration_minutes"]
                        else None,
                        overall_score=float(row["overall_score"])
                        if row["overall_score"]
                        else None,
                        status=SessionStatus(row["status"]),
                    )
                    for row in rows
                ]

    def save_conversation(self, session_id: str, message: Message) -> None:
        """Save a conversation message."""
        if self.logger:
            self.logger.debug(
                component="PostgresDataStore",
                operation="save_conversation",
                message=f"Saving conversation message for session {session_id}",
                session_id=session_id,
                metadata={"role": message.role, "content_length": len(message.content)},
            )
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO conversations (session_id, timestamp, role, content, metadata)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            session_id,
                            message.timestamp,
                            message.role,
                            message.content,
                            psycopg2.extras.Json(message.metadata),
                        ),
                    )
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="PostgresDataStore",
                    operation="save_conversation",
                    message=f"Failed to save conversation message for session {session_id}",
                    session_id=session_id,
                    exc_info=e,
                )
            raise

    def get_conversation_history(self, session_id: str) -> List[Message]:
        """Retrieve all messages for a session."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT role, content, timestamp, metadata
                    FROM conversations
                    WHERE session_id = %s
                    ORDER BY timestamp ASC
                    """,
                    (session_id,),
                )
                rows = cur.fetchall()
                return [
                    Message(
                        role=row["role"],
                        content=row["content"],
                        timestamp=row["timestamp"],
                        metadata=row["metadata"] or {},
                    )
                    for row in rows
                ]

    def save_evaluation(self, evaluation: EvaluationReport) -> None:
        """Save an evaluation report."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Convert evaluation data to JSON-serializable format
                competency_scores_json = {
                    key: {
                        "score": score.score,
                        "confidence_level": score.confidence_level,
                        "evidence": score.evidence,
                    }
                    for key, score in evaluation.competency_scores.items()
                }

                feedback_json = {
                    "went_well": [
                        {
                            "category": f.category,
                            "description": f.description,
                            "evidence": f.evidence,
                        }
                        for f in evaluation.went_well
                    ],
                    "went_okay": [
                        {
                            "category": f.category,
                            "description": f.description,
                            "evidence": f.evidence,
                        }
                        for f in evaluation.went_okay
                    ],
                    "needs_improvement": [
                        {
                            "category": f.category,
                            "description": f.description,
                            "evidence": f.evidence,
                        }
                        for f in evaluation.needs_improvement
                    ],
                }

                improvement_plan_json = {
                    "priority_areas": evaluation.improvement_plan.priority_areas,
                    "concrete_steps": [
                        {
                            "step_number": step.step_number,
                            "description": step.description,
                            "resources": step.resources,
                        }
                        for step in evaluation.improvement_plan.concrete_steps
                    ],
                    "resources": evaluation.improvement_plan.resources,
                }

                communication_analysis_json = {
                    "audio_quality": evaluation.communication_mode_analysis.audio_quality,
                    "video_presence": evaluation.communication_mode_analysis.video_presence,
                    "whiteboard_usage": evaluation.communication_mode_analysis.whiteboard_usage,
                    "screen_share_usage": evaluation.communication_mode_analysis.screen_share_usage,
                    "overall_communication": evaluation.communication_mode_analysis.overall_communication,
                }

                cur.execute(
                    """
                    INSERT INTO evaluations (
                        session_id, overall_score, competency_scores,
                        feedback, improvement_plan, communication_analysis, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (session_id) DO UPDATE SET
                        overall_score = EXCLUDED.overall_score,
                        competency_scores = EXCLUDED.competency_scores,
                        feedback = EXCLUDED.feedback,
                        improvement_plan = EXCLUDED.improvement_plan,
                        communication_analysis = EXCLUDED.communication_analysis,
                        created_at = EXCLUDED.created_at
                    """,
                    (
                        evaluation.session_id,
                        evaluation.overall_score,
                        psycopg2.extras.Json(competency_scores_json),
                        psycopg2.extras.Json(feedback_json),
                        psycopg2.extras.Json(improvement_plan_json),
                        psycopg2.extras.Json(communication_analysis_json),
                        evaluation.created_at,
                    ),
                )

    def get_evaluation(self, session_id: str) -> Optional[EvaluationReport]:
        """Retrieve evaluation for a session."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT session_id, overall_score, competency_scores,
                           feedback, improvement_plan, communication_analysis, created_at
                    FROM evaluations
                    WHERE session_id = %s
                    """,
                    (session_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None

                from src.models import (
                    CompetencyScore,
                    Feedback,
                    ActionItem,
                    ImprovementPlan,
                    ModeAnalysis,
                )

                # Reconstruct competency scores
                competency_scores = {
                    key: CompetencyScore(
                        score=data["score"],
                        confidence_level=data["confidence_level"],
                        evidence=data["evidence"],
                    )
                    for key, data in row["competency_scores"].items()
                }

                # Reconstruct feedback
                feedback_data = row["feedback"]
                went_well = [
                    Feedback(
                        category=f["category"],
                        description=f["description"],
                        evidence=f["evidence"],
                    )
                    for f in feedback_data["went_well"]
                ]
                went_okay = [
                    Feedback(
                        category=f["category"],
                        description=f["description"],
                        evidence=f["evidence"],
                    )
                    for f in feedback_data["went_okay"]
                ]
                needs_improvement = [
                    Feedback(
                        category=f["category"],
                        description=f["description"],
                        evidence=f["evidence"],
                    )
                    for f in feedback_data["needs_improvement"]
                ]

                # Reconstruct improvement plan
                plan_data = row["improvement_plan"]
                improvement_plan = ImprovementPlan(
                    priority_areas=plan_data["priority_areas"],
                    concrete_steps=[
                        ActionItem(
                            step_number=step["step_number"],
                            description=step["description"],
                            resources=step["resources"],
                        )
                        for step in plan_data["concrete_steps"]
                    ],
                    resources=plan_data["resources"],
                )

                # Reconstruct communication analysis
                comm_data = row["communication_analysis"]
                communication_analysis = ModeAnalysis(
                    audio_quality=comm_data.get("audio_quality"),
                    video_presence=comm_data.get("video_presence"),
                    whiteboard_usage=comm_data.get("whiteboard_usage"),
                    screen_share_usage=comm_data.get("screen_share_usage"),
                    overall_communication=comm_data.get("overall_communication", ""),
                )

                return EvaluationReport(
                    session_id=row["session_id"],
                    overall_score=float(row["overall_score"]),
                    competency_scores=competency_scores,
                    went_well=went_well,
                    went_okay=went_okay,
                    needs_improvement=needs_improvement,
                    improvement_plan=improvement_plan,
                    communication_mode_analysis=communication_analysis,
                    created_at=row["created_at"],
                )

    def save_media_reference(self, session_id: str, media: MediaFile) -> None:
        """Save media file reference."""
        if self.logger:
            self.logger.info(
                component="PostgresDataStore",
                operation="save_media_reference",
                message=f"Saving media file reference for session {session_id}",
                session_id=session_id,
                metadata={
                    "file_type": media.file_type,
                    "file_path": media.file_path,
                    "file_size_bytes": media.file_size_bytes,
                },
            )
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO media_files (
                            session_id, file_type, file_path, file_size_bytes, timestamp, metadata
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            session_id,
                            media.file_type,
                            media.file_path,
                            media.file_size_bytes,
                            media.timestamp,
                            psycopg2.extras.Json(media.metadata),
                        ),
                    )
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="PostgresDataStore",
                    operation="save_media_reference",
                    message=f"Failed to save media file reference for session {session_id}",
                    session_id=session_id,
                    exc_info=e,
                )
            raise

    def get_media_files(self, session_id: str) -> List[MediaFile]:
        """Retrieve all media files for a session."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT file_type, file_path, file_size_bytes, timestamp, metadata
                    FROM media_files
                    WHERE session_id = %s
                    ORDER BY timestamp ASC
                    """,
                    (session_id,),
                )
                rows = cur.fetchall()
                return [
                    MediaFile(
                        file_type=row["file_type"],
                        file_path=row["file_path"],
                        file_size_bytes=row["file_size_bytes"],
                        timestamp=row["timestamp"],
                        metadata=row["metadata"] or {},
                    )
                    for row in rows
                ]

    def save_resume(self, resume_data: ResumeData) -> None:
        """Save resume data."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Convert work experience and education to JSON
                work_experience_json = [
                    {
                        "company": exp.company,
                        "title": exp.title,
                        "duration": exp.duration,
                        "description": exp.description,
                    }
                    for exp in resume_data.work_experience
                ]

                education_json = [
                    {
                        "institution": edu.institution,
                        "degree": edu.degree,
                        "field": edu.field,
                        "year": edu.year,
                    }
                    for edu in resume_data.education
                ]

                cur.execute(
                    """
                    INSERT INTO resumes (
                        user_id, name, email, experience_level, years_of_experience,
                        domain_expertise, work_experience, education, skills, raw_text
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        experience_level = EXCLUDED.experience_level,
                        years_of_experience = EXCLUDED.years_of_experience,
                        domain_expertise = EXCLUDED.domain_expertise,
                        work_experience = EXCLUDED.work_experience,
                        education = EXCLUDED.education,
                        skills = EXCLUDED.skills,
                        raw_text = EXCLUDED.raw_text,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        resume_data.user_id,
                        resume_data.name,
                        resume_data.email,
                        resume_data.experience_level,
                        resume_data.years_of_experience,
                        psycopg2.extras.Json(resume_data.domain_expertise),
                        psycopg2.extras.Json(work_experience_json),
                        psycopg2.extras.Json(education_json),
                        psycopg2.extras.Json(resume_data.skills),
                        resume_data.raw_text,
                    ),
                )

    def get_resume(self, user_id: str) -> Optional[ResumeData]:
        """Retrieve resume data for a user."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT user_id, name, email, experience_level, years_of_experience,
                           domain_expertise, work_experience, education, skills, raw_text
                    FROM resumes
                    WHERE user_id = %s
                    """,
                    (user_id,),
                )
                row = cur.fetchone()
                if not row:
                    return None

                from src.models import WorkExperience, Education

                # Reconstruct work experience
                work_experience = [
                    WorkExperience(
                        company=exp["company"],
                        title=exp["title"],
                        duration=exp["duration"],
                        description=exp["description"],
                    )
                    for exp in row["work_experience"]
                ]

                # Reconstruct education
                education = [
                    Education(
                        institution=edu["institution"],
                        degree=edu["degree"],
                        field=edu["field"],
                        year=edu["year"],
                    )
                    for edu in row["education"]
                ]

                return ResumeData(
                    user_id=row["user_id"],
                    name=row["name"],
                    email=row["email"],
                    experience_level=row["experience_level"],
                    years_of_experience=row["years_of_experience"],
                    domain_expertise=row["domain_expertise"],
                    work_experience=work_experience,
                    education=education,
                    skills=row["skills"],
                    raw_text=row["raw_text"],
                )

    def save_token_usage(self, session_id: str, token_usage: TokenUsage) -> None:
        """Save token usage record."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO token_usage (
                        session_id, operation, provider, model,
                        input_tokens, output_tokens, total_tokens, estimated_cost
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        token_usage.operation,
                        token_usage.provider,
                        token_usage.model,
                        token_usage.input_tokens,
                        token_usage.output_tokens,
                        token_usage.total_tokens,
                        token_usage.estimated_cost,
                    ),
                )

    def get_token_usage(self, session_id: str) -> List[TokenUsage]:
        """Retrieve all token usage records for a session."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT operation, provider, model, input_tokens, output_tokens,
                           total_tokens, estimated_cost
                    FROM token_usage
                    WHERE session_id = %s
                    ORDER BY timestamp ASC
                    """,
                    (session_id,),
                )
                rows = cur.fetchall()
                return [
                    TokenUsage(
                        input_tokens=row["input_tokens"],
                        output_tokens=row["output_tokens"],
                        total_tokens=row["total_tokens"],
                        estimated_cost=float(row["estimated_cost"]),
                        provider=row["provider"],
                        model=row["model"],
                        operation=row["operation"],
                    )
                    for row in rows
                ]

    def save_audit_log(self, log_entry: LogEntry) -> None:
        """Save audit log entry."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_logs (
                        timestamp, level, component, operation, session_id,
                        user_id, message, stack_trace, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        log_entry.timestamp,
                        log_entry.level,
                        log_entry.component,
                        log_entry.operation,
                        log_entry.session_id,
                        log_entry.user_id,
                        log_entry.message,
                        log_entry.stack_trace,
                        psycopg2.extras.Json(log_entry.metadata),
                    ),
                )

    def close(self) -> None:
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
