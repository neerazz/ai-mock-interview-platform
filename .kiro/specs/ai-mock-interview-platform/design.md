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


## Documentation Architecture (Requirements 20-21)

### End-User Documentation (Requirement 20)

**Quick Start Guide for Non-Technical Users**

The Quick Start Guide is designed for users with no technical background, providing step-by-step instructions with screenshots and plain language.

**Location**: `docs/user-guide/quick-start.md`

**Structure**:
1. **Welcome** - Brief introduction (2-3 sentences)
2. **What You'll Need** - Simple checklist with download links
3. **Installation Steps** - Numbered steps with screenshots
4. **First Interview** - Walkthrough with images
5. **Troubleshooting** - Common issues with solutions
6. **Getting Help** - Support resources

**Key Features**:
- No technical jargon (avoid terms like "Docker", "PostgreSQL", "API")
- Use simple language ("download", "install", "click", "type")
- Screenshots for every step
- Estimated time for each step
- Success indicators ("You should see...")
- Clear error messages with fixes

**Example Content Structure**:
```markdown
# Quick Start Guide

Welcome! This guide will help you start practicing interviews in about 10 minutes.

## What You'll Need

Before starting, download these free programs:
- [ ] Docker Desktop - [Download here](link) (5 minutes to install)
- [ ] Your OpenAI API key - [Get one here](link) (2 minutes to create)

## Step 1: Download the Interview Platform (2 minutes)

1. Click this link: [Download Interview Platform](link)
2. Save the file to your Downloads folder
3. Double-click the downloaded file to extract it
4. You should see a folder called "ai-mock-interview-platform"

[Screenshot showing the folder]

## Step 2: Install Docker Desktop (5 minutes)

1. Open the Docker Desktop installer you downloaded
2. Click "Next" through the installation wizard
3. Wait for installation to complete (about 3 minutes)
4. Click "Finish" and restart your computer if prompted

[Screenshot of Docker Desktop running]

✅ Success: You should see a whale icon in your taskbar

## Step 3: Get Your API Key (2 minutes)

...
```


**Startup Validation Script**

A user-friendly script that checks all prerequisites and provides clear feedback:

**Location**: `scripts/validate_setup.py`

```python
"""
Startup validation script for non-technical users.
Checks all dependencies and provides clear, actionable feedback.
"""

import sys
import subprocess
from typing import List, Tuple

class ValidationResult:
    def __init__(self, name: str, passed: bool, message: str, fix: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
        self.fix = fix

def check_docker() -> ValidationResult:
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return ValidationResult(
                "Docker Installation",
                True,
                f"✅ Docker is installed: {result.stdout.strip()}"
            )
    except Exception:
        pass
    
    return ValidationResult(
        "Docker Installation",
        False,
        "❌ Docker is not installed or not running",
        "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    )

def check_env_file() -> ValidationResult:
    """Check if .env file exists and has required variables."""
    import os
    from pathlib import Path
    
    env_path = Path(".env")
    if not env_path.exists():
        return ValidationResult(
            "Configuration File",
            False,
            "❌ Configuration file (.env) not found",
            "Run: cp .env.template .env\nThen edit .env and add your API keys"
        )
    
    # Check for required variables
    with open(env_path) as f:
        content = f.read()
    
    required = ["DB_PASSWORD", "OPENAI_API_KEY"]
    missing = [var for var in required if f"{var}=" not in content or f"{var}=your_" in content]
    
    if missing:
        return ValidationResult(
            "Configuration File",
            False,
            f"❌ Missing or incomplete configuration: {', '.join(missing)}",
            f"Edit .env file and set: {', '.join(missing)}"
        )
    
    return ValidationResult(
        "Configuration File",
        True,
        "✅ Configuration file is complete"
    )

def print_results(results: List[ValidationResult]):
    """Print validation results in a user-friendly format."""
    print("\n" + "="*60)
    print("  SETUP VALIDATION RESULTS")
    print("="*60 + "\n")
    
    all_passed = True
    for result in results:
        print(f"{result.message}")
        if not result.passed:
            all_passed = False
            if result.fix:
                print(f"   How to fix: {result.fix}")
        print()
    
    print("="*60)
    if all_passed:
        print("✅ All checks passed! You're ready to start.")
        print("\nNext step: Run ./startup.sh to start the platform")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nNeed help? Check docs/user-guide/troubleshooting.md")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == "__main__":
    results = [
        check_docker(),
        check_env_file(),
        # Add more checks as needed
    ]
    
    success = print_results(results)
    sys.exit(0 if success else 1)
```


### Developer Documentation (Requirement 21)

**Developer Setup Guide**

Comprehensive guide for new developers to get started without pain points.

**Location**: `docs/developer-guide/setup.md`

**Structure**:
1. **Prerequisites** - Exact versions required
2. **Environment Setup** - Step-by-step with validation
3. **IDE Configuration** - Recommended settings and extensions
4. **Running Locally** - Development workflow
5. **Debugging** - Breakpoint setup and troubleshooting
6. **Architecture Overview** - High-level component diagram
7. **Common Workflows** - Feature development, bug fixing
8. **Testing** - Running and writing tests

