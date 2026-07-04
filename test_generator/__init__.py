"""
Public Testing Automation System Package Entry point.

Exposes only explicit structural definitions required for standard usage patterns.
"""

from test_generator.models import GeneratedTest
from test_generator.manager import TestGenerationManager

__all__ = ["GeneratedTest", "TestGenerationManager"]