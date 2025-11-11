"""
Data models and type definitions for the AI Mock Interview Platform.

This module defines all core data structures used throughout the application,
including sessions, messages, evaluations, and configuration objects.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any


class CommunicationMode(Enum):
    """Communication modes available during interview sessions."""
    AUDIO = "audio"
    VIDEO = "video"
    WHITEBOARD = "whiteboard"
    SCREEN_SHARE = "screen_share"
    TEXT = "text"


class SessionStatus(Enum):
    """Status values for interview sessions."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class WorkExperience:
    """Work experience entry from resume."""
    company: str
    title: str
    duration: str
    description: str


@dataclass
class Education:
    """Education entry from resume."""
    institution: str
    degree: str
    field: str
    year: str


@dataclass
class ResumeData:
    """
    Structured data extracted from candidate resume.
    
    Attributes:
        user_id: Unique identifier for the user
        name: Candidate's full name
        email: Candidate's email address
        experience_level: Experience level (junior, mid, senior, staff)
        years_of_experience: Total years of professional experience
        domain_expertise: List of domain areas (e.g., backend, distributed-systems)
        work_experience: List of work experience entries
        education: List of education entries
        skills: List of technical skills
        raw_text: Original resume text
    """
    user_id: str
    name: str
    email: str
    experience_level: str
    years_of_experience: int
    domain_expertise: List[str]
    work_experience: List[WorkExperience]
    education: List[Education]
    skills: List[str]
    raw_text: str


@dataclass
class SessionConfig:
    """
    Configuration for an interview session.
    
    Attributes:
        enabled_modes: List of communication modes enabled for the session
        ai_provider: AI provider name (openai or anthropic)
        ai_model: Specific model to use
        resume_data: Optional resume data for resume-aware problem generation
        duration_minutes: Optional session duration limit
    """
    enabled_modes: List[CommunicationMode]
    ai_provider: str
    ai_model: str
    resume_data: Optional[ResumeData] = None
    duration_minutes: Optional[int] = None


@dataclass
class Session:
    """
    Interview session instance.
    
    Attributes:
        id: Unique session identifier (UUID)
        user_id: User identifier
        created_at: Session creation timestamp
        ended_at: Session end timestamp (None if active)
        status: Current session status
        config: Session configuration
        metadata: Additional session metadata
    """
    id: str
    user_id: str
    created_at: datetime
    ended_at: Optional[datetime]
    status: SessionStatus
    config: SessionConfig
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """
    Conversation message between interviewer and candidate.
    
    Attributes:
        role: Message sender role (interviewer or candidate)
        content: Message text content
        timestamp: Message timestamp
        metadata: Additional message metadata
    """
    role: str
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MediaFile:
    """
    Reference to a media file stored on filesystem.
    
    Attributes:
        file_type: Type of media (audio, video, whiteboard, screen)
        file_path: Path to file on filesystem
        timestamp: File creation timestamp
        file_size_bytes: File size in bytes
        metadata: Additional file metadata
    """
    file_type: str
    file_path: str
    timestamp: datetime
    file_size_bytes: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TokenUsage:
    """
    Token usage tracking for AI API calls.
    
    Attributes:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        total_tokens: Total tokens (input + output)
        estimated_cost: Estimated cost in USD
        provider: AI provider name
        model: Model name
        operation: Operation type (e.g., question_generation, response_analysis)
    """
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost: float
    provider: str
    model: str
    operation: str = ""


@dataclass
class SessionTokenUsage:
    """
    Aggregated token usage for a session.
    
    Attributes:
        total_input_tokens: Total input tokens across all operations
        total_output_tokens: Total output tokens across all operations
        total_tokens: Total tokens (input + output)
        total_cost: Total estimated cost in USD
        breakdown_by_operation: Token usage breakdown by operation type
    """
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: float
    breakdown_by_operation: Dict[str, TokenUsage] = field(default_factory=dict)


@dataclass
class Feedback:
    """
    Feedback item in evaluation report.
    
    Attributes:
        category: Feedback category (went_well, went_okay, needs_improvement)
        description: Feedback description
        evidence: List of specific examples supporting the feedback
    """
    category: str
    description: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class ActionItem:
    """
    Action item in improvement plan.
    
    Attributes:
        step_number: Sequential step number
        description: Action description
        resources: List of recommended resources
    """
    step_number: int
    description: str
    resources: List[str] = field(default_factory=list)


