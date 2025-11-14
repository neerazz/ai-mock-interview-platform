"""
Unit tests for communication handlers.

This module provides comprehensive tests for audio, video, whiteboard,
and screen share handlers, focusing on core functionality and edge cases.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.communication.audio_handler import AudioHandler
from src.communication.video_handler import VideoHandler
from src.communication.whiteboard_handler import WhiteboardHandler
from src.communication.screen_handler import ScreenShareHandler
from src.storage.file_storage import FileStorage
from src.exceptions import CommunicationError


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def file_storage(temp_dir):
    """Create a FileStorage instance for testing."""
    return FileStorage(base_dir=temp_dir)


class TestAudioHandlerCore:
    """Core tests for AudioHandler functionality."""

    def test_audio_handler_initialization(self, file_storage):
        """Test audio handler initializes with correct defaults."""
        handler = AudioHandler(file_storage=file_storage)
        
        assert handler.file_storage == file_storage
        assert handler.sample_rate == 16000
        assert handler.channels == 1
        assert handler.audio_format == "wav"

    def test_audio_handler_custom_config(self, file_storage):
        """Test audio handler with custom configuration."""
        handler = AudioHandler(
            file_storage=file_storage,
            sample_rate=44100,
            channels=2,
            audio_format="mp3"
        )
        
        assert handler.sample_rate == 44100
        assert handler.channels == 2
        assert handler.audio_format == "mp3"

    def test_record_audio_basic(self, file_storage):
        """Test basic audio recording."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "audio-test-001"
        audio_data = b"test audio data content"
        
        file_path = handler.record_audio(
            session_id=session_id,
            audio_data=audio_data
        )
        
        assert file_path is not None
        assert isinstance(file_path, str)
        assert "audio" in file_path
        assert file_storage.file_exists(file_path)

    def test_record_audio_with_duration(self, file_storage):
        """Test audio recording with duration metadata."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "audio-test-002"
        audio_data = b"test audio with duration"
        duration = 15.5
        
        file_path = handler.record_audio(
            session_id=session_id,
            audio_data=audio_data,
            duration_seconds=duration
        )
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)

    def test_record_audio_empty_data(self, file_storage):
        """Test recording with empty audio data."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "audio-test-003"
        
        file_path = handler.record_audio(
            session_id=session_id,
            audio_data=b""
        )
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)

    def test_recording_state_management(self, file_storage):
        """Test recording state tracking."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "audio-test-004"
        
        # Initially not recording
        assert not handler.is_recording(session_id)
        
        # Start recording
        handler.start_recording(session_id)
        assert handler.is_recording(session_id)
        
        # Stop recording
        metadata = handler.stop_recording(session_id)
        assert not handler.is_recording(session_id)
        assert metadata is not None
        assert "duration_seconds" in metadata
        assert metadata["duration_seconds"] >= 0

    def test_stop_recording_not_started(self, file_storage):
        """Test stopping recording that was never started."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "audio-test-005"
        
        result = handler.stop_recording(session_id)
        assert result is None

    def test_multiple_recordings_same_session(self, file_storage):
        """Test multiple audio recordings for the same session."""
        handler = AudioHandler(file_storage=file_storage)
        session_id = "audio-test-006"
        
        # Record first audio
        path1 = handler.record_audio(session_id, b"audio 1")
        
        # Record second audio
        path2 = handler.record_audio(session_id, b"audio 2")
        
        # Both should exist and be different
        assert path1 != path2
        assert file_storage.file_exists(path1)
        assert file_storage.file_exists(path2)


