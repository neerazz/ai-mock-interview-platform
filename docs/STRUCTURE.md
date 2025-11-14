# Project Structure

This document describes the directory structure and organization of the AI Mock Interview Platform.

## Directory Overview

```
ai-mock-interview-platform/
├── src/                    # Application source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── data/                   # Local data storage (gitignored)
├── logs/                   # Application logs (gitignored)
├── .streamlit/             # Streamlit configuration
├── .github/                # GitHub Actions workflows
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Application container definition
├── init.sql                # Database schema initialization
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── config.yaml             # Application configuration
├── startup.sh              # Automated setup script
├── .env.template           # Environment variables template
├── .env                    # Environment variables (gitignored)
├── .gitignore              # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── pytest.ini              # Pytest configuration
├── pyproject.toml          # Python project metadata
└── README.md               # Project overview
```

## Source Code (`src/`)

The `src/` directory contains all application source code, organized by functional domain.

```
src/
├── __init__.py
├── main.py                 # Streamlit application entry point
├── app_factory.py          # Dependency injection and app initialization
├── config.py               # Configuration management
├── models.py               # Data models and type definitions
├── exceptions.py           # Custom exception classes
```

### AI Components (`src/ai/`)

Handles AI-powered interview functionality.

```
src/ai/
├── __init__.py
├── ai_interviewer.py       # LLM-powered interviewer logic
└── token_tracker.py        # Token usage tracking and cost estimation
```

**Purpose**:
- `ai_interviewer.py`: Generates interview questions, analyzes responses, maintains conversation context
- `token_tracker.py`: Tracks API token usage, calculates costs, monitors budget limits

### Communication Components (`src/communication/`)

Manages multi-modal communication (audio, video, whiteboard, screen share).

```
src/communication/
├── __init__.py
├── communication_manager.py  # Orchestrates communication modes
├── audio_handler.py          # Audio recording and transcription
├── video_handler.py          # Video recording
├── whiteboard_handler.py     # Whiteboard snapshot management
├── screen_handler.py         # Screen share capture
└── transcript_handler.py     # Real-time transcript generation
```

**Purpose**:
- `communication_manager.py`: Coordinates between different communication handlers
- `audio_handler.py`: Records audio, transcribes with Whisper API
- `video_handler.py`: Captures video streams from webcam
- `whiteboard_handler.py`: Saves canvas snapshots as images
- `screen_handler.py`: Captures screen share images
- `transcript_handler.py`: Generates and updates real-time transcripts

### Database Components (`src/database/`)

Handles data persistence with PostgreSQL.

```
src/database/
├── __init__.py
└── data_store.py           # PostgreSQL repository implementation
```

**Purpose**:
- `data_store.py`: Implements repository pattern for data access, manages database connections, executes queries

### Evaluation Components (`src/evaluation/`)

Generates performance feedback and improvement plans.

```
src/evaluation/
├── __init__.py
└── evaluation_manager.py   # Interview evaluation and feedback generation
```

**Purpose**:
- `evaluation_manager.py`: Analyzes interview performance, calculates competency scores, generates improvement plans

### Logging Components (`src/log_manager/`)

Comprehensive logging system for debugging and monitoring.

```
src/log_manager/
├── __init__.py
└── logging_manager.py      # Multi-destination logging (console, file, database)
```

**Purpose**:
- `logging_manager.py`: Structured logging with multiple handlers, error tracking, audit trails

### Resume Components (`src/resume/`)

Processes and analyzes candidate resumes.

```
src/resume/
├── __init__.py
└── resume_manager.py       # Resume parsing and analysis
```

**Purpose**:
- `resume_manager.py`: Parses PDF/TXT resumes, extracts experience level and domain expertise

### Session Components (`src/session/`)

Manages interview session lifecycle.

```
src/session/
├── __init__.py
└── session_manager.py      # Session orchestration and state management
```

**Purpose**:
- `session_manager.py`: Creates/starts/ends sessions, coordinates between components, manages state transitions

### Storage Components (`src/storage/`)

Manages media file storage on local filesystem.

