-- Database initialization script for AI Mock Interview Platform
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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