class TestVideoHandlerCore:
    """Core tests for VideoHandler functionality."""

    def test_video_handler_initialization(self, file_storage):
        """Test video handler initializes with correct defaults."""
        handler = VideoHandler(file_storage=file_storage)
        
        assert handler.file_storage == file_storage
        assert handler.fps == 30
        assert handler.width == 1280
        assert handler.height == 720
        assert handler.video_format == "webm"

    def test_video_handler_custom_resolution(self, file_storage):
        """Test video handler with custom resolution."""
        handler = VideoHandler(
            file_storage=file_storage,
            resolution="1920x1080",
            fps=60
        )
        
        assert handler.width == 1920
        assert handler.height == 1080
        assert handler.fps == 60

    def test_capture_video_basic(self, file_storage):
        """Test basic video capture."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "video-test-001"
        video_data = b"test video data content"
        
        file_path = handler.capture_video(
            session_id=session_id,
            video_data=video_data
        )
        
        assert file_path is not None
        assert isinstance(file_path, str)
        assert "video" in file_path
        assert file_storage.file_exists(file_path)

    def test_capture_video_with_metadata(self, file_storage):
        """Test video capture with duration and codec."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "video-test-002"
        video_data = b"test video with metadata"
        
        file_path = handler.capture_video(
            session_id=session_id,
            video_data=video_data,
            duration_seconds=30.0,
            codec="vp9"
        )
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)

    def test_video_recording_state(self, file_storage):
        """Test video recording state management."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "video-test-003"
        
        # Initially not recording
        assert not handler.is_recording(session_id)
        
        # Start recording
        handler.start_recording(session_id)
        assert handler.is_recording(session_id)
        
        # Stop recording
        metadata = handler.stop_recording(session_id)
        assert not handler.is_recording(session_id)
        assert metadata is not None
        assert "duration_seconds" in metadata

    def test_video_chunk_management(self, file_storage):
        """Test adding video chunks to active recording."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "video-test-004"
        
        # Start recording
        handler.start_recording(session_id)
        
        # Add chunks
        handler.add_video_chunk(session_id, b"chunk 1")
        handler.add_video_chunk(session_id, b"chunk 2")
        handler.add_video_chunk(session_id, b"chunk 3")
        
        # Stop and check
        metadata = handler.stop_recording(session_id)
        assert metadata["chunk_count"] == 3

    def test_get_recording_duration(self, file_storage):
        """Test getting current recording duration."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "video-test-005"
        
        # No recording
        assert handler.get_recording_duration(session_id) is None
        
        # Start recording
        handler.start_recording(session_id)
        duration = handler.get_recording_duration(session_id)
        assert duration is not None
        assert duration >= 0

    def test_save_recording_with_chunks(self, file_storage):
        """Test saving a complete recording with chunks."""
        handler = VideoHandler(file_storage=file_storage)
        session_id = "video-test-006"
        
        # Start recording and add chunks
        handler.start_recording(session_id)
        handler.add_video_chunk(session_id, b"chunk 1")
        handler.add_video_chunk(session_id, b"chunk 2")
        
        # Save recording
        file_path = handler.save_recording(session_id)
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)


class TestWhiteboardHandlerCore:
    """Core tests for WhiteboardHandler functionality."""

    def test_whiteboard_handler_initialization(self, file_storage):
        """Test whiteboard handler initializes with correct defaults."""
        handler = WhiteboardHandler(file_storage=file_storage)
        
        assert handler.file_storage == file_storage
        assert handler.canvas_width == 800
        assert handler.canvas_height == 600
        assert handler.image_format == "png"

    def test_save_whiteboard_basic(self, file_storage):
        """Test basic whiteboard snapshot saving."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-001"
        canvas_data = b"test canvas image data"
        
        file_path = handler.save_whiteboard(
            session_id=session_id,
            canvas_data=canvas_data
        )
        
        assert file_path is not None
        assert isinstance(file_path, str)
        assert "whiteboard" in file_path
        assert file_storage.file_exists(file_path)

    def test_save_whiteboard_with_snapshot_number(self, file_storage):
        """Test saving whiteboard with snapshot number."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-002"
        
        file_path = handler.save_whiteboard(
            session_id=session_id,
            canvas_data=b"snapshot data",
            snapshot_number=5
        )
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)

    def test_snapshot_count_tracking(self, file_storage):
        """Test snapshot count tracking."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-003"
        
        # Initially zero
        assert handler.get_snapshot_count(session_id) == 0
        
        # Save snapshots
        handler.save_whiteboard(session_id, b"snapshot 1")
        assert handler.get_snapshot_count(session_id) == 1
        
        handler.save_whiteboard(session_id, b"snapshot 2")
        assert handler.get_snapshot_count(session_id) == 2
        
        handler.save_whiteboard(session_id, b"snapshot 3")
        assert handler.get_snapshot_count(session_id) == 3

    def test_get_snapshots_list(self, file_storage):
        """Test retrieving list of snapshots."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-004"
        
        # Save multiple snapshots
        path1 = handler.save_whiteboard(session_id, b"snapshot 1")
        path2 = handler.save_whiteboard(session_id, b"snapshot 2")
        path3 = handler.save_whiteboard(session_id, b"snapshot 3")
        
        snapshots = handler.get_snapshots(session_id)
        assert len(snapshots) == 3
        assert path1 in snapshots
        assert path2 in snapshots
        assert path3 in snapshots

    def test_get_latest_snapshot(self, file_storage):
        """Test getting the latest snapshot."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-005"
        
        # No snapshots
        assert handler.get_latest_snapshot(session_id) is None
        
        # Save snapshots
        handler.save_whiteboard(session_id, b"snapshot 1")
        handler.save_whiteboard(session_id, b"snapshot 2")
        path3 = handler.save_whiteboard(session_id, b"snapshot 3")
        
        latest = handler.get_latest_snapshot(session_id)
        assert latest == path3

    def test_clear_canvas(self, file_storage):
        """Test canvas clearing operation."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-006"
        
        # Clear canvas (logical operation)
        handler.clear_canvas(session_id)
        # Should not raise any errors

    def test_delete_snapshot(self, file_storage):
        """Test deleting a specific snapshot."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-007"
        
        # Save snapshots
        path1 = handler.save_whiteboard(session_id, b"snapshot 1")
        path2 = handler.save_whiteboard(session_id, b"snapshot 2")
        
        # Delete first snapshot
        result = handler.delete_snapshot(session_id, path1)
        assert result is True
        assert handler.get_snapshot_count(session_id) == 1
        
        # Verify it's gone
        snapshots = handler.get_snapshots(session_id)
        assert path1 not in snapshots
        assert path2 in snapshots

    def test_get_canvas_config(self, file_storage):
        """Test retrieving canvas configuration."""
        handler = WhiteboardHandler(file_storage=file_storage)
        config = handler.get_canvas_config()
        
        assert config["width"] == 800
        assert config["height"] == 600
        assert config["format"] == "png"
        assert "drawing_modes" in config
        assert isinstance(config["drawing_modes"], list)

    def test_auto_save_snapshot(self, file_storage):
        """Test auto-save functionality."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-008"
        
        file_path = handler.auto_save_snapshot(
            session_id=session_id,
            canvas_data=b"auto-saved snapshot",
            interval_seconds=60
        )
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)
        assert handler.get_snapshot_count(session_id) == 1

    def test_export_snapshots(self, file_storage, temp_dir):
        """Test exporting snapshots to directory."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-009"
        
        # Save snapshots
        handler.save_whiteboard(session_id, b"snapshot 1")
        handler.save_whiteboard(session_id, b"snapshot 2")
        handler.save_whiteboard(session_id, b"snapshot 3")
        
        # Export
        export_dir = Path(temp_dir) / "exports"
        exported_files = handler.export_snapshots(session_id, str(export_dir))
        
        assert len(exported_files) == 3
        for file_path in exported_files:
            assert Path(file_path).exists()

    def test_export_snapshots_empty(self, file_storage):
        """Test exporting when no snapshots exist."""
        handler = WhiteboardHandler(file_storage=file_storage)
        session_id = "whiteboard-test-010"
        
        exported_files = handler.export_snapshots(session_id)
        assert len(exported_files) == 0


