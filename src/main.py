"""
AI Mock Interview Platform - Main Entry Point
"""

import streamlit as st
from src.app_factory import create_app
from src.ui.pages.setup import render_setup_page
from src.ui.pages.interview import render_interview_page
from src.ui.pages.evaluation import render_evaluation_page
from src.ui.pages.history import render_history_page


def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="AI Mock Interview Platform",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize application components
    if "app_components" not in st.session_state:
        try:
            with st.spinner("Initializing application..."):
                st.session_state.app_components = create_app()
        except Exception as e:
            st.error(f"❌ Failed to initialize application: {str(e)}")
            st.stop()
    
    # Get components from session state
    components = st.session_state.app_components
    
    # Initialize page state
    if "current_page" not in st.session_state:
        st.session_state.current_page = "setup"
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🎯 Navigation")
        
        page = st.radio(
            "Select Page",
            options=["setup", "interview", "evaluation", "history"],
            format_func=lambda x: {
                "setup": "📄 Setup",
                "interview": "🎤 Interview",
                "evaluation": "📊 Evaluation",
                "history": "📈 History"
            }[x],
            index=["setup", "interview", "evaluation", "history"].index(st.session_state.current_page)
        )
        
        st.session_state.current_page = page
        
        st.divider()
        
        # Display session info if available
        if st.session_state.get("current_session_id"):
            st.subheader("Current Session")
            st.write(f"ID: {st.session_state.current_session_id[:8]}...")
            
            if st.button("End Session"):
                st.session_state.current_page = "evaluation"
                st.rerun()
        
        st.divider()
        
        # Application info
        st.subheader("About")
        st.write("AI Mock Interview Platform")
        st.write("Version 1.0.0")
    
    # Render current page
    if st.session_state.current_page == "setup":
        render_setup_page(
            components["resume_manager"],
            components["session_manager"],
            components["config"]
        )
    elif st.session_state.current_page == "interview":
        render_interview_page(
            components["session_manager"],
            components["communication_manager"],
            components["ai_interviewer"],
            components["config"]
        )
    elif st.session_state.current_page == "evaluation":
        render_evaluation_page(
            components["session_manager"],
            components["evaluation_manager"],
            components["config"]
        )
    elif st.session_state.current_page == "history":
        render_history_page(
            components["session_manager"],
            components["evaluation_manager"],
            components["config"]
        )


if __name__ == "__main__":
    main()
