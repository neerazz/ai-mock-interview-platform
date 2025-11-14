# AI Mock Interview Platform

[![CI](https://github.com/YOUR_USERNAME/ai-mock-interview-platform/workflows/CI/badge.svg)](https://github.com/YOUR_USERNAME/ai-mock-interview-platform/actions)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/ai-mock-interview-platform/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/ai-mock-interview-platform)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

A local proof-of-concept AI-powered mock interview platform focused on System Design interviews. Practice system design interviews with an AI interviewer that provides real-time feedback and comprehensive evaluation.

## Features

- 🎤 **Multi-modal Communication**: Audio, video, whiteboard, and screen share
- 🤖 **AI Interviewer**: Powered by OpenAI GPT-4 or Anthropic Claude
- 📝 **Resume-Aware**: Generates problems tailored to your experience level
- 🎨 **Interactive Whiteboard**: Draw system architecture diagrams
- 📊 **Comprehensive Feedback**: Detailed evaluation with improvement plans
- 💾 **Local Storage**: All data stored locally with PostgreSQL
- 📈 **Progress Tracking**: View past sessions and track improvement

## Prerequisites

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
  - Windows: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - Mac: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
  - Linux: [Docker Engine](https://docs.docker.com/engine/install/)
- **Python 3.10+** (for local development)
  - Windows: [Python.org](https://www.python.org/downloads/) or [Microsoft Store](https://apps.microsoft.com/store/detail/python-310/9PJPW5LDXLZ5)
  - Mac: `brew install python@3.10`
  - Linux: `sudo apt install python3.10` (Ubuntu/Debian)
- **OpenAI API key** (required)
- **Anthropic API key** (optional)

### Windows-Specific Requirements

- **WSL2** (Windows Subsystem for Linux 2) - Required for Docker Desktop
- **Git for Windows** (optional, for Git Bash) - [Download](https://git-scm.com/download/win)
- **PowerShell 5.1+** or **Windows Terminal** (recommended)

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-mock-interview-platform

# Copy environment template
cp .env.template .env

# Edit .env with your API keys
# Required: DB_PASSWORD, OPENAI_API_KEY
# Optional: ANTHROPIC_API_KEY
```

### 2. Start the Platform

#### Option A: Using Docker Compose (All Platforms)

```bash
# Start services
docker-compose up -d

# Check logs to verify startup
docker-compose logs -f
```

#### Option B: Using Startup Script

**Linux/Mac:**
```bash
# Make startup script executable
chmod +x startup.sh

# Run startup script
./startup.sh
```

**Windows (PowerShell):**
```powershell
# Run Docker Compose directly
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Windows (Git Bash):**
```bash
# Run startup script
bash startup.sh
```

The startup process will:
- Validate environment variables
- Create necessary directories
- Start Docker services (PostgreSQL + App)
- Initialize database schema
- Verify all services are running

### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

## Project Structure

```
ai-mock-interview-platform/
├── src/                    # Application source code
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models
│   ├── exceptions.py      # Custom exceptions
│   ├── main.py            # Main entry point
│   ├── database/          # Database layer
│   │   └── data_store.py  # PostgreSQL implementation
│   └── log_manager/       # Logging system
│       ├── __init__.py
│       └── logging_manager.py
├── tests/                 # Test files
├── docs/                  # Documentation
│   └── LOGGING.md        # Logging system docs
├── data/                  # Local data storage
│   └── sessions/         # Session media files
├── logs/                  # Application logs
│   └── interview_platform.log
├── .streamlit/           # Streamlit configuration
│   └── config.toml
├── docker-compose.yml    # Docker services configuration
├── Dockerfile            # Application container
├── init.sql              # Database schema
├── requirements.txt      # Python dependencies
├── config.yaml           # Application configuration
├── startup.sh            # Automated setup script
├── .env.template         # Environment variables template
└── .gitignore           # Git ignore rules
```

## Configuration

### Environment Variables (.env)

```bash
# Database
DB_PASSWORD=your_secure_password

# AI Providers
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional

# Application
LOG_LEVEL=INFO
DATA_DIR=./data
```

### Application Settings (config.yaml)

Configure AI models, storage paths, communication settings, and more in `config.yaml`.

## Docker Services

### PostgreSQL Database
- **Port**: 5432
- **Database**: interview_platform
- **User**: interview_user
- **Data**: Persisted in Docker volume

### Streamlit Application
- **Port**: 8501
- **Volumes**: 
  - `./data` → `/app/data`
  - `./logs` → `/app/logs`

## Useful Commands

```bash
# View all logs
docker-compose logs -f

# View application logs only
docker-compose logs -f app

# View database logs only
docker-compose logs -f postgres

# Stop services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild application
docker-compose up -d --build
```

## Database Schema

The platform uses PostgreSQL with the following tables:
- `resumes` - User resume data
- `sessions` - Interview session metadata
- `conversations` - Chat history
- `evaluations` - Performance evaluations
- `media_files` - Media file references
- `token_usage` - AI API token tracking
- `audit_logs` - System logs and events

## Development

### Local Development Setup

**Linux/Mac:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run locally (requires PostgreSQL running)
streamlit run src/main.py
```

**Windows (PowerShell):**
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run locally (requires PostgreSQL running)
streamlit run src/main.py
```

**Windows (Command Prompt):**
```cmd
# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run locally (requires PostgreSQL running)
streamlit run src/main.py
```

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Code Quality and Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks run automatically before each commit to check:
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)
- Import sorting (isort)
- Trailing whitespace and file endings

**Setup pre-commit hooks:**

```bash
# Install pre-commit (included in requirements-dev.txt)
pip install -r requirements-dev.txt

# Install the git hooks
pre-commit install

# (Optional) Run hooks manually on all files
pre-commit run --all-files
```

**Manual code quality checks:**

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/ --fix

# Type check with mypy
mypy src/

# Sort imports with isort
isort src/ tests/
```

The CI pipeline automatically runs all these checks on every push and pull request.

## Troubleshooting

### Windows-Specific Issues

#### Docker Desktop Not Starting
- Ensure WSL2 is installed and enabled
- Check Docker Desktop settings → Resources → WSL Integration
- Restart Docker Desktop service

#### Line Ending Issues (Git)
```powershell
# Configure Git to handle line endings properly
git config --global core.autocrlf true
```

#### Permission Issues with Volumes
- Ensure Docker Desktop has access to the drive where the project is located
- Docker Desktop → Settings → Resources → File Sharing

#### PowerShell Execution Policy
```powershell
# If scripts are blocked, run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PostgreSQL Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep interview_platform_db

# Check PostgreSQL logs
docker-compose logs postgres

# Verify database connection
docker exec interview_platform_db psql -U interview_user -d interview_platform -c "SELECT 1;"
```

### Application Not Starting

```bash
# Check application logs
docker-compose logs app

# Rebuild application
docker-compose up -d --build app
```

### Port Already in Use

**Windows:**
```powershell
# Check what's using port 8501
netstat -ano | findstr :8501

# Kill process by PID (if needed)
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Check what's using port 8501
lsof -i :8501

# Kill process by PID (if needed)
kill -9 <PID>
```

**Alternative:** Change port in docker-compose.yml if needed

## Architecture

The platform follows a modular architecture with clear separation of concerns:

- **UI Layer**: Streamlit-based interface
- **Session Manager**: Orchestrates interview lifecycle
- **Communication Manager**: Handles audio/video/whiteboard
- **AI Interviewer**: LangChain-powered interview agent
- **Evaluation Manager**: Generates feedback and scores
- **Data Store**: PostgreSQL with repository pattern
- **File Storage**: Local filesystem for media files
- **Logging System**: Comprehensive logging with multiple handlers (console, file, database)

### Logging System

The platform includes a comprehensive logging system with:
- **Multiple Handlers**: Console, rotating file, and database logging
- **Structured JSON Format**: Machine-readable logs for analysis
- **Context-Aware**: Includes session_id and user_id when available
- **Error Tracking**: Full stack traces with contextual information

See [docs/LOGGING.md](docs/LOGGING.md) for detailed documentation.

## License

[Your License Here]

## Contributing

[Contributing guidelines if applicable]

## Support

For issues and questions, please [create an issue](link-to-issues) or contact [support email].
