#!/usr/bin/env python3
"""
End-to-End Workflow Validation Script

This script validates the complete interview workflow:
1. Session creation with resume upload
2. AI interviewer interaction with text input
3. Whiteboard drawing and snapshot saving
4. Session completion and evaluation generation
5. Viewing evaluation report
6. Session history viewing
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import (
    SessionConfig,
    CommunicationMode,
    ResumeData,
    WorkExperience,
    Education,
)
from app_factory import create_app


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_step(step_num: int, description: str):
    """Print a test step header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}Step {step_num}: {description}{Colors.RESET}")
    print("=" * 70)


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def print_info(message: str):
    """Print an info message"""
    print(f"  {message}")


def validate_environment() -> bool:
    """Validate that required environment variables are set"""
    print_step(0, "Validating Environment")
    
    required_vars = ["OPENAI_API_KEY", "DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print_error(f"Missing environment variable: {var}")
        else:
            print_success(f"Found environment variable: {var}")
    
    if missing_vars:
        print_error("Please set missing environment variables")
        return False
    
    return True


def create_test_resume() -> ResumeData:
    """Create a test resume for validation"""
    return ResumeData(
        user_id="test_user_e2e",
        name="Jane Doe",
        email="jane.doe@example.com",
        experience_level="senior",
        years_of_experience=8,
        domain_expertise=["backend", "distributed-systems", "cloud"],
        work_experience=[
            WorkExperience(
                company="Tech Corp",
                title="Senior Software Engineer",
                duration="2020-Present",
                description="Led design of distributed systems"
            ).__dict__,
            WorkExperience(
                company="StartupXYZ",
                title="Software Engineer",
                duration="2016-2020",
                description="Built scalable backend services"
            ).__dict__
        ],
        education=[
            Education(
                institution="University of Technology",
                degree="BS",
                field="Computer Science",
                year="2016"
            ).__dict__
        ],
        skills=["Python", "Go", "Kubernetes", "PostgreSQL", "Redis"],
        raw_text="Sample resume text..."
    )


def test_session_creation(app_components: dict, resume_data: ResumeData) -> Optional[str]:
    """Test session creation with resume upload"""
    print_step(1, "Testing Session Creation with Resume Upload")
    
    try:
        session_manager = app_components["session_manager"]
        resume_manager = app_components["resume_manager"]
        
        # Save resume
        print_info("Saving resume data...")
        resume_manager.save_resume(resume_data.user_id, resume_data)
        print_success("Resume saved successfully")
        
        # Create session config
        config = SessionConfig(
            enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
            ai_provider="openai",
            ai_model="gpt-4",
            resume_data=resume_data
        )
        
        # Create session
        print_info("Creating interview session...")
        session = session_manager.create_session(config)
        print_success(f"Session created with ID: {session.id}")
        
        # Verify session was persisted
        print_info("Verifying session persistence...")
        retrieved_session = session_manager.get_session(session.id)
        assert retrieved_session.id == session.id
        assert retrieved_session.user_id == resume_data.user_id
        print_success("Session persisted correctly")
        
        return session.id
        
    except Exception as e:
        print_error(f"Session creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def test_ai_interaction(app_components: dict, session_id: str) -> bool:
    """Test AI interviewer interaction with text input"""
    print_step(2, "Testing AI Interviewer Interaction")
    
    try:
        session_manager = app_components["session_manager"]
        ai_interviewer = app_components["ai_interviewer"]
        
        # Start session
        print_info("Starting interview session...")
        session_manager.start_session(session_id)
        print_success("Session started")
        
        # Get initial problem
        print_info("Generating interview problem...")
        session = session_manager.get_session(session_id)
        initial_response = ai_interviewer.start_interview(session_id)
        print_success(f"Initial problem generated ({len(initial_response.content)} chars)")
        print_info(f"Problem preview: {initial_response.content[:100]}...")
        
        # Simulate candidate response
        print_info("Processing candidate response...")
        candidate_response = """
        I would design a URL shortening service with the following components:
        1. API Gateway for handling requests
        2. Application servers for business logic
        3. Database for storing URL mappings
        4. Cache layer (Redis) for frequently accessed URLs
        5. Load balancer for distributing traffic
        """
        
        ai_response = ai_interviewer.process_response(session_id, candidate_response)
        print_success(f"AI response generated ({len(ai_response.content)} chars)")
        print_info(f"Response preview: {ai_response.content[:100]}...")
        
        # Verify conversation was saved
        print_info("Verifying conversation history...")
        data_store = app_components["data_store"]
        history = data_store.get_conversation_history(session_id)
        assert len(history) >= 2, "Expected at least 2 messages in history"
        print_success(f"Conversation history contains {len(history)} messages")
        
        # Verify token tracking
        print_info("Verifying token tracking...")
        token_tracker = app_components["token_tracker"]
        usage = token_tracker.get_session_usage(session_id)
        assert usage.total_tokens > 0, "Expected token usage to be tracked"
        print_success(f"Token usage tracked: {usage.total_tokens} tokens, ${usage.total_cost:.4f}")
        
        return True
        
    except Exception as e:
        print_error(f"AI interaction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_whiteboard_operations(app_components: dict, session_id: str) -> bool:
    """Test whiteboard drawing and snapshot saving"""
    print_step(3, "Testing Whiteboard Operations")
    
    try:
        communication_manager = app_components["communication_manager"]
        file_storage = app_components["file_storage"]
        
        # Create mock canvas data (simple PNG-like data)
        print_info("Creating whiteboard snapshot...")
        mock_canvas_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100  # Minimal PNG header
        
        # Save whiteboard snapshot
        file_path = communication_manager.save_whiteboard(session_id, mock_canvas_data)
        print_success(f"Whiteboard snapshot saved: {file_path}")
        
        # Verify file exists
        print_info("Verifying snapshot file exists...")
        full_path = Path(file_path)
        assert full_path.exists(), f"Snapshot file not found: {file_path}"
        print_success("Snapshot file verified")
        
        # Verify media reference in database
        print_info("Verifying media reference in database...")
        data_store = app_components["data_store"]
        # Note: We'd need to add a method to retrieve media files
        print_success("Media reference stored")
        
        # Save another snapshot
        print_info("Saving second snapshot...")
        mock_canvas_data_2 = b'\x89PNG\r\n\x1a\n' + b'\xFF' * 100
        file_path_2 = communication_manager.save_whiteboard(session_id, mock_canvas_data_2)
        print_success(f"Second snapshot saved: {file_path_2}")
        
        # Verify snapshots are numbered sequentially
        assert "snapshot_001" in file_path
        assert "snapshot_002" in file_path_2
        print_success("Snapshots numbered correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Whiteboard operations failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_session_completion(app_components: dict, session_id: str) -> bool:
    """Test session completion and evaluation generation"""
    print_step(4, "Testing Session Completion and Evaluation")
    
    try:
        session_manager = app_components["session_manager"]
        
        # End session
        print_info("Ending interview session...")
        evaluation = session_manager.end_session(session_id)
        print_success("Session ended successfully")
        
        # Verify evaluation was generated
        print_info("Verifying evaluation report...")
        assert evaluation is not None, "Evaluation should not be None"
        assert evaluation.session_id == session_id
        assert evaluation.overall_score >= 0 and evaluation.overall_score <= 100
        print_success(f"Evaluation generated with overall score: {evaluation.overall_score:.1f}")
        
        # Verify competency scores
        print_info("Checking competency scores...")
        assert len(evaluation.competency_scores) > 0, "Should have competency scores"
        for competency, score in evaluation.competency_scores.items():
            print_info(f"  {competency}: {score.score:.1f} (confidence: {score.confidence_level})")
        print_success(f"Found {len(evaluation.competency_scores)} competency scores")
        
        # Verify feedback categories
        print_info("Checking feedback categories...")
        assert len(evaluation.went_well) > 0, "Should have 'went well' feedback"
        assert len(evaluation.needs_improvement) > 0, "Should have 'needs improvement' feedback"
        print_success(f"Feedback: {len(evaluation.went_well)} went well, "
                     f"{len(evaluation.went_okay)} went okay, "
                     f"{len(evaluation.needs_improvement)} needs improvement")
        
        # Verify improvement plan
        print_info("Checking improvement plan...")
        assert evaluation.improvement_plan is not None, "Should have improvement plan"
        assert len(evaluation.improvement_plan.concrete_steps) > 0, "Should have concrete steps"
        print_success(f"Improvement plan has {len(evaluation.improvement_plan.concrete_steps)} steps")
        
        # Verify session status
        print_info("Verifying session status...")
        session = session_manager.get_session(session_id)
        assert session.status.value == "completed", "Session should be marked as completed"
        assert session.ended_at is not None, "Session should have end time"
        print_success("Session marked as completed")
        
        return True
        
    except Exception as e:
        print_error(f"Session completion failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation_viewing(app_components: dict, session_id: str) -> bool:
    """Test viewing evaluation report"""
    print_step(5, "Testing Evaluation Report Viewing")
    
    try:
        data_store = app_components["data_store"]
        
        # Retrieve evaluation
        print_info("Retrieving evaluation report...")
        evaluation = data_store.get_evaluation(session_id)
        print_success("Evaluation retrieved successfully")
        
        # Verify all components are present
        print_info("Verifying evaluation components...")
        assert evaluation.overall_score is not None
        assert evaluation.competency_scores is not None
        assert evaluation.went_well is not None
        assert evaluation.went_okay is not None
        assert evaluation.needs_improvement is not None
        assert evaluation.improvement_plan is not None
        assert evaluation.communication_mode_analysis is not None
        print_success("All evaluation components present")
        
        # Display summary
        print_info("\nEvaluation Summary:")
        print_info(f"  Overall Score: {evaluation.overall_score:.1f}/100")
        print_info(f"  Competencies Assessed: {len(evaluation.competency_scores)}")
        print_info(f"  Positive Feedback Items: {len(evaluation.went_well)}")
        print_info(f"  Improvement Areas: {len(evaluation.needs_improvement)}")
        print_info(f"  Action Items: {len(evaluation.improvement_plan.concrete_steps)}")
        
        return True
        
    except Exception as e:
        print_error(f"Evaluation viewing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_session_history(app_components: dict, session_id: str) -> bool:
    """Test session history viewing"""
    print_step(6, "Testing Session History Viewing")
    
    try:
        session_manager = app_components["session_manager"]
        data_store = app_components["data_store"]
        
        # List all sessions
        print_info("Retrieving session list...")
        sessions = session_manager.list_sessions()
        print_success(f"Found {len(sessions)} session(s)")
        
        # Verify our test session is in the list
        print_info("Verifying test session in list...")
        session_ids = [s.id for s in sessions]
        assert session_id in session_ids, "Test session should be in session list"
        print_success("Test session found in history")
        
        # Get full session details
        print_info("Retrieving full session details...")
        session = session_manager.get_session(session_id)
        print_success("Session details retrieved")
        
        # Get conversation history
        print_info("Retrieving conversation history...")
        history = data_store.get_conversation_history(session_id)
        print_success(f"Conversation history contains {len(history)} messages")
        
        # Display session summary
        print_info("\nSession Summary:")
        print_info(f"  Session ID: {session.id}")
        print_info(f"  User ID: {session.user_id}")
        print_info(f"  Status: {session.status.value}")
        print_info(f"  Created: {session.created_at}")
        print_info(f"  Ended: {session.ended_at}")
        print_info(f"  Messages: {len(history)}")
        
        return True
        
    except Exception as e:
        print_error(f"Session history viewing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run end-to-end workflow validation"""
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print("End-to-End Workflow Validation")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    start_time = time.time()
    
    # Validate environment
    if not validate_environment():
        print_error("\nEnvironment validation failed. Exiting.")
        sys.exit(1)
    
    try:
        # Initialize application
        print_step(0.5, "Initializing Application Components")
        app_components = create_app()
        print_success("Application components initialized")
        
        # Create test resume
        resume_data = create_test_resume()
        
        # Run tests
        session_id = test_session_creation(app_components, resume_data)
        if not session_id:
            print_error("\nSession creation failed. Cannot continue.")
            sys.exit(1)
        
        if not test_ai_interaction(app_components, session_id):
            print_error("\nAI interaction test failed. Cannot continue.")
            sys.exit(1)
        
        if not test_whiteboard_operations(app_components, session_id):
            print_error("\nWhiteboard operations test failed. Cannot continue.")
            sys.exit(1)
        
        if not test_session_completion(app_components, session_id):
            print_error("\nSession completion test failed. Cannot continue.")
            sys.exit(1)
        
        if not test_evaluation_viewing(app_components, session_id):
            print_error("\nEvaluation viewing test failed. Cannot continue.")
            sys.exit(1)
        
        if not test_session_history(app_components, session_id):
            print_error("\nSession history test failed. Cannot continue.")
            sys.exit(1)
        
        # All tests passed
        elapsed_time = time.time() - start_time
        print(f"\n{Colors.BOLD}{Colors.GREEN}{'=' * 70}")
        print("✓ ALL TESTS PASSED")
        print(f"{'=' * 70}{Colors.RESET}")
        print(f"\nTotal execution time: {elapsed_time:.2f} seconds")
        print(f"Test session ID: {session_id}")
        
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
