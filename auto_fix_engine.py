from langchain_ollama import ChatOllama
from patch_engine.prompt_builder import build_patch_prompt

import textwrap


# ==========================================
# Load LLM
# ==========================================

llm = ChatOllama(
    model="llama3.2:3b"
)


# ==========================================
# Generate Patch
# ==========================================

def generate_patch(
    issue: str,
    code_block: str
) -> str:
    """
    Generate a fixed version of a single code block.

    Args:
        issue: Static analysis issue
        code_block: Original extracted code block

    Returns:
        AI-generated fixed code block with original indentation.
    """

    # --------------------------------------
    # Detect indentation
    # --------------------------------------

    indent = ""

    for line in code_block.splitlines():

        if line.strip():

            indent = line[:len(line) - len(line.lstrip())]
            break

    # --------------------------------------
    # Remove indentation before sending to AI
    # --------------------------------------

    clean_code = textwrap.dedent(code_block)

    prompt = build_patch_prompt(
        issue,
        clean_code
    )

    print("[✓] Sending patch request to AI...\n")

    response = llm.invoke(prompt)

    # --------------------------------------
    # Clean AI output
    # --------------------------------------

    fixed_block = (
        response.content
        .replace("```python", "")
        .replace("```", "")
        .strip()
    )

    if not fixed_block:

        print("❌ AI returned an empty response.")

        return code_block

    # --------------------------------------
    # Reject hallucinated output
    # --------------------------------------

    original_lines = len(clean_code.splitlines())
    generated_lines = len(fixed_block.splitlines())

    if generated_lines > original_lines + 2:

        print("❌ AI modified more than expected.")

        return code_block

    # --------------------------------------
    # Reject unchanged output
    # --------------------------------------

    clean_fixed = textwrap.dedent(fixed_block).strip()
    clean_original = textwrap.dedent(code_block).strip()

    if clean_fixed == clean_original:

        print("⚠ AI returned the original code without any changes.")

        return code_block
    
    # --------------------------------------
    # Restore indentation
    # --------------------------------------

    fixed_block = textwrap.dedent(fixed_block)

    fixed_block = textwrap.indent(
        fixed_block,
        indent
    )

    fixed_block = fixed_block.rstrip() + "\n"
    return fixed_block


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    sample_issue = "E722: Do not use bare except."

    sample_code = """
        try:
            collection.delete(ids=[filename])
        except:
            pass
"""

    print("=" * 60)
    print("ORIGINAL BLOCK")
    print("=" * 60)
    print(sample_code)

    print()

    fixed = generate_patch(
        sample_issue,
        sample_code
    )

    print("=" * 60)
    print("FINAL PATCH")
    print("=" * 60)
    print(fixed)