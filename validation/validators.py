"""Validation Utilities Configuration.

This module houses stateless, single-responsibility verification workers utilized
by the Patch Validation Engine. Every handler captures errors internally and
normalizes the operational outcome into an immutable ValidationStage payload.
"""

import ast
import subprocess
from pathlib import Path

from validation.models import ValidationStage


def validate_syntax(source_code: str) -> ValidationStage:
    """Verifies that the provided source code compiles successfully into valid bytecode.

    This function executes standard python bytecode compilation targets purely in-memory
    without dropping transactional footprints or state files onto absolute local storage.

    Args:
        source_code: The raw implementation string payload to pass downstream.

    Returns:
        A ValidationStage tracking metadata and evaluation criteria details.
    """
    stage_name = "Syntax"
    try:
        # FIXED: Simplified standard filename identifier
        compile(source_code, filename="<validation>", mode="exec")
        return ValidationStage(
            name=stage_name,
            passed=True,
            message="Syntax validation passed."
        )
    except (SyntaxError, ValueError, TypeError) as exc:
        # FIXED: Targeted explicit exceptions with streamlined error context
        return ValidationStage(
            name=stage_name,
            passed=False,
            message=f"Syntax validation failed: {exc}"
        )


def validate_ast(source_code: str) -> ValidationStage:
    """Parses source code into an Abstract Syntax Tree to identify deep architectural bugs.

    Args:
        source_code: The raw target python script data to pass down.

    Returns:
        A ValidationStage structure containing pass/fail parsing results.
    """
    stage_name = "AST"
    try:
        # FIXED: Simplified standard filename identifier
        ast.parse(source_code, filename="<validation>")
        return ValidationStage(
            name=stage_name,
            passed=True,
            message="AST validation passed."
        )
    except (SyntaxError, ValueError, TypeError) as exc:
        # FIXED: Targeted explicit exceptions with streamlined error context
        return ValidationStage(
            name=stage_name,
            passed=False,
            message=f"AST validation failed: {exc}"
        )


def validate_ruff(file_path: str) -> ValidationStage:
    """Invokes a separate ruff validation process tool via an isolated subprocess execution layer.

    Args:
        file_path: Absolute string disk target address or structured path pointing to a system file.

    Returns:
        A ValidationStage instance capturing check results or systemic platform issues.
    """
    stage_name = "Ruff"
    target = Path(file_path)

    # FIXED: Concise and readable file existence error signature
    if not target.exists():
        return ValidationStage(
            name=stage_name,
            passed=False,
            message=f"File not found: {target}"
        )

    try:
        # Executing absolute ruff checks while bypassing vulnerable shell engine configurations
        result = subprocess.run(
            ["ruff", "check", str(target)],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            return ValidationStage(
                name=stage_name,
                passed=True,
                message="Ruff validation passed."
            )
        
        # FIXED: Clean conditional join mechanism that strips out empty structural components
        output = "\n".join(
            part for part in (result.stdout.strip(), result.stderr.strip())
            if part
        )
        return ValidationStage(
            name=stage_name,
            passed=False,
            message=output or f"Ruff validation failed with exit code: {result.returncode}"
        )

    except (FileNotFoundError, subprocess.SubprocessError, OSError) as exc:
        # FIXED: Streamlined fallback context signature block
        return ValidationStage(
            name=stage_name,
            passed=False,
            message=f"Ruff validation failed: {exc}"
        )