class TestScreenShareHandlerCore:
    """Core tests for ScreenShareHandler functionality."""

    def test_screen_handler_initialization(self, file_storage):
        """Test screen share handler initializes with correct defaults."""
        handler = ScreenShareHandler(file_storage=file_storage)
        
        assert handler.file_storage == file_storage
        assert handler.capture_interval_seconds == 5
        assert handler.image_format == "png"

    def test_capture_screen_basic(self, file_storage):
        """Test basic screen capture."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-001"
        screen_data = b"test screen capture data"
        
        file_path = handler.capture_screen(
            session_id=session_id,
            screen_data=screen_data
        )
        
        assert file_path is not None
        assert isinstance(file_path, str)
        assert "screen" in file_path
        assert file_storage.file_exists(file_path)

    def test_capture_screen_with_number(self, file_storage):
        """Test screen capture with capture number."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-002"
        
        file_path = handler.capture_screen(
            session_id=session_id,
            screen_data=b"capture data",
            capture_number=10
        )
        
        assert file_path is not None
        assert file_storage.file_exists(file_path)

    def test_capture_count_tracking(self, file_storage):
        """Test capture count tracking."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-003"
        
        # Initially zero
        assert handler.get_capture_count(session_id) == 0
        
        # Capture screens
        handler.capture_screen(session_id, b"capture 1")
        assert handler.get_capture_count(session_id) == 1
        
        handler.capture_screen(session_id, b"capture 2")
        assert handler.get_capture_count(session_id) == 2

    def test_capture_state_management(self, file_storage):
        """Test capture state management."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-004"
        
        # Initially not capturing
        assert not handler.is_capturing(session_id)
        
        # Start capture
        handler.start_capture(session_id)
        assert handler.is_capturing(session_id)
        
        # Stop capture
        metadata = handler.stop_capture(session_id)
        assert not handler.is_capturing(session_id)
        assert metadata is not None
        assert "duration_seconds" in metadata

    def test_get_captures_list(self, file_storage):
        """Test retrieving list of captures."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-005"
        
        # Capture multiple screens
        path1 = handler.capture_screen(session_id, b"capture 1")
        path2 = handler.capture_screen(session_id, b"capture 2")
        path3 = handler.capture_screen(session_id, b"capture 3")
        
        captures = handler.get_captures(session_id)
        assert len(captures) == 3
        assert path1 in captures
        assert path2 in captures
        assert path3 in captures

    def test_get_latest_capture(self, file_storage):
        """Test getting the latest capture."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-006"
        
        # No captures
        assert handler.get_latest_capture(session_id) is None
        
        # Capture screens
        handler.capture_screen(session_id, b"capture 1")
        handler.capture_screen(session_id, b"capture 2")
        path3 = handler.capture_screen(session_id, b"capture 3")
        
        latest = handler.get_latest_capture(session_id)
        assert latest == path3

    def test_get_capture_duration(self, file_storage):
        """Test getting capture duration."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-007"
        
        # No capture
        assert handler.get_capture_duration(session_id) is None
        
        # Start capture
        handler.start_capture(session_id)
        duration = handler.get_capture_duration(session_id)
        assert duration is not None
        assert duration >= 0

    def test_increment_capture_count(self, file_storage):
        """Test incrementing capture count."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-008"
        
        # Start capture
        handler.start_capture(session_id)
        
        # Increment count
        handler.increment_capture_count(session_id)
        handler.increment_capture_count(session_id)
        
        # Stop and check
        metadata = handler.stop_capture(session_id)
        assert metadata["capture_count"] == 2

    def test_delete_capture(self, file_storage):
        """Test deleting a specific capture."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-009"
        
        # Capture screens
        path1 = handler.capture_screen(session_id, b"capture 1")
        path2 = handler.capture_screen(session_id, b"capture 2")
        
        # Delete first capture
        result = handler.delete_capture(session_id, path1)
        assert result is True
        assert handler.get_capture_count(session_id) == 1
        
        # Verify it's gone
        captures = handler.get_captures(session_id)
        assert path1 not in captures
        assert path2 in captures

    def test_export_captures(self, file_storage, temp_dir):
        """Test exporting captures to directory."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-010"
        
        # Capture screens
        handler.capture_screen(session_id, b"capture 1")
        handler.capture_screen(session_id, b"capture 2")
        
        # Export
        export_dir = Path(temp_dir) / "screen_exports"
        exported_files = handler.export_captures(session_id, str(export_dir))
        
        assert len(exported_files) == 2
        for file_path in exported_files:
            assert Path(file_path).exists()

    def test_get_capture_stats(self, file_storage):
        """Test getting capture statistics."""
        handler = ScreenShareHandler(file_storage=file_storage)
        session_id = "screen-test-011"
        
        # Capture screens
        handler.capture_screen(session_id, b"capture 1")
        handler.capture_screen(session_id, b"capture 2")
        
        stats = handler.get_capture_stats(session_id)
        assert stats["capture_count"] == 2
        assert stats["total_size_bytes"] > 0
        assert stats["capture_interval_seconds"] == 5
        assert not stats["is_capturing"]


