"""LLM Subsystem Package for the AI Code Auto Fixer.

This package provides a resilient interface for integrating localized language models
into the automated fixing pipeline. It exposes a low-level client for model connectivity
and a high-level manager facade for orchestrating patch generation, parsing, and guardrails.
"""

from llm.client import LLMClient
from llm.manager import LLMManager

__all__ = [
    "LLMClient",
    "LLMManager",
]