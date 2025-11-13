"""
Session history page for viewing past interview sessions.

This module provides the UI for listing all completed interview sessions,
displaying session metadata, and providing filters and sorting options.
"""

import streamlit as st
from typing import Optional, List
from datetime import datetime, timedelta

from src.models import SessionSummary, SessionStatus, Message, MediaFile


def render_history_page(session_manager, evaluation_manager, config):
    """
    Render the session history page with session list and filters.
    
    Displays all completed sessions from database with metadata including
    date, duration, and overall score. Provides filters and sorting options
    for easy navigation.
    
    Requirements: 7.1
    
    Args:
        session_manager: SessionManager instance
        evaluation_manager: EvaluationManager instance
        config: Configuration object
    """
    # Check if we should show session detail view
    if "selected_session_id" in st.session_state and st.session_state.selected_session_id:
        render_session_detail_view(
            st.session_state.selected_session_id,
            session_manager,
            evaluation_manager
        )
        return
    
    # Page header
    st.title("📈 Session History")
    st.write("View and manage your past interview sessions")
    
    # Initialize session state for filters
    if "history_filter_status" not in st.session_state:
        st.session_state.history_filter_status = "all"
    if "history_sort_by" not in st.session_state:
        st.session_state.history_sort_by = "date_desc"
    if "history_date_range" not in st.session_state:
        st.session_state.history_date_range = "all"
    if "history_page" not in st.session_state:
        st.session_state.history_page = 0
    if "history_page_size" not in st.session_state:
        st.session_state.history_page_size = 10
    
    # Render filters and sorting controls
    render_filters_section()
    
    st.divider()
    
    # Load sessions from database
    sessions = load_sessions(session_manager)
    
    # Apply filters
    filtered_sessions = apply_filters(sessions)
    
    # Apply sorting
    sorted_sessions = apply_sorting(filtered_sessions)
    
    # Calculate pagination
    total_sessions = len(sorted_sessions)
    page_size = st.session_state.history_page_size
    current_page = st.session_state.history_page
    total_pages = (total_sessions + page_size - 1) // page_size if total_sessions > 0 else 1
    
    # Ensure current page is valid
    if current_page >= total_pages:
        st.session_state.history_page = max(0, total_pages - 1)
        current_page = st.session_state.history_page
    
    # Get sessions for current page
    start_idx = current_page * page_size
    end_idx = min(start_idx + page_size, total_sessions)
    paginated_sessions = sorted_sessions[start_idx:end_idx]
    
    # Display session count
    if total_sessions > 0:
        st.caption(f"Showing {start_idx + 1}-{end_idx} of {total_sessions} session(s)")
    else:
        st.caption("No sessions found")
    
    # Display sessions
    if paginated_sessions:
        render_session_list(paginated_sessions, session_manager, evaluation_manager)
        
        # Render pagination controls if needed
        if total_pages > 1:
            render_pagination_controls(current_page, total_pages)
    else:
        render_empty_state()
    
    # Navigation section
    st.divider()
    render_navigation_section()


def render_filters_section():
    """
    Render filters and sorting controls.
    
    Provides UI controls for filtering sessions by status and date range,
    and sorting by different criteria.
    """
    st.subheader("🔍 Filters & Sorting")
    
    # Create columns for filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Status filter
        status_filter = st.selectbox(
            "Status",
            options=["all", "completed", "active", "paused"],
            index=["all", "completed", "active", "paused"].index(
                st.session_state.history_filter_status
            ),
            help="Filter sessions by status"
        )
        st.session_state.history_filter_status = status_filter
    
    with col2:
        # Date range filter
        date_range = st.selectbox(
            "Date Range",
            options=["all", "today", "last_7_days", "last_30_days", "last_90_days"],
            format_func=lambda x: {
                "all": "All Time",
                "today": "Today",
                "last_7_days": "Last 7 Days",
                "last_30_days": "Last 30 Days",
                "last_90_days": "Last 90 Days"
            }[x],
            index=["all", "today", "last_7_days", "last_30_days", "last_90_days"].index(
                st.session_state.history_date_range
            ),
            help="Filter sessions by date range"
        )
        st.session_state.history_date_range = date_range
    
    with col3:
        # Sort by
        sort_by = st.selectbox(
            "Sort By",
            options=["date_desc", "date_asc", "score_desc", "score_asc", "duration_desc", "duration_asc"],
            format_func=lambda x: {
                "date_desc": "Date (Newest First)",
                "date_asc": "Date (Oldest First)",
                "score_desc": "Score (Highest First)",
                "score_asc": "Score (Lowest First)",
                "duration_desc": "Duration (Longest First)",
                "duration_asc": "Duration (Shortest First)"
            }[x],
            index=["date_desc", "date_asc", "score_desc", "score_asc", "duration_desc", "duration_asc"].index(
                st.session_state.history_sort_by
            ),
            help="Sort sessions by different criteria"
        )
        st.session_state.history_sort_by = sort_by


