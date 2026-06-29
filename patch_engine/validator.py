import ast
import textwrap


def validate_patch(code_block: str) -> tuple[bool, str]:
    """
    Validate an AI-generated Python code block.

    Returns:
        (True, "Valid Python code")
        (False, "Syntax error details")
    """

    try:

        # Remove leading indentation before parsing
        clean_code = textwrap.dedent(code_block)

        ast.parse(clean_code)

        return True, "Valid Python code"

    except SyntaxError as e:

        message = (
            f"SyntaxError at line {e.lineno}, "
            f"column {e.offset}: {e.msg}"
        )

        if e.text:
            message += (
                f"\nProblematic code: {e.text.strip()}"
            )

        return False, message


def print_validation_result(code_block: str):
    """
    Print validation result in a readable format.
    """

    print("=" * 60)
    print("PATCH VALIDATION")
    print("=" * 60)

    valid, message = validate_patch(code_block)

    if valid:
        print("✔ Patch is valid.\n")
    else:
        print("❌ Patch is invalid.\n")

    print(message)


if __name__ == "__main__":

    valid_patch = """
        try:
            collection.delete(ids=[filename])
        except Exception:
            pass
"""

    invalid_patch = """
        try:
            collection.delete(ids=[filename])
        except
            pass
"""

    print("\nTesting VALID patch\n")
    print_validation_result(valid_patch)

    print("\nTesting INVALID patch\n")
    print_validation_result(invalid_patch)