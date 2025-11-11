# Resume Manager Implementation

## Overview

The Resume Manager component handles resume upload, parsing, and extraction of structured candidate information using LLM-based analysis. This enables the AI interviewer to generate resume-aware interview problems tailored to the candidate's experience level and domain expertise.

## Components

### ResumeManager Class

Located in `src/resume/resume_manager.py`, the ResumeManager provides:

- **Resume Upload**: Accepts PDF and TXT file formats
- **Text Extraction**: Extracts text from PDF files using PyPDF2
- **LLM-based Parsing**: Uses OpenAI GPT-4 or Anthropic Claude to extract structured data
- **Data Persistence**: Saves and retrieves resume data from PostgreSQL database
- **Experience Classification**: Categorizes candidates as junior, mid, senior, or staff level

## Key Features

### Supported File Formats

- **PDF**: Extracted using PyPDF2 library
- **TXT**: Direct text file reading

### Extracted Information

The ResumeManager extracts the following structured data:

1. **Basic Information**
   - Name
   - Email address

2. **Experience Details**
   - Experience level (junior/mid/senior/staff)
   - Years of professional experience
   - Domain expertise areas (e.g., backend, distributed-systems, cloud)

3. **Work History**
   - Company name
   - Job title
   - Duration
   - Role description

4. **Education**
   - Institution name
   - Degree type
   - Field of study
   - Graduation year

5. **Technical Skills**
   - List of technical skills and technologies

### Experience Level Classification

The system classifies candidates into four levels:

- **Junior**: 0-2 years of experience, entry-level roles
- **Mid**: 3-5 years of experience, intermediate roles
- **Senior**: 6-10 years of experience, senior roles
- **Staff**: 10+ years of experience, staff/principal/lead roles

### Domain Expertise

Common domain areas identified:
- backend
- frontend
- full-stack
- distributed-systems
- cloud
- devops
- data-engineering
- machine-learning
- mobile
- security

## API Reference

### ResumeManager Methods

#### `__init__(data_store, config, logger=None)`

Initialize ResumeManager with dependencies.

**Parameters:**
- `data_store`: IDataStore instance for database operations
- `config`: Configuration object with AI provider settings
- `logger`: Optional LoggingManager instance

#### `upload_resume(file_path: str, user_id: str) -> ResumeData`

Upload and parse a resume file.

**Parameters:**
- `file_path`: Path to resume file (PDF or TXT)
- `user_id`: User identifier

**Returns:**
- ResumeData object with extracted information

**Raises:**
- `ValidationError`: If file format is invalid or file doesn't exist
- `AIProviderError`: If LLM parsing fails

#### `parse_resume(file_path: str) -> ResumeData`

Parse resume file and extract structured data using LLM.

**Parameters:**
- `file_path`: Path to resume file

**Returns:**
- ResumeData object with extracted information

#### `get_resume(user_id: str) -> Optional[ResumeData]`

Retrieve resume data for a user from database.

**Parameters:**
- `user_id`: User identifier

**Returns:**
- ResumeData if found, None otherwise

#### `save_resume(user_id: str, resume_data: ResumeData) -> None`

Save resume data to database.

**Parameters:**
- `user_id`: User identifier
- `resume_data`: ResumeData object to save

#### `extract_experience_level(resume_data: ResumeData) -> str`

Extract experience level from resume data.

**Parameters:**
- `resume_data`: ResumeData object

**Returns:**
- Experience level string (junior/mid/senior/staff)

#### `extract_domain_expertise(resume_data: ResumeData) -> List[str]`

Extract domain expertise from resume data.

**Parameters:**
- `resume_data`: ResumeData object

**Returns:**
- List of domain expertise areas

## Database Schema

Resume data is stored in the `resumes` table:

```sql
CREATE TABLE resumes (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    email VARCHAR(200),
    experience_level VARCHAR(20) NOT NULL,
    years_of_experience INTEGER NOT NULL,
    domain_expertise JSONB NOT NULL,
    work_experience JSONB NOT NULL,
    education JSONB NOT NULL,
    skills JSONB NOT NULL,
    raw_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Example

```python
from src.resume.resume_manager import ResumeManager
from src.database.data_store import PostgresDataStore
from src.config import get_config

# Initialize dependencies
config = get_config()
data_store = PostgresDataStore(
    host=config.database.host,
    port=config.database.port,
    database=config.database.database,
    user=config.database.user,
    password=config.database.password,
)

# Create ResumeManager
resume_manager = ResumeManager(
    data_store=data_store,
    config=config,
)

# Upload and parse resume
resume_data = resume_manager.upload_resume(
    file_path="path/to/resume.pdf",
    user_id="user123",
)

# Access extracted information
print(f"Name: {resume_data.name}")
print(f"Experience Level: {resume_data.experience_level}")
print(f"Years of Experience: {resume_data.years_of_experience}")
print(f"Domain Expertise: {', '.join(resume_data.domain_expertise)}")

# Retrieve resume later
saved_resume = resume_manager.get_resume("user123")
```

## LLM Integration

The ResumeManager uses LLM to parse resumes with the following approach:

1. **Text Extraction**: Extract raw text from PDF or TXT file
2. **Prompt Construction**: Build structured prompt with extraction guidelines
3. **LLM Call**: Send prompt to OpenAI GPT-4 or Anthropic Claude
4. **JSON Parsing**: Parse LLM response as JSON
5. **Data Validation**: Validate and structure extracted data
6. **Database Storage**: Save to PostgreSQL database

### LLM Prompt Structure

The prompt instructs the LLM to:
- Extract specific fields in JSON format
- Classify experience level based on years and role seniority
- Identify domain expertise using standardized naming
- Structure work experience and education entries
- Extract technical skills list

## Error Handling

The ResumeManager handles various error scenarios:

- **File Not Found**: Raises ValidationError if file doesn't exist
- **Invalid Format**: Raises ValidationError for unsupported file types
- **Empty Resume**: Raises ValidationError if resume text is too short
- **LLM Failure**: Raises AIProviderError if LLM call fails
- **JSON Parse Error**: Raises AIProviderError if LLM response is invalid JSON
- **Database Error**: Propagates DataStoreError from database operations

## Testing

Test file: `test_resume_manager.py`

Tests cover:
- ResumeManager initialization
- Text extraction from TXT files
- Resume parsing with mocked LLM
- Resume retrieval from database
- Resume saving to database

Run tests:
```bash
python test_resume_manager.py
```

## Dependencies

- **PyPDF2**: PDF text extraction
- **openai**: OpenAI API client (optional)
- **anthropic**: Anthropic API client (optional)
- **psycopg2**: PostgreSQL database driver

## Future Enhancements

Potential improvements:
- Support for DOCX format
- OCR for scanned PDFs
- Resume quality scoring
- Duplicate detection
- Batch processing
- Resume comparison
- Skills gap analysis
