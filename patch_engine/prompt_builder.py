def build_patch_prompt(
    issue: str,
    code_block: str
) -> str:
    """
    Build an AI prompt for fixing a single code block.
    """

    special_rules = ""

    # --------------------------------------
    # Ruff E722
    # --------------------------------------

    if issue.startswith("E722"):

        special_rules = """
Special Rule
============

Replace ONLY:

except:

with:

except Exception:

Do NOT modify any other line.

Example
=======

Input:

try:
    collection.delete(ids=[filename])
except:
    pass

Output:

try:
    collection.delete(ids=[filename])
except Exception:
    pass
"""

    # --------------------------------------
    # Bandit B105
    # --------------------------------------

    elif issue.startswith("B105"):

        special_rules = """
Special Rule
============

Replace ONLY the hardcoded password.

Example
=======

Input:

password = "admin123"

Output:

password = os.getenv("PASSWORD", "")

Do NOT modify any surrounding code.
Do NOT add imports unless they already exist.
"""

    # --------------------------------------
    # Bandit B307 / Semgrep no-eval
    # --------------------------------------

    elif issue.startswith("B307") or issue.startswith("no-eval"):

        special_rules = """
Special Rule
============

Replace ONLY the use of eval().

Example
=======

Input:

result = eval(user_input)

Output:

result = ast.literal_eval(user_input)

Do NOT modify surrounding code.
Do NOT generate try/except blocks.
Do NOT generate unrelated statements.
Do NOT reuse code from previous examples.
"""

    # --------------------------------------
    # Bandit B110
    # --------------------------------------

    elif issue.startswith("B110"):

        special_rules = """
Special Rule
============

Do NOT rewrite the try block.

If no safe automatic fix exists,
return the ORIGINAL code block unchanged.

Do NOT add logging.
Do NOT add print().
Do NOT change program behaviour.
"""

    # --------------------------------------
    # Bandit B603
    # --------------------------------------

    elif issue.startswith("B603"):

        special_rules = """
Special Rule
============

The subprocess call uses untrusted input.

Requirements
============

- Do NOT use shell=True.
- Preserve the existing functionality.
- Prefer passing command arguments as a list.
- Do NOT concatenate user input into a shell command.
- Do NOT invent sanitization functions.
- Do NOT invent helper functions.
- If no safe automatic fix exists,
  return the ORIGINAL code block unchanged.
"""

    # --------------------------------------
    # Bandit B607
    # --------------------------------------

    elif issue.startswith("B607"):

        special_rules = """
Special Rule
============

Bandit requires an absolute executable path.

Requirements
============

- Use an absolute executable path ONLY if it is already known from the code.
- Do NOT guess operating system paths.
- Do NOT invent executable paths.
- Do NOT hardcode Windows or Linux paths.
- If an absolute executable path cannot be determined safely,
  return the ORIGINAL code block unchanged.
"""

    prompt = f"""
You are an expert Python software engineer.

Your task is to fix ONLY the reported issue in the given code block.

Issue
=====

{issue}

Code Block
==========

{code_block}

Rules
=====

1. Fix ONLY the reported issue.
2. Modify the minimum number of lines possible.
3. Preserve formatting.
4. Preserve indentation.
5. Preserve functionality.
6. Preserve control flow.
7. Preserve every unchanged line.
8. Return ONLY the corrected code block.
9. Never return the entire file.
10. Never generate surrounding code.
11. Never infer nearby code.
12. Never add explanations.
13. Never add Markdown.
14. Never surround the answer with ```.

Critical Constraints
====================

- The output must have exactly the same scope as the input.
- If the input contains one statement, return one statement.
- If the input contains one try/except block, return one try/except block.
- Do NOT introduce identifiers that do not already exist in the input code block.
- Do NOT reuse code from previous examples.
- Do NOT invent helper variables.
- Do NOT invent functions.
- Do NOT invent classes.
- Do NOT invent imports.
- Never generate unrelated code.
- Never generate surrounding code.
- Never modify unrelated statements.
- Never rewrite the entire function.
- Return the original code unchanged if no safe fix exists.

{special_rules}

Expected Output
===============

Return ONLY the corrected code block.

Nothing else.
"""

    return prompt