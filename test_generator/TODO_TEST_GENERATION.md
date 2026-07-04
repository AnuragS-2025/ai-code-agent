# Future Test Generation Optimization Roadmap

This document captures detailed operational integration blueprints intended for implementation during downstream software evolution phases.

---

## 1. Architectural Alignment & Parser Mapping Layer

### AST Parser Enhancement

The current `ProjectIndex` implementation (Sprint 3.2) exposes class metadata as a flat `list[str]`.

The current Test Generator is designed to support nested class method extraction using the following structure:

```python
{
    "ApiClient": ["connect", "close"]
}
```

Future iterations should extend the AST parser to collect class methods directly, or introduce a lightweight transformation layer that converts the existing parser output into the structure expected by the test generation engine.

### Module Resolution

Current implementations accept a `module_name` property directly.

During pipeline integration, module names should instead be derived from indexed file paths.

Example:

```python
from pathlib import Path

module_name = Path(path).stem
```

This removes duplicate metadata and aligns the generator with the Project Index architecture.

---

## 2. Pipeline Integration

Hook the `TestGenerationManager` into the execution pipeline after a successful patch application.

Suggested execution point:

```
Patch Applied
        │
        ▼
Patch Validation
        │
        ▼
Generate Regression Test
        │
        ▼
Write Test File
```

Tests should only be generated after syntax validation succeeds.

---

## 3. AI-Assisted Test Generation

Replace the placeholder templates (`assert True`) with LLM-generated unit tests.

The future prompt should include:

- module context
- imported modules
- exported symbols
- dependency graph
- fixed source code
- analyzer rule
- patch information

This enables generation of meaningful assertions instead of placeholder tests.

---

## 4. Regression Testing

Immediately execute generated tests after patch application.

Workflow:

```
Patch Applied
        │
        ▼
Generate Tests
        │
        ▼
Run Pytest
        │
        ▼
Pass
    │
    ▼
Commit Patch

Fail
    │
    ▼
Rollback Patch
```

---

## 5. Coverage Awareness

Future versions should integrate with coverage.py to detect uncovered functions.

Test generation should prioritize modules having the lowest coverage.

---

## 6. Safe File Management

Current implementation intentionally avoids overwriting existing tests.

Future enhancements may support:

- overwrite mode
- merge mode
- append mode

through configurable writer options.

---

## 7. Project Index Compatibility

Future releases should consume `ModuleInfo` objects directly from the Project Index rather than relying on lightweight mock-compatible objects.

This removes duplicate metadata extraction and keeps the test generation subsystem synchronized with the indexing architecture.