"""
Basic tests for AI Interviewer functionality.

These tests verify the core functionality of the AIInterviewer class
without making actual API calls.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.ai.ai_interviewer import AIInterviewer
from src.ai.token_tracker import TokenTracker
from src.models import ResumeData, WorkExperience, Education, TokenUsage


@pytest.fixture
def mock_token_tracker():
    """Create a mock token tracker."""
    tracker = Mock(spec=TokenTracker)
    tracker.record_usage.return_value = TokenUsage(
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        estimated_cost=0.005,
        provider="openai",
        model="gpt-4",
        operation="test",
    )
    return tracker


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    return logger


@pytest.fixture
def sample_resume_data():
    """Create sample resume data for testing."""
    return ResumeData(
        user_id="test_user_123",
        name="John Doe",
        email="john@example.com",
        experience_level="senior",
        years_of_experience=8,
        domain_expertise=["backend", "distributed-systems", "cloud"],
        work_experience=[
            WorkExperience(
                company="Tech Corp",
                title="Senior Software Engineer",
                duration="2020-2024",
                description="Built scalable distributed systems",
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
        skills=["Python", "Go", "Kubernetes", "PostgreSQL"],
        raw_text="Sample resume text",
    )


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_ai_interviewer_initialization_openai(
    mock_chat_openai, mock_token_tracker, mock_logger
):
    """Test AI Interviewer initialization with OpenAI."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    # Create interviewer
    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    # Verify
    assert interviewer.provider == "openai"
    assert interviewer.model == "gpt-4"
    assert interviewer.token_tracker == mock_token_tracker
    assert interviewer.logger == mock_logger
    mock_chat_openai.assert_called_once()


@patch("src.ai.ai_interviewer.ChatAnthropic")
def test_ai_interviewer_initialization_anthropic(
    mock_chat_anthropic, mock_token_tracker, mock_logger
):
    """Test AI Interviewer initialization with Anthropic."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_anthropic.return_value = mock_llm

    # Create interviewer
    interviewer = AIInterviewer(
        provider="anthropic",
        model="claude-3-opus-20240229",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    # Verify
    assert interviewer.provider == "anthropic"
    assert interviewer.model == "claude-3-opus-20240229"
    mock_chat_anthropic.assert_called_once()


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_initialize_session(
    mock_chat_openai, mock_token_tracker, mock_logger, sample_resume_data
):
    """Test session initialization."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    # Initialize session
    session_id = "test_session_123"
    interviewer.initialize(session_id, sample_resume_data)

    # Verify
    assert interviewer.session_id == session_id
    assert interviewer.resume_data == sample_resume_data
    assert len(interviewer.memory.chat_memory.messages) == 0


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_start_interview_without_resume(
    mock_chat_openai, mock_token_tracker, mock_logger
):
    """Test starting interview without resume data."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Start interview
    response = interviewer.start_interview()

    # Verify
    assert response is not None
    assert "Welcome" in response.content
    assert "URL shortening" in response.content  # Default problem
    assert response.token_usage.total_tokens == 0  # No API call for opening


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_generate_problem_with_resume(
    mock_chat_openai, mock_token_tracker, mock_logger, sample_resume_data
):
    """Test problem generation with resume data."""
    # Setup
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Design a distributed caching system..."
    mock_response.response_metadata = {
        "token_usage": {"prompt_tokens": 200, "completion_tokens": 100}
    }
    mock_llm.invoke.return_value = mock_response
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123", sample_resume_data)

    # Generate problem
    problem = interviewer.generate_problem(sample_resume_data)

    # Verify
    assert problem is not None
    assert len(problem) > 0
    mock_llm.invoke.assert_called_once()
    mock_token_tracker.record_usage.assert_called_once()


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_process_response(mock_chat_openai, mock_token_tracker, mock_logger):
    """Test processing candidate response."""
    # Setup
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "That's a good start. Can you elaborate on how you would handle data consistency?"
    mock_response.response_metadata = {
        "token_usage": {"prompt_tokens": 150, "completion_tokens": 75}
    }
    mock_llm.invoke.return_value = mock_response
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Process response
    candidate_response = "I would use a load balancer and multiple application servers."
    response = interviewer.process_response(candidate_response)

    # Verify
    assert response is not None
    assert len(response.content) > 0
    assert response.token_usage.total_tokens > 0
    mock_llm.invoke.assert_called_once()


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_ask_clarifying_question(mock_chat_openai, mock_token_tracker, mock_logger):
    """Test asking clarifying question."""
    # Setup
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "Could you clarify what you mean by 'handle it'?"
    mock_response.response_metadata = {
        "token_usage": {"prompt_tokens": 100, "completion_tokens": 50}
    }
    mock_llm.invoke.return_value = mock_response
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Ask clarifying question
    ambiguous_response = "I would just handle it."
    response = interviewer.ask_clarifying_question(ambiguous_response)

    # Verify
    assert response is not None
    assert len(response.content) > 0
    mock_llm.invoke.assert_called_once()


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_adapt_difficulty(mock_chat_openai, mock_token_tracker, mock_logger):
    """Test difficulty adaptation."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Adapt difficulty
    performance_indicators = {
        "response_quality": "high",
        "depth_of_understanding": "deep",
        "technical_accuracy": "accurate",
    }

    interviewer.adapt_difficulty(performance_indicators)

    # Verify - should add a system message to memory
    assert len(interviewer.memory.chat_memory.messages) > 0


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_analyze_whiteboard(mock_chat_openai, mock_token_tracker, mock_logger):
    """Test whiteboard analysis."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Analyze whiteboard (placeholder implementation)
    whiteboard_image = b"fake_image_data"
    analysis = interviewer.analyze_whiteboard(whiteboard_image)

    # Verify
    assert analysis is not None
    assert len(analysis.components_identified) > 0
    assert len(analysis.relationships) > 0


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_get_conversation_history(mock_chat_openai, mock_token_tracker, mock_logger):
    """Test getting conversation history."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Add some messages to memory
    interviewer.memory.chat_memory.add_user_message("Test user message")
    interviewer.memory.chat_memory.add_ai_message("Test AI message")

    # Get history
    history = interviewer.get_conversation_history()

    # Verify
    assert len(history) == 2
    assert history[0].role == "candidate"
    assert history[1].role == "interviewer"


@patch("src.ai.ai_interviewer.ChatOpenAI")
def test_clear_memory(mock_chat_openai, mock_token_tracker, mock_logger):
    """Test clearing conversation memory."""
    # Setup
    mock_llm = MagicMock()
    mock_chat_openai.return_value = mock_llm

    interviewer = AIInterviewer(
        provider="openai",
        model="gpt-4",
        api_key="test-key",
        token_tracker=mock_token_tracker,
        logger=mock_logger,
    )

    interviewer.initialize("test_session_123")

    # Add messages
    interviewer.memory.chat_memory.add_user_message("Test message")

    # Clear memory
    interviewer.clear_memory()

    # Verify
    assert len(interviewer.memory.chat_memory.messages) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
