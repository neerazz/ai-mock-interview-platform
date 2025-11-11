# Recording Controls Documentation

## Overview

The recording controls provide a comprehensive bottom bar interface for managing communication modes, displaying session information, and controlling the interview session in the AI Mock Interview Platform.

## Visual Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        🎛️ Recording Controls                                 │
├─────────┬──────────┬─────────┬───────┬───────┬────────────┬────────┬─────────┤
│ ⏱️ Time │ 🆔 Session│ 🪙 Tokens│ 🎤    │ 📹    │ 🎨         │ 🖥️     │ 🛑 End  │
│ 05:23   │ a1b2c3...│ 1,234   │ Audio │ Video │ Whiteboard │ Screen │ Interview│
│         │          │ $0.056  │       │       │            │        │         │
│         │          │         │ 🔴    │ ⚪    │ 📷 3 saved │ 🟢     │         │
│         │          │         │Recording│Inactive│          │Active  │         │
└─────────┴──────────┴─────────┴───────┴───────┴────────────┴────────┴─────────┘
│ Active Modes: 🔴 Audio Recording · 🟢 Screen Sharing                         │
│ 💡 Tip: Speak clearly for accurate transcription                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Session Timer (⏱️ Time)
- **Purpose**: Display elapsed session time
- **Format**: MM:SS (e.g., "05:23")
- **Updates**: Real-time, every second
- **Initial State**: "00:00"

### 2. Session ID (🆔 Session)
- **Purpose**: Display current session identifier
- **Format**: First 8 characters + "..." (e.g., "a1b2c3d4...")
- **Tooltip**: Shows full session ID on hover
- **Static**: Does not change during session

### 3. Token Usage (🪙 Tokens)
- **Purpose**: Display AI API token consumption and cost
- **Format**: 
  - Main value: Token count with thousands separator (e.g., "1,234")
  - Delta: Estimated cost in USD (e.g., "$0.056")
- **Updates**: After each AI interaction
- **Calculation**: Average $0.045 per 1K tokens

### 4. Audio Control (🎤 Audio)
- **Purpose**: Toggle audio recording and transcription
- **States**:
  - 🔴 **Recording**: Audio actively recording
  - ⚪ **Inactive**: Enabled but not recording
  - ⚫ **Disabled**: Not enabled for session
- **Action**: Click toggle to start/stop recording
- **Integration**: Uses streamlit-webrtc for real-time capture

### 5. Video Control (📹 Video)
- **Purpose**: Toggle video recording
- **States**:
  - 🔴 **Recording**: Video actively recording
  - ⚪ **Inactive**: Enabled but not recording
  - ⚫ **Disabled**: Not enabled for session
- **Action**: Click toggle to start/stop recording
- **Format**: H264 video format

### 6. Whiteboard Status (🎨 Whiteboard)
- **Purpose**: Display whiteboard snapshot count
- **Format**: "📷 X saved" (e.g., "📷 3 saved")
- **States**:
  - Shows count when enabled
  - ⚫ **Disabled**: Not enabled for session
- **Note**: Snapshot button is in whiteboard panel

### 7. Screen Share Control (🖥️ Screen)
- **Purpose**: Toggle screen sharing
- **States**:
  - 🟢 **Active**: Screen sharing active
  - ⚪ **Inactive**: Enabled but not active
  - ⚫ **Disabled**: Not enabled for session
- **Action**: Click toggle to start/stop sharing
- **Capture**: Every 5 seconds as PNG images

### 8. End Interview Button (🛑 End Interview)
- **Purpose**: End session and generate evaluation
- **Type**: Primary button (red)
- **Confirmation**: Two-click pattern
  - First click: Shows "⚠️ Confirm?" warning
  - Second click: Ends session
- **Action**: 
  1. Stops all active recordings
  2. Generates evaluation
  3. Navigates to evaluation page

## Active Modes Summary

Located below the main controls, this bar shows:
- **Active Modes**: List of currently active communication modes
- **Format**: "🔴 Audio Recording · 🟢 Screen Sharing"
- **Empty State**: "None (Text-only mode)"

## Contextual Tips

Dynamic tips based on current state:
- **Audio Active**: "💡 Tip: Speak clearly for accurate transcription"
- **Whiteboard Enabled**: "💡 Tip: Use the whiteboard to draw your system design"
- **Text Only**: "💡 Tip: Type your responses in the chat panel"

## Visual Indicators

### Color Coding
- 🔴 **Red Circle**: Active recording (audio, video)
- 🟢 **Green Circle**: Active sharing (screen)
- ⚪ **White Circle**: Inactive but enabled
- ⚫ **Black Circle**: Disabled for session

### Status Text
- **Recording**: Mode is actively capturing
- **Active**: Mode is actively sharing
- **Inactive**: Mode is enabled but not active
- **Disabled**: Mode not enabled for session

## User Interactions

### Starting a Recording Mode
1. Locate the desired mode control (Audio, Video, Screen)
2. Click the toggle switch
3. Visual indicator changes to active state (🔴 or 🟢)
4. Mode appears in "Active Modes" summary
5. Contextual tip updates if applicable

### Stopping a Recording Mode
1. Click the active toggle switch
2. Visual indicator changes to inactive state (⚪)
3. Mode is removed from "Active Modes" summary
4. Recording/sharing stops immediately

