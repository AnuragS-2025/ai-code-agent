"""Comprehensive pytest test suite for the LLM subsystem."""

from typing import Any
import pytest

# Module under test imports
from llm.client import LLMClient
from llm.manager import LLMManager
from llm.prompts import build_patch_prompt
from llm.parser import clean_response
from llm.guardrails import (
    is_empty_patch,
    is_same_patch,
    is_patch_too_large,
    validate_generated_patch,
)

# ==============================================================================
# Test Helpers & Fixtures
# ==============================================================================

class FakeResponse:
    """Simple fake response object returned by the mocked LLM."""

    def __init__(self, content: Any) -> None:
        self.content = content


@pytest.fixture
def mock_chatollama(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Mock ChatOllama used by LLMClient."""

    state: dict[str, Any] = {
        "init_error": False,
        "runtime_error": False,
        "connection_error": False,
        "generic_error": False,
        "response": FakeResponse(
            "  def fixed_function():\n    return True\n"
        ),
    }

    class MockChatOllama:
        def __init__(self, model: str) -> None:
            if state["init_error"]:
                raise RuntimeError("Initialization failed")

            self.model = model

        def invoke(self, prompt: str) -> Any:
            if state["runtime_error"]:
                raise RuntimeError("Runtime failure")

            if state["connection_error"]:
                raise ConnectionError("Connection failure")

            if state["generic_error"]:
                raise ValueError("Unexpected failure")

            return state["response"]

    monkeypatch.setattr(
        "llm.client.ChatOllama",
        MockChatOllama,
    )

    return state


# ==============================================================================
# LLMClient Tests
# ==============================================================================

def test_generate_returns_stripped_response(
    mock_chatollama: dict[str, Any],
) -> None:
    """LLMClient should strip surrounding whitespace."""

    client = LLMClient()
    result = client.generate("Fix this")
    assert result == "def fixed_function():\n    return True"


def test_generate_returns_empty_for_empty_prompt() -> None:
    """Empty prompts should never reach the model."""

    client = LLMClient()
    assert client.generate("") == ""
    assert client.generate("   ") == ""
    assert client.generate("\n\n") == ""


def test_generate_returns_empty_when_client_not_initialized(
    mock_chatollama: dict[str, Any],
) -> None:
    """Initialization failures should never crash generation."""

    mock_chatollama["init_error"] = True
    client = LLMClient()
    assert client.generate("hello") == ""


def test_generate_handles_none_response(
    mock_chatollama: dict[str, Any],
) -> None:
    """A None response should safely return an empty string."""

    mock_chatollama["response"] = None
    client = LLMClient()
    assert client.generate("hello") == ""


def test_generate_handles_runtime_error(
    mock_chatollama: dict[str, Any],
) -> None:
    """RuntimeError should be isolated."""

    mock_chatollama["runtime_error"] = True
    client = LLMClient()
    assert client.generate("hello") == ""


def test_generate_handles_connection_error(
    mock_chatollama: dict[str, Any],
) -> None:
    """ConnectionError should be isolated."""

    mock_chatollama["connection_error"] = True
    client = LLMClient()
    assert client.generate("hello") == ""


def test_generate_handles_unexpected_exception(
    mock_chatollama: dict[str, Any],
) -> None:
    """Unexpected exceptions should never propagate."""

    mock_chatollama["generic_error"] = True
    client = LLMClient()
    assert client.generate("hello") == ""


# ==============================================================================
# Prompt Builder Tests
# ==============================================================================

def test_build_patch_prompt_contains_required_fields() -> None:
    """Prompt should contain all issue metadata and code."""

    issue = {
        "rule": "B105",
        "message": "Hardcoded password",
        "file": "app.py",
        "line": 15,
    }

    prompt = build_patch_prompt(
        issue,
        'PASSWORD = "admin123"',
        "import os",
    )

    assert "Issue Rule: B105" in prompt
    assert "Issue Message: Hardcoded password" in prompt
    assert "Issue File: app.py" in prompt
    assert "Issue Line: 15" in prompt
    assert 'PASSWORD = "admin123"' in prompt
    assert "import os" in prompt
    assert "Return ONLY the replacement code block" in prompt


def test_build_patch_prompt_uses_default_values() -> None:
    """Missing keys should fall back to defaults."""

    prompt = build_patch_prompt({}, "x = 1", "")

    assert "Unknown-Rule" in prompt
    assert "Unknown-File" in prompt
    assert "No structural message provided." in prompt
    assert "Issue Line: ?" in prompt


def test_build_patch_prompt_empty_context() -> None:
    """Empty context should use fallback text."""

    issue = {
        "rule": "R1",
        "message": "Example",
        "file": "a.py",
        "line": 1,
    }

    prompt = build_patch_prompt(
        issue,
        "pass",
        "",
    )

    assert "No additional project context available." in prompt


def test_build_patch_prompt_whitespace_context() -> None:
    """Whitespace-only context should use fallback."""

    issue = {
        "rule": "R1",
        "message": "Example",
        "file": "a.py",
        "line": 1,
    }

    prompt = build_patch_prompt(
        issue,
        "pass",
        "    \n    ",
    )

    assert "No additional project context available." in prompt


# ==============================================================================
# Parser Tests
# ==============================================================================

def test_clean_response_removes_python_fence() -> None:
    raw = """```python
x = 1
```"""
    assert clean_response(raw) == "x = 1\n"


def test_clean_response_removes_py_fence() -> None:
    raw = """```py
x = 1
```"""
    assert clean_response(raw) == "x = 1\n"


def test_clean_response_removes_uppercase_fence() -> None:
    raw = """```PYTHON
x = 1
```"""
    assert clean_response(raw) == "x = 1\n"


def test_clean_response_preserves_indentation() -> None:
    raw = """```python
def hello():
    return 1
```"""
    cleaned = clean_response(raw)
    assert cleaned == "def hello():\n    return 1\n"


def test_clean_response_returns_empty_for_empty_input() -> None:
    assert clean_response("") == ""
    assert clean_response("   ") == ""


def test_clean_response_has_single_trailing_newline() -> None:
    raw = "x = 1"
    cleaned = clean_response(raw)
    assert cleaned.endswith("\n")
    assert not cleaned.endswith("\n\n")


def test_clean_response_only_code_fence() -> None:
    """An empty markdown code fence should evaluate to an empty string."""
    raw = "```python\n```"
    assert clean_response(raw) == ""


# ==============================================================================
# Guardrails Tests
# ==============================================================================

def test_is_empty_patch() -> None:
    assert is_empty_patch("")
    assert is_empty_patch("   ")
    assert not is_empty_patch("x = 1")


def test_is_same_patch() -> None:
    assert is_same_patch("x = 1", "x = 1")
    assert is_same_patch("x = 1\n", "x = 1")
    assert not is_same_patch("x = 1", "y = 2")


def test_is_patch_too_large() -> None:
    original = "a\nb"
    valid = "a\nb\nc\nd"
    invalid = "a\nb\nc\nd\ne"

    assert not is_patch_too_large(original, valid)
    assert is_patch_too_large(original, invalid)


def test_is_patch_too_large_boundary() -> None:
    """Patches with exactly two extra lines should be accepted at the boundary limit."""
    original = "a\nb"
    generated = "a\nb\nc\nd"

    # Verify directly via the lower-level guardrail function
    assert is_patch_too_large(original, generated) is False

    # Verify through the orchestrating validation function
    valid, reason = validate_generated_patch(original, generated)
    assert valid is True
    assert reason == "Valid patch"


def test_validate_generated_patch_success() -> None:
    valid, reason = validate_generated_patch(
        "x = 1",
        "x = 2",
    )
    assert valid is True
    assert reason == "Valid patch"


def test_validate_generated_patch_empty() -> None:
    valid, _ = validate_generated_patch(
        "x = 1",
        "",
    )
    assert valid is False


def test_validate_generated_patch_same() -> None:
    valid, _ = validate_generated_patch(
        "x = 1",
        "x = 1",
    )
    assert valid is False


def test_validate_generated_patch_too_large() -> None:
    valid, _ = validate_generated_patch(
        "a\nb",
        "a\nb\nc\nd\ne",
    )
    assert valid is False


# ==============================================================================
# LLMManager Tests
# ==============================================================================

def test_manager_generate_patch_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """LLMManager should return a cleaned patch when every stage succeeds."""

    class FakeClient:
        def generate(self, prompt: str) -> str:
            return "```python\nx = 2\n```"

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        lambda issue, code, context: "prompt",
    )

    manager = LLMManager(client=FakeClient())

    patch = manager.generate_patch(
        issue={"rule": "B105"},
        code_block="x = 1",
        context="",
    )

    assert patch == "x = 2\n"


def test_manager_returns_none_for_empty_llm_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty model responses should terminate safely."""

    class FakeClient:
        def generate(self, prompt: str) -> str:
            return ""

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        lambda issue, code, context: "prompt",
    )

    manager = LLMManager(client=FakeClient())

    assert (
        manager.generate_patch(
            {"rule": "B105"},
            "x = 1",
            "",
        )
        is None
    )


