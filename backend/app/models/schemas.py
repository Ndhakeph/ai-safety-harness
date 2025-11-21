"""Pydantic models and schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


# Adversarial Prompt Models
class AdversarialPromptBase(BaseModel):
    """Base schema for adversarial prompts."""

    category: Literal["jailbreak", "injection", "harmful", "manipulation", "encoding"]
    prompt: str = Field(..., min_length=1, max_length=5000)
    expected_blocked: bool = True
    severity: Literal["low", "medium", "high"]


class AdversarialPromptCreate(AdversarialPromptBase):
    """Schema for creating a new adversarial prompt."""

    pass


class AdversarialPromptUpdate(BaseModel):
    """Schema for updating an adversarial prompt."""

    category: Optional[Literal["jailbreak", "injection", "harmful", "manipulation", "encoding"]] = None
    prompt: Optional[str] = Field(None, min_length=1, max_length=5000)
    expected_blocked: Optional[bool] = None
    severity: Optional[Literal["low", "medium", "high"]] = None


class AdversarialPrompt(AdversarialPromptBase):
    """Schema for adversarial prompt response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Guardrail Models
class GuardrailResult(BaseModel):
    """Result from guardrail check."""

    blocked: bool
    triggered_rules: List[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: Optional[str] = None


# Test Run Models
class TestRunCreate(BaseModel):
    """Schema for creating a new test run."""

    prompt_id: Optional[UUID] = None
    input_prompt: str = Field(..., min_length=1)
    model_used: str = "gemini-pro"


class BatchTestRunCreate(BaseModel):
    """Schema for creating batch test runs."""

    category: Optional[Literal["jailbreak", "injection", "harmful", "manipulation", "encoding"]] = None
    prompt_ids: Optional[List[UUID]] = None
    model_used: str = "gemini-pro"


class TestRunResponse(BaseModel):
    """Schema for test run response."""

    id: UUID
    prompt_id: Optional[UUID]
    input_prompt: str
    pre_guardrail_blocked: bool
    pre_guardrail_rules: List[str]
    model_response: Optional[str]
    post_guardrail_blocked: bool
    post_guardrail_rules: List[str]
    jailbreak_successful: bool
    safety_score: int = Field(..., ge=0, le=100)
    model_used: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchTestRunResponse(BaseModel):
    """Schema for batch test run response."""

    total_tests: int
    completed: int
    results: List[TestRunResponse]


# Incident Models
class IncidentCreate(BaseModel):
    """Schema for creating an incident."""

    test_run_id: UUID
    severity: Literal["low", "medium", "high", "critical"]
    description: str = Field(..., min_length=1)


class Incident(IncidentCreate):
    """Schema for incident response."""

    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Metrics Models
class SafetyMetrics(BaseModel):
    """Schema for safety metrics summary."""

    total_tests: int
    tests_today: int
    jailbreak_success_rate: float = Field(..., ge=0.0, le=100.0)
    guardrail_trigger_rate: float = Field(..., ge=0.0, le=100.0)
    false_positive_rate: float = Field(..., ge=0.0, le=100.0)
    average_safety_score: float = Field(..., ge=0.0, le=100.0)
    active_incidents: int
    incidents_today: int


class SafetyScoreTimeSeries(BaseModel):
    """Schema for safety score over time."""

    date: str
    average_score: float
    test_count: int


class CategoryBreakdown(BaseModel):
    """Schema for category-wise breakdown."""

    category: str
    total_tests: int
    jailbreak_success_rate: float
    average_safety_score: float


# Filter Models
class TestRunFilters(BaseModel):
    """Schema for filtering test runs."""

    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[Literal["jailbreak", "injection", "harmful", "manipulation", "encoding"]] = None
    jailbreak_successful: Optional[bool] = None
    min_safety_score: Optional[int] = Field(None, ge=0, le=100)
    max_safety_score: Optional[int] = Field(None, ge=0, le=100)
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)


# Health Check
class HealthCheck(BaseModel):
    """Schema for health check response."""

    status: str
    timestamp: datetime
    version: str = "1.0.0"
