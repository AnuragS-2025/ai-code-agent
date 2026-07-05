"""Data models and Pydantic schemas for the AI Code Auto Fixer API.

This module defines the validation structures for incoming scan requests
and outgoing issue report frames.
"""

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