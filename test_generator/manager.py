"""
Centralized Test Generation Facade Client.

Coordinates execution steps across processing systems and persistence layers
using clean encapsulation.
"""

from typing import Any
from test_generator.models import GeneratedTest
from test_generator.generator import TestGenerator
from test_generator.writer import TestWriter


class TestGenerationManager:
    # Tell pytest explicitly to ignore this class for test collection
    __test__ = False

    """
    High-level transaction system orchestrating isolated internal engine modules.
    """

    def __init__(self, tests_directory: str = "tests"):
        self._generator = TestGenerator()
        self._writer = TestWriter(base_tests_dir=tests_directory)

    def generate(self, module_info: Any) -> GeneratedTest:
        """Processes and returns intermediate in-memory testing model configurations."""
        return self._generator.generate_test_suite(module_info)

    def generate_and_save(self, module_info: Any) -> str | None:
        """Compiles standard unit templates and safely commits them onto system storage tracks."""
        generated_test = self.generate(module_info)
        return self._writer.write_test_to_disk(generated_test)