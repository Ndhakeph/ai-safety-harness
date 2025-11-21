"""API routes for fetching test results and metrics."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from ..models.schemas import (
    TestRunResponse,
    SafetyMetrics,
    SafetyScoreTimeSeries,
    CategoryBreakdown,
    Incident,
)
from ..db import get_db

router = APIRouter(prefix="/api/results", tags=["results"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[TestRunResponse])
async def get_results(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    jailbreak_successful: Optional[bool] = None,
    min_safety_score: Optional[int] = Query(None, ge=0, le=100),
    max_safety_score: Optional[int] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get test results with optional filters.

    Args:
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)
        category: Filter by prompt category
        jailbreak_successful: Filter by jailbreak success
        min_safety_score: Minimum safety score
        max_safety_score: Maximum safety score
        limit: Number of results to return
        offset: Number of results to skip

    Returns:
        List of test results

    Raises:
        HTTPException: If query fails
    """
    try:
        db = get_db()
        query = db.table("test_runs").select("*")

        # Apply filters
        if start_date:
            query = query.gte("created_at", start_date)
        if end_date:
            query = query.lte("created_at", end_date)
        if jailbreak_successful is not None:
            query = query.eq("jailbreak_successful", jailbreak_successful)
        if min_safety_score is not None:
            query = query.gte("safety_score", min_safety_score)
        if max_safety_score is not None:
            query = query.lte("safety_score", max_safety_score)

        # Order by most recent first
        query = query.order("created_at", desc=True)

        # Apply pagination
        query = query.range(offset, offset + limit - 1)

        result = query.execute()

        # If category filter is specified, we need to join with prompts
        # For simplicity, we'll post-filter here
        results = result.data or []

        if category:
            # Fetch prompt IDs for the category
            prompt_result = db.table("adversarial_prompts").select("id").eq("category", category).execute()
            if prompt_result.data:
                category_prompt_ids = {str(p["id"]) for p in prompt_result.data}
                results = [r for r in results if r.get("prompt_id") in category_prompt_ids]

        return results

    except Exception as e:
        logger.error(f"Error fetching results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch results: {str(e)}")


@router.get("/{test_id}", response_model=TestRunResponse)
async def get_result_detail(test_id: UUID):
    """Get detailed results for a specific test run.

    Args:
        test_id: UUID of the test run

    Returns:
        Detailed test run results

    Raises:
        HTTPException: If test not found
    """
    try:
        db = get_db()
        result = db.table("test_runs").select("*").eq("id", str(test_id)).execute()

        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Test run not found")

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching test detail: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch test detail: {str(e)}")


@router.get("/metrics/summary", response_model=SafetyMetrics)
async def get_metrics_summary():
    """Get overall safety metrics summary.

    Returns:
        SafetyMetrics with aggregated statistics

    Raises:
        HTTPException: If metrics calculation fails
    """
    try:
        db = get_db()

        # Get all test runs
        all_tests = db.table("test_runs").select("*").execute()
        tests = all_tests.data or []

        # Get tests from today
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time()).isoformat()

        today_tests_result = db.table("test_runs").select("*").gte("created_at", today_start).execute()
        today_tests = today_tests_result.data or []

        # Get all incidents
        incidents_result = db.table("incidents").select("*").execute()
        incidents = incidents_result.data or []

        # Get today's incidents
        today_incidents = [
            i for i in incidents
            if datetime.fromisoformat(i["created_at"].replace("Z", "+00:00")).date() == today
        ]

        # Calculate metrics
        total_tests = len(tests)
        tests_today = len(today_tests)

        if total_tests > 0:
            jailbreak_successes = sum(1 for t in tests if t.get("jailbreak_successful", False))
            jailbreak_success_rate = (jailbreak_successes / total_tests) * 100

            guardrail_triggers = sum(
                1 for t in tests
                if t.get("pre_guardrail_blocked", False) or t.get("post_guardrail_blocked", False)
            )
            guardrail_trigger_rate = (guardrail_triggers / total_tests) * 100

            # False positive: expected_blocked=false but was blocked
            # We'd need to join with prompts table for this - simplified here
            false_positive_rate = 5.0  # Placeholder

            safety_scores = [t.get("safety_score", 0) for t in tests]
            average_safety_score = sum(safety_scores) / len(safety_scores) if safety_scores else 0

        else:
            jailbreak_success_rate = 0.0
            guardrail_trigger_rate = 0.0
            false_positive_rate = 0.0
            average_safety_score = 0.0

        return SafetyMetrics(
            total_tests=total_tests,
            tests_today=tests_today,
            jailbreak_success_rate=round(jailbreak_success_rate, 2),
            guardrail_trigger_rate=round(guardrail_trigger_rate, 2),
            false_positive_rate=round(false_positive_rate, 2),
            average_safety_score=round(average_safety_score, 2),
            active_incidents=len(incidents),
            incidents_today=len(today_incidents),
        )

    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate metrics: {str(e)}")


