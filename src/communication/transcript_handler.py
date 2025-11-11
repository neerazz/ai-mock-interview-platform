"""
Transcript Handler for real-time conversation transcript management.

This module provides the TranscriptHandler class for managing conversation
transcripts with timestamps, speaker labels, search, and export functionality.
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, asdict

from src.exceptions import CommunicationError


@dataclass
class TranscriptEntry:
    """
    Single entry in a conversation transcript.
    
    Attributes:
        timestamp: Entry timestamp
        speaker: Speaker label (interviewer or candidate)
        text: Transcript text content
        metadata: Additional metadata
    """
    timestamp: datetime
    speaker: str
    text: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with ISO format timestamp."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptEntry':
        """Create from dictionary with ISO format timestamp."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class TranscriptHandler:
    """
    Handles conversation transcript management.
    
    Provides real-time transcript display, storage, search, and export
    functionality for interview conversations.
    """

    def __init__(
        self,
        file_storage,
        logger=None
    ):
        """
        Initialize transcript handler.
        
        Args:
            file_storage: FileStorage instance for saving transcripts
            logger: LoggingManager instance for logging
        """
        self.file_storage = file_storage
        self.logger = logger
        
        # Track transcripts per session
        self._session_transcripts: Dict[str, List[TranscriptEntry]] = {}
        
        if self.logger:
            self.logger.info(
                component="TranscriptHandler",
                operation="initialize",
                message="Transcript handler initialized"
            )

    def add_entry(
        self,
        session_id: str,
        speaker: str,
        text: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TranscriptEntry:
        """
        Add an entry to the transcript.
        
        Args:
            session_id: Session identifier
            speaker: Speaker label (interviewer or candidate)
            text: Transcript text content
            timestamp: Optional timestamp (default: current time)
            metadata: Optional metadata
            
        Returns:
            Created transcript entry
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        entry = TranscriptEntry(
            timestamp=timestamp,
            speaker=speaker,
            text=text,
            metadata=metadata or {}
        )
        
        # Add to session transcript
        if session_id not in self._session_transcripts:
            self._session_transcripts[session_id] = []
        self._session_transcripts[session_id].append(entry)
        
        if self.logger:
            self.logger.debug(
                component="TranscriptHandler",
                operation="add_entry",
                message=f"Added transcript entry for session {session_id}",
                session_id=session_id,
                metadata={
                    "speaker": speaker,
                    "text_length": len(text),
                    "entry_count": len(self._session_transcripts[session_id])
                }
            )
        
        return entry

    def get_transcript(self, session_id: str) -> List[TranscriptEntry]:
        """
        Get complete transcript for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of transcript entries
        """
        return self._session_transcripts.get(session_id, []).copy()

    def get_recent_entries(
        self,
        session_id: str,
        count: int = 10
    ) -> List[TranscriptEntry]:
        """
        Get most recent transcript entries.
        
        Args:
            session_id: Session identifier
            count: Number of recent entries to retrieve
            
        Returns:
            List of recent transcript entries
        """
        transcript = self._session_transcripts.get(session_id, [])
        return transcript[-count:] if transcript else []

    def search_transcript(
        self,
        session_id: str,
        query: str,
        case_sensitive: bool = False
    ) -> List[TranscriptEntry]:
        """
        Search transcript for entries containing query text.
        
        Args:
            session_id: Session identifier
            query: Search query text
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            List of matching transcript entries
        """
        transcript = self._session_transcripts.get(session_id, [])
        
        if not query:
            return transcript.copy()
        
        matches = []
        search_query = query if case_sensitive else query.lower()
        
        for entry in transcript:
            search_text = entry.text if case_sensitive else entry.text.lower()
            if search_query in search_text:
                matches.append(entry)
        
        if self.logger:
            self.logger.debug(
                component="TranscriptHandler",
                operation="search_transcript",
                message=f"Searched transcript for session {session_id}",
                session_id=session_id,
                metadata={
                    "query": query,
                    "matches_found": len(matches),
                    "case_sensitive": case_sensitive
                }
            )
        
        return matches

    def filter_by_speaker(
        self,
        session_id: str,
        speaker: str
    ) -> List[TranscriptEntry]:
        """
        Filter transcript entries by speaker.
        
        Args:
            session_id: Session identifier
            speaker: Speaker label to filter by
            
        Returns:
            List of entries from specified speaker
        """
        transcript = self._session_transcripts.get(session_id, [])
        return [entry for entry in transcript if entry.speaker == speaker]

    def get_entry_count(self, session_id: str) -> int:
        """
        Get number of transcript entries for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of entries
        """
        return len(self._session_transcripts.get(session_id, []))

    def save_transcript(
        self,
        session_id: str,
        format: str = "json"
    ) -> str:
        """
        Save transcript to filesystem.
        
        Args:
            session_id: Session identifier
            format: Output format (json or txt)
            
        Returns:
            Relative file path to saved transcript
            
        Raises:
            CommunicationError: If saving fails
        """
        try:
            transcript = self._session_transcripts.get(session_id, [])
            
            if not transcript:
                if self.logger:
                    self.logger.warning(
                        component="TranscriptHandler",
                        operation="save_transcript",
                        message=f"No transcript to save for session {session_id}",
                        session_id=session_id
                    )
                return ""
            
            # Get session directory
            session_dir = self.file_storage.base_dir / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcript_{timestamp_str}.{format}"
            file_path = session_dir / filename
            
            # Save based on format
            if format == "json":
                self._save_json(file_path, transcript)
            elif format == "txt":
                self._save_text(file_path, transcript)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Calculate relative path
            relative_path = str(file_path.relative_to(self.file_storage.base_dir))
            
            if self.logger:
                self.logger.info(
                    component="TranscriptHandler",
                    operation="save_transcript",
                    message=f"Saved transcript for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_path": relative_path,
                        "format": format,
                        "entry_count": len(transcript)
                    }
                )
            
            return relative_path
            
        except Exception as e:
            error_msg = f"Failed to save transcript for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="TranscriptHandler",
                    operation="save_transcript",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def _save_json(self, file_path: Path, transcript: List[TranscriptEntry]) -> None:
        """Save transcript in JSON format."""
        data = {
            "transcript": [entry.to_dict() for entry in transcript],
            "entry_count": len(transcript),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_text(self, file_path: Path, transcript: List[TranscriptEntry]) -> None:
        """Save transcript in plain text format."""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Interview Transcript\n")
            f.write("=" * 80 + "\n\n")
            
            for entry in transcript:
                timestamp_str = entry.timestamp.strftime("%H:%M:%S")
                f.write(f"[{timestamp_str}] {entry.speaker.upper()}:\n")
                f.write(f"{entry.text}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write(f"Total entries: {len(transcript)}\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def export_transcript(
        self,
        session_id: str,
        export_path: str,
        format: str = "json"
    ) -> str:
        """
        Export transcript to a specific path.
        
        Args:
            session_id: Session identifier
            export_path: Path to export file
            format: Output format (json or txt)
            
        Returns:
            Path to exported file
            
        Raises:
            CommunicationError: If export fails
        """
        try:
            transcript = self._session_transcripts.get(session_id, [])
            
            if not transcript:
                raise CommunicationError(f"No transcript found for session {session_id}")
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save based on format
            if format == "json":
                self._save_json(export_file, transcript)
            elif format == "txt":
                self._save_text(export_file, transcript)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            if self.logger:
                self.logger.info(
                    component="TranscriptHandler",
                    operation="export_transcript",
                    message=f"Exported transcript for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "export_path": str(export_file),
                        "format": format,
                        "entry_count": len(transcript)
                    }
                )
            
            return str(export_file)
            
        except Exception as e:
            error_msg = f"Failed to export transcript for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="TranscriptHandler",
                    operation="export_transcript",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def load_transcript(
        self,
        session_id: str,
        file_path: str
    ) -> List[TranscriptEntry]:
        """
        Load transcript from file.
        
        Args:
            session_id: Session identifier
            file_path: Path to transcript file
            
        Returns:
            List of transcript entries
            
        Raises:
            CommunicationError: If loading fails
        """
        try:
            abs_path = Path(file_path)
            if not abs_path.is_absolute():
                abs_path = self.file_storage.get_file_path(file_path)
            
            if not abs_path.exists():
                raise FileNotFoundError(f"Transcript file not found: {file_path}")
            
            # Load based on file extension
            if abs_path.suffix == '.json':
                with open(abs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    transcript = [
                        TranscriptEntry.from_dict(entry_data)
                        for entry_data in data.get('transcript', [])
                    ]
            else:
                raise ValueError(f"Unsupported file format: {abs_path.suffix}")
            
            # Store loaded transcript
            self._session_transcripts[session_id] = transcript
            
            if self.logger:
                self.logger.info(
                    component="TranscriptHandler",
                    operation="load_transcript",
                    message=f"Loaded transcript for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_path": str(abs_path),
                        "entry_count": len(transcript)
                    }
                )
            
            return transcript
            
        except Exception as e:
            error_msg = f"Failed to load transcript for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="TranscriptHandler",
                    operation="load_transcript",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def clear_transcript(self, session_id: str) -> None:
        """
        Clear transcript for a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self._session_transcripts:
            entry_count = len(self._session_transcripts[session_id])
            del self._session_transcripts[session_id]
            
            if self.logger:
                self.logger.info(
                    component="TranscriptHandler",
                    operation="clear_transcript",
                    message=f"Cleared transcript for session {session_id}",
                    session_id=session_id,
                    metadata={"entries_cleared": entry_count}
                )

    def get_transcript_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a transcript.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with transcript statistics
        """
        transcript = self._session_transcripts.get(session_id, [])
        
        if not transcript:
            return {
                "entry_count": 0,
                "total_words": 0,
                "total_characters": 0,
                "speakers": []
            }
        
        total_words = sum(len(entry.text.split()) for entry in transcript)
        total_characters = sum(len(entry.text) for entry in transcript)
        speakers = list(set(entry.speaker for entry in transcript))
        
        # Count entries per speaker
        speaker_counts = {}
        for speaker in speakers:
            speaker_counts[speaker] = len([e for e in transcript if e.speaker == speaker])
        
        # Calculate duration
        if len(transcript) >= 2:
            duration = (transcript[-1].timestamp - transcript[0].timestamp).total_seconds()
        else:
            duration = 0
        
        return {
            "entry_count": len(transcript),
            "total_words": total_words,
            "total_characters": total_characters,
            "speakers": speakers,
            "speaker_counts": speaker_counts,
            "duration_seconds": duration,
            "start_time": transcript[0].timestamp.isoformat() if transcript else None,
            "end_time": transcript[-1].timestamp.isoformat() if transcript else None
        }
