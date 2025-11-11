"""
Setup page for resume upload and interview configuration.

This module provides the UI for uploading resumes, configuring AI providers,
selecting communication modes, and starting interview sessions.
"""

import streamlit as st
import tempfile
import os
from pathlib import Path
from typing import Optional, List

from src.models import ResumeData, SessionConfig, CommunicationMode
from src.exceptions import ValidationError, AIProviderError


def render_setup_page(resume_manager, session_manager, config):
    """
    Render the setup page for interview configuration.
    
    Args:
        resume_manager: ResumeManager instance
        session_manager: SessionManager instance
        config: Configuration object
    """
    st.title("🎯 Interview Setup")
    st.write("Configure your interview session and upload your resume")
    
    # Initialize session state
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = None
    if "resume_uploaded" not in st.session_state:
        st.session_state.resume_uploaded = False
    if "ai_provider" not in st.session_state:
        st.session_state.ai_provider = None
    if "ai_model" not in st.session_state:
        st.session_state.ai_model = None
    if "enabled_modes" not in st.session_state:
        st.session_state.enabled_modes = []
    
    # Create tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📄 Resume Upload", "🤖 AI Configuration", "🎙️ Communication Modes"])
    
    # Tab 1: Resume Upload
    with tab1:
        render_resume_upload_section(resume_manager)
    
    # Tab 2: AI Provider Configuration
    with tab2:
        render_ai_configuration_section(config)
    
    # Tab 3: Communication Mode Selection
    with tab3:
        render_communication_mode_section()
    
    # Start Interview Button
    st.divider()
    render_start_interview_button(session_manager, config)


def render_resume_upload_section(resume_manager):
    """
    Render the resume upload section.
    
    Args:
        resume_manager: ResumeManager instance
    """
    st.header("📄 Upload Your Resume")
    st.write("Upload your resume to enable resume-aware interview questions")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF or TXT file",
        type=["pdf", "txt"],
        help="Upload your resume in PDF or text format"
    )
    
    if uploaded_file is not None:
        # Display upload progress
        with st.spinner("Processing resume..."):
            try:
                # Save uploaded file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # Generate user_id from filename (or use existing)
                user_id = st.session_state.get("user_id", f"user_{uploaded_file.name.split('.')[0]}")
                st.session_state.user_id = user_id
                
                # Parse resume
                resume_data = resume_manager.upload_resume(tmp_file_path, user_id)
                
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
                # Store in session state
                st.session_state.resume_data = resume_data
                st.session_state.resume_uploaded = True
                
                st.success("✅ Resume uploaded and analyzed successfully!")
                
            except ValidationError as e:
                st.error(f"❌ Validation Error: {str(e)}")
                st.session_state.resume_uploaded = False
            except AIProviderError as e:
                st.error(f"❌ AI Provider Error: {str(e)}")
                st.session_state.resume_uploaded = False
            except Exception as e:
                st.error(f"❌ Unexpected Error: {str(e)}")
                st.session_state.resume_uploaded = False
    
    # Display resume analysis results if available
    if st.session_state.resume_uploaded and st.session_state.resume_data:
        render_resume_analysis_results(st.session_state.resume_data)


def render_resume_analysis_results(resume_data: ResumeData):
    """
    Display resume analysis results.
    
    Args:
        resume_data: Parsed ResumeData object
    """
    st.subheader("📊 Resume Analysis")
    
    # Create columns for key information
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Name", resume_data.name or "Not found")
    
    with col2:
        st.metric("Experience Level", resume_data.experience_level.upper())
    
    with col3:
        st.metric("Years of Experience", resume_data.years_of_experience)
    
    # Display domain expertise as badges
    if resume_data.domain_expertise:
        st.subheader("💼 Domain Expertise")
        # Create badge-like display using columns
        cols = st.columns(min(len(resume_data.domain_expertise), 4))
        for idx, domain in enumerate(resume_data.domain_expertise):
            with cols[idx % 4]:
                st.markdown(
                    f'<span style="background-color: #0066cc; color: white; padding: 5px 10px; '
                    f'border-radius: 15px; display: inline-block; margin: 2px; font-size: 14px;">'
                    f'{domain}</span>',
                    unsafe_allow_html=True
                )
    
    # Display work experience summary
    if resume_data.work_experience:
        st.subheader("💼 Work Experience")
        for exp in resume_data.work_experience[:3]:  # Show first 3
            with st.expander(f"{exp.title} at {exp.company}"):
                st.write(f"**Duration:** {exp.duration}")
                st.write(f"**Description:** {exp.description}")
    
    # Display education summary
    if resume_data.education:
        st.subheader("🎓 Education")
        for edu in resume_data.education[:2]:  # Show first 2
            st.write(f"• {edu.degree} in {edu.field} - {edu.institution} ({edu.year})")
    
    # Display skills
    if resume_data.skills:
        st.subheader("🛠️ Skills")
        skills_text = ", ".join(resume_data.skills[:10])  # Show first 10
        st.write(skills_text)


