"""
Tests for SessionManager.

This module contains tests for the SessionManager class to verify
session lifecycle management functionality.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
import uuid

from src.session.session_manager import SessionManager
from src.models import (
    Session,
    SessionConfig,
    SessionStatus,
    CommunicationMode,
    ResumeData,
    WorkExperience,
    Education,
    Message,
    InterviewResponse,
    TokenUsage,
    EvaluationReport,
    CompetencyScore,
    ImprovementPlan,
    ModeAnalysis,
)
from src.exceptions import InterviewPlatformError


@pytest.fixture
def mock_data_store():
    """Create a mock data store."""
    return Mock()


@pytest.fixture
def mock_ai_interviewer():
    """Create a mock AI interviewer."""
    return Mock()


@pytest.fixture
def mock_evaluation_manager():
    """Create a mock evaluation manager."""
    return Mock()


@pytest.fixture
def mock_communication_manager():
    """Create a mock communication manager."""
    mock = Mock()
    mock.get_enabled_modes.return_value = []
    return mock


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    return Mock()


@pytest.fixture
def session_manager(
    mock_data_store,
    mock_ai_interviewer,
    mock_evaluation_manager,
    mock_communication_manager,
    mock_logger,
):
    """Create a SessionManager instance with mocked dependencies."""
    return SessionManager(
        data_store=mock_data_store,
        ai_interviewer=mock_ai_interviewer,
        evaluation_manager=mock_evaluation_manager,
        communication_manager=mock_communication_manager,
        logger=mock_logger,
    )


@pytest.fixture
def sample_resume_data():
    """Create sample resume data."""
    return ResumeData(
        user_id="test_user_123",
        name="John Doe",
        email="john@example.com",
        experience_level="senior",
        years_of_experience=8,
        domain_expertise=["backend", "distributed-systems"],
        work_experience=[
            WorkExperience(
                company="Tech Corp",
                title="Senior Engineer",
                duration="2020-2024",
                description="Built scalable systems",
            )
        ],
        education=[
            Education(
                institution="University",
                degree="BS",
                field="Computer Science",
                year="2016",
            )
        ],
        skills=["Python", "Java", "AWS"],
        raw_text="Resume text...",
    )


@pytest.fixture
def sample_session_config(sample_resume_data):
    """Create sample session configuration."""
    return SessionConfig(
        enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
        ai_provider="openai",
        ai_model="gpt-4",
        resume_data=sample_resume_data,
        duration_minutes=45,
    )


def test_session_manager_initialization(session_manager):
    """Test SessionManager initialization."""
    assert session_manager.data_store is not None
    assert session_manager.ai_interviewer is not None
    assert session_manager.evaluation_manager is not None
    assert session_manager.communication_manager is not None
    assert session_manager._active_session_id is None


def test_create_session(session_manager, sample_session_config):
    """Test creating a new session."""
    # Act
    session = session_manager.create_session(sample_session_config)

    # Assert
    assert session is not None
    assert session.id is not None
    assert session.user_id == "test_user_123"
    assert session.status == SessionStatus.ACTIVE
    assert session.config == sample_session_config
    assert session.created_at is not None
    assert session.ended_at is None

    # Verify session was saved to data store
    session_manager.data_store.save_session.assert_called_once()


def test_create_session_without_resume(session_manager):
    """Test creating a session without resume data."""
    # Arrange
    config = SessionConfig(
        enabled_modes=[CommunicationMode.TEXT],
        ai_provider="openai",
        ai_model="gpt-4",
        resume_data=None,
    )

    # Act
    session = session_manager.create_session(config)

    # Assert
    assert session is not None
    assert session.user_id.startswith("user_")
    assert session.status == SessionStatus.ACTIVE


def test_start_session(session_manager, sample_session_config):
    """Test starting a session."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session
    
    # Mock AI interviewer start_interview response
    mock_response = InterviewResponse(
        content="Welcome to your interview!",
        token_usage=TokenUsage(
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            estimated_cost=0.0,
            provider="openai",
            model="gpt-4",
            operation="start_interview",
        ),
    )
    session_manager.ai_interviewer.start_interview.return_value = mock_response

    # Act
    session_manager.start_session(session_id)

    # Assert
    session_manager.ai_interviewer.initialize.assert_called_once_with(
        session_id=session_id,
        resume_data=sample_session_config.resume_data,
    )
    session_manager.ai_interviewer.start_interview.assert_called_once()
    
    # Verify communication modes were enabled
    assert session_manager.communication_manager.enable_mode.call_count == 2
    
    # Verify opening message was saved
    session_manager.data_store.save_conversation.assert_called_once()
    
    # Verify active session was set
    assert session_manager._active_session_id == session_id