def load_sessions(session_manager) -> List[SessionSummary]:
    """
    Load all sessions from the database.
    
    Loads sessions from the database with a reasonable limit.
    Pagination is handled in the UI layer for better user experience.
    
    Requirements: 7.1, 7.5
    
    Args:
        session_manager: SessionManager instance
    
    Returns:
        List of SessionSummary objects ordered by date (most recent first)
    """
    try:
        # Load sessions with a reasonable limit
        # The database query already orders by created_at DESC (most recent first)
        # UI pagination is applied after filtering and sorting
        sessions = session_manager.list_sessions(limit=1000, offset=0)
        return sessions
    except Exception as e:
        st.error(f"❌ Failed to load sessions: {str(e)}")
        return []


def apply_filters(sessions: List[SessionSummary]) -> List[SessionSummary]:
    """
    Apply filters to session list.
    
    Filters sessions based on status and date range selections.
    
    Args:
        sessions: List of SessionSummary objects
    
    Returns:
        Filtered list of SessionSummary objects
    """
    filtered = sessions
    
    # Apply status filter
    status_filter = st.session_state.history_filter_status
    if status_filter != "all":
        filtered = [
            s for s in filtered
            if s.status.value == status_filter
        ]
    
    # Apply date range filter
    date_range = st.session_state.history_date_range
    if date_range != "all":
        cutoff_date = get_cutoff_date(date_range)
        filtered = [
            s for s in filtered
            if s.created_at >= cutoff_date
        ]
    
    return filtered


def get_cutoff_date(date_range: str) -> datetime:
    """
    Get cutoff date for date range filter.
    
    Args:
        date_range: Date range identifier
    
    Returns:
        Cutoff datetime
    """
    now = datetime.now()
    
    if date_range == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range == "last_7_days":
        return now - timedelta(days=7)
    elif date_range == "last_30_days":
        return now - timedelta(days=30)
    elif date_range == "last_90_days":
        return now - timedelta(days=90)
    else:
        return datetime.min


def apply_sorting(sessions: List[SessionSummary]) -> List[SessionSummary]:
    """
    Apply sorting to session list.
    
    Sorts sessions based on the selected sorting criteria.
    
    Args:
        sessions: List of SessionSummary objects
    
    Returns:
        Sorted list of SessionSummary objects
    """
    sort_by = st.session_state.history_sort_by
    
    if sort_by == "date_desc":
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)
    elif sort_by == "date_asc":
        return sorted(sessions, key=lambda s: s.created_at, reverse=False)
    elif sort_by == "score_desc":
        return sorted(
            sessions,
            key=lambda s: s.overall_score if s.overall_score is not None else -1,
            reverse=True
        )
    elif sort_by == "score_asc":
        return sorted(
            sessions,
            key=lambda s: s.overall_score if s.overall_score is not None else float('inf'),
            reverse=False
        )
    elif sort_by == "duration_desc":
        return sorted(
            sessions,
            key=lambda s: s.duration_minutes if s.duration_minutes is not None else -1,
            reverse=True
        )
    elif sort_by == "duration_asc":
        return sorted(
            sessions,
            key=lambda s: s.duration_minutes if s.duration_minutes is not None else float('inf'),
            reverse=False
        )
    else:
        # Default to date descending
        return sorted(sessions, key=lambda s: s.created_at, reverse=True)


