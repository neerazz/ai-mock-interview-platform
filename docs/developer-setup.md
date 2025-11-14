# Developer Setup Guide

This guide provides comprehensive instructions for developers who want to contribute to or extend the AI Mock Interview Platform.

## Prerequisites

### Required Software

| Software | Version | Purpose | Download Link |
|----------|---------|---------|---------------|
| Python | 3.10+ | Runtime environment | [python.org](https://www.python.org/downloads/) |
| Docker Desktop | Latest | Container orchestration | [docker.com](https://www.docker.com/products/docker-desktop) |
| Git | Latest | Version control | [git-scm.com](https://git-scm.com/downloads) |
| PostgreSQL Client | 15+ | Database management (optional) | [postgresql.org](https://www.postgresql.org/download/) |

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

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

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
LOG_LEVEL=DEBUG
DATA_DIR=./data
ENVIRONMENT=development
```

### 5. Start Docker Services

```bash
# Start PostgreSQL and other services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 6. Verify Setup

Run the validation script:

```bash
python scripts/validate_setup.py
```

## Local Development

### Running the Application

**Using Streamlit directly (recommended):**

```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

streamlit run src/main.py
```

**Using Docker Compose:**

```bash
docker-compose up --build
```

### Hot Reloading

Streamlit automatically reloads when you save changes to Python files.

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_session_manager.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Integration Tests

```bash
# Run integration tests only
pytest tests/integration/

# Run with markers
pytest -m integration
```

## Code Quality

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Manual Quality Checks

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type check
mypy src/ --strict

# Sort imports
isort src/ tests/ --profile black
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
      "args": ["run", "src/main.py"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Debugging Tips

1. Enable debug logging in `.env`: `LOG_LEVEL=DEBUG`
2. Use IDE breakpoints
3. Check logs: `tail -f logs/interview_platform.log`
4. Inspect database: `docker exec -it interview_platform_db psql -U interview_user -d interview_platform`

## Contributing

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Ensure all quality checks pass
6. Submit a pull request

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** feat, fix, docs, style, refactor, test, chore

**Example:**
```
feat(ai): add resume-aware problem generation

Implement logic to generate interview problems based on candidate's
experience level and domain expertise from resume.

Closes #123
```

## Additional Resources

- [Architecture Documentation](architecture.md)
- [API Reference](api/index.md)
- [Quick Start Guide](quick-start.md)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

Happy coding! 🚀
