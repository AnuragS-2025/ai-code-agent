"""Module for centralizing all LLM prompt templates and builders.

This module guarantees consistent instruction engineering for the auto-fix engine,
enforcing rigid constraints on formatting, output structure, and structural boundaries.
"""

from typing import Any, Mapping


def build_patch_prompt(
    issue: Mapping[str, Any],
    code_block: str,
    context: str,
) -> str:
    """Constructs a deterministic instruction prompt forcing the LLM to generate code-only patches.

    This prompt enforces absolute constraints to prevent the model from generating Markdown,
    adding conversational prose, introducing arbitrary line changes, or leaking imaginary imports.

    Args:
        issue: A type-safe mapping containing static analysis engine issue diagnostics.
            Expected keys: "rule" (str), "message" (str), "file" (str), and "line" (int/str).
        code_block: The isolated raw code block identified as needing correction.
        context: Surrounding structural file context to assist systemic analysis.

    Returns:
        A fully constructed string prompt engineered for raw python extraction.
    """
    rule = issue.get("rule", "Unknown-Rule")
    message = issue.get("message", "No structural message provided.")
    file_path = issue.get("file", "Unknown-File")
    line = issue.get("line", "?")

    # FIXED: Handles falsy, empty, as well as whitespace-only string context inputs perfectly
    normalized_context = (
        context.strip()
        if context and context.strip()
        else "No additional project context available."
    )

    return f"""You are a precise automated code repair agent. Your single objective is to fix the reported issue in the provided code block.

CRITICAL DIRECTIVES:
1. Fix ONLY the specific problem described in the Issue section.
2. Maintain the exact formatting, indentation spacing, and code style of the original block.
3. NEVER rewrite, modify, or truncate surrounding or unrelated code logic.
4. Output absolutely NO explanations, markdown code blocks (do not use ```python), or text commentary.
5. Return ONLY executable, syntax-valid Python code.
6. Do NOT invent or add new import statements unless explicitly mandated by the issue description.
7. Keep the functional patch block delta as minimal as humanly possible.
8. Do not rename variables, functions, classes, or parameters unless required to fix the reported issue.
9. Preserve existing comments and docstrings unless the reported issue explicitly requires changing them.

---
[System Diagnostic Context]
Issue File: {file_path}
Issue Line: {line}
Issue Rule: {rule}
Issue Message: {message}

[Surrounding Architecture Context]
{normalized_context}

[Original Code Target Block]
{code_block}
---

Return ONLY the replacement code block. Do not include explanations, markdown, headings, comments outside the code, or any additional text."""