@dataclass
class ImprovementPlan:
    """
    Structured improvement plan with actionable steps.
    
    Attributes:
        priority_areas: List of priority improvement areas
        concrete_steps: List of action items
        resources: List of general resources
    """
    priority_areas: List[str]
    concrete_steps: List[ActionItem]
    resources: List[str] = field(default_factory=list)


@dataclass
class CompetencyScore:
    """
    Score for a specific competency area.
    
    Attributes:
        score: Numeric score (0-100)
        confidence_level: Confidence in assessment (high, medium, low)
        evidence: List of specific examples supporting the score
    """
    score: float
    confidence_level: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class ModeAnalysis:
    """
    Analysis of communication mode usage.
    
    Attributes:
        audio_quality: Audio quality assessment
        video_presence: Video presence assessment
        whiteboard_usage: Whiteboard usage assessment
        screen_share_usage: Screen share usage assessment
        overall_communication: Overall communication effectiveness
    """
    audio_quality: Optional[str] = None
    video_presence: Optional[str] = None
    whiteboard_usage: Optional[str] = None
    screen_share_usage: Optional[str] = None
    overall_communication: str = ""


@dataclass
class EvaluationReport:
    """
    Comprehensive evaluation report for a completed session.
    
    Attributes:
        session_id: Associated session identifier
        overall_score: Overall performance score (0-100)
        competency_scores: Scores for individual competencies
        went_well: List of things that went well
        went_okay: List of things that were okay
        needs_improvement: List of things that need improvement
        improvement_plan: Structured improvement plan
        communication_mode_analysis: Analysis of communication modes
        created_at: Report creation timestamp
    """
    session_id: str
    overall_score: float
    competency_scores: Dict[str, CompetencyScore]
    went_well: List[Feedback]
    went_okay: List[Feedback]
    needs_improvement: List[Feedback]
    improvement_plan: ImprovementPlan
    communication_mode_analysis: ModeAnalysis
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionSummary:
    """
    Summary information for a session (used in session lists).
    
    Attributes:
        id: Session identifier
        user_id: User identifier
        created_at: Session creation timestamp
        duration_minutes: Session duration in minutes
        overall_score: Overall evaluation score (None if not evaluated)
        status: Session status
    """
    id: str
    user_id: str
    created_at: datetime
    duration_minutes: Optional[int]
    overall_score: Optional[float]
    status: SessionStatus


@dataclass
class LogEntry:
    """
    Structured log entry for audit trail.
    
    Attributes:
        timestamp: Log entry timestamp
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        component: Component name that generated the log
        operation: Operation being performed
        message: Log message
        session_id: Associated session identifier (if applicable)
        user_id: Associated user identifier (if applicable)
        metadata: Additional structured metadata
        stack_trace: Exception stack trace (if applicable)
    """
    timestamp: datetime
    level: str
    component: str
    operation: str
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None


@dataclass
class WhiteboardAnalysis:
    """
    Analysis of whiteboard diagram content.
    
    Attributes:
        components_identified: List of system components identified
        relationships: List of relationships between components
        missing_elements: List of potentially missing elements
        design_patterns: List of design patterns recognized
    """
    components_identified: List[str]
    relationships: List[str]
    missing_elements: List[str]
    design_patterns: List[str]


@dataclass
class InterviewResponse:
    """
    Response from AI interviewer.
    
    Attributes:
        content: Response text content
        token_usage: Token usage for this response
    """
    content: str
    token_usage: TokenUsage


@dataclass
class ConversationContext:
    """
    Context for conversation management.
    
    Attributes:
        session_id: Session identifier
        messages: List of conversation messages
        whiteboard_snapshots: List of whiteboard snapshot paths
        metadata: Additional context metadata
    """
    session_id: str
    messages: List[Message]
    whiteboard_snapshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """
    Health status for a system component.
    
    Attributes:
        status: Status value (healthy, degraded, unhealthy)
        message: Status message
        last_check: Last health check timestamp
        details: Additional status details
    """
    status: str
    message: str
    last_check: datetime
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """
    Overall system health status.
    
    Attributes:
        database: Database health status
        ai_providers: AI provider health statuses
        file_storage: File storage health status
        overall_status: Overall system status
    """
    database: HealthStatus
    ai_providers: Dict[str, HealthStatus]
    file_storage: HealthStatus
    overall_status: str
