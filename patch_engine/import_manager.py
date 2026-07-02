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
# File-Level Import Fixers
# ==========================================

def move_imports_to_top(filename: str) -> None:
    """
    Safely moves ONLY top-level imports to the top of the file,
    preserving shebangs, encoding declarations, and module-level docstrings.
    Local/indented imports inside functions/classes are left completely untouched.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    header_lines = []
    import_lines = []
    code_lines = []

    shebang_or_encoding_pattern = re.compile(r"^(#!/|#\s*-\*-)")
    
    in_docstring = False
    docstring_quotes = None
    docstring_collected = False

    for line in lines:
        # Pura logic original 'line' aur uske 'stripped' version ko track karega
        stripped = line.strip()

        # Case 1: Inside a top-level docstring
        if in_docstring:
            header_lines.append(line)
            if docstring_quotes and stripped.endswith(docstring_quotes):
                in_docstring = False
                docstring_collected = True
            continue

        # Case 2: Detect start of a module-level docstring (only at the absolute top)
        if not docstring_collected and not import_lines and not code_lines and (stripped.startswith('"""') or stripped.startswith("'''")):
            header_lines.append(line)
            quotes = '"""' if stripped.startswith('"""') else "'''"
            if len(stripped) >= 6 and stripped.endswith(quotes):
                docstring_collected = True
            else:
                in_docstring = True
                docstring_quotes = quotes
            continue

        # Case 3: Shebang or encoding declarations (absolute top of file)
        if not import_lines and not code_lines and shebang_or_encoding_pattern.match(line):
            header_lines.append(line)
            continue

        # Case 4: Top-level imports ONLY (Fixed: checking original line without strip)
        if line.startswith(("import ", "from ")):
            import_lines.append(line)
            continue

        # Case 5: Normal Code & local indented imports (def foo(): import os)
        code_lines.append(line)

    # --- Reconstruction ---
    header_part = "".join(header_lines)
    import_part = "".join(import_lines)
    code_part = "".join(code_lines).lstrip("\n") 

    final_content = ""
    if header_part:
        final_content += header_part
        if not header_part.endswith("\n"):
            final_content += "\n"
        if import_part:
            final_content += "\n"  # Gap between header/docstring and imports

    if import_part:
        final_content += import_part
        final_content += "\n"  # Gap between imports and code

    final_content += code_part

    with open(filename, "w", encoding="utf-8") as file:
        file.write(final_content)


def sort_imports(filename: str) -> None:
    """
    Placeholder for future I001 / isort logic.
    Kept here as requested for future readiness without active imports.
    """
    pass


# ==========================================
# Ensure Import Exists
# ==========================================

def ensure_import(
    filename: str,
    module: str,
) -> None:
    """
    Inserts a required import at the top-level import block.
    Note: Future improvement will align this with shebang/docstring headers.
    """
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

    for line in lines:
        # Fixed: check top-level imports accurately to avoid touching local ones
        if line.startswith(("import ", "from ")):
            stripped = line.strip()
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
    Perform block-level post-patch import tasks.
    Independent of E402 file fixer.
    """
    ensure_required_imports(
        filename,
        generated_patch,
    )
    remove_duplicate_imports(
        filename,
    )