**Automated Setup Script**

**Location**: `scripts/dev_setup.sh`

```bash
#!/bin/bash
# Automated development environment setup

set -e

echo "🚀 Setting up development environment..."

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ required. Found: $python_version"
    exit 1
fi
echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/sessions logs config

# Copy environment template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.template .env
    echo "⚠️  Please edit .env and add your API keys"
fi

# Start PostgreSQL
echo "🐘 Starting PostgreSQL..."
docker-compose up -d postgres

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until docker exec interview_platform_db pg_isready -U interview_user 2>/dev/null; do
    sleep 1
done
echo "✅ PostgreSQL is ready"

# Run validation
echo "🔍 Validating setup..."
python scripts/validate_dev_setup.py

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run: source venv/bin/activate"
echo "  3. Run: streamlit run src/main.py"
echo ""
```


**Development Environment Validation Script**

**Location**: `scripts/validate_dev_setup.py`

```python
"""
Validates development environment configuration.
Checks all tools, dependencies, and configurations needed for development.
"""

import sys
import subprocess
from pathlib import Path
from typing import List

def check_python_version() -> bool:
    """Check Python version is 3.10+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
    return False

def check_docker() -> bool:
    """Check Docker is installed and running"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker is running")
            return True
    except Exception:
        pass
    print("❌ Docker is not running")
    return False

def check_virtual_env() -> bool:
    """Check if running in virtual environment"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment activated")
        return True
    print("⚠️  Not in virtual environment (recommended)")
    return True  # Warning, not error

def check_dependencies() -> bool:
    """Check required packages are installed"""
    required = ["streamlit", "openai", "anthropic", "psycopg2", "pytest"]
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if not missing:
        print(f"✅ All required packages installed")
        return True
    print(f"❌ Missing packages: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")
    return False

def check_pre_commit() -> bool:
    """Check pre-commit hooks are installed"""
    git_hooks = Path(".git/hooks/pre-commit")
    if git_hooks.exists():
        print("✅ Pre-commit hooks installed")
        return True
    print("⚠️  Pre-commit hooks not installed")
    print("   Run: pre-commit install")
    return True  # Warning, not error

def check_database() -> bool:
    """Check PostgreSQL is accessible"""
    try:
        result = subprocess.run(
            ["docker", "exec", "interview_platform_db", "pg_isready", "-U", "interview_user"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ PostgreSQL is accessible")
            return True
    except Exception:
        pass
    print("❌ PostgreSQL is not accessible")
    print("   Run: docker-compose up -d postgres")
    return False

def main():
    print("\n" + "="*60)
    print("  DEVELOPMENT ENVIRONMENT VALIDATION")
    print("="*60 + "\n")
    
    checks = [
        check_python_version(),
        check_docker(),
        check_virtual_env(),
        check_dependencies(),
        check_pre_commit(),
        check_database(),
    ]
    
    print("\n" + "="*60)
    if all(checks):
        print("✅ Development environment is ready!")
    else:
        print("❌ Some checks failed. Fix issues above.")
    print("="*60 + "\n")
    
    return 0 if all(checks) else 1

if __name__ == "__main__":
    sys.exit(main())
```


## Project Structure Organization (Requirement 22)

### Directory Structure

Clean, organized structure with clear separation of concerns:

```
ai-mock-interview-platform/
├── README.md                          # Project overview and quick links
├── LICENSE                            # License file
├── .gitignore                         # Git ignore rules
├── .env.template                      # Environment variable template
├── docker-compose.yml                 # Docker services configuration
├── requirements.txt                   # Production dependencies
├── requirements-dev.txt               # Development dependencies
├── pyproject.toml                     # Python project configuration
├── .pre-commit-config.yaml           # Pre-commit hooks configuration
│
├── src/                              # Source code (all application code)
│   ├── __init__.py
│   ├── main.py                       # Streamlit entry point
│   ├── config.py                     # Configuration management
│   │
│   ├── core/                         # Core business logic
│   │   ├── __init__.py
│   │   ├── session_manager.py
│   │   ├── ai_interviewer.py
│   │   ├── evaluation_manager.py
│   │   └── resume_manager.py
│   │
│   ├── communication/                # Communication modes
│   │   ├── __init__.py
│   │   ├── communication_manager.py
│   │   ├── audio_handler.py
│   │   ├── video_handler.py
│   │   ├── whiteboard_handler.py
│   │   └── screen_share_handler.py
│   │
│   ├── storage/                      # Data persistence
│   │   ├── __init__.py
│   │   ├── data_store.py            # Abstract interface
│   │   ├── postgres_store.py        # PostgreSQL implementation
│   │   └── file_storage.py          # File system storage
│   │
│   ├── monitoring/                   # Logging and metrics
│   │   ├── __init__.py
│   │   ├── logging_manager.py
│   │   ├── token_tracker.py
│   │   └── metrics_collector.py
│   │
│   ├── ui/                           # UI components
│   │   ├── __init__.py
│   │   ├── interview_interface.py
│   │   ├── resume_upload.py
│   │   ├── session_history.py
│   │   └── evaluation_display.py
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── validators.py
│       ├── formatters.py
│       └── exceptions.py
│
├── tests/                            # All test files
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration and fixtures
│   │
│   ├── unit/                         # Unit tests (mirror src structure)
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── test_session_manager.py
│   │   │   ├── test_ai_interviewer.py
│   │   │   └── test_evaluation_manager.py
│   │   ├── communication/
│   │   │   └── test_communication_manager.py
│   │   └── storage/
│   │       └── test_postgres_store.py
│   │
│   ├── integration/                  # Integration tests
│   │   ├── __init__.py
│   │   ├── test_interview_workflow.py
│   │   ├── test_database_integration.py
│   │   └── test_ai_provider_integration.py
│   │
│   └── e2e/                          # End-to-end tests
│       ├── __init__.py
│       └── test_complete_interview.py
│
├── docs/                             # All documentation
│   ├── index.md                      # Documentation homepage
│   │
│   ├── user-guide/                   # End-user documentation
│   │   ├── quick-start.md
│   │   ├── using-the-platform.md
│   │   ├── troubleshooting.md
│   │   └── faq.md
│   │
│   ├── developer-guide/              # Developer documentation
│   │   ├── setup.md
│   │   ├── architecture.md
│   │   ├── contributing.md
│   │   ├── code-standards.md
│   │   ├── testing-guide.md
│   │   └── debugging.md
│   │
│   ├── api/                          # API documentation
│   │   ├── session-manager.md
│   │   ├── ai-interviewer.md
│   │   └── data-store.md
│   │
│   ├── adr/                          # Architecture Decision Records
│   │   ├── 001-postgresql-docker.md
│   │   ├── 002-streamlit-ui.md
│   │   └── 003-langchain-integration.md
│   │
│   └── implementation-notes/         # Implementation details
│       ├── resume-parsing.md
│       ├── token-tracking.md
│       └── error-handling.md
│
├── scripts/                          # Utility scripts
│   ├── startup.sh                    # Application startup
│   ├── dev_setup.sh                  # Development setup
│   ├── validate_setup.py             # Setup validation
│   ├── validate_dev_setup.py         # Dev environment validation
│   ├── backup.sh                     # Backup script
│   └── cleanup.sh                    # Cleanup old sessions
│
├── config/                           # Configuration files
│   ├── config.yaml                   # Application configuration
│   ├── logging.yaml                  # Logging configuration
│   └── docker/
│       └── init.sql                  # Database initialization
│
├── data/                             # Runtime data (gitignored)
│   └── sessions/                     # Session media files
│       └── {session_id}/
│           ├── audio/
│           ├── video/
│           ├── whiteboard/
│           └── screen/
│
└── logs/                             # Application logs (gitignored)
    └── app.log
```

**Key Principles**:
1. **Maximum 10 files in project root** - Only essential files
2. **Clear module separation** - Each directory has single responsibility
3. **Test structure mirrors source** - Easy to find corresponding tests
4. **Documentation organized by audience** - User vs developer docs separated
5. **No scattered files** - Everything has a designated place


### Structure Enforcement

**Linting Rules** (pyproject.toml):

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "PTH", # flake8-use-pathlib
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__.py
"tests/*" = ["S101"]      # Allow assert in tests

