-- Supabase Database Schema
-- Create tables for workflows, fields, and prompts

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create workflows table
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create fields table
CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL,
    name TEXT NOT NULL,
    data_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_fields_workflow_id 
        FOREIGN KEY (workflow_id) 
        REFERENCES workflows(id) 
        ON DELETE CASCADE
);

-- Create prompts table
CREATE TABLE prompts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL,
    prompt_template TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Foreign key constraint
    CONSTRAINT fk_prompts_field_id 
        FOREIGN KEY (field_id) 
        REFERENCES fields(id) 
        ON DELETE CASCADE
);

-- Create indexes for better query performance

-- Index on workflows.created_at for time-based queries
CREATE INDEX idx_workflows_created_at ON workflows(created_at);

-- Index on workflows.name for name-based searches
CREATE INDEX idx_workflows_name ON workflows(name);

-- Index on fields.workflow_id for efficient joins
CREATE INDEX idx_fields_workflow_id ON fields(workflow_id);

-- Index on fields.data_type for filtering by data type
CREATE INDEX idx_fields_data_type ON fields(data_type);

-- Index on fields.name for name-based searches
CREATE INDEX idx_fields_name ON fields(name);

-- Index on prompts.field_id for efficient joins
CREATE INDEX idx_prompts_field_id ON prompts(field_id);

-- Index on prompts.created_at for time-based queries
CREATE INDEX idx_prompts_created_at ON prompts(created_at);

-- Add constraints for data validation

-- Ensure data_type is one of common types
ALTER TABLE fields 
ADD CONSTRAINT chk_fields_data_type 
CHECK (data_type IN ('text', 'number', 'boolean', 'date', 'email', 'url', 'json'));

-- Ensure name fields are not empty
ALTER TABLE workflows 
ADD CONSTRAINT chk_workflows_name_not_empty 
CHECK (LENGTH(TRIM(name)) > 0);

ALTER TABLE fields 
ADD CONSTRAINT chk_fields_name_not_empty 
CHECK (LENGTH(TRIM(name)) > 0);

-- Ensure prompt_template is not empty
ALTER TABLE prompts 
ADD CONSTRAINT chk_prompts_template_not_empty 
CHECK (LENGTH(TRIM(prompt_template)) > 0);

-- Add unique constraints where appropriate

-- Ensure workflow names are unique
ALTER TABLE workflows 
ADD CONSTRAINT uq_workflows_name UNIQUE (name);

-- Ensure field names are unique within a workflow
ALTER TABLE fields 
ADD CONSTRAINT uq_fields_name_per_workflow UNIQUE (workflow_id, name);

-- Add comments for documentation
COMMENT ON TABLE workflows IS 'Stores workflow definitions with metadata';
COMMENT ON TABLE fields IS 'Stores field definitions for each workflow';
COMMENT ON TABLE prompts IS 'Stores prompt templates for each field';

COMMENT ON COLUMN workflows.id IS 'Unique identifier for the workflow';
COMMENT ON COLUMN workflows.name IS 'Human-readable name for the workflow';
COMMENT ON COLUMN workflows.created_at IS 'Timestamp when the workflow was created';

COMMENT ON COLUMN fields.id IS 'Unique identifier for the field';
COMMENT ON COLUMN fields.workflow_id IS 'Reference to the parent workflow';
COMMENT ON COLUMN fields.name IS 'Name of the field within the workflow';
COMMENT ON COLUMN fields.data_type IS 'Type of data this field expects (text, number, boolean, etc.)';

COMMENT ON COLUMN prompts.id IS 'Unique identifier for the prompt';
COMMENT ON COLUMN prompts.field_id IS 'Reference to the field this prompt is for';
COMMENT ON COLUMN prompts.prompt_template IS 'Template text for the AI prompt';
