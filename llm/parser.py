"""Module for parsing and cleaning raw textual responses from LLMs.

This module provides utility operations to strip markdown decorators, code fences,
and non-python structural noise from model outputs before passing them to the validation layer.
"""


def clean_response(response: str) -> str:
    """Cleans and normalizes raw LLM text outputs by stripping markdown code fences.

    This function isolates the raw Python code block from common markdown containers
    (such as ```python or ```) without altering the internal code structures, indentations,
    or inline code comments.

    Args:
        response: The raw string payload received directly from the LLM client execution.

    Returns:
        A completely normalized code string stripped of markdown artifacts, with leading
        and trailing whitespace removed, ending with a standard single newline if code exists.
    """
    if not response or not response.strip():
        return ""

    lines = response.splitlines()
    cleaned_lines = []

    for line in lines:
        # Strip trailing carriage returns/spaces to inspect the structure accurately
        stripped_line = line.strip()
        
        # FIXED: Convert to lowercase to robustly match variants like ```Python, ```PYTHON, or ```py
        lower_line = stripped_line.lower()

        # Skip explicit markdown language block definitions safely
        if lower_line.startswith("```python") or lower_line.startswith("```py"):
            continue
        
        # Skip generic closed or open markdown blocks
        if stripped_line == "```":
            continue

        cleaned_lines.append(line)

    # Reconstruct the string and perform whitespace cleanup
    cleaned_code = "\n".join(cleaned_lines).strip()

    # Guarantee a clean, single trailing newline structural termination if content is present
    return f"{cleaned_code}\n" if cleaned_code else ""