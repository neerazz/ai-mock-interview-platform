# Design Document: AI-Powered Mock Interview Platform

## Overview

The AI-powered mock interview platform is a local Python application that enables candidates to practice system design interviews with an AI interviewer. The platform supports multiple communication modes (audio, video, whiteboard, screen share), provides real-time interaction, and generates comprehensive feedback with structured improvement plans.

### Design Principles

1. **Simplicity First**: Minimize dependencies and complexity for POC
2. **Modularity**: Clear separation of concerns with well-defined interfaces
3. **Extensibility**: Easy to add new features without modifying existing code
4. **Local-First**: All data stored locally, no cloud dependencies
5. **Testability**: Design for easy unit and integration testing

### Technology Choices and Rationale

**Streamlit for UI**:
- Rapid prototyping with Python-only stack
- Built-in components for chat, file upload, and layout
- Easy integration with ML/AI libraries
- No frontend JavaScript required
- Good for POC and internal tools

**PostgreSQL in Docker**:
- Production-grade database from day one
- Same engine used in cloud (AWS RDS, Azure Database)
- JSONB support for flexible schema
- Easy local setup with Docker
- Clear migration path to cloud

**LangChain for AI**:
- Unified interface for multiple LLM providers
- Built-in conversation memory management
- Agent framework for complex interactions
- Active community and good documentation

**streamlit-webrtc for Audio/Video**:
- Real-time audio capture in browser
- No additional server infrastructure needed
- Works within Streamlit framework
- Supports both audio and video streams

**OpenAI Whisper for Transcription**:
- State-of-the-art accuracy
- Fast transcription (< 2 seconds)
- Supports multiple languages
- Can run locally or via API

### SOLID Principles Implementation

The platform architecture follows SOLID principles for maintainable, extensible code:

**Single Responsibility Principle (SRP)**:
- Each component has one clear responsibility
- SessionManager: orchestrates sessions
- CommunicationManager: handles I/O modes
- AIInterviewer: conducts interviews
- EvaluationManager: generates feedback
- No component handles multiple concerns

**Open-Closed Principle (OCP)**:
- Components are open for extension, closed for modification
- New AI providers can be added without modifying existing code
- New communication modes can be plugged in via interface
- New evaluation strategies can be implemented through inheritance

**Liskov Substitution Principle (LSP)**:
- IDataStore interface allows PostgreSQL or cloud database substitution
- Any IDataStore implementation can replace another without breaking code
- Communication mode handlers are interchangeable

**Interface Segregation Principle (ISP)**:
- Focused interfaces with minimal methods
- Clients depend only on methods they use
- No "fat" interfaces with unused methods

**Dependency Inversion Principle (DIP)**:
- High-level modules depend on abstractions (interfaces), not concrete implementations
- SessionManager depends on IDataStore interface, not PostgresDataStore
- Enables dependency injection and testing with mocks

## Architecture

### High-Level Architecture

```mermaid
graph TB
    UI[Streamlit UI Layer]
    SM[Session Manager]
    CM[Communication Manager]
    AI[AI Interviewer Agent]
    EM[Evaluation Manager]
    DS[Data Store]
    FS[File Storage]
    TT[Token Tracker]
    LM[Logging Manager]
    MC[Metrics Collector]
    
    UI --> SM
    UI --> CM
    SM --> AI
    SM --> EM
    SM --> DS
    CM --> FS
    AI --> DS
    AI --> TT
    EM --> DS
    EM --> FS
    
    SM -.-> LM
    CM -.-> LM
    AI -.-> LM
    EM -.-> LM
    DS -.-> LM
    
    SM -.-> MC
    AI -.-> MC
    DS -.-> MC
    
    TT --> DS
    LM --> DS
    MC --> DS
```

### Layer Responsibilities

**UI Layer (Streamlit)**
- Renders user interface components with 3-panel layout
- Left panel: AI interviewer chat interface
- Center panel: Whiteboard canvas for system design diagrams
- Right panel: Real-time transcript display
- Bottom: Recording controls for audio/video
- Handles user interactions
- Displays interview content and feedback
- Manages communication mode controls

**Session Manager**
- Creates and manages interview sessions
- Coordinates between components
- Handles session lifecycle (start, pause, end)
- Triggers evaluation generation

**Communication Manager**
- Handles audio recording and transcription
- Manages video capture
- Controls whiteboard canvas
- Captures screen share content
- Stores media files to filesystem

**AI Interviewer Agent**
- Generates resume-aware interview questions based on candidate experience
- Analyzes candidate responses and whiteboard content
- Maintains conversation context
- Adapts difficulty based on performance
- Asks clarifying questions when responses are ambiguous

**Evaluation Manager**
- Analyzes session data across all communication modes
- Generates structured feedback reports
- Calculates confidence levels and scores
- Creates improvement plans

**Data Store (PostgreSQL in Docker)**
- Persists session metadata
- Stores conversation history
- Maintains evaluation reports
- Tracks user progress
- Provides abstraction layer for future cloud migration

**File Storage**
- Organizes media files by session
- Stores audio, video, whiteboard, screen captures
- Manages file lifecycle

## Components and Interfaces

### Dependency Injection Pattern

All components use dependency injection to promote testability, modularity, and loose coupling. Dependencies are injected through constructor parameters rather than created internally.

**Benefits**:
- Easy to mock dependencies for unit testing
- Clear declaration of component dependencies
- Flexible component composition
- Supports interface-based programming

**Example Implementation**:
```python
class SessionManager:
    """Session manager with injected dependencies."""
    
    def __init__(
        self,
        data_store: IDataStore,
        ai_interviewer: AIInterviewer,
        evaluation_manager: EvaluationManager,
        communication_manager: CommunicationManager,
        logger: LoggingManager
    ):
        self.data_store = data_store
        self.ai_interviewer = ai_interviewer
        self.evaluation_manager = evaluation_manager
        self.communication_manager = communication_manager
        self.logger = logger

# Application initialization with dependency injection
def create_app() -> SessionManager:
    """Factory function to wire up dependencies."""
    # Create infrastructure components
    data_store = PostgresDataStore(connection_string=config.database_url)
    file_storage = FileStorage(data_dir=config.data_dir)
    logger = LoggingManager(config=config.logging)
    token_tracker = TokenTracker(data_store=data_store)
    
    # Create domain components
    resume_manager = ResumeManager(data_store=data_store, logger=logger)
    communication_manager = CommunicationManager(
        file_storage=file_storage,
        logger=logger
    )
    ai_interviewer = AIInterviewer(
        config=config.ai,
        token_tracker=token_tracker,
        logger=logger
    )
    evaluation_manager = EvaluationManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        logger=logger
    )
    
    # Create session manager with all dependencies
    session_manager = SessionManager(
        data_store=data_store,
        ai_interviewer=ai_interviewer,
        evaluation_manager=evaluation_manager,
        communication_manager=communication_manager,
        logger=logger
    )
    
    return session_manager
```

### 1. Session Manager

**Purpose**: Orchestrates interview session lifecycle and coordinates between components

**Interface**:
```python
class SessionManager:
    def create_session(self, config: SessionConfig) -> Session
    def start_session(self, session_id: str) -> None
    def end_session(self, session_id: str) -> EvaluationReport
    def get_session(self, session_id: str) -> Session
    def list_sessions(self) -> List[SessionSummary]
    def get_active_session(self) -> Optional[Session]
```

**Key Responsibilities**:
- Session creation with unique identifiers
- State management (active, paused, completed)
- Coordination with AI Interviewer and Evaluation Manager
- Database persistence

### 2. Communication Manager

**Purpose**: Handles all input/output modes and media capture

**Interface**:
```python
class CommunicationManager:
    def enable_mode(self, mode: CommunicationMode) -> None
    def disable_mode(self, mode: CommunicationMode) -> None
    def get_enabled_modes(self) -> List[CommunicationMode]
    def record_audio(self, session_id: str) -> AudioRecording
    def transcribe_audio(self, audio_path: str) -> str
    def capture_video(self, session_id: str) -> VideoRecording
    def save_whiteboard(self, session_id: str, canvas_data: bytes) -> str
    def capture_screen(self, session_id: str) -> ScreenCapture
```