def render_session_list(
    sessions: List[SessionSummary],
    session_manager,
    evaluation_manager
):
    """
    Render the list of sessions.
    
    Displays each session as a card with metadata and action buttons.
    
    Requirements: 7.1, 7.2, 7.5
    
    Args:
        sessions: List of SessionSummary objects to display
        session_manager: SessionManager instance
        evaluation_manager: EvaluationManager instance
    """
    st.subheader("📋 Your Sessions")
    
    # Display sessions in a grid layout
    for session in sessions:
        render_session_card(session, session_manager, evaluation_manager)


def render_session_card(
    session: SessionSummary,
    session_manager,
    evaluation_manager
):
    """
    Render a single session card.
    
    Displays session metadata including date, duration, and overall score
    with appropriate styling and action buttons.
    
    Requirements: 7.2
    
    Args:
        session: SessionSummary object to display
        session_manager: SessionManager instance
        evaluation_manager: EvaluationManager instance
    """
    # Create a card-like container
    with st.container():
        # Card border and padding using columns
        col_main = st.columns([1])[0]
        
        with col_main:
            # Session header with ID and status
            col_header1, col_header2 = st.columns([3, 1])
            
            with col_header1:
                st.markdown(f"### 🎯 Session {session.id[:8]}...")
            
            with col_header2:
                # Status badge
                status_emoji, status_color = get_status_display(session.status)
                st.markdown(
                    f'<span style="background-color: {status_color}; color: white; '
                    f'padding: 5px 10px; border-radius: 15px; display: inline-block; '
                    f'font-size: 12px; font-weight: bold;">'
                    f'{status_emoji} {session.status.value.upper()}</span>',
                    unsafe_allow_html=True
                )
            
            # Session metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Date
                date_str = session.created_at.strftime("%Y-%m-%d %H:%M")
                st.metric("📅 Date", date_str)
            
            with col2:
                # Duration
                if session.duration_minutes is not None:
                    duration_str = f"{session.duration_minutes} min"
                else:
                    duration_str = "N/A"
                st.metric("⏱️ Duration", duration_str)
            
            with col3:
                # Overall score
                if session.overall_score is not None:
                    score_str = f"{session.overall_score:.1f}/100"
                    score_category, score_color = get_score_category_and_color(session.overall_score)
                    st.metric("📊 Score", score_str, delta=score_category)
                else:
                    st.metric("📊 Score", "Not evaluated")
            
            # Action buttons
            st.write("")  # Add spacing
            
            col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
            
            with col_btn1:
                if st.button(
                    "📝 View Details",
                    key=f"view_{session.id}",
                    use_container_width=True
                ):
                    # Navigate to session detail view
                    st.session_state.selected_session_id = session.id
                    st.session_state.current_page = "session_detail"
                    st.rerun()
            
            with col_btn2:
                if session.overall_score is not None:
                    if st.button(
                        "📊 View Evaluation",
                        key=f"eval_{session.id}",
                        use_container_width=True
                    ):
                        # Navigate to evaluation page
                        st.session_state.current_session_id = session.id
                        st.session_state.current_page = "evaluation"
                        st.rerun()
                else:
                    st.button(
                        "📊 No Evaluation",
                        key=f"eval_{session.id}",
                        disabled=True,
                        use_container_width=True
                    )
            
            with col_btn3:
                if st.button(
                    "🔄 Resume Config",
                    key=f"resume_{session.id}",
                    use_container_width=True,
                    help="Start new session with same configuration"
                ):
                    # Load session configuration and navigate to setup
                    st.session_state.resume_from_session_id = session.id
                    st.session_state.current_page = "setup"
                    st.rerun()
            
            with col_btn4:
                if st.button(
                    "📥 Export",
                    key=f"export_{session.id}",
                    use_container_width=True,
                    help="Export session data"
                ):
                    # Show export options
                    st.session_state.export_session_id = session.id
                    st.info("Export functionality coming soon!")
        
        # Divider between cards
        st.divider()


