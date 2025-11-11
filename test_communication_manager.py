"""
Tests for Communication Manager and handlers.

This module tests the core functionality of the communication manager
and its associated handlers.
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

from src.communication.communication_manager import CommunicationManager
from src.communication.audio_handler import AudioHandler
from src.communication.video_handler import VideoHandler
from src.communication.whiteboard_handler import WhiteboardHandler
from src.communication.screen_handler import ScreenShareHandler
from src.communication.transcript_handler import TranscriptHandler, TranscriptEntry
from src.storage.file_storage import FileStorage
from src.models import CommunicationMode
from src.exceptions import CommunicationError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def file_storage(temp_dir):
    """Create a FileStorage instance for testing."""
    return FileStorage(base_dir=temp_dir)


class TestCommunicationManager:
    """Tests for CommunicationManager class."""

    def test_initialization(self, file_storage):
        """Test communication manager initialization."""
        manager = CommunicationManager(file_storage=file_storage)
        assert manager.file_storage == file_storage
        assert manager.get_enabled_modes() == []

    def test_enable_mode(self, file_storage):
        """Test enabling a communication mode."""
        manager = CommunicationManager(file_storage=file_storage)
        manager.enable_mode(CommunicationMode.TEXT)
        
        assert CommunicationMode.TEXT in manager.get_enabled_modes()
        assert manager.is_mode_enabled(CommunicationMode.TEXT)

    def test_disable_mode(self, file_storage):
        """Test disabling a communication mode."""
        manager = CommunicationManager(file_storage=file_storage)
        manager.enable_mode(CommunicationMode.TEXT)
        manager.disable_mode(CommunicationMode.TEXT)
        
        assert CommunicationMode.TEXT not in manager.get_enabled_modes()
        assert not manager.is_mode_enabled(CommunicationMode.TEXT)

    def test_enable_mode_twice(self, file_storage):
        """Test enabling the same mode twice."""
        manager = CommunicationManager(file_storage=file_storage)
        manager.enable_mode(CommunicationMode.TEXT)
        manager.enable_mode(CommunicationMode.TEXT)
        
        # Should only be enabled once
        enabled_modes = manager.get_enabled_modes()
        assert enabled_modes.count(CommunicationMode.TEXT) == 1

    def test_multiple_modes(self, file_storage):
        """Test enabling multiple communication modes."""
        manager = CommunicationManager(file_storage=file_storage)
        
        # Set up handlers for the modes we want to enable
        whiteboard_handler = WhiteboardHandler(file_storage=file_storage)
        manager.set_whiteboard_handler(whiteboard_handler)
        
        manager.enable_mode(CommunicationMode.TEXT)
        manager.enable_mode(CommunicationMode.WHITEBOARD)
        
        enabled_modes = manager.get_enabled_modes()
        assert len(enabled_modes) == 2
        assert CommunicationMode.TEXT in enabled_modes
        assert CommunicationMode.WHITEBOARD in enabled_modes


class TestAudioHandler:
    """Tests for AudioHandler class."""

    def test_initialization(self, file_storage):
        """Test audio handler initialization."""
        handler = AudioHandler(file_storage=file_storage)
        assert handler.file_storage == file_storage
        assert handler.sample_rate == 16000
        assert handler.channels == 1

    def test_record_audio(self, file_storage):
        """Test audio recording."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "test-session-1"
        audio_data = b"mock audio data"
        
        file_path = handler.record_audio(
            session_id=session_id,
            audio_data=audio_data,
            duration_seconds=5.0
        )
        
        assert file_path is not None
        assert "audio" in file_path
        assert file_storage.file_exists(file_path)

    def test_start_stop_recording(self, file_storage):
        """Test recording state management."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "test-session-2"
        
        # Start recording
        handler.start_recording(session_id)
        assert handler.is_recording(session_id)
        
        # Stop recording
        metadata = handler.stop_recording(session_id)
        assert not handler.is_recording(session_id)
        assert metadata is not None
        assert "duration_seconds" in metadata


class TestVideoHandler:
    """Tests for VideoHandler class."""

    def test_initialization(self, file_storage):
        """Test video handler initialization."""
        handler = VideoHandler(file_storage=file_storage)
        assert handler.file_storage == file_storage
        assert handler.fps == 30
        assert handler.width == 1280
        assert handler.height == 720

    def test_capture_video(self, file_storage):
        """Test video capture."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "test-session-3"
        video_data = b"mock video data"
        
        file_path = handler.capture_video(
            session_id=session_id,
            video_data=video_data,
            duration_seconds=10.0
        )
        
        assert file_path is not None
        assert "video" in file_path
        assert file_storage.file_exists(file_path)

    def test_start_stop_recording(self, file_storage):
        """Test video recording state management."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "test-session-4"
        
        # Start recording
        handler.start_recording(session_id)
        assert handler.is_recording(session_id)
        
        # Stop recording
        metadata = handler.stop_recording(session_id)
        assert not handler.is_recording(session_id)
        assert metadata is not None


class TestWhiteboardHandler:
    """Tests for WhiteboardHandler class."""

    def test_initialization(self, file_storage):
        """Test whiteboard handler initialization."""
        handler = WhiteboardHandler(file_storage=file_storage)
        assert handler.file_storage == file_storage
        assert handler.canvas_width == 800
        assert handler.canvas_height == 600

    def test_save_whiteboard(self, file_storage):
        """Test whiteboard snapshot saving."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "test-session-5"
        canvas_data = b"mock canvas image data"
        
        file_path = handler.save_whiteboard(
            session_id=session_id,
            canvas_data=canvas_data,
            snapshot_number=1
        )
        
        assert file_path is not None
        assert "whiteboard" in file_path
        assert file_storage.file_exists(file_path)

    def test_snapshot_tracking(self, file_storage):
        """Test snapshot tracking."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "test-session-6"
        
        # Save multiple snapshots
        handler.save_whiteboard(session_id, b"snapshot 1")
        handler.save_whiteboard(session_id, b"snapshot 2")
        handler.save_whiteboard(session_id, b"snapshot 3")
        
        # Check count
        assert handler.get_snapshot_count(session_id) == 3
        
        # Get all snapshots
        snapshots = handler.get_snapshots(session_id)
        assert len(snapshots) == 3
        
        # Get latest
        latest = handler.get_latest_snapshot(session_id)
        assert latest == snapshots[-1]

    def test_get_canvas_config(self, file_storage):
        """Test canvas configuration retrieval."""
        handler = WhiteboardHandler(file_storage=file_storage)
        config = handler.get_canvas_config()
        
        assert config["width"] == 800
        assert config["height"] == 600
        assert "drawing_modes" in config


class TestScreenShareHandler:
    """Tests for ScreenShareHandler class."""

    def test_initialization(self, file_storage):
        """Test screen share handler initialization."""
        handler = ScreenShareHandler(file_storage=file_storage)
        assert handler.file_storage == file_storage
        assert handler.capture_interval_seconds == 5

    def test_capture_screen(self, file_storage):
        """Test screen capture."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "test-session-7"
        screen_data = b"mock screen capture data"
        
        file_path = handler.capture_screen(
            session_id=session_id,
            screen_data=screen_data,
            capture_number=1
        )
        
        assert file_path is not None
        assert "screen" in file_path
        assert file_storage.file_exists(file_path)

    def test_capture_tracking(self, file_storage):
        """Test capture tracking."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "test-session-8"
        
        # Capture multiple screens
        handler.capture_screen(session_id, b"capture 1")
        handler.capture_screen(session_id, b"capture 2")
        
        # Check count
        assert handler.get_capture_count(session_id) == 2
        
        # Get all captures
        captures = handler.get_captures(session_id)
        assert len(captures) == 2

    def test_start_stop_capture(self, file_storage):
        """Test capture state management."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "test-session-9"
        
        # Start capture
        handler.start_capture(session_id)
        assert handler.is_capturing(session_id)
        
        # Stop capture
        metadata = handler.stop_capture(session_id)
        assert not handler.is_capturing(session_id)
        assert metadata is not None