**Sub-Components**:
- **AudioHandler**: streamlit-webrtc for audio capture with real-time transcription via OpenAI Whisper (transcription within 2 seconds)
- **VideoHandler**: Video stream capture and storage in H264 format
- **WhiteboardHandler**: streamlit-drawable-canvas integration for drawing system diagrams
- **ScreenShareHandler**: Screen capture functionality with 5-second interval snapshots stored as PNG images
- **TranscriptHandler**: Real-time transcript display and storage (updates within 2 seconds)

**Design Rationale - Screen Capture Interval**:
The 5-second capture interval for screen sharing balances several concerns:
- **Storage efficiency**: Continuous video would consume excessive disk space
- **Performance**: Periodic snapshots minimize CPU/memory overhead
- **Usefulness**: 5 seconds captures meaningful changes without missing important content
- **Review capability**: Provides sufficient granularity for post-interview analysis
- **Cost**: Reduces AI analysis costs compared to full video processing

### 3. Resume Manager

**Purpose**: Handles resume upload, parsing, and extraction of candidate information

**Interface**:
```python
class ResumeManager:
    def upload_resume(self, file_path: str, user_id: str) -> ResumeData
    def parse_resume(self, file_path: str) -> ResumeData
    def extract_experience_level(self, resume_data: ResumeData) -> str
    def extract_domain_expertise(self, resume_data: ResumeData) -> List[str]
    def get_resume(self, user_id: str) -> Optional[ResumeData]
    def save_resume(self, user_id: str, resume_data: ResumeData) -> None

@dataclass
class ResumeData:
    user_id: str
    name: str
    email: str
    experience_level: str  # "junior", "mid", "senior", "staff"
    years_of_experience: int
    domain_expertise: List[str]  # ["backend", "distributed-systems", "cloud"]
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[str]
    raw_text: str
    
@dataclass
class WorkExperience:
    company: str
    title: str
    duration: str
    description: str
    
@dataclass
class Education:
    institution: str
    degree: str
    field: str
    year: str
```

**Key Features**:
- PDF and text resume parsing using LLM
- Structured data extraction
- Experience level classification
- Domain expertise identification
- Database persistence

### 4. AI Interviewer Agent

**Purpose**: Conducts the interview using LLM capabilities with token tracking and resume awareness

**Interface**:
```python
class AIInterviewer:
    def initialize(self, config: AIConfig, resume_data: Optional[ResumeData] = None) -> None
    def start_interview(self, session_id: str) -> InterviewResponse
    def process_response(self, session_id: str, response: str, whiteboard_image: Optional[bytes] = None) -> InterviewResponse
    def generate_followup(self, session_id: str, context: ConversationContext) -> InterviewResponse
    def generate_problem(self, resume_data: ResumeData) -> str
    def analyze_whiteboard(self, whiteboard_image: bytes) -> WhiteboardAnalysis
    def ask_clarifying_question(self, ambiguous_response: str) -> str
    def adapt_difficulty(self, performance_indicators: Dict) -> None
    def get_token_usage(self, session_id: str) -> TokenUsage

@dataclass
class WhiteboardAnalysis:
    components_identified: List[str]
    relationships: List[str]
    missing_elements: List[str]
    design_patterns: List[str]

@dataclass
class InterviewResponse:
    content: str
    token_usage: TokenUsage
    
@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
```

**Key Features**:
- LangChain integration for agent framework
- Support for OpenAI GPT-4 and Anthropic Claude
- Resume-aware problem generation tailored to candidate experience
- Whiteboard content analysis using vision-enabled LLMs
- Conversation memory management
- Context-aware question generation
- Clarifying questions for ambiguous responses
- System design topic coverage (scalability, reliability, trade-offs)
- Real-time token tracking for all API calls
- Cost estimation based on provider pricing

**Resume-Aware Problem Generation**:
```python
def generate_problem(self, resume_data: ResumeData) -> str:
    """
    Generate system design problem based on candidate's resume.
    
    Considers:
    - Experience level (junior/mid/senior/staff)
    - Domain expertise (backend, frontend, distributed systems, etc.)
    - Years of experience
    - Previous company scale
    
    Returns problem statement tailored to candidate background.
    """
    prompt = f"""
    Generate a system design interview problem for a candidate with:
    - Experience Level: {resume_data.experience_level}
    - Years of Experience: {resume_data.years_of_experience}
    - Domain Expertise: {', '.join(resume_data.domain_expertise)}
    - Recent Role: {resume_data.work_experience[0].title if resume_data.work_experience else 'N/A'}
    
    The problem should:
    1. Match their experience level
    2. Relate to their domain expertise
    3. Be appropriate for a 45-minute interview
    4. Cover key system design concepts
    """
    return self.llm.generate(prompt)

### 4. Evaluation Manager

**Purpose**: Analyzes session data and generates comprehensive feedback

**Interface**:
```python
class EvaluationManager:
    def generate_evaluation(self, session_id: str) -> EvaluationReport
    def analyze_communication_modes(self, session_id: str) -> ModeAnalysis
    def calculate_scores(self, session_data: SessionData) -> Dict[str, Score]
    def generate_improvement_plan(self, weaknesses: List[Weakness]) -> ImprovementPlan
```

**Evaluation Structure**:
```python
@dataclass
class EvaluationReport:
    session_id: str
    overall_score: float
    competency_scores: Dict[str, CompetencyScore]
    went_well: List[Feedback]
    went_okay: List[Feedback]
    needs_improvement: List[Feedback]
    improvement_plan: ImprovementPlan
    communication_mode_analysis: ModeAnalysis

@dataclass
class CompetencyScore:
    score: float  # 0-100
    confidence_level: str  # "high", "medium", "low"
    evidence: List[str]

@dataclass
class ImprovementPlan:
    priority_areas: List[str]
    concrete_steps: List[ActionItem]
    resources: List[str]
```

### 5. Data Store

**Purpose**: Persistent storage using PostgreSQL with abstraction for cloud migration

**Database Architecture**:
- Local development: PostgreSQL in Docker container
- Future: Easy migration to cloud databases (AWS RDS, Azure Database, etc.)
- Abstraction layer using repository pattern

**Schema**:

```sql
-- Users/Resumes table
CREATE TABLE resumes (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200),
    email VARCHAR(200),
    experience_level VARCHAR(20) NOT NULL,  -- 'junior', 'mid', 'senior', 'staff'
    years_of_experience INTEGER NOT NULL,
    domain_expertise JSONB NOT NULL,  -- Array of domains
    work_experience JSONB NOT NULL,  -- Array of work experiences
    education JSONB NOT NULL,  -- Array of education entries
    skills JSONB NOT NULL,  -- Array of skills
    raw_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resumes_user_id ON resumes(user_id);
CREATE INDEX idx_resumes_experience_level ON resumes(experience_level);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL,  -- 'active', 'completed'
    enabled_modes JSONB NOT NULL,
    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (user_id) REFERENCES resumes(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);

-- Conversations table
CREATE TABLE conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) NOT NULL,  -- 'interviewer', 'candidate'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_conversations_session ON conversations(session_id, timestamp);

