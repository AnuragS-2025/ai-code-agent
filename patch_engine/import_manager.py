import os
import re


def ensure_import(
    filename: str,
    module: str,
) -> None:
    """
    Ensure that 'import <module>' exists exactly once.
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    import_line = f"import {module}"

    for line in lines:

        if line.strip() == import_line:
            return

    insert_at = 0

    while (
        insert_at < len(lines)
        and (
            lines[insert_at].startswith("import ")
            or lines[insert_at].startswith("from ")
        )
    ):
        insert_at += 1

    lines.insert(insert_at, import_line + "\n")

    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(lines)


def remove_duplicate_imports(
    filename: str,
) -> None:
    """
    Remove duplicate import statements.
    """

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    seen = set()
    output = []

    pattern = re.compile(r"^(import|from)\s+")

    for line in lines:

        stripped = line.strip()

        if pattern.match(stripped):

            if stripped in seen:
                continue

            seen.add(stripped)

        output.append(line)

    with open(filename, "w", encoding="utf-8") as file:
        file.writelines(output)