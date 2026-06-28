from langchain_ollama import ChatOllama


# ==========================================
# Load LLM
# ==========================================

llm = ChatOllama(
    model="llama3.2:3b"
)


# ==========================================
# AI Auto Fix
# ==========================================

def fix_code(
    code: str,
    ruff_report: str,
    bandit_report: str,
    semgrep_report: str
) -> str:
    """
    Generates AI-fixed Python code using analyzer reports.
    """

    prompt = f"""
You are an expert Python software engineer.

Your task is to fix ONLY the issues reported by the static analysis tools.

You MUST return the COMPLETE updated Python source file.

Static Analysis Reports
=======================

Ruff Issues:
{ruff_report}

Bandit Issues:
{bandit_report}

Semgrep Findings:
{semgrep_report}

Instructions
============

- Fix ONLY the reported issues.
- Return the COMPLETE updated Python file.
- Never return only a code snippet.
- Preserve all existing functionality.
- Preserve the overall project structure.
- Do NOT rewrite unrelated code.
- Do NOT refactor unrelated functions.
- Do NOT add new features.
- Do NOT remove required imports.
- Do NOT rename variables, functions, or classes unless required to fix an issue.
- Modify the minimum number of lines necessary.
- Leave all unaffected code unchanged.
- Preserve formatting whenever possible.
- If no fixes are required, return the original file unchanged.
- The returned code must be syntactically valid Python.
- Return ONLY Python code.
- Do NOT use markdown.
- Do NOT add explanations.
- Do NOT add comments describing your changes.
- Do NOT surround the response with ```.

Original Python File
====================

{code}
"""

    print("Sending code to AI...\n")

    response = llm.invoke(prompt)

    fixed_code = response.content

    # Remove markdown if returned
    fixed_code = fixed_code.replace("```python", "")
    fixed_code = fixed_code.replace("```", "")
    fixed_code = fixed_code.strip()

    # Fallback
    if not fixed_code:
        print("❌ AI returned empty response.")
        return code

    return fixed_code