def get_status_display(status: SessionStatus) -> tuple[str, str]:
    """
    Get display emoji and color for session status.
    
    Args:
        status: SessionStatus enum value
    
    Returns:
        Tuple of (emoji, color_hex)
    """
    if status == SessionStatus.COMPLETED:
        return ("✅", "#28a745")
    elif status == SessionStatus.ACTIVE:
        return ("🟢", "#007bff")
    elif status == SessionStatus.PAUSED:
        return ("⏸️", "#ffc107")
    else:
        return ("⚪", "#6c757d")


def get_score_category_and_color(score: float) -> tuple[str, str]:
    """
    Determine score category and color based on score value.
    
    Uses color coding for score ranges:
    - Excellent (80-100): green
    - Good (60-79): blue
    - Needs Work (<60): orange
    
    Args:
        score: Score value (0-100)
    
    Returns:
        Tuple of (category_name, color_name)
    """
    if score >= 80:
        return ("Excellent", "green")
    elif score >= 60:
        return ("Good", "blue")
    else:
        return ("Needs Work", "orange")


def render_pagination_controls(current_page: int, total_pages: int):
    """
    Render pagination controls for navigating through sessions.
    
    Displays page navigation buttons and page size selector when
    there are many sessions to display.
    
    Args:
        current_page: Current page index (0-based)
        total_pages: Total number of pages
    """
    st.divider()
    
    # Create columns for pagination controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        # First page button
        if st.button("⏮️ First", disabled=current_page == 0, use_container_width=True):
            st.session_state.history_page = 0
            st.rerun()
    
    with col2:
        # Previous page button
        if st.button("◀️ Prev", disabled=current_page == 0, use_container_width=True):
            st.session_state.history_page = max(0, current_page - 1)
            st.rerun()
    
    with col3:
        # Page indicator and page size selector
        col_page, col_size = st.columns(2)
        
        with col_page:
            st.markdown(
                f'<div style="text-align: center; padding: 8px; font-weight: bold;">'
                f'Page {current_page + 1} of {total_pages}</div>',
                unsafe_allow_html=True
            )
        
        with col_size:
            # Page size selector
            page_size = st.selectbox(
                "Per page",
                options=[10, 25, 50, 100],
                index=[10, 25, 50, 100].index(st.session_state.history_page_size),
                key="page_size_selector",
                label_visibility="collapsed"
            )
            if page_size != st.session_state.history_page_size:
                st.session_state.history_page_size = page_size
                st.session_state.history_page = 0  # Reset to first page
                st.rerun()
    
    with col4:
        # Next page button
        if st.button("Next ▶️", disabled=current_page >= total_pages - 1, use_container_width=True):
            st.session_state.history_page = min(total_pages - 1, current_page + 1)
            st.rerun()
    
    with col5:
        # Last page button
        if st.button("Last ⏭️", disabled=current_page >= total_pages - 1, use_container_width=True):
            st.session_state.history_page = total_pages - 1
            st.rerun()


def render_empty_state():
    """
    Render empty state when no sessions match filters.
    
    Provides clear messaging and suggestions for the user.
    """
    st.info("📭 No sessions found matching your filters")
    
    st.write("Try adjusting your filters or start a new interview session.")
    
    # Suggestions
    with st.expander("💡 Suggestions"):
        st.write("- Change the status filter to 'All'")
        st.write("- Expand the date range to 'All Time'")
        st.write("- Start a new interview session")


def render_navigation_section():
    """
    Render navigation section with action buttons.
    
    Provides buttons to navigate to other pages like setup or current session.
    """
    st.subheader("🧭 Navigation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "🎯 Start New Interview",
            type="primary",
            use_container_width=True
        ):
            st.session_state.current_page = "setup"
            st.rerun()
    
    with col2:
        if st.button(
            "🏠 Back to Home",
            use_container_width=True
        ):
            st.session_state.current_page = "setup"
            st.rerun()