def test_manager_returns_none_when_parser_returns_empty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Empty parser output should be rejected."""

    class FakeClient:
        def generate(self, prompt: str) -> str:
            return "some response"

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        lambda issue, code, context: "prompt",
    )

    monkeypatch.setattr(
        "llm.manager.clean_response",
        lambda response: "",
    )

    manager = LLMManager(client=FakeClient())

    assert (
        manager.generate_patch(
            {"rule": "B105"},
            "x = 1",
            "",
        )
        is None
    )


def test_manager_returns_none_when_guardrails_reject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rejected patches should never reach callers."""

    class FakeClient:
        def generate(self, prompt: str) -> str:
            return "patched"

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        lambda issue, code, context: "prompt",
    )

    monkeypatch.setattr(
        "llm.manager.clean_response",
        lambda response: "patched",
    )

    monkeypatch.setattr(
        "llm.manager.validate_generated_patch",
        lambda original, patch: (
            False,
            "Rejected",
        ),
    )

    manager = LLMManager(client=FakeClient())

    assert (
        manager.generate_patch(
            {"rule": "B105"},
            "x = 1",
            "",
        )
        is None
    )


def test_manager_handles_client_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unexpected client exceptions should be isolated."""

    class FakeClient:
        def generate(self, prompt: str) -> str:
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        lambda issue, code, context: "prompt",
    )

    manager = LLMManager(client=FakeClient())

    assert (
        manager.generate_patch(
            {"rule": "B105"},
            "x = 1",
            "",
        )
        is None
    )


def test_manager_handles_prompt_builder_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prompt builder exceptions should be caught and isolated by LLMManager."""

    class FakeClient:
        def generate(self, prompt: str) -> str:
            raise AssertionError("Client should never be called when prompt building fails.")

    def fake_builder_fail(issue: dict[str, Any], code: str, context: str) -> str:
        raise RuntimeError("Prompt failure")

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        fake_builder_fail,
    )

    manager = LLMManager(client=FakeClient())

    result = manager.generate_patch(
        issue={"rule": "B105"},
        code_block="x = 1",
        context="",
    )

    assert result is None


