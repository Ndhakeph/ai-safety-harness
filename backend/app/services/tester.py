"""Test runner service for executing adversarial tests against AI models."""

import os
import logging
from typing import Optional
from uuid import UUID

import google.generativeai as genai
from dotenv import load_dotenv

from ..models.schemas import (
    TestRunCreate,
    TestRunResponse,
    GuardrailResult,
)
from ..db import get_db
from .guardrails import get_guardrail_service
from .scorer import get_safety_scorer

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRunner:
    """Service for running adversarial tests against AI models."""

    def __init__(self):
        """Initialize test runner with Gemini API."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be set in environment variables")

        genai.configure(api_key=api_key)
        self.guardrail_service = get_guardrail_service()
        self.scorer = get_safety_scorer()

    async def run_test(self, test_data: TestRunCreate) -> TestRunResponse:
        """Run a single adversarial test.

        Args:
            test_data: Test configuration

        Returns:
            TestRunResponse with results

        Raises:
            Exception: If test execution fails
        """
        logger.info(f"Running test with prompt: {test_data.input_prompt[:50]}...")

        # Step 1: Pre-guardrail check
        pre_guardrail = self.guardrail_service.check_input(test_data.input_prompt)
        logger.info(f"Pre-guardrail check: blocked={pre_guardrail.blocked}, rules={len(pre_guardrail.triggered_rules)}")

        model_response = None
        post_guardrail = None
        jailbreak_successful = False

        # Step 2: If not blocked, send to model
        if not pre_guardrail.blocked:
            try:
                model_response = await self._query_model(
                    test_data.input_prompt,
                    test_data.model_used
                )
                logger.info(f"Model response length: {len(model_response) if model_response else 0}")

                # Step 3: Post-guardrail check on response
                if model_response:
                    post_guardrail = self.guardrail_service.check_output(
                        model_response,
                        test_data.input_prompt
                    )
                    logger.info(f"Post-guardrail check: blocked={post_guardrail.blocked}, rules={len(post_guardrail.triggered_rules)}")

            except Exception as e:
                logger.error(f"Error querying model: {str(e)}")
                model_response = f"Error: {str(e)}"
                post_guardrail = GuardrailResult(
                    blocked=False,
                    triggered_rules=["model_error"],
                    confidence=0.0,
                    reason="Model query failed"
                )

        # Step 4: Determine jailbreak success
        jailbreak_successful = self.scorer.determine_jailbreak_success(
            pre_guardrail,
            post_guardrail,
            model_response
        )
        logger.info(f"Jailbreak successful: {jailbreak_successful}")

        # Step 5: Calculate safety score
        safety_score = self.scorer.calculate_safety_score(
            pre_guardrail,
            post_guardrail,
            jailbreak_successful
        )
        logger.info(f"Safety score: {safety_score}")

        # Step 6: Save to database
        test_run = await self._save_test_run(
            test_data=test_data,
            pre_guardrail=pre_guardrail,
            post_guardrail=post_guardrail,
            model_response=model_response,
            jailbreak_successful=jailbreak_successful,
            safety_score=safety_score,
        )

        # Step 7: Create incident if needed
        incident_severity = self.scorer.determine_incident_severity(
            jailbreak_successful,
            safety_score,
            pre_guardrail,
            post_guardrail,
        )

        if incident_severity:
            await self._create_incident(
                test_run_id=test_run["id"],
                severity=incident_severity,
                input_prompt=test_data.input_prompt,
                model_response=model_response,
                pre_guardrail=pre_guardrail,
                post_guardrail=post_guardrail,
                jailbreak_successful=jailbreak_successful,
            )
            logger.info(f"Created incident with severity: {incident_severity}")

        return TestRunResponse(
            id=test_run["id"],
            prompt_id=test_data.prompt_id,
            input_prompt=test_data.input_prompt,
            pre_guardrail_blocked=pre_guardrail.blocked,
            pre_guardrail_rules=pre_guardrail.triggered_rules,
            model_response=model_response,
            post_guardrail_blocked=post_guardrail.blocked if post_guardrail else False,
            post_guardrail_rules=post_guardrail.triggered_rules if post_guardrail else [],
            jailbreak_successful=jailbreak_successful,
            safety_score=safety_score,
            model_used=test_data.model_used,
            created_at=test_run["created_at"],
        )

    async def _query_model(self, prompt: str, model_name: str) -> str:
        """Query the AI model with the given prompt.

        Args:
            prompt: Input prompt
            model_name: Model to use (e.g., 'gemini-pro')

        Returns:
            Model's response text

        Raises:
            Exception: If model query fails
        """
        try:
            model = genai.GenerativeModel(model_name)

            # Configure generation with safety settings at lowest (to test guardrails)
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )

            # Set safety settings to BLOCK_NONE to test our own guardrails
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                },
            ]

            response = model.generate_content(
                prompt,
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            # Handle blocked responses
            if not response.text:
                if hasattr(response, 'prompt_feedback'):
                    return f"Model blocked: {response.prompt_feedback}"
                return "Model returned empty response"

            return response.text

        except Exception as e:
            logger.error(f"Error in _query_model: {str(e)}")
            raise

    async def _save_test_run(
        self,
        test_data: TestRunCreate,
        pre_guardrail: GuardrailResult,
        post_guardrail: Optional[GuardrailResult],
        model_response: Optional[str],
        jailbreak_successful: bool,
        safety_score: int,
    ) -> dict:
        """Save test run to database.

        Args:
            test_data: Original test data
            pre_guardrail: Pre-check result
            post_guardrail: Post-check result
            model_response: Model's response
            jailbreak_successful: Whether jailbreak succeeded
            safety_score: Calculated safety score

        Returns:
            Saved test run record

        Raises:
            Exception: If database save fails
        """
        db = get_db()

        data = {
            "prompt_id": str(test_data.prompt_id) if test_data.prompt_id else None,
            "input_prompt": test_data.input_prompt,
            "pre_guardrail_blocked": pre_guardrail.blocked,
            "pre_guardrail_rules": pre_guardrail.triggered_rules,
            "model_response": model_response,
            "post_guardrail_blocked": post_guardrail.blocked if post_guardrail else False,
            "post_guardrail_rules": post_guardrail.triggered_rules if post_guardrail else [],
            "jailbreak_successful": jailbreak_successful,
            "safety_score": safety_score,
            "model_used": test_data.model_used,
        }

        result = db.table("test_runs").insert(data).execute()

        if not result.data or len(result.data) == 0:
            raise Exception("Failed to save test run to database")

        return result.data[0]

    async def _create_incident(
        self,
        test_run_id: str,
        severity: str,
        input_prompt: str,
        model_response: Optional[str],
        pre_guardrail: GuardrailResult,
        post_guardrail: Optional[GuardrailResult],
        jailbreak_successful: bool,
    ) -> None:
        """Create an incident record.

        Args:
            test_run_id: ID of the test run
            severity: Incident severity
            input_prompt: Original input
            model_response: Model's response
            pre_guardrail: Pre-check result
            post_guardrail: Post-check result
            jailbreak_successful: Whether jailbreak succeeded
        """
        db = get_db()

        description = self.scorer.generate_incident_description(
            input_prompt,
            model_response,
            pre_guardrail,
            post_guardrail,
            jailbreak_successful,
        )

        data = {
            "test_run_id": test_run_id,
            "severity": severity,
            "description": description,
        }

        db.table("incidents").insert(data).execute()


# Global instance
_test_runner = None


def get_test_runner() -> TestRunner:
    """Get or create test runner instance.

    Returns:
        TestRunner instance
    """
    global _test_runner
    if _test_runner is None:
        _test_runner = TestRunner()
    return _test_runner