def render_session_detail_view(session_id: str, session_manager, evaluation_manager):
    """
    Render detailed view for a selected session.
    
    Displays full session details including conversation history with timestamps,
    whiteboard snapshots in gallery view, and evaluation report summary.
    
    Requirements: 7.3, 7.4
    
    Args:
        session_id: Session identifier to display
        session_manager: SessionManager instance
        evaluation_manager: EvaluationManager instance
    """
    # Back button
    if st.button("⬅️ Back to Session List"):
        st.session_state.selected_session_id = None
        st.rerun()
    
    st.divider()
    
    # Load session data
    session = session_manager.get_session(session_id)
    
    if not session:
        st.error(f"❌ Session {session_id} not found")
        if st.button("Return to List"):
            st.session_state.selected_session_id = None
            st.rerun()
        return
    
    # Page header
    st.title(f"📋 Session Details")
    st.caption(f"Session ID: {session_id}")
    
    # Session metadata section
    render_session_metadata_section(session)
    
    st.divider()
    
    # Load conversation history
    conversation_history = session_manager.data_store.get_conversation_history(session_id)
    
    # Load media files
    media_files = session_manager.data_store.get_media_files(session_id)
    
    # Load evaluation if available
    evaluation = session_manager.data_store.get_evaluation(session_id)
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs([
        "💬 Conversation History",
        "🎨 Whiteboard Gallery",
        "📊 Evaluation Summary"
    ])
    
    with tab1:
        render_conversation_history_section(conversation_history)
    
    with tab2:
        render_whiteboard_gallery_section(media_files)
    
    with tab3:
        render_evaluation_summary_section(evaluation, session_id)
    
    # Export and action buttons
    st.divider()
    render_session_actions(session_id, conversation_history, media_files)


