import os


BLOCK_STARTS = (
    "try:",
    "def ",
    "class ",
    "if ",
    "elif ",
    "else:",
    "for ",
    "while ",
    "with ",
)


def extract_code_block(
    filename: str,
    line_number: int,
) -> dict:
    """
    Extract the smallest logical code block containing an issue.

    Returns:
    {
        "code": ...,
        "indent": ...
    }
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    issue_index = line_number - 1

    if issue_index < 0 or issue_index >= len(lines):
        raise ValueError("Invalid line number.")

    # --------------------------------------
    # Find nearest enclosing block
    # --------------------------------------

    start = issue_index
    inside_block = False

    while start >= 0:

        stripped = lines[start].lstrip()

        if stripped.startswith(BLOCK_STARTS):

            inside_block = True
            break

        if start != issue_index:

            indent = len(lines[start]) - len(lines[start].lstrip())

            if indent == 0:
                break

        start -= 1

    # --------------------------------------
    # Single statement
    # --------------------------------------

    if not inside_block:

        line = lines[issue_index]

        indent = line[:len(line) - len(line.lstrip())]

        return {
            "code": line,
            "indent": indent,
        }

    # --------------------------------------
    # Determine indentation
    # --------------------------------------

    indent_size = (
        len(lines[start]) -
        len(lines[start].lstrip())
    )

    indent = lines[start][:indent_size]

    # --------------------------------------
    # Find block end
    # --------------------------------------

    end = start + 1

    while end < len(lines):

        line = lines[end]

        stripped = line.strip()

        current_indent = (
            len(line) -
            len(line.lstrip())
        )

        if stripped == "":
            end += 1
            continue

        if (
            current_indent <= indent_size
            and not stripped.startswith(
                (
                    "except",
                    "finally",
                    "else",
                    "elif",
                )
            )
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