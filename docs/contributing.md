# Contributing Guide

Thank you for your interest in contributing to the AI Mock Interview Platform! This guide will help you get started.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Follow the [Developer Setup Guide](developer-setup.md)
4. Create a feature branch
5. Make your changes
6. Submit a pull request

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names:
- `feature/add-coding-interviews`
- `fix/audio-recording-bug`
- `docs/update-api-reference`

### 2. Make Your Changes

Follow our coding standards:
- Write clean, readable code
- Add type hints to all functions
- Write docstrings for public APIs
- Keep functions under 50 lines
- Keep files under 300 lines

### 3. Write Tests

- Unit tests for business logic
- Integration tests for workflows
- Aim for 80%+ coverage

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### 4. Run Quality Checks

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type check
mypy src/

# Run all checks
pre-commit run --all-files
```

### 5. Commit Your Changes

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

**Example:**
```
feat(ai): add resume-aware problem generation

Implement logic to generate interview problems based on candidate's
experience level and domain expertise from resume.

Closes #123
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Python Style

Follow PEP 8 with these specifics:

- 4 spaces for indentation
- Max line length: 88 characters (Black default)
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

### Type Hints

Always use type hints:

```python
def process_response(
    session_id: str,
    response: str,
    whiteboard_image: Optional[bytes] = None
) -> InterviewResponse:
    """Process candidate response."""
    pass
```

### Docstrings

Use Google-style docstrings:

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
        >>> config = SessionConfig(enabled_modes=[CommunicationMode.TEXT])
        >>> session = manager.create_session(config)
    """
    pass
```

### Error Handling

Always handle errors gracefully:

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

## Testing Guidelines

### Unit Tests

Test individual components in isolation:

```python
def test_create_session(mock_data_store):
    # Arrange
    session_manager = SessionManager(data_store=mock_data_store)
    config = SessionConfig(enabled_modes=[CommunicationMode.TEXT])
    
    # Act
    session = session_manager.create_session(config)
    
    # Assert
    assert session.id is not None
    mock_data_store.save_session.assert_called_once()
```

### Integration Tests

Test complete workflows:

```python
@pytest.mark.integration
def test_complete_interview_workflow(test_database):
    # Test full interview from start to evaluation
    pass
```

## Pull Request Process

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings
- [ ] Dependent changes merged

### PR Template

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

## Screenshots (if applicable)
Add screenshots here
```

### Review Process

1. Automated checks run (CI/CD)
2. Code review by maintainers
3. Address feedback
4. Approval and merge

## Community Guidelines

### Be Respectful

- Be kind and courteous
- Respect different viewpoints
- Accept constructive criticism
- Focus on what's best for the project

### Be Collaborative

- Help others learn
- Share knowledge
- Ask questions
- Provide feedback

### Be Professional

- Keep discussions on-topic
- Avoid personal attacks
- Use inclusive language
- Follow the code of conduct

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Create an issue with reproduction steps
- **Features**: Open an issue to discuss before implementing
- **Security**: Email security@example.com

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🎉
