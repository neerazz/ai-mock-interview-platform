# AI Mock Interview Platform - POC Specification
## Python-Only Local Implementation

**Version**: 1.0 (POC)
**Last Updated**: November 10, 2025
**Maintainer**: @neerazz

---

## Project Overview

A **local proof-of-concept** for an AI-powered mock interview platform focused on **System Design interviews**. This POC uses **Python for both UI and backend** to keep complexity minimal while demonstrating core functionality.

### Key Simplifications for POC:
- Python-only (no JavaScript/Node.js)
- Local execution (no cloud deployment)
- SQLite database (no PostgreSQL setup)
- Local file storage (no S3/cloud storage)
- Streamlit for UI (no React/Next.js)
- Focus on System Design interviews only

---

## Tech Stack

### Core Technologies
- **UI Framework**: Streamlit
- **Backend**: Python 3.10+
- **Database**: SQLite
- **File Storage**: Local filesystem
- **AI/LLM**: OpenAI GPT-4 or Anthropic Claude
- **Speech-to-Text**: OpenAI Whisper
- **Agent Framework**: LangChain
- **Whiteboard**: streamlit-drawable-canvas

### Key Python Libraries
```
streamlit>=1.28.0
langchain>=0.1.0
openai>=1.0.0
anthropic>=0.18.0
pyPDF2>=3.0.0
sqlite3 (built-in)
pillow>=10.0.0
streamlit-drawable-canvas>=0.9.0
streamlit-webrtc>=0.47.0
langchain-openai>=0.0.2
```

---

## Project Structure

```
ai-mock-interview-platform/
├── app.py                    # Main Streamlit app
├── requirements.txt
├── .env                     # API keys (gitignored)
├── data/
│   ├── interviews.db        # SQLite database
│   ├── uploads/             # User resumes
│   └── recordings/          # Session recordings
├── src/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── home.py          # Landing page
│   │   ├── upload.py        # Resume upload
│   │   ├── config.py        # Session config
│   │   ├── interview.py     # Main interview UI
│   │   └── results.py       # Feedback display
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── interviewer.py   # AI interviewer agent
│   │   ├── analyzer.py      # Multi-modal analysis
│   │   └── prompts.py       # Prompt templates
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py        # Database schema
│   │   └── operations.py    # CRUD operations
│   └── utils/
│       ├── __init__.py
│       ├── resume_parser.py # Extract resume data
│       ├── recorder.py      # A/V recording
│       └── transcriber.py   # Speech-to-text
└── tests/
    └── __init__.py
```

---

## Code Quality & Testing Guidelines

**IMPORTANT**: This project includes a comprehensive `.cursorrules` file that ensures code quality, modularity, extensibility, and maintainability.

### Always Check .cursorrules Before Coding
Before writing any code, review the `.cursorrules` file in the repository root. It contains:

- **Modularity Rules**: Keep functions small, single responsibility, clear separation of concerns
- **Testing Requirements**: 80% minimum coverage, 95%+ for critical paths
- **Code Style Standards**: PEP 8, type hints, Google-style docstrings
- **Documentation Guidelines**: When to document, how to document
- **Error Handling**: Proper logging, graceful failures
- **File Organization**: When to create vs update files
- **Git Commit Guidelines**: Conventional commits format
- **Security Best Practices**: Never commit secrets, input validation

### Key Principles from .cursorrules

1. **Check Existing Code First** - Never duplicate functionality
2. **Write Tests Immediately** - Don't wait until the end
3. **Document As You Go** - Add docstrings and type hints
4. **Keep It Simple** - Simplest solution is often best
5. **Handle Errors Gracefully** - Proper logging and error messages

