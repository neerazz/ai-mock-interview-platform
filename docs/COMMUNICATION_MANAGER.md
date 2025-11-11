# Communication Manager Documentation

## Overview

The Communication Manager module provides comprehensive support for multiple communication modes during interview sessions, including audio, video, whiteboard, screen sharing, and transcript management.

## Architecture

The Communication Manager follows a modular architecture with specialized handlers for each communication mode:

```
CommunicationManager (Coordinator)
├── AudioHandler (Audio capture & transcription)
├── VideoHandler (Video recording)
├── WhiteboardHandler (Canvas snapshots)
├── ScreenShareHandler (Screen captures)
└── TranscriptHandler (Conversation transcript)
```

## Components

### 1. CommunicationManager

**Purpose**: Coordinates between different communication mode handlers and tracks enabled modes.

**Key Features**:
- Enable/disable communication modes dynamically
- Track active communication modes
- Provide access to individual handlers
- Coordinate between handlers

**Usage Example**:
```python
from src.communication import CommunicationManager
from src.models import CommunicationMode

# Initialize manager
comm_manager = CommunicationManager(
    file_storage=file_storage,
    logger=logger
)

# Enable audio mode
comm_manager.enable_mode(CommunicationMode.AUDIO)

# Check if mode is enabled
if comm_manager.is_mode_enabled(CommunicationMode.AUDIO):
    audio_handler = comm_manager.get_handler(CommunicationMode.AUDIO)

# Get all enabled modes
enabled_modes = comm_manager.get_enabled_modes()

# Disable mode
comm_manager.disable_mode(CommunicationMode.AUDIO)
```

### 2. AudioHandler

**Purpose**: Handles audio recording and real-time transcription using OpenAI Whisper.

**Key Features**:
- Real-time audio capture via streamlit-webrtc
- Audio transcription using OpenAI Whisper (< 2 seconds)
- WAV format audio storage
- Transcript text storage
- Recording state management

**Usage Example**:
```python
from src.communication.audio_handler import AudioHandler

# Initialize handler
audio_handler = AudioHandler(
    file_storage=file_storage,
    whisper_client=openai_client,
    logger=logger,
    sample_rate=16000,
    channels=1
)

# Start recording
audio_handler.start_recording(session_id)

# Record and save audio
audio_path = audio_handler.record_audio(
    session_id=session_id,
    audio_data=audio_bytes,
    duration_seconds=5.2
)

# Transcribe audio
transcript = audio_handler.transcribe_audio(
    audio_file_path=audio_path,
    language="en"
)

# Save transcript
transcript_path = audio_handler.save_transcript(
    session_id=session_id,
    transcript_text=transcript,
    audio_file_path=audio_path
)

# Combined operation
audio_path, transcript = audio_handler.record_and_transcribe(
    session_id=session_id,
    audio_data=audio_bytes,
    duration_seconds=5.2,
    on_transcription_complete=lambda text: print(f"Transcribed: {text}")
)

# Stop recording
metadata = audio_handler.stop_recording(session_id)
```

**Configuration**:
- `sample_rate`: Audio sample rate in Hz (default: 16000)
- `channels`: Number of audio channels (default: 1 for mono)
- `audio_format`: File format (default: wav)

### 3. VideoHandler

**Purpose**: Captures and stores video streams during interview sessions.

**Key Features**:
- Video stream capture
- H264 codec support
- WebM/MP4 format storage
- Recording state management
- Chunk-based recording

**Usage Example**:
```python
from src.communication.video_handler import VideoHandler

# Initialize handler
video_handler = VideoHandler(
    file_storage=file_storage,
    logger=logger,
    fps=30,
    resolution="1280x720",
    video_format="webm"
)

# Start recording
video_handler.start_recording(session_id)

# Add video chunks
video_handler.add_video_chunk(session_id, chunk_data)

# Get recording duration
duration = video_handler.get_recording_duration(session_id)

# Save complete recording
video_path = video_handler.save_recording(session_id)

# Or capture directly
video_path = video_handler.capture_video(
    session_id=session_id,
    video_data=video_bytes,
    duration_seconds=30.5,
    codec="h264"
)

# Stop recording
metadata = video_handler.stop_recording(session_id)
```

**Configuration**:
- `fps`: Frames per second (default: 30)
- `resolution`: Video resolution as "WIDTHxHEIGHT" (default: 1280x720)
- `video_format`: File format (default: webm)

### 4. WhiteboardHandler

**Purpose**: Manages whiteboard canvas operations and snapshot storage.

**Key Features**:
- Canvas snapshot saving (PNG format)
- Snapshot tracking and retrieval
- Auto-save functionality
- Snapshot export
- Canvas clearing