[tool.ruff.lint.isort]
known-first-party = ["src"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

# Enforce file organization
[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"  # Require absolute imports

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --strict-markers --cov=src --cov-report=term-missing"

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
files = ["src"]

[tool.black]
line-length = 100
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
```

**STRUCTURE.md Documentation**:

**Location**: `docs/STRUCTURE.md`

```markdown
# Project Structure

This document describes the organization of the codebase.

## Directory Overview

### `/src` - Source Code
All application code lives here. Organized by functional area.

- **core/**: Business logic (session management, AI interviewer, evaluation)
- **communication/**: Input/output modes (audio, video, whiteboard, screen)
- **storage/**: Data persistence (database, file storage)
- **monitoring/**: Logging, metrics, token tracking
- **ui/**: Streamlit UI components
- **utils/**: Shared utilities and helpers

### `/tests` - Test Code
All tests organized to mirror source structure.

- **unit/**: Fast, isolated tests for individual components
- **integration/**: Tests for component interactions
- **e2e/**: End-to-end workflow tests

### `/docs` - Documentation
All documentation organized by audience.

- **user-guide/**: For end users (non-technical)
- **developer-guide/**: For contributors (technical)
- **api/**: API reference documentation
- **adr/**: Architecture Decision Records
- **implementation-notes/**: Detailed implementation docs

### `/scripts` - Utility Scripts
Automation and maintenance scripts.

- Setup scripts (startup.sh, dev_setup.sh)
- Validation scripts (validate_setup.py)
- Maintenance scripts (backup.sh, cleanup.sh)

### `/config` - Configuration
Configuration files separate from code.

- Application config (config.yaml)
- Logging config (logging.yaml)
- Docker initialization (docker/init.sql)

### `/data` - Runtime Data
Generated at runtime, not in version control.

- Session media files organized by session ID
- Subdirectories for each media type

### `/logs` - Application Logs
Log files, not in version control.

## File Naming Conventions

- Python modules: `snake_case.py`
- Test files: `test_<module_name>.py`
- Documentation: `kebab-case.md`
- Scripts: `snake_case.sh` or `snake_case.py`
- Config files: `kebab-case.yaml`

## Import Guidelines

Always use absolute imports from `src`:

```python
# Good
from src.core.session_manager import SessionManager
from src.storage.data_store import IDataStore

# Bad
from ..core.session_manager import SessionManager
from .data_store import IDataStore
```

## Adding New Files

When adding new files, follow these rules:

1. **Source code** → `/src/<appropriate_module>/`
2. **Tests** → `/tests/<unit|integration|e2e>/<mirror_src_structure>/`
3. **Documentation** → `/docs/<user-guide|developer-guide|api>/`
4. **Scripts** → `/scripts/`
5. **Config** → `/config/`

Never add files directly to project root unless absolutely necessary.

## Module Responsibilities

Each module has a single, clear responsibility:

- **session_manager**: Orchestrates session lifecycle
- **ai_interviewer**: Conducts interviews with LLM
- **evaluation_manager**: Generates feedback reports
- **communication_manager**: Handles I/O modes
- **data_store**: Persists data to database
- **file_storage**: Manages media files
- **logging_manager**: Centralized logging
- **token_tracker**: Tracks AI API usage

## Dependency Rules

- **core/** can depend on: storage, monitoring, utils
- **communication/** can depend on: storage, monitoring, utils
- **ui/** can depend on: core, communication, utils
- **storage/** can depend on: utils only
- **monitoring/** can depend on: storage, utils
- **utils/** has no dependencies (leaf nodes)

No circular dependencies allowed.
```


## GitHub Pages Documentation Site (Requirement 23)

### Documentation Framework

**Technology**: MkDocs with Material theme

**Rationale**:
- Markdown-based (easy to write and maintain)
- Beautiful, responsive design
- Built-in search functionality
- Easy GitHub Pages deployment
- Version control friendly
- Supports code highlighting and diagrams

### Site Structure

**Location**: All documentation in `/docs` directory

**MkDocs Configuration** (`mkdocs.yml`):

```yaml
site_name: AI Mock Interview Platform
site_description: Practice system design interviews with AI
site_author: Your Team
site_url: https://yourusername.github.io/ai-mock-interview-platform/

repo_name: yourusername/ai-mock-interview-platform
repo_url: https://github.com/yourusername/ai-mock-interview-platform
edit_uri: edit/main/docs/

theme:
  name: material
  palette:
    # Light mode
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    # Dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.instant
    - navigation.tracking
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.code.copy
    - content.code.annotate

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: true
            show_root_heading: true
            heading_level: 2

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.tasklist:
      custom_checkbox: true
  - admonition
  - pymdownx.details
  - attr_list
  - md_in_html
  - toc:
      permalink: true

nav:
  - Home: index.md
  
  - User Guide:
    - Quick Start: user-guide/quick-start.md
    - Using the Platform: user-guide/using-the-platform.md
    - Troubleshooting: user-guide/troubleshooting.md
    - FAQ: user-guide/faq.md
  
  - Developer Guide:
    - Setup: developer-guide/setup.md
    - Architecture: developer-guide/architecture.md
    - Contributing: developer-guide/contributing.md
    - Code Standards: developer-guide/code-standards.md
    - Testing Guide: developer-guide/testing-guide.md
    - Debugging: developer-guide/debugging.md
  
  - API Reference:
    - Session Manager: api/session-manager.md
    - AI Interviewer: api/ai-interviewer.md
    - Data Store: api/data-store.md
  
  - Architecture:
    - Overview: developer-guide/architecture.md
    - Decision Records:
      - PostgreSQL in Docker: adr/001-postgresql-docker.md
      - Streamlit UI: adr/002-streamlit-ui.md
      - LangChain Integration: adr/003-langchain-integration.md
  
  - Implementation Notes:
    - Resume Parsing: implementation-notes/resume-parsing.md
    - Token Tracking: implementation-notes/token-tracking.md
    - Error Handling: implementation-notes/error-handling.md
  
  - Changelog: CHANGELOG.md

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/yourusername/ai-mock-interview-platform
  version:
    provider: mike
```


### CI/CD for GitHub Pages

**GitHub Actions Workflow** (`.github/workflows/docs.yml`):

```yaml
name: Deploy Documentation

on:
  push:
    branches:
      - main
    paths:
      - 'docs/**'
      - 'mkdocs.yml'
      - '.github/workflows/docs.yml'
  workflow_dispatch:  # Allow manual trigger

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Fetch all history for git info
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install mkdocs-material
          pip install mkdocstrings[python]
          pip install pymdown-extensions
      
      - name: Build documentation
        run: mkdocs build --strict
      
      - name: Deploy to GitHub Pages
        run: mkdocs gh-deploy --force
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Verify deployment
        run: |
          echo "Documentation deployed to:"
          echo "https://${{ github.repository_owner }}.github.io/${{ github.event.repository.name }}/"
```

**Deployment Process**:

1. Developer updates documentation in `/docs` directory
2. Commits and pushes to `main` branch
3. GitHub Actions workflow triggers automatically
4. MkDocs builds static site from markdown files
5. Site deployed to GitHub Pages within 5 minutes
6. Available at `https://yourusername.github.io/ai-mock-interview-platform/`

**Local Preview**:

```bash
# Install MkDocs
pip install mkdocs-material mkdocstrings[python]

# Serve documentation locally
mkdocs serve

# Open browser to http://localhost:8000
# Auto-reloads on file changes
```

### Documentation Homepage

**Location**: `docs/index.md`

```markdown
# AI Mock Interview Platform

Practice system design interviews with an AI interviewer that provides real-time feedback.

## Quick Links

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Quick Start__

    ---

    Get started in 10 minutes with our step-by-step guide

    [:octicons-arrow-right-24: Quick Start Guide](user-guide/quick-start.md)

-   :material-code-braces:{ .lg .middle } __For Developers__

    ---

    Set up your development environment and start contributing

    [:octicons-arrow-right-24: Developer Setup](developer-guide/setup.md)

-   :material-book-open-variant:{ .lg .middle } __API Reference__

    ---

    Detailed API documentation for all components

    [:octicons-arrow-right-24: API Docs](api/session-manager.md)

-   :material-help-circle:{ .lg .middle } __Need Help?__

    ---

    Troubleshooting guides and FAQ

    [:octicons-arrow-right-24: Troubleshooting](user-guide/troubleshooting.md)

</div>

## Features

- **Multiple Communication Modes**: Audio, video, whiteboard, and screen sharing
- **AI-Powered Feedback**: Detailed evaluation with improvement plans
- **Resume-Aware**: Problems tailored to your experience level
- **Local-First**: All data stored locally, no cloud dependencies
- **Production-Quality**: Clean code, comprehensive tests, full documentation

## Architecture Overview

```mermaid
graph TB
    UI[Streamlit UI]
    SM[Session Manager]
    AI[AI Interviewer]
    DB[(PostgreSQL)]
    FS[File Storage]
    
    UI --> SM
    SM --> AI
    SM --> DB
    SM --> FS
```

## Getting Started

Choose your path:

=== "End User"

    New to the platform? Start here:
    
    1. [Quick Start Guide](user-guide/quick-start.md) - Get up and running
    2. [Using the Platform](user-guide/using-the-platform.md) - Learn the features
    3. [FAQ](user-guide/faq.md) - Common questions

=== "Developer"

    Want to contribute? Start here:
    
    1. [Developer Setup](developer-guide/setup.md) - Environment setup
    2. [Architecture](developer-guide/architecture.md) - System design
    3. [Contributing](developer-guide/contributing.md) - Contribution guidelines
    4. [Code Standards](developer-guide/code-standards.md) - Coding conventions

## Latest Updates

See [CHANGELOG](CHANGELOG.md) for recent changes and releases.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-mock-interview-platform/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-mock-interview-platform/discussions)
- **Documentation**: You're reading it!
```


## Documentation Validation (Requirement 24)

### Automated Documentation Testing

**Purpose**: Ensure all setup instructions are accurate and complete

**Test Framework**: pytest with custom documentation validators

**Location**: `tests/documentation/`

### Documentation Test Suite

**Location**: `tests/documentation/test_setup_instructions.py`

```python
"""
Tests that validate setup instructions in documentation.
Ensures all documented commands and steps actually work.
"""

import subprocess
import pytest
from pathlib import Path
from typing import List, Tuple

class DocumentationValidator:
    """Validates documentation instructions."""
    
    def __init__(self, doc_path: Path):
        self.doc_path = doc_path
        self.content = doc_path.read_text()
    
    def extract_commands(self) -> List[str]:
        """Extract shell commands from markdown code blocks."""
        commands = []
        in_code_block = False
        current_lang = None
        
        for line in self.content.split('\n'):
            if line.startswith('```'):
                if in_code_block:
                    in_code_block = False
                    current_lang = None
                else:
                    in_code_block = True
                    current_lang = line[3:].strip()
            elif in_code_block and current_lang in ['bash', 'sh', 'shell']:
                if line.strip() and not line.strip().startswith('#'):
                    commands.append(line.strip())
        
        return commands
    
    def extract_file_references(self) -> List[str]:
        """Extract file paths mentioned in documentation."""
        import re
        # Match file paths like `path/to/file.ext` or "path/to/file.ext"
        pattern = r'[`"]([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)[`"]'
        return re.findall(pattern, self.content)
    
    def extract_links(self) -> List[str]:
        """Extract URLs from documentation."""
        import re
        # Match markdown links [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        return [url for text, url in re.findall(pattern, self.content)]

@pytest.fixture
def quick_start_doc():
    """Load Quick Start Guide."""
    return DocumentationValidator(Path("docs/user-guide/quick-start.md"))

@pytest.fixture
def dev_setup_doc():
    """Load Developer Setup Guide."""
    return DocumentationValidator(Path("docs/developer-guide/setup.md"))

class TestQuickStartGuide:
    """Test Quick Start Guide instructions."""
    
    def test_all_referenced_files_exist(self, quick_start_doc):
        """Verify all files mentioned in Quick Start exist."""
        files = quick_start_doc.extract_file_references()
        missing = []
        
        for file_path in files:
            if not Path(file_path).exists():
                missing.append(file_path)
        
        assert not missing, f"Missing files referenced in Quick Start: {missing}"
    
    def test_download_links_accessible(self, quick_start_doc):
        """Verify all download links are accessible."""
        import requests
        
        links = quick_start_doc.extract_links()
        external_links = [link for link in links if link.startswith('http')]
        
        failed = []
        for link in external_links:
            try:
                response = requests.head(link, timeout=10, allow_redirects=True)
                if response.status_code >= 400:
                    failed.append((link, response.status_code))
            except Exception as e:
                failed.append((link, str(e)))
        
        assert not failed, f"Inaccessible links: {failed}"
    
    def test_env_template_exists(self):
        """Verify .env.template file exists as documented."""
        assert Path(".env.template").exists(), ".env.template not found"
    
    def test_startup_script_exists(self):
        """Verify startup.sh script exists as documented."""
        assert Path("scripts/startup.sh").exists(), "startup.sh not found"
    
    def test_docker_compose_file_exists(self):
        """Verify docker-compose.yml exists as documented."""
        assert Path("docker-compose.yml").exists(), "docker-compose.yml not found"

class TestDeveloperSetupGuide:
    """Test Developer Setup Guide instructions."""
    
    def test_requirements_files_exist(self):
        """Verify requirements files exist as documented."""
        assert Path("requirements.txt").exists(), "requirements.txt not found"
        assert Path("requirements-dev.txt").exists(), "requirements-dev.txt not found"
    
    def test_dev_setup_script_exists(self):
        """Verify dev_setup.sh script exists as documented."""
        assert Path("scripts/dev_setup.sh").exists(), "dev_setup.sh not found"
    
    def test_validation_script_exists(self):
        """Verify validation scripts exist as documented."""
        assert Path("scripts/validate_setup.py").exists()
        assert Path("scripts/validate_dev_setup.py").exists()
    
    def test_precommit_config_exists(self):
        """Verify pre-commit config exists as documented."""
        assert Path(".pre-commit-config.yaml").exists()
    
    def test_python_version_requirement(self):
        """Verify Python version meets documented requirement."""
        import sys
        version = sys.version_info
        assert version.major == 3 and version.minor >= 10, \
            f"Python 3.10+ required, found {version.major}.{version.minor}"
    
    def test_all_documented_directories_exist(self):
        """Verify all documented directories exist."""
        required_dirs = [
            "src", "tests", "docs", "scripts", "config",
            "src/core", "src/communication", "src/storage",
            "tests/unit", "tests/integration", "tests/e2e"
        ]
        
        missing = [d for d in required_dirs if not Path(d).exists()]
        assert not missing, f"Missing directories: {missing}"

class TestDockerSetup:
    """Test Docker setup instructions."""
    
    def test_docker_compose_valid(self):
        """Verify docker-compose.yml is valid."""
        result = subprocess.run(
            ["docker-compose", "config"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Invalid docker-compose.yml: {result.stderr}"
    
    def test_docker_compose_services_defined(self):
        """Verify required services are defined in docker-compose.yml."""
        import yaml
        
        with open("docker-compose.yml") as f:
            config = yaml.safe_load(f)
        
        required_services = ["postgres", "app"]
        defined_services = list(config.get("services", {}).keys())
        
        missing = [s for s in required_services if s not in defined_services]
        assert not missing, f"Missing services in docker-compose.yml: {missing}"
```


### Command Validation Tests

**Location**: `tests/documentation/test_command_execution.py`

```python
"""
Tests that execute documented commands to verify they work.
"""

import subprocess
import pytest
from pathlib import Path

@pytest.mark.slow
class TestDocumentedCommands:
    """Test commands from documentation actually work."""
    
    def test_docker_version_command(self):
        """Test: docker --version"""
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "Docker version" in result.stdout
    
    def test_docker_compose_version_command(self):
        """Test: docker-compose --version"""
        result = subprocess.run(
            ["docker-compose", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
    
    def test_python_version_command(self):
        """Test: python --version"""
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        assert result.returncode == 0
        assert "Python 3." in result.stdout
    
    def test_pip_install_dry_run(self):
        """Test: pip install requirements (dry run)"""
        result = subprocess.run(
            ["pip", "install", "--dry-run", "-r", "requirements.txt"],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Dry run should succeed or show what would be installed
        assert result.returncode == 0 or "Would install" in result.stdout
    
    def test_mkdocs_build(self):
        """Test: mkdocs build"""
        result = subprocess.run(
            ["mkdocs", "build", "--strict"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"MkDocs build failed: {result.stderr}"
        assert Path("site/index.html").exists()

class TestValidationScripts:
    """Test validation scripts work as documented."""
    
    def test_validate_setup_script_runs(self):
        """Test: python scripts/validate_setup.py"""
        result = subprocess.run(
            ["python", "scripts/validate_setup.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        # Script should run without crashing
        assert result.returncode in [0, 1]  # 0=success, 1=validation failed
        assert "VALIDATION" in result.stdout
    
    def test_validate_dev_setup_script_runs(self):
        """Test: python scripts/validate_dev_setup.py"""
        result = subprocess.run(
            ["python", "scripts/validate_dev_setup.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode in [0, 1]
        assert "DEVELOPMENT ENVIRONMENT" in result.stdout

### Manual Validation Checklist

**Location**: `docs/developer-guide/manual-validation-checklist.md`

For steps that cannot be automated:

```markdown
# Manual Validation Checklist

This checklist covers setup steps that require manual verification.

## Quick Start Guide Validation

- [ ] Download links work in browser
- [ ] Docker Desktop installer runs successfully
- [ ] API key creation process works
- [ ] Screenshots match current UI
- [ ] Estimated times are accurate
- [ ] Success indicators are visible
- [ ] Error messages are helpful

## Developer Setup Guide Validation

- [ ] IDE configuration instructions work
- [ ] Debugger setup instructions work
- [ ] Breakpoints can be set and hit
- [ ] All recommended extensions install
- [ ] Code formatting works as described
- [ ] Linting catches documented issues

## Docker Setup Validation

- [ ] Docker containers start successfully
- [ ] Health checks pass
- [ ] Database is accessible
- [ ] Application UI loads
- [ ] Logs are visible and readable

## Testing Validation

- [ ] All tests run successfully
- [ ] Coverage reports generate
- [ ] Test output is readable
- [ ] Failed tests show clear errors

## Documentation Validation

- [ ] All links work
- [ ] All images display
- [ ] Search functionality works
- [ ] Code examples are correct
- [ ] Diagrams render properly

## Validation Schedule

- **Before each release**: Run full checklist
- **Monthly**: Spot check random items
- **After doc updates**: Validate affected sections
```


### CI/CD Integration for Documentation Validation

**GitHub Actions Workflow** (`.github/workflows/validate-docs.yml`):

```yaml
name: Validate Documentation

on:
  pull_request:
    paths:
      - 'docs/**'
      - 'scripts/**'
      - 'requirements*.txt'
      - 'docker-compose.yml'
  push:
    branches:
      - main
    paths:
      - 'docs/**'

jobs:
  validate-docs:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11']
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install pytest requests pyyaml
      
      - name: Run documentation tests
        run: pytest tests/documentation/ -v
      
      - name: Validate file references
        run: python scripts/validate_doc_references.py
      
      - name: Check for broken links
        run: python scripts/check_doc_links.py
      
      - name: Validate code examples
        run: python scripts/validate_code_examples.py
      
      - name: Build documentation
        run: mkdocs build --strict
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: doc-validation-results-${{ matrix.os }}-py${{ matrix.python-version }}
          path: |
            test-results/
            site/

  validate-setup-instructions:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Docker
        uses: docker/setup-buildx-action@v3
      
      - name: Validate docker-compose
        run: docker-compose config
      
      - name: Test Docker setup
        run: |
          docker-compose up -d postgres
          sleep 10
          docker exec interview_platform_db pg_isready -U interview_user
          docker-compose down
      
      - name: Validate scripts are executable
        run: |
          test -x scripts/startup.sh
          test -x scripts/dev_setup.sh
          test -x scripts/backup.sh
```

### Documentation Validation Scripts

**Link Checker** (`scripts/check_doc_links.py`):

```python
"""Check all links in documentation are valid."""

import re
import requests
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_links(file_path: Path) -> List[Tuple[str, int]]:
    """Extract all links from markdown file with line numbers."""
    content = file_path.read_text()
    links = []
    
    for i, line in enumerate(content.split('\n'), 1):
        # Match markdown links [text](url)
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            url = match.group(2)
            if url.startswith('http'):
                links.append((url, i))
    
    return links

def check_link(url: str) -> Tuple[str, bool, str]:
    """Check if a link is accessible."""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code < 400:
            return (url, True, "OK")
        return (url, False, f"HTTP {response.status_code}")
    except Exception as e:
        return (url, False, str(e))

def main():
    """Check all links in documentation."""
    docs_dir = Path("docs")
    all_links = []
    
    # Collect all links
    for md_file in docs_dir.rglob("*.md"):
        links = extract_links(md_file)
        all_links.extend([(md_file, url, line) for url, line in links])
    
    print(f"Checking {len(all_links)} links...")
    
    # Check links in parallel
    broken_links = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(check_link, url): (file, url, line)
            for file, url, line in all_links
        }
        
        for future in as_completed(futures):
            file, url, line = futures[future]
            url_result, is_valid, message = future.result()
            
            if not is_valid:
                broken_links.append((file, line, url, message))
                print(f"❌ {file}:{line} - {url} - {message}")
    
    if broken_links:
        print(f"\n❌ Found {len(broken_links)} broken links")
        return 1
    else:
        print(f"\n✅ All {len(all_links)} links are valid")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

**Code Example Validator** (`scripts/validate_code_examples.py`):

```python
"""Validate code examples in documentation are syntactically correct."""

import re
import ast
from pathlib import Path
from typing import List, Tuple

def extract_python_code_blocks(file_path: Path) -> List[Tuple[str, int]]:
    """Extract Python code blocks from markdown."""
    content = file_path.read_text()
    code_blocks = []
    
    in_code_block = False
    current_code = []
    start_line = 0
    current_lang = None
    
    for i, line in enumerate(content.split('\n'), 1):
        if line.startswith('```'):
            if in_code_block:
                if current_lang == 'python':
                    code_blocks.append(('\n'.join(current_code), start_line))
                in_code_block = False
                current_code = []
                current_lang = None
            else:
                in_code_block = True
                start_line = i + 1
                current_lang = line[3:].strip()
        elif in_code_block:
            current_code.append(line)
    
    return code_blocks

def validate_python_syntax(code: str) -> Tuple[bool, str]:
    """Check if Python code is syntactically valid."""
    try:
        ast.parse(code)
        return (True, "OK")
    except SyntaxError as e:
        return (False, f"Syntax error at line {e.lineno}: {e.msg}")

def main():
    """Validate all Python code examples in documentation."""
    docs_dir = Path("docs")
    errors = []
    total_blocks = 0
    
    for md_file in docs_dir.rglob("*.md"):
        code_blocks = extract_python_code_blocks(md_file)
        total_blocks += len(code_blocks)
        
        for code, line_num in code_blocks:
            is_valid, message = validate_python_syntax(code)
            if not is_valid:
                errors.append((md_file, line_num, message))
                print(f"❌ {md_file}:{line_num} - {message}")
    
    if errors:
        print(f"\n❌ Found {len(errors)} invalid code examples out of {total_blocks}")
        return 1
    else:
        print(f"\n✅ All {total_blocks} Python code examples are valid")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

### Documentation Coverage Metrics

Track documentation completeness:

```python
"""Calculate documentation coverage metrics."""

from pathlib import Path
import ast

def count_documented_functions(file_path: Path) -> tuple[int, int]:
    """Count functions and how many have docstrings."""
    content = file_path.read_text()
    tree = ast.parse(content)
    
    total_functions = 0
    documented_functions = 0
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total_functions += 1
            if ast.get_docstring(node):
                documented_functions += 1
    
    return total_functions, documented_functions

def main():
    """Calculate documentation coverage for the project."""
    src_dir = Path("src")
    total_funcs = 0
    documented_funcs = 0
    
    for py_file in src_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        funcs, docs = count_documented_functions(py_file)
        total_funcs += funcs
        documented_funcs += docs
    
    coverage = (documented_funcs / total_funcs * 100) if total_funcs > 0 else 0
    
    print(f"Documentation Coverage: {coverage:.1f}%")
    print(f"Documented functions: {documented_funcs}/{total_funcs}")
    
    if coverage < 80:
        print("❌ Documentation coverage below 80%")
        return 1
    else:
        print("✅ Documentation coverage meets requirement")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
```

## Summary of New Design Elements

The design now comprehensively addresses Requirements 20-24:

**Requirement 20 (End-User Documentation)**:
- Quick Start Guide with plain language and screenshots
- Startup validation script with clear error messages
- Step-by-step instructions with time estimates
- Troubleshooting guide for common issues

**Requirement 21 (Developer Documentation)**:
- Comprehensive Developer Setup Guide
- Automated setup scripts (dev_setup.sh)
- Development environment validation
- Architecture diagrams and workflow documentation
- Debugging instructions with examples

**Requirement 22 (Project Organization)**:
- Clean directory structure with max 10 root files
- Organized by functional area (src/, tests/, docs/, scripts/, config/)
- STRUCTURE.md documenting organization
- Linting rules enforcing structure
- Clear module responsibilities and dependencies

**Requirement 23 (GitHub Pages)**:
- MkDocs with Material theme for documentation site
- Automated deployment via GitHub Actions
- Search functionality and responsive design
- API documentation generated from code
- Changelog and implementation notes

**Requirement 24 (Documentation Validation)**:
- Automated tests for setup instructions
- Link checker for broken URLs
- Code example syntax validation
- Multi-OS testing (Windows, macOS, Linux)
- Manual validation checklist for non-automatable steps
- CI/CD integration blocking invalid documentation

All documentation is validated automatically on every commit, ensuring instructions remain accurate and complete.
