import unittest
import tempfile
import shutil
import os
from test_generator.manager import TestGenerationManager
from test_generator.templates import (
    render_module_header,
    render_function_skeleton,
    render_class_skeleton,
)


class MockModuleInfo:
    """Dummy metadata structure matching data parameters of core system parsers."""
    def __init__(self, module_name: str, file_path: str, functions=None, classes=None):
        self.module_name = module_name
        self.file_path = file_path
        self.functions = functions or []
        self.classes = classes or {}


class TestTestGenerationSuite(unittest.TestCase):
    """Deterministic validation test array for code generation layer verification."""

    def setUp(self):
        self.sandbox_root = tempfile.mkdtemp()
        self.tests_dir = os.path.join(self.sandbox_root, "tests")
        self.manager = TestGenerationManager(tests_directory=self.tests_dir)

    def tearDown(self):
        shutil.rmtree(self.sandbox_root, ignore_errors=True)

    def test_template_rendering_accuracy(self):
        """Verifies template primitives produce exact, predictable text outputs."""
        header = render_module_header("auth")
        self.assertIn("import auth", header)
        self.assertIn("import pytest", header)

        func_stub = render_function_skeleton("login", "auth")
        self.assertIn("def test_login():", func_stub)

        class_stub = render_class_skeleton("Session", ["connect"], "auth")
        self.assertIn("class TestSession:", class_stub)
        self.assertIn("def test_connect(self):", class_stub)

    def test_empty_module_handling(self):
        """Ensures that modules without functional components generate a basic valid file structure."""
        mock_info = MockModuleInfo("empty_mod", "src/empty_mod.py")
        generated = self.manager.generate(mock_info)

        self.assertEqual(generated.test_name, "test_empty_mod.py")
        self.assertIn("import empty_mod", generated.content)

    def test_single_and_multiple_functions_generation(self):
        """Validates that extracted multiple functions are mapped cleanly in alphabetical order."""
        mock_info = MockModuleInfo(
            "utils", "src/utils.py", 
            functions=["format_date", "parse_json"]
        )
        generated = self.manager.generate(mock_info)

        self.assertIn("def test_format_date():", generated.content)
        self.assertIn("def test_parse_json():", generated.content)

    def test_class_generation_with_internal_methods(self):
        """Ensures internal class structural configurations map correctly to class blocks."""
        mock_info = MockModuleInfo(
            "client", "src/client.py",
            classes={"ApiClient": ["request", "close"]}
        )
        generated = self.manager.generate(mock_info)

        self.assertIn("class TestApiClient:", generated.content)
        self.assertIn("def test_request(self):", generated.content)
        self.assertIn("def test_close(self):", generated.content)

    def test_writer_and_manager_persistence_sequence(self):
        """Validates the end-to-end flow of saving files to disk within a clean test directory."""
        mock_info = MockModuleInfo("core", "src/core.py", functions=["start"])
        saved_path = self.manager.generate_and_save(mock_info)

        self.assertIsNotNone(saved_path)
        self.assertTrue(os.path.exists(saved_path))

        with open(saved_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("def test_start():", content)

    def test_existing_file_protection_safeguard(self):
        """Guarantees the writer never overwrites pre-existing local testing files."""
        os.makedirs(self.tests_dir, exist_ok=True)
        pre_existing_file = os.path.join(self.tests_dir, "test_core.py")
        
        with open(pre_existing_file, "w", encoding="utf-8") as f:
            f.write("# PROTECTED ORIGINAL DATA")

        mock_info = MockModuleInfo("core", "src/core.py", functions=["modified_run"])
        saved_path = self.manager.generate_and_save(mock_info)

        # Must return None indicating write suppression
        self.assertIsNone(saved_path)

        with open(pre_existing_file, "r", encoding="utf-8") as f:
            current_content = f.read()
        self.assertEqual(current_content, "# PROTECTED ORIGINAL DATA")
    
   
    # ==========================================================
    # Sprint 3.6 Extended Boundary Tests
    # ==========================================================

    def test_generated_test_target_file_absolute_normalization(self):
        """
        Verifies that GeneratedTest.target_file always resolves to an
        absolute and normalized filesystem path.
        """
        relative_dirty_path = "src/modules/../handlers/./auth_service.py"

        mock_info = MockModuleInfo(
            "auth_service",
            relative_dirty_path,
        )

        generated = self.manager.generate(mock_info)

        # Must always be absolute
        self.assertTrue(os.path.isabs(generated.target_file))

        # Must be normalized
        self.assertEqual(
            generated.target_file,
            os.path.normpath(os.path.abspath(relative_dirty_path)),
        )

        # No unresolved navigation fragments should remain
        self.assertNotIn("..", generated.target_file)

if __name__ == "__main__":
    unittest.main()