"""
Test file storage functionality.

This test verifies that the FileStorage class can save and manage
media files correctly.
"""

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.storage import FileStorage


def test_file_storage_basic():
    """Test basic file storage operations."""
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize file storage
        storage = FileStorage(base_dir=temp_dir)
        
        # Test session ID
        session_id = "test-session-123"
        
        # Test save_audio
        audio_data = b"fake audio data"
        audio_path = storage.save_audio(
            session_id=session_id,
            audio_data=audio_data,
            format="wav",
            metadata={"duration": 10.5}
        )
        print(f"✓ Audio saved: {audio_path}")
        assert storage.file_exists(audio_path)
        
        # Test save_video
        video_data = b"fake video data"
        video_path = storage.save_video(
            session_id=session_id,
            video_data=video_data,
            format="mp4",
            metadata={"duration": 30.0, "resolution": "1920x1080"}
        )
        print(f"✓ Video saved: {video_path}")
        assert storage.file_exists(video_path)
        
        # Test save_whiteboard
        whiteboard_data = b"fake whiteboard image"
        whiteboard_path = storage.save_whiteboard(
            session_id=session_id,
            canvas_data=whiteboard_data,
            format="png",
            metadata={"snapshot_number": 1}
        )
        print(f"✓ Whiteboard saved: {whiteboard_path}")
        assert storage.file_exists(whiteboard_path)
        
        # Test save_screen_capture
        screen_data = b"fake screen capture"
        screen_path = storage.save_screen_capture(
            session_id=session_id,
            screen_data=screen_data,
            format="png",
            metadata={"capture_interval": 5}
        )
        print(f"✓ Screen capture saved: {screen_path}")
        assert storage.file_exists(screen_path)
        
        # Test get_session_files
        session_files = storage.get_session_files(session_id)
        print(f"✓ Found {len(session_files)} files for session")
        assert len(session_files) == 4
        
        # Test get_storage_stats
        stats = storage.get_storage_stats()
        print(f"✓ Storage stats: {stats['file_count']} files, {stats['total_size_bytes']} bytes")
        assert stats['file_count'] == 4
        assert stats['session_count'] == 1
        
        # Test cleanup_session
        storage.cleanup_session(session_id)
        print(f"✓ Session cleaned up")
        session_files_after = storage.get_session_files(session_id)
        assert len(session_files_after) == 0
        
        print("\n✅ All file storage tests passed!")
        
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_directory_structure():
    """Test that directory structure is created correctly."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        storage = FileStorage(base_dir=temp_dir)
        session_id = "test-session-456"
        
        # Save files of different types
        storage.save_audio(session_id, b"audio", format="wav")
        storage.save_video(session_id, b"video", format="mp4")
        storage.save_whiteboard(session_id, b"whiteboard", format="png")
        storage.save_screen_capture(session_id, b"screen", format="png")
        
        # Check directory structure
        session_dir = Path(temp_dir) / session_id
        assert session_dir.exists()
        assert (session_dir / "audio").exists()
        assert (session_dir / "video").exists()
        assert (session_dir / "whiteboard").exists()
        assert (session_dir / "screen").exists()
        
        print("✅ Directory structure test passed!")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("Testing FileStorage implementation...\n")
    test_file_storage_basic()
    print()
    test_directory_structure()