-- Evaluations table
CREATE TABLE evaluations (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL,
    competency_scores JSONB NOT NULL,
    feedback JSONB NOT NULL,
    improvement_plan JSONB NOT NULL,
    communication_analysis JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_evaluations_session ON evaluations(session_id);

-- Media files table
CREATE TABLE media_files (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    file_type VARCHAR(20) NOT NULL,  -- 'audio', 'video', 'whiteboard', 'screen'
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_media_files_session ON media_files(session_id, file_type);

-- Token usage tracking table
CREATE TABLE token_usage (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation VARCHAR(50) NOT NULL,  -- 'question_generation', 'response_analysis', 'evaluation'
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    estimated_cost DECIMAL(10,6) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_token_usage_session ON token_usage(session_id);
CREATE INDEX idx_token_usage_timestamp ON token_usage(timestamp DESC);

-- Audit logs table
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL,  -- 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    component VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    session_id UUID,
    user_id VARCHAR(100),
    message TEXT NOT NULL,
    stack_trace TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_level ON audit_logs(level);
CREATE INDEX idx_audit_logs_session ON audit_logs(session_id);
CREATE INDEX idx_audit_logs_component ON audit_logs(component);
```

**Repository Interface** (Database Abstraction):
```python
from abc import ABC, abstractmethod

class IDataStore(ABC):
    """Abstract interface for data storage - enables easy cloud migration"""
    
    @abstractmethod
    def initialize_schema(self) -> None:
        """Initialize database schema"""
        pass
    
    @abstractmethod
    def save_session(self, session: Session) -> None:
        """Save or update a session"""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Session:
        """Retrieve a session by ID"""
        pass
    
    @abstractmethod
    def save_conversation(self, session_id: str, message: Message) -> None:
        """Save a conversation message"""
        pass
    
    @abstractmethod
    def get_conversation_history(self, session_id: str) -> List[Message]:
        """Retrieve all messages for a session"""
        pass
    
    @abstractmethod
    def save_evaluation(self, evaluation: EvaluationReport) -> None:
        """Save an evaluation report"""
        pass
    
    @abstractmethod
    def get_evaluation(self, session_id: str) -> EvaluationReport:
        """Retrieve evaluation for a session"""
        pass
    
    @abstractmethod
    def save_media_reference(self, session_id: str, media: MediaFile) -> None:
        """Save media file reference"""
        pass
    
    @abstractmethod
    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[SessionSummary]:
        """List sessions with pagination"""
        pass

class PostgresDataStore(IDataStore):
    """PostgreSQL implementation of data store"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    # Implementation of all abstract methods...

class CloudDataStore(IDataStore):
    """Future cloud database implementation (AWS RDS, Azure, etc.)"""
    pass
```

**Docker Configuration**:
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: interview_platform_db
    environment:
      POSTGRES_DB: interview_platform
      POSTGRES_USER: interview_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U interview_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - interview_network

  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: interview_platform_app
    environment:
      - DATABASE_URL=postgresql://interview_user:${DB_PASSWORD}@postgres:5432/interview_platform
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATA_DIR=/app/data
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - interview_network
    command: streamlit run src/main.py --server.port=8501 --server.address=0.0.0.0

volumes:
  postgres_data:

networks:
  interview_network:
    driver: bridge
```

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    ffmpeg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .streamlit/ ./.streamlit/
COPY config.yaml .

# Create data and logs directories
RUN mkdir -p /app/data /app/logs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Database Initialization Script** (init.sql):
```sql
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (schema from above)
-- Users/Resumes table
CREATE TABLE IF NOT EXISTS resumes (
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

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL,
    enabled_modes JSONB NOT NULL,
    ai_provider VARCHAR(50) NOT NULL,
    ai_model VARCHAR(100) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (user_id) REFERENCES resumes(user_id) ON DELETE CASCADE
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Evaluations table
CREATE TABLE IF NOT EXISTS evaluations (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID UNIQUE NOT NULL,
    overall_score DECIMAL(5,2) NOT NULL,
    competency_scores JSONB NOT NULL,
    feedback JSONB NOT NULL,
    improvement_plan JSONB NOT NULL,
    communication_analysis JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Media files table
CREATE TABLE IF NOT EXISTS media_files (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    file_type VARCHAR(20) NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes BIGINT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Token usage tracking table
CREATE TABLE IF NOT EXISTS token_usage (
    id BIGSERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    operation VARCHAR(50) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    estimated_cost DECIMAL(10,6) NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    session_id UUID,
    user_id VARCHAR(100),
    message TEXT NOT NULL,
    stack_trace TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE SET NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_experience_level ON resumes(experience_level);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_evaluations_session ON evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_media_files_session ON media_files(session_id, file_type);
CREATE INDEX IF NOT EXISTS idx_token_usage_session ON token_usage(session_id);
CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp ON token_usage(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_level ON audit_logs(level);
CREATE INDEX IF NOT EXISTS idx_audit_logs_session ON audit_logs(session_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_component ON audit_logs(component);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO interview_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO interview_user;
```

**Startup Script** (startup.sh):
```bash
#!/bin/bash

# Startup script for AI Mock Interview Platform

set -e

echo "Starting AI Mock Interview Platform..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file with required environment variables."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Validate required environment variables
required_vars=("DB_PASSWORD" "OPENAI_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set in .env file"
        exit 1
    fi
done

# Create necessary directories
mkdir -p data/sessions logs

# Start Docker services
echo "Starting Docker services..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec interview_platform_db pg_isready -U interview_user; do
    sleep 1
done

echo "PostgreSQL is ready!"

# Check database connection
echo "Verifying database connection..."
docker exec interview_platform_db psql -U interview_user -d interview_platform -c "SELECT 1;" > /dev/null

if [ $? -eq 0 ]; then
    echo "Database connection successful!"
else
    echo "Error: Could not connect to database"
    exit 1
fi

# Display service status
echo ""
echo "Services started successfully!"
echo "================================"
echo "PostgreSQL: http://localhost:5432"
echo "Streamlit App: http://localhost:8501"
echo "================================"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
```

**Environment Template** (.env.template):
```bash
# Database Configuration
DB_PASSWORD=your_secure_password_here

# AI Provider API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Application Configuration
LOG_LEVEL=INFO
DATA_DIR=./data

# Optional: Token Budget
MAX_TOKENS_PER_SESSION=50000
TOKEN_BUDGET_WARNING_THRESHOLD=0.8
```

### 6. Token Tracker

**Purpose**: Track and monitor AI API token usage and costs

**Interface**:
```python
class TokenTracker:
    def record_usage(
        self,
        session_id: str,
        operation: str,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> None
    def get_session_usage(self, session_id: str) -> SessionTokenUsage
    def get_total_cost(self, session_id: str) -> float
    def get_usage_breakdown(self, session_id: str) -> Dict[str, TokenUsage]

@dataclass
class SessionTokenUsage:
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: float
    breakdown_by_operation: Dict[str, TokenUsage]
```

**Key Features**:
- Real-time token counting for all AI API calls
- Cost estimation based on provider pricing
- Per-session and per-operation tracking
- Historical usage analytics
- Budget alerts and warnings

### 7. Logging System

**Purpose**: Comprehensive logging for debugging, monitoring, and audit trails

**Architecture**:
```python
class LoggingManager:
    def __init__(self, config: LoggingConfig):
        self.logger = self._setup_logger(config)
        self.db_handler = DatabaseLogHandler()
        self.file_handler = RotatingFileHandler()
    
    def log_operation(
        self,
        level: str,
        component: str,
        operation: str,
        message: str,
        session_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
        exc_info: Optional[Exception] = None
    ) -> None
    
    def log_error(
        self,
        component: str,
        operation: str,
        error: Exception,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> None
    
    def log_api_call(
        self,
        provider: str,
        endpoint: str,
        request_data: Dict,
        response_data: Dict,
        duration_ms: float,
        session_id: Optional[str] = None
    ) -> None
```

**Logging Levels**:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error events that might still allow the application to continue
- **CRITICAL**: Critical events that may cause the application to abort

**Logging Destinations**:
1. **Console**: Real-time output during development
2. **File**: Rotating log files with size/time-based rotation
3. **Database**: Structured logs in audit_logs table for querying
4. **Structured JSON**: Machine-readable format for log aggregation

**Log Format**:
```json
{
  "timestamp": "2024-11-10T14:30:00.123Z",
  "level": "INFO",
  "component": "AIInterviewer",
  "operation": "process_response",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Processing candidate response",
  "metadata": {
    "response_length": 250,
    "processing_time_ms": 1234
  }
}
```

**Key Logging Points**:
- Session lifecycle events (create, start, end)
- AI API calls (request, response, errors)
- Communication mode changes
- Media file operations
- Database operations
- Error conditions and exceptions
- Performance metrics
- User actions

### 8. File Storage

**Purpose**: Organize and manage media files on local filesystem

**Directory Structure**:
```
data/
├── sessions/
│   ├── {session_id}/
│   │   ├── audio/
│   │   │   ├── recording_001.wav
│   │   │   └── recording_002.wav
│   │   ├── video/
│   │   │   └── interview.mp4
│   │   ├── whiteboard/
│   │   │   ├── snapshot_001.png
│   │   │   └── snapshot_002.png
│   │   └── screen/
│   │       ├── capture_001.png
│   │       └── capture_002.png
└── postgres/
    └── (Docker volume data)
```

**Interface**:
```python
class FileStorage:
    def save_audio(self, session_id: str, audio_data: bytes) -> str
    def save_video(self, session_id: str, video_data: bytes) -> str
    def save_whiteboard(self, session_id: str, image_data: bytes) -> str
    def save_screen_capture(self, session_id: str, image_data: bytes) -> str
    def get_file_path(self, session_id: str, file_type: str, filename: str) -> str
    def cleanup_session(self, session_id: str) -> None
```

**File Format Specifications**:
- **Audio files**: WAV format for lossless quality and compatibility
- **Video files**: MP4 format with H264 codec for efficient storage
- **Whiteboard snapshots**: PNG format for lossless diagram quality
- **Screen captures**: PNG format for clarity and text readability
- **Transcripts**: Plain text files with timestamps

**Storage Organization**:
- Each session has dedicated directory: `data/sessions/{session_id}/`
- Media types separated into subdirectories (audio/, video/, whiteboard/, screen/)
- Sequential numbering for multiple files of same type
- File references stored in database media_files table

## User Interface Design

### Interview Interface Layout

The interview interface uses a 3-panel layout optimized for system design interviews:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Header / Navigation                       │
├──────────────┬──────────────────────────┬──────────────────────┤
│              │                          │                      │
│   AI Chat    │    Whiteboard Canvas     │    Transcript       │
│   (Left)     │       (Center)           │     (Right)         │
│              │                          │                      │
│  - Questions │  - Drawing tools         │  - Real-time text   │
│  - Responses │  - System diagrams       │  - Conversation     │
│  - Follow-ups│  - Save snapshots        │  - Searchable       │
│              │  - Clear canvas          │  - Timestamps       │
│              │                          │                      │
│              │                          │                      │
│              │                          │                      │
├──────────────┴──────────────────────────┴──────────────────────┤
│                     Recording Controls                           │
│  [●] Audio  [●] Video  [📷] Whiteboard  [🖥️] Screen  [End]     │
└─────────────────────────────────────────────────────────────────┘
```

**Panel Specifications**:

**Left Panel - AI Chat (30% width)**:
- Scrollable conversation history
- AI interviewer messages with avatar
- Candidate text input box
- Clear visual distinction between roles
- Timestamp for each message
- Auto-scroll to latest message

**Center Panel - Whiteboard Canvas (45% width)**:
- streamlit-drawable-canvas component
- Drawing tools: pen, eraser, shapes, text
- Color picker for different components
- Undo/redo functionality
- Save snapshot button
- Clear canvas button
- Full-screen mode option
- Grid overlay (optional)

**Right Panel - Transcript (25% width)**:
- Real-time transcription display
- Auto-updating as speech is transcribed (within 2 seconds)
- Scrollable history
- Speaker labels (Interviewer/Candidate)
- Timestamps
- Search functionality
- Export transcript button

**Layout Constraints**:
- Panel proportions remain fixed throughout the session (30% / 45% / 25%)
- No dynamic resizing or collapsing panels
- Consistent layout provides predictable user experience
- Bottom bar spans full width below all panels

**Bottom Bar - Recording Controls**:
- Audio recording toggle (red dot when active)
- Video recording toggle (red dot when active)
- Whiteboard snapshot button
- Screen share toggle (visual indicator when active)
- End interview button (with confirmation)
- Session timer display
- Token usage indicator
- Visual indicators for active modes (distinct color/icon per mode)
  - Audio: Red pulsing dot
  - Video: Red recording icon
  - Screen share: Green active indicator
  - Whiteboard: Highlight when snapshot saved

### Streamlit Implementation

**Layout Code Structure**:
```python
import streamlit as st
from streamlit_drawable_canvas import st_canvas
from streamlit_webrtc import webrtc_streamer

def render_interview_interface(session_id: str):
    """Render the 3-panel interview interface."""
    
    # Header
    st.title("AI Mock Interview - System Design")
    col_timer, col_tokens = st.columns([3, 1])
    with col_timer:
        st.metric("Session Time", format_duration(session.duration))
    with col_tokens:
        st.metric("Tokens Used", f"{session.tokens:,}")
    
    # Main 3-panel layout
    col_left, col_center, col_right = st.columns([3, 4.5, 2.5])
    
    with col_left:
        render_ai_chat_panel(session_id)
    
    with col_center:
        render_whiteboard_panel(session_id)
    
    with col_right:
        render_transcript_panel(session_id)
    
    # Bottom controls
    render_recording_controls(session_id)

def render_ai_chat_panel(session_id: str):
    """Render AI interviewer chat interface."""
    st.subheader("AI Interviewer")
    
    # Chat history
    chat_container = st.container(height=500)
    with chat_container:
        for msg in get_conversation_history(session_id):
            with st.chat_message(msg.role):
                st.write(msg.content)
                st.caption(msg.timestamp.strftime("%H:%M:%S"))
    
    # Text input
    user_input = st.chat_input("Type your response...")
    if user_input:
        process_candidate_response(session_id, user_input)

def render_whiteboard_panel(session_id: str):
    """Render whiteboard canvas."""
    st.subheader("Whiteboard")
    
    # Canvas controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        drawing_mode = st.selectbox(
            "Tool",
            ["freedraw", "line", "rect", "circle", "transform"]
        )
    with col2:
        stroke_color = st.color_picker("Color", "#000000")
    with col3:
        stroke_width = st.slider("Width", 1, 25, 3)
    
    # Canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#ffffff",
        height=500,
        width=700,
        drawing_mode=drawing_mode,
        key=f"canvas_{session_id}",
    )
    
    # Canvas actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save Snapshot"):
            save_whiteboard_snapshot(session_id, canvas_result.image_data)
    with col2:
        if st.button("Clear Canvas"):
            clear_canvas(session_id)
    with col3:
        if st.button("Full Screen"):
            toggle_fullscreen()

def render_transcript_panel(session_id: str):
    """Render real-time transcript display."""
    st.subheader("Transcript")
    
    # Search box
    search_query = st.text_input("Search transcript", key="transcript_search")
    
    # Transcript display
    transcript_container = st.container(height=500)
    with transcript_container:
        transcript = get_transcript(session_id)
        for entry in transcript:
            if search_query and search_query.lower() not in entry.text.lower():
                continue
            st.markdown(f"**{entry.speaker}** ({entry.timestamp})")
            st.write(entry.text)
            st.divider()
    
    # Export button
    if st.button("Export Transcript"):
        export_transcript(session_id)

def render_recording_controls(session_id: str):
    """Render recording control buttons."""
    st.divider()
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        audio_active = st.toggle("🎤 Audio", value=False)
        if audio_active:
            webrtc_ctx = webrtc_streamer(
                key="audio",
                mode=WebRtcMode.SENDONLY,
                audio_receiver_size=1024,
                media_stream_constraints={"audio": True, "video": False},
            )
            if webrtc_ctx.audio_receiver:
                process_audio_stream(session_id, webrtc_ctx.audio_receiver)
    
    with col2:
        video_active = st.toggle("📹 Video", value=False)
        if video_active:
            webrtc_ctx = webrtc_streamer(
                key="video",
                mode=WebRtcMode.SENDONLY,
                media_stream_constraints={"audio": False, "video": True},
            )
    
    with col3:
        if st.button("📷 Snapshot"):
            save_whiteboard_snapshot(session_id)
    
    with col4:
        screen_share = st.toggle("🖥️ Screen", value=False)
        if screen_share:
            capture_screen(session_id)
    
    with col5:
        st.write("")  # Spacer
    
    with col6:
        if st.button("🛑 End Interview", type="primary"):
            if st.confirm("End interview and generate feedback?"):
                end_session(session_id)
```

### Resume Upload Interface

**Pre-Interview Setup**:
```python
def render_resume_upload():
    """Render resume upload and configuration interface."""
    st.title("Setup Your Mock Interview")
    
    # Resume upload
    st.subheader("1. Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or TXT)",
        type=["pdf", "txt"],
        help="We'll analyze your experience to generate relevant problems"
    )
    
    if uploaded_file:
        with st.spinner("Analyzing resume..."):
            resume_data = parse_resume(uploaded_file)
            st.success("Resume analyzed successfully!")
            
            # Display extracted info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Experience Level", resume_data.experience_level)
                st.metric("Years of Experience", resume_data.years_of_experience)
            with col2:
                st.write("**Domain Expertise:**")
                for domain in resume_data.domain_expertise:
                    st.badge(domain)
    
    # AI provider selection
    st.subheader("2. Select AI Provider")
    provider = st.selectbox(
        "Choose your AI provider",
        ["OpenAI GPT-4", "Anthropic Claude"]
    )
    
    # Communication modes
    st.subheader("3. Select Communication Modes")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        audio_enabled = st.checkbox("Audio", value=True)
    with col2:
        video_enabled = st.checkbox("Video", value=False)
    with col3:
        whiteboard_enabled = st.checkbox("Whiteboard", value=True)
    with col4:
        screen_enabled = st.checkbox("Screen Share", value=False)
    
    # Start button
    if st.button("Start Interview", type="primary", disabled=not uploaded_file):
        config = SessionConfig(
            enabled_modes=get_enabled_modes(audio_enabled, video_enabled, whiteboard_enabled, screen_enabled),
            ai_provider=provider,
            ai_model=get_model_for_provider(provider),
            resume_data=resume_data
        )
        session = create_session(config)
        st.switch_page("interview")
```

## Data Models

### Core Models

```python
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict

class CommunicationMode(Enum):
    AUDIO = "audio"
    VIDEO = "video"
    WHITEBOARD = "whiteboard"
    SCREEN_SHARE = "screen_share"
    TEXT = "text"

class SessionStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

@dataclass
class SessionConfig:
    enabled_modes: List[CommunicationMode]
    ai_provider: str  # "openai" or "anthropic"
    ai_model: str
    resume_data: Optional[ResumeData] = None
    duration_minutes: Optional[int] = None

@dataclass
class Session:
    id: str
    user_id: str
    created_at: datetime
    ended_at: Optional[datetime]
    status: SessionStatus
    config: SessionConfig

@dataclass
class ResumeData:
    user_id: str
    name: str
    email: str
    experience_level: str  # "junior", "mid", "senior", "staff"
    years_of_experience: int
    domain_expertise: List[str]
    work_experience: List[Dict]
    education: List[Dict]
    skills: List[str]
    raw_text: str

@dataclass
class Message:
    role: str  # "interviewer" or "candidate"
    content: str
    timestamp: datetime

@dataclass
class MediaFile:
    file_type: str
    file_path: str
    timestamp: datetime

@dataclass
class Feedback:
    category: str
    description: str
    evidence: List[str]

@dataclass
class ActionItem:
    step_number: int
    description: str
    resources: List[str]

@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    provider: str
    model: str

@dataclass
class LogEntry:
    timestamp: datetime
    level: str
    component: str
    operation: str
    message: str
    session_id: Optional[str]
    metadata: Dict
    stack_trace: Optional[str]
```

## Monitoring and Observability

### Metrics Collection

**System Metrics**:
- Session creation rate
- Active sessions count
- Session completion rate
- Average session duration
- Error rate by component
- API response times

**AI Metrics**:
- Token usage per session
- Token usage per operation
- Cost per session
- Average response time
- API error rate
- Model performance metrics

**Storage Metrics**:
- Database query performance
- File storage usage
- Media file sizes
- Database connection pool status

**Implementation**:
```python
class MetricsCollector:
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Dict[str, str]
    ) -> None
    
    def increment_counter(
        self,
        counter_name: str,
        tags: Dict[str, str]
    ) -> None
    
    def record_timing(
        self,
        operation: str,
        duration_ms: float,
        tags: Dict[str, str]
    ) -> None
    
    def get_metrics_summary(
        self,
        time_range: TimeRange
    ) -> MetricsSummary
```

### Health Checks

**Health Check Endpoints**:
```python
class HealthChecker:
    def check_database(self) -> HealthStatus
    def check_ai_providers(self) -> Dict[str, HealthStatus]
    def check_file_storage(self) -> HealthStatus
    def check_overall_health(self) -> SystemHealth

@dataclass
class HealthStatus:
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    last_check: datetime
    details: Dict
```

### Alerting

**Alert Conditions**:
- High error rate (> 5% of requests)
- Database connection failures
- AI API failures or rate limits
- Disk space low (< 10% free)
- High token usage (approaching budget limits)
- Long response times (> 10 seconds)

**Alert Channels**:
- Console warnings
- Log file entries
- Email notifications (future)
- Slack/Discord webhooks (future)

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Invalid API keys
   - Missing dependencies
   - Invalid session configuration

2. **Runtime Errors**
   - Audio/video capture failures
   - Transcription errors
   - LLM API failures
   - Database connection issues

3. **Data Errors**
   - Corrupted session data
   - Missing media files
   - Invalid evaluation data

### Error Handling Strategy

```python
class InterviewPlatformError(Exception):
    """Base exception for all platform errors"""
    pass

class ConfigurationError(InterviewPlatformError):
    """Raised when configuration is invalid"""
    pass

class CommunicationError(InterviewPlatformError):
    """Raised when communication mode fails"""
    pass

class AIProviderError(InterviewPlatformError):
    """Raised when AI provider encounters an error"""
    pass

class DataStoreError(InterviewPlatformError):
    """Raised when database operations fail"""
    pass
```

**Error Handling Principles**:
- Fail fast for configuration errors
- Graceful degradation for communication mode failures
- Retry logic for transient API failures
- Clear error messages displayed to users
- Comprehensive logging for debugging

**Retry Implementation**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class AIInterviewer:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((APIError, ConnectionError)),
        reraise=True
    )
    def _call_llm_api(self, prompt: str) -> str:
        """
        Call LLM API with automatic retry on transient failures.
        
        Retry strategy:
        - Maximum 3 attempts
        - Exponential backoff: 1s, 2s, 4s
        - Only retry on transient errors (API errors, connection issues)
        - Re-raise exception after final attempt
        """
        try:
            response = self.llm.generate(prompt)
            return response
        except Exception as e:
            logger.error(
                "llm_api_call_failed",
                error=str(e),
                retry_attempt=self._call_llm_api.retry.statistics.get("attempt_number", 0)
            )
            raise

class PostgresDataStore:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((OperationalError, InterfaceError)),
        reraise=True
    )
    def _execute_query(self, query: str, params: Dict) -> Any:
        """
        Execute database query with automatic retry on connection failures.
        """
        try:
            with self.pool.connection() as conn:
                result = conn.execute(query, params)
                return result
        except Exception as e:
            logger.error(
                "database_query_failed",
                query=query[:100],  # Truncate for logging
                error=str(e),
                retry_attempt=self._execute_query.retry.statistics.get("attempt_number", 0)
            )
            raise
```

## Testing Strategy

### Unit Tests

**Coverage Areas**:
- Session Manager: session lifecycle, state transitions
- Communication Manager: mode enabling/disabling, file storage
- AI Interviewer: question generation, context management
- Evaluation Manager: score calculation, feedback generation
- Data Store: CRUD operations, query logic
- File Storage: file operations, path management

**Testing Approach**:
- Mock external dependencies (LLM APIs, file system)
- Test edge cases and error conditions
- Verify interface contracts
- Aim for 80%+ code coverage

### Integration Tests

**Test Scenarios**:
1. Complete interview flow (start → interact → end → evaluate)
2. Multi-mode communication (audio + video + whiteboard)
3. Session persistence and retrieval
4. Error recovery scenarios
5. AI provider switching

**Testing Tools**:
- pytest for test framework
- pytest-mock for mocking
- pytest-cov for coverage reporting
- Factory pattern for test data generation

### End-to-End Tests

**Critical Workflows**:
1. New user starts first interview
2. User completes interview and views feedback
3. User reviews past interview sessions
4. User switches AI providers

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run linting
        run: |
          ruff check .
          black --check .
      - name: Run type checking
        run: mypy src/
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Quality Gates

**Pull Request Requirements**:
- All tests pass
- Code coverage ≥ 80%
- No linting errors
- Type checking passes
- Code formatted with Black
- At least one approval from code owner

### Code Quality Tools

- **Linting**: Ruff (fast Python linter)
- **Formatting**: Black (opinionated formatter)
- **Import Sorting**: isort (import organizer)
- **Type Checking**: mypy (static type checker)
- **Testing**: pytest (test framework)
- **Coverage**: pytest-cov (coverage plugin)
- **Pre-commit**: Automated checks before commits

### Pre-commit Configuration

**.pre-commit-config.yaml**:
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-json
      - id: check-toml
      - id: detect-private-key

  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.292
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict, --ignore-missing-imports]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [--tb=short, -v]
```

**Setup Pre-commit**:
```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run against all files
pre-commit run --all-files
```

## Documentation Standards

### Code Documentation

**Module Level**:
```python
"""
Module: session_manager.py

This module provides the SessionManager class which orchestrates interview
session lifecycle and coordinates between components.

Key responsibilities:
- Session creation and management
- State transitions
- Component coordination
- Database persistence
"""
```

**Class Level**:
```python
class SessionManager:
    """
    Manages interview session lifecycle and coordinates between components.
    
    The SessionManager is responsible for creating sessions, managing their
    state, and coordinating with the AI Interviewer and Evaluation Manager.
    
    Attributes:
        data_store: DataStore instance for persistence
        ai_interviewer: AIInterviewer instance for conducting interviews
        evaluation_manager: EvaluationManager for generating feedback
    """
```

**Function Level**:
```python
def create_session(self, config: SessionConfig) -> Session:
    """
    Create a new interview session with the specified configuration.
    
    Args:
        config: SessionConfig containing enabled modes and AI settings
        
    Returns:
        Session: The newly created session instance
        
    Raises:
        ConfigurationError: If the configuration is invalid
        DataStoreError: If session cannot be persisted
    """
```

### Architecture Decision Records (ADRs)

**Format**:
```markdown
# ADR-001: Use PostgreSQL in Docker for Local Data Storage

## Status
Accepted

## Context
Need local data persistence without cloud dependencies for POC, with a clear path to cloud migration.

## Decision
Use PostgreSQL running in Docker container as the database engine.

## Rationale
- PostgreSQL is production-grade and widely used in cloud environments
- Docker containerization provides easy local setup without manual installation
- Same database engine can be used in cloud (AWS RDS, Azure Database, Google Cloud SQL)
- Supports JSONB for flexible schema evolution
- Better concurrent access than SQLite
- Repository pattern abstraction enables seamless cloud migration

## Consequences
Positive:
- No code changes needed when migrating to cloud
- Production-quality database from day one
- Better performance and concurrency
- Rich feature set (JSONB, full-text search, etc.)
- Easy backup and restore with pg_dump

Negative:
- Requires Docker installation
- Slightly more complex setup than SQLite
- Additional container to manage

## Alternatives Considered
- SQLite: Too limited for future scaling, different engine than cloud
- MySQL: Less feature-rich than PostgreSQL for our use case
- MongoDB: Overkill for structured data, less mature cloud migration path
```

### README Structure

1. Project Overview
2. Features
3. Prerequisites
4. Installation
5. Configuration
6. Usage Examples
7. Architecture Overview
8. Development Setup
9. Testing
10. Contributing Guidelines
11. License

## Dependency Management

### Core Dependencies

```
# UI and Framework
streamlit>=1.28.0
streamlit-drawable-canvas>=0.9.0
streamlit-webrtc>=0.47.0  # Real-time audio/video

# AI and LLM
openai>=1.0.0
anthropic>=0.7.0
langchain>=0.1.0
tiktoken>=0.5.0  # Token counting

# Database
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0
alembic>=1.12.0

# Media Processing
opencv-python>=4.8.0
pillow>=10.0.0
pydub>=0.25.0  # Audio processing
whisper>=1.0.0  # OpenAI Whisper for transcription
pyaudio>=0.2.13  # Audio I/O
av>=10.0.0  # Audio/video processing for webrtc

# Resume Parsing
pypdf2>=3.0.0  # PDF parsing
pdfplumber>=0.10.0  # Alternative PDF parser

# Utilities
python-dotenv>=1.0.0  # Environment variables
pydantic>=2.0.0  # Data validation
structlog>=23.1.0  # Structured logging
tenacity>=8.2.0  # Retry logic

# Monitoring
prometheus-client>=0.17.0  # Metrics (optional)
```

### Development Dependencies

```
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0
pytest-asyncio>=0.21.0
factory-boy>=3.3.0  # Test data factories

# Code Quality
black>=23.9.0
ruff>=0.0.292
mypy>=1.5.0
isort>=5.12.0
pre-commit>=3.4.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.4.0
```

### Dependency Principles

- Pin major versions, allow minor/patch updates
- Regular security updates
- Minimize dependency count
- Prefer well-maintained packages
- Document why each dependency is needed

## Deployment Considerations

### Local Setup

1. Clone repository
2. Start PostgreSQL with Docker Compose: `docker-compose up -d`
3. Create virtual environment: `python -m venv venv`
4. Activate virtual environment
5. Install dependencies: `pip install -r requirements.txt`
6. Configure API keys in `.env` file
7. Run database migrations: `alembic upgrade head`
8. Run Streamlit app: `streamlit run src/main.py`

### Configuration Management

**Environment Variables** (.env file):
```
# AI Provider Keys
OPENAI_API_KEY=<key>
ANTHROPIC_API_KEY=<key>

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=interview_platform
DB_USER=interview_user
DB_PASSWORD=<secure_password>
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Storage
DATA_DIR=./data

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json  # or 'text'
LOG_TO_FILE=true
LOG_TO_DB=true
LOG_FILE_PATH=./logs/app.log
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Token Budget (optional)
MAX_TOKENS_PER_SESSION=50000
TOKEN_BUDGET_WARNING_THRESHOLD=0.8
```

**Config File** (config.yaml):
```yaml
ai:
  default_provider: openai
  default_model: gpt-4
  timeout_seconds: 30
  max_retries: 3
  retry_delay_seconds: 1
  
  # Token pricing (USD per 1K tokens)
  pricing:
    openai:
      gpt-4:
        input: 0.03
        output: 0.06
      gpt-4-turbo:
        input: 0.01
        output: 0.03
    anthropic:
      claude-3-opus:
        input: 0.015
        output: 0.075
      claude-3-sonnet:
        input: 0.003
        output: 0.015
  
storage:
  data_directory: ./data
  max_session_size_mb: 500
  cleanup_old_sessions_days: 90
  
communication:
  audio_sample_rate: 16000
  audio_max_size_mb: 100
  video_fps: 30
  video_max_size_mb: 500
  video_codec: h264
  whiteboard_resolution: [1920, 1080]
  screen_capture_interval_seconds: 5

database:
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600
  echo: false  # Set to true for SQL debugging

logging:
  version: 1
  formatters:
    json:
      format: '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "component": "%(name)s", "message": "%(message)s"}'
    text:
      format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  handlers:
    console:
      class: logging.StreamHandler
      level: INFO
      formatter: text
    file:
      class: logging.handlers.RotatingFileHandler
      level: DEBUG
      formatter: json
      filename: ./logs/app.log
      maxBytes: 10485760
      backupCount: 5
    database:
      class: custom_handlers.DatabaseLogHandler
      level: WARNING
  loggers:
    root:
      level: INFO
      handlers: [console, file, database]
    sqlalchemy:
      level: WARNING
    openai:
      level: INFO
    anthropic:
      level: INFO

monitoring:
  health_check_interval_seconds: 30
  metrics_collection_enabled: true
  alert_on_error_rate: 0.05  # 5%
  alert_on_response_time_ms: 10000  # 10 seconds
```

## Production-Quality Requirements

### Code Quality Standards

**Code Organization**:
- Follow PEP 8 style guide
- Maximum function length: 50 lines
- Maximum class length: 200 lines
- Maximum file length: 300 lines
- Clear separation of concerns
- Single Responsibility Principle
- Cyclomatic complexity below 10 per function

**Type Hints**:
- All function signatures must have type hints
- Use `mypy` in strict mode
- No `Any` types without justification

**Error Handling**:
- Never use bare `except` clauses
- Always log exceptions with context
- Provide meaningful error messages
- Include recovery suggestions

**Documentation**:
- All public APIs documented
- Complex algorithms explained
- Examples for non-obvious usage
- Keep documentation in sync with code

### Performance Requirements

**Response Times**:
- UI interactions: < 100ms
- Audio transcription: < 2 seconds (per audio input)
- AI response display: < 1 second (after generation)
- AI response processing: < 500ms (sending to AI Interviewer)
- Whiteboard snapshot save: < 1 second
- Transcript display update: < 2 seconds
- Database queries: < 100ms
- File operations: < 500ms

**Resource Limits**:
- Maximum session size: 500MB
- Maximum video length: 2 hours
- Maximum concurrent sessions: 10
- Database connection pool: 5-20 connections

**Optimization Strategies**:
- Lazy loading for media files
- Database query optimization with EXPLAIN
- Connection pooling
- Caching for frequently accessed data
- Async operations where appropriate

### Reliability Requirements

**Data Integrity**:
- Database transactions for multi-step operations
- Atomic file operations
- Backup and recovery procedures
- Data validation at boundaries

**Fault Tolerance**:
- Retry logic for transient failures (maximum 3 attempts with exponential backoff)
  - First retry: 1 second delay
  - Second retry: 2 seconds delay
  - Third retry: 4 seconds delay
  - Applied to: AI API calls, database operations, file operations
- Circuit breaker for external APIs
- Graceful degradation when services unavailable
- Auto-recovery from connection failures
- Clear error messages for non-recoverable failures

**Availability**:
- Database health checks every 30 seconds
- Automatic reconnection on connection loss
- Session state recovery after crashes
- Clear error messages for user actions

### Maintainability Requirements

**Code Cleanliness**:
- Remove dead code immediately
- No commented-out code in commits
- No TODO comments without tickets
- Regular dependency updates

**Refactoring**:
- Continuous refactoring as part of development
- Extract common patterns into utilities
- Simplify complex logic
- Remove duplication

**Testing**:
- Tests written before or with code
- Tests as documentation
- Fast test execution (< 30 seconds for unit tests)
- Isolated tests (no shared state)

### Logging Best Practices

**What to Log**:
- All errors and exceptions with full context
- API calls (request/response/duration)
- State transitions
- Performance metrics
- Security events
- User actions

**What NOT to Log**:
- Sensitive data (API keys, passwords)
- Personal information (unless anonymized)
- Large payloads (truncate to reasonable size)
- Redundant information

**Log Levels Usage**:
- **DEBUG**: Detailed flow information for debugging
- **INFO**: Important business events
- **WARNING**: Unexpected but handled situations
- **ERROR**: Errors that need attention
- **CRITICAL**: System-threatening issues

**Structured Logging Example**:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "session_created",
    session_id=session.id,
    enabled_modes=session.config.enabled_modes,
    ai_provider=session.config.ai_provider
)

logger.error(
    "ai_api_call_failed",
    session_id=session_id,
    provider=provider,
    error=str(error),
    retry_count=retry_count,
    exc_info=True
)
```

## Security Considerations

1. **API Key Management**
   - Store in environment variables or secure vault
   - Never commit to version control
   - Validate before use
   - Rotate keys regularly
   - Use separate keys for dev/prod

2. **Data Privacy**
   - All data stored locally
   - No external transmission except to AI APIs
   - Clear data retention policies
   - Secure deletion of sensitive data
   - Encryption at rest (future consideration)

3. **Input Validation**
   - Sanitize all user inputs before processing
   - Validate file uploads (type, size, content)
   - Limit file sizes (audio: 100MB, video: 500MB)
   - SQL injection prevention (parameterized queries for all database operations)
   - Path traversal prevention
   - Validate session configuration before starting interview
   - Validate API credentials before use
   - Input validation at system boundaries before processing

4. **Rate Limiting**
   - Limit API calls to prevent abuse
   - Implement backoff strategies
   - Monitor for unusual patterns
   - Budget controls for AI API usage

## Performance Considerations

1. **Media Processing**
   - Compress video recordings
   - Optimize whiteboard image storage
   - Stream audio instead of loading entirely

2. **Database Queries**
   - Index frequently queried fields
   - Limit result sets
   - Use pagination for session lists

3. **LLM API Calls**
   - Implement request caching
   - Use streaming responses
   - Handle rate limits gracefully

## Operational Procedures

### Startup Checklist

1. **Environment Validation**
   - Verify all required environment variables are set
   - Validate API keys with test calls
   - Check database connectivity
   - Verify file storage permissions

2. **Database Initialization**
   - Run health check on PostgreSQL
   - Apply pending migrations: `alembic upgrade head`
   - Verify schema integrity
   - Check connection pool status

3. **Service Startup**
   - Start Docker containers: `docker-compose up -d`
   - Wait for database health check to pass
   - Initialize logging system
   - Start metrics collection
   - Launch Streamlit app

### Monitoring Procedures

**Daily Checks**:
- Review error logs for critical issues
- Check token usage and costs
- Verify database performance
- Monitor disk space usage

**Weekly Checks**:
- Review session completion rates
- Analyze performance trends
- Check for dependency updates
- Review and archive old logs

**Monthly Checks**:
- Database maintenance (VACUUM, ANALYZE)
- Review and optimize slow queries
- Update dependencies
- Review and update documentation

### Troubleshooting Guide

**Database Connection Issues**:
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
docker logs interview_platform_db

# Test connection
psql -h localhost -U interview_user -d interview_platform

# Restart database
docker-compose restart postgres
```

**AI API Failures**:
1. Check API key validity
2. Verify network connectivity
3. Check rate limits
4. Review error logs for specific error codes
5. Implement fallback to alternative provider

**High Token Usage**:
1. Review token usage breakdown by operation
2. Check for inefficient prompts
3. Verify conversation history truncation
4. Consider using cheaper models for non-critical operations

**Performance Issues**:
1. Check database query performance with EXPLAIN
2. Review slow query logs
3. Monitor connection pool usage
4. Check file system I/O
5. Profile Python code with cProfile

### Backup and Recovery

**Backup Strategy**:
```bash
# Database backup
docker exec interview_platform_db pg_dump -U interview_user interview_platform > backup_$(date +%Y%m%d).sql

# File storage backup
tar -czf sessions_backup_$(date +%Y%m%d).tar.gz data/sessions/

# Automated daily backups
0 2 * * * /path/to/backup_script.sh
```

**Recovery Procedure**:
```bash
# Restore database
docker exec -i interview_platform_db psql -U interview_user interview_platform < backup_20241110.sql

# Restore file storage
tar -xzf sessions_backup_20241110.tar.gz -C data/
```

### Maintenance Tasks

**Database Maintenance**:
```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex
REINDEX DATABASE interview_platform;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Log Rotation**:
- Automatic rotation configured in logging config
- Manual cleanup: `find ./logs -name "*.log.*" -mtime +30 -delete`

**Session Cleanup**:
```python
# Remove sessions older than 90 days
def cleanup_old_sessions(days: int = 90):
    cutoff_date = datetime.now() - timedelta(days=days)
    old_sessions = db.query(Session).filter(
        Session.created_at < cutoff_date
    ).all()
    
    for session in old_sessions:
        # Delete media files
        file_storage.cleanup_session(session.id)
        # Delete database records (cascade)
        db.delete(session)
    
    db.commit()
```

## Cloud Migration Strategy

### Database Migration Path

The repository pattern abstraction enables seamless migration from local PostgreSQL to cloud databases:

**Step 1: Local Development (Current)**
- PostgreSQL in Docker container
- Local file storage
- Connection via localhost

**Step 2: Cloud Database Migration**
- Update `DATABASE_URL` to point to cloud database (AWS RDS, Azure Database, etc.)
- No code changes required - same `IDataStore` interface
- Optional: Implement `CloudDataStore` class for cloud-specific optimizations

**Step 3: Cloud Storage Migration (Optional)**
- Implement cloud storage adapter (S3, Azure Blob, etc.)
- Update `FileStorage` to use cloud storage
- Maintain same interface for backward compatibility

### Supported Cloud Providers

**AWS**:
- Database: Amazon RDS for PostgreSQL
- Storage: Amazon S3
- Configuration: Update `DATABASE_URL` and storage backend

**Azure**:
- Database: Azure Database for PostgreSQL
- Storage: Azure Blob Storage
- Configuration: Update connection strings

**Google Cloud**:
- Database: Cloud SQL for PostgreSQL
- Storage: Google Cloud Storage
- Configuration: Update connection strings

### Migration Checklist

1. Export data from local PostgreSQL
2. Create cloud database instance
3. Import data to cloud database
4. Update environment variables
5. Test connection
6. Update file storage configuration (if migrating storage)
7. Deploy application

## Future Extensibility

### Potential Extensions

1. **Additional Interview Types**
   - Coding interviews
   - Behavioral interviews
   - Technical deep-dives

2. **Enhanced Analytics**
   - Progress tracking over time
   - Competency trend analysis
   - Comparative benchmarking

3. **Collaboration Features**
   - Share sessions with mentors
   - Peer review functionality
   - Group practice sessions

4. **Cloud Deployment**
   - Multi-user support
   - Cloud storage integration
   - Real-time collaboration

### Extension Points

- **AI Provider Interface**: Easy to add new LLM providers
- **Communication Mode Interface**: Pluggable communication modes
- **Evaluation Strategy**: Customizable evaluation algorithms
- **Storage Backend**: Swappable storage implementations


## Complete Local Setup Guide

### Prerequisites

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: For cloning the repository
- **API Keys**: OpenAI API key (required), Anthropic API key (optional)

### Quick Start (Recommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd ai-mock-interview-platform

# 2. Create .env file from template
cp .env.template .env

# 3. Edit .env file and add your API keys
# Required: DB_PASSWORD, OPENAI_API_KEY
# Optional: ANTHROPIC_API_KEY
nano .env  # or use your preferred editor

# 4. Make startup script executable
chmod +x startup.sh

# 5. Run startup script
./startup.sh

# 6. Access the application
# Open browser to http://localhost:8501
```

### Manual Setup (Development)

For development without Docker for the application:

```bash
# 1. Start only PostgreSQL with Docker
docker-compose up -d postgres

# 2. Wait for PostgreSQL to be ready
until docker exec interview_platform_db pg_isready -U interview_user; do
    sleep 1
done

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development tools

# 5. Configure environment
cp .env.template .env
# Edit .env with your API keys and configuration

# 6. Create necessary directories
mkdir -p data/sessions logs

# 7. Run Streamlit app locally
streamlit run src/main.py --server.port=8501
```

### Verification Steps

```bash
# Check Docker services status
docker-compose ps

# Expected output:
# NAME                        STATUS              PORTS
# interview_platform_db       Up (healthy)        0.0.0.0:5432->5432/tcp
# interview_platform_app      Up                  0.0.0.0:8501->8501/tcp

# Check PostgreSQL connection
docker exec interview_platform_db psql -U interview_user -d interview_platform -c "SELECT version();"

# List database tables
docker exec interview_platform_db psql -U interview_user -d interview_platform -c "\dt"

# Check application logs
docker-compose logs -f app

# Check database logs
docker-compose logs -f postgres

# Test API keys (from Python)
python -c "
from openai import OpenAI
client = OpenAI()
print('OpenAI API key is valid!')
"
```

### Troubleshooting

**Issue: PostgreSQL container won't start**
```bash
# Check if port 5432 is already in use
lsof -i :5432  # On Linux/Mac
netstat -ano | findstr :5432  # On Windows

# If port is in use, either:
# 1. Stop the conflicting service
# 2. Change the port in docker-compose.yml
```

**Issue: Application can't connect to database**
```bash
# Verify DATABASE_URL in .env
echo $DATABASE_URL

# Test connection manually
docker exec interview_platform_db psql -U interview_user -d interview_platform -c "SELECT 1;"

# Check network connectivity
docker network inspect interview_network
```

**Issue: API key errors**
```bash
# Verify API keys are set
echo $OPENAI_API_KEY | head -c 10

# Test API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Issue: Streamlit won't start**
```bash
# Check if port 8501 is available
lsof -i :8501  # On Linux/Mac

# Check application logs
docker-compose logs app

# Restart application container
docker-compose restart app
```

### Stopping and Cleaning Up

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove only application container (keeps database)
docker-compose stop app
docker-compose rm -f app

# View disk usage
docker system df
```

### Development Workflow

**Running Tests**:
```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test file
pytest tests/test_session_manager.py

# Run tests matching pattern
pytest -k "test_audio"
```

**Code Quality Checks**:
```bash
# Run linting
ruff check src/

# Run formatting check
black --check src/

# Run type checking
mypy src/

# Run all pre-commit hooks
pre-commit run --all-files
```

**Database Migrations** (if using Alembic):
```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Production Deployment Considerations

**Environment Variables**:
- Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)
- Never commit .env file to version control
- Rotate API keys regularly
- Use different keys for dev/staging/prod

**Database**:
- Use managed PostgreSQL service (AWS RDS, Azure Database, etc.)
- Enable automated backups
- Set up read replicas for scaling
- Monitor query performance

**Application**:
- Use container orchestration (Kubernetes, ECS, etc.)
- Implement health checks
- Set up auto-scaling
- Configure logging aggregation
- Enable monitoring and alerting

**Security**:
- Use HTTPS/TLS for all connections
- Implement rate limiting
- Enable database encryption at rest
- Use VPC/private networks
- Regular security audits

### Monitoring and Maintenance

**Daily Tasks**:
- Check error logs: `docker-compose logs --tail=100 app | grep ERROR`
- Monitor token usage: Check database token_usage table
- Verify disk space: `df -h`

**Weekly Tasks**:
- Review session completion rates
- Analyze performance metrics
- Check for dependency updates: `pip list --outdated`
- Review and archive old logs

**Monthly Tasks**:
- Database maintenance: `VACUUM ANALYZE;`
- Update dependencies
- Review and optimize slow queries
- Backup verification

### Backup and Recovery

**Automated Backup Script** (backup.sh):
```bash
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec interview_platform_db pg_dump -U interview_user interview_platform | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Backup session files
tar -czf $BACKUP_DIR/sessions_backup_$DATE.tar.gz data/sessions/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

**Recovery**:
```bash
# Restore database
gunzip -c backups/db_backup_20241110_120000.sql.gz | \
  docker exec -i interview_platform_db psql -U interview_user interview_platform

# Restore session files
tar -xzf backups/sessions_backup_20241110_120000.tar.gz
```

### Performance Optimization

**Database Optimization**:
```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM sessions WHERE status = 'active';

-- Create additional indexes if needed
CREATE INDEX idx_sessions_user_status ON sessions(user_id, status);

-- Vacuum and analyze
VACUUM ANALYZE sessions;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Application Optimization**:
- Use Streamlit caching: `@st.cache_data` and `@st.cache_resource`
- Implement lazy loading for media files
- Optimize database queries with proper indexes
- Use connection pooling
- Compress large media files

### Scaling Considerations

**Vertical Scaling**:
- Increase Docker container resources
- Upgrade database instance size
- Add more CPU/memory to host machine

**Horizontal Scaling**:
- Use load balancer for multiple app instances
- Implement session affinity
- Use shared storage (S3, NFS) for media files
- Database read replicas for read-heavy workloads

**Cost Optimization**:
- Monitor token usage and set budgets
- Use cheaper LLM models for non-critical operations
- Implement caching for repeated queries
- Compress and archive old sessions
- Use spot instances for non-production environments
