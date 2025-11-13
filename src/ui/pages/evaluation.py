"""
Evaluation display page for interview feedback and assessment.

This module provides the UI for displaying comprehensive evaluation reports
including overall scores, competency breakdowns, categorized feedback,
improvement plans, and communication mode analysis.
"""

import streamlit as st
from typing import Optional, Dict, List
from datetime import datetime
import json

from src.models import EvaluationReport, SessionStatus, CompetencyScore, Feedback, ImprovementPlan, ActionItem, ModeAnalysis


def render_evaluation_page(
    session_manager,
    evaluation_manager,
    config
):
    """
    Render the evaluation page with comprehensive feedback display.
    
    Displays overall score, competency breakdown, categorized feedback,
    improvement plan, and communication mode analysis. Provides navigation
    back to setup or history pages.
    
    Requirements: 6.9
    
    Args:
        session_manager: SessionManager instance
        evaluation_manager: EvaluationManager instance
        config: Configuration object
    """
    # Page header
    st.title("📊 Interview Evaluation")
    st.write("Comprehensive feedback and assessment of your interview performance")
    
    # Check if there's a session to evaluate
    session_id = st.session_state.get("current_session_id")
    
    if not session_id:
        # No session available - show empty state
        render_empty_state()
        return
    
    # Initialize evaluation state
    if "evaluation_report" not in st.session_state:
        st.session_state.evaluation_report = None
    if "evaluation_loading" not in st.session_state:
        st.session_state.evaluation_loading = False
    
    # Check if evaluation already exists
    evaluation_report = st.session_state.evaluation_report
    
    # If no evaluation report, try to load or generate it
    if not evaluation_report:
        try:
            # Try to load existing evaluation from database
            evaluation_report = evaluation_manager.data_store.get_evaluation(session_id)
            st.session_state.evaluation_report = evaluation_report
        except Exception:
            # No existing evaluation - need to generate
            pass
    
    # If still no evaluation, show generation prompt
    if not evaluation_report and not st.session_state.evaluation_loading:
        render_generate_evaluation_prompt(
            session_id,
            session_manager,
            evaluation_manager
        )
        return
    
    # Show loading state while generating
    if st.session_state.evaluation_loading:
        render_loading_state()
        return
    
    # Display the evaluation report
    if evaluation_report:
        render_evaluation_report(evaluation_report)
        
        # Navigation section at bottom
        st.divider()
        render_navigation_section()


def render_empty_state():
    """
    Render empty state when no session is available.
    
    Provides clear messaging and navigation options to start a new interview
    or view past sessions.
    """
    st.info("ℹ️ No interview session available for evaluation")
    
    st.write("To view an evaluation report, you need to:")
    st.write("1. Complete an interview session")
    st.write("2. Generate the evaluation report")
    
    st.divider()
    
    # Navigation options
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
            "📈 View Past Sessions",
            use_container_width=True
        ):
            st.session_state.current_page = "history"
            st.rerun()


def render_generate_evaluation_prompt(
    session_id: str,
    session_manager,
    evaluation_manager
):
    """
    Render prompt to generate evaluation for completed session.
    
    Args:
        session_id: Session identifier
        session_manager: SessionManager instance
        evaluation_manager: EvaluationManager instance
    """
    st.info("📝 Interview session completed - ready to generate evaluation")
    
    # Display session information
    try:
        session = session_manager.get_session(session_id)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Session ID", f"{session_id[:8]}...")
        
        with col2:
            if session.created_at:
                st.metric("Date", session.created_at.strftime("%Y-%m-%d"))
        
        with col3:
            if session.ended_at and session.created_at:
                duration = (session.ended_at - session.created_at).total_seconds() / 60
                st.metric("Duration", f"{int(duration)} min")
    
    except Exception as e:
        st.warning(f"⚠️ Could not load session details: {str(e)}")
    
    st.divider()
    
    # Generate evaluation button
    st.write("Click the button below to generate your comprehensive evaluation report:")
    
    if st.button(
        "🚀 Generate Evaluation Report",
        type="primary",
        use_container_width=True
    ):
        # Set loading state
        st.session_state.evaluation_loading = True
        st.rerun()


