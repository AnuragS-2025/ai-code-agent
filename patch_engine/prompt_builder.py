def build_patch_prompt(
    issue: str,
    code_block: str
) -> str:
    """
    Build an AI prompt for fixing a single code block.
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
2. Do NOT rewrite unrelated code.
3. Preserve existing functionality.
4. Preserve the original logic.
5. Preserve the original formatting.
6. Preserve the original indentation exactly.
7. Do NOT add new functionality.
8. Do NOT remove existing functionality.
9. Do NOT add logging or print statements.
10. Do NOT add comments.
11. Do NOT introduce new exception types unless absolutely required.
12. Do NOT add additional try/except blocks.
13. Do NOT rename variables, functions, or classes.
14. Keep the same control flow.
15. Modify the minimum number of lines possible.
16. Return ONLY the corrected code block.
17. Do NOT return the entire file.
18. Do NOT use Markdown.
19. Do NOT surround the response with ```.
20. If the input code block contains only a single statement, return only that single corrected statement.
21. Do NOT generate surrounding code.
22. Do NOT infer nearby code.
23. Do NOT recreate the rest of the file.
24. Return exactly the same code block boundaries as the input.
25. Never add code that is not present in the input block.
26. The number of statements in the output should match the input whenever possible.

Special Rules
=============

If the issue is:

E722: Do not use bare except

Replace ONLY:

except:

with:

except Exception:

Do not modify any other line.

--------------------------------------------

If the issue is:

B110: Try, Except, Pass detected.

Replace ONLY:

except:
    pass

with:

except Exception:
    pass

Preserve the existing try block.
Do NOT add logging.
Do NOT add print statements.
Do NOT introduce additional exception handling.
Do NOT change the control flow.

--------------------------------------------

If the issue is:

B105: Possible hardcoded password

Replace ONLY the hardcoded password assignment.

Replace:

password = "..."

with:

password = os.getenv("PASSWORD", "")

Return ONLY the corrected assignment.

Do NOT generate surrounding code.
Do NOT generate helper variables.
Do NOT generate configuration files.
Do NOT add explanations.
Do NOT add comments.
Do NOT add functions.
Do NOT add classes.
Do NOT add imports unless they already exist inside the provided code block.

Output Requirements
===================

- Return ONLY the corrected version of the provided code block.
- Do NOT return the entire file.
- Do NOT generate surrounding code.
- Do NOT infer missing code.
- Preserve every unchanged line inside the provided code block.
- The first line of your response must be the first line of the input code block.
- The last line of your response must be the last line of the input code block.
- Keep the same indentation.
- Keep the same block boundaries.
- Keep the same number of statements unless fixing the reported issue requires otherwise.

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

Expected Output
===============

Return ONLY the corrected code block.

Do NOT add explanations.
Do NOT add Markdown.
Do NOT add surrounding code.
Do NOT recreate nearby code.
Do NOT infer missing code.

The output must contain exactly the same scope as the input.

If the input is one statement, return exactly one corrected statement.

If the input is a try/except block, return only that try/except block.

Do NOT add imports, variables, functions, classes, or additional statements.

Do NOT modify any code outside the given code block.
"""

    return prompt