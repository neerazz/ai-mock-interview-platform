"""
Integration tests for complete interview workflow.

This module tests the end-to-end interview workflow including:
- Session creation with resume upload
- AI interviewer interaction
- Session completion and evaluation generation

Requirements: 12.2
"""

import pytest
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.session.session_manager import SessionManager
from src.resume.resume_manager import ResumeManager
from src.ai.ai_interviewer import AIInterviewer
from src.evaluation.evaluation_manager import EvaluationManager
from src.communication.communication_manager import CommunicationManager
from src.database.data_store import IDataStore
from src.storage.file_storage import FileStorage
from src.ai.token_tracker import TokenTracker
from src.models import (
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
    Feedback,
    ImprovementPlan,
    ActionItem,
    ModeAnalysis,
)


@pytest.fixture
def mock_data_store():
    """Create a mock data store for integration testing."""
    data_store = Mock(spec=IDataStore)
    
    # Mock session storage
    data_store.sessions = {}
    data_store.conversations = {}
    data_store.evaluations = {}
    data_store.resumes = {}
    
    def save_session(session):
        data_store.sessions[session.id] = session
    
    def get_session(session_id):
        return data_store.sessions.get(session_id)
    
    def save_conversation(session_id, message):
        if session_id not in data_store.conversations:
            data_store.conversations[session_id] = []
        data_store.conversations[session_id].append(message)
    
    def get_conversation_history(session_id):
        return data_store.conversations.get(session_id, [])
    
    def save_evaluation(evaluation):
        data_store.evaluations[evaluation.session_id] = evaluation
    
    def get_evaluation(session_id):
        return data_store.evaluations.get(session_id)
    
    def save_resume(resume_data):
        data_store.resumes[resume_data.user_id] = resume_data
    
    def get_resume(user_id):
        return data_store.resumes.get(user_id)
    
    def list_sessions(user_id=None, limit=50, offset=0):
        sessions = list(data_store.sessions.values())
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        return sessions[offset:offset+limit]
    
    def get_media_files(session_id):
        return []
    
    data_store.save_session.side_effect = save_session
    data_store.get_session.side_effect = get_session
    data_store.save_conversation.side_effect = save_conversation
    data_store.get_conversation_history.side_effect = get_conversation_history
    data_store.save_evaluation.side_effect = save_evaluation
    