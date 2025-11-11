"""
Communication Manager for coordinating multiple communication modes.

This module provides the CommunicationManager class that coordinates
between audio, video, whiteboard, and screen share handlers.
"""

from typing import List, Optional, Dict, Any

from src.models import CommunicationMode
from src.exceptions import CommunicationError


class CommunicationManager:
    """
    Manages communication modes and coordinates between handlers.
    
    The CommunicationManager tracks which communication modes are enabled
    and coordinates between audio, video, whiteboard, and screen handlers.
    """

    def __init__(
        self,
        file_storage=None,
        logger=None,
        audio_handler=None,
        video_handler=None,
        whiteboard_handler=None,
        screen_handler=None,
        transcript_handler=None
    ):
        """
        Initialize communication manager.
        
        Args:
            file_storage: FileStorage instance for media file storage
            logger: LoggingManager instance for logging
            audio_handler: Optional AudioHandler instance
            video_handler: Optional VideoHandler instance
            whiteboard_handler: Optional WhiteboardHandler instance
            screen_handler: Optional ScreenShareHandler instance
            transcript_handler: Optional TranscriptHandler instance
        """
        self.file_storage = file_storage
        self.logger = logger
        
        # Initialize handlers (can be injected or created later)
        self.audio_handler = audio_handler
        self.video_handler = video_handler
        self.whiteboard_handler = whiteboard_handler
        self.screen_handler = screen_handler
        self.transcript_handler = transcript_handler
        
        # Track enabled modes
        self._enabled_modes: List[CommunicationMode] = []
        
        if self.logger:
            self.logger.info(
                component="CommunicationManager",
                operation="initialize",
                message="Communication manager initialized",
                metadata={"enabled_modes": []}
            )

    def enable_mode(self, mode: CommunicationMode) -> None:
        """
        Enable a communication mode.
        
        Args:
            mode: Communication mode to enable
            
        Raises:
            CommunicationError: If mode cannot be enabled
        """
        if mode in self._enabled_modes:
            if self.logger:
                self.logger.warning(
                    component="CommunicationManager",
                    operation="enable_mode",
                    message=f"Mode {mode.value} is already enabled",
                    metadata={"mode": mode.value}
                )
            return
        
        try:
            # Validate that handler exists for the mode
            handler = self._get_handler_for_mode(mode)
            if handler is None and mode != CommunicationMode.TEXT:
                raise CommunicationError(
                    f"No handler available for mode: {mode.value}"
                )
            
            self._enabled_modes.append(mode)
            
            if self.logger:
                self.logger.info(
                    component="CommunicationManager",
                    operation="enable_mode",
                    message=f"Enabled communication mode: {mode.value}",
                    metadata={
                        "mode": mode.value,
                        "enabled_modes": [m.value for m in self._enabled_modes]
                    }
                )
                
        except Exception as e:
            error_msg = f"Failed to enable mode {mode.value}: {e}"
            if self.logger:
                self.logger.error(
                    component="CommunicationManager",
                    operation="enable_mode",
                    message=error_msg,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def disable_mode(self, mode: CommunicationMode) -> None:
        """
        Disable a communication mode.
        
        Args:
            mode: Communication mode to disable
        """
        if mode not in self._enabled_modes:
            if self.logger:
                self.logger.warning(
                    component="CommunicationManager",
                    operation="disable_mode",
                    message=f"Mode {mode.value} is not enabled",
                    metadata={"mode": mode.value}
                )
            return
        
        try:
            self._enabled_modes.remove(mode)
            
            if self.logger:
                self.logger.info(
                    component="CommunicationManager",
                    operation="disable_mode",
                    message=f"Disabled communication mode: {mode.value}",
                    metadata={
                        "mode": mode.value,
                        "enabled_modes": [m.value for m in self._enabled_modes]
                    }
                )
                
        except Exception as e:
            error_msg = f"Failed to disable mode {mode.value}: {e}"
            if self.logger:
                self.logger.error(
                    component="CommunicationManager",
                    operation="disable_mode",
                    message=error_msg,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def get_enabled_modes(self) -> List[CommunicationMode]:
        """
        Get list of currently enabled communication modes.
        
        Returns:
            List of enabled communication modes
        """
        return self._enabled_modes.copy()

    def is_mode_enabled(self, mode: CommunicationMode) -> bool:
        """
        Check if a communication mode is enabled.
        
        Args:
            mode: Communication mode to check
            
        Returns:
            True if mode is enabled, False otherwise
        """
        return mode in self._enabled_modes

    def _get_handler_for_mode(self, mode: CommunicationMode) -> Optional[Any]:
        """
        Get the handler for a specific communication mode.
        
        Args:
            mode: Communication mode
            
        Returns:
            Handler instance or None if not available
        """
        handler_map = {
            CommunicationMode.AUDIO: self.audio_handler,
            CommunicationMode.VIDEO: self.video_handler,
            CommunicationMode.WHITEBOARD: self.whiteboard_handler,
            CommunicationMode.SCREEN_SHARE: self.screen_handler,
            CommunicationMode.TEXT: None  # Text mode doesn't need a handler
        }
        return handler_map.get(mode)

    def get_handler(self, mode: CommunicationMode) -> Optional[Any]:
        """
        Get the handler for a specific communication mode.
        
        Args:
            mode: Communication mode
            
        Returns:
            Handler instance or None if not available
        """
        return self._get_handler_for_mode(mode)

    def set_audio_handler(self, handler) -> None:
        """Set the audio handler."""
        self.audio_handler = handler

    def set_video_handler(self, handler) -> None:
        """Set the video handler."""
        self.video_handler = handler

    def set_whiteboard_handler(self, handler) -> None:
        """Set the whiteboard handler."""
        self.whiteboard_handler = handler

    def set_screen_handler(self, handler) -> None:
        """Set the screen share handler."""
        self.screen_handler = handler

    def set_transcript_handler(self, handler) -> None:
        """Set the transcript handler."""
        self.transcript_handler = handler
