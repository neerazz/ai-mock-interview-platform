# Developer Setup Guide - AI Mock Interview Platform

This guide provides comprehensive instructions for developers who want to contribute to or extend the AI Mock Interview Platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Running Tests](#running-tests)
- [Debugging](#debugging)
- [Development Workflows](#development-workflows)
- [Code Quality](#code-quality)
- [Architecture Overview](#architecture-overview)
- [Contributing](#contributing)

## Prerequisites

### Required Software

| Software | Version | Purpose | Download Link |
|----------|---------|---------|---------------|
| Python | 3.10+ | Runtime environment | [python.org](https://www.python.org/downloads/) |
| Docker Desktop | Latest | Container orchestration | [docker.com](https://www.docker.com/products/docker-desktop) |
| Git | Latest | Version control | [git-scm.com](https://git-scm.com/downloads) |
| PostgreSQL Client | 15+ | Database management (optional) | [postgresql.org](https://www.postgresql.org/download/) |

### Recommended Tools

- **IDE**: VS Code, PyCharm, or similar
- **API Testing**: Postman or curl
- **Database GUI**: pgAdmin, DBeaver, or TablePlus
- **Terminal**: iTerm2 (macOS), Windows Terminal, or similar

### API Keys

You'll need API keys for development:
- **OpenAI API Key** (required): [platform.openai.com](https://platform.openai.com/api-keys)
- **Anthropic API Key** (optional): [console.anthropic.com](https://console.anthropic.com/)

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-mock-interview-platform
```

### 2. Create Python Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Verify activation:**
```bash
which python  # macOS/Linux
where python  # Windows
# Should point to venv/bin/python or venv\Scripts\python
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
pip list
```

**Key Dependencies:**
- `streamlit`: Web UI framework
- `langchain`: LLM orchestration
- `openai`: OpenAI API client
- `anthropic`: Anthropic API client
- `psycopg2-binary`: PostgreSQL adapter
- `streamlit-webrtc`: Audio/video capture
- `streamlit-drawable-canvas`: Whiteboard component
- `pytest`: Testing framework
- `black`: Code formatter
- `ruff`: Linter
- `mypy`: Type checker

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp config/.env.template .env
```

Edit `.env` with your configuration:

```bash
# Database Configuration
DB_PASSWORD=dev_password_123
DATABASE_URL=postgresql://interview_user:dev_password_123@localhost:5432/interview_platform

# AI Provider API Keys
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Application Configuration
LOG_LEVEL=DEBUG  # Use DEBUG for development
DATA_DIR=./data
ENVIRONMENT=development

# Optional: Token Budget
MAX_TOKENS_PER_SESSION=50000
TOKEN_BUDGET_WARNING_THRESHOLD=0.8

# Optional: Feature Flags
ENABLE_VIDEO_RECORDING=true
ENABLE_SCREEN_SHARE=true
ENABLE_AUDIO_TRANSCRIPTION=true
```

**Environment Variable Reference:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_PASSWORD` | Yes | - | PostgreSQL password |
| `DATABASE_URL` | Yes | - | Full database connection string |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for GPT-4 |
| `ANTHROPIC_API_KEY` | No | - | Anthropic API key for Claude |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `DATA_DIR` | No | ./data | Directory for media file storage |
| `ENVIRONMENT` | No | production | Environment name (development, staging, production) |
| `MAX_TOKENS_PER_SESSION` | No | 50000 | Maximum tokens per interview session |
| `TOKEN_BUDGET_WARNING_THRESHOLD` | No | 0.8 | Warn when 80% of token budget used |

### 5. Start Docker Services

```bash
# Start PostgreSQL and other services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f postgres
```

**Expected output:**
```
NAME                          STATUS              PORTS
interview_platform_db         Up 30 seconds       0.0.0.0:5432->5432/tcp
```

### 6. Initialize Database

The database schema is automatically initialized when PostgreSQL starts for the first time using `init.sql`. To manually reinitialize:

```bash
# Connect to database
docker exec -it interview_platform_db psql -U interview_user -d interview_platform

# Verify tables exist
\dt

# Expected tables:
# - resumes
# - sessions
# - conversations
# - evaluations
# - media_files
# - token_usage
# - audit_logs

# Exit psql
\q
```

### 7. Verify Setup

Run the validation script to ensure everything is configured correctly:

```bash
python scripts/validate_setup.py
```

This checks:
- Python version
- Required packages installed
- Environment variables set
- Docker services running
- Database connectivity
- API keys valid

## Local Development

### Running the Application

**Option 1: Using Streamlit directly (recommended for development)**

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run Streamlit app
streamlit run src/main.py

# App will open at http://localhost:8501
```

**Option 2: Using Docker Compose**

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f app
```

**Option 3: Using startup script**

```bash
# Make script executable (first time only)
chmod +x startup.sh

# Run startup script
./startup.sh
```

### Hot Reloading

Streamlit automatically reloads when you save changes to Python files. You'll see:

```
Source file changed: src/main.py
Rerunning...
```

### Project Structure

```
ai-mock-interview-platform/
├── src/                          # Application source code
│   ├── __init__.py
│   ├── main.py                   # Streamlit entry point
│   ├── app_factory.py            # Dependency injection setup
│   ├── config.py                 # Configuration management
│   ├── models.py                 # Data models and types
│   ├── exceptions.py             # Custom exception classes
│   ├── ai/                       # AI components
│   │   ├── __init__.py
│   │   ├── ai_interviewer.py    # LLM-powered interviewer
│   │   └── token_tracker.py     # Token usage tracking
│   ├── communication/            # Communication handlers
│   │   ├── __init__.py
│   │   ├── communication_manager.py
│   │   ├── audio_handler.py
│   │   ├── video_handler.py
│   │   ├── whiteboard_handler.py
│   │   ├── screen_handler.py
│   │   └── transcript_handler.py
│   ├── database/                 # Data persistence
│   │   ├── __init__.py
│   │   └── data_store.py        # PostgreSQL implementation
│   ├── evaluation/               # Evaluation system
│   │   ├── __init__.py
│   │   └── evaluation_manager.py
│   ├── log_manager/              # Logging system
│   │   ├── __init__.py
│   │   └── logging_manager.py
│   ├── resume/                   # Resume processing
│   │   ├── __init__.py
│   │   └── resume_manager.py
│   ├── session/                  # Session management
│   │   ├── __init__.py
│   │   └── session_manager.py
│   ├── storage/                  # File storage
│   │   ├── __init__.py
│   │   └── file_storage.py
│   └── ui/                       # UI components
│       ├── __init__.py
│       └── pages/
│           ├── setup.py          # Resume upload & config
│           ├── interview.py      # Main interview interface
│           ├── evaluation.py     # Evaluation display
│           └── history.py        # Session history
├── tests/                        # Test files
│   ├── __init__.py
│   ├── test_ai_interviewer.py
│   ├── test_communication_handlers.py
│   ├── test_communication_manager.py
│   ├── test_evaluation_manager.py
│   ├── test_file_storage.py
│   ├── test_logging.py
│   ├── test_resume_manager.py
│   ├── test_session_manager.py
│   ├── test_token_tracker.py
│   └── integration/              # Integration tests
│       ├── test_integration_workflow.py
│       ├── test_integration_multimode.py
│       └── test_integration_error_recovery.py
├── docs/                         # Documentation
│   ├── QUICK_START_GUIDE.md
│   ├── DEVELOPER_SETUP_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── LOGGING.md
│   └── API_REFERENCE.md
├── data/                         # Local data storage
│   └── sessions/                 # Session media files
├── logs/                         # Application logs
│   └── interview_platform.log
├── .streamlit/                   # Streamlit configuration
│   └── config.toml
├── .github/                      # GitHub Actions workflows
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml            # Docker services
├── Dockerfile                    # Application container
├── init.sql                      # Database schema
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── config.yaml                   # Application configuration
├── startup.sh                    # Automated setup script
├── .env.template                 # Environment template
├── .env                          # Environment variables (gitignored)
├── .gitignore                    # Git ignore rules
├── .pre-commit-config.yaml       # Pre-commit hooks
├── pytest.ini                    # Pytest configuration
├── pyproject.toml                # Python project metadata
└── README.md                     # Project overview
```

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_session_manager.py

# Run specific test function
pytest tests/test_session_manager.py::test_create_session

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# Open coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Integration Tests

```bash
# Run integration tests only
pytest tests/integration/

# Run specific integration test
pytest tests/integration/test_integration_workflow.py

# Run with markers
pytest -m integration
```

### Test Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: Integration tests
    slow: Slow-running tests
    unit: Unit tests
addopts = 
    --strict-markers
    --tb=short
    -ra
```

### Writing Tests

**Example unit test:**

```python
import pytest
from src.session.session_manager import SessionManager
from src.models import SessionConfig, CommunicationMode

def test_create_session(mock_data_store, mock_ai_interviewer):
    """Test session creation with valid configuration."""
    # Arrange
    session_manager = SessionManager(
        data_store=mock_data_store,
        ai_interviewer=mock_ai_interviewer,
        evaluation_manager=mock_evaluation_manager,
        communication_manager=mock_communication_manager,
        logger=mock_logger
    )
    config = SessionConfig(
        enabled_modes=[CommunicationMode.TEXT, CommunicationMode.WHITEBOARD],
        ai_provider="openai",
        ai_model="gpt-4"
    )
    
    # Act
    session = session_manager.create_session(config)
    
    # Assert
    assert session.id is not None
    assert session.status == SessionStatus.ACTIVE
    assert len(session.config.enabled_modes) == 2
    mock_data_store.save_session.assert_called_once()
```

**Example integration test:**

```python
import pytest
from src.app_factory import create_app

@pytest.mark.integration
def test_complete_interview_workflow(test_database):
    """Test complete interview workflow from start to evaluation."""
    # Arrange
    app = create_app()
    resume_data = create_test_resume()
    
    # Act - Create session
    session = app.session_manager.create_session(
        config=create_test_config(resume_data)
    )
    
    # Act - Start interview
    app.session_manager.start_session(session.id)
    
    # Act - Process responses
    response1 = app.ai_interviewer.process_response(
        session.id,
        "I would design a distributed system with..."
    )
    
    # Act - End session
    evaluation = app.session_manager.end_session(session.id)
    
    # Assert
    assert evaluation is not None
    assert evaluation.overall_score > 0
    assert len(evaluation.competency_scores) > 0
    assert len(evaluation.improvement_plan.concrete_steps) > 0
```

## Debugging

### VS Code Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Streamlit",
      "type": "python",
      "request": "launch",
      "module": "streamlit",
      "args": [
        "run",
        "src/main.py",
        "--server.port=8501"
      ],
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "-v",
        "${file}"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

### PyCharm Configuration

1. **Run Configuration for Streamlit:**
   - Script path: `<path-to-venv>/bin/streamlit`
   - Parameters: `run src/main.py --server.port=8501`
   - Working directory: `<project-root>`

2. **Run Configuration for Tests:**
   - Target: `tests/`
   - Pattern: `test_*.py`
   - Working directory: `<project-root>`

### Debugging Tips

**1. Enable Debug Logging:**

```python
# In your code
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set in `.env`:
```bash
LOG_LEVEL=DEBUG
```

**2. Use Breakpoints:**

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use IDE breakpoints (recommended)
```

**3. Inspect Database:**

```bash
# Connect to database
docker exec -it interview_platform_db psql -U interview_user -d interview_platform

# Query sessions
SELECT id, status, created_at FROM sessions ORDER BY created_at DESC LIMIT 10;

# Query conversations
SELECT role, content, timestamp FROM conversations WHERE session_id = '<session-id>';

# Query logs
SELECT level, component, message FROM audit_logs ORDER BY timestamp DESC LIMIT 20;
```

**4. Check Logs:**

```bash
# Application logs
tail -f logs/interview_platform.log

# Docker logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres
```

**5. Debug AI API Calls:**

```python
# Enable LangChain debugging
import langchain
langchain.debug = True

# Or set environment variable
export LANGCHAIN_VERBOSE=true
```

## Development Workflows

### Feature Development

1. **Create Feature Branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Implement Feature:**
   - Write code following SOLID principles
   - Add type hints to all functions
   - Write docstrings for public APIs
   - Keep functions under 50 lines
   - Keep files under 300 lines

3. **Write Tests:**
   - Unit tests for business logic
   - Integration tests for workflows
   - Aim for 80%+ coverage

4. **Run Quality Checks:**
```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type check
mypy src/

# Run tests
pytest --cov=src
```

5. **Commit Changes:**
```bash
git add .
git commit -m "feat: add your feature description"
```

6. **Push and Create PR:**
```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

### Bug Fixing

1. **Create Bug Fix Branch:**
```bash
git checkout -b fix/bug-description
```

2. **Reproduce Bug:**
   - Write a failing test that demonstrates the bug
   - Debug to identify root cause

3. **Fix Bug:**
   - Implement fix
   - Ensure test now passes
   - Verify no regressions

4. **Follow Quality Checks** (same as feature development)

### Code Review Process

**As Author:**
- Ensure all tests pass
- Ensure code quality checks pass
- Write clear PR description
- Link related issues
- Request review from team members

**As Reviewer:**
- Check code follows SOLID principles
- Verify tests are comprehensive
- Look for potential bugs or edge cases
- Ensure documentation is updated
- Approve or request changes

## Code Quality

### Pre-commit Hooks

Install pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

**What gets checked:**
- Code formatting (black)
- Import sorting (isort)
- Linting (ruff)
- Type checking (mypy)
- Trailing whitespace
- File endings
- Large files
- Private keys

### Manual Quality Checks

**Format Code:**
```bash
black src/ tests/
```

**Lint Code:**
```bash
ruff check src/ tests/ --fix
```

**Type Check:**
```bash
mypy src/ --strict
```

**Sort Imports:**
```bash
isort src/ tests/ --profile black
```

### Code Style Guidelines

**1. Follow PEP 8:**
- 4 spaces for indentation
- Max line length: 88 characters (Black default)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

**2. Type Hints:**
```python
def process_response(
    session_id: str,
    response: str,
    whiteboard_image: Optional[bytes] = None
) -> InterviewResponse:
    """Process candidate response and generate follow-up."""
    pass
```

**3. Docstrings (Google Style):**
```python
def create_session(self, config: SessionConfig) -> Session:
    """Create a new interview session.
    
    Args:
        config: Session configuration including enabled modes and AI provider.
        
    Returns:
        Created session with unique identifier.
        
    Raises:
        ConfigurationError: If configuration is invalid.
        DataStoreError: If database operation fails.
        
    Example:
        >>> config = SessionConfig(
        ...     enabled_modes=[CommunicationMode.TEXT],
        ...     ai_provider="openai"
        ... )
        >>> session = manager.create_session(config)
        >>> print(session.id)
        '550e8400-e29b-41d4-a716-446655440000'
    """
    pass
```

**4. Error Handling:**
```python
try:
    result = self.data_store.save_session(session)
except DatabaseError as e:
    self.logger.error(
        "session_save_failed",
        session_id=session.id,
        error=str(e)
    )
    raise DataStoreError(f"Failed to save session: {e}") from e
```

## Architecture Overview

### Design Principles

1. **SOLID Principles:**
   - Single Responsibility: Each class has one clear purpose
   - Open-Closed: Extend through inheritance, not modification
   - Liskov Substitution: Interfaces are interchangeable
   - Interface Segregation: Focused, minimal interfaces
   - Dependency Inversion: Depend on abstractions, not concretions

2. **Dependency Injection:**
   - All dependencies injected through constructors
   - Easy to mock for testing
   - Clear dependency graph

3. **Repository Pattern:**
   - Abstract data access behind interfaces
   - Easy to swap implementations (PostgreSQL → Cloud DB)

### Key Components

**Session Manager:**
- Orchestrates interview lifecycle
- Coordinates between components
- Manages state transitions

**Communication Manager:**
- Handles audio, video, whiteboard, screen share
- Delegates to specific handlers
- Stores media files

**AI Interviewer:**
- Generates interview questions
- Analyzes responses
- Maintains conversation context
- Tracks token usage

**Evaluation Manager:**
- Analyzes session data
- Generates feedback reports
- Creates improvement plans

**Data Store:**
- PostgreSQL implementation
- Repository pattern for abstraction
- Supports future cloud migration

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Contributing

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Write/update tests**
5. **Ensure all quality checks pass**
6. **Submit a pull request**

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Examples:**
```
feat(ai): add resume-aware problem generation

Implement logic to generate interview problems based on candidate's
experience level and domain expertise from resume.

Closes #123
```

```
fix(database): handle connection timeout gracefully

Add retry logic with exponential backoff for database connection
failures. Prevents application crash on transient network issues.

Fixes #456
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Dependent changes merged
```

## Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [API Reference](API_REFERENCE.md)
- [Logging Guide](LOGGING.md)
- [Quick Start Guide](QUICK_START_GUIDE.md)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Getting Help

- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: [developer-support@example.com]
- **Slack**: [Join our Slack channel]

---

Happy coding! 🚀
