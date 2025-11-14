"""
Integration tests for multi-mode communication.

This module tests the integration of multiple communication modes
including audio, video, whiteboard, and screen share working simultaneously.

Requirements: 12.2
"""

import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.communication.communication_manager import CommunicationManager
from src.communication.audio_handler import AudioHandler
from src.communication.video_handler import VideoHandler
from src.communication.whiteboard_handler import WhiteboardHandler
from src.communication.screen_handler import ScreenShareHandler
from src.storage.file_storage import FileStorage
from src.models import CommunicationMode


@pytest.fixture
def temp_storage():
    """Create temporary storage for testing."""
    temp_dir = tempfile.mkdtemp()
    file_storage = FileStorage(base_dir=temp_dir)
    yield file_storage
    # Cleanup handled by tempfile


@pytest.fixture
def communication_handlers(temp_storage):
    """Create all communication handlers."""
    audio_handler = AudioHandler(file_storage=temp_storage)
    video_handler = VideoHandler(file_storage=temp_storage)
    whiteboard_handler = WhiteboardHandler(file_storage=temp_storage)
    screen_handler = ScreenShareHandler(file_storage=temp_storage)
    
    return {
        "audio": audio_handler,
        "video": video_handler,
        "whiteboard": whiteboard_handler,
        "screen": screen_handler,
    }


@pytest.fixture
def communication_manager(communication_handlers):
    """Create communication manager with all handlers."""
    manager = CommunicationManager(
        audio_handler=communication_handlers["audio"],
        video_handler=communication_handlers["video"],
        whiteboard_handler=communication_handlers["whiteboard"],
        screen_handler=communication_handlers["screen"],
    )
    return manager


