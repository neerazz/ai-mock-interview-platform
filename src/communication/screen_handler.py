"""
Screen Share Handler for screen capture management.

This module provides the ScreenShareHandler class for capturing
screen content at regular intervals during interview sessions.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.exceptions import CommunicationError


class ScreenShareHandler:
    """
    Handles screen share capture and storage.
    
    Captures screen content at regular intervals (default: 5 seconds)
    and stores snapshots to the local filesystem.
    """

    def __init__(
        self,
        file_storage,
        logger=None,
        capture_interval_seconds: int = 5,
        image_format: str = "png"
    ):
        """
        Initialize screen share handler.
        
        Args:
            file_storage: FileStorage instance for saving screen captures
            logger: LoggingManager instance for logging
            capture_interval_seconds: Interval between captures (default: 5)
            image_format: Image format for captures (default: png)
        """
        self.file_storage = file_storage
        self.logger = logger
        self.capture_interval_seconds = capture_interval_seconds
        self.image_format = image_format
        
        # Track captures per session
        self._session_captures: Dict[str, List[str]] = {}
        self._active_captures: Dict[str, Dict[str, Any]] = {}
        
        if self.logger:
            self.logger.info(
                component="ScreenShareHandler",
                operation="initialize",
                message="Screen share handler initialized",
                metadata={
                    "capture_interval_seconds": capture_interval_seconds,
                    "format": image_format
                }
            )

    def capture_screen(
        self,
        session_id: str,
        screen_data: bytes,
        capture_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Capture and save screen content.
        
        Args:
            session_id: Session identifier
            screen_data: Screen capture image data as bytes
            capture_number: Optional capture number for ordering
            metadata: Optional metadata (e.g., timestamp, dimensions)
            
        Returns:
            Relative file path to saved screen capture
            
        Raises:
            CommunicationError: If screen capture fails
        """
        try:
            if self.logger:
                self.logger.debug(
                    component="ScreenShareHandler",
                    operation="capture_screen",
                    message=f"Capturing screen for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "screen_size_bytes": len(screen_data),
                        "capture_number": capture_number
                    }
                )
            
            # Prepare metadata
            save_metadata = {
                "timestamp": datetime.now().isoformat(),
                "capture_interval_seconds": self.capture_interval_seconds
            }
            if capture_number is not None:
                save_metadata["capture_number"] = capture_number
            if metadata:
                save_metadata.update(metadata)
            
            # Save screen capture
            file_path = self.file_storage.save_screen_capture(
                session_id=session_id,
                screen_data=screen_data,
                format=self.image_format,
                metadata=save_metadata
            )
            
            # Track capture for this session
            if session_id not in self._session_captures:
                self._session_captures[session_id] = []
            self._session_captures[session_id].append(file_path)
            
            if self.logger:
                self.logger.info(
                    component="ScreenShareHandler",
                    operation="capture_screen",
                    message=f"Screen captured for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_path": file_path,
                        "capture_count": len(self._session_captures[session_id])
                    }
                )
            
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to capture screen for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="ScreenShareHandler",
                    operation="capture_screen",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def start_capture(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Start screen capture for a session.
        
        Args:
            session_id: Session identifier
            metadata: Optional metadata for the capture session
        """
        self._active_captures[session_id] = {
            "start_time": datetime.now(),
            "capture_count": 0,
            "metadata": metadata or {}
        }
        
        if self.logger:
            self.logger.info(
                component="ScreenShareHandler",
                operation="start_capture",
                message=f"Started screen capture for session {session_id}",
                session_id=session_id,
                metadata={
                    "capture_interval_seconds": self.capture_interval_seconds
                }
            )

    def stop_capture(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Stop screen capture for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Capture session metadata or None if not capturing
        """
        if session_id not in self._active_captures:
            if self.logger:
                self.logger.warning(
                    component="ScreenShareHandler",
                    operation="stop_capture",
                    message=f"No active capture for session {session_id}",
                    session_id=session_id
                )
            return None
        
        capture_data = self._active_captures.pop(session_id)
        duration = (datetime.now() - capture_data["start_time"]).total_seconds()
        
        result = {
            "duration_seconds": duration,
            "capture_count": capture_data["capture_count"],
            "total_captures": len(self._session_captures.get(session_id, [])),
            "metadata": capture_data["metadata"]
        }
        
        if self.logger:
            self.logger.info(
                component="ScreenShareHandler",
                operation="stop_capture",
                message=f"Stopped screen capture for session {session_id}",
                session_id=session_id,
                metadata=result
            )
        
        return result

    def is_capturing(self, session_id: str) -> bool:
        """
        Check if screen capture is active for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if capturing is active, False otherwise
        """
        return session_id in self._active_captures

    def get_capture_count(self, session_id: str) -> int:
        """
        Get the number of screen captures for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of captures
        """
        return len(self._session_captures.get(session_id, []))

    def get_captures(self, session_id: str) -> List[str]:
        """
        Get all screen capture file paths for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of capture file paths
        """
        return self._session_captures.get(session_id, []).copy()

    def get_latest_capture(self, session_id: str) -> Optional[str]:
        """
        Get the most recent screen capture for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            File path to latest capture or None if no captures
        """
        captures = self._session_captures.get(session_id, [])
        return captures[-1] if captures else None

    def get_capture_duration(self, session_id: str) -> Optional[float]:
        """
        Get current capture session duration.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Duration in seconds or None if not capturing
        """
        if session_id not in self._active_captures:
            return None
        
        start_time = self._active_captures[session_id]["start_time"]
        duration = (datetime.now() - start_time).total_seconds()
        return duration

    def increment_capture_count(self, session_id: str) -> None:
        """
        Increment the capture count for an active session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._active_captures:
            self._active_captures[session_id]["capture_count"] += 1

    def delete_capture(self, session_id: str, file_path: str) -> bool:
        """
        Delete a specific screen capture.
        
        Args:
            session_id: Session identifier
            file_path: Path to capture file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if session_id not in self._session_captures:
                return False
            
            if file_path not in self._session_captures[session_id]:
                return False
            
            # Remove from tracking
            self._session_captures[session_id].remove(file_path)
            
            # Delete file from filesystem
            abs_path = self.file_storage.get_file_path(file_path)
            if abs_path.exists():
                abs_path.unlink()
            
            if self.logger:
                self.logger.info(
                    component="ScreenShareHandler",
                    operation="delete_capture",
                    message=f"Deleted screen capture for session {session_id}",
                    session_id=session_id,
                    metadata={"file_path": file_path}
                )
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="ScreenShareHandler",
                    operation="delete_capture",
                    message=f"Failed to delete capture: {e}",
                    session_id=session_id,
                    exc_info=e
                )
            return False

    def export_captures(
        self,
        session_id: str,
        export_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export all screen captures for a session to a directory.
        
        Args:
            session_id: Session identifier
            export_dir: Optional export directory (default: session directory)
            
        Returns:
            List of exported file paths
            
        Raises:
            CommunicationError: If export fails
        """
        try:
            captures = self.get_captures(session_id)
            
            if not captures:
                if self.logger:
                    self.logger.warning(
                        component="ScreenShareHandler",
                        operation="export_captures",
                        message=f"No captures to export for session {session_id}",
                        session_id=session_id
                    )
                return []
            
            # Determine export directory
            if export_dir:
                export_path = Path(export_dir)
            else:
                export_path = self.file_storage.base_dir / session_id / "screen_export"
            
            export_path.mkdir(parents=True, exist_ok=True)
            
            exported_files = []
            for i, capture_path in enumerate(captures, 1):
                # Copy capture to export directory
                src_path = self.file_storage.get_file_path(capture_path)
                dst_path = export_path / f"screen_capture_{i:03d}.{self.image_format}"
                
                if src_path.exists():
                    import shutil
                    shutil.copy2(src_path, dst_path)
                    exported_files.append(str(dst_path))
            
            if self.logger:
                self.logger.info(
                    component="ScreenShareHandler",
                    operation="export_captures",
                    message=f"Exported {len(exported_files)} captures for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "export_dir": str(export_path),
                        "capture_count": len(exported_files)
                    }
                )
            
            return exported_files
            
        except Exception as e:
            error_msg = f"Failed to export captures for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="ScreenShareHandler",
                    operation="export_captures",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def get_capture_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for screen captures in a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with capture statistics
        """
        captures = self.get_captures(session_id)
        
        total_size = 0
        for capture_path in captures:
            abs_path = self.file_storage.get_file_path(capture_path)
            if abs_path.exists():
                total_size += abs_path.stat().st_size
        
        stats = {
            "capture_count": len(captures),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "capture_interval_seconds": self.capture_interval_seconds,
            "is_capturing": self.is_capturing(session_id)
        }
        
        if self.is_capturing(session_id):
            stats["current_duration_seconds"] = self.get_capture_duration(session_id)
        
        return stats
