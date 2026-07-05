"""Validation Models Configuration.

This module provides immutable data representations for managing specific testing 
and structural verification pipelines. It contains only clean data structures
without validation logic, side-effects, or external dependencies.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationStage:
    """Represents the execution outcome of an isolated validation step or metric check.

    Attributes:
        name: The distinct descriptor identifier of the verification step.
        passed: A boolean flag indicating if the stage met all quality gates.
        message: Operational feedback, error constraints, or completion diagnostic logs.
    """
    name: str
    passed: bool
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """Represents the compiled structural report summarizing a suite of validation operations.

    Attributes:
        success: True if the entire suite passes without critical degradation or failures.
        stages: A sequential sequence listing every evaluated ValidationStage.
    """
    success: bool
    stages: list[ValidationStage] = field(default_factory=list)

    def add_stage(self, stage: ValidationStage) -> "ValidationReport":
        """Appends a new ValidationStage record into the execution tracker logs.

        Because the dataclass is explicitly defined with frozen attributes, this 
        method guarantees complete functional isolation by constructing and 
        returning a brand-new instance frame rather than mutating the original object.

        Args:
            stage: The targeted ValidationStage tracking token to inject.

        Returns:
            A new ValidationReport instance containing the structural additions.
        """
        updated_stages = self.stages + [stage]
        # FIXED: Derived safely directly from all actual stage states to avoid configuration drift
        updated_success = all(s.passed for s in updated_stages)
        
        return ValidationReport(
            success=updated_success,
            stages=updated_stages
        )

    def failed_stage(self) -> ValidationStage | None:
        """Scans the validation collection matrix sequentially to extract the first failure.

        Returns:
            The first ValidationStage instance where 'passed' is false, or 
            None if all systems verified successfully.
        """
        for stage in self.stages:
            if not stage.passed:
                return stage
        return None