def render_loading_state():
    """
    Render loading state while evaluation is being generated.
    
    Shows progress indicator and informative message about the evaluation
    generation process.
    """
    st.info("🔄 Generating your comprehensive evaluation report...")
    
    with st.spinner("Analyzing your interview performance..."):
        st.write("This may take a moment as we:")
        st.write("- 📝 Analyze conversation history")
        st.write("- 🎨 Review whiteboard diagrams")
        st.write("- 📊 Calculate competency scores")
        st.write("- 💡 Generate improvement recommendations")
        
        # Note: Actual generation happens in the background
        # This is just a visual indicator
        st.write("")
        st.write("Please wait...")


def render_evaluation_report(evaluation_report: EvaluationReport):
    """
    Render the complete evaluation report with all sections.
    
    Displays overall score, competency breakdown, categorized feedback,
    improvement plan, and communication mode analysis.
    
    Args:
        evaluation_report: EvaluationReport instance to display
    """
    # Report header with timestamp
    st.caption(f"📅 Generated: {evaluation_report.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.divider()
    
    # Overall Score Section
    render_overall_score(evaluation_report.overall_score)
    
    st.divider()
    
    # Competency Breakdown Section
    render_competency_breakdown(evaluation_report.competency_scores)
    
    st.divider()
    
    # Categorized Feedback Section
    render_categorized_feedback(
        evaluation_report.went_well,
        evaluation_report.went_okay,
        evaluation_report.needs_improvement
    )
    
    st.divider()
    
    # Improvement Plan Section
    render_improvement_plan(evaluation_report.improvement_plan)
    
    st.divider()
    
    # Communication Mode Analysis Section
    render_communication_mode_analysis(evaluation_report.communication_mode_analysis)


def render_overall_score(overall_score: float):
    """
    Render the overall score section with visual indicator.
    
    Displays the overall performance score with a progress bar and color coding
    based on score ranges (excellent/good/needs work).
    
    Requirements: 6.2
    
    Args:
        overall_score: Overall score value (0-100)
    """
    st.subheader("📈 Overall Score")
    
    # Determine score category and color
    score_category, score_color = get_score_category_and_color(overall_score)
    
    # Display score with large metric
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        st.metric(
            label="Overall Performance",
            value=f"{overall_score:.1f}/100",
            delta=score_category
        )
    
    # Display progress bar with color coding
    st.progress(
        overall_score / 100,
        text=f"{score_category} - {overall_score:.1f}%"
    )
    
    # Display score interpretation
    st.markdown(f"**Performance Level:** :{score_color}[{score_category}]")
    
    # Add contextual message based on score
    if overall_score >= 80:
        st.success("🎉 Excellent performance! You demonstrated strong system design skills.")
    elif overall_score >= 60:
        st.info("👍 Good performance! There are some areas where you can improve further.")
    else:
        st.warning("💪 Keep practicing! Focus on the improvement areas highlighted below.")


def render_competency_breakdown(competency_scores: Dict[str, 'CompetencyScore']):
    """
    Render the competency breakdown section with individual scores.
    
    Displays scores for each competency area with confidence levels,
    organized in sections with color coding for score ranges.
    
    Requirements: 6.2, 6.3
    
    Args:
        competency_scores: Dictionary mapping competency names to CompetencyScore objects
    """
    st.subheader("🎯 Competency Breakdown")
    
    if not competency_scores:
        st.info("No competency scores available")
        return
    
    st.write("Detailed assessment of your performance across key competency areas:")
    
    # Display each competency score
    for competency_name, competency_score in competency_scores.items():
        render_competency_card(competency_name, competency_score)


def render_competency_card(competency_name: str, competency_score: 'CompetencyScore'):
    """
    Render a single competency score card.
    
    Displays the competency name, score, confidence level, and visual indicator
    with appropriate color coding.
    
    Args:
        competency_name: Name of the competency
        competency_score: CompetencyScore object with score and confidence
    """
    # Determine score category and color
    score_category, score_color = get_score_category_and_color(competency_score.score)
    
    # Create expandable section for each competency
    with st.expander(
        f"**{format_competency_name(competency_name)}** - {competency_score.score:.1f}/100 "
        f"(:{score_color}[{score_category}])",
        expanded=False
    ):
        # Display score with progress bar
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.progress(
                competency_score.score / 100,
                text=f"Score: {competency_score.score:.1f}/100"
            )
        
        with col2:
            # Display confidence level with icon
            confidence_icon = get_confidence_icon(competency_score.confidence_level)
            st.markdown(f"**Confidence:** {confidence_icon} {competency_score.confidence_level.title()}")
        
        # Display evidence if available
        if competency_score.evidence:
            st.markdown("**Evidence:**")
            for evidence_item in competency_score.evidence:
                st.markdown(f"- {evidence_item}")


def render_categorized_feedback(
    went_well: List['Feedback'],
    went_okay: List['Feedback'],
    needs_improvement: List['Feedback']
):
    """
    Render categorized feedback sections.
    
    Displays three sections of feedback:
    - Went Well: Positive feedback with green styling
    - Went Okay: Moderate feedback with blue styling
    - Needs Improvement: Areas to work on with orange styling
    
    Each section includes specific examples from candidate responses.
    
    Requirements: 6.4, 6.6
    
    Args:
        went_well: List of positive feedback items
        went_okay: List of moderate feedback items
        needs_improvement: List of improvement feedback items
    """
    st.subheader("💬 Detailed Feedback")
    
    st.write("Comprehensive feedback on your interview performance, categorized by strength:")
    
    # Went Well Section (Positive Feedback)
    render_feedback_section(
        title="✅ Went Well",
        feedback_items=went_well,
        color="green",
        icon="🎉",
        empty_message="No specific strengths identified in this session."
    )
    
    st.write("")  # Add spacing
    
    # Went Okay Section (Moderate Feedback)
    render_feedback_section(
        title="👍 Went Okay",
        feedback_items=went_okay,
        color="blue",
        icon="💡",
        empty_message="No moderate performance areas identified."
    )
    
    st.write("")  # Add spacing
    
    # Needs Improvement Section
    render_feedback_section(
        title="🎯 Needs Improvement",
        feedback_items=needs_improvement,
        color="orange",
        icon="📈",
        empty_message="No specific improvement areas identified - great job!"
    )


def render_feedback_section(
    title: str,
    feedback_items: List['Feedback'],
    color: str,
    icon: str,
    empty_message: str
):
    """
    Render a single feedback section with items.
    
    Displays feedback items in an organized format with color coding,
    including descriptions and specific evidence examples.
    
    Args:
        title: Section title
        feedback_items: List of feedback items to display
        color: Color for styling (green, blue, orange)
        icon: Icon emoji for the section
        empty_message: Message to display if no feedback items
    """
    # Section header with color coding
    st.markdown(f"### :{color}[{title}]")
    
    if not feedback_items:
        st.info(empty_message)
        return
    
    # Display count
    st.caption(f"{len(feedback_items)} item(s)")
    
    # Display each feedback item
    for idx, feedback_item in enumerate(feedback_items, 1):
        render_feedback_item(feedback_item, idx, icon, color)


def render_feedback_item(
    feedback_item: 'Feedback',
    index: int,
    icon: str,
    color: str
):
    """
    Render a single feedback item with description and evidence.
    
    Displays the feedback description and specific examples from the
    candidate's responses that support the feedback.
    
    Requirements: 6.6
    
    Args:
        feedback_item: Feedback object to display
        index: Item number in the list
        icon: Icon emoji for the item
        color: Color for styling
    """
    # Create a card-like container for each feedback item
    with st.container():
        # Feedback description with icon and number
        st.markdown(f"**{icon} {index}. {feedback_item.description}**")
        
        # Display evidence if available
        if feedback_item.evidence:
            st.markdown("**Specific Examples:**")
            
            # Display each evidence item as a quote
            for evidence in feedback_item.evidence:
                # Use different styling based on color
                if color == "green":
                    st.success(f"💬 {evidence}", icon="✅")
                elif color == "blue":
                    st.info(f"💬 {evidence}", icon="ℹ️")
                elif color == "orange":
                    st.warning(f"💬 {evidence}", icon="⚠️")
                else:
                    st.markdown(f"> {evidence}")
        else:
            st.caption("_No specific examples recorded_")
        
        # Add spacing between items
        if index < len(feedback_item.evidence):
            st.write("")


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


def get_confidence_icon(confidence_level: str) -> str:
    """
    Get icon for confidence level.
    
    Args:
        confidence_level: Confidence level (high, medium, low)
    
    Returns:
        Icon emoji string
    """
    confidence_icons = {
        "high": "🟢",
        "medium": "🟡",
        "low": "🔴"
    }
    return confidence_icons.get(confidence_level.lower(), "⚪")


def format_competency_name(competency_name: str) -> str:
    """
    Format competency name for display.
    
    Converts snake_case or kebab-case to Title Case.
    
    Args:
        competency_name: Raw competency name
    
    Returns:
        Formatted competency name
    """
    # Replace underscores and hyphens with spaces
    formatted = competency_name.replace("_", " ").replace("-", " ")
    # Convert to title case
    return formatted.title()


def render_improvement_plan(improvement_plan: 'ImprovementPlan'):
    """
    Render the improvement plan section with actionable recommendations.
    
    Displays priority areas, concrete steps to address weaknesses,
    and resources for improvement. Provides export functionality.
    
    Requirements: 6.7, 6.8
    
    Args:
        improvement_plan: ImprovementPlan object with recommendations
    """
    st.subheader("📋 Improvement Plan")
    
    if not improvement_plan:
        st.info("No improvement plan available for this session.")
        return
    
    st.write("Actionable recommendations to enhance your system design interview skills:")
    
    # Priority Areas Section
    if improvement_plan.priority_areas:
        st.markdown("### 🎯 Priority Areas")
        st.write("Focus on these key areas for maximum improvement:")
        
        for idx, area in enumerate(improvement_plan.priority_areas, 1):
            st.markdown(f"**{idx}.** {area}")
        
        st.write("")  # Add spacing
    
    # Concrete Steps Section
    if improvement_plan.concrete_steps:
        st.markdown("### 📝 Action Steps")
        st.write("Follow these concrete steps to address your weaknesses:")
        
        for action_item in improvement_plan.concrete_steps:
            render_action_item(action_item)
        
        st.write("")  # Add spacing
    
    # General Resources Section
    if improvement_plan.resources:
        st.markdown("### 📚 Recommended Resources")
        st.write("Additional resources to support your learning:")
        
        for resource in improvement_plan.resources:
            st.markdown(f"- {resource}")
        
        st.write("")  # Add spacing
    
    # Export Section
    st.divider()
    render_improvement_plan_export(improvement_plan)


def render_action_item(action_item: 'ActionItem'):
    """
    Render a single action item with description and resources.
    
    Displays the step number, description, and any associated resources
    in an organized, easy-to-follow format.
    
    Args:
        action_item: ActionItem object to display
    """
    # Create expandable section for each action item
    with st.expander(
        f"**Step {action_item.step_number}: {action_item.description[:80]}{'...' if len(action_item.description) > 80 else ''}**",
        expanded=True
    ):
        # Full description
        st.markdown(action_item.description)
        
        # Resources specific to this step
        if action_item.resources:
            st.markdown("**Resources for this step:**")
            for resource in action_item.resources:
                st.markdown(f"- {resource}")


def render_improvement_plan_export(improvement_plan: 'ImprovementPlan'):
    """
    Render export functionality for the improvement plan.
    
    Provides options to download or export the improvement plan in
    various formats (text, JSON) for offline reference.
    
    Args:
        improvement_plan: ImprovementPlan object to export
    """
    st.markdown("### 💾 Export Improvement Plan")
    st.write("Download your improvement plan for offline reference:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as formatted text
        text_content = format_improvement_plan_as_text(improvement_plan)
        st.download_button(
            label="📄 Download as Text",
            data=text_content,
            file_name="improvement_plan.txt",
            mime="text/plain",
            use_container_width=True,
            help="Download improvement plan as a formatted text file"
        )
    
    with col2:
        # Export as JSON
        json_content = format_improvement_plan_as_json(improvement_plan)
        st.download_button(
            label="📊 Download as JSON",
            data=json_content,
            file_name="improvement_plan.json",
            mime="application/json",
            use_container_width=True,
            help="Download improvement plan as JSON for programmatic access"
        )


def format_improvement_plan_as_text(improvement_plan: 'ImprovementPlan') -> str:
    """
    Format improvement plan as human-readable text.
    
    Creates a well-formatted text document with all improvement plan
    sections organized for easy reading.
    
    Args:
        improvement_plan: ImprovementPlan object to format
    
    Returns:
        Formatted text string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("IMPROVEMENT PLAN")
    lines.append("=" * 80)
    lines.append("")
    
    # Priority Areas
    if improvement_plan.priority_areas:
        lines.append("PRIORITY AREAS")
        lines.append("-" * 80)
        for idx, area in enumerate(improvement_plan.priority_areas, 1):
            lines.append(f"{idx}. {area}")
        lines.append("")
    
    # Concrete Steps
    if improvement_plan.concrete_steps:
        lines.append("ACTION STEPS")
        lines.append("-" * 80)
        for action_item in improvement_plan.concrete_steps:
            lines.append(f"\nStep {action_item.step_number}:")
            lines.append(f"{action_item.description}")
            
            if action_item.resources:
                lines.append("\nResources:")
                for resource in action_item.resources:
                    lines.append(f"  - {resource}")
            lines.append("")
    
    # General Resources
    if improvement_plan.resources:
        lines.append("RECOMMENDED RESOURCES")
        lines.append("-" * 80)
        for resource in improvement_plan.resources:
            lines.append(f"- {resource}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def format_improvement_plan_as_json(improvement_plan: 'ImprovementPlan') -> str:
    """
    Format improvement plan as JSON.
    
    Creates a JSON representation of the improvement plan for
    programmatic access or integration with other tools.
    
    Args:
        improvement_plan: ImprovementPlan object to format
    
    Returns:
        JSON string
    """
    data = {
        "priority_areas": improvement_plan.priority_areas,
        "concrete_steps": [
            {
                "step_number": action.step_number,
                "description": action.description,
                "resources": action.resources
            }
            for action in improvement_plan.concrete_steps
        ],
        "resources": improvement_plan.resources,
        "generated_at": datetime.now().isoformat()
    }
    
    return json.dumps(data, indent=2)


def render_communication_mode_analysis(mode_analysis: 'ModeAnalysis'):
    """
    Render communication mode analysis section.
    
    Displays analysis of all enabled communication modes including:
    - Audio quality assessment (if used)
    - Video presence assessment (if used)
    - Whiteboard usage assessment (if used)
    - Screen share usage assessment (if used)
    - Overall communication effectiveness
    
    Requirements: 6.5
    
    Args:
        mode_analysis: ModeAnalysis object with communication assessments
    """
    st.subheader("🎙️ Communication Mode Analysis")
    
    if not mode_analysis:
        st.info("No communication mode analysis available for this session.")
        return
    
    st.write("Assessment of how effectively you used different communication modes during the interview:")
    
    # Create a grid layout for mode analysis cards
    has_any_mode = any([
        mode_analysis.audio_quality,
        mode_analysis.video_presence,
        mode_analysis.whiteboard_usage,
        mode_analysis.screen_share_usage
    ])
    
    if not has_any_mode:
        st.info("No communication modes were used during this interview session.")
        return
    
    # Display each enabled mode analysis
    mode_cards = []
    
    if mode_analysis.audio_quality:
        mode_cards.append({
            "title": "🎤 Audio Quality",
            "content": mode_analysis.audio_quality,
            "icon": "🎤"
        })
    
    if mode_analysis.video_presence:
        mode_cards.append({
            "title": "📹 Video Presence",
            "content": mode_analysis.video_presence,
            "icon": "📹"
        })
    
    if mode_analysis.whiteboard_usage:
        mode_cards.append({
            "title": "🎨 Whiteboard Usage",
            "content": mode_analysis.whiteboard_usage,
            "icon": "🎨"
        })
    
    if mode_analysis.screen_share_usage:
        mode_cards.append({
            "title": "🖥️ Screen Share",
            "content": mode_analysis.screen_share_usage,
            "icon": "🖥️"
        })
    
    # Display mode cards in a grid (2 columns)
    for i in range(0, len(mode_cards), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(mode_cards):
                card = mode_cards[i + j]
                with col:
                    render_mode_analysis_card(
                        card["title"],
                        card["content"],
                        card["icon"]
                    )
    
    # Overall communication assessment
    if mode_analysis.overall_communication:
        st.write("")  # Add spacing
        st.markdown("### 📊 Overall Communication Effectiveness")
        
        # Determine assessment level and styling
        assessment_level = get_communication_assessment_level(
            mode_analysis.overall_communication
        )
        
        if assessment_level == "excellent":
            st.success(f"✅ {mode_analysis.overall_communication}")
        elif assessment_level == "good":
            st.info(f"👍 {mode_analysis.overall_communication}")
        else:
            st.warning(f"💡 {mode_analysis.overall_communication}")


def render_mode_analysis_card(title: str, content: str, icon: str):
    """
    Render a single communication mode analysis card.
    
    Displays the mode name, icon, and assessment content in a
    visually organized card format.
    
    Args:
        title: Mode title (e.g., "Audio Quality")
        content: Assessment content
        icon: Icon emoji for the mode
    """
    # Create a card-like container
    with st.container():
        st.markdown(f"**{title}**")
        
        # Determine if the assessment is positive, neutral, or needs improvement
        assessment_type = get_mode_assessment_type(content)
        
        if assessment_type == "positive":
            st.success(content, icon=icon)
        elif assessment_type == "neutral":
            st.info(content, icon=icon)
        else:
            st.warning(content, icon=icon)


def get_mode_assessment_type(content: str) -> str:
    """
    Determine the assessment type based on content keywords.
    
    Analyzes the assessment text to determine if it's positive,
    neutral, or indicates areas for improvement.
    
    Args:
        content: Assessment content text
    
    Returns:
        Assessment type: "positive", "neutral", or "needs_improvement"
    """
    content_lower = content.lower()
    
    # Positive indicators
    positive_keywords = ["excellent", "good", "active", "effective", "strong", "present"]
    if any(keyword in content_lower for keyword in positive_keywords):
        return "positive"
    
    # Negative indicators
    negative_keywords = ["no ", "not used", "limited", "but no", "enabled but"]
    if any(keyword in content_lower for keyword in negative_keywords):
        return "needs_improvement"
    
    # Default to neutral
    return "neutral"


def get_communication_assessment_level(assessment: str) -> str:
    """
    Determine the overall communication assessment level.
    
    Analyzes the overall assessment text to categorize it as
    excellent, good, or basic.
    
    Args:
        assessment: Overall assessment text
    
    Returns:
        Assessment level: "excellent", "good", or "basic"
    """
    assessment_lower = assessment.lower()
    
    if "excellent" in assessment_lower:
        return "excellent"
    elif "good" in assessment_lower:
        return "good"
    else:
        return "basic"


def render_navigation_section():
    """
    Render navigation controls for moving to other pages.
    
    Provides buttons to navigate back to setup page for starting a new
    interview or to history page for viewing past sessions.
    """
    st.subheader("🧭 What's Next?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(
            "🎯 Start New Interview",
            type="primary",
            use_container_width=True,
            help="Go to setup page to configure and start a new interview session"
        ):
            # Clear current session state
            st.session_state.current_session_id = None
            st.session_state.evaluation_report = None
            st.session_state.evaluation_loading = False
            st.session_state.interview_started = False
            
            # Navigate to setup
            st.session_state.current_page = "setup"
            st.rerun()
    
    with col2:
        if st.button(
            "📈 View Session History",
            use_container_width=True,
            help="View all past interview sessions and their evaluations"
        ):
            st.session_state.current_page = "history"
            st.rerun()
    
    with col3:
        if st.button(
            "🔄 Regenerate Evaluation",
            use_container_width=True,
            help="Generate a new evaluation report for this session"
        ):
            # Clear existing evaluation to trigger regeneration
            st.session_state.evaluation_report = None
            st.session_state.evaluation_loading = False
            st.rerun()
