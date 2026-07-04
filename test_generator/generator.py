"""
Core Test Generation Orchestrator.

Converts explicit incoming mockable ModuleInfo structures down into complete
plain-text GeneratedTest objects by inspecting isolated top-level blocks.
"""

import os
from typing import Any
from test_generator.models import GeneratedTest
from test_generator.templates import (
    render_module_header,
    render_function_skeleton,
    render_class_skeleton,
)


class TestGenerator:
    """
    Transforms system analytical node models into complete execution script stubs.
    """

    def generate_test_suite(self, module_info: Any) -> GeneratedTest:
        """
        Parses explicit targets inside ModuleInfo metadata structures without
        touching active hardware filesystems.
        """
        # Safely capture string module properties
        module_path = getattr(module_info, "file_path", "unknown_module.py")
        module_name = getattr(module_info, "module_name", "unknown_module")
        
        # Pull extracted parsing elements safely
        functions = getattr(module_info, "functions", [])
        classes = getattr(module_info, "classes", {})

        # 1. Base Framework Setup
        buffer = render_module_header(module_name)

        # 2. Extract Top-Level Plain Functions
        for func in sorted(functions):
            buffer += render_function_skeleton(func, module_name)

        # 3. Extract Top-Level Plain Classes
        for cls_name in sorted(classes.keys()):
            methods = classes[cls_name]
            buffer += render_class_skeleton(cls_name, sorted(methods), module_name)

        # Derive target filename configuration
        base_name = os.path.basename(module_path)
        name_without_ext, _ = os.path.splitext(base_name)
        test_filename = f"test_{name_without_ext}.py"

        return GeneratedTest(
            module=module_name,
            test_name=test_filename,
            content=buffer.strip() + "\n",
            target_file=os.path.normpath(os.path.abspath(module_path)),
        )