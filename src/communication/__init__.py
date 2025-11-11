"""
Communication module for handling multiple input/output modes.

This module provides components for managing audio, video, whiteboard,
screen share, and transcript functionality during interview sessions.
"""

from src.communication.communication_manager import CommunicationManager
from src.communication.audio_handler import AudioHandler
from src.communication.video_handler import VideoHandler
from src.communication.whiteboard_handler import WhiteboardHandler
from src.communication.screen_handler import ScreenShareHandler
from src.communication.transcript_handler import TranscriptHandler, TranscriptEntry

__all__ = [
    "CommunicationManager",
    "AudioHandler",
    "VideoHandler",
    "WhiteboardHandler",
    "ScreenShareHandler",
    "TranscriptHandler",
    "TranscriptEntry"
]
