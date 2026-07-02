import os


def replace_code_block(
    filename: str,
    start_line: int,
    end_line: int,
    new_block: str,
) -> bool:
    """
    Replace an existing code block directly using absolute line ranges 
    provided by the AST extractor. Eliminates risky string-matching algorithms.

    Args:
        filename: Target file path
        start_line: 1-indexed start line of the target block
        end_line: 1-indexed end line of the target block
        new_block: The new code string block to inject

    Returns:
        True  -> Replacement successful
        False -> Validation or file bounds failure (Silent API style)
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Convert 1-indexed ranges to 0-indexed slice boundaries
    start_idx = start_line - 1
    end_idx = end_line  # Slicing operates non-inclusively on the upper boundary

    # Bounds validation checks (Fails silently; pipeline logs explicit errors)
    if start_idx < 0 or end_idx > len(lines) or start_idx >= end_idx:
        return False

    # Normalize incoming patch block safely
    new_block = new_block.rstrip("\n")
    
    # Check if patch implies total code block removal
    if not new_block.strip():
        patch_lines = []
    else:
        new_block += "\n"
        patch_lines = new_block.splitlines(keepends=True)

    # Inplace mutation via explicit line array slice override
    lines[start_idx:end_idx] = patch_lines

    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(lines)

    return True