# Validation Suite Quick Reference

## Quick Commands

```bash
# Run all validations
python run_all_validations.py

# Run individual validations
python validate_e2e_workflow.py        # E2E workflow (requires API)
python validate_error_scenarios.py     # Error handling (no API needed)
python validate_docker_deployment.py   # Docker deployment (requires Docker)
python validate_performance.py         # Performance (requires API)
python validate_ui_ux.py              # UI/UX (no API needed)
```

## Prerequisites Checklist

- [ ] Python 3.10+
- [ ] `pip install -r requirements.txt`
- [ ] `OPENAI_API_KEY` environment variable set
- [ ] `DATABASE_URL` environment variable set
- [ ] PostgreSQL database running
- [ ] Docker installed (for deployment tests)

## What Each Script Tests

| Script | Tests | Duration | Requires API | Requires Docker |
|--------|-------|----------|--------------|-----------------|
| `validate_e2e_workflow.py` | Complete user journey | 30-60s | ✓ | ✗ |
| `validate_error_scenarios.py` | Error handling | 5-10s | ✗ | ✗ |
| `validate_docker_deployment.py` | Deployment | 60-90s | ✗ | ✓ |
| `validate_performance.py` | Performance metrics | 60-120s | ✓ | ✗ |
| `validate_ui_ux.py` | UI quality | <5s | ✗ | ✗ |

## Expected Results

### ✓ Success
- All tests pass
- Green checkmarks
- Exit code 0

### ⚠ Warning
- Non-critical issues
- Yellow warnings
- Optional features missing

### ✗ Failure
- Critical issues
- Red X marks
- Exit code 1

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Missing API key | Set `OPENAI_API_KEY` in `.env` |
| Database connection failed | Run `docker-compose up -d postgres` |
| Docker not found | Install Docker Desktop |
| Module not found | Run `pip install -r requirements.txt` |
| Port already in use | Stop conflicting services |

## Performance Thresholds

| Metric | Threshold |
|--------|-----------|
| AI response generation | < 10 seconds |
| Whiteboard snapshot save | < 1 second |
| Session list retrieval | < 2 seconds |
| Database query | < 1 second |
| Session retrieval | < 0.5 seconds |

## CI/CD Integration

```yaml
# Add to .github/workflows/ci.yml
- name: Run Validations
  run: python run_all_validations.py
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

## Manual Testing Checklist

After automated validation, manually verify:

- [ ] UI appears correctly on different screen sizes
- [ ] All buttons respond to clicks
- [ ] Forms validate input properly
- [ ] Error messages are helpful
- [ ] Navigation flow is intuitive
- [ ] Whiteboard drawing is responsive
- [ ] Audio/video controls work (if enabled)

## Support

For detailed information, see `VALIDATION_GUIDE.md`

For implementation details, see `TASK_23_VALIDATION_IMPLEMENTATION.md`