class TestMultiModeCommunication:
    """Test multiple communication modes working simultaneously."""

    def test_enable_multiple_modes(self, communication_manager):
        """Test enabling multiple communication modes at once."""
        # Enable all modes
        communication_manager.enable_mode(CommunicationMode.AUDIO)
        communication_manager.enable_mode(CommunicationMode.VIDEO)
        communication_manager.enable_mode(CommunicationMode.WHITEBOARD)
        communication_manager.enable_mode(CommunicationMode.SCREEN_SHARE)
        
        # Verify all modes are enabled
        enabled_modes = communication_manager.get_enabled_modes()
        assert CommunicationMode.AUDIO in enabled_modes
        assert CommunicationMode.VIDEO in enabled_modes
        assert CommunicationMode.WHITEBOARD in enabled_modes
        assert CommunicationMode.SCREEN_SHARE in enabled_modes
        assert len(enabled_modes) == 4

    def test_audio_and_video_simultaneously(self, communication_manager, temp_storage):
        """Test audio and video recording simultaneously."""
        session_id = "multimode-test-001"
        
        # Enable both modes
        communication_manager.enable_mode(CommunicationMode.AUDIO)
        communication_manager.enable_mode(CommunicationMode.VIDEO)
        
        # Start recording both
        audio_handler = communication_manager.audio_handler
        video_handler = communication_manager.video_handler
        
        audio_handler.start_recording(session_id)
        video_handler.start_recording(session_id)
        
        # Verify both are recording
        assert audio_handler.is_recording(session_id)
        assert video_handler.is_recording(session_id)
        
        # Record some data
        audio_path = audio_handler.record_audio(session_id, b"audio data")
        video_path = video_handler.capture_video(session_id, b"video data")
        
        # Verify files were created
        assert temp_storage.file_exists(audio_path)
        assert temp_storage.file_exists(video_path)
        
        # Stop both recordings
        audio_metadata = audio_handler.stop_recording(session_id)
        video_metadata = video_handler.stop_recording(session_id)
        
        assert audio_metadata is not None
        assert video_metadata is not None
        assert not audio_handler.is_recording(session_id)
        assert not video_handler.is_recording(session_id)

    def test_audio_video_whiteboard_simultaneously(
        self, communication_manager, temp_storage
    ):
        """Test audio, video, and whiteboard working together."""
        session_id = "multimode-test-002"
        
        # Enable three modes
        communication_manager.enable_mode(CommunicationMode.AUDIO)
        communication_manager.enable_mode(CommunicationMode.VIDEO)
        communication_manager.enable_mode(CommunicationMode.WHITEBOARD)
        
        # Get handlers
        audio_handler = communication_manager.audio_handler
        video_handler = communication_manager.video_handler
        whiteboard_handler = communication_manager.whiteboard_handler
        
        # Start audio and video recording
        audio_handler.start_recording(session_id)
        video_handler.start_recording(session_id)
        
        # Record data from all three modes
        audio_path = audio_handler.record_audio(session_id, b"audio data")
        video_path = video_handler.capture_video(session_id, b"video data")
        whiteboard_path = whiteboard_handler.save_whiteboard(
            session_id, b"whiteboard snapshot"
        )
        
        # Verify all files exist
        assert temp_storage.file_exists(audio_path)
        assert temp_storage.file_exists(video_path)
        assert temp_storage.file_exists(whiteboard_path)
        
        # Verify session has files from all modes
        session_files = temp_storage.get_session_files(session_id)
        assert len(session_files) >= 3

    def test_all_four_modes_simultaneously(self, communication_manager, temp_storage):
        """Test all four communication modes working together."""
        session_id = "multimode-test-003"
        
        # Enable all modes
        for mode in [
            CommunicationMode.AUDIO,
            CommunicationMode.VIDEO,
            CommunicationMode.WHITEBOARD,
            CommunicationMode.SCREEN_SHARE,
        ]:
            communication_manager.enable_mode(mode)
        
        # Get all handlers
        audio_handler = communication_manager.audio_handler
        video_handler = communication_manager.video_handler
        whiteboard_handler = communication_manager.whiteboard_handler
        screen_handler = communication_manager.screen_handler
        
        # Start recordings
        audio_handler.start_recording(session_id)
        video_handler.start_recording(session_id)
        screen_handler.start_capture(session_id)
        
        # Capture data from all modes
        audio_path = audio_handler.record_audio(session_id, b"audio data")
        video_path = video_handler.capture_video(session_id, b"video data")
        whiteboard_path = whiteboard_handler.save_whiteboard(
            session_id, b"whiteboard data"
        )
        screen_path = screen_handler.capture_screen(session_id, b"screen data")
        
        # Verify all files exist
        assert temp_storage.file_exists(audio_path)
        assert temp_storage.file_exists(video_path)
        assert temp_storage.file_exists(whiteboard_path)
        assert temp_storage.file_exists(screen_path)
        
        # Verify session has files from all modes
        session_files = temp_storage.get_session_files(session_id)
        assert len(session_files) >= 4
        
        # Stop recordings
        audio_handler.stop_recording(session_id)
        video_handler.stop_recording(session_id)
        screen_handler.stop_capture(session_id)

    def test_mode_switching_during_session(self, communication_manager, temp_storage):
        """Test switching modes on and off during a session."""
        session_id = "multimode-test-004"
        
        # Start with audio only
        communication_manager.enable_mode(CommunicationMode.AUDIO)
        audio_handler = communication_manager.audio_handler
        audio_handler.start_recording(session_id)
        
        # Record some audio
        audio_path1 = audio_handler.record_audio(session_id, b"audio 1")
        assert temp_storage.file_exists(audio_path1)
        
        # Add video mid-session
        communication_manager.enable_mode(CommunicationMode.VIDEO)
        video_handler = communication_manager.video_handler
        video_handler.start_recording(session_id)
        
        # Record both
        audio_path2 = audio_handler.record_audio(session_id, b"audio 2")
        video_path1 = video_handler.capture_video(session_id, b"video 1")
        
        assert temp_storage.file_exists(audio_path2)
        assert temp_storage.file_exists(video_path1)
        
        # Add whiteboard
        communication_manager.enable_mode(CommunicationMode.WHITEBOARD)
        whiteboard_handler = communication_manager.whiteboard_handler
        whiteboard_path = whiteboard_handler.save_whiteboard(
            session_id, b"whiteboard"
        )
        assert temp_storage.file_exists(whiteboard_path)
        
        # Disable audio
        communication_manager.disable_mode(CommunicationMode.AUDIO)
        audio_handler.stop_recording(session_id)
        
        # Continue with video and whiteboard
        video_path2 = video_handler.capture_video(session_id, b"video 2")
        assert temp_storage.file_exists(video_path2)
        
        # Verify final state
        enabled_modes = communication_manager.get_enabled_modes()
        assert CommunicationMode.AUDIO not in enabled_modes
        assert CommunicationMode.VIDEO in enabled_modes
        assert CommunicationMode.WHITEBOARD in enabled_modes

    def test_multiple_captures_per_mode(self, communication_manager, temp_storage):
        """Test multiple captures from each mode in a single session."""
        session_id = "multimode-test-005"
        
        # Enable all modes
        communication_manager.enable_mode(CommunicationMode.AUDIO)
        communication_manager.enable_mode(CommunicationMode.VIDEO)
        communication_manager.enable_mode(CommunicationMode.WHITEBOARD)
        communication_manager.enable_mode(CommunicationMode.SCREEN_SHARE)
        
        # Get handlers
        audio_handler = communication_manager.audio_handler
        video_handler = communication_manager.video_handler
        whiteboard_handler = communication_manager.whiteboard_handler
        screen_handler = communication_manager.screen_handler
        
        # Capture multiple times from each mode
        audio_paths = []
        video_paths = []
        whiteboard_paths = []
        screen_paths = []
        
        for i in range(3):
            audio_paths.append(
                audio_handler.record_audio(session_id, f"audio {i}".encode())
            )
            video_paths.append(
                video_handler.capture_video(session_id, f"video {i}".encode())
            )
            whiteboard_paths.append(
                whiteboard_handler.save_whiteboard(
                    session_id, f"whiteboard {i}".encode()
                )
            )
            screen_paths.append(
                screen_handler.capture_screen(session_id, f"screen {i}".encode())
            )
        
        # Verify all files exist
        for path in audio_paths + video_paths + whiteboard_paths + screen_paths:
            assert temp_storage.file_exists(path)
        
        # Verify counts
        assert whiteboard_handler.get_snapshot_count(session_id) == 3
        assert screen_handler.get_capture_count(session_id) == 3
        
        # Verify total session files
        session_files = temp_storage.get_session_files(session_id)
        assert len(session_files) >= 12  # 3 from each of 4 modes

    def test_mode_isolation(self, communication_manager, temp_storage):
        """Test that modes operate independently without interference."""
        session_id = "multimode-test-006"
        
        # Enable all modes
        communication_manager.enable_mode(CommunicationMode.AUDIO)
        communication_manager.enable_mode(CommunicationMode.VIDEO)
        communication_manager.enable_mode(CommunicationMode.WHITEBOARD)
        
        # Get handlers
        audio_handler = communication_manager.audio_handler
        video_handler = communication_manager.video_handler
        whiteboard_handler = communication_manager.whiteboard_handler
        
        # Start audio recording
        audio_handler.start_recording(session_id)
        assert audio_handler.is_recording(session_id)
        assert not video_handler.is_recording(session_id)
        
        # Start video recording
        video_handler.start_recording(session_id)
        assert audio_handler.is_recording(session_id)
        assert video_handler.is_recording(session_id)
        
        # Stop audio (video should continue)
        audio_handler.stop_recording(session_id)
        assert not audio_handler.is_recording(session_id)
        assert video_handler.is_recording(session_id)
        
        # Whiteboard operations don't affect recordings
        whiteboard_handler.save_whiteboard(session_id, b"snapshot")
        assert video_handler.is_recording(session_id)
        
        # Stop video
        video_handler.stop_recording(session_id)
        assert not video_handler.is_recording(session_id)

    def test_concurrent_file_operations(self, communication_manager, temp_storage):
        """Test concurrent file operations from multiple modes."""
        session_id = "multimode-test-007"
        
        # Enable modes
        communication_manager.enable_mode(CommunicationMode.WHITEBOARD)
        communication_manager.enable_mode(CommunicationMode.SCREEN_SHARE)
        
        whiteboard_handler = communication_manager.whiteboard_handler
        screen_handler = communication_manager.screen_handler
        
        # Perform rapid concurrent operations
        paths = []
        for i in range(5):
            wb_path = whiteboard_handler.save_whiteboard(
                session_id, f"wb{i}".encode()
            )
            sc_path = screen_handler.capture_screen(session_id, f"sc{i}".encode())
            paths.extend([wb_path, sc_path])
        
        # Verify all files were created successfully
        for path in paths:
            assert temp_storage.file_exists(path)
        
        # Verify no file corruption or conflicts
        session_files = temp_storage.get_session_files(session_id)
        assert len(session_files) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