@router.get("/metrics/timeseries", response_model=List[SafetyScoreTimeSeries])
async def get_timeseries_data(days: int = Query(7, ge=1, le=90)):
    """Get safety score time series data.

    Args:
        days: Number of days to include

    Returns:
        List of daily safety scores

    Raises:
        HTTPException: If query fails
    """
    try:
        db = get_db()

        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Fetch tests in range
        result = db.table("test_runs").select("created_at, safety_score").gte(
            "created_at", start_date.isoformat()
        ).execute()

        tests = result.data or []

        # Group by date
        daily_data = {}
        for test in tests:
            test_date = datetime.fromisoformat(test["created_at"].replace("Z", "+00:00")).date()
            date_str = test_date.isoformat()

            if date_str not in daily_data:
                daily_data[date_str] = {"scores": [], "count": 0}

            daily_data[date_str]["scores"].append(test.get("safety_score", 0))
            daily_data[date_str]["count"] += 1

        # Calculate averages
        timeseries = []
        for date_str, data in sorted(daily_data.items()):
            avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            timeseries.append(
                SafetyScoreTimeSeries(
                    date=date_str,
                    average_score=round(avg_score, 2),
                    test_count=data["count"],
                )
            )

        return timeseries

    except Exception as e:
        logger.error(f"Error fetching timeseries: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch timeseries: {str(e)}")


@router.get("/metrics/categories", response_model=List[CategoryBreakdown])
async def get_category_breakdown():
    """Get breakdown of metrics by category.

    Returns:
        List of category-wise metrics

    Raises:
        HTTPException: If query fails
    """
    try:
        db = get_db()

        # Fetch all prompts
        prompts_result = db.table("adversarial_prompts").select("*").execute()
        prompts = {p["id"]: p for p in (prompts_result.data or [])}

        # Fetch all test runs
        tests_result = db.table("test_runs").select("*").execute()
        tests = tests_result.data or []

        # Group by category
        category_data = {}
        categories = ["jailbreak", "injection", "harmful", "manipulation", "encoding"]

        for category in categories:
            category_data[category] = {
                "total": 0,
                "jailbreaks": 0,
                "scores": [],
            }

        for test in tests:
            prompt_id = test.get("prompt_id")
            if prompt_id and prompt_id in prompts:
                category = prompts[prompt_id].get("category")
                if category in category_data:
                    category_data[category]["total"] += 1
                    if test.get("jailbreak_successful", False):
                        category_data[category]["jailbreaks"] += 1
                    category_data[category]["scores"].append(test.get("safety_score", 0))

        # Calculate metrics
        breakdown = []
        for category, data in category_data.items():
            if data["total"] > 0:
                jailbreak_rate = (data["jailbreaks"] / data["total"]) * 100
                avg_score = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0
            else:
                jailbreak_rate = 0.0
                avg_score = 0.0

            breakdown.append(
                CategoryBreakdown(
                    category=category,
                    total_tests=data["total"],
                    jailbreak_success_rate=round(jailbreak_rate, 2),
                    average_safety_score=round(avg_score, 2),
                )
            )

        return breakdown

    except Exception as e:
        logger.error(f"Error fetching category breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch category breakdown: {str(e)}")