### Testing Standards

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Coverage targets
# - Minimum: 80% for all modules
# - Critical paths (AI agent, DB): 95%+
```

### Code Review Checklist
Before committing code, ensure:
- [ ] Tests written and passing
- [ ] Code coverage meets requirements
- [ ] Docstrings added
- [ ] Type hints included
- [ ] .cursorrules guidelines followed
- [ ] No duplicate code
- [ ] Error handling implemented

**See `.cursorrules` for complete details**



## Core Features (POC)

### 1. Resume Upload & Parsing
- Upload PDF/DOCX resume
- Extract text using PyPDF2
- Parse structure with LLM
- Store in SQLite

### 2. Session Configuration
- Duration slider (10-60 mins)
- Start interview button

### 3. Interview Interface
- **Left Panel**: AI interviewer chat
- **Center**: Whiteboard canvas
- **Right Panel**: Transcript display
- **Bottom**: Recording controls

### 4. AI Interviewer
- Resume-aware problem generation
- Follow-up questions based on whiteboard
- Clarifying questions

### 5. Whiteboard
- Simple drawable canvas
- Save drawings as images

### 6. Recording
- Audio capture via streamlit-webrtc
- Real-time transcription
- Store audio + transcript

### 7. Feedback Generation
- Analyze transcript + whiteboard
- Generate structured feedback
- Display scores and recommendations

---

## Implementation Phases

### Phase 1: Project Setup (Status: To Do)
**Tasks:**
- [ ] Create project structure
- [ ] Set up virtual environment
- [ ] Install dependencies
- [ ] Create .env template
- [ ] Initialize SQLite database
- [ ] Create basic Streamlit app skeleton

---

### Phase 2: Database Schema (Status: To Do)
**Tasks:**
- [ ] Design database schema (users, sessions, interviews)
- [ ] Create SQLite tables
- [ ] Implement CRUD operations
- [ ] Add sample data for testing

**Schema:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP
);

CREATE TABLE resumes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    filename TEXT,
    file_path TEXT,
    parsed_data JSON,
    uploaded_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    resume_id INTEGER,
    duration_minutes INTEGER,
    status TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

CREATE TABLE interviews (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    transcript TEXT,
    whiteboard_image_path TEXT,
    audio_path TEXT,
    feedback JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

### Phase 3: Resume Upload & Parsing (Status: To Do)
**Tasks:**
- [ ] Create file upload component
- [ ] Implement PDF text extraction (PyPDF2)
- [ ] Build LLM-based parser for structure
- [ ] Store parsed resume in database
- [ ] Display parsed information to user
- [ ] Add edit capability

**Resume Parser Prompt:**
```python
EXTRACT_RESUME_PROMPT = """
Extract structured information from this resume text:

{resume_text}

Return JSON with:
- name
- email
- education (list of degrees)
- work_experience (list with company, role, duration, achievements)
- skills (list)
- projects (list)
"""
```

---

### Phase 4: Streamlit UI Pages (Status: To Do)
**Tasks:**
- [ ] Create home page with navigation
- [ ] Build resume upload page
- [ ] Implement session configuration page
- [ ] Design interview interface layout
- [ ] Create results/feedback page
- [ ] Add session state management

---

### Phase 5: Whiteboard Integration (Status: To Do)
**Tasks:**
- [ ] Integrate streamlit-drawable-canvas
- [ ] Add drawing tools (pen, shapes, text)
- [ ] Implement clear/undo functions
- [ ] Save whiteboard state to file
- [ ] Display saved whiteboards

**Code Snippet:**
```python
from streamlit_drawable_canvas import st_canvas

canvas_result = st_canvas(
    fill_color="#ffffff",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#ffffff",
    height=600,
    width=800,
    drawing_mode="freedraw",
    key="whiteboard",
)
```

---

### Phase 6: Audio Recording & Transcription (Status: To Do)
**Tasks:**
- [ ] Integrate streamlit-webrtc for audio
- [ ] Implement audio recording
- [ ] Save audio files locally
- [ ] Connect to Whisper API
- [ ] Display live transcription
- [ ] Store transcript in database

---

### Phase 7: AI Interviewer Agent (Status: To Do)
**Tasks:**
- [ ] Design agent architecture with LangChain
- [ ] Create system design problem generator
- [ ] Implement resume context retriever
- [ ] Build conversation memory
- [ ] Add follow-up question logic
- [ ] Implement clarification triggers
- [ ] Add time-based interventions

**Agent Architecture:**
```python
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

tools = [
    Tool(
        name="ResumeRetriever",
        func=retrieve_resume_context,
        description="Get relevant info from candidate resume"
    ),
    Tool(
        name="WhiteboardAnalyzer",
        func=analyze_whiteboard,
        description="Analyze current whiteboard diagram"
    ),
]

