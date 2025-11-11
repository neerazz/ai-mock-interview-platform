"""
Video Handler for video stream capture and recording.

This module provides the VideoHandler class for capturing and storing
video streams during interview sessions.
"""

from datetime import datetime
from typing import Optional, Dict, Any

from src.exceptions import CommunicationError


class VideoHandler:
    """
    Handles video recording and storage.
    
    Captures video streams and stores them to the local filesystem
    with references in the database.
    """

    def __init__(
        self,
        file_storage,
        data_store=None,
        logger=None,
        fps: int = 30,
        resolution: str = "1280x720",
        video_format: str = "webm"
    ):
        """
        Initialize video handler.
        
        Args:
            file_storage: FileStorage instance for saving video files
            data_store: Optional IDataStore instance for saving file references
            logger: LoggingManager instance for logging
            fps: Frames per second for video recording (default: 30)
            resolution: Video resolution as "WIDTHxHEIGHT" (default: 1280x720)
            video_format: Video file format (default: webm)
        """
        self.file_storage = file_storage
        self.data_store = data_store
        self.logger = logger
        self.fps = fps
        self.resolution = resolution
        self.video_format = video_format
        
        # Parse resolution
        try:
            width, height = resolution.split('x')
            self.width = int(width)
            self.height = int(height)
        except (ValueError, AttributeError):
            self.width = 1280
            self.height = 720
        
        # Track active recordings
        self._active_recordings = {}
        
        if self.logger:
            self.logger.info(
                component="VideoHandler",
                operation="initialize",
                message="Video handler initialized",
                metadata={
                    "fps": fps,
                    "resolution": resolution,
                    "format": video_format
                }
            )

    def capture_video(
        self,
        session_id: str,
        video_data: bytes,
        duration_seconds: Optional[float] = None,
        codec: str = "h264"
    ) -> str:
        """
        Capture and save video stream.
        
        Args:
            session_id: Session identifier
            video_data: Video data as bytes
            duration_seconds: Optional duration of video in seconds
            codec: Video codec used (default: h264)
            
        Returns:
            Relative file path to saved video file
            
        Raises:
            CommunicationError: If video capture fails
        """
        try:
            if self.logger:
                self.logger.debug(
                    component="VideoHandler",
                    operation="capture_video",
                    message=f"Capturing video for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "video_size_bytes": len(video_data),
                        "duration_seconds": duration_seconds,
                        "codec": codec
                    }
                )
            
            # Prepare metadata
            metadata = {
                "fps": self.fps,
                "resolution": self.resolution,
                "width": self.width,
                "height": self.height,
                "codec": codec
            }
            if duration_seconds:
                metadata["duration_seconds"] = duration_seconds
            
            # Save video file
            file_path = self.file_storage.save_video(
                session_id=session_id,
                video_data=video_data,
                format=self.video_format,
                metadata=metadata
            )
            
            if self.logger:
                self.logger.info(
                    component="VideoHandler",
                    operation="capture_video",
                    message=f"Video captured successfully for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_path": file_path,
                        "duration_seconds": duration_seconds,
                        "size_bytes": len(video_data)
                    }
                )
            
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to capture video for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="VideoHandler",
                    operation="capture_video",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def start_recording(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Start video recording for a session.
        
        Args:
            session_id: Session identifier
            metadata: Optional metadata for the recording
        """
        self._active_recordings[session_id] = {
            "start_time": datetime.now(),
            "chunks": [],
            "metadata": metadata or {}
        }
        
        if self.logger:
            self.logger.info(
                component="VideoHandler",
                operation="start_recording",
                message=f"Started video recording for session {session_id}",
                session_id=session_id,
                metadata=metadata or {}
            )

    def stop_recording(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Stop video recording for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Recording metadata or None if not recording
        """
        if session_id not in self._active_recordings:
            if self.logger:
                self.logger.warning(
                    component="VideoHandler",
                    operation="stop_recording",
                    message=f"No active recording for session {session_id}",
                    session_id=session_id
                )
            return None
        
        recording_data = self._active_recordings.pop(session_id)
        duration = (datetime.now() - recording_data["start_time"]).total_seconds()
        
        result = {
            "duration_seconds": duration,
            "chunk_count": len(recording_data["chunks"]),
            "metadata": recording_data["metadata"]
        }
        
        if self.logger:
            self.logger.info(
                component="VideoHandler",
                operation="stop_recording",
                message=f"Stopped video recording for session {session_id}",
                session_id=session_id,
                metadata=result
            )
        
        return result

    def is_recording(self, session_id: str) -> bool:
        """
        Check if video recording is active for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if recording is active, False otherwise
        """
        return session_id in self._active_recordings

    def add_video_chunk(self, session_id: str, chunk_data: bytes) -> None:
        """
        Add a video chunk to an active recording.
        
        Args:
            session_id: Session identifier
            chunk_data: Video chunk data as bytes
        """
        if session_id not in self._active_recordings:
            if self.logger:
                self.logger.warning(
                    component="VideoHandler",
                    operation="add_video_chunk",
                    message=f"No active recording for session {session_id}",
                    session_id=session_id
                )
            return
        
        self._active_recordings[session_id]["chunks"].append({
            "timestamp": datetime.now(),
            "size_bytes": len(chunk_data),
            "data": chunk_data
        })
        
        if self.logger:
            self.logger.debug(
                component="VideoHandler",
                operation="add_video_chunk",
                message=f"Added video chunk for session {session_id}",
                session_id=session_id,
                metadata={
                    "chunk_size_bytes": len(chunk_data),
                    "total_chunks": len(self._active_recordings[session_id]["chunks"])
                }
            )

    def get_recording_duration(self, session_id: str) -> Optional[float]:
        """
        Get current recording duration for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Duration in seconds or None if not recording
        """
        if session_id not in self._active_recordings:
            return None
        
        start_time = self._active_recordings[session_id]["start_time"]
        duration = (datetime.now() - start_time).total_seconds()
        return duration

    def save_recording(self, session_id: str) -> Optional[str]:
        """
        Save the complete recording for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            File path to saved video or None if no recording
            
        Raises:
            CommunicationError: If saving fails
        """
        if session_id not in self._active_recordings:
            return None
        
        try:
            recording_data = self._active_recordings[session_id]
            
            # Combine all chunks
            video_data = b''.join([chunk["data"] for chunk in recording_data["chunks"]])
            
            # Calculate duration
            duration = (datetime.now() - recording_data["start_time"]).total_seconds()
            
            # Save video
            file_path = self.capture_video(
                session_id=session_id,
                video_data=video_data,
                duration_seconds=duration
            )
            
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to save recording for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="VideoHandler",
                    operation="save_recording",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)
