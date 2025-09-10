"""
FastAPI application with CRUD endpoints for workflows, fields, and prompts.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import uuid
from datetime import datetime

from database import supabase
from models import (
    WorkflowCreate, Workflow, WorkflowComplete,
    FieldCreate, FieldSchema, FieldWithPrompts,
    PromptCreate, Prompt,
    WorkflowExecutionRequest, WorkflowExecutionResponse, FieldExecutionResult
)
from services import execute_prompt

# Initialize FastAPI app
app = FastAPI(
    title="AI Configurable MVP API",
    description="API for managing workflows, fields, and prompts",
    version="1.0.0"
)


# =============================================================================
# WORKFLOW ENDPOINTS
# =============================================================================

@app.post("/workflows/", response_model=Workflow, status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow_data: WorkflowCreate):
    """
    Create a new workflow.
    """
    try:
        # Insert workflow into database
        result = supabase.table("workflows").insert({
            "name": workflow_data.name
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create workflow"
            )
        
        workflow = result.data[0]
        return Workflow(
            id=workflow["id"],
            name=workflow["name"],
            created_at=workflow["created_at"]
        )
        
    except Exception as e:
        if "duplicate key value" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A workflow with this name already exists"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/workflows/{workflow_id}", response_model=WorkflowComplete)
async def get_workflow(workflow_id: str):
    """
    Get a workflow with all its fields and their prompts.
    """
    try:
        # Validate UUID format
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workflow ID format"
            )
        
        # Get workflow
        workflow_result = supabase.table("workflows").select("*").eq("id", str(workflow_uuid)).execute()
        
        if not workflow_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        workflow = workflow_result.data[0]
        
        # Get fields for this workflow
        fields_result = supabase.table("fields").select("*").eq("workflow_id", str(workflow_uuid)).execute()
        fields = []
        
        for field_data in fields_result.data:
            # Get prompts for each field
            prompts_result = supabase.table("prompts").select("*").eq("field_id", field_data["id"]).execute()
            
            prompts = [
                Prompt(
                    id=prompt["id"],
                    field_id=prompt["field_id"],
                    prompt_template=prompt["prompt_template"],
                    created_at=prompt["created_at"]
                )
                for prompt in prompts_result.data
            ]
            
            field = FieldWithPrompts(
                id=field_data["id"],
                workflow_id=field_data["workflow_id"],
                name=field_data["name"],
                data_type=field_data["data_type"],
                created_at=field_data["created_at"],
                prompts=prompts
            )
            fields.append(field)
        
        return WorkflowComplete(
            id=workflow["id"],
            name=workflow["name"],
            created_at=workflow["created_at"],
            fields=fields
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# =============================================================================
# FIELD ENDPOINTS
# =============================================================================

@app.post("/workflows/{workflow_id}/fields", response_model=FieldWithPrompts, status_code=status.HTTP_201_CREATED)
async def create_field_with_prompt(workflow_id: str, field_data: FieldCreate, prompt_data: PromptCreate):
    """
    Add a new field and its prompt to a workflow.
    """
    try:
        # Validate UUID format
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workflow ID format"
            )
        
        # Verify workflow exists
        workflow_result = supabase.table("workflows").select("id").eq("id", str(workflow_uuid)).execute()
        if not workflow_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Validate that field_data.workflow_id matches the URL parameter
        if field_data.workflow_id != workflow_uuid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Field workflow_id must match the URL workflow_id"
            )
        
        # Create field
        field_result = supabase.table("fields").insert({
            "workflow_id": str(workflow_uuid),
            "name": field_data.name,
            "data_type": field_data.data_type
        }).execute()
        
        if not field_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create field"
            )
        
        field = field_result.data[0]
        field_id = field["id"]
        
        # Validate that prompt_data.field_id matches the created field
        if prompt_data.field_id != uuid.UUID(field_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt field_id must match the created field ID"
            )
        
        # Create prompt
        prompt_result = supabase.table("prompts").insert({
            "field_id": field_id,
            "prompt_template": prompt_data.prompt_template
        }).execute()
        
        if not prompt_result.data:
            # If prompt creation fails, clean up the field
            supabase.table("fields").delete().eq("id", field_id).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create prompt"
            )
        
        prompt = prompt_result.data[0]
        
        return FieldWithPrompts(
            id=field["id"],
            workflow_id=field["workflow_id"],
            name=field["name"],
            data_type=field["data_type"],
            created_at=field["created_at"],
            prompts=[
                Prompt(
                    id=prompt["id"],
                    field_id=prompt["field_id"],
                    prompt_template=prompt["prompt_template"],
                    created_at=prompt["created_at"]
                )
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        if "duplicate key value" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A field with this name already exists in this workflow"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# =============================================================================
# WORKFLOW EXECUTION ENDPOINT
# =============================================================================

@app.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(workflow_id: str, execution_request: WorkflowExecutionRequest):
    """
    Execute a workflow by running all field prompts with the provided user input.
    """
    try:
        # Validate UUID format
        try:
            workflow_uuid = uuid.UUID(workflow_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid workflow ID format"
            )
        
        # Get workflow with all fields and prompts
        workflow_result = supabase.table("workflows").select("*").eq("id", str(workflow_uuid)).execute()
        
        if not workflow_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        workflow = workflow_result.data[0]
        
        # Get all fields for this workflow
        fields_result = supabase.table("fields").select("*").eq("workflow_id", str(workflow_uuid)).execute()
        
        if not fields_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No fields found for this workflow"
            )
        
        fields = fields_result.data
        field_results = []
        successful_executions = 0
        failed_executions = 0
        
        # Process each field asynchronously
        for field in fields:
            # Get prompts for this field
            prompts_result = supabase.table("prompts").select("*").eq("field_id", field["id"]).execute()
            
            if not prompts_result.data:
                # Field has no prompts
                field_result = FieldExecutionResult(
                    field_id=field["id"],
                    field_name=field["name"],
                    data_type=field["data_type"],
                    prompt_template="",
                    ai_response="",
                    execution_success=False,
                    error_message="No prompts found for this field"
                )
                field_results.append(field_result)
                failed_executions += 1
                continue
            
            # Use the first prompt (assuming one prompt per field for now)
            prompt = prompts_result.data[0]
            
            try:
                # Execute the prompt asynchronously
                ai_response = await execute_prompt(
                    prompt_template=prompt["prompt_template"],
                    user_input=execution_request.user_input
                )
                
                field_result = FieldExecutionResult(
                    field_id=field["id"],
                    field_name=field["name"],
                    data_type=field["data_type"],
                    prompt_template=prompt["prompt_template"],
                    ai_response=ai_response,
                    execution_success=True,
                    error_message=None
                )
                field_results.append(field_result)
                successful_executions += 1
                
            except Exception as e:
                # Handle prompt execution errors
                field_result = FieldExecutionResult(
                    field_id=field["id"],
                    field_name=field["name"],
                    data_type=field["data_type"],
                    prompt_template=prompt["prompt_template"],
                    ai_response="",
                    execution_success=False,
                    error_message=str(e)
                )
                field_results.append(field_result)
                failed_executions += 1
        
        # Create response
        response = WorkflowExecutionResponse(
            workflow_id=workflow["id"],
            workflow_name=workflow["name"],
            user_input=execution_request.user_input,
            total_fields=len(fields),
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            field_results=field_results,
            execution_timestamp=datetime.utcnow()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during workflow execution: {str(e)}"
        )


# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    try:
        # Test database connection
        supabase.table("workflows").select("id").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )


# =============================================================================
# ROOT ENDPOINT
# =============================================================================

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "AI Configurable MVP API",
        "version": "1.0.0",
        "endpoints": {
            "workflows": "/workflows/",
            "workflow_detail": "/workflows/{workflow_id}",
            "add_field": "/workflows/{workflow_id}/fields",
            "execute_workflow": "/workflows/{workflow_id}/execute",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