def render_ai_configuration_section(config):
    """
    Render the AI provider configuration section.
    
    Args:
        config: Configuration object
    """
    st.header("🤖 AI Provider Configuration")
    st.write("Select your preferred AI provider and model")
    
    # Get available providers
    available_providers = []
    provider_models = {}
    
    for provider_name, provider_config in config.ai_providers.items():
        if provider_config.api_key:
            available_providers.append(provider_name)
            provider_models[provider_name] = provider_config.default_model
    
    if not available_providers:
        st.error("❌ No AI providers configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        return
    
    # Provider selection
    selected_provider = st.selectbox(
        "Select AI Provider",
        options=available_providers,
        format_func=lambda x: f"OpenAI GPT-4" if x == "openai" else f"Anthropic Claude",
        help="Choose the AI provider for conducting the interview"
    )
    
    # Store in session state
    st.session_state.ai_provider = selected_provider
    st.session_state.ai_model = provider_models[selected_provider]
    
    # Display provider information
    st.info(f"✅ Using **{selected_provider.upper()}** with model **{provider_models[selected_provider]}**")
    
    # Validate credentials
    if st.button("🔍 Validate API Credentials"):
        with st.spinner("Validating credentials..."):
            try:
                # Attempt to validate by checking if the provider is properly configured
                if selected_provider == "openai":
                    import openai
                    client = openai.OpenAI(api_key=config.ai_providers[selected_provider].api_key)
                    # Simple test call
                    response = client.chat.completions.create(
                        model=provider_models[selected_provider],
                        messages=[{"role": "user", "content": "test"}],
                        max_tokens=5
                    )
                    st.success("✅ OpenAI credentials are valid!")
                elif selected_provider == "anthropic":
                    import anthropic
                    client = anthropic.Anthropic(api_key=config.ai_providers[selected_provider].api_key)
                    # Simple test call
                    response = client.messages.create(
                        model=provider_models[selected_provider],
                        max_tokens=5,
                        messages=[{"role": "user", "content": "test"}]
                    )
                    st.success("✅ Anthropic credentials are valid!")
            except ImportError as e:
                st.error(f"❌ Required library not installed: {str(e)}")
            except Exception as e:
                st.error(f"❌ Invalid credentials or API error: {str(e)}")


def render_communication_mode_section():
    """
    Render the communication mode selection section.
    """
    st.header("🎙️ Communication Modes")
    st.write("Select the communication modes you want to use during the interview")
    
    # Create checkboxes for each mode
    col1, col2 = st.columns(2)
    
    with col1:
        audio_enabled = st.checkbox(
            "🎤 Audio",
            value=False,
            help="Enable audio recording and real-time transcription"
        )
        
        video_enabled = st.checkbox(
            "📹 Video",
            value=False,
            help="Enable video recording"
        )
    
    with col2:
        whiteboard_enabled = st.checkbox(
            "🎨 Whiteboard",
            value=True,  # Default to enabled for system design
            help="Enable interactive whiteboard for diagrams"
        )
        
        screen_share_enabled = st.checkbox(
            "🖥️ Screen Share",
            value=False,
            help="Enable screen sharing capability"
        )
    
    # Build list of enabled modes
    enabled_modes = []
    if audio_enabled:
        enabled_modes.append(CommunicationMode.AUDIO)
    if video_enabled:
        enabled_modes.append(CommunicationMode.VIDEO)
    if whiteboard_enabled:
        enabled_modes.append(CommunicationMode.WHITEBOARD)
    if screen_share_enabled:
        enabled_modes.append(CommunicationMode.SCREEN_SHARE)
    
    # Always include text mode
    enabled_modes.append(CommunicationMode.TEXT)
    
    # Store in session state
    st.session_state.enabled_modes = enabled_modes
    
    # Display selected modes
    if enabled_modes:
        st.info(f"✅ Selected modes: {', '.join([mode.value for mode in enabled_modes])}")
    else:
        st.warning("⚠️ Please select at least one communication mode")


def render_start_interview_button(session_manager, config):
    """
    Render the start interview button and handle session creation.
    
    Args:
        session_manager: SessionManager instance
        config: Configuration object
    """
    st.header("🚀 Start Interview")
    
    # Check if all required configurations are set
    can_start = True
    missing_items = []
    
    if not st.session_state.get("ai_provider"):
        can_start = False
        missing_items.append("AI Provider")
    
    if not st.session_state.get("enabled_modes"):
        can_start = False
        missing_items.append("Communication Modes")
    
    if missing_items:
        st.warning(f"⚠️ Please configure: {', '.join(missing_items)}")
    
    # Display resume status
    if st.session_state.get("resume_uploaded"):
        st.success("✅ Resume uploaded - Interview will be tailored to your experience")
    else:
        st.info("ℹ️ No resume uploaded - Interview will use general questions")
    
    # Start interview button
    if st.button(
        "🎯 Start Interview",
        type="primary",
        disabled=not can_start,
        use_container_width=True
    ):
        with st.spinner("Creating interview session..."):
            try:
                # Create session configuration
                session_config = SessionConfig(
                    enabled_modes=st.session_state.enabled_modes,
                    ai_provider=st.session_state.ai_provider,
                    ai_model=st.session_state.ai_model,
                    resume_data=st.session_state.get("resume_data"),
                    duration_minutes=config.session.default_duration_minutes
                )
                
                # Create session
                session = session_manager.create_session(session_config)
                
                # Store session ID in session state
                st.session_state.current_session_id = session.id
                st.session_state.session_created = True
                
                st.success(f"✅ Session created successfully! Session ID: {session.id[:8]}...")
                
                # Navigate to interview interface
                st.info("🎯 Redirecting to interview interface...")
                st.session_state.current_page = "interview"
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to create session: {str(e)}")