llm = ChatOpenAI(model="gpt-4", temperature=0.7)
agent = AgentExecutor(tools=tools, llm=llm)
```

---

### Phase 8: Whiteboard Analysis (Status: To Do)
**Tasks:**
- [ ] Capture whiteboard as image
- [ ] Use GPT-4 Vision for analysis
- [ ] Extract system components
- [ ] Identify design patterns
- [ ] Flag missing elements
- [ ] Store analysis results

---

### Phase 9: Feedback Generation (Status: To Do)
**Tasks:**
- [ ] Aggregate transcript + whiteboard data
- [ ] Design evaluation rubric
- [ ] Implement scoring algorithm
- [ ] Generate strengths/weaknesses
- [ ] Create actionable recommendations
- [ ] Format feedback as markdown/JSON
- [ ] Display in results page

**Rubric:**
- Technical Depth (0-10)
- Communication Clarity (0-10)
- Problem Solving (0-10)
- Scalability Consideration (0-10)
- Trade-off Analysis (0-10)

---

### Phase 10: Report Export (Status: To Do)
**Tasks:**
- [ ] Create PDF report template
- [ ] Include session summary
- [ ] Embed whiteboard screenshots
- [ ] Add transcript excerpts
- [ ] Show performance scores
- [ ] Generate download link

---

### Phase 11: Testing (Status: To Do)
**Tasks:**
- [ ] Unit tests for resume parser
- [ ] Integration tests for agent
- [ ] UI testing with Streamlit
- [ ] End-to-end interview simulation
- [ ] Edge case handling

---

### Phase 12: Polish & Documentation (Status: To Do)
**Tasks:**
- [ ] Add error handling
- [ ] Improve UI/UX
- [ ] Write README with setup instructions
- [ ] Create demo video
- [ ] Add usage examples
- [ ] Document API keys setup

---

## AI Model Configuration

### Interviewer Agent
- **Model**: GPT-4 Turbo
- **Temperature**: 0.7
- **Max Tokens**: 500
- **System Prompt**: Act as a senior FANG engineer conducting a system design interview

### Resume Parser
- **Model**: GPT-3.5 Turbo (cost-effective)
- **Temperature**: 0.2
- **Output**: Structured JSON

### Whiteboard Analysis
- **Model**: GPT-4 Vision
- **Temperature**: 0.5
- **Trigger**: Every 60 seconds or on-demand

### Feedback Generator
- **Model**: GPT-4 Turbo
- **Temperature**: 0.6
- **Input**: Full transcript + whiteboard images

---

## Environment Setup

### .env Template
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DB_PATH=data/interviews.db
UPLOAD_DIR=data/uploads
RECORDING_DIR=data/recordings
```

### Installation
```bash
# Clone repository
git clone https://github.com/neerazz/ai-mock-interview-platform.git
cd ai-mock-interview-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys

# Initialize database
python -m src.db.models

# Run application
streamlit run app.py
```

---

## Running the POC

1. **Start Streamlit app**: `streamlit run app.py`
2. **Upload Resume**: Navigate to upload page
3. **Configure Session**: Set duration
4. **Start Interview**: Begin mock interview
5. **Interact**: Answer questions, draw on whiteboard
6. **View Feedback**: See results after completion

---

## Cost Estimation (Per Interview)

- Resume Parsing: ~$0.02
- Interview Agent (30 min): ~$0.50
- Whiteboard Analysis (10x): ~$0.30
- Feedback Generation: ~$0.10
**Total per interview**: ~$0.92

---

## Future Enhancements

- Add user authentication
- Multi-user support
- Interview history
- Different interview types (behavioral, coding)
- Deploy to cloud (Streamlit Cloud)
- Add peer review feature
- Export to more formats

---

## Success Metrics

- Interview completion rate
- User satisfaction (post-interview survey)
- Feedback quality (user ratings)
- System reliability (crash rate)

---

## Contributing

See CONTRIBUTING.md

## License

MIT License

---

**Maintainer**: @neerazz  
**Status**: POC Development  
**Last Updated**: November 10, 2025
