"""
Basic tests for ResumeManager functionality.

This test file verifies core resume parsing and data extraction functionality.
"""

import os
import tempfile
from unittest.mock import Mock, MagicMock, patch
import json

from src.resume.resume_manager import ResumeManager
from src.models import ResumeData, WorkExperience, Education
from src.config import Config, AIProviderConfig, StorageConfig, CommunicationConfig
from src.config import AudioConfig, VideoConfig, WhiteboardConfig, ScreenShareConfig
from src.config import SessionConfig, LoggingConfig, TokenTrackingConfig, DatabaseConfig


def create_test_config():
    """Create a test configuration object."""
    return Config(
        ai_providers={
            "openai": AIProviderConfig(
                default_model="gpt-4",
                temperature=0.1,
                max_tokens=2000,
                api_key="test-key",
            )
        },
        storage=StorageConfig(
            data_dir="./data",
            sessions_dir="./data/sessions",
            logs_dir="./logs",
            max_file_size_mb=100,
        ),
        communication=CommunicationConfig(
            audio=AudioConfig(sample_rate=16000, channels=1, format="wav"),
            video=VideoConfig(fps=30, resolution="1280x720", format="webm"),
            whiteboard=WhiteboardConfig(canvas_width=800, canvas_height=600, stroke_width=2),
            screen_share=ScreenShareConfig(fps=10, format="png"),
        ),
        session=SessionConfig(
            default_duration_minutes=45,
            max_duration_minutes=90,
            auto_save_interval_seconds=60,
        ),
        logging=LoggingConfig(
            level="INFO",
            format="json",
            console_output=True,
            file_output=True,
            database_output=True,
            max_file_size_mb=10,
            backup_count=5,
        ),
        token_tracking=TokenTrackingConfig(
            enabled=True,
            track_by_operation=True,
            display_costs=True,
        ),
        database=DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass",
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
        ),
    )


def test_resume_manager_initialization():
    """Test ResumeManager initialization."""
    mock_data_store = Mock()
    config = create_test_config()
    
    with patch('openai.OpenAI'):
        manager = ResumeManager(
            data_store=mock_data_store,
            config=config,
            logger=None,
        )
        
        assert manager.data_store == mock_data_store
        assert manager.config == config
        assert manager.llm_provider == "openai"


def test_extract_text_from_txt_file():
    """Test extracting text from a TXT file."""
    mock_data_store = Mock()
    config = create_test_config()
    
    with patch('openai.OpenAI'):
        manager = ResumeManager(
            data_store=mock_data_store,
            config=config,
            logger=None,
        )
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("John Doe\nSoftware Engineer\n5 years experience")
            temp_path = f.name
        
        try:
            text = manager._extract_text_from_file(temp_path)
            assert "John Doe" in text
            assert "Software Engineer" in text
            assert "5 years experience" in text
        finally:
            os.unlink(temp_path)


def test_parse_resume_with_mock_llm():
    """Test resume parsing with mocked LLM response."""
    mock_data_store = Mock()
    config = create_test_config()
    
    # Mock LLM response
    mock_llm_response = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "experience_level": "senior",
        "years_of_experience": 8,
        "domain_expertise": ["backend", "distributed-systems", "cloud"],
        "work_experience": [
            {
                "company": "Tech Corp",
                "title": "Senior Software Engineer",
                "duration": "2018-2023",
                "description": "Led backend development team",
            }
        ],
        "education": [
            {
                "institution": "University of Technology",
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "year": "2015",
            }
        ],
        "skills": ["Python", "Go", "Kubernetes", "AWS"],
    }
    
    with patch('openai.OpenAI') as mock_openai:
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(mock_llm_response)
        mock_client.chat.completions.create.return_value = mock_response
        
        manager = ResumeManager(
            data_store=mock_data_store,
            config=config,
            logger=None,
        )
        
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("John Doe\njohn.doe@example.com\nSenior Software Engineer at Tech Corp")
            temp_path = f.name
        
        try:
            resume_data = manager.parse_resume(temp_path)
            
            assert resume_data.name == "John Doe"
            assert resume_data.email == "john.doe@example.com"
            assert resume_data.experience_level == "senior"
            assert resume_data.years_of_experience == 8
            assert "backend" in resume_data.domain_expertise
            assert len(resume_data.work_experience) == 1
            assert resume_data.work_experience[0].company == "Tech Corp"
            assert len(resume_data.education) == 1
            assert resume_data.education[0].institution == "University of Technology"
            assert "Python" in resume_data.skills
        finally:
            os.unlink(temp_path)


def test_get_resume():
    """Test retrieving resume from data store."""
    mock_data_store = Mock()
    config = create_test_config()
    
    # Mock resume data
    mock_resume = ResumeData(
        user_id="user123",
        name="Jane Smith",
        email="jane@example.com",
        experience_level="mid",
        years_of_experience=4,
        domain_expertise=["frontend", "mobile"],
        work_experience=[],
        education=[],
        skills=["React", "TypeScript"],
        raw_text="Resume text",
    )
    
    mock_data_store.get_resume.return_value = mock_resume
    
    with patch('openai.OpenAI'):
        manager = ResumeManager(
            data_store=mock_data_store,
            config=config,
            logger=None,
        )
        
        result = manager.get_resume("user123")
        
        assert result == mock_resume
        mock_data_store.get_resume.assert_called_once_with("user123")


def test_save_resume():
    """Test saving resume to data store."""
    mock_data_store = Mock()
    config = create_test_config()
    
    resume_data = ResumeData(
        user_id="user456",
        name="Bob Johnson",
        email="bob@example.com",
        experience_level="junior",
        years_of_experience=2,
        domain_expertise=["backend"],
        work_experience=[],
        education=[],
        skills=["Python", "Django"],
        raw_text="Resume text",
    )
    
    with patch('openai.OpenAI'):
        manager = ResumeManager(
            data_store=mock_data_store,
            config=config,
            logger=None,
        )
        
        manager.save_resume("user456", resume_data)
        
        mock_data_store.save_resume.assert_called_once()
        saved_resume = mock_data_store.save_resume.call_args[0][0]
        assert saved_resume.user_id == "user456"
        assert saved_resume.name == "Bob Johnson"


if __name__ == "__main__":
    print("Running ResumeManager tests...")
    
    test_resume_manager_initialization()
    print("✓ test_resume_manager_initialization passed")
    
    test_extract_text_from_txt_file()
    print("✓ test_extract_text_from_txt_file passed")
    
    test_parse_resume_with_mock_llm()
    print("✓ test_parse_resume_with_mock_llm passed")
    
    test_get_resume()
    print("✓ test_get_resume passed")
    
    test_save_resume()
    print("✓ test_save_resume passed")
    
    print("\nAll tests passed!")
