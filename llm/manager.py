"""Module orchestrating the complete AI patch generation lifecycle.

This manager coordinates prompt construction, model inference execution, response parsing,
and validation guardrails to ensure only clean, bounded structural patches are returned
to the core auto-fix pipeline.
"""

import logging
from typing import Any, Mapping

from llm.client import LLMClient
from llm.prompts import build_patch_prompt
from llm.parser import clean_response
from llm.guardrails import validate_generated_patch

# Standard module-level logger
logger = logging.getLogger(__name__)


class LLMManager:
    """Orchestrates the entire execution flow for generating code patches via an LLM.

    This class serves as a unified facade, isolating external callers from the discrete
    steps of prompting, querying, parsing, and verifying generated output code.
    """

    def __init__(self, client: LLMClient | None = None) -> None:
        """Initializes the LLMManager with a shared or default LLM client instance.

        Args:
            client: An existing configured LLMClient instance. If None, a new
                default client will be initialized internally.
        """
        self.client = client if client is not None else LLMClient()

    def generate_patch(self, issue: Mapping[str, Any], code_block: str, context: str) -> str | None:
        """Runs the sequential pipeline to generate a verified fix patch for an issue.

        This method encapsulates all intermediate failures, structural rejections, and
        unexpected exceptions. It will never raise an error outside the manager layer,
        ensuring absolute stability of the main execution thread.

        Args:
            issue: A type-safe mapping containing static analysis engine diagnostics.
            code_block: The isolated raw code block identified as needing correction.
            context: Surrounding structural file context to assist systemic analysis.

        Returns:
            A clean, ready-to-apply string patch if all steps and guardrails pass;
            None if generation fails, crashes, or is rejected by safety guardrails.
        """
        rule = issue.get("rule", "Unknown-Rule")
        file_path = issue.get("file", "Unknown-File")
        
        logger.info(">>> [START] AI Fix Cycle | Rule: %s for File: %s", rule, file_path)

        try:
            # 1. Prompt Construction Phase
            logger.debug("Building specialized instruction prompt payload.")
            prompt = build_patch_prompt(issue, code_block, context)

            # 2. Inference Execution Phase
            logger.info("Dispatching patch request to the underlying LLM client.")
            raw_response = self.client.generate(prompt)

            if not raw_response:
                logger.warning("AI Fix Cycle Aborted: LLM returned an empty response.")
                return None

            # 3. Response Parsing and Normalization Phase
            logger.debug("Parsing raw response to strip markdown formatting/fences.")
            cleaned_patch = clean_response(raw_response)

            if not cleaned_patch:
                logger.warning("AI Fix Cycle Aborted: Parsed response code block is empty.")
                return None

            # 4. Guardrails Verification Phase
            logger.info("Enforcing local structural guardrail checks on the parsed patch.")
            is_valid, reason = validate_generated_patch(code_block, cleaned_patch)

            if not is_valid:
                logger.warning("AI Patch Rejected by Guardrails: %s", reason)
                return None

            # 5. Success Capture
            logger.info("<<< [END] AI Fix Cycle | Successfully generated valid patch block.")
            return cleaned_patch

        except Exception as exc:
            # Cleaned log message and standardized naming convention
            logger.exception("LLM patch generation failed: %s", str(exc))
            return None