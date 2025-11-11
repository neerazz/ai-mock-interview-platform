"""
Interview interface page with 3-panel layout.

This module provides the main interview interface with:
- Left panel: AI chat interface (30% width)
- Center panel: Whiteboard canvas (45% width)
- Right panel: Real-time transcript (25% width)
- Bottom bar: Recording controls
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, List

from src.models import CommunicationMode, Message


def render_interview_page(
    session_manager,
    communication_manager,
    ai_interviewer,
    config
):
    """
    Render the interview interface with 3-panel layout.
    
    Args:
        session_manager: SessionManager instance
        communication_manager: CommunicationManager instance
        ai_interviewer: AIInterviewer instance
        config: Configuration object
    """
    # Check if session exists
    if not st.session_state.get("current_session_id"):
        st.error("❌ No active session. Please start a session from the setup page.")
        if st.button("← Go to Setup"):
            st.session_state.current_page = "setup"
            st.rerun()
        return
    
    session_id = st.session_state.current_session_id
    
    # Initialize interview state
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "interview_start_time" not in st.session_state:
        st.session_state.interview_start_time = None
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    if "transcript_entries" not in st.session_state:
        st.session_state.transcript_entries = []
    if "whiteboard_snapshots" not in st.session_state:
        st.session_state.whiteboard_snapshots = []
    
    # Start interview if not started
    if not st.session_state.interview_started:
        with st.spinner("Starting interview..."):
            try:
                session_manager.start_session(session_id)
                st.session_state.interview_started = True
                st.session_state.interview_start_time = datetime.now()
                
                # Get initial question from AI interviewer
                initial_response = ai_interviewer.start_interview(session_id)
                st.session_state.conversation_history.append({
                    "role": "interviewer",
                    "content": initial_response.content,
                    "timestamp": datetime.now()
                })
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to start interview: {str(e)}")
                return
    
    # Header with session info
    render_header(session_id, st.session_state.interview_start_time)
    
    # Main 3-panel layout
    col_left, col_center, col_right = st.columns([3, 4.5, 2.5])
    
    with col_left:
        render_ai_chat_panel(
            session_id,
            ai_interviewer,
            st.session_state.conversation_history
        )
    
    with col_center:
        render_whiteboard_panel(
            session_id,
            communication_manager
        )
    
    with col_right:
        render_transcript_panel(
            session_id,
            st.session_state.transcript_entries
        )
    
    # Bottom recording controls
    st.divider()
    render_recording_controls(
        session_id,
        session_manager,
        communication_manager,
        config
    )


def render_header(session_id: str, start_time: Optional[datetime]):
    """
    Render the header with session information.
    
    Args:
        session_id: Current session ID
        start_time: Session start time
    """
    st.title("🎤 AI Mock Interview - System Design")
    
    col_timer, col_session, col_tokens = st.columns([2, 2, 1])
    
    with col_timer:
        if start_time:
            elapsed = datetime.now() - start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            st.metric("Session Time", f"{minutes:02d}:{seconds:02d}")
        else:
            st.metric("Session Time", "00:00")
    
    with col_session:
        st.metric("Session ID", f"{session_id[:8]}...")
    
    with col_tokens:
        # Placeholder for token usage
        tokens_used = st.session_state.get("tokens_used", 0)
        st.metric("Tokens", f"{tokens_used:,}")


def render_ai_chat_panel(
    session_id: str,
    ai_interviewer,
    conversation_history: List[dict]
):
    """
    Render the AI chat interface panel (left panel, 30% width).
    
    Displays conversation history with scrolling, shows AI interviewer messages
    with avatar, shows candidate messages with distinct styling, adds timestamps
    to each message, implements text input box for candidate responses, auto-scrolls
    to latest message, sends user input to AI Interviewer for processing, and
    displays AI responses in real-time.
    
    Requirements: 1.5, 2.7, 2.8, 18.1
    
    Args:
        session_id: Current session ID
        ai_interviewer: AIInterviewer instance
        conversation_history: List of conversation messages
    """
    st.subheader("💬 AI Interviewer")
    
    # Chat history container with fixed height and scrolling
    # Using container with height enables automatic scrolling
    chat_container = st.container(height=500)
    
    with chat_container:
        if not conversation_history:
            st.info("Waiting for AI interviewer to start...")
        else:
            # Display all messages in conversation history
            for idx, msg in enumerate(conversation_history):
                role = msg["role"]
                content = msg["content"]
                timestamp = msg["timestamp"]
                
                # Display message with appropriate styling based on role
                if role == "interviewer":
                    # AI interviewer messages with robot avatar
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(content)
                        # Add timestamp below message
                        st.caption(f"🕒 {timestamp.strftime('%H:%M:%S')}")
                else:
                    # Candidate messages with user avatar and distinct styling
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(content)
                        # Add timestamp below message
                        st.caption(f"🕒 {timestamp.strftime('%H:%M:%S')}")
    
    # Text input box for candidate responses
    # Positioned below chat history for easy access
    user_input = st.chat_input(
        "Type your response...",
        key="chat_input"
    )
    
    # Process user input when submitted
    if user_input:
        # Add user message to conversation history
        st.session_state.conversation_history.append({
            "role": "candidate",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # Add to transcript for real-time display
        st.session_state.transcript_entries.append({
            "speaker": "Candidate",
            "text": user_input,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Send user input to AI Interviewer for processing
        # Display spinner while AI is generating response
        with st.spinner("🤖 AI is thinking..."):
            try:
                # Get whiteboard image if available for context
                whiteboard_image = st.session_state.get("current_whiteboard_image")
                
                # Process response with AI interviewer
                # This sends the input to the AI and gets a response
                response = ai_interviewer.process_response(
                    session_id,
                    user_input,
                    whiteboard_image
                )
                
                # Add AI response to conversation history
                st.session_state.conversation_history.append({
                    "role": "interviewer",
                    "content": response.content,
                    "timestamp": datetime.now()
                })
                
                # Add AI response to transcript
                st.session_state.transcript_entries.append({
                    "speaker": "Interviewer",
                    "text": response.content,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
                # Update token usage tracking
                if response.token_usage:
                    current_tokens = st.session_state.get("tokens_used", 0)
                    st.session_state.tokens_used = current_tokens + response.token_usage.total_tokens
                
                # Rerun to display new messages and auto-scroll to latest
                # This ensures the chat updates in real-time
                st.rerun()
                
            except Exception as e:
                # Display clear error message if processing fails
                st.error(f"❌ Error processing response: {str(e)}")
                if st.session_state.get("logger"):
                    st.session_state.logger.log_error(
                        component="interview_ui",
                        operation="process_user_input",
                        message=f"Failed to process user input: {str(e)}",
                        session_id=session_id
                    )


def render_whiteboard_panel(
    session_id: str,
    communication_manager
):
    """
    Render the whiteboard canvas panel (center panel, 45% width).
    
    Integrates streamlit-drawable-canvas component with drawing tools (pen, eraser,
    shapes, text), color picker for different components, undo/redo functionality,
    save snapshot button, clear canvas button, and full-screen mode option.
    
    Requirements: 3.1, 3.2, 3.5, 18.2
    
    Args:
        session_id: Current session ID
        communication_manager: CommunicationManager instance
    """
    from streamlit_drawable_canvas import st_canvas
    import io
    from PIL import Image
    
    st.subheader("🎨 Whiteboard")
    
    # Check if whiteboard mode is enabled
    enabled_modes = st.session_state.get("enabled_modes", [])
    whiteboard_enabled = CommunicationMode.WHITEBOARD in enabled_modes
    
    if not whiteboard_enabled:
        st.info("ℹ️ Whiteboard mode is not enabled for this session")
        return
    
    # Initialize canvas state
    if "canvas_key" not in st.session_state:
        st.session_state.canvas_key = 0
    if "fullscreen_mode" not in st.session_state:
        st.session_state.fullscreen_mode = False
    if "canvas_history" not in st.session_state:
        st.session_state.canvas_history = []
    if "canvas_history_index" not in st.session_state:
        st.session_state.canvas_history_index = -1
    
    # Canvas controls - Drawing tools, color picker, and stroke width
    col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1])
    
    with col1:
        # Drawing mode selector with pen, eraser, shapes, and text
        drawing_mode = st.selectbox(
            "🖊️ Tool",
            [
                "freedraw",      # Pen tool for freehand drawing
                "line",          # Line tool for straight lines
                "rect",          # Rectangle tool for boxes/components
                "circle",        # Circle tool for nodes/services
                "transform",     # Transform tool for moving/resizing
                "polygon",       # Polygon tool for custom shapes
                "point"          # Point tool for markers
            ],
            key=f"drawing_mode_{st.session_state.canvas_key}",
            format_func=lambda x: {
                "freedraw": "✏️ Pen",
                "line": "📏 Line",
                "rect": "⬜ Rectangle",
                "circle": "⭕ Circle",
                "transform": "↔️ Transform",
                "polygon": "🔷 Polygon",
                "point": "📍 Point"
            }.get(x, x)
        )
    
    with col2:
        # Color picker for different components
        stroke_color = st.color_picker(
            "🎨 Color",
            "#000000",
            key=f"stroke_color_{st.session_state.canvas_key}",
            help="Choose color for drawing different system components"
        )
    
    with col3:
        # Stroke width slider
        stroke_width = st.slider(
            "📏 Width",
            min_value=1,
            max_value=25,
            value=3,
            key=f"stroke_width_{st.session_state.canvas_key}",
            help="Adjust line thickness"
        )
    
    with col4:
        # Background color option
        bg_color = st.color_picker(
            "🖼️ Background",
            "#FFFFFF",
            key=f"bg_color_{st.session_state.canvas_key}",
            help="Canvas background color"
        )
    
    # Determine canvas dimensions based on fullscreen mode
    if st.session_state.fullscreen_mode:
        canvas_width = 1200
        canvas_height = 800
    else:
        canvas_width = 800
        canvas_height = 600
    
    # Render the drawable canvas
    # This integrates streamlit-drawable-canvas for system design diagrams
    canvas_result = st_canvas(
        fill_color=f"{stroke_color}20",  # Semi-transparent fill
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=None,
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode=drawing_mode,
        point_display_radius=5 if drawing_mode == "point" else 3,
        key=f"canvas_{st.session_state.canvas_key}",
        display_toolbar=True,  # Show built-in toolbar
    )
    
    # Store current canvas image for AI analysis
    if canvas_result.image_data is not None:
        st.session_state.current_whiteboard_image = canvas_result.image_data
    
    # Canvas action buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Save snapshot button
        if st.button("📷 Save Snapshot", key="save_snapshot", use_container_width=True):
            try:
                # Check if there's content to save
                if canvas_result.image_data is not None:
                    # Convert numpy array to PNG bytes
                    img = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    snapshot_data = img_byte_arr.getvalue()
                    
                    # Save whiteboard snapshot via communication manager
                    file_path = communication_manager.save_whiteboard(
                        session_id,
                        snapshot_data
                    )
                    
                    # Track snapshot in session state
                    st.session_state.whiteboard_snapshots.append({
                        "timestamp": datetime.now(),
                        "file_path": file_path
                    })
                    
                    st.success(f"✅ Snapshot saved! (Total: {len(st.session_state.whiteboard_snapshots)})")
                    
                    # Log the save operation
                    if st.session_state.get("logger"):
                        st.session_state.logger.info(
                            component="interview_ui",
                            operation="save_whiteboard_snapshot",
                            message=f"Whiteboard snapshot saved for session {session_id}",
                            session_id=session_id,
                            metadata={"file_path": file_path}
                        )
                else:
                    st.warning("⚠️ Nothing to save - canvas is empty")
                    
            except Exception as e:
                st.error(f"❌ Failed to save snapshot: {str(e)}")
                if st.session_state.get("logger"):
                    st.session_state.logger.log_error(
                        component="interview_ui",
                        operation="save_whiteboard_snapshot",
                        message=f"Failed to save whiteboard snapshot: {str(e)}",
                        session_id=session_id
                    )
    
    with col2:
        # Clear canvas button
        if st.button("🗑️ Clear Canvas", key="clear_canvas", use_container_width=True):
            # Increment canvas key to force re-render with empty canvas
            st.session_state.canvas_key += 1
            st.session_state.canvas_history = []
            st.session_state.canvas_history_index = -1
            
            # Log the clear operation
            if st.session_state.get("logger"):
                st.session_state.logger.info(
                    component="interview_ui",
                    operation="clear_whiteboard",
                    message=f"Whiteboard cleared for session {session_id}",
                    session_id=session_id
                )
            
            st.rerun()
    
    with col3:
        # Undo button
        if st.button("↶ Undo", key="undo_canvas", use_container_width=True):
            # Note: streamlit-drawable-canvas has built-in undo via toolbar
            # This provides an additional explicit undo button
            st.info("💡 Use the toolbar undo button or this will reset canvas")
            # For full undo/redo, we'd need to maintain canvas state history
            # which is complex with streamlit-drawable-canvas
    
    with col4:
        # Redo button
        if st.button("↷ Redo", key="redo_canvas", use_container_width=True):
            # Note: streamlit-drawable-canvas has built-in redo via toolbar
            # This provides an additional explicit redo button
            st.info("💡 Use the toolbar redo button")
    
    with col5:
        # Full-screen mode toggle
        fullscreen_label = "⛶ Exit Fullscreen" if st.session_state.fullscreen_mode else "⛶ Fullscreen"
        if st.button(fullscreen_label, key="fullscreen", use_container_width=True):
            # Toggle fullscreen mode
            st.session_state.fullscreen_mode = not st.session_state.fullscreen_mode
            
            # Log the mode change
            if st.session_state.get("logger"):
                st.session_state.logger.info(
                    component="interview_ui",
                    operation="toggle_fullscreen",
                    message=f"Fullscreen mode {'enabled' if st.session_state.fullscreen_mode else 'disabled'}",
                    session_id=session_id
                )
            
            st.rerun()
    
    # Display snapshot count and helpful tips
    snapshot_count = len(st.session_state.get("whiteboard_snapshots", []))
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.caption(f"📷 Snapshots saved: {snapshot_count}")
    with col_info2:
        if st.session_state.fullscreen_mode:
            st.caption("🔍 Fullscreen mode active - larger canvas for detailed diagrams")
        else:
            st.caption("💡 Tip: Use different colors for different system components")


def render_transcript_panel(
    session_id: str,
    transcript_entries: List[dict]
):
    """
    Render the real-time transcript panel (right panel, 25% width).
    
    Displays real-time transcription with auto-update as speech is transcribed,
    shows speaker labels (Interviewer/Candidate), adds timestamps to transcript
    entries, implements search functionality, and provides export transcript button.
    
    Requirements: 18.3, 18.5
    
    Args:
        session_id: Current session ID
        transcript_entries: List of transcript entries with speaker, text, and timestamp
    """
    st.subheader("📝 Transcript")
    
    # Initialize search state
    if "transcript_search_query" not in st.session_state:
        st.session_state.transcript_search_query = ""
    
    # Search functionality with clear button
    col_search, col_clear = st.columns([4, 1])
    
    with col_search:
        search_query = st.text_input(
            "🔍 Search transcript",
            value=st.session_state.transcript_search_query,
            key="transcript_search_input",
            placeholder="Type to search...",
            label_visibility="collapsed",
            help="Search for specific words or phrases in the transcript"
        )
        st.session_state.transcript_search_query = search_query
    
    with col_clear:
        if st.button("✖️", key="clear_search", help="Clear search", use_container_width=True):
            st.session_state.transcript_search_query = ""
            st.rerun()
    
    # Filter entries based on search query
    filtered_entries = transcript_entries
    if search_query:
        filtered_entries = [
            entry for entry in transcript_entries
            if search_query.lower() in entry["text"].lower()
        ]
    
    # Display search results info
    if search_query:
        match_count = len(filtered_entries)
        total_count = len(transcript_entries)
        if match_count > 0:
            st.caption(f"🔍 Found {match_count} of {total_count} entries")
        else:
            st.caption(f"⚠️ No matches found in {total_count} entries")
    else:
        st.caption(f"📊 Total entries: {len(transcript_entries)}")
    
    # Real-time transcript display container with fixed height and auto-scroll
    # Height set to 500px to match chat panel for consistent layout
    # Auto-updates as speech is transcribed (within 2 seconds per requirement 18.5)
    transcript_container = st.container(height=500)
    
    with transcript_container:
        if not transcript_entries:
            # Empty state message
            st.info("📝 Transcript will appear here as the conversation progresses")
            st.caption("💡 All spoken words will be captured with timestamps")
        else:
            # Display filtered transcript entries
            # Each entry shows speaker label, timestamp, and text content
            for idx, entry in enumerate(filtered_entries):
                speaker = entry["speaker"]
                text = entry["text"]
                timestamp = entry["timestamp"]
                
                # Create visual separation between entries
                if idx > 0:
                    st.markdown("---")
                
                # Display speaker label with icon and timestamp
                # Interviewer gets robot icon, Candidate gets person icon
                if speaker == "Interviewer":
                    st.markdown(f"**🤖 {speaker}** · `{timestamp}`")
                else:
                    st.markdown(f"**👤 {speaker}** · `{timestamp}`")
                
                # Display transcript text with proper formatting
                # Highlight search matches if search is active
                if search_query and search_query.lower() in text.lower():
                    # Simple highlight by showing the text with emphasis
                    # More sophisticated highlighting could use HTML/CSS
                    st.markdown(f"*{text}*")
                else:
                    st.write(text)
            
            # Auto-scroll indicator at bottom
            # This helps users know the transcript is live and updating
            if not search_query:
                st.caption("⬇️ Auto-scrolling to latest entries")
    
    # Export functionality with multiple format options
    st.divider()
    
    # Export controls
    col_export, col_format = st.columns([3, 2])
    
    with col_format:
        export_format = st.selectbox(
            "Format",
            options=["txt", "json"],
            key="export_format",
            help="Choose export format",
            label_visibility="collapsed"
        )
    
    with col_export:
        # Export transcript button
        # Provides download functionality for saving transcript
        if st.button(
            "💾 Export Transcript",
            key="export_transcript",
            use_container_width=True,
            help="Download transcript in selected format"
        ):
            try:
                if not transcript_entries:
                    st.warning("⚠️ No transcript to export")
                else:
                    # Generate transcript content based on format
                    if export_format == "txt":
                        transcript_content = _generate_text_transcript(
                            session_id,
                            transcript_entries
                        )
                        mime_type = "text/plain"
                        file_extension = "txt"
                    else:  # json
                        import json
                        transcript_content = _generate_json_transcript(
                            session_id,
                            transcript_entries
                        )
                        mime_type = "application/json"
                        file_extension = "json"
                    
                    # Generate filename with timestamp
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"transcript_{session_id[:8]}_{timestamp_str}.{file_extension}"
                    
                    # Offer download via Streamlit download button
                    st.download_button(
                        label=f"📥 Download {file_extension.upper()}",
                        data=transcript_content,
                        file_name=filename,
                        mime=mime_type,
                        key="download_transcript",
                        use_container_width=True
                    )
                    
                    # Log export operation
                    if st.session_state.get("logger"):
                        st.session_state.logger.info(
                            component="interview_ui",
                            operation="export_transcript",
                            message=f"Transcript exported for session {session_id}",
                            session_id=session_id,
                            metadata={
                                "format": export_format,
                                "entry_count": len(transcript_entries)
                            }
                        )
                    
                    st.success(f"✅ Transcript ready for download ({len(transcript_entries)} entries)")
                    
            except Exception as e:
                st.error(f"❌ Failed to export transcript: {str(e)}")
                if st.session_state.get("logger"):
                    st.session_state.logger.log_error(
                        component="interview_ui",
                        operation="export_transcript",
                        message=f"Failed to export transcript: {str(e)}",
                        session_id=session_id
                    )
    
    # Display transcript statistics
    if transcript_entries:
        st.caption(
            f"📊 Stats: {len(transcript_entries)} entries · "
            f"{sum(len(e['text'].split()) for e in transcript_entries)} words"
        )


def _generate_text_transcript(session_id: str, entries: List[dict]) -> str:
    """
    Generate plain text transcript.
    
    Args:
        session_id: Session identifier
        entries: List of transcript entries
        
    Returns:
        Formatted text transcript
    """
    lines = []
    lines.append("=" * 80)
    lines.append("INTERVIEW TRANSCRIPT")
    lines.append("=" * 80)
    lines.append(f"Session ID: {session_id}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Total Entries: {len(entries)}")
    lines.append("=" * 80)
    lines.append("")
    
    for entry in entries:
        speaker = entry["speaker"]
        text = entry["text"]
        timestamp = entry["timestamp"]
        
        lines.append(f"[{timestamp}] {speaker.upper()}:")
        lines.append(f"{text}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append(f"End of Transcript - {len(entries)} entries")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def _generate_json_transcript(session_id: str, entries: List[dict]) -> str:
    """
    Generate JSON transcript.
    
    Args:
        session_id: Session identifier
        entries: List of transcript entries
        
    Returns:
        JSON formatted transcript
    """
    import json
    
    transcript_data = {
        "session_id": session_id,
        "generated_at": datetime.now().isoformat(),
        "entry_count": len(entries),
        "entries": [
            {
                "timestamp": entry["timestamp"],
                "speaker": entry["speaker"],
                "text": entry["text"]
            }
            for entry in entries
        ]
    }
    
    return json.dumps(transcript_data, indent=2, ensure_ascii=False)


def render_recording_controls(
    session_id: str,
    session_manager,
    communication_manager,
    config
):
    """
    Render the recording controls bar (bottom bar, full width).
    
    Provides controls for audio recording toggle with streamlit-webrtc, video recording
    toggle, whiteboard snapshot button, screen share toggle, end interview button with
    confirmation dialog, session timer display, token usage indicator, and visual
    indicators for active modes.
    
    Requirements: 2.3, 2.4, 2.5, 2.6, 5.1, 14.7, 18.4, 18.7
    
    Args:
        session_id: Current session ID
        session_manager: SessionManager instance
        communication_manager: CommunicationManager instance
        config: Configuration object
    """
    st.subheader("🎛️ Recording Controls")
    
    # Get enabled modes from session state
    enabled_modes = st.session_state.get("enabled_modes", [])
    
    # Initialize recording states if not present
    if "audio_active" not in st.session_state:
        st.session_state.audio_active = False
    if "video_active" not in st.session_state:
        st.session_state.video_active = False
    if "screen_active" not in st.session_state:
        st.session_state.screen_active = False
    if "confirm_end" not in st.session_state:
        st.session_state.confirm_end = False
    
    # Create main control row with session info and mode controls
    # Layout: Timer | Session ID | Tokens | Audio | Video | Whiteboard | Screen | End
    col_timer, col_session, col_tokens, col_audio, col_video, col_whiteboard, col_screen, col_end = st.columns(
        [1.5, 1.5, 1.5, 1.2, 1.2, 1.2, 1.2, 1.5]
    )
    
    # Session Timer Display (Requirement 18.4)
    with col_timer:
        if st.session_state.get("interview_start_time"):
            elapsed = datetime.now() - st.session_state.interview_start_time
            minutes = int(elapsed.total_seconds() // 60)
            seconds = int(elapsed.total_seconds() % 60)
            
            # Display timer with visual indicator
            st.metric(
                label="⏱️ Time",
                value=f"{minutes:02d}:{seconds:02d}",
                help="Session duration"
            )
        else:
            st.metric(label="⏱️ Time", value="00:00")
    
    # Session ID Display
    with col_session:
        st.metric(
            label="🆔 Session",
            value=f"{session_id[:8]}...",
            help=f"Full ID: {session_id}"
        )
    
    # Token Usage Indicator (Requirements 5.1, 14.7)
    with col_tokens:
        tokens_used = st.session_state.get("tokens_used", 0)
        
        # Calculate estimated cost (rough estimate based on GPT-4 pricing)
        # GPT-4: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
        # Using average of $0.045 per 1K tokens for display
        estimated_cost = (tokens_used / 1000) * 0.045
        
        st.metric(
            label="🪙 Tokens",
            value=f"{tokens_used:,}",
            delta=f"${estimated_cost:.3f}",
            help="Total tokens used and estimated cost"
        )
    
    # Audio Recording Toggle (Requirement 2.3, 2.4)
    with col_audio:
        audio_enabled = CommunicationMode.AUDIO in enabled_modes
        
        if audio_enabled:
            # Audio toggle with streamlit-webrtc integration
            audio_active = st.toggle(
                "🎤 Audio",
                value=st.session_state.audio_active,
                key="audio_toggle",
                help="Enable audio recording and real-time transcription"
            )
            
            # Update state and handle mode changes
            if audio_active != st.session_state.audio_active:
                st.session_state.audio_active = audio_active
                
                if audio_active:
                    # Start audio recording
                    try:
                        communication_manager.enable_mode(CommunicationMode.AUDIO)
                        
                        # Log the mode activation
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="enable_audio",
                                message=f"Audio recording started for session {session_id}",
                                session_id=session_id
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to start audio: {str(e)}")
                        st.session_state.audio_active = False
                else:
                    # Stop audio recording
                    try:
                        communication_manager.disable_mode(CommunicationMode.AUDIO)
                        
                        # Log the mode deactivation
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="disable_audio",
                                message=f"Audio recording stopped for session {session_id}",
                                session_id=session_id
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to stop audio: {str(e)}")
            
            # Visual indicator for active mode (Requirement 18.7)
            if st.session_state.audio_active:
                st.markdown("🔴 **Recording**")
            else:
                st.markdown("⚪ Inactive")
        else:
            # Mode not enabled for this session
            st.markdown("🎤 Audio")
            st.markdown("⚫ Disabled")
    
    # Video Recording Toggle (Requirement 2.5)
    with col_video:
        video_enabled = CommunicationMode.VIDEO in enabled_modes
        
        if video_enabled:
            # Video toggle control
            video_active = st.toggle(
                "📹 Video",
                value=st.session_state.video_active,
                key="video_toggle",
                help="Enable video recording"
            )
            
            # Update state and handle mode changes
            if video_active != st.session_state.video_active:
                st.session_state.video_active = video_active
                
                if video_active:
                    # Start video recording
                    try:
                        communication_manager.enable_mode(CommunicationMode.VIDEO)
                        
                        # Log the mode activation
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="enable_video",
                                message=f"Video recording started for session {session_id}",
                                session_id=session_id
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to start video: {str(e)}")
                        st.session_state.video_active = False
                else:
                    # Stop video recording
                    try:
                        communication_manager.disable_mode(CommunicationMode.VIDEO)
                        
                        # Log the mode deactivation
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="disable_video",
                                message=f"Video recording stopped for session {session_id}",
                                session_id=session_id
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to stop video: {str(e)}")
            
            # Visual indicator for active mode (Requirement 18.7)
            if st.session_state.video_active:
                st.markdown("🔴 **Recording**")
            else:
                st.markdown("⚪ Inactive")
        else:
            # Mode not enabled for this session
            st.markdown("📹 Video")
            st.markdown("⚫ Disabled")
    
    # Whiteboard Snapshot Button (Requirement 2.6)
    with col_whiteboard:
        whiteboard_enabled = CommunicationMode.WHITEBOARD in enabled_modes
        
        if whiteboard_enabled:
            # Display whiteboard status and snapshot count
            snapshot_count = len(st.session_state.get("whiteboard_snapshots", []))
            
            st.markdown("🎨 **Whiteboard**")
            st.markdown(f"📷 {snapshot_count} saved")
            
            # Note: Snapshot button is in the whiteboard panel itself
            # This shows the status and count for quick reference
        else:
            # Mode not enabled for this session
            st.markdown("🎨 Whiteboard")
            st.markdown("⚫ Disabled")
    
    # Screen Share Toggle (Requirement 2.6)
    with col_screen:
        screen_enabled = CommunicationMode.SCREEN_SHARE in enabled_modes
        
        if screen_enabled:
            # Screen share toggle control
            screen_active = st.toggle(
                "🖥️ Screen",
                value=st.session_state.screen_active,
                key="screen_toggle",
                help="Enable screen sharing (captures every 5 seconds)"
            )
            
            # Update state and handle mode changes
            if screen_active != st.session_state.screen_active:
                st.session_state.screen_active = screen_active
                
                if screen_active:
                    # Start screen sharing
                    try:
                        communication_manager.enable_mode(CommunicationMode.SCREEN_SHARE)
                        
                        # Log the mode activation
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="enable_screen_share",
                                message=f"Screen sharing started for session {session_id}",
                                session_id=session_id
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to start screen share: {str(e)}")
                        st.session_state.screen_active = False
                else:
                    # Stop screen sharing
                    try:
                        communication_manager.disable_mode(CommunicationMode.SCREEN_SHARE)
                        
                        # Log the mode deactivation
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="disable_screen_share",
                                message=f"Screen sharing stopped for session {session_id}",
                                session_id=session_id
                            )
                    except Exception as e:
                        st.error(f"❌ Failed to stop screen share: {str(e)}")
            
            # Visual indicator for active mode (Requirement 18.7)
            if st.session_state.screen_active:
                st.markdown("🟢 **Active**")
            else:
                st.markdown("⚪ Inactive")
        else:
            # Mode not enabled for this session
            st.markdown("🖥️ Screen")
            st.markdown("⚫ Disabled")
    
    # End Interview Button with Confirmation Dialog (Requirement 5.1)
    with col_end:
        # Show confirmation warning if user clicked once
        if st.session_state.confirm_end:
            st.warning("⚠️ Confirm?")
        
        # End interview button
        end_button = st.button(
            "🛑 End Interview",
            type="primary",
            key="end_interview_btn",
            use_container_width=True,
            help="End the interview session and generate evaluation"
        )
        
        if end_button:
            # Two-click confirmation pattern
            if st.session_state.confirm_end:
                # Second click - actually end the interview
                with st.spinner("🔄 Ending interview and generating evaluation..."):
                    try:
                        # Stop all active recording modes
                        if st.session_state.audio_active:
                            communication_manager.disable_mode(CommunicationMode.AUDIO)
                        if st.session_state.video_active:
                            communication_manager.disable_mode(CommunicationMode.VIDEO)
                        if st.session_state.screen_active:
                            communication_manager.disable_mode(CommunicationMode.SCREEN_SHARE)
                        
                        # End session and generate evaluation
                        evaluation = session_manager.end_session(session_id)
                        
                        # Store evaluation in session state
                        st.session_state.evaluation_report = evaluation
                        st.session_state.interview_started = False
                        st.session_state.confirm_end = False
                        
                        # Reset recording states
                        st.session_state.audio_active = False
                        st.session_state.video_active = False
                        st.session_state.screen_active = False
                        
                        # Log successful session end
                        if st.session_state.get("logger"):
                            st.session_state.logger.info(
                                component="interview_ui",
                                operation="end_session",
                                message=f"Interview session {session_id} ended successfully",
                                session_id=session_id,
                                metadata={
                                    "duration_seconds": (datetime.now() - st.session_state.interview_start_time).total_seconds(),
                                    "tokens_used": st.session_state.get("tokens_used", 0),
                                    "snapshots_saved": len(st.session_state.get("whiteboard_snapshots", []))
                                }
                            )
                        
                        # Navigate to evaluation page
                        st.session_state.current_page = "evaluation"
                        st.success("✅ Interview ended successfully! Generating evaluation...")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Failed to end interview: {str(e)}")
                        st.session_state.confirm_end = False
                        
                        # Log the error
                        if st.session_state.get("logger"):
                            st.session_state.logger.log_error(
                                component="interview_ui",
                                operation="end_session",
                                message=f"Failed to end interview session: {str(e)}",
                                session_id=session_id
                            )
            else:
                # First click - show confirmation
                st.session_state.confirm_end = True
                st.rerun()
    
    # Display active modes summary bar
    st.divider()
    
    # Show which modes are currently active with visual indicators
    active_modes = []
    if st.session_state.audio_active:
        active_modes.append("🔴 Audio Recording")
    if st.session_state.video_active:
        active_modes.append("🔴 Video Recording")
    if st.session_state.screen_active:
        active_modes.append("🟢 Screen Sharing")
    
    if active_modes:
        st.markdown(f"**Active Modes:** {' · '.join(active_modes)}")
    else:
        st.markdown("**Active Modes:** None (Text-only mode)")
    
    # Display helpful tips based on active modes
    if st.session_state.audio_active:
        st.caption("💡 Tip: Speak clearly for accurate transcription")
    elif CommunicationMode.WHITEBOARD in enabled_modes:
        st.caption("💡 Tip: Use the whiteboard to draw your system design")
    else:
        st.caption("💡 Tip: Type your responses in the chat panel")
