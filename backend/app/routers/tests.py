"""API routes for running adversarial tests."""

import logging
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, BackgroundTasks

from ..models.schemas import (
    TestRunCreate,
    TestRunResponse,
    BatchTestRunCreate,
    BatchTestRunResponse,
)
from ..services import get_test_runner
from ..db import get_db

router = APIRouter(prefix="/api/test", tags=["tests"])
logger = logging.getLogger(__name__)


@router.post("/run", response_model=TestRunResponse)
async def run_single_test(test_data: TestRunCreate) -> TestRunResponse:
    """Run a single adversarial test.

    Args:
        test_data: Test configuration

    Returns:
        TestRunResponse with results

    Raises:
        HTTPException: If test execution fails
    """
    try:
        test_runner = get_test_runner()
        result = await test_runner.run_test(test_data)
        return result
    except Exception as e:
        logger.error(f"Error running test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")


@router.post("/batch", response_model=BatchTestRunResponse)
async def run_batch_tests(batch_data: BatchTestRunCreate) -> BatchTestRunResponse:
    """Run batch adversarial tests.

    Args:
        batch_data: Batch test configuration (by category or specific prompt IDs)

    Returns:
        BatchTestRunResponse with all results

    Raises:
        HTTPException: If batch test execution fails
    """
    try:
        db = get_db()
        test_runner = get_test_runner()

        # Fetch prompts based on criteria
        query = db.table("adversarial_prompts").select("*")

        if batch_data.category:
            query = query.eq("category", batch_data.category)
        elif batch_data.prompt_ids:
            # Convert UUIDs to strings for query
            prompt_ids_str = [str(pid) for pid in batch_data.prompt_ids]
            query = query.in_("id", prompt_ids_str)
        else:
            raise HTTPException(
                status_code=400,
                detail="Must specify either category or prompt_ids"
            )

        result = query.execute()

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="No prompts found matching criteria"
            )

        prompts = result.data
        logger.info(f"Running batch test with {len(prompts)} prompts")

        # Run tests for each prompt
        results = []
        completed = 0

        for prompt in prompts:
            try:
                test_data = TestRunCreate(
                    prompt_id=prompt["id"],
                    input_prompt=prompt["prompt"],
                    model_used=batch_data.model_used,
                )

                test_result = await test_runner.run_test(test_data)
                results.append(test_result)
                completed += 1

            except Exception as e:
                logger.error(f"Error running test for prompt {prompt['id']}: {str(e)}")
                # Continue with other tests even if one fails

        return BatchTestRunResponse(
            total_tests=len(prompts),
            completed=completed,
            results=results,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running batch tests: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch test execution failed: {str(e)}"
        )


@router.get("/status/{test_id}")
async def get_test_status(test_id: UUID):
    """Get the status of a specific test run.

    Args:
        test_id: UUID of the test run

    Returns:
        Test run details

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
        logger.error(f"Error fetching test status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch test status: {str(e)}")
