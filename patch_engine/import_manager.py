import os
import re


# ==========================================
# API -> Required Import Mapping
# ==========================================

IMPORT_MAP = {
    "ast.literal_eval": "ast",
    "os.getenv": "os",
    "json.loads": "json",
    "json.dumps": "json",
    "yaml.safe_load": "yaml",
    "yaml.safe_dump": "yaml",
    "Path(": "pathlib",
    "Path.": "pathlib",
    "datetime.now": "datetime",
    "datetime.utcnow": "datetime",
}


# ==========================================
# Ensure Import Exists
# ==========================================

def ensure_import(
    filename: str,
    module: str,
) -> None:

    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    import_line = f"import {module}"

    if any(line.strip() == import_line for line in lines):
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


# ==========================================
# Auto Add Required Imports
# ==========================================

def ensure_required_imports(
    filename: str,
    code_block: str,
) -> None:
    """
    Detect APIs used in the generated patch and
    automatically add the required imports.
    """

    for api, module in IMPORT_MAP.items():

        if api in code_block:
            ensure_import(
                filename,
                module,
            )


# ==========================================
# Remove Duplicate Imports
# ==========================================

def remove_duplicate_imports(
    filename: str,
) -> None:

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


# ==========================================
# Full Import Cleanup
# ==========================================

def update_imports(
    filename: str,
    generated_patch: str,
) -> None:
    """
    Perform all import management tasks.
    """

    ensure_required_imports(
        filename,
        generated_patch,
    )

    remove_duplicate_imports(
        filename,
    )