class TestTranscriptHandler:
    """Tests for TranscriptHandler class."""

    def test_initialization(self, file_storage):
        """Test transcript handler initialization."""
        handler = TranscriptHandler(file_storage=file_storage)
        assert handler.file_storage == file_storage

    def test_add_entry(self, file_storage):
        """Test adding transcript entries."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-10"
        
        entry = handler.add_entry(
            session_id=session_id,
            speaker="interviewer",
            text="What is your approach to system design?"
        )
        
        assert entry.speaker == "interviewer"
        assert "system design" in entry.text
        assert handler.get_entry_count(session_id) == 1

    def test_get_transcript(self, file_storage):
        """Test retrieving complete transcript."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-11"
        
        handler.add_entry(session_id, "interviewer", "Question 1")
        handler.add_entry(session_id, "candidate", "Answer 1")
        handler.add_entry(session_id, "interviewer", "Question 2")
        
        transcript = handler.get_transcript(session_id)
        assert len(transcript) == 3
        assert transcript[0].speaker == "interviewer"
        assert transcript[1].speaker == "candidate"

    def test_search_transcript(self, file_storage):
        """Test transcript search functionality."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-12"
        
        handler.add_entry(session_id, "interviewer", "Tell me about scaling systems")
        handler.add_entry(session_id, "candidate", "I use load balancing")
        handler.add_entry(session_id, "interviewer", "What about caching?")
        
        # Search for "scaling"
        results = handler.search_transcript(session_id, "scaling")
        assert len(results) == 1
        assert results[0].speaker == "interviewer"
        
        # Case-insensitive search
        results = handler.search_transcript(session_id, "LOAD", case_sensitive=False)
        assert len(results) == 1

    def test_filter_by_speaker(self, file_storage):
        """Test filtering by speaker."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-13"
        
        handler.add_entry(session_id, "interviewer", "Question 1")
        handler.add_entry(session_id, "candidate", "Answer 1")
        handler.add_entry(session_id, "interviewer", "Question 2")
        handler.add_entry(session_id, "candidate", "Answer 2")
        
        interviewer_entries = handler.filter_by_speaker(session_id, "interviewer")
        assert len(interviewer_entries) == 2
        
        candidate_entries = handler.filter_by_speaker(session_id, "candidate")
        assert len(candidate_entries) == 2

    def test_save_transcript_json(self, file_storage):
        """Test saving transcript in JSON format."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-14"
        
        handler.add_entry(session_id, "interviewer", "Question")
        handler.add_entry(session_id, "candidate", "Answer")
        
        file_path = handler.save_transcript(session_id, format="json")
        assert file_path is not None
        assert file_path.endswith(".json")

    def test_save_transcript_text(self, file_storage):
        """Test saving transcript in text format."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-15"
        
        handler.add_entry(session_id, "interviewer", "Question")
        handler.add_entry(session_id, "candidate", "Answer")
        
        file_path = handler.save_transcript(session_id, format="txt")
        assert file_path is not None
        assert file_path.endswith(".txt")

    def test_get_transcript_stats(self, file_storage):
        """Test transcript statistics."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-16"
        
        handler.add_entry(session_id, "interviewer", "What is your approach?")
        handler.add_entry(session_id, "candidate", "I focus on scalability and reliability.")
        
        stats = handler.get_transcript_stats(session_id)
        assert stats["entry_count"] == 2
        assert stats["total_words"] > 0
        assert stats["total_characters"] > 0
        assert "interviewer" in stats["speakers"]
        assert "candidate" in stats["speakers"]

    def test_clear_transcript(self, file_storage):
        """Test clearing transcript."""
        handler = TranscriptHandler(file_storage=file_storage)
        session_id = "test-session-17"
        
        handler.add_entry(session_id, "interviewer", "Question")
        assert handler.get_entry_count(session_id) == 1
        
        handler.clear_transcript(session_id)
        assert handler.get_entry_count(session_id) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
