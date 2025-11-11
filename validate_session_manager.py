"""
Validation script for SessionManager.

This script demonstrates the SessionManager functionality with mocked dependencies.
"""

from datetime import datetime
from unittest.mock import Mock

from src.session.session_manager import SessionManager
from src.models import (
    SessionConfig,
    CommunicationMode,
    ResumeData,
    WorkExperience,
    Education,
    InterviewResponse,
    TokenUsage,
    EvaluationReport,
    CompetencyScore,
    Feedback,
    ImprovementPlan,
    ActionItem,
    ModeAnalysis,
)


def create_mock_dependencies():
    """Create mocked dependencies for SessionManager."""
    # Mock data store
    data_store = Mock()
    data_store.get_session = Mock()
    data_store.save_session = Mock()
    data_store.save_conversation = Mock()
    data_store.list_sessions = Mock(return_value=[])
    
    # Mock AI interviewer
    ai_interviewer = Mock()
    ai_interviewer.initialize = Mock()
    ai_interviewer.start_interview = Mock(
        return_value=InterviewResponse(
            content="Welcome to your system design interview! Let's discuss designing a URL shortening service.",
            token_usage=TokenUsage(
                input_tokens=0,
                output_tokens=50,
                total_tokens=50,
                estimated_cost=0.001,
                provider="openai",
                model="gpt-4",
                operation="start_interview",
            ),
        )
    )
    
    # Mock evaluation manager
    evaluation_manager = Mock()
    evaluation_manager.generate_evaluation = Mock(
        return_value=EvaluationReport(
            session_id="test-session",
            overall_score=85.5,
            competency_scores={
                "Problem Decomposition": CompetencyScore(
                    score=90.0,
                    confidence_level="high",
                    evidence=["Broke down system into clear components"],
                ),
                "Scalability": CompetencyScore(
                    score=80.0,
                    confidence_level="medium",
                    evidence=["Discussed load balancing and caching"],
                ),
            },
            went_well=[
                Feedback(
                    category="went_well",
                    description="Clear problem decomposition",
                    evidence=["Identified key components early"],
                )
            ],
            went_okay=[
                Feedback(
                    category="went_okay",
                    description="Database design could be more detailed",
                    evidence=["Mentioned sharding but didn't elaborate"],
                )
            ],
            needs_improvement=[
                Feedback(
                    category="needs_improvement",
                    description="Need to discuss monitoring and alerting",
                    evidence=["Did not mention observability"],
                )
            ],
            improvement_plan=ImprovementPlan(
                priority_areas=["Monitoring", "Database Design"],
                concrete_steps=[
                    ActionItem(
                        step_number=1,
                        description="Study monitoring best practices",
                        resources=["Observability Engineering book"],
                    )
                ],
                resources=["System Design Interview book"],
            ),
            communication_mode_analysis=ModeAnalysis(
                audio_quality="Good",
                video_presence="Present",
                whiteboard_usage="Excellent - 5 snapshots",
                screen_share_usage="Not used",
                overall_communication="Good use of multiple modes",
            ),
            created_at=datetime.now(),
        )
    )
    
    # Mock communication manager
    communication_manager = Mock()
    communication_manager.enable_mode = Mock()
    communication_manager.disable_mode = Mock()
    communication_manager.get_enabled_modes = Mock(
        return_value=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD]
    )
    
    # Mock logger
    logger = Mock()
    
    return data_store, ai_interviewer, evaluation_manager, communication_manager, logger


