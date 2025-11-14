#!/usr/bin/env python3
"""
Performance Validation Script

This script validates performance requirements:
1. AI response generation within reasonable time
2. Whiteboard snapshot save within 1 second
3. Multiple whiteboard snapshots handling
4. Token tracking accuracy
5. Session list loading performance
6. Database query performance
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import (
    SessionConfig,
    CommunicationMode,
    ResumeData,
    WorkExperience,
    Education,
)


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
    print(f"\n{Colors.BOLD}{Colors.BLUE}Test {step_num}: {description}{Colors.RESET}")
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


def print_metric(name: str, value: float, unit: str, threshold: float, pass_if_less: bool = True):
    """Print a performance metric with pass/fail indication"""
    passed = (value < threshold) if pass_if_less else (value > threshold)
    status = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"
    comparison = "<" if pass_if_less else ">"
    print(f"  {status} {name}: {value:.2f}{unit} (threshold: {comparison} {threshold}{unit})")
    return passed


def create_test_resume() -> ResumeData:
    """Create a test resume"""
    return ResumeData(
        user_id=f"perf_test_user_{int(time.time())}",
        name="Performance Test User",
        email="perf@test.com",
        experience_level="senior",
        years_of_experience=8,
        domain_expertise=["backend", "distributed-systems"],
        work_experience=[
            WorkExperience(
                company="Tech Corp",
                title="Senior Engineer",
                duration="2020-Present",
                description="System design"
            ).__dict__
        ],
        education=[
            Education(
                institution="University",
                degree="BS",
                field="CS",
                year="2016"
            ).__dict__
        ],
        skills=["Python", "PostgreSQL"],
        raw_text="Sample resume"
    )


def test_ai_response_time(app_components: dict) -> bool:
    """Test AI response generation time"""
    print_step(1, "Testing AI Response Generation Time")
    
    try:
        session_manager = app_components["session_manager"]
        ai_interviewer = app_components["ai_interviewer"]
        resume_manager = app_components["resume_manager"]
        
        # Create session
        resume_data = create_test_resume()
        resume_manager.save_resume(resume_data.user_id, resume_data)
        
        config = SessionConfig(
            enabled_modes=[CommunicationMode.TEXT],
            ai_provider="openai",
            ai_model="gpt-4",
            resume_data=resume_data
        )
        
        session = session_manager.create_session(config)
        session_manager.start_session(session.id)
        
        # Test initial problem generation
        print_info("Testing initial problem generation...")
        start_time = time.time()
        response = ai_interviewer.start_interview(session.id)
        elapsed = time.time() - start_time
        
        passed = print_metric("Initial problem generation", elapsed, "s", 10.0)
        
        # Test response processing
        print_info("Testing response processing...")
        candidate_response = "I would use a microservices architecture with API gateway, load balancer, and database."
        
        start_time = time.time()
        ai_response = ai_interviewer.process_response(session.id, candidate_response)
        elapsed = time.time() - start_time
        
        passed = passed and print_metric("Response processing", elapsed, "s", 10.0)
        
        # Test multiple responses
        print_info("Testing multiple consecutive responses...")
        response_times = []
        
        for i in range(3):
            start_time = time.time()
            ai_response = ai_interviewer.process_response(
                session.id,
                f"Additional response {i+1} with more details about the system design."
            )
            elapsed = time.time() - start_time
            response_times.append(elapsed)
        
        avg_time = sum(response_times) / len(response_times)
        passed = passed and print_metric("Average response time", avg_time, "s", 10.0)
        
        # Cleanup
        session_manager.end_session(session.id)
        
        return passed
        
    except Exception as e:
        print_error(f"AI response time test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_whiteboard_snapshot_performance(app_components: dict) -> bool:
    """Test whiteboard snapshot save performance"""
    print_step(2, "Testing Whiteboard Snapshot Performance")
    
    try:
        session_manager = app_components["session_manager"]
        communication_manager = app_components["communication_manager"]
        
        # Create session
        resume_data = create_test_resume()
        config = SessionConfig(
            enabled_modes=[CommunicationMode.WHITEBOARD],
            ai_provider="openai",
            ai_model="gpt-4",
            resume_data=resume_data
        )
        
        session = session_manager.create_session(config)
        
        # Test single snapshot save
        print_info("Testing single snapshot save...")
        mock_canvas_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 1000  # 1KB PNG
        
        start_time = time.time()
        file_path = communication_manager.save_whiteboard(session.id, mock_canvas_data)
        elapsed = time.time() - start_time
        
        passed = print_metric("Single snapshot save", elapsed, "s", 1.0)
        
        # Test multiple snapshots
        print_info("Testing multiple snapshot saves...")
        save_times = []
        
        for i in range(10):
            mock_data = b'\x89PNG\r\n\x1a\n' + bytes([i] * 1000)
            start_time = time.time()
            file_path = communication_manager.save_whiteboard(session.id, mock_data)
            elapsed = time.time() - start_time
            save_times.append(elapsed)
        
        avg_time = sum(save_times) / len(save_times)
        max_time = max(save_times)
        
        passed = passed and print_metric("Average snapshot save", avg_time, "s", 1.0)
        passed = passed and print_metric("Max snapshot save", max_time, "s", 1.0)
        
        print_success(f"Saved {len(save_times)} snapshots successfully")
        
        # Test larger snapshot
        print_info("Testing larger snapshot (100KB)...")
        large_canvas_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100000
        
        start_time = time.time()
        file_path = communication_manager.save_whiteboard(session.id, large_canvas_data)
        elapsed = time.time() - start_time
        
        passed = passed and print_metric("Large snapshot save", elapsed, "s", 1.0)
        
        return passed
        
    except Exception as e:
        print_error(f"Whiteboard performance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_token_tracking_accuracy(app_components: dict) -> bool:
    """Test token tracking accuracy"""
    print_step(3, "Testing Token Tracking Accuracy")
    
    try:
        session_manager = app_components["session_manager"]
        ai_interviewer = app_components["ai_interviewer"]
        token_tracker = app_components["token_tracker"]
        
        # Create session
        resume_data = create_test_resume()
        config = SessionConfig(
            enabled_modes=[CommunicationMode.TEXT],
            ai_provider="openai",
            ai_model="gpt-4",
            resume_data=resume_data
        )
        
        session = session_manager.create_session(config)
        session_manager.start_session(session.id)
        
        # Make AI calls
        print_info("Making AI API calls...")
        ai_interviewer.start_interview(session.id)
        ai_interviewer.process_response(session.id, "Test response 1")
        ai_interviewer.process_response(session.id, "Test response 2")
        
        # Check token tracking
        print_info("Verifying token tracking...")
        usage = token_tracker.get_session_usage(session.id)
        
        print_info(f"Input tokens: {usage.total_input_tokens}")
        print_info(f"Output tokens: {usage.total_output_tokens}")
        print_info(f"Total tokens: {usage.total_tokens}")
        print_info(f"Estimated cost: ${usage.total_cost:.4f}")
        
        # Verify tokens were tracked
        if usage.total_tokens == 0:
            print_error("No tokens were tracked")
            return False
        
        print_success("Tokens are being tracked")
        
        # Verify cost calculation
        if usage.total_cost == 0:
            print_error("Cost was not calculated")
            return False
        
        print_success("Cost is being calculated")
        
        # Verify breakdown by operation
        print_info("Checking usage breakdown...")
        breakdown = token_tracker.get_usage_breakdown(session.id)
        
        if len(breakdown) == 0:
            print_error("No usage breakdown available")
            return False
        
        print_success(f"Usage breakdown has {len(breakdown)} operation types")
        for operation, usage_data in breakdown.items():
            print_info(f"  {operation}: {usage_data.total_tokens} tokens")
        
        # Verify accuracy (total should equal sum of parts)
        breakdown_total = sum(u.total_tokens for u in breakdown.values())
        if breakdown_total != usage.total_tokens:
            print_error(f"Token count mismatch: {breakdown_total} vs {usage.total_tokens}")
            return False
        
        print_success("Token tracking is accurate")
        
        return True
        
    except Exception as e:
        print_error(f"Token tracking test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_session_list_performance(app_components: dict) -> bool:
    """Test session list loading performance"""
    print_step(4, "Testing Session List Loading Performance")
    
    try:
        session_manager = app_components["session_manager"]
        
        # Create multiple sessions
        print_info("Creating test sessions...")
        session_ids = []
        
        for i in range(20):
            resume_data = create_test_resume()
            config = SessionConfig(
                enabled_modes=[CommunicationMode.TEXT],
                ai_provider="openai",
                ai_model="gpt-4",
                resume_data=resume_data
            )
            session = session_manager.create_session(config)
            session_ids.append(session.id)
        
        print_success(f"Created {len(session_ids)} test sessions")
        
        # Test list performance
        print_info("Testing session list retrieval...")
        start_time = time.time()
        sessions = session_manager.list_sessions()
        elapsed = time.time() - start_time
        
        passed = print_metric("Session list retrieval", elapsed, "s", 2.0)
        print_info(f"Retrieved {len(sessions)} sessions")
        
        # Test with pagination
        print_info("Testing paginated retrieval...")
        start_time = time.time()
        sessions_page1 = session_manager.list_sessions(limit=10, offset=0)
        elapsed = time.time() - start_time
        
        passed = passed and print_metric("Paginated retrieval", elapsed, "s", 1.0)
        print_info(f"Retrieved {len(sessions_page1)} sessions (page 1)")
        
        # Test multiple retrievals
        print_info("Testing multiple consecutive retrievals...")
        retrieval_times = []
        
        for i in range(5):
            start_time = time.time()
            sessions = session_manager.list_sessions()
            elapsed = time.time() - start_time
            retrieval_times.append(elapsed)
        
        avg_time = sum(retrieval_times) / len(retrieval_times)
        passed = passed and print_metric("Average retrieval time", avg_time, "s", 2.0)
        
        return passed
        
    except Exception as e:
        print_error(f"Session list performance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_query_performance(app_components: dict) -> bool:
    """Test database query performance"""
    print_step(5, "Testing Database Query Performance")
    
    try:
        data_store = app_components["data_store"]
        session_manager = app_components["session_manager"]
        
        # Create test data
        print_info("Creating test data...")
        resume_data = create_test_resume()
        config = SessionConfig(
            enabled_modes=[CommunicationMode.TEXT],
            ai_provider="openai",
            ai_model="gpt-4",
            resume_data=resume_data
        )
        
        session = session_manager.create_session(config)
        session_id = session.id
        
        # Add conversation messages
        from models import Message
        for i in range(20):
            msg = Message(
                role="candidate" if i % 2 == 0 else "interviewer",
                content=f"Test message {i}",
                timestamp=datetime.now()
            )
            data_store.save_conversation(session_id, msg)
        
        # Test conversation retrieval
        print_info("Testing conversation history retrieval...")
        start_time = time.time()
        history = data_store.get_conversation_history(session_id)
        elapsed = time.time() - start_time
        
        passed = print_metric("Conversation retrieval", elapsed, "s", 1.0)
        print_info(f"Retrieved {len(history)} messages")
        
        # Test session retrieval
        print_info("Testing session retrieval...")
        start_time = time.time()
        retrieved_session = data_store.get_session(session_id)
        elapsed = time.time() - start_time
        
        passed = passed and print_metric("Session retrieval", elapsed, "s", 0.5)
        
        # Test multiple queries
        print_info("Testing multiple consecutive queries...")
        query_times = []
        
        for i in range(10):
            start_time = time.time()
            history = data_store.get_conversation_history(session_id)
            elapsed = time.time() - start_time
            query_times.append(elapsed)
        
        avg_time = sum(query_times) / len(query_times)
        passed = passed and print_metric("Average query time", avg_time, "s", 1.0)
        
        return passed
        
    except Exception as e:
        print_error(f"Database query performance test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run performance validation"""
    print(f"\n{Colors.BOLD}{'=' * 70}")
    print("Performance Validation")
    print(f"{'=' * 70}{Colors.RESET}\n")
    
    # Check environment
    if not os.getenv("OPENAI_API_KEY"):
        print_error("OPENAI_API_KEY not set. Exiting.")
        sys.exit(1)
    
    if not os.getenv("DATABASE_URL"):
        print_error("DATABASE_URL not set. Exiting.")
        sys.exit(1)
    
    try:
        # Initialize application
        print_info("Initializing application components...")
        from app_factory import create_app
        app_components = create_app()
        print_success("Application initialized")
        
        # Run performance tests
        tests = [
            ("AI Response Time", test_ai_response_time),
            ("Whiteboard Snapshot Performance", test_whiteboard_snapshot_performance),
            ("Token Tracking Accuracy", test_token_tracking_accuracy),
            ("Session List Performance", test_session_list_performance),
            ("Database Query Performance", test_database_query_performance),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func(app_components)
                results.append((test_name, result))
            except Exception as e:
                print_error(f"Test '{test_name}' crashed: {str(e)}")
                results.append((test_name, False))
        
        # Print summary
        print(f"\n{Colors.BOLD}{'=' * 70}")
        print("Performance Test Summary")
        print(f"{'=' * 70}{Colors.RESET}\n")
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = f"{Colors.GREEN}PASS{Colors.RESET}" if result else f"{Colors.RED}FAIL{Colors.RESET}"
            print(f"  {status} - {test_name}")
        
        print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}")
        
        if passed == total:
            print(f"{Colors.GREEN}✓ All performance tests passed{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"{Colors.YELLOW}⚠ Some performance tests failed{Colors.RESET}\n")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
