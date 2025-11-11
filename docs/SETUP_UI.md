# Setup UI Implementation

## Overview

The Setup UI provides the interview configuration interface where users can upload their resume, configure AI providers, select communication modes, and start interview sessions.

## Components

### 1. Resume Upload Section (`render_resume_upload_section`)

**Features:**
- File uploader supporting PDF and TXT formats
- Real-time resume parsing using LLM
- Progress indicator during upload
- Error handling with clear messages

**Resume Analysis Display:**
- Candidate name, experience level, and years of experience
- Domain expertise displayed as styled badges
- Work experience summary (first 3 entries)
- Education summary (first 2 entries)
- Skills list (first 10 skills)

### 2. AI Provider Configuration (`render_ai_configuration_section`)

**Features:**
- Dropdown selection for OpenAI GPT-4 or Anthropic Claude
- Automatic detection of available providers based on API keys
- API credential validation with test calls
- Clear error messages for missing or invalid credentials

**Supported Providers:**
- OpenAI GPT-4 (requires OPENAI_API_KEY)
- Anthropic Claude (requires ANTHROPIC_API_KEY)

### 3. Communication Mode Selection (`render_communication_mode_section`)

**Features:**
- Checkboxes for each communication mode:
  - 🎤 Audio (recording and transcription)
  - 📹 Video (recording)
  - 🎨 Whiteboard (system design diagrams) - default enabled
  - 🖥️ Screen Share (periodic captures)
- Multiple modes can be enabled simultaneously
- Text mode is always included
- Visual confirmation of selected modes

### 4. Start Interview Button (`render_start_interview_button`)

**Features:**
- Validation of required configurations
- Clear indication of missing items
- Session creation with all selected configurations
- Automatic navigation to interview interface
- Error handling for session creation failures

## Application Factory

The `src/app_factory.py` module provides dependency injection for all components:

```python
def create_app(config_path: str = "config.yaml") -> dict:
    """
    Creates and wires up all application components.
    
    Returns:
        Dictionary with initialized components:
        - config
        - data_store
        - file_storage
        - logger
        - token_tracker
        - resume_manager
        - communication_manager
        - ai_interviewer
        - evaluation_manager
        - session_manager
    """
```

## Main Application Integration

The `src/main.py` has been updated to:
- Initialize application components on first load
- Provide sidebar navigation between pages
- Route to appropriate page based on user selection
- Display session information when active
- Handle page transitions

## Session State Management

The following session state variables are used:

- `app_components`: Dictionary of initialized components
- `current_page`: Current page name (setup, interview, evaluation, history)
- `resume_data`: Parsed resume data
- `resume_uploaded`: Boolean flag for resume upload status
- `ai_provider`: Selected AI provider name
- `ai_model`: Selected AI model name
- `enabled_modes`: List of enabled communication modes
- `current_session_id`: Active session identifier
- `session_created`: Boolean flag for session creation status
- `user_id`: User identifier

## Usage

### Starting the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_PASSWORD="your_db_password"
export OPENAI_API_KEY="your_openai_key"  # or ANTHROPIC_API_KEY

# Run the application
streamlit run src/main.py
```

### User Workflow

1. **Upload Resume** (Optional)
   - Click "Choose a PDF or TXT file"
   - Wait for parsing to complete
   - Review extracted information

2. **Configure AI Provider**
   - Select OpenAI GPT-4 or Anthropic Claude
   - Optionally validate credentials

3. **Select Communication Modes**
   - Check desired modes (audio, video, whiteboard, screen share)
   - Text mode is always enabled

4. **Start Interview**
   - Click "Start Interview" button
   - System creates session and navigates to interview interface

## Error Handling

The implementation includes comprehensive error handling:

- **ValidationError**: Invalid file format or empty resume
- **AIProviderError**: LLM parsing failures or invalid credentials
- **InterviewPlatformError**: Session creation failures
- Generic exceptions with user-friendly messages

## Requirements Satisfied

### Requirement 19.1 (Resume Upload)
✅ Interface to upload resume before starting session
✅ Extract experience level from resume
✅ Extract domain expertise from resume

### Requirements 9.1-9.5 (AI Configuration)
✅ Support for OpenAI GPT-4
✅ Support for Anthropic Claude
✅ Configuration interface for API keys and model selection
✅ Validate API credentials before starting session
✅ Display clear error messages for invalid credentials

### Requirements 2.1-2.2 (Communication Modes)
✅ Provide audio, video, whiteboard, and screen share options
✅ Allow multiple modes to be enabled simultaneously

### Requirements 1.1-1.2 (Session Creation)
✅ Interface to initiate new interview session
✅ Create unique session identifier
✅ Initialize AI Interviewer with configuration

## Future Enhancements

- Resume editing capability
- Multiple resume support per user
- Advanced AI model configuration (temperature, max tokens)
- Communication mode presets
- Session templates
