"""API routes for managing the adversarial prompt library."""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from ..models.schemas import (
    AdversarialPrompt,
    AdversarialPromptCreate,
    AdversarialPromptUpdate,
    Incident,
)
from ..db import get_db

router = APIRouter(prefix="/api/library", tags=["library"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[AdversarialPrompt])
async def get_prompts(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get adversarial prompts with optional filters.

    Args:
        category: Filter by category
        severity: Filter by severity
        limit: Number of results to return
        offset: Number of results to skip

    Returns:
        List of adversarial prompts

    Raises:
        HTTPException: If query fails
    """
    try:
        db = get_db()
        query = db.table("adversarial_prompts").select("*")

        # Apply filters
        if category:
            query = query.eq("category", category)
        if severity:
            query = query.eq("severity", severity)

        # Order by most recent first
        query = query.order("created_at", desc=True)

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        return result.data or []

    except Exception as e:
        logger.error(f"Error fetching prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch prompts: {str(e)}")


@router.get("/{prompt_id}", response_model=AdversarialPrompt)
async def get_prompt(prompt_id: UUID):
    """Get a specific adversarial prompt by ID.

    Args:
        prompt_id: UUID of the prompt

    Returns:
        Adversarial prompt details

    Raises:
        HTTPException: If prompt not found
    """
    try:
        db = get_db()
        result = db.table("adversarial_prompts").select("*").eq("id", str(prompt_id)).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Prompt not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch prompt: {str(e)}")


@router.post("/", response_model=AdversarialPrompt, status_code=201)
async def create_prompt(prompt_data: AdversarialPromptCreate):
    """Create a new adversarial prompt.

    Args:
        prompt_data: Prompt data to create

    Returns:
        Created adversarial prompt

    Raises:
        HTTPException: If creation fails
    """
    try:
        db = get_db()

        data = {
            "category": prompt_data.category,
            "prompt": prompt_data.prompt,
            "expected_blocked": prompt_data.expected_blocked,
            "severity": prompt_data.severity,
        }

        result = db.table("adversarial_prompts").insert(data).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=500, detail="Failed to create prompt")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create prompt: {str(e)}")


@router.patch("/{prompt_id}", response_model=AdversarialPrompt)
async def update_prompt(prompt_id: UUID, prompt_data: AdversarialPromptUpdate):
    """Update an existing adversarial prompt.

    Args:
        prompt_id: UUID of the prompt to update
        prompt_data: Updated prompt data

    Returns:
        Updated adversarial prompt

    Raises:
        HTTPException: If prompt not found or update fails
    """
    try:
        db = get_db()

        # Build update data (only include non-None fields)
        update_data = {}
        if prompt_data.category is not None:
            update_data["category"] = prompt_data.category
        if prompt_data.prompt is not None:
            update_data["prompt"] = prompt_data.prompt
        if prompt_data.expected_blocked is not None:
            update_data["expected_blocked"] = prompt_data.expected_blocked
        if prompt_data.severity is not None:
            update_data["severity"] = prompt_data.severity

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        result = db.table("adversarial_prompts").update(update_data).eq("id", str(prompt_id)).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Prompt not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update prompt: {str(e)}")


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(prompt_id: UUID):
    """Delete an adversarial prompt.

    Args:
        prompt_id: UUID of the prompt to delete

    Raises:
        HTTPException: If prompt not found or deletion fails
    """
    try:
        db = get_db()

        result = db.table("adversarial_prompts").delete().eq("id", str(prompt_id)).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Prompt not found")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete prompt: {str(e)}")


@router.get("/categories/list")
async def get_categories():
    """Get list of available categories.

    Returns:
        List of category names
    """
    return {
        "categories": [
            "jailbreak",
            "injection",
            "harmful",
            "manipulation",
            "encoding",
        ]
    }


@router.get("/severity/list")
async def get_severity_levels():
    """Get list of available severity levels.

    Returns:
        List of severity levels
    """
    return {
        "severity_levels": [
            "low",
            "medium",
            "high",
        ]
    }


# Incidents endpoints
@router.get("/incidents/", response_model=List[Incident])
async def get_incidents(
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get list of security incidents.

    Args:
        severity: Filter by severity level
        limit: Number of results to return
        offset: Number of results to skip

    Returns:
        List of incidents

    Raises:
        HTTPException: If query fails
    """
    try:
        db = get_db()
        query = db.table("incidents").select("*")

        # Apply filters
        if severity:
            query = query.eq("severity", severity)

        # Order by most recent first
        query = query.order("created_at", desc=True)

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        result = query.execute()
        return result.data or []

    except Exception as e:
        logger.error(f"Error fetching incidents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch incidents: {str(e)}")


@router.get("/incidents/{incident_id}", response_model=Incident)
async def get_incident(incident_id: UUID):
    """Get details of a specific incident.

    Args:
        incident_id: UUID of the incident

    Returns:
        Incident details

    Raises:
        HTTPException: If incident not found
    """
    try:
        db = get_db()
        result = db.table("incidents").select("*").eq("id", str(incident_id)).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Incident not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching incident: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch incident: {str(e)}")
