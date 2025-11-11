"""
File storage system for managing media files.

This module provides the FileStorage class for organizing and storing
audio, video, whiteboard, and screen capture files by session.
"""

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

from src.models import MediaFile
from src.exceptions import FileStorageError


class FileStorage:
    """
    File storage manager for session media files.
    
    Organizes files by session ID and provides methods for saving
    audio, video, whiteboard snapshots, and screen captures.
    """

    def __init__(self, base_dir: str, data_store=None, logger=None):
        """
        Initialize file storage.
        
        Args:
            base_dir: Base directory for file storage
            data_store: Optional IDataStore instance for saving file references
            logger: Optional LoggingManager instance
        """
        self.base_dir = Path(base_dir)
        self.data_store = data_store
        self.logger = logger
        
        # Create base directory if it doesn't exist
        self._ensure_directory_exists(self.base_dir)
        
        if self.logger:
            self.logger.info(
                component="FileStorage",
                operation="initialize",
                message=f"File storage initialized at {self.base_dir}",
                metadata={"base_dir": str(self.base_dir)}
            )

    def _ensure_directory_exists(self, directory: Path) -> None:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory: Directory path to create
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            error_msg = f"Failed to create directory {directory}: {e}"
            if self.logger:
                self.logger.error(
                    component="FileStorage",
                    operation="ensure_directory_exists",
                    message=error_msg,
                    exc_info=e
                )
            raise FileStorageError(error_msg)

    def _get_session_directory(self, session_id: str) -> Path:
        """
        Get directory path for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to session directory
        """
        session_dir = self.base_dir / session_id
        self._ensure_directory_exists(session_dir)
        return session_dir

    def _save_file(
        self,
        session_id: str,
        file_data: bytes,
        file_type: str,
        file_extension: str,
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save file to filesystem and optionally store reference in database.
        
        Args:
            session_id: Session identifier
            file_data: File content as bytes
            file_type: Type of file (audio, video, whiteboard, screen)
            file_extension: File extension (e.g., 'wav', 'mp4', 'png')
            metadata: Optional metadata dictionary
            
        Returns:
            Relative file path
            
        Raises:
            FileStorageError: If file save fails
        """
        try:
            # Get session directory
            session_dir = self._get_session_directory(session_id)
            
            # Create subdirectory for file type
            type_dir = session_dir / file_type
            self._ensure_directory_exists(type_dir)
            
            # Generate filename with timestamp
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{file_type}_{timestamp_str}.{file_extension}"
            file_path = type_dir / filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Calculate relative path from base directory
            relative_path = str(file_path.relative_to(self.base_dir))
            
            if self.logger:
                self.logger.info(
                    component="FileStorage",
                    operation="save_file",
                    message=f"Saved {file_type} file for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_type": file_type,
                        "file_path": relative_path,
                        "file_size_bytes": file_size
                    }
                )
            
            # Save reference to database if data_store is available
            if self.data_store:
                media_file = MediaFile(
                    file_type=file_type,
                    file_path=relative_path,
                    timestamp=timestamp,
                    file_size_bytes=file_size,
                    metadata=metadata or {}
                )
                self.data_store.save_media_reference(session_id, media_file)
            
            return relative_path
            
        except Exception as e:
            error_msg = f"Failed to save {file_type} file for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="FileStorage",
                    operation="save_file",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise FileStorageError(error_msg)

    def save_audio(
        self,
        session_id: str,
        audio_data: bytes,
        format: str = "wav",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save audio recording.
        
        Args:
            session_id: Session identifier
            audio_data: Audio file content as bytes
            format: Audio format (default: wav)
            metadata: Optional metadata (e.g., duration, sample_rate)
            
        Returns:
            Relative file path
        """
        if self.logger:
            self.logger.debug(
                component="FileStorage",
                operation="save_audio",
                message=f"Saving audio file for session {session_id}",
                session_id=session_id,
                metadata={"format": format, "size_bytes": len(audio_data)}
            )
        
        return self._save_file(
            session_id=session_id,
            file_data=audio_data,
            file_type="audio",
            file_extension=format,
            metadata=metadata
        )

    def save_video(
        self,
        session_id: str,
        video_data: bytes,
        format: str = "mp4",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save video recording.
        
        Args:
            session_id: Session identifier
            video_data: Video file content as bytes
            format: Video format (default: mp4)
            metadata: Optional metadata (e.g., duration, resolution, codec)
            
        Returns:
            Relative file path
        """
        if self.logger:
            self.logger.debug(
                component="FileStorage",
                operation="save_video",
                message=f"Saving video file for session {session_id}",
                session_id=session_id,
                metadata={"format": format, "size_bytes": len(video_data)}
            )
        
        return self._save_file(
            session_id=session_id,
            file_data=video_data,
            file_type="video",
            file_extension=format,
            metadata=metadata
        )

    def save_whiteboard(
        self,
        session_id: str,
        canvas_data: bytes,
        format: str = "png",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save whiteboard canvas snapshot.
        
        Args:
            session_id: Session identifier
            canvas_data: Canvas image data as bytes
            format: Image format (default: png)
            metadata: Optional metadata (e.g., dimensions, snapshot_number)
            
        Returns:
            Relative file path
        """
        if self.logger:
            self.logger.debug(
                component="FileStorage",
                operation="save_whiteboard",
                message=f"Saving whiteboard snapshot for session {session_id}",
                session_id=session_id,
                metadata={"format": format, "size_bytes": len(canvas_data)}
            )
        
        return self._save_file(
            session_id=session_id,
            file_data=canvas_data,
            file_type="whiteboard",
            file_extension=format,
            metadata=metadata
        )

    def save_screen_capture(
        self,
        session_id: str,
        screen_data: bytes,
        format: str = "png",
        metadata: Optional[dict] = None
    ) -> str:
        """
        Save screen share capture.
        
        Args:
            session_id: Session identifier
            screen_data: Screen capture image data as bytes
            format: Image format (default: png)
            metadata: Optional metadata (e.g., dimensions, capture_interval)
            
        Returns:
            Relative file path
        """
        if self.logger:
            self.logger.debug(
                component="FileStorage",
                operation="save_screen_capture",
                message=f"Saving screen capture for session {session_id}",
                session_id=session_id,
                metadata={"format": format, "size_bytes": len(screen_data)}
            )
        
        return self._save_file(
            session_id=session_id,
            file_data=screen_data,
            file_type="screen",
            file_extension=format,
            metadata=metadata
        )

    def get_file_path(self, relative_path: str) -> Path:
        """
        Get absolute file path from relative path.
        
        Args:
            relative_path: Relative path from base directory
            
        Returns:
            Absolute file path
        """
        return self.base_dir / relative_path

    def file_exists(self, relative_path: str) -> bool:
        """
        Check if file exists.
        
        Args:
            relative_path: Relative path from base directory
            
        Returns:
            True if file exists, False otherwise
        """
        file_path = self.get_file_path(relative_path)
        return file_path.exists() and file_path.is_file()

    def get_session_files(self, session_id: str) -> List[Path]:
        """
        Get all files for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of file paths
        """
        session_dir = self.base_dir / session_id
        if not session_dir.exists():
            return []
        
        files = []
        for root, _, filenames in os.walk(session_dir):
            for filename in filenames:
                files.append(Path(root) / filename)
        
        return files

    def cleanup_session(self, session_id: str) -> None:
        """
        Remove all files for a session.
        
        Args:
            session_id: Session identifier
        """
        session_dir = self.base_dir / session_id
        
        if not session_dir.exists():
            if self.logger:
                self.logger.warning(
                    component="FileStorage",
                    operation="cleanup_session",
                    message=f"Session directory does not exist: {session_id}",
                    session_id=session_id
                )
            return
        
        try:
            shutil.rmtree(session_dir)
            if self.logger:
                self.logger.info(
                    component="FileStorage",
                    operation="cleanup_session",
                    message=f"Cleaned up session directory for {session_id}",
                    session_id=session_id
                )
        except Exception as e:
            error_msg = f"Failed to cleanup session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="FileStorage",
                    operation="cleanup_session",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise FileStorageError(error_msg)

    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Remove session directories older than specified days.
        
        Args:
            days_old: Number of days to keep sessions (default: 30)
            
        Returns:
            Number of sessions cleaned up
        """
        if self.logger:
            self.logger.info(
                component="FileStorage",
                operation="cleanup_old_sessions",
                message=f"Starting cleanup of sessions older than {days_old} days",
                metadata={"days_old": days_old}
            )
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        cleaned_count = 0
        
        try:
            for session_dir in self.base_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                
                # Check directory modification time
                dir_mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
                
                if dir_mtime < cutoff_time:
                    try:
                        shutil.rmtree(session_dir)
                        cleaned_count += 1
                        if self.logger:
                            self.logger.info(
                                component="FileStorage",
                                operation="cleanup_old_sessions",
                                message=f"Cleaned up old session: {session_dir.name}",
                                metadata={
                                    "session_id": session_dir.name,
                                    "last_modified": dir_mtime.isoformat()
                                }
                            )
                    except Exception as e:
                        if self.logger:
                            self.logger.error(
                                component="FileStorage",
                                operation="cleanup_old_sessions",
                                message=f"Failed to cleanup session {session_dir.name}",
                                exc_info=e
                            )
            
            if self.logger:
                self.logger.info(
                    component="FileStorage",
                    operation="cleanup_old_sessions",
                    message=f"Cleanup completed: {cleaned_count} sessions removed",
                    metadata={"cleaned_count": cleaned_count}
                )
            
            return cleaned_count
            
        except Exception as e:
            error_msg = f"Failed to cleanup old sessions: {e}"
            if self.logger:
                self.logger.error(
                    component="FileStorage",
                    operation="cleanup_old_sessions",
                    message=error_msg,
                    exc_info=e
                )
            raise FileStorageError(error_msg)

    def get_storage_stats(self) -> dict:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        total_size = 0
        file_count = 0
        session_count = 0
        
        try:
            for session_dir in self.base_dir.iterdir():
                if not session_dir.is_dir():
                    continue
                
                session_count += 1
                
                for root, _, filenames in os.walk(session_dir):
                    for filename in filenames:
                        file_path = Path(root) / filename
                        total_size += file_path.stat().st_size
                        file_count += 1
            
            stats = {
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "session_count": session_count,
                "base_dir": str(self.base_dir)
            }
            
            if self.logger:
                self.logger.debug(
                    component="FileStorage",
                    operation="get_storage_stats",
                    message="Retrieved storage statistics",
                    metadata=stats
                )
            
            return stats
            
        except Exception as e:
            error_msg = f"Failed to get storage statistics: {e}"
            if self.logger:
                self.logger.error(
                    component="FileStorage",
                    operation="get_storage_stats",
                    message=error_msg,
                    exc_info=e
                )
            raise FileStorageError(error_msg)