```
src/storage/
├── __init__.py
└── file_storage.py         # Local file system operations
```

**Purpose**:
- `file_storage.py`: Saves audio/video/image files, organizes by session, generates file paths

### UI Components (`src/ui/`)

Streamlit-based user interface components.

```
src/ui/
├── __init__.py
└── pages/
    ├── setup.py            # Resume upload and configuration
    ├── interview.py        # Main interview interface (3-panel layout)
    ├── evaluation.py       # Evaluation report display
    └── history.py          # Session history and past interviews
```

**Purpose**:
- `setup.py`: Resume upload, AI provider selection, communication mode configuration
- `interview.py`: Main interview UI with chat, whiteboard, and transcript panels
- `evaluation.py`: Displays evaluation scores, feedback, and improvement plans
- `history.py`: Lists past sessions, allows reviewing previous interviews

## Tests (`tests/`)

Comprehensive test suite with unit and integration tests.

```
tests/
├── __init__.py
├── test_ai_interviewer.py           # AI interviewer unit tests
├── test_communication_handlers.py   # Communication handler tests
├── test_communication_manager.py    # Communication manager tests
├── test_evaluation_manager.py       # Evaluation manager tests
├── test_file_storage.py             # File storage tests
├── test_logging.py                  # Logging system tests
├── test_resume_manager.py           # Resume manager tests
├── test_session_manager.py          # Session manager tests
├── test_token_tracker.py            # Token tracker tests
└── integration/                     # Integration tests
    ├── test_integration_workflow.py        # Complete workflow tests
    ├── test_integration_multimode.py       # Multi-mode communication tests
    └── test_integration_error_recovery.py  # Error handling tests
```

**Organization Principles**:
- One test file per source module
- Integration tests in separate subdirectory
- Test fixtures in conftest.py files
- Mock external dependencies (APIs, database)

## Documentation (`docs/`)

Comprehensive documentation for users and developers.

```
docs/
├── QUICK_START_GUIDE.md      # End-user setup guide
├── DEVELOPER_SETUP_GUIDE.md  # Developer environment setup
├── ARCHITECTURE.md            # Architecture and design decisions
├── LOGGING.md                 # Logging system documentation
└── API_REFERENCE.md           # API documentation (future)
```

**Purpose**:
- `QUICK_START_GUIDE.md`: Step-by-step guide for end users to set up and use the platform
- `DEVELOPER_SETUP_GUIDE.md`: Comprehensive guide for developers to set up development environment
- `ARCHITECTURE.md`: System architecture, component relationships, design principles, ADRs
- `LOGGING.md`: Logging system usage, configuration, and best practices

## Data Storage (`data/`)

Local data storage for media files (gitignored).

```
data/
└── sessions/
    └── {session_id}/
        ├── audio/
        │   ├── recording_001.wav
        │   └── recording_002.wav
        ├── video/
        │   └── interview.mp4
        ├── whiteboard/
        │   ├── snapshot_001.png
        │   └── snapshot_002.png
        └── screen/
            ├── capture_001.png
            └── capture_002.png
```

**Organization Principles**:
- Each session has its own directory
- Media types separated into subdirectories
- Sequential numbering for multiple files
- File references stored in database

## Logs (`logs/`)

Application logs for debugging and monitoring (gitignored).

```
logs/
└── interview_platform.log    # Rotating log file
```

**Log Rotation**:
- Maximum file size: 10MB
- Backup count: 5 files
- Format: Structured JSON

## Configuration Files

### `.streamlit/config.toml`

Streamlit application configuration.

```toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#4A90E2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### `docker-compose.yml`

Docker services configuration for PostgreSQL and application.

**Services**:
- `postgres`: PostgreSQL 15 database
- `app`: Streamlit application (optional, can run locally)

### `Dockerfile`

Application container definition.

**Base Image**: python:3.10-slim
**Exposed Port**: 8501

### `init.sql`

Database schema initialization script.

**Tables**:
- `resumes`: User resume data
- `sessions`: Interview session metadata
- `conversations`: Chat history
- `evaluations`: Performance evaluations
- `media_files`: Media file references
- `token_usage`: AI API token tracking
- `audit_logs`: System logs and events

### `requirements.txt`

Production dependencies.

**Key Dependencies**:
- streamlit: Web UI framework
- langchain: LLM orchestration
- openai: OpenAI API client
- anthropic: Anthropic API client
- psycopg2-binary: PostgreSQL adapter
- streamlit-webrtc: Audio/video capture
- streamlit-drawable-canvas: Whiteboard component

### `requirements-dev.txt`

Development dependencies.

**Key Dependencies**:
- pytest: Testing framework
- pytest-cov: Coverage reporting
- black: Code formatter
- ruff: Linter
- mypy: Type checker
- pre-commit: Git hooks

### `config.yaml`

Application configuration.

**Sections**:
- Database connection settings
- AI provider configurations
- Storage paths
- Logging configuration
- Feature flags

### `.env.template`

Environment variables template.

**Variables**:
- `DB_PASSWORD`: Database password
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key (optional)
- `LOG_LEVEL`: Logging level
- `DATA_DIR`: Data directory path

### `.pre-commit-config.yaml`

Pre-commit hooks configuration.

**Hooks**:
- trailing-whitespace: Remove trailing whitespace
- end-of-file-fixer: Ensure files end with newline
- black: Format code
- ruff: Lint code
- mypy: Type check
- pytest: Run tests

### `pytest.ini`

Pytest configuration.

**Settings**:
- Test paths: `tests/`
- Test patterns: `test_*.py`
- Markers: integration, slow, unit
- Coverage settings

### `pyproject.toml`

Python project metadata and tool configuration.

**Sections**:
- Project metadata (name, version, description)
- Black configuration
- Ruff configuration
- isort configuration

## File Organization Principles

### 1. Separation of Concerns

Each directory has a single, clear purpose:
- `src/`: Application code only
- `tests/`: Test code only
- `docs/`: Documentation only
- `data/`: Runtime data only

### 2. Modular Structure

Components are organized by functional domain:
- AI components in `src/ai/`
- Communication components in `src/communication/`
- Database components in `src/database/`

### 3. Flat Hierarchy

Avoid deep nesting:
- Maximum 2-3 levels of subdirectories
- Related files grouped together
- Easy to navigate and find files

### 4. Consistent Naming

Follow naming conventions:
- Python files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_CASE`

### 5. Clear Dependencies

Dependencies flow in one direction:
- UI → Session Manager → Domain Components → Infrastructure
- No circular dependencies
- Clear dependency graph

## Adding New Components

When adding new functionality, follow these guidelines:

### 1. Create New Module

```bash
# For a new domain component
mkdir src/new_component
touch src/new_component/__init__.py
touch src/new_component/new_component_manager.py
```

### 2. Create Tests

```bash
# Create corresponding test file
touch tests/test_new_component_manager.py
```

### 3. Update Documentation

```bash
# Update relevant documentation
# - Add to STRUCTURE.md
# - Update ARCHITECTURE.md if architectural change
# - Update README.md if user-facing feature
```

### 4. Add Dependencies

```bash
# Add to requirements.txt or requirements-dev.txt
echo "new-package==1.0.0" >> requirements.txt
```

### 5. Update Configuration

```bash
# Add configuration to config.yaml if needed
# Add environment variables to .env.template if needed
```

## Maintenance Guidelines

### Keep It Clean

- Remove unused files and code
- Update documentation when code changes
- Run linters and formatters regularly
- Keep dependencies up to date

### Keep It Organized

- Follow the established structure
- Don't create new top-level directories without reason
- Group related files together
- Use clear, descriptive names

### Keep It Simple

- Avoid over-engineering
- Prefer flat over nested structures
- Keep files focused and small
- Follow SOLID principles

---

For more information, see:
- [README.md](README.md) - Project overview
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture details
- [docs/DEVELOPER_SETUP_GUIDE.md](docs/DEVELOPER_SETUP_GUIDE.md) - Development setup
