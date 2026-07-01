import os


def extract_code_block(
    filename: str,
    line_number: int,
) -> dict:
    """
    Extract the smallest code block containing the issue.

    Returns:
    {
        "code": original_code_block,
        "indent": original_indentation
    }
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    issue_index = line_number - 1
    print(f"\nDEBUG: line_number={line_number}")
    print(f"DEBUG: total_lines={len(lines)}")
    print(f"DEBUG: issue_index={issue_index}")

    if 0 <= issue_index < len(lines):
        print("DEBUG LINE:", repr(lines[issue_index]))
    if issue_index < 0 or issue_index >= len(lines):
        raise ValueError("Invalid line number.")

    # --------------------------------------
    # Check if issue belongs to a try block
    # --------------------------------------

    start = issue_index
    inside_try = False

    while start >= 0:

        stripped = lines[start].lstrip()

        if stripped.startswith("try:"):
            inside_try = True
            break

        # Stop searching when a new top-level statement begins
        if start != issue_index:

            current_indent = len(lines[start]) - len(lines[start].lstrip())

            if current_indent == 0:
                break

        start -= 1

    # --------------------------------------
    # Single statement (non try-block)
    # --------------------------------------
    
    if not inside_try:

        line = lines[issue_index]

        indent_size = len(line) - len(line.lstrip())
        print("RETURNING SINGLE:")
        print(repr(line))
        return {
            "code": line,
            "indent": line[:indent_size],
        }

    # --------------------------------------
    # Extract try block
    # --------------------------------------

    indent_size = len(lines[start]) - len(lines[start].lstrip())

    indent = lines[start][:indent_size]

    end = start + 1

    while end < len(lines):

        line = lines[end]

        stripped = line.strip()

        current_indent = len(line) - len(line.lstrip())

        # Skip blank lines inside block
        if stripped == "":
            end += 1
            continue

        # Stop when another statement begins at same indentation
        if (
            current_indent <= indent_size
            and not stripped.startswith(("except", "finally", "else"))
        ):
            break

        end += 1

    block = "".join(lines[start:end])
    print("RETURNING TRY BLOCK:")
    print(repr(block))
    return {
        "code": block,
        "indent": indent,
    }


def extract_multiple_blocks(
    filename: str,
    line_numbers: list[int],
) -> list[dict]:

    blocks = []

    for line in sorted(set(line_numbers)):

        data = extract_code_block(
            filename,
            line,
        )

        blocks.append(
            {
                "line": line,
                "code": data["code"],
                "indent": data["indent"],
            }
        )

    return blocks


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    data = extract_code_block(
        "app.py",
        42,
    )

    print("=" * 60)
    print("EXTRACTED BLOCK")
    print("=" * 60)
    print(data["code"])

    print("=" * 60)
    print("INDENT")
    print("=" * 60)
    print(repr(data["indent"]))