def render_session_metadata_section(session):
    """
    Render session metadata section.
    
    Displays key session information including dates, duration, status,
    and configuration.
    
    Args:
        session: Session object
    """
    st.subheader("📌 Session Information")
    
    # Create columns for metadata
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Status
        status_emoji, status_color = get_status_display(session.status)
        st.markdown(
            f'<div style="text-align: center;">'
            f'<div style="font-size: 12px; color: #666; margin-bottom: 5px;">Status</div>'
            f'<span style="background-color: {status_color}; color: white; '
            f'padding: 5px 10px; border-radius: 15px; display: inline-block; '
            f'font-size: 14px; font-weight: bold;">'
            f'{status_emoji} {session.status.value.upper()}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    
    with col2:
        # Created date
        created_str = session.created_at.strftime("%Y-%m-%d %H:%M:%S")
        st.metric("📅 Created", created_str)
    
    with col3:
        # Ended date
        if session.ended_at:
            ended_str = session.ended_at.strftime("%Y-%m-%d %H:%M:%S")
            st.metric("🏁 Ended", ended_str)
        else:
            st.metric("🏁 Ended", "N/A")
    
    with col4:
        # Duration
        if session.ended_at:
            duration = session.ended_at - session.created_at
            duration_minutes = int(duration.total_seconds() / 60)
            st.metric("⏱️ Duration", f"{duration_minutes} min")
        else:
            st.metric("⏱️ Duration", "N/A")
    
    # Configuration details
    with st.expander("⚙️ Session Configuration", expanded=False):
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            st.write("**AI Provider:**", session.config.ai_provider)
            st.write("**AI Model:**", session.config.ai_model)
        
        with col_config2:
            st.write("**Communication Modes:**")
            for mode in session.config.enabled_modes:
                mode_emoji = {
                    "audio": "🎤",
                    "video": "📹",
                    "whiteboard": "🎨",
                    "screen_share": "🖥️",
                    "text": "💬"
                }.get(mode.value, "📝")
                st.write(f"  {mode_emoji} {mode.value.replace('_', ' ').title()}")


def render_conversation_history_section(conversation_history: List):
    """
    Render conversation history section with timestamps.
    
    Displays all messages exchanged during the interview session
    with timestamps and speaker labels.
    
    Requirements: 7.3
    
    Args:
        conversation_history: List of Message objects
    """
    st.subheader("💬 Conversation History")
    
    if not conversation_history:
        st.info("📭 No conversation history available for this session")
        return
    
    st.caption(f"Total messages: {len(conversation_history)}")
    
    # Display messages in chronological order
    for message in conversation_history:
        render_message_card(message)


def render_message_card(message):
    """
    Render a single message card.
    
    Displays message content with timestamp and role indicator.
    
    Args:
        message: Message object
    """
    # Determine styling based on role
    if message.role == "interviewer":
        avatar = "🤖"
        bg_color = "#f0f8ff"
        border_color = "#4a90e2"
    else:
        avatar = "👤"
        bg_color = "#f5f5f5"
        border_color = "#888888"
    
    # Format timestamp
    timestamp_str = message.timestamp.strftime("%H:%M:%S")
    
    # Create message container
    st.markdown(
        f'<div style="background-color: {bg_color}; border-left: 4px solid {border_color}; '
        f'padding: 15px; margin: 10px 0; border-radius: 5px;">'
        f'<div style="display: flex; justify-content: space-between; margin-bottom: 8px;">'
        f'<span style="font-weight: bold; color: {border_color};">'
        f'{avatar} {message.role.title()}</span>'
        f'<span style="color: #666; font-size: 12px;">{timestamp_str}</span>'
        f'</div>'
        f'<div style="color: #333; line-height: 1.6;">{message.content}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


def render_whiteboard_gallery_section(media_files: List):
    """
    Render whiteboard gallery section.
    
    Displays whiteboard snapshots in a gallery view with timestamps.
    
    Requirements: 7.3, 7.4
    
    Args:
        media_files: List of MediaFile objects
    """
    st.subheader("🎨 Whiteboard Gallery")
    
    # Filter for whiteboard files
    whiteboard_files = [
        f for f in media_files
        if f.file_type == "whiteboard"
    ]
    
    if not whiteboard_files:
        st.info("📭 No whiteboard snapshots available for this session")
        return
    
    st.caption(f"Total snapshots: {len(whiteboard_files)}")
    
    # Display whiteboard snapshots in a grid
    # Use 2 columns for better visibility
    cols_per_row = 2
    
    for i in range(0, len(whiteboard_files), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(whiteboard_files):
                with cols[j]:
                    render_whiteboard_snapshot(whiteboard_files[idx], idx + 1)


def render_whiteboard_snapshot(media_file, snapshot_number: int):
    """
    Render a single whiteboard snapshot.
    
    Displays whiteboard image with timestamp and download option.
    
    Args:
        media_file: MediaFile object
        snapshot_number: Sequential snapshot number
    """
    import os
    
    # Format timestamp
    timestamp_str = media_file.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    # Display snapshot info
    st.markdown(f"**Snapshot #{snapshot_number}**")
    st.caption(f"📅 {timestamp_str}")
    
    # Display image if file exists
    if os.path.exists(media_file.file_path):
        try:
            st.image(
                media_file.file_path,
                use_container_width=True,
                caption=f"Snapshot {snapshot_number}"
            )
            
            # Download button
            with open(media_file.file_path, "rb") as f:
                st.download_button(
                    label="📥 Download",
                    data=f.read(),
                    file_name=f"whiteboard_snapshot_{snapshot_number}.png",
                    mime="image/png",
                    key=f"download_wb_{media_file.file_path}_{snapshot_number}",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Failed to load image: {str(e)}")
    else:
        st.warning(f"⚠️ Image file not found: {media_file.file_path}")
    
    st.divider()


def render_evaluation_summary_section(evaluation, session_id: str):
    """
    Render evaluation summary section.
    
    Displays key evaluation metrics and provides link to full evaluation report.
    
    Requirements: 7.3, 7.4
    
    Args:
        evaluation: EvaluationReport object or None
        session_id: Session identifier
    """
    st.subheader("📊 Evaluation Summary")
    
    if not evaluation:
        st.info("📭 No evaluation available for this session")
        st.write("The evaluation may not have been generated yet, or the session may still be active.")
        return
    
    # Overall score
    st.metric(
        "🎯 Overall Score",
        f"{evaluation.overall_score:.1f}/100",
        delta=get_score_category_and_color(evaluation.overall_score)[0]
    )
    
    st.write("")
    
    # Competency scores
    st.write("**📈 Competency Scores:**")
    
    # Display top competencies
    competency_items = list(evaluation.competency_scores.items())
    
    if competency_items:
        # Create columns for competency scores
        num_cols = min(3, len(competency_items))
        cols = st.columns(num_cols)
        
        for idx, (competency, score_data) in enumerate(competency_items[:6]):
            col_idx = idx % num_cols
            with cols[col_idx]:
                # Format competency name
                competency_display = competency.replace("_", " ").title()
                
                # Display score with confidence indicator
                confidence_emoji = {
                    "high": "🟢",
                    "medium": "🟡",
                    "low": "🔴"
                }.get(score_data.confidence_level.lower(), "⚪")
                
                st.metric(
                    f"{competency_display}",
                    f"{score_data.score:.1f}",
                    delta=f"{confidence_emoji} {score_data.confidence_level}"
                )
    
    st.write("")
    
    # Feedback summary
    col_feedback1, col_feedback2, col_feedback3 = st.columns(3)
    
    with col_feedback1:
        st.metric("✅ Went Well", len(evaluation.went_well))
    
    with col_feedback2:
        st.metric("⚠️ Went Okay", len(evaluation.went_okay))
    
    with col_feedback3:
        st.metric("🔴 Needs Improvement", len(evaluation.needs_improvement))
    
    st.write("")
    
    # Link to full evaluation
    if st.button("📊 View Full Evaluation Report", type="primary", use_container_width=True):
        st.session_state.current_session_id = session_id
        st.session_state.current_page = "evaluation"
        st.session_state.selected_session_id = None  # Clear selection
        st.rerun()


def render_session_actions(session_id: str, conversation_history: List, media_files: List):
    """
    Render session action buttons.
    
    Provides options to export conversation history, download media files,
    and start new session with same configuration.
    
    Requirements: 7.4
    
    Args:
        session_id: Session identifier
        conversation_history: List of Message objects
        media_files: List of MediaFile objects
    """
    st.subheader("🔧 Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export conversation history
        if st.button("📥 Export Conversation", use_container_width=True):
            export_conversation_history(conversation_history, session_id)
    
    with col2:
        # Download whiteboard snapshots
        whiteboard_files = [f for f in media_files if f.file_type == "whiteboard"]
        if whiteboard_files:
            if st.button("🎨 Download All Whiteboards", use_container_width=True):
                st.info("💡 Use the download buttons in the Whiteboard Gallery tab to download individual snapshots")
        else:
            st.button("🎨 No Whiteboards", disabled=True, use_container_width=True)
    
    with col3:
        # Start new session with same config
        if st.button("🔄 Use This Config", use_container_width=True):
            st.session_state.resume_from_session_id = session_id
            st.session_state.current_page = "setup"
            st.session_state.selected_session_id = None  # Clear selection
            st.rerun()


def export_conversation_history(conversation_history: List, session_id: str):
    """
    Export conversation history as downloadable text file.
    
    Creates a formatted text file with all conversation messages
    and timestamps.
    
    Args:
        conversation_history: List of Message objects
        session_id: Session identifier
    """
    if not conversation_history:
        st.warning("⚠️ No conversation history to export")
        return
    
    # Format conversation as text
    export_text = f"Conversation History - Session {session_id}\n"
    export_text += "=" * 80 + "\n\n"
    
    for message in conversation_history:
        timestamp_str = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        role_display = message.role.upper()
        export_text += f"[{timestamp_str}] {role_display}:\n"
        export_text += f"{message.content}\n\n"
        export_text += "-" * 80 + "\n\n"
    
    # Provide download button
    st.download_button(
        label="💾 Download Conversation History",
        data=export_text,
        file_name=f"conversation_history_{session_id[:8]}.txt",
        mime="text/plain",
        use_container_width=True
    )