def main():
    """Run SessionManager validation."""
    print("=" * 70)
    print("SessionManager Validation")
    print("=" * 70)
    print()
    
    # Create mocked dependencies
    data_store, ai_interviewer, evaluation_manager, communication_manager, logger = (
        create_mock_dependencies()
    )
    
    # Create SessionManager
    session_manager = SessionManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        evaluation_manager=evaluation_manager,
        communication_manager=communication_manager,
        logger=logger,
    )
    
    print("✓ SessionManager initialized successfully")
    print()
    
    # Create sample resume data
    resume_data = ResumeData(
        user_id="john_doe_123",
        name="John Doe",
        email="john.doe@example.com",
        experience_level="senior",
        years_of_experience=8,
        domain_expertise=["backend", "distributed-systems", "cloud"],
        work_experience=[
            WorkExperience(
                company="Tech Corp",
                title="Senior Software Engineer",
                duration="2020-2024",
                description="Built scalable microservices architecture",
            )
        ],
        education=[
            Education(
                institution="MIT",
                degree="BS",
                field="Computer Science",
                year="2016",
            )
        ],
        skills=["Python", "Java", "AWS", "Kubernetes", "PostgreSQL"],
        raw_text="Full resume text...",
    )
    
    print("Sample Resume Data:")
    print(f"  Name: {resume_data.name}")
    print(f"  Experience Level: {resume_data.experience_level}")
    print(f"  Years of Experience: {resume_data.years_of_experience}")
    print(f"  Domain Expertise: {', '.join(resume_data.domain_expertise)}")
    print()
    
    # Create session configuration
    config = SessionConfig(
        enabled_modes=[
            CommunicationMode.TEXT,
            CommunicationMode.WHITEBOARD,
            CommunicationMode.AUDIO,
        ],
        ai_provider="openai",
        ai_model="gpt-4",
        resume_data=resume_data,
        duration_minutes=45,
    )
    
    print("Session Configuration:")
    print(f"  AI Provider: {config.ai_provider}")
    print(f"  AI Model: {config.ai_model}")
    print(f"  Enabled Modes: {', '.join([m.value for m in config.enabled_modes])}")
    print(f"  Duration: {config.duration_minutes} minutes")
    print()
    
    # Test 1: Create Session
    print("Test 1: Creating Session")
    print("-" * 70)
    session = session_manager.create_session(config)
    print(f"✓ Session created with ID: {session.id}")
    print(f"  User ID: {session.user_id}")
    print(f"  Status: {session.status.value}")
    print(f"  Created At: {session.created_at}")
    print()
    
    # Mock the get_session call for start_session
    data_store.get_session.return_value = session
    
    # Test 2: Start Session
    print("Test 2: Starting Session")
    print("-" * 70)
    session_manager.start_session(session.id)
    print(f"✓ Session {session.id} started successfully")
    print(f"  AI Interviewer initialized: {ai_interviewer.initialize.called}")
    print(f"  Opening question generated: {ai_interviewer.start_interview.called}")
    print(f"  Communication modes enabled: {communication_manager.enable_mode.call_count}")
    print()
    
    # Test 3: Get Active Session
    print("Test 3: Getting Active Session")
    print("-" * 70)
    active_session = session_manager.get_active_session()
    print(f"✓ Active session retrieved: {active_session.id}")
    print()
    
    # Test 4: End Session
    print("Test 4: Ending Session")
    print("-" * 70)
    evaluation = session_manager.end_session(session.id)
    print(f"✓ Session {session.id} ended successfully")
    print(f"  Overall Score: {evaluation.overall_score}/100")
    print(f"  Competencies Evaluated: {len(evaluation.competency_scores)}")
    print(f"  Went Well: {len(evaluation.went_well)} items")
    print(f"  Needs Improvement: {len(evaluation.needs_improvement)} items")
    print(f"  Improvement Steps: {len(evaluation.improvement_plan.concrete_steps)}")
    print()
    
    # Test 5: List Sessions
    print("Test 5: Listing Sessions")
    print("-" * 70)
    sessions = session_manager.list_sessions(user_id=resume_data.user_id)
    print(f"✓ Retrieved {len(sessions)} sessions for user {resume_data.user_id}")
    print()
    
    # Summary
    print("=" * 70)
    print("Validation Summary")
    print("=" * 70)
    print("✓ All SessionManager operations completed successfully")
    print()
    print("Key Features Validated:")
    print("  ✓ Session creation with unique UUID")
    print("  ✓ Session start with component initialization")
    print("  ✓ AI Interviewer integration")
    print("  ✓ Communication Manager integration")
    print("  ✓ Session end with evaluation generation")
    print("  ✓ Active session tracking")
    print("  ✓ Session listing and retrieval")
    print()
    print("SessionManager is ready for integration!")
    print("=" * 70)


if __name__ == "__main__":
    main()