def test_start_session_not_found(session_manager):
    """Test starting a non-existent session."""
    # Arrange
    session_id = str(uuid.uuid4())
    session_manager.data_store.get_session.return_value = None

    # Act & Assert
    with pytest.raises(InterviewPlatformError, match="not found"):
        session_manager.start_session(session_id)


def test_end_session(session_manager, sample_session_config):
    """Test ending a session."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session
    session_manager._active_session_id = session_id
    
    # Mock evaluation
    mock_evaluation = Mock(spec=EvaluationReport)
    mock_evaluation.overall_score = 85.0
    session_manager.evaluation_manager.generate_evaluation.return_value = mock_evaluation

    # Act
    evaluation = session_manager.end_session(session_id)

    # Assert
    assert evaluation == mock_evaluation
    
    # Verify session was updated
    session_manager.data_store.save_session.assert_called()
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.status == SessionStatus.COMPLETED
    assert saved_session.ended_at is not None
    
    # Verify evaluation was generated
    session_manager.evaluation_manager.generate_evaluation.assert_called_once_with(session_id)
    
    # Verify active session was cleared
    assert session_manager._active_session_id is None


def test_end_session_not_active(session_manager, sample_session_config):
    """Test ending a session that is not active."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=datetime.now(),
        status=SessionStatus.COMPLETED,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session

    # Act & Assert
    with pytest.raises(InterviewPlatformError, match="Cannot end session"):
        session_manager.end_session(session_id)


def test_get_session(session_manager, sample_session_config):
    """Test retrieving a session."""
    # Arrange
    session_id = str(uuid.uuid4())
    expected_session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = expected_session

    # Act
    session = session_manager.get_session(session_id)

    # Assert
    assert session == expected_session
    session_manager.data_store.get_session.assert_called_once_with(session_id)


def test_get_session_not_found(session_manager):
    """Test retrieving a non-existent session."""
    # Arrange
    session_id = str(uuid.uuid4())
    session_manager.data_store.get_session.return_value = None

    # Act
    session = session_manager.get_session(session_id)

    # Assert
    assert session is None


def test_list_sessions(session_manager):
    """Test listing sessions."""
    # Arrange
    from src.models import SessionSummary
    
    expected_sessions = [
        SessionSummary(
            id=str(uuid.uuid4()),
            user_id="test_user_123",
            created_at=datetime.now(),
            duration_minutes=45,
            overall_score=85.0,
            status=SessionStatus.COMPLETED,
        )
    ]

    session_manager.data_store.list_sessions.return_value = expected_sessions

    # Act
    sessions = session_manager.list_sessions(user_id="test_user_123", limit=10, offset=0)

    # Assert
    assert sessions == expected_sessions
    session_manager.data_store.list_sessions.assert_called_once_with(
        user_id="test_user_123", limit=10, offset=0
    )


def test_get_active_session(session_manager, sample_session_config):
    """Test getting the active session."""
    # Arrange
    session_id = str(uuid.uuid4())
    expected_session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager._active_session_id = session_id
    session_manager.data_store.get_session.return_value = expected_session

    # Act
    session = session_manager.get_active_session()

    # Assert
    assert session == expected_session


def test_get_active_session_none(session_manager):
    """Test getting active session when none exists."""
    # Arrange
    session_manager._active_session_id = None

    # Act
    session = session_manager.get_active_session()

    # Assert
    assert session is None


def test_pause_session(session_manager, sample_session_config):
    """Test pausing a session."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session

    # Act
    session_manager.pause_session(session_id)

    # Assert
    session_manager.data_store.save_session.assert_called()
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.status == SessionStatus.PAUSED


def test_resume_session(session_manager, sample_session_config):
    """Test resuming a paused session."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.PAUSED,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session

    # Act
    session_manager.resume_session(session_id)

    # Assert
    session_manager.data_store.save_session.assert_called()
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.status == SessionStatus.ACTIVE
    assert session_manager._active_session_id == session_id