class TestFileStorageIntegration:
    """Integration tests for file storage with handlers."""

    def test_multiple_handlers_same_session(self, file_storage):
        """Test multiple handlers saving to the same session."""
        session_id = "integration-test-001"
        
        # Create handlers
        audio_handler = AudioHandler(file_storage=file_storage)
        video_handler = VideoHandler(file_storage=file_storage)
        whiteboard_handler = WhiteboardHandler(file_storage=file_storage)
        screen_handler = ScreenShareHandler(file_storage=file_storage)
        
        # Save files from each handler
        audio_path = audio_handler.record_audio(session_id, b"audio")
        video_path = video_handler.capture_video(session_id, b"video")
        whiteboard_path = whiteboard_handler.save_whiteboard(session_id, b"whiteboard")
        screen_path = screen_handler.capture_screen(session_id, b"screen")
        
        # Verify all files exist
        assert file_storage.file_exists(audio_path)
        assert file_storage.file_exists(video_path)
        assert file_storage.file_exists(whiteboard_path)
        assert file_storage.file_exists(screen_path)
        
        # Check session files
        session_files = file_storage.get_session_files(session_id)
        assert len(session_files) == 4

    def test_session_cleanup_removes_all_files(self, file_storage):
        """Test that session cleanup removes all handler files."""
        session_id = "integration-test-002"
        
        # Create handlers and save files
        audio_handler = AudioHandler(file_storage=file_storage)
        whiteboard_handler = WhiteboardHandler(file_storage=file_storage)
        
        audio_handler.record_audio(session_id, b"audio")
        whiteboard_handler.save_whiteboard(session_id, b"whiteboard")
        
        # Verify files exist
        assert len(file_storage.get_session_files(session_id)) == 2
        
        # Cleanup session
        file_storage.cleanup_session(session_id)
        
        # Verify files are gone
        assert len(file_storage.get_session_files(session_id)) == 0

    def test_storage_stats_with_multiple_handlers(self, file_storage):
        """Test storage statistics with multiple handlers."""
        session_id = "integration-test-003"
        
        # Create handlers and save files
        audio_handler = AudioHandler(file_storage=file_storage)
        video_handler = VideoHandler(file_storage=file_storage)
        
        audio_handler.record_audio(session_id, b"audio data")
        video_handler.capture_video(session_id, b"video data")
        
        # Get stats
        stats = file_storage.get_storage_stats()
        assert stats["file_count"] == 2
        assert stats["session_count"] == 1
        assert stats["total_size_bytes"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