def test_manager_builds_prompt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prompt builder should receive the expected arguments."""

    captured: dict[str, object] = {}

    def fake_builder(
        issue: dict[str, Any],
        code: str,
        context: str,
    ) -> str:
        captured["issue"] = issue
        captured["code"] = code
        captured["context"] = context
        return "prompt"

    class FakeClient:
        def generate(self, prompt: str) -> str:
            return "patched"

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        fake_builder,
    )

    monkeypatch.setattr(
        "llm.manager.clean_response",
        lambda response: "patched",
    )

    monkeypatch.setattr(
        "llm.manager.validate_generated_patch",
        lambda original, patch: (
            True,
            "Valid patch",
        ),
    )

    manager = LLMManager(client=FakeClient())

    result = manager.generate_patch(
        {"rule": "B105"},
        "x = 1",
        "project context",
    )

    assert result == "patched"
    assert captured["code"] == "x = 1"
    assert captured["context"] == "project context"


def test_manager_passes_generated_prompt_to_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generated prompt should be forwarded unchanged to the client."""

    received: dict[str, str] = {}

    class FakeClient:
        def generate(self, prompt: str) -> str:
            received["prompt"] = prompt
            return "patched"

    monkeypatch.setattr(
        "llm.manager.build_patch_prompt",
        lambda issue, code, context: "EXPECTED PROMPT",
    )

    monkeypatch.setattr(
        "llm.manager.clean_response",
        lambda response: "patched",
    )

    monkeypatch.setattr(
        "llm.manager.validate_generated_patch",
        lambda original, patch: (
            True,
            "Valid patch",
        ),
    )

    manager = LLMManager(client=FakeClient())

    manager.generate_patch(
        {"rule": "B105"},
        "x = 1",
        "",
    )

    assert received["prompt"] == "EXPECTED PROMPT"