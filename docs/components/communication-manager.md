# Communication Manager

The Communication Manager handles multi-modal communication during interviews, including audio, video, whiteboard, and screen sharing.

## Overview

The Communication Manager:

- Enables/disables communication modes
- Coordinates mode-specific handlers
- Stores media files
- Manages transcription

## Supported Modes

### Audio

- Records audio using WebRTC
- Transcribes with OpenAI Whisper
- Stores audio files locally

### Video

- Records video streams
- Stores video files locally
- Optional: Extract frames for analysis

### Whiteboard

- Captures canvas snapshots
- Stores images with timestamps
- Includes in AI context

### Screen Share

- Captures screen recordings
- Stores screen captures
- Optional: OCR for text extraction

## Architecture

```python
class CommunicationManager:
    def __init__(
        self,
        file_storage: FileStorage,
        data_store: DataStore,
        logger: LoggingManager
    ):
        self.audio_handler = AudioHandler(file_storage, logger)
        self.video_handler = VideoHandler(file_storage, logger)
        self.whiteboard_handler = WhiteboardHandler(file_storage, logger)
        self.screen_handler = ScreenHandler(file_storage, logger)
```

## Usage Example

```python
# Enable modes
communication_manager.enable_mode(session_id, CommunicationMode.AUDIO)
communication_manager.enable_mode(session_id, CommunicationMode.WHITEBOARD)

# Save audio
audio_path = communication_manager.save_audio(session_id, audio_bytes)

# Save whiteboard snapshot
snapshot_path = communication_manager.save_whiteboard_snapshot(
    session_id,
    canvas_image_bytes
)

# Get transcript
transcript = communication_manager.get_transcript(session_id)
```

## File Storage

Media files are organized by session:

```
data/sessions/{session_id}/
├── audio/
│   ├── recording_001.wav
│   └── recording_002.wav
├── video/
│   └── interview.mp4
├── whiteboard/
│   ├── snapshot_001.png
│   └── snapshot_002.png
└── screen/
    └── capture_001.png
```

## Related Components

- [Session Manager](session-manager.md)
- [File Storage](../features/file-storage.md)