def test_pause_session_not_active(session_manager, sample_session_config):
    """Test pausing a session that is not active."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=datetime.now(),
        status=SessionStatus.COMPLETED,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session

    # Act & Assert
    with pytest.raises(InterviewPlatformError, match="Cannot pause session"):
        session_manager.pause_session(session_id)


def test_resume_session_not_paused(session_manager, sample_session_config):
    """Test resuming a session that is not paused."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session

    # Act & Assert
    with pytest.raises(InterviewPlatformError, match="Cannot resume session"):
        session_manager.resume_session(session_id)


def test_state_transition_active_to_completed(session_manager, sample_session_config):
    """Test complete state transition from ACTIVE to COMPLETED."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session
    session_manager._active_session_id = session_id
    
    mock_evaluation = Mock(spec=EvaluationReport)
    mock_evaluation.overall_score = 85.0
    session_manager.evaluation_manager.generate_evaluation.return_value = mock_evaluation

    # Act
    evaluation = session_manager.end_session(session_id)

    # Assert - Verify state transition
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.status == SessionStatus.COMPLETED
    assert saved_session.ended_at is not None
    assert session_manager._active_session_id is None


def test_state_transition_active_to_paused_to_active(session_manager, sample_session_config):
    """Test state transition from ACTIVE to PAUSED and back to ACTIVE."""
    # Arrange
    session_id = str(uuid.uuid4())
    active_session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    # First call returns active session for pause
    session_manager.data_store.get_session.return_value = active_session

    # Act - Pause
    session_manager.pause_session(session_id)

    # Assert - Verify paused state
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.status == SessionStatus.PAUSED

    # Arrange - Update session to paused for resume
    paused_session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.PAUSED,
        config=sample_session_config,
        metadata={},
    )
    session_manager.data_store.get_session.return_value = paused_session

    # Act - Resume
    session_manager.resume_session(session_id)

    # Assert - Verify active state
    saved_session = session_manager.data_store.save_session.call_args_list[-1][0][0]
    assert saved_session.status == SessionStatus.ACTIVE
    assert session_manager._active_session_id == session_id


def test_session_persistence_on_create(session_manager, sample_session_config):
    """Test that session is persisted immediately on creation."""
    # Act
    session = session_manager.create_session(sample_session_config)

    # Assert - Verify persistence
    session_manager.data_store.save_session.assert_called_once()
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.id == session.id
    assert saved_session.user_id == session.user_id
    assert saved_session.status == SessionStatus.ACTIVE


def test_session_persistence_on_end(session_manager, sample_session_config):
    """Test that session is persisted with updated state on end."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session
    session_manager._active_session_id = session_id
    
    mock_evaluation = Mock(spec=EvaluationReport)
    mock_evaluation.overall_score = 85.0
    session_manager.evaluation_manager.generate_evaluation.return_value = mock_evaluation

    # Act
    session_manager.end_session(session_id)

    # Assert - Verify persistence with updated state
    session_manager.data_store.save_session.assert_called()
    saved_session = session_manager.data_store.save_session.call_args[0][0]
    assert saved_session.status == SessionStatus.COMPLETED
    assert saved_session.ended_at is not None


def test_multiple_sessions_lifecycle(session_manager, sample_session_config):
    """Test managing multiple sessions through their lifecycle."""
    # Create first session
    session1 = session_manager.create_session(sample_session_config)
    assert session1.status == SessionStatus.ACTIVE

    # Create second session
    session2 = session_manager.create_session(sample_session_config)
    assert session2.status == SessionStatus.ACTIVE

    # Verify both sessions were persisted
    assert session_manager.data_store.save_session.call_count == 2

    # Verify sessions have different IDs
    assert session1.id != session2.id


def test_end_session_clears_communication_modes(session_manager, sample_session_config):
    """Test that ending a session disables all communication modes."""
    # Arrange
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        user_id="test_user_123",
        created_at=datetime.now(),
        ended_at=None,
        status=SessionStatus.ACTIVE,
        config=sample_session_config,
        metadata={},
    )

    session_manager.data_store.get_session.return_value = session
    session_manager._active_session_id = session_id
    
    # Mock enabled modes
    enabled_modes = [CommunicationMode.TEXT, CommunicationMode.WHITEBOARD]
    session_manager.communication_manager.get_enabled_modes.return_value = enabled_modes
    
    mock_evaluation = Mock(spec=EvaluationReport)
    mock_evaluation.overall_score = 85.0
    session_manager.evaluation_manager.generate_evaluation.return_value = mock_evaluation

    # Act
    session_manager.end_session(session_id)

    # Assert - Verify all modes were disabled
    assert session_manager.communication_manager.disable_mode.call_count == len(enabled_modes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