**Usage Example**:
```python
from src.communication.whiteboard_handler import WhiteboardHandler

# Initialize handler
whiteboard_handler = WhiteboardHandler(
    file_storage=file_storage,
    logger=logger,
    canvas_width=800,
    canvas_height=600
)

# Save snapshot
snapshot_path = whiteboard_handler.save_whiteboard(
    session_id=session_id,
    canvas_data=canvas_image_bytes,
    snapshot_number=1,
    metadata={"description": "Initial system design"}
)

# Auto-save snapshot
auto_path = whiteboard_handler.auto_save_snapshot(
    session_id=session_id,
    canvas_data=canvas_image_bytes,
    interval_seconds=60
)

# Get all snapshots
snapshots = whiteboard_handler.get_snapshots(session_id)

# Get latest snapshot
latest = whiteboard_handler.get_latest_snapshot(session_id)

# Get snapshot count
count = whiteboard_handler.get_snapshot_count(session_id)

# Export snapshots
exported_files = whiteboard_handler.export_snapshots(
    session_id=session_id,
    export_dir="/path/to/export"
)

# Clear canvas (logical operation)
whiteboard_handler.clear_canvas(session_id)

# Get canvas configuration
config = whiteboard_handler.get_canvas_config()
```

**Configuration**:
- `canvas_width`: Canvas width in pixels (default: 800)
- `canvas_height`: Canvas height in pixels (default: 600)
- `image_format`: Image format (default: png)

### 5. ScreenShareHandler

**Purpose**: Captures screen content at regular intervals (5-second intervals).

**Key Features**:
- Periodic screen capture (default: 5 seconds)
- PNG format storage
- Capture tracking and retrieval
- Capture statistics
- Export functionality

**Usage Example**:
```python
from src.communication.screen_handler import ScreenShareHandler

# Initialize handler
screen_handler = ScreenShareHandler(
    file_storage=file_storage,
    logger=logger,
    capture_interval_seconds=5
)

# Start capture session
screen_handler.start_capture(session_id)

# Capture screen
capture_path = screen_handler.capture_screen(
    session_id=session_id,
    screen_data=screen_image_bytes,
    capture_number=1,
    metadata={"resolution": "1920x1080"}
)

# Get capture count
count = screen_handler.get_capture_count(session_id)

# Get all captures
captures = screen_handler.get_captures(session_id)

# Get latest capture
latest = screen_handler.get_latest_capture(session_id)

# Get capture duration
duration = screen_handler.get_capture_duration(session_id)

# Get capture statistics
stats = screen_handler.get_capture_stats(session_id)

# Export captures
exported_files = screen_handler.export_captures(
    session_id=session_id,
    export_dir="/path/to/export"
)

# Stop capture
metadata = screen_handler.stop_capture(session_id)
```

**Configuration**:
- `capture_interval_seconds`: Interval between captures (default: 5)
- `image_format`: Image format (default: png)

**Design Rationale**:
The 5-second capture interval balances:
- Storage efficiency (vs. continuous video)
- Performance (minimal CPU/memory overhead)
- Usefulness (captures meaningful changes)
- Review capability (sufficient granularity)
- Cost (reduces AI analysis costs)

### 6. TranscriptHandler

**Purpose**: Manages real-time conversation transcripts with search and export.

**Key Features**:
- Real-time transcript entry addition
- Timestamp and speaker tracking
- Search functionality
- Speaker filtering
- JSON and text export
- Transcript statistics

**Usage Example**:
```python
from src.communication.transcript_handler import TranscriptHandler

# Initialize handler
transcript_handler = TranscriptHandler(
    file_storage=file_storage,
    logger=logger
)

# Add transcript entry
entry = transcript_handler.add_entry(
    session_id=session_id,
    speaker="interviewer",
    text="Can you explain your approach to scaling this system?",
    metadata={"source": "ai_interviewer"}
)

# Get complete transcript
transcript = transcript_handler.get_transcript(session_id)

# Get recent entries
recent = transcript_handler.get_recent_entries(session_id, count=5)

# Search transcript
matches = transcript_handler.search_transcript(
    session_id=session_id,
    query="scaling",
    case_sensitive=False
)

# Filter by speaker
interviewer_entries = transcript_handler.filter_by_speaker(
    session_id=session_id,
    speaker="interviewer"
)

# Get entry count
count = transcript_handler.get_entry_count(session_id)

# Save transcript
json_path = transcript_handler.save_transcript(
    session_id=session_id,
    format="json"
)

txt_path = transcript_handler.save_transcript(
    session_id=session_id,
    format="txt"
)

# Export transcript
export_path = transcript_handler.export_transcript(
    session_id=session_id,
    export_path="/path/to/export/transcript.json",
    format="json"
)

# Get transcript statistics
stats = transcript_handler.get_transcript_stats(session_id)
# Returns: entry_count, total_words, total_characters, speakers, 
#          speaker_counts, duration_seconds, start_time, end_time

# Load transcript from file
loaded_transcript = transcript_handler.load_transcript(
    session_id=session_id,
    file_path="path/to/transcript.json"
)

# Clear transcript
transcript_handler.clear_transcript(session_id)
```

**TranscriptEntry Structure**:
```python
@dataclass
class TranscriptEntry:
    timestamp: datetime
    speaker: str  # "interviewer" or "candidate"
    text: str
    metadata: Dict[str, Any]
```

## Integration with Other Components

### File Storage Integration

All handlers integrate with the FileStorage component for persistent storage:

```python
# Initialize file storage
file_storage = FileStorage(base_dir="./data/sessions")

# Initialize handlers with file storage
audio_handler = AudioHandler(file_storage=file_storage)
video_handler = VideoHandler(file_storage=file_storage)
whiteboard_handler = WhiteboardHandler(file_storage=file_storage)
screen_handler = ScreenShareHandler(file_storage=file_storage)
transcript_handler = TranscriptHandler(file_storage=file_storage)
```

### Logging Integration

All handlers support optional logging:

```python
from src.log_manager import LoggingManager

# Initialize logger
logger = LoggingManager(config=logging_config)

# Initialize handlers with logger
audio_handler = AudioHandler(
    file_storage=file_storage,
    logger=logger
)
```

### Database Integration

Handlers can optionally integrate with the database for storing file references:

```python
from src.database.data_store import PostgresDataStore

# Initialize data store
data_store = PostgresDataStore(connection_string=db_url)

# Initialize handlers with data store
audio_handler = AudioHandler(
    file_storage=file_storage,
    data_store=data_store
)
```

## File Organization

Media files are organized by session and type:

```
data/sessions/
└── {session_id}/
    ├── audio/
    │   ├── audio_20241110_143000_123456.wav
    │   ├── audio_20241110_143000_123456_transcript.txt
    │   └── audio_20241110_143030_789012.wav
    ├── video/
    │   └── video_20241110_143000_456789.webm
    ├── whiteboard/
    │   ├── whiteboard_20241110_143015_234567.png
    │   └── whiteboard_20241110_143045_890123.png
    ├── screen/
    │   ├── screen_20241110_143005_345678.png
    │   └── screen_20241110_143010_901234.png
    └── transcript_20241110_143100.json
```

## Error Handling

All handlers raise `CommunicationError` for operation failures:

```python
from src.exceptions import CommunicationError

try:
    audio_path = audio_handler.record_audio(session_id, audio_data)
except CommunicationError as e:
    logger.error(f"Audio recording failed: {e}")
    # Handle error gracefully
```

## Performance Considerations

### Audio Transcription
- Target: < 2 seconds for transcription
- Uses OpenAI Whisper API
- Asynchronous processing recommended for UI responsiveness

### Video Recording
- Chunk-based recording for memory efficiency
- H264 codec for compression
- Consider storage limits for long sessions

### Whiteboard Snapshots
- PNG format for lossless quality
- Target: < 1 second for snapshot save
- Auto-save at regular intervals (60 seconds)

### Screen Captures
- 5-second interval balances storage and usefulness
- PNG format for text readability
- Periodic cleanup recommended for old sessions

### Transcript Updates
- Real-time updates (< 2 seconds)
- In-memory storage during session
- Periodic saves to filesystem

## Testing

Example test structure:

```python
def test_audio_handler_record():
    """Test audio recording functionality."""
    handler = AudioHandler(file_storage=mock_storage)
    audio_path = handler.record_audio(
        session_id="test-session",
        audio_data=b"mock audio data"
    )
    assert audio_path is not None
    assert "audio" in audio_path

def test_transcript_search():
    """Test transcript search functionality."""
    handler = TranscriptHandler(file_storage=mock_storage)
    handler.add_entry("session-1", "interviewer", "scaling systems")
    handler.add_entry("session-1", "candidate", "load balancing")
    
    results = handler.search_transcript("session-1", "scaling")
    assert len(results) == 1
    assert results[0].speaker == "interviewer"
```

## Requirements Mapping

This implementation satisfies the following requirements:

- **Requirement 2.1, 2.2**: Communication mode selection and management
- **Requirement 2.3, 2.4, 2.10**: Audio capture and transcription
- **Requirement 2.5**: Video recording
- **Requirement 2.6**: Screen share capture
- **Requirement 3.1, 3.2, 3.3, 3.4, 3.5**: Whiteboard canvas operations
- **Requirement 18.3, 18.5**: Real-time transcript display and functionality

## Future Enhancements

Potential improvements for future iterations:

1. **Audio**: Support for multiple audio formats (MP3, OGG)
2. **Video**: Live streaming support
3. **Whiteboard**: Collaborative drawing features
4. **Screen**: Adaptive capture intervals based on activity
5. **Transcript**: Real-time translation support
6. **General**: Cloud storage integration for media files
