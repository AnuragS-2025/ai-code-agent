"""Validation Manager Orchestrator.

This module provides the central orchestration layer for the Patch Validation 
Engine. It uses a high-level facade to execute specific sequential pipelines,
managing early short-circuiting conditions while ensuring absolute exception safety.
"""

from validation.models import ValidationReport, ValidationStage
# FIXED: Changed to module-level import to support dynamic runtime mocking/monkeypatching
import validation.validators as validators


class ValidationManager:
    """Orchestrates sequential validation pipelines over modified system code footprints.

    This manager controls the logical order of verification gates (Syntax, AST, and 
    optionally Ruff) and encapsulates any operational unexpected crash states safely 
    into standard immutable data payloads.
    """

    def __init__(self) -> None:
        """Initializes the structural orchestrator instance frame."""
        pass

    def validate_patch(
        self,
        source_code: str,
        file_path: str,
        *,
        run_ruff: bool = True,
    ) -> ValidationReport:
        """Runs validation tasks sequentially on the provided code patch.

        The execution window immediately halts and short-circuits out if any single 
        verification validation engine fails its quality gate criteria.

        Args:
            source_code: The raw string payload containing the candidate code patch.
            file_path: Absolute targeted string storage file coordinate for linter tooling.
            run_ruff: Flag to conditionally determine if subprocess lint checks execute.

        Returns:
            An immutable ValidationReport tracking system state matrices.
        """
        try:
            # Step 1: Initialize an empty, successful report base
            report = ValidationReport(success=True, stages=[])

            # Step 2: Define the chain of validation tasks using the module reference
            validation_pipeline = [
                (validators.validate_syntax, source_code),
                (validators.validate_ast, source_code),
            ]

            if run_ruff:
                validation_pipeline.append((validators.validate_ruff, file_path))

            # Step 3 & 4: Process the validation chain sequentially with short-circuit logic
            for validator, target_input in validation_pipeline:
                stage_outcome = validator(target_input)
                report = report.add_stage(stage_outcome)

                # Short-circuit checking: Instantly drop execution if the step fails
                if not stage_outcome.passed:
                    return report

            # Step 5: Return complete successful execution matrix payload
            return report

        except Exception as exc:
            # High-resiliency guard: Convert unexpected exceptions into an insulated report frame
            fallback_stage = ValidationStage(
                name="Manager",
                passed=False,
                message=f"Validation manager failed: {exc}"
            )
            return ValidationReport(success=False, stages=[fallback_stage])