"""
Pydantic models for database operations.
Includes create models for POST requests and response models with IDs and timestamps.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


# =============================================================================
# CREATE MODELS (for POST requests)
# =============================================================================

class WorkflowCreate(BaseModel):
    """Model for creating a new workflow."""
    name: str = Field(..., min_length=1, description="Name of the workflow")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Workflow name cannot be empty')
        return v.strip()


class FieldCreate(BaseModel):
    """Model for creating a new field."""
    workflow_id: UUID = Field(..., description="ID of the parent workflow")
    name: str = Field(..., min_length=1, description="Name of the field")
    data_type: str = Field(..., description="Type of data this field expects")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Field name cannot be empty')
        return v.strip()

    @validator('data_type')
    def validate_data_type(cls, v):
        valid_types = ['text', 'number', 'boolean', 'date', 'email', 'url', 'json']
        if v not in valid_types:
            raise ValueError(f'Data type must be one of: {", ".join(valid_types)}')
        return v


class PromptCreate(BaseModel):
    """Model for creating a new prompt."""
    field_id: UUID = Field(..., description="ID of the parent field")
    prompt_template: str = Field(..., min_length=1, description="Template text for the AI prompt")

    @validator('prompt_template')
    def validate_prompt_template(cls, v):
        if not v.strip():
            raise ValueError('Prompt template cannot be empty')
        return v.strip()


# =============================================================================
# RESPONSE MODELS (for GET responses with IDs and timestamps)
# =============================================================================

class Prompt(BaseModel):
    """Model for prompt responses."""
    id: UUID
    field_id: UUID
    prompt_template: str
    created_at: datetime

    class Config:
        from_attributes = True


class FieldSchema(BaseModel):
    """Model for field responses."""
    id: UUID
    workflow_id: UUID
    name: str
    data_type: str
    created_at: datetime
    prompts: Optional[List[Prompt]] = None  # Optional nested prompts

    class Config:
        from_attributes = True


class Workflow(BaseModel):
    """Model for workflow responses."""
    id: UUID
    name: str
    created_at: datetime
    fields: Optional[List[FieldSchema]] = None  # Optional nested fields

    class Config:
        from_attributes = True


# =============================================================================
# UPDATE MODELS (for PUT/PATCH requests)
# =============================================================================

class WorkflowUpdate(BaseModel):
    """Model for updating a workflow."""
    name: Optional[str] = Field(None, min_length=1, description="Updated name of the workflow")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Workflow name cannot be empty')
        return v.strip() if v else v


class FieldUpdate(BaseModel):
    """Model for updating a field."""
    name: Optional[str] = Field(None, min_length=1, description="Updated name of the field")
    data_type: Optional[str] = Field(None, description="Updated data type")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Field name cannot be empty')
        return v.strip() if v else v

    @validator('data_type')
    def validate_data_type(cls, v):
        if v is not None:
            valid_types = ['text', 'number', 'boolean', 'date', 'email', 'url', 'json']
            if v not in valid_types:
                raise ValueError(f'Data type must be one of: {", ".join(valid_types)}')
        return v


class PromptUpdate(BaseModel):
    """Model for updating a prompt."""
    prompt_template: Optional[str] = Field(None, min_length=1, description="Updated prompt template")

    @validator('prompt_template')
    def validate_prompt_template(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Prompt template cannot be empty')
        return v.strip() if v else v


# =============================================================================
# UTILITY MODELS
# =============================================================================

class WorkflowWithFields(Workflow):
    """Workflow model that always includes fields."""
    fields: List[FieldSchema] = []


class FieldWithPrompts(FieldSchema):
    """Field model that always includes prompts."""
    prompts: List[Prompt] = []


class WorkflowComplete(Workflow):
    """Complete workflow model with all nested relationships."""
    fields: List[FieldWithPrompts] = []


# =============================================================================
# EXECUTION MODELS
# =============================================================================

class WorkflowExecutionRequest(BaseModel):
    """Model for workflow execution requests."""
    user_input: str = Field(..., min_length=1, description="User input text to process")

    @validator('user_input')
    def validate_user_input(cls, v):
        if not v.strip():
            raise ValueError('User input cannot be empty')
        return v.strip()


class FieldExecutionResult(BaseModel):
    """Model for individual field execution results."""
    field_id: UUID
    field_name: str
    data_type: str
    prompt_template: str
    ai_response: str
    execution_success: bool
    error_message: Optional[str] = None


class WorkflowExecutionResponse(BaseModel):
    """Model for workflow execution responses."""
    workflow_id: UUID
    workflow_name: str
    user_input: str
    total_fields: int
    successful_executions: int
    failed_executions: int
    field_results: List[FieldExecutionResult]
    execution_timestamp: datetime
