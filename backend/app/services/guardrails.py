"""Guardrail detection service for identifying jailbreaks and harmful content."""

import re
from typing import List, Tuple
from ..models.schemas import GuardrailResult


class GuardrailService:
    """Service for detecting adversarial prompts and harmful content."""

    # Jailbreak patterns
    JAILBREAK_PATTERNS = [
        r"ignore\s+(?:all\s+)?(?:previous|prior|your)\s+(?:instructions|prompts|rules|directives)",
        r"disregard\s+(?:your\s+)?(?:programming|instructions|rules|guidelines)",
        r"you\s+are\s+now\s+(?:in\s+)?(?:DAN|developer)\s+mode",
        r"pretend\s+(?:you\s+are|to\s+be)\s+(?:an?\s+)?(?:AI|assistant|chatbot)?\s*(?:with|without|that|who)",
        r"act\s+as\s+(?:if|though|an?)\s+(?:you|we|there)",
        r"new\s+(?:role|character|personality|mode)",
        r"jailbreak|bypass\s+(?:filters|restrictions|safety)",
        r"unrestricted\s+(?:AI|mode|assistant)",
        r"without\s+(?:any\s+)?(?:restrictions|limits|filters|rules|ethics)",
        r"no\s+(?:ethical|moral|safety)\s+(?:guidelines|restrictions|rules)",
    ]

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"(?:system|admin|root)(?:\s*:|::|>|>>)\s*(?:new|override|execute)",
        r"\{\{(?:system|admin|config)\}\}",
        r"reveal\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions|message|config)",
        r"print\s+(?:the\s+)?(?:exact\s+)?(?:text|content|instructions)",
        r"what\s+(?:are|were)\s+(?:your\s+)?(?:secret|hidden|initial)\s+instructions",
        r"repeat\s+(?:the\s+)?(?:hidden|secret|system)\s+(?:prompt|instructions|message)",
        r"execute\s+(?:the\s+following|this|as)\s+(?:a\s+)?(?:system|admin)?\s*command",
        r"override\s+(?:previous|all)\s+(?:directives|instructions|commands)",
    ]

    # Harmful content keywords
    HARMFUL_KEYWORDS = [
        "bomb", "explosive", "weapon", "malware", "virus", "hack", "hacking",
        "phishing", "steal", "illegal", "drugs", "poison", "kill", "murder",
        "suicide", "self-harm", "abuse", "trafficking", "fraud", "scam",
        "credentials", "password", "bypass security", "break into",
        "fake id", "counterfeit", "laundering", "ransomware",
    ]

    # Role manipulation patterns
    ROLE_MANIPULATION_PATTERNS = [
        r"you\s+are\s+(?:now\s+)?(?:an?|the)\s+(?:evil|bad|malicious|unrestricted|unfiltered)",
        r"from\s+now\s+on,?\s+(?:act|behave|respond)\s+as",
        r"roleplay\s+as\s+(?:an?|the)",
        r"pretend\s+(?:that\s+)?this\s+is\s+(?:a|an)\s+(?:movie|game|simulation|test)",
        r"for\s+(?:research|educational)\s+purposes?,?\s+(?:provide|explain|describe)",
        r"in\s+(?:this|a)\s+(?:hypothetical|fictional)\s+scenario",
    ]

    # Encoding patterns
    ENCODING_PATTERNS = [
        r"base64|b64|decode",
        r"rot13|caesar\s+cipher",
        r"[a-zA-Z0-9+/]{20,}={0,2}",  # Base64-like strings
        r"(?:[a-z]-){3,}",  # Hyphen-separated letters
        r"\\x[0-9a-fA-F]{2}",  # Hex encoding
        r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",  # IP addresses (can be used for obfuscation)
    ]

    # Refusal indicators (signs that the model properly refused)
    REFUSAL_INDICATORS = [
        r"I (?:cannot|can't|won't|shouldn't|must not)",
        r"I'm (?:not able|unable|sorry|afraid)",
        r"I (?:don't|do not) (?:feel comfortable|think it's appropriate)",
        r"(?:that|this) (?:would be|is) (?:harmful|dangerous|unethical|illegal|inappropriate)",
        r"I'm designed to be (?:helpful|harmless|honest)",
        r"I (?:don't|do not) have the ability to",
        r"against my (?:guidelines|principles|programming|values)",
        r"I (?:must|should|need to) (?:decline|refuse)",
    ]

    def __init__(self):
        """Initialize the guardrail service with compiled patterns."""
        self.jailbreak_regex = [re.compile(p, re.IGNORECASE) for p in self.JAILBREAK_PATTERNS]
        self.injection_regex = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        self.role_manipulation_regex = [re.compile(p, re.IGNORECASE) for p in self.ROLE_MANIPULATION_PATTERNS]
        self.encoding_regex = [re.compile(p, re.IGNORECASE) for p in self.ENCODING_PATTERNS]
        self.refusal_regex = [re.compile(p, re.IGNORECASE) for p in self.REFUSAL_INDICATORS]

    def check_input(self, text: str) -> GuardrailResult:
        """Check input text against guardrail patterns.

        Args:
            text: Input text to check

        Returns:
            GuardrailResult with detection results
        """
        triggered_rules = []
        confidence_scores = []

        # Check jailbreak patterns
        jailbreak_matches = self._check_patterns(text, self.jailbreak_regex, "jailbreak")
        if jailbreak_matches:
            triggered_rules.extend(jailbreak_matches)
            confidence_scores.append(0.9)

        # Check injection patterns
        injection_matches = self._check_patterns(text, self.injection_regex, "prompt_injection")
        if injection_matches:
            triggered_rules.extend(injection_matches)
            confidence_scores.append(0.85)

        # Check harmful keywords
        harmful_matches = self._check_keywords(text, self.HARMFUL_KEYWORDS, "harmful_content")
        if harmful_matches:
            triggered_rules.extend(harmful_matches)
            confidence_scores.append(0.7)

        # Check role manipulation
        role_matches = self._check_patterns(text, self.role_manipulation_regex, "role_manipulation")
        if role_matches:
            triggered_rules.extend(role_matches)
            confidence_scores.append(0.8)

        # Check encoding tricks
        encoding_matches = self._check_patterns(text, self.encoding_regex, "encoding_trick")
        if encoding_matches:
            triggered_rules.extend(encoding_matches)
            confidence_scores.append(0.75)

        # Calculate overall confidence
        blocked = len(triggered_rules) > 0
        confidence = max(confidence_scores) if confidence_scores else 0.0

        reason = None
        if blocked:
            reason = f"Detected {len(triggered_rules)} potential threats"

        return GuardrailResult(
            blocked=blocked,
            triggered_rules=triggered_rules,
            confidence=confidence,
            reason=reason,
        )

    def check_output(self, text: str, input_prompt: str) -> GuardrailResult:
        """Check output text for harmful content or jailbreak success.

        Args:
            text: Output text to check
            input_prompt: Original input prompt for context

        Returns:
            GuardrailResult with detection results
        """
        triggered_rules = []
        confidence_scores = []

        # Check if model properly refused
        refusal_found = any(pattern.search(text) for pattern in self.refusal_regex)

        if refusal_found:
            # Model properly refused, this is good
            return GuardrailResult(
                blocked=False,
                triggered_rules=["proper_refusal"],
                confidence=0.9,
                reason="Model appropriately refused the request",
            )

        # Check for harmful content in response
        harmful_matches = self._check_keywords(text, self.HARMFUL_KEYWORDS, "harmful_output")
        if harmful_matches:
            triggered_rules.extend(harmful_matches)
            confidence_scores.append(0.85)

        # Check if response suggests compliance with harmful request
        compliance_patterns = [
            r"(?:here|this)\s+is\s+(?:how|a\s+(?:guide|method|way))",
            r"(?:step|steps)\s+(?:to|for)\s+(?:make|create|build|develop)",
            r"you\s+(?:can|could|should|would)\s+(?:use|try|do|follow)",
            r"(?:first|next|then|finally),?\s+(?:you\s+)?(?:need|should|must|can)",
        ]

        for pattern_str in compliance_patterns:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            if pattern.search(text):
                triggered_rules.append("compliance_detected")
                confidence_scores.append(0.8)
                break

        # Check for length - very short responses might indicate refusal
        if len(text.strip()) < 50:
            confidence_scores.append(0.3)  # Lower confidence for short responses

        blocked = len(triggered_rules) > 0
        confidence = max(confidence_scores) if confidence_scores else 0.0

        reason = None
        if blocked:
            reason = f"Response appears to comply with adversarial request"

        return GuardrailResult(
            blocked=blocked,
            triggered_rules=triggered_rules,
            confidence=confidence,
            reason=reason,
        )

    def _check_patterns(self, text: str, patterns: List[re.Pattern], rule_type: str) -> List[str]:
        """Check text against compiled regex patterns.

        Args:
            text: Text to check
            patterns: List of compiled regex patterns
            rule_type: Type of rule being checked

        Returns:
            List of triggered rule names
        """
        matches = []
        for i, pattern in enumerate(patterns):
            if pattern.search(text):
                matches.append(f"{rule_type}_{i+1}")
        return matches

    def _check_keywords(self, text: str, keywords: List[str], rule_type: str) -> List[str]:
        """Check text for harmful keywords.

        Args:
            text: Text to check
            keywords: List of keywords to check for
            rule_type: Type of rule being checked

        Returns:
            List of triggered rule names with matched keywords
        """
        text_lower = text.lower()
        matches = []

        for keyword in keywords:
            # Use word boundaries to avoid false positives
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            if pattern.search(text):
                matches.append(f"{rule_type}:{keyword}")

        return matches


# Global instance
_guardrail_service = None


def get_guardrail_service() -> GuardrailService:
    """Get or create guardrail service instance.

    Returns:
        GuardrailService instance
    """
    global _guardrail_service
    if _guardrail_service is None:
        _guardrail_service = GuardrailService()
    return _guardrail_service
