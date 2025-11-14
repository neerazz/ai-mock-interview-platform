# Resume Manager

The Resume Manager handles resume upload, parsing, and analysis to generate personalized interview problems.

## Overview

The Resume Manager:

- Accepts PDF and text resumes
- Extracts key information
- Analyzes experience level
- Identifies domain expertise
- Stores resume data

## Resume Analysis

### Experience Level Detection

- Junior (0-2 years)
- Mid-level (2-5 years)
- Senior (5-10 years)
- Staff+ (10+ years)

### Domain Expertise Extraction

- E-commerce
- Fintech
- Social media
- Healthcare
- Gaming
- Enterprise software

### Skills Identification

- Programming languages
- Frameworks and tools
- Cloud platforms
- Databases
- System design patterns

## Usage Example

```python
# Upload and parse resume
resume_data = resume_manager.parse_resume(
    file_content=pdf_bytes,
    file_type="pdf"
)

# Access parsed data
print(f"Experience: {resume_data.experience_level}")
print(f"Domains: {resume_data.domains}")
print(f"Skills: {resume_data.skills}")
```

## Related Components

- [Session Manager](session-manager.md)
- [AI Interviewer](ai-interviewer.md)