### Ending the Interview
1. Click "🛑 End Interview" button
2. Warning appears: "⚠️ Confirm?"
3. Click "🛑 End Interview" again to confirm
4. Spinner shows: "🔄 Ending interview and generating evaluation..."
5. All active modes stop automatically
6. Evaluation is generated
7. Navigate to evaluation page

### Canceling End Interview
- Click anywhere else after first click
- Warning disappears on next rerun
- Session continues normally

## Error Handling

### Mode Start Failure
- **Display**: "❌ Failed to start [mode]: [error message]"
- **Action**: Mode remains inactive
- **State**: Toggle returns to off position
- **Logging**: Error logged with context

### Mode Stop Failure
- **Display**: "❌ Failed to stop [mode]: [error message]"
- **Action**: Mode may remain active
- **State**: Toggle state may be inconsistent
- **Logging**: Error logged with context

### Session End Failure
- **Display**: "❌ Failed to end interview: [error message]"
- **Action**: Session continues
- **State**: Confirmation resets
- **Logging**: Error logged with full context

## State Management

### Session State Variables
```python
st.session_state.audio_active = False      # Audio recording state
st.session_state.video_active = False      # Video recording state
st.session_state.screen_active = False     # Screen share state
st.session_state.confirm_end = False       # End confirmation state
st.session_state.interview_start_time      # Session start timestamp
st.session_state.tokens_used = 0           # Total tokens consumed
st.session_state.whiteboard_snapshots = [] # Saved snapshots
st.session_state.enabled_modes = []        # Enabled communication modes
```

### State Lifecycle
1. **Initialization**: States created on first render
2. **Updates**: Modified by user interactions
3. **Persistence**: Maintained across reruns
4. **Reset**: Cleared on session end

## Integration Points

### CommunicationManager
```python
# Enable a communication mode
communication_manager.enable_mode(CommunicationMode.AUDIO)

# Disable a communication mode
communication_manager.disable_mode(CommunicationMode.AUDIO)
```

### SessionManager
```python
# End session and generate evaluation
evaluation = session_manager.end_session(session_id)
```

### Logger
```python
# Log mode changes
logger.info(
    component="interview_ui",
    operation="enable_audio",
    message=f"Audio recording started for session {session_id}",
    session_id=session_id
)

# Log errors
logger.log_error(
    component="interview_ui",
    operation="end_session",
    message=f"Failed to end interview session: {error}",
    session_id=session_id
)
```

## Accessibility

### Keyboard Navigation
- Tab through controls in logical order
- Space/Enter to activate toggles and buttons
- Escape to cancel confirmation (future enhancement)

### Screen Readers
- All controls have descriptive labels
- State changes announced
- Error messages read aloud
- Help text available on focus

### Visual Accessibility
- High contrast indicators
- Color-blind friendly (uses shapes + colors)
- Clear text labels
- Adequate spacing between controls

## Performance

### Update Frequency
- **Timer**: Updates every render (appears real-time)
- **Tokens**: Updates after AI interactions
- **Snapshots**: Updates on save action
- **Mode States**: Updates on toggle action

### Optimization
- Minimal state updates
- Efficient rerun triggers
- Conditional logging
- Batch operations where possible

## Best Practices

### For Users
1. **Start modes early**: Enable recording modes at session start
2. **Monitor tokens**: Keep eye on token usage for cost control
3. **Save snapshots**: Regularly save whiteboard progress
4. **Confirm carefully**: Double-check before ending session

### For Developers
1. **Error handling**: Always wrap mode changes in try-except
2. **State management**: Initialize all states before use
3. **Logging**: Log all mode changes and errors
4. **User feedback**: Provide clear messages for all actions

## Troubleshooting

### Audio Not Recording
- Check if audio mode is enabled for session
- Verify microphone permissions in browser
- Check browser console for WebRTC errors
- Ensure streamlit-webrtc is properly installed

### Video Not Recording
- Check if video mode is enabled for session
- Verify camera permissions in browser
- Check available disk space
- Ensure video codec support

### Screen Share Not Working
- Check if screen share mode is enabled
- Verify screen capture permissions
- Check browser compatibility
- Ensure sufficient system resources

### End Interview Hangs
- Check network connectivity
- Verify database connection
- Check AI API availability
- Review logs for specific errors

## Requirements Mapping

| Requirement | Component | Implementation |
|-------------|-----------|----------------|
| 2.3, 2.4 | Audio Toggle | streamlit-webrtc integration with real-time transcription |
| 2.5 | Video Toggle | Video recording with H264 format |
| 2.6 | Whiteboard | Snapshot count display |
| 2.6 | Screen Share | Toggle with 5-second capture interval |
| 5.1 | End Button | Two-click confirmation with evaluation generation |
| 14.7, 5.1 | Token Display | Usage tracking with cost estimation |
| 18.4 | Timer | Real-time elapsed time in MM:SS format |
| 18.7 | Visual Indicators | Color-coded status indicators for all modes |

## Related Documentation

- [Interview UI Documentation](INTERVIEW_UI.md)
- [Communication Manager Documentation](COMMUNICATION_MANAGER.md)
- [Session Manager Documentation](SESSION_MANAGER.md)
- [Token Tracking Documentation](TOKEN_TRACKING.md)

---

**Last Updated**: 2025-11-11  
**Version**: 1.0  
**Status**: ✅ Complete
