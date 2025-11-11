"""
Audio Handler for real-time audio capture and transcription.

This module provides the AudioHandler class for capturing audio using
streamlit-webrtc and transcribing it using OpenAI Whisper.
"""

import io
import wave
from datetime import datetime
from typing import Optional, Callable
from pathlib import Path

from src.exceptions import CommunicationError


class AudioHandler:
    """
    Handles audio recording and transcription.
    
    Integrates with streamlit-webrtc for real-time audio capture
    and OpenAI Whisper for transcription.
    """

    def __init__(
        self,
        file_storage,
        whisper_client=None,
        logger=None,
        sample_rate: int = 16000,
        channels: int = 1,
        audio_format: str = "wav"
    ):
        """
        Initialize audio handler.
        
        Args:
            file_storage: FileStorage instance for saving audio files
            whisper_client: OpenAI Whisper client for transcription
            logger: LoggingManager instance for logging
            sample_rate: Audio sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            audio_format: Audio file format (default: wav)
        """
        self.file_storage = file_storage
        self.whisper_client = whisper_client
        self.logger = logger
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_format = audio_format
        
        # Track active recordings
        self._active_recordings = {}
        
        if self.logger:
            self.logger.info(
                component="AudioHandler",
                operation="initialize",
                message="Audio handler initialized",
                metadata={
                    "sample_rate": sample_rate,
                    "channels": channels,
                    "format": audio_format
                }
            )

    def record_audio(
        self,
        session_id: str,
        audio_data: bytes,
        duration_seconds: Optional[float] = None
    ) -> str:
        """
        Record and save audio data.
        
        Args:
            session_id: Session identifier
            audio_data: Raw audio data as bytes
            duration_seconds: Optional duration of audio in seconds
            
        Returns:
            Relative file path to saved audio file
            
        Raises:
            CommunicationError: If audio recording fails
        """
        try:
            if self.logger:
                self.logger.debug(
                    component="AudioHandler",
                    operation="record_audio",
                    message=f"Recording audio for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "audio_size_bytes": len(audio_data),
                        "duration_seconds": duration_seconds
                    }
                )
            
            # Convert raw audio data to WAV format
            wav_data = self._convert_to_wav(audio_data)
            
            # Save audio file
            metadata = {}
            if duration_seconds:
                metadata["duration_seconds"] = duration_seconds
            metadata["sample_rate"] = self.sample_rate
            metadata["channels"] = self.channels
            
            file_path = self.file_storage.save_audio(
                session_id=session_id,
                audio_data=wav_data,
                format=self.audio_format,
                metadata=metadata
            )
            
            if self.logger:
                self.logger.info(
                    component="AudioHandler",
                    operation="record_audio",
                    message=f"Audio recorded successfully for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_path": file_path,
                        "duration_seconds": duration_seconds
                    }
                )
            
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to record audio for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="AudioHandler",
                    operation="record_audio",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def transcribe_audio(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> str:
        """
        Transcribe audio file using OpenAI Whisper.
        
        Args:
            audio_file_path: Path to audio file
            language: Language code for transcription (default: en)
            
        Returns:
            Transcribed text
            
        Raises:
            CommunicationError: If transcription fails
        """
        if not self.whisper_client:
            raise CommunicationError("Whisper client not configured")
        
        try:
            if self.logger:
                self.logger.debug(
                    component="AudioHandler",
                    operation="transcribe_audio",
                    message=f"Transcribing audio file: {audio_file_path}",
                    metadata={"file_path": audio_file_path, "language": language}
                )
            
            start_time = datetime.now()
            
            # Get absolute file path
            abs_path = self.file_storage.get_file_path(audio_file_path)
            
            # Transcribe using Whisper
            with open(abs_path, "rb") as audio_file:
                transcript = self.whisper_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            transcribed_text = transcript.text
            
            # Calculate transcription time
            transcription_time = (datetime.now() - start_time).total_seconds()
            
            if self.logger:
                self.logger.info(
                    component="AudioHandler",
                    operation="transcribe_audio",
                    message=f"Audio transcribed successfully",
                    metadata={
                        "file_path": audio_file_path,
                        "transcription_time_seconds": transcription_time,
                        "text_length": len(transcribed_text)
                    }
                )
            
            return transcribed_text
            
        except Exception as e:
            error_msg = f"Failed to transcribe audio {audio_file_path}: {e}"
            if self.logger:
                self.logger.error(
                    component="AudioHandler",
                    operation="transcribe_audio",
                    message=error_msg,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def save_transcript(
        self,
        session_id: str,
        transcript_text: str,
        audio_file_path: str
    ) -> str:
        """
        Save transcript text to filesystem.
        
        Args:
            session_id: Session identifier
            transcript_text: Transcribed text
            audio_file_path: Path to corresponding audio file
            
        Returns:
            Relative file path to saved transcript
            
        Raises:
            CommunicationError: If saving transcript fails
        """
        try:
            # Create transcript filename based on audio filename
            audio_path = Path(audio_file_path)
            transcript_filename = audio_path.stem + "_transcript.txt"
            
            # Get session directory
            session_dir = self.file_storage.base_dir / session_id / "audio"
            transcript_path = session_dir / transcript_filename
            
            # Write transcript
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            
            # Calculate relative path
            relative_path = str(transcript_path.relative_to(self.file_storage.base_dir))
            
            if self.logger:
                self.logger.info(
                    component="AudioHandler",
                    operation="save_transcript",
                    message=f"Transcript saved for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "transcript_path": relative_path,
                        "audio_path": audio_file_path,
                        "text_length": len(transcript_text)
                    }
                )
            
            return relative_path
            
        except Exception as e:
            error_msg = f"Failed to save transcript for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="AudioHandler",
                    operation="save_transcript",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def record_and_transcribe(
        self,
        session_id: str,
        audio_data: bytes,
        duration_seconds: Optional[float] = None,
        language: str = "en",
        on_transcription_complete: Optional[Callable[[str], None]] = None
    ) -> tuple[str, str]:
        """
        Record audio and transcribe it in one operation.
        
        Args:
            session_id: Session identifier
            audio_data: Raw audio data as bytes
            duration_seconds: Optional duration of audio in seconds
            language: Language code for transcription
            on_transcription_complete: Optional callback with transcribed text
            
        Returns:
            Tuple of (audio_file_path, transcribed_text)
            
        Raises:
            CommunicationError: If recording or transcription fails
        """
        try:
            # Record audio
            audio_file_path = self.record_audio(
                session_id=session_id,
                audio_data=audio_data,
                duration_seconds=duration_seconds
            )
            
            # Transcribe audio
            transcribed_text = self.transcribe_audio(
                audio_file_path=audio_file_path,
                language=language
            )
            
            # Save transcript
            self.save_transcript(
                session_id=session_id,
                transcript_text=transcribed_text,
                audio_file_path=audio_file_path
            )
            
            # Call callback if provided
            if on_transcription_complete:
                on_transcription_complete(transcribed_text)
            
            return audio_file_path, transcribed_text
            
        except Exception as e:
            error_msg = f"Failed to record and transcribe audio: {e}"
            if self.logger:
                self.logger.error(
                    component="AudioHandler",
                    operation="record_and_transcribe",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def _convert_to_wav(self, audio_data: bytes) -> bytes:
        """
        Convert raw audio data to WAV format.
        
        Args:
            audio_data: Raw audio data as bytes
            
        Returns:
            WAV formatted audio data
        """
        try:
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            
            wav_buffer.seek(0)
            return wav_buffer.read()
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="AudioHandler",
                    operation="_convert_to_wav",
                    message=f"Failed to convert audio to WAV: {e}",
                    exc_info=e
                )
            # If conversion fails, return original data
            return audio_data

    def start_recording(self, session_id: str) -> None:
        """
        Mark recording as started for a session.
        
        Args:
            session_id: Session identifier
        """
        self._active_recordings[session_id] = {
            "start_time": datetime.now(),
            "chunks": []
        }
        
        if self.logger:
            self.logger.info(
                component="AudioHandler",
                operation="start_recording",
                message=f"Started audio recording for session {session_id}",
                session_id=session_id
            )

    def stop_recording(self, session_id: str) -> Optional[dict]:
        """
        Mark recording as stopped for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Recording metadata or None if not recording
        """
        if session_id not in self._active_recordings:
            return None
        
        recording_data = self._active_recordings.pop(session_id)
        duration = (datetime.now() - recording_data["start_time"]).total_seconds()
        
        if self.logger:
            self.logger.info(
                component="AudioHandler",
                operation="stop_recording",
                message=f"Stopped audio recording for session {session_id}",
                session_id=session_id,
                metadata={"duration_seconds": duration}
            )
        
        return {
            "duration_seconds": duration,
            "chunk_count": len(recording_data["chunks"])
        }

    def is_recording(self, session_id: str) -> bool:
        """
        Check if recording is active for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if recording is active, False otherwise
        """
        return session_id in self._active_recordings
