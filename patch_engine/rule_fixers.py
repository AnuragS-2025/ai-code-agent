import re

# ==========================================
# Ruff Fixers (Active)
# ==========================================

def fix_e722(code_block: str) -> str:
    """
    Replace bare except with except Exception.
    """
    return code_block.replace("except:", "except Exception:")


def fix_f401(code_block: str) -> str:
    """
    Remove an unused import statement.
    Assumes extractor returns only the offending import statement.
    """
    lines = code_block.splitlines()
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            continue
        filtered.append(line)
    return "\n".join(filtered).rstrip() + "\n"


def fix_f811(code_block: str) -> str:
    """
    Remove duplicate import statements inside a block.
    """
    seen = set()
    result = []
    for line in code_block.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            if stripped in seen:
                continue
            seen.add(stripped)
        result.append(line)
    return "\n".join(result).rstrip() + "\n"


def fix_e402(code_block: str) -> str:
    """
    Placeholder.

    Import ordering is handled by update_imports()
    and cleanup_file().
    """
    return code_block


def fix_w291(code_block: str) -> str:
    """
    Remove trailing whitespaces from each line.
    """
    return "\n".join(line.rstrip() for line in code_block.splitlines()) + "\n"


def fix_w293(code_block: str) -> str:
    """
    Remove whitespace from blank lines.
    """
    return "\n".join("" if not line.strip() else line for line in code_block.splitlines()) + "\n"


def fix_e303(code_block: str) -> str:
    """
    Too many blank lines (collapses 3+ consecutive newlines down to 2).
    """
    return re.sub(r"\n{3,}", "\n\n", code_block)


# ==========================================
# Bandit Fixers (Active)
# ==========================================

def fix_b307(code_block: str) -> str:
    """
    Replace eval() with ast.literal_eval().
    """
    return re.sub(r"\beval\s*\(", "ast.literal_eval(", code_block)


def fix_b110(code_block: str) -> str:
    """
    Placeholder.
    Auto-fix not yet implemented.
    """
    return code_block


def fix_b105(code_block: str) -> str:
    """
    Replace a hardcoded password with an environment variable.
    """
    return re.sub(
        r'(?i)\bpassword\s*=\s*["\'].*?["\']',
        'password = os.getenv("PASSWORD", "")',
        code_block,
        count=1,
    )


# ==========================================
# Semgrep Fixers (Active)
# ==========================================

def fix_no_eval(code_block: str) -> str:
    """
    Same fix as Bandit B307.
    """
    return fix_b307(code_block)


# ==========================================
# Experimental / Future Fixers
#
# These are intentionally NOT registered in
# rule_registry.py until they are validated.
# ==========================================

def fix_f841(code_block: str) -> str:
    """
    TODO: Remove unused local variable assignments completely.
    Simple line-based approach for now; needs AST to verify scope and safely remove.
    """
    lines = code_block.splitlines()
    filtered = [
        line for line in lines 
        if not re.match(r"^\s*[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*[^=]+$", line)
    ]
    return "\n".join(filtered).rstrip() + "\n"


def fix_f821(code_block: str) -> str:
    """TODO: Handle undefined names."""
    return code_block


def fix_e305(code_block: str) -> str:
    """TODO: Requires AST analysis to evaluate top-level spacing safely."""
    return code_block


def fix_up006(code_block: str) -> str:
    """TODO: Upgrade to standard collection generics (requires import cleanup)."""
    return code_block


def fix_up007(code_block: str) -> str:
    """TODO: Upgrade to | syntax (must handle complex/nested Unions)."""
    return code_block


def fix_sim105(code_block: str) -> str:
    """TODO: Replace try-except-pass (requires injection of contextlib import)."""
    return code_block


def fix_c401(code_block: str) -> str:
    """TODO: Generator-to-set comprehension rewrite."""
    return code_block