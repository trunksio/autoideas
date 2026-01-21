-- Healthcare AI Survey Schema
-- Stores anonymous survey responses from ElevenLabs voice conversations

-- Sessions (anonymous, tracked by ElevenLabs conversation ID)
CREATE TABLE survey_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(255) UNIQUE NOT NULL,
    survey_id VARCHAR(100) NOT NULL DEFAULT 'healthcare_ai_2025',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

-- Answers (one row per question per session)
CREATE TABLE survey_answers (
    id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES survey_sessions(id) ON DELETE CASCADE,
    question_id VARCHAR(100) NOT NULL,
    section_name VARCHAR(100),
    question_text TEXT,
    answer_type VARCHAR(50) NOT NULL,  -- 'free_text', 'rating', 'multiple_choice'
    answer_text TEXT,
    answer_rating INTEGER CHECK (answer_rating BETWEEN 1 AND 5),
    answer_choices JSONB,
    raw_transcript TEXT,
    answered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(session_id, question_id)
);

-- Indexes for common queries
CREATE INDEX idx_sessions_survey ON survey_sessions(survey_id);
CREATE INDEX idx_sessions_started ON survey_sessions(started_at);
CREATE INDEX idx_sessions_completed ON survey_sessions(completed_at);
CREATE INDEX idx_answers_session ON survey_answers(session_id);
CREATE INDEX idx_answers_question ON survey_answers(question_id);
CREATE INDEX idx_answers_section ON survey_answers(section_name);
