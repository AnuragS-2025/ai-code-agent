"""
Test Generation System Immutable Models.

Provides safe, hashable structural components used for transferring state details
across the automated test file creation process.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedTest:
    """
    An immutable structure detailing a compiled test component.

    Attributes:
        module (str): Name of the underlying module being analyzed.
        test_name (str): Deterministic target filename for the test module.
        content (str): The completely formatted plaintext source string.
        target_file (str): Absolute file location profile of the module under analysis.
    """
    module: str
    test_name: str
    content: str
    target_file: str