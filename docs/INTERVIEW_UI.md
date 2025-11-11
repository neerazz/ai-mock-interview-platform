# Interview UI Implementation

## Overview

The interview interface provides a comprehensive 3-panel layout optimized for system design interviews. The interface enables real-time interaction between the candidate and AI interviewer while supporting multiple communication modes.

## Architecture

### Layout Structure

The interview interface uses a fixed 3-panel layout with the following proportions:

```
┌─────────────────────────────────────────────────────────────────┐
│                    Header (Session Info)                         │
├──────────────┬──────────────────────────┬──────────────────────┤
│              │                          │                      │
│   AI Chat    │    Whiteboard Canvas     │    Transcript       │
│   (30%)      │       (45%)              │     (25%)           │
│              │                          │                      │
│  - Questions │  - Drawing tools         │  - Real-time text   │
│  - Responses │  - System diagrams       │  - Conversation     │
│  - Follow-ups│  - Save snapshots        │  - Searchable       │
│              │  - Clear canvas          │  - Timestamps       │
│              │                          │                      │
├──────────────┴──────────────────────────┴──────────────────────┤
│                     Recording Controls                           │
│  [●] Audio  [●] Video  [📷] Whiteboard  [🖥️] Screen  [End]     │
└─────────────────────────────────────────────────────────────────┘
```

### Panel Specifications

#### Left Panel - AI Chat Interface (30% width)
- **Purpose**: Display conversation between AI interviewer and candidate
- **Features**:
  - Scrollable conversation history with fixed height (500px)
  - Distinct styling for interviewer (🤖) and candidate (👤) messages
  - Timestamps for each message
  - Text input box for candidate responses
  - Auto-scroll to latest message
  - Real-time AI response processing

#### Center Panel - Whiteboard Canvas (45% width)
- **Purpose**: Enable visual system design diagrams
- **Features**:
  - Drawing tools (freedraw, line, rect, circle, transform)
  - Color picker for different components
  - Stroke width adjustment
  - Save snapshot functionality
  - Clear canvas functionality
  - Full-screen mode option
  - Integration with AI for whiteboard analysis

#### Right Panel - Transcript Display (25% width)
- **Purpose**: Show real-time conversation transcript
- **Features**:
  - Scrollable transcript with fixed height (500px)
  - Speaker labels (Interviewer/Candidate)
  - Timestamps for each entry
  - Search functionality
  - Export transcript button
  - Auto-update as conversation progresses

#### Bottom Bar - Recording Controls (Full width)
- **Purpose**: Control communication modes and session
- **Features**:
  - Audio recording toggle with visual indicator
  - Video recording toggle with visual indicator
  - Whiteboard snapshot counter
  - Screen share toggle with visual indicator
  - End interview button with confirmation
  - Visual indicators for active modes:
    - Audio: 🔴 Recording / ⚪ Inactive / ⚫ Disabled
    - Video: 🔴 Recording / ⚪ Inactive / ⚫ Disabled
    - Whiteboard: 📷 Snapshot count
    - Screen: 🟢 Active / ⚪ Inactive / ⚫ Disabled

## Implementation Details

### File Structure

```
src/ui/pages/
├── __init__.py
├── setup.py          # Resume upload and configuration
└── interview.py      # Interview interface (NEW)
```

### Key Functions

#### `render_interview_page()`
Main entry point for the interview interface. Handles:
- Session validation
- Interview initialization
- Layout rendering
- Component coordination

#### `render_header()`
Displays session information:
- Session timer (MM:SS format)
- Session ID (truncated)
- Token usage counter

#### `render_ai_chat_panel()`
Manages the AI chat interface:
- Displays conversation history
- Handles user input
- Processes AI responses
- Updates transcript
- Tracks token usage

#### `render_whiteboard_panel()`
Manages the whiteboard canvas:
- Drawing tool selection
- Color and width controls
- Canvas rendering (placeholder for streamlit-drawable-canvas)
- Snapshot saving
- Canvas clearing

#### `render_transcript_panel()`
Manages the transcript display:
- Real-time transcript updates
- Search functionality
- Export functionality
- Speaker identification

#### `render_recording_controls()`
Manages communication mode controls:
- Audio/video toggles
- Whiteboard snapshot tracking
- Screen share toggle
- End interview button with confirmation

### Session State Management

The interview interface uses Streamlit session state to maintain:

```python
st.session_state.interview_started          # Boolean: Interview active
st.session_state.interview_start_time       # datetime: Session start
st.session_state.conversation_history       # List[dict]: Chat messages
st.session_state.transcript_entries         # List[dict]: Transcript entries
st.session_state.whiteboard_snapshots       # List[dict]: Saved snapshots
st.session_state.tokens_used                # int: Total tokens consumed
st.session_state.audio_active               # Boolean: Audio recording state
st.session_state.video_active               # Boolean: Video recording state
st.session_state.screen_active              # Boolean: Screen share state
```

### Integration Points

#### Session Manager
- `start_session(session_id)`: Initialize interview session
- `end_session(session_id)`: Complete session and generate evaluation

#### AI Interviewer
- `start_interview(session_id)`: Get initial question
- `process_response(session_id, response, whiteboard_image)`: Process candidate input

#### Communication Manager
- `save_whiteboard(session_id, canvas_data)`: Save whiteboard snapshot
- Communication mode status tracking

## Requirements Coverage

### Requirement 18.1
✅ **AI chat interface in left panel (30% width)**
- Implemented with `st.columns([3, 4.5, 2.5])`
- Left column (3/10 = 30%) contains AI chat

### Requirement 18.2
✅ **Whiteboard canvas in center panel (45% width)**
- Implemented with `st.columns([3, 4.5, 2.5])`
- Center column (4.5/10 = 45%) contains whiteboard

### Requirement 18.3
✅ **Transcript display in right panel (25% width)**
- Implemented with `st.columns([3, 4.5, 2.5])`
- Right column (2.5/10 = 25%) contains transcript

### Requirement 18.4
✅ **Recording controls in bottom bar**
- Implemented with `render_recording_controls()`
- Spans full width below panels

### Requirement 18.6
✅ **Consistent layout throughout session**
- Fixed column proportions
- No dynamic resizing
- Persistent layout structure

## Usage

### Starting an Interview

1. Complete setup page (resume upload, AI configuration, communication modes)
2. Click "Start Interview" button
3. System navigates to interview interface
4. Session automatically starts and AI asks initial question

### During Interview

1. **Chat**: Type responses in the text input box
2. **Whiteboard**: Use drawing tools to create diagrams
3. **Snapshots**: Click "Save Snapshot" to capture whiteboard state
4. **Transcript**: View real-time conversation transcript
5. **Search**: Use search box to find specific transcript content
6. **Controls**: Toggle audio/video/screen modes as needed

### Ending Interview

1. Click "End Interview" button
2. Confirm by clicking again
3. System generates evaluation report
4. Navigates to evaluation page

## Future Enhancements

### Planned for Task 12.2 (AI Chat Panel)
- Enhanced message formatting
- Typing indicators
- Message reactions
- Code snippet support

### Planned for Task 12.3 (Whiteboard Panel)
- Full streamlit-drawable-canvas integration
- Undo/redo functionality
- Shape library
- Template diagrams
- Real-time collaboration (future)

### Planned for Task 12.4 (Transcript Panel)
- Advanced search with filters
- Highlight search results
- Export formats (PDF, JSON)
- Timestamp navigation

### Planned for Task 12.5 (Recording Controls)
- Real-time audio/video streaming
- Waveform visualization
- Recording quality indicators
- Bandwidth monitoring

## Testing

### Validation Script

Run `validate_interview_ui.py` to verify implementation:

```bash
python validate_interview_ui.py
```

The script validates:
- File structure
- Function existence
- Layout proportions
- Component integration
- Requirements coverage

### Manual Testing

1. Start application: `streamlit run src/main.py`
2. Complete setup page
3. Navigate to interview interface
4. Verify:
   - 3-panel layout renders correctly
   - Chat input works
   - Whiteboard controls are visible
   - Transcript displays correctly
   - Recording controls are functional
   - End interview button works

## Known Limitations

1. **Whiteboard Canvas**: Currently uses placeholder (text area) instead of streamlit-drawable-canvas
   - Will be fully implemented in task 12.3
   - Snapshot functionality works with placeholder data

2. **Audio/Video**: Toggle controls are present but streaming not yet implemented
   - Will be fully implemented in task 12.5
   - Visual indicators work correctly

3. **Screen Share**: Toggle control present but capture not yet implemented
   - Will be fully implemented in task 12.5

## Troubleshooting

### Layout Issues

**Problem**: Panels not displaying with correct proportions
**Solution**: Verify `st.columns([3, 4.5, 2.5])` is used correctly

**Problem**: Content overflowing panels
**Solution**: Check container heights (500px for chat and transcript)

### Session Issues

**Problem**: "No active session" error
**Solution**: Ensure session is created from setup page before navigating to interview

**Problem**: Interview not starting
**Solution**: Check session_manager and ai_interviewer are properly initialized

### Integration Issues

**Problem**: AI responses not appearing
**Solution**: Verify ai_interviewer.process_response() is called correctly

**Problem**: Transcript not updating
**Solution**: Check transcript_entries are being appended to session state

## References

- Design Document: `.kiro/specs/ai-mock-interview-platform/design.md`
- Requirements: `.kiro/specs/ai-mock-interview-platform/requirements.md`
- Tasks: `.kiro/specs/ai-mock-interview-platform/tasks.md`
- Setup UI: `docs/SETUP_UI.md`
