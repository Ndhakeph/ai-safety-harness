-- AI Safety Testing Harness Database Schema
-- Execute this in your Supabase SQL editor

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Adversarial Prompts Library Table
CREATE TABLE IF NOT EXISTS adversarial_prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT NOT NULL CHECK (category IN ('jailbreak', 'injection', 'harmful', 'manipulation', 'encoding')),
    prompt TEXT NOT NULL,
    expected_blocked BOOLEAN NOT NULL DEFAULT true,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster category queries
CREATE INDEX IF NOT EXISTS idx_adversarial_prompts_category ON adversarial_prompts(category);
CREATE INDEX IF NOT EXISTS idx_adversarial_prompts_severity ON adversarial_prompts(severity);

-- Test Runs Table
CREATE TABLE IF NOT EXISTS test_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prompt_id UUID REFERENCES adversarial_prompts(id) ON DELETE SET NULL,
    input_prompt TEXT NOT NULL,
    pre_guardrail_blocked BOOLEAN NOT NULL DEFAULT false,
    pre_guardrail_rules JSONB DEFAULT '[]'::jsonb,
    model_response TEXT,
    post_guardrail_blocked BOOLEAN NOT NULL DEFAULT false,
    post_guardrail_rules JSONB DEFAULT '[]'::jsonb,
    jailbreak_successful BOOLEAN NOT NULL DEFAULT false,
    safety_score INTEGER NOT NULL CHECK (safety_score >= 0 AND safety_score <= 100),
    model_used TEXT NOT NULL DEFAULT 'gemini-pro',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_test_runs_prompt_id ON test_runs(prompt_id);
CREATE INDEX IF NOT EXISTS idx_test_runs_created_at ON test_runs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_test_runs_jailbreak ON test_runs(jailbreak_successful);
CREATE INDEX IF NOT EXISTS idx_test_runs_safety_score ON test_runs(safety_score);

-- Incidents Table
CREATE TABLE IF NOT EXISTS incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_run_id UUID NOT NULL REFERENCES test_runs(id) ON DELETE CASCADE,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster incident queries
CREATE INDEX IF NOT EXISTS idx_incidents_test_run_id ON incidents(test_run_id);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents(created_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER update_adversarial_prompts_updated_at
    BEFORE UPDATE ON adversarial_prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE adversarial_prompts ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (adjust based on your security needs)
CREATE POLICY "Enable read access for all users" ON adversarial_prompts
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON adversarial_prompts
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON adversarial_prompts
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete access for all users" ON adversarial_prompts
    FOR DELETE USING (true);

CREATE POLICY "Enable read access for all users" ON test_runs
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON test_runs
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON incidents
    FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON incidents
    FOR INSERT WITH CHECK (true);
