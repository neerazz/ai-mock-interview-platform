"""
Tests for EvaluationManager.

This module tests the evaluation generation functionality including
competency analysis, feedback categorization, and improvement plan creation.
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from src.evaluation.evaluation_manager import EvaluationManager
from src.models import (
    Session,
    SessionConfig,
    SessionStatus,
    CommunicationMode,
    Message,
    MediaFile,
    CompetencyScore,
    Feedback,
    ImprovementPlan,
    ActionItem,
    ModeAnalysis,
    TokenUsage,
)


def test_evaluation_manager_initialization():
    """Test EvaluationManager initialization."""
    data_store = Mock()
    ai_interviewer = Mock()
    logger = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        logger=logger,
    )

    assert manager.data_store == data_store
    assert manager.ai_interviewer == ai_interviewer
    assert manager.logger == logger


def test_generate_evaluation():
    """Test complete evaluation generation."""
    # Setup mocks
    data_store = Mock()
    ai_interviewer = Mock()
    logger = Mock()

    # Create test session
    session_id = "test-session-123"
    session = Session(
        id=session_id,
        user_id="test-user",
        created_at=datetime.now(),
        ended_at=datetime.now(),
        status=SessionStatus.COMPLETED,
        config=SessionConfig(
            enabled_modes=[CommunicationMode.AUDIO, CommunicationMode.WHITEBOARD],
            ai_provider="openai",
            ai_model="gpt-4",
        ),
    )

    # Create test conversation
    conversation = [
        Message(
            role="interviewer",
            content="Design a URL shortening service.",
            timestamp=datetime.now(),
        ),
        Message(
            role="candidate",
            content="I would start by identifying the key components...",
            timestamp=datetime.now(),
        ),
    ]

    # Create test media files
    media_files = [
        MediaFile(
            file_type="audio",
            file_path="test/audio.wav",
            timestamp=datetime.now(),
            file_size_bytes=1024,
        ),
        MediaFile(
            file_type="whiteboard",
            file_path="test/whiteboard.png",
            timestamp=datetime.now(),
            file_size_bytes=2048,
        ),
    ]

    # Mock data store responses
    data_store.get_session.return_value = session
    data_store.get_conversation_history.return_value = conversation
    data_store.get_media_files.return_value = media_files

    # Mock AI interviewer responses
    competency_response = """{
        "Problem Decomposition": {
            "score": 85,
            "confidence_level": "high",
            "evidence": ["Identified key components", "Clear structure"]
        },
        "Scalability Considerations": {
            "score": 75,
            "confidence_level": "medium",
            "evidence": ["Mentioned load balancing"]
        }
    }"""

    feedback_response = """{
        "went_well": [
            {"description": "Clear problem decomposition", "evidence": ["Identified components"]}
        ],
        "went_okay": [
            {"description": "Basic scalability discussion", "evidence": ["Mentioned load balancing"]}
        ],
        "needs_improvement": [
            {"description": "Limited discussion of trade-offs", "evidence": ["No alternatives discussed"]}
        ]
    }"""

    improvement_response = """{
        "concrete_steps": [
            {
                "step_number": 1,
                "description": "Practice trade-off analysis",
                "resources": ["System Design Primer"]
            }
        ],
        "resources": ["Designing Data-Intensive Applications"]
    }"""

    # Mock LLM calls
    ai_interviewer._call_llm_with_retry.side_effect = [
        (competency_response, TokenUsage(100, 200, 300, 0.01, "openai", "gpt-4", "analyze")),
        (feedback_response, TokenUsage(100, 200, 300, 0.01, "openai", "gpt-4", "feedback")),
        (improvement_response, TokenUsage(100, 200, 300, 0.01, "openai", "gpt-4", "improvement")),
    ]

    # Create manager and generate evaluation
    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        logger=logger,
    )

    evaluation = manager.generate_evaluation(session_id)

    # Verify evaluation structure
    assert evaluation.session_id == session_id
    assert evaluation.overall_score > 0
    assert len(evaluation.competency_scores) > 0
    assert len(evaluation.went_well) > 0
    assert len(evaluation.needs_improvement) > 0
    assert evaluation.improvement_plan is not None
    assert evaluation.communication_mode_analysis is not None

    # Verify data store was called
    data_store.get_session.assert_called_once_with(session_id)
    data_store.get_conversation_history.assert_called_once_with(session_id)
    data_store.get_media_files.assert_called_once_with(session_id)
    data_store.save_evaluation.assert_called_once()


def test_calculate_overall_score():
    """Test overall score calculation."""
    data_store = Mock()
    ai_interviewer = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
    )

    competency_scores = {
        "Problem Decomposition": CompetencyScore(
            score=80.0, confidence_level="high", evidence=[]
        ),
        "Scalability": CompetencyScore(
            score=70.0, confidence_level="medium", evidence=[]
        ),
        "Communication": CompetencyScore(
            score=90.0, confidence_level="high", evidence=[]
        ),
    }

    overall = manager._calculate_overall_score(competency_scores)
    assert overall == 80.0  # (80 + 70 + 90) / 3


def test_analyze_communication_modes():
    """Test communication mode analysis."""
    data_store = Mock()
    ai_interviewer = Mock()
    logger = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        logger=logger,
    )

    enabled_modes = [
        CommunicationMode.AUDIO,
        CommunicationMode.WHITEBOARD,
    ]

    media_files = [
        MediaFile("audio", "audio1.wav", datetime.now(), 1024),
        MediaFile("audio", "audio2.wav", datetime.now(), 1024),
        MediaFile("whiteboard", "wb1.png", datetime.now(), 2048),
        MediaFile("whiteboard", "wb2.png", datetime.now(), 2048),
        MediaFile("whiteboard", "wb3.png", datetime.now(), 2048),
    ]

    analysis = manager._analyze_communication_modes(
        "test-session", enabled_modes, media_files
    )

    assert analysis.audio_quality is not None
    assert "2 audio recordings" in analysis.audio_quality
    assert analysis.whiteboard_usage is not None
    assert "3 snapshots" in analysis.whiteboard_usage
    assert analysis.overall_communication is not None


def test_format_conversation():
    """Test conversation formatting."""
    data_store = Mock()
    ai_interviewer = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
    )

    messages = [
        Message("interviewer", "Question 1", datetime.now()),
        Message("candidate", "Answer 1", datetime.now()),
        Message("interviewer", "Question 2", datetime.now()),
        Message("candidate", "Answer 2", datetime.now()),
    ]

    formatted = manager._format_conversation(messages)

    assert "Interviewer: Question 1" in formatted
    assert "Candidate: Answer 1" in formatted
    assert "Interviewer: Question 2" in formatted
    assert "Candidate: Answer 2" in formatted


def test_parse_competency_scores_with_valid_json():
    """Test parsing competency scores from valid JSON."""
    data_store = Mock()
    ai_interviewer = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
    )

    response = """{
        "Problem Decomposition": {
            "score": 85,
            "confidence_level": "high",
            "evidence": ["Good structure", "Clear components"]
        },
        "Scalability": {
            "score": 70,
            "confidence_level": "medium",
            "evidence": ["Basic understanding"]
        }
    }"""

    competencies = ["Problem Decomposition", "Scalability"]
    scores = manager._parse_competency_scores(response, competencies)

    assert len(scores) == 2
    assert scores["Problem Decomposition"].score == 85
    assert scores["Problem Decomposition"].confidence_level == "high"
    assert len(scores["Problem Decomposition"].evidence) == 2
    assert scores["Scalability"].score == 70


def test_parse_feedback_with_valid_json():
    """Test parsing feedback from valid JSON."""
    data_store = Mock()
    ai_interviewer = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
    )

    response = """{
        "went_well": [
            {"description": "Good analysis", "evidence": ["Example 1"]}
        ],
        "went_okay": [
            {"description": "Basic understanding", "evidence": ["Example 2"]}
        ],
        "needs_improvement": [
            {"description": "Limited depth", "evidence": ["Example 3"]}
        ]
    }"""

    feedback = manager._parse_feedback(response)

    assert len(feedback["went_well"]) == 1
    assert feedback["went_well"][0].description == "Good analysis"
    assert len(feedback["went_okay"]) == 1
    assert len(feedback["needs_improvement"]) == 1


def test_parse_improvement_plan_with_valid_json():
    """Test parsing improvement plan from valid JSON."""
    data_store = Mock()
    ai_interviewer = Mock()

    manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
    )

    response = """{
        "concrete_steps": [
            {
                "step_number": 1,
                "description": "Practice system design",
                "resources": ["Book 1", "Course 1"]
            },
            {
                "step_number": 2,
                "description": "Study scalability patterns",
                "resources": ["Book 2"]
            }
        ],
        "resources": ["General resource"]
    }"""

    priority_areas = ["Scalability", "Trade-offs"]
    plan = manager._parse_improvement_plan(response, priority_areas)

    assert len(plan.priority_areas) == 2
    assert len(plan.concrete_steps) == 2
    assert plan.concrete_steps[0].step_number == 1
    assert plan.concrete_steps[0].description == "Practice system design"
    assert len(plan.concrete_steps[0].resources) == 2
    assert len(plan.resources) == 1


if __name__ == "__main__":
    print("Running EvaluationManager tests...")
    
    test_evaluation_manager_initialization()
    print("✓ Initialization test passed")
    
    test_generate_evaluation()
    print("✓ Generate evaluation test passed")
    
    test_calculate_overall_score()
    print("✓ Calculate overall score test passed")
    
    test_analyze_communication_modes()
    print("✓ Analyze communication modes test passed")
    
    test_format_conversation()
    print("✓ Format conversation test passed")
    
    test_parse_competency_scores_with_valid_json()
    print("✓ Parse competency scores test passed")
    
    test_parse_feedback_with_valid_json()
    print("✓ Parse feedback test passed")
    
    test_parse_improvement_plan_with_valid_json()
    print("✓ Parse improvement plan test passed")
    
    print("\nAll tests passed! ✓")
