"""Data models and Pydantic schemas for the AI Code Auto Fixer API.

This module defines the validation structures for incoming scan requests
and outgoing issue report frames.
"""

from enum import Enum
from pydantic import BaseModel, Field


class ScanRequest(BaseModel):
    """Schema for structural project scan tracking requests."""

    project_path: str = Field(
        ..., description="The local filesystem route to the target project directory or file"
    )


class IssueModel(BaseModel):
    """Schema representing an isolated engine static analysis diagnostic finding."""

    rule: str = Field(..., description="The unique identification rule tag code")
    message: str = Field(..., description="The diagnostic textual string description")
    file: str = Field(..., description="Normalized structural path location of the file")
    line: int = Field(..., description="The source file target coordinate line number")


class ScanResponse(BaseModel):
    """Schema representing the unified aggregation response model frame."""

    success: bool = Field(..., description="Execution diagnostic state flag")
    issues: list[IssueModel] = Field(
        default_factory=list, description="Aggregated structural collection of analysis findings"
    )


class FixRequest(BaseModel):
    """Schema for incoming auto-fix generation requests."""

    project_path: str = Field(
        ..., description="The local filesystem route to the target project directory or file"
    )


class FixResponse(BaseModel):
    """Schema representing the unified aggregation execution response after applying auto-fixes."""

    success: bool = Field(
        ..., description="Execution diagnostic state flag indicating if the process completed successfully"
    )
    message: str = Field(
        ..., description="The diagnostic textual string summary of the applied automated fixes"
    )
    files_modified: int = Field(
        0, description="The total quantity of distinct files rewritten during processing"
    )
    issues_fixed: int = Field(
        0, description="The total count of individual structural diagnostic findings resolved"
    )


class ToolSummary(BaseModel):
    """Schema representing compiled metrics partitioned across individual analyzer backends."""

    ruff: int = Field(..., description="Total count of unique analysis findings flagged by Ruff")
    bandit: int = Field(..., description="Total count of unique analysis findings flagged by Bandit")
    semgrep: int = Field(..., description="Total count of unique analysis findings flagged by Semgrep")


class ReportResponse(BaseModel):
    """Schema representing the unified analytics summary payload framework for analytical profiling."""

    success: bool = Field(..., description="Execution diagnostic state flag")
    total_issues: int = Field(..., description="The overall grand total sum of deduplicated issues discovered")
    by_tool: ToolSummary = Field(..., description="Aggregated overview structural split grouped by individual tool metrics")
    by_rule: dict[str, int] = Field(..., description="Key-value mapping correlating unique rule identification tags to their density occurrences")


class JobStatus(str, Enum):
    """Enumeration representing the execution state lifecycle transitions of an asynchronous background job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class JobResponse(BaseModel):
    """Schema representing tracking context metadata state tracking frameworks for automated execution tasks."""

    job_id: str = Field(..., description="The unique identification cryptographic token tracking string for the worker task")
    status: JobStatus = Field(..., description="The active discrete execution state flag indicating job progress context")
    message: str = Field(..., description="The diagnostic textual string reporting details about the active processing state")


class ExportFormat(str, Enum):
    """Enumeration representing supported structured document output types for generated reports."""

    JSON = "json"
    CSV = "csv"


class ExportResponse(BaseModel):
    """Schema representing execution context feedback metadata returning localized download configurations."""

    success: bool = Field(..., description="Execution diagnostic state flag mapping operation status")
    file_path: str = Field(..., description="The local absolute or relative filesystem path holding the written export document")
    format: ExportFormat = Field(..., description="The explicit structural encoding protocol chosen for tracking distribution")
    message: str = Field(..., description="The diagnostic textual string summarizing analytical generation processing logs")


class ScanHistoryEntry(BaseModel):
    """Schema representing a historical timeline record of a project execution event entry."""

    timestamp: str = Field(..., description="ISO 8601 serialized date-time tracking coordinate string detailing execution launch")
    project_path: str = Field(..., description="The local filesystem absolute targeting coordinate route evaluated")
    total_issues: int = Field(..., description="The overall grand total count of static analysis rule findings identified during execution")


class ScanHistoryResponse(BaseModel):
    """Schema representing the compiled list aggregate context wrapping all execution timeline historical logs."""

    success: bool = Field(..., description="Execution diagnostic state flag mapping operation status")
    history: list[ScanHistoryEntry] = Field(default_factory=list, description="Aggregated collection sequence profiling historical analytical diagnostic snapshots")


class ToolInfo(BaseModel):
    """Schema tracking detailed diagnostic backend operational state configurations."""

    name: str = Field(..., description="The structural engine registration identifier string code name")
    enabled: bool = Field(..., description="Active activation feature flag detailing whether the runner layer is toggled on")


class SupportedToolsResponse(BaseModel):
    """Schema representing the aggregate breakdown schema response capturing status arrays of all backend engines."""

    success: bool = Field(..., description="Execution diagnostic state flag mapping operation status")
    tools: list[ToolInfo] = Field(default_factory=list, description="Aggregated sequence collection listing specific analyzer metadata frames")


class ConfigResponse(BaseModel):
    """Schema representing the current configuration environment settings profile state."""

    success: bool = Field(..., description="Execution diagnostic state flag mapping operation status")
    ai_enabled: bool = Field(..., description="Feature flag indicating if the AI pipeline orchestrator layer is active")
    ruff_enabled: bool = Field(..., description="Feature flag detailing whether the Ruff linter engine execution is toggled on")
    bandit_enabled: bool = Field(..., description="Feature flag detailing whether the Bandit security analysis pipeline is enabled")
    semgrep_enabled: bool = Field(..., description="Feature flag detailing whether the Semgrep analytical processor is turned on")
    semgrep_config_path: str = Field(..., description="The configuration ruleset targeting route path identifier utilized by Semgrep")
    max_iterations: int = Field(..., description="The threshold cap bounding maximum sequential transformation processing loop attempts")


class PreviewIssue(BaseModel):
    """Schema representing the differential modification blueprint for a single flagged static finding."""

    file: str = Field(..., description="Normalized structural filesystem path location of the targeted source file")
    line: int = Field(..., description="The source code coordinate entry line number indicating violation site location")
    rule: str = Field(..., description="The unique identification analyzer rule configuration tag code name")
    original: str = Field(..., description="The raw un-remediated original snippet block currently existing in the text source frame")
    suggested: str = Field(..., description="The proposed transformation resolution sequence generated to automatically fix the file state")


class FixPreviewResponse(BaseModel):
    """Schema representing the prospective summary change log tracking dry-run optimization iterations."""

    success: bool = Field(..., description="Execution diagnostic state flag mapping operation status")
    previews: list[PreviewIssue] = Field(default_factory=list, description="Aggregated sequence collection summarizing prospective differential modification payloads")