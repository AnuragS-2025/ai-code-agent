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

Output Requirements
===================

- Return the COMPLETE corrected code block.
- Do NOT return only the modified line.
- Preserve every unchanged line.
- The first line of your response must be the first line of the input code block.
- The last line of your response must be the last line of the input code block.
- Keep the same indentation.
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
"""

    return prompt