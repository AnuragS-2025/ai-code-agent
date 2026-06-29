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

    # --------------------------------------
    # Find start of try block
    # --------------------------------------

    start = issue_index

    while start >= 0:

        if lines[start].lstrip().startswith("try:"):
            break

        start -= 1

    if start < 0:
        start = issue_index

    # --------------------------------------
    # Find end of block
    # --------------------------------------

    indent_size = len(lines[start]) - len(lines[start].lstrip())
    indent = lines[start][:indent_size]

    end = start + 1

    while end < len(lines):

        line = lines[end]

        stripped = line.strip()

        current_indent = len(line) - len(line.lstrip())

        if stripped == "":
            end += 1
            continue

        if (
            current_indent <= indent_size
            and not stripped.startswith(("except", "finally", "else"))
        ):
            break

        end += 1

    block = "".join(lines[start:end])

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