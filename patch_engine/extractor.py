import ast
import os
from typing import Optional


def _node_contains_line(node: ast.AST, target_line: int) -> bool:
    """
    Checks if the given AST node spans across the target line number.
    """
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        # Python AST lines are 1-indexed
        return node.lineno <= target_line <= node.end_lineno
    return False


def _find_smallest_node(node: ast.AST, target_line: int) -> Optional[ast.AST]:
    """
    Recursively traverses the AST to find the deepest (smallest) logical block 
    node that contains the target line.
    """
    # Supported target compound/block statement types
    supported_nodes = (
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.If,
        ast.Try,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.With,
        ast.AsyncWith,
        ast.Match,
    )

    best_node = None
    if isinstance(node, supported_nodes) and _node_contains_line(node, target_line):
        best_node = node

    # Optimized Traversal: Only traverse down the subtree that actually contains the target line
    for child in ast.iter_child_nodes(node):
        if _node_contains_line(child, target_line):
            deep_node = _find_smallest_node(child, target_line)
            if deep_node:
                best_node = deep_node

    return best_node


def _extract_source(lines: list[str], start_line: int, end_line: int) -> tuple[str, str]:
    """
    Extracts explicit lines from the source list, keeping track of 
    the indentation of the block's starting line.
    """
    # Convert 1-indexed AST lines to 0-indexed list indices
    start_idx = start_line - 1
    end_idx = end_line  # End line inclusive slicing

    block_lines = lines[start_idx:end_idx]
    block_code = "".join(block_lines)

    # First line se original indentation preserve karo
    first_line = lines[start_idx]
    indent_size = len(first_line) - len(first_line.lstrip())
    indent = first_line[:indent_size]

    return block_code, indent


def extract_code_block(
    filename: str,
    line_number: int,
) -> dict:
    """
    Extracts the smallest logical AST-based code block containing an issue line.
    Falls back gracefully to a single line extraction if any exception occurs.
    
    Returns:
    {
        "code": str,
        "indent": str,
        "start": int,   # Line number where the block starts
        "end": int      # Line number where the block ends
    }
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(filename)

    with open(filename, "r", encoding="utf-8") as file:
        source_code = file.read()

    lines = source_code.splitlines(keepends=True)

    if line_number < 1 or line_number > len(lines):
        raise ValueError(f"Invalid line number: {line_number}. File has {len(lines)} lines.")

    try:
        # Parse complete syntax tree
        tree = ast.parse(source_code, filename=filename)
        target_node = _find_smallest_node(tree, line_number)
        
        if target_node:
            code, indent = _extract_source(lines, target_node.lineno, target_node.end_lineno)
            return {
                "code": code,
                "indent": indent,
                "start": target_node.lineno,
                "end": target_node.end_lineno,
            }
            
    except Exception:
        # Catch generic exceptions (SyntaxError, UnicodeDecodeError, etc.) safely
        pass

    # --------------------------------------
    # Fallback: Single Line Block Extraction
    # --------------------------------------
    # Fallback intentionally extracts only the target line 
    # to safeguard against corrupted file states during dynamic line-scanning.
    fallback_line = lines[line_number - 1]
    indent_size = len(fallback_line) - len(fallback_line.lstrip())
    indent = fallback_line[:indent_size]

    return {
        "code": fallback_line,
        "indent": indent,
        "start": line_number,
        "end": line_number,
    }


def extract_multiple_blocks(
    filename: str,
    line_numbers: list[int],
) -> list[dict]:
    """
    Extracts multiple blocks sorted by line numbers uniquely.
    """
    blocks = []

    for line in sorted(set(line_numbers)):
        data = extract_code_block(filename, line)
        blocks.append(
            {
                "line": line,
                "code": data["code"],
                "indent": data["indent"],
                "start": data["start"],
                "end": data["end"],
            }
        )

    return blocks


# ==========================================
# Local Verification / Test Runner
# ==========================================
if __name__ == "__main__":
    test_file = "app.py"
    if os.path.exists(test_file):
        data = extract_code_block(test_file, 42)
        print("=" * 60)
        print("EXTRACTED AST BLOCK")
        print("=" * 60)
        print(data["code"])
        print("=" * 60)
        print("METADATA")
        print("=" * 60)
        print(f"Indent : {repr(data['indent'])}")
        print(f"Range  : {data['start']} -> {data['end']}")