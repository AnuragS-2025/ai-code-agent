"""Validation Subsystem Unit Tests.

This test suite thoroughly verifies the operational correctness of the 
Validation Engine package, covering the immutable data structures, individual 
stateless validators, and the short-circuiting orchestrator facade.
"""

from pathlib import Path
import pytest

from validation.models import ValidationReport, ValidationStage
from validation.validators import validate_syntax, validate_ast, validate_ruff
from validation import ValidationManager
import validation.validators


# ==========================================
# 1. Validation Models Tests
# ==========================================

def test_validation_stage_creation():
    """Verifies that ValidationStage initializes and stores its parameters correctly."""
    stage = ValidationStage(name="Syntax", passed=True, message="Looks good")
    
    assert stage.name == "Syntax"
    assert stage.passed is True
    assert stage.message == "Looks good"


def test_validation_report_add_stage():
    """Verifies that ValidationReport remains immutable when appending new stages."""
    original_report = ValidationReport(success=True, stages=[])
    stage = ValidationStage(name="Syntax", passed=True, message="Passed")
    
    new_report = original_report.add_stage(stage)
    
    # Verify original report is unchanged due to frozen=True immutability
    assert len(original_report.stages) == 0
    assert original_report.success is True
    
    # Verify new report structural updates
    assert len(new_report.stages) == 1
    assert new_report.stages[0] == stage
    assert new_report.success is True


def test_validation_report_failed_stage():
    """Verifies that failed_stage() isolates the first failed validation step."""
    stage1 = ValidationStage(name="Syntax", passed=True, message="Ok")
    stage2 = ValidationStage(name="AST", passed=False, message="Failed parsing")
    stage3 = ValidationStage(name="Ruff", passed=True, message="Ok")
    
    report = ValidationReport(success=False, stages=[stage1, stage2, stage3])
    
    failed = report.failed_stage()
    assert failed is not None
    assert failed.name == "AST"
    assert failed.passed is False


# ==========================================
# 2. Syntax Validator Tests
# ==========================================

def test_validate_syntax_success():
    """Verifies that valid Python syntax passes bytecode compilation checks."""
    valid_code = "def hello():\n    return 1\n"
    stage = validate_syntax(valid_code)
    
    assert stage.name == "Syntax"
    assert stage.passed is True
    # FIXED: Strict exact string match assertion
    assert stage.message == "Syntax validation passed."


def test_validate_syntax_failure():
    """Verifies that broken Python syntax safely returns a failed validation stage."""
    invalid_code = "def hello("
    stage = validate_syntax(invalid_code)
    
    assert stage.name == "Syntax"
    assert stage.passed is False
    assert stage.message.startswith("Syntax validation failed:")


# ==========================================
# 3. AST Validator Tests
# ==========================================

def test_validate_ast_success():
    """Verifies that valid Python code generates a healthy abstract syntax tree."""
    valid_code = "x = [1, 2, 3]\nfor i in x:\n    print(i)"
    stage = validate_ast(valid_code)
    
    assert stage.name == "AST"
    assert stage.passed is True
    # FIXED: Strict exact string match assertion
    assert stage.message == "AST validation passed."


def test_validate_ast_failure():
    """Verifies that malformed code causes an AST parsing validation failure stage."""
    invalid_code = "for x in:"
    stage = validate_ast(invalid_code)
    
    assert stage.name == "AST"
    assert stage.passed is False
    assert stage.message.startswith("AST validation failed:")


# ==========================================
# 4. Ruff Validator Tests
# ==========================================

def test_validate_ruff_success(tmp_path: Path):
    """Verifies that a compliant Python file passes external Ruff checks successfully."""
    test_file = tmp_path / "compliant.py"
    test_file.write_text("x = 1\n", encoding="utf-8")
    
    stage = validate_ruff(str(test_file))
    
    assert stage.name == "Ruff"
    assert stage.passed is True
    # FIXED: Strict exact string match assertion
    assert stage.message == "Ruff validation passed."


def test_validate_ruff_missing_file(tmp_path: Path):
    """Verifies that tracking missing paths safely returns a descriptive failure stage."""
    # FIXED: Used tmp_path to maintain cross-platform reliable testing path structures
    missing_path = tmp_path / "ghost_file.py"
    stage = validate_ruff(str(missing_path))
    
    assert stage.name == "Ruff"
    assert stage.passed is False
    assert stage.message == f"File not found: {missing_path}"


# ==========================================
# 5. Validation Manager Tests
# ==========================================

def test_validation_manager_success(tmp_path: Path):
    """Verifies that the manager executes all 3 sequential stages for healthy modules."""
    test_file = tmp_path / "perfect.py"
    code_content = "def sample_utility():\n    pass\n"
    test_file.write_text(code_content, encoding="utf-8")
    
    manager = ValidationManager()
    report = manager.validate_patch(
        source_code=code_content,
        file_path=str(test_file),
        run_ruff=True
    )
    
    assert report.success is True
    assert len(report.stages) == 3
    assert report.stages[0].name == "Syntax"
    assert report.stages[1].name == "AST"
    assert report.stages[2].name == "Ruff"


def test_validation_manager_short_circuit():
    """Verifies that a failure in an early gate instantly halts downstream verification."""
    broken_code = "class MissingParenthesis("
    manager = ValidationManager()
    
    report = manager.validate_patch(
        source_code=broken_code,
        file_path="dummy_path.py",
        run_ruff=True
    )
    
    assert report.success is False
    assert len(report.stages) == 1
    assert report.stages[0].name == "Syntax"
    assert report.stages[0].passed is False


def test_validation_manager_exception_path(monkeypatch: pytest.MonkeyPatch):
    """Verifies that unexpected sub-module exceptions are caught and wrapped cleanly by the manager facade."""
    def mock_runtime_crash(source_code: str):
        raise RuntimeError("Simulated internal worker crash")
    
    # FIXED: Works seamlessly now due to module-referenced imports inside manager.py
    monkeypatch.setattr(validation.validators, "validate_syntax", mock_runtime_crash)
    
    manager = ValidationManager()
    report = manager.validate_patch(
        source_code="x = 1",
        file_path="dummy_path.py",
        run_ruff=False
    )
    
    assert report.success is False
    assert len(report.stages) == 1
    assert report.stages[0].name == "Manager"
    assert report.stages[0].passed is False
    assert report.stages[0].message == "Validation manager failed: Simulated internal worker crash"