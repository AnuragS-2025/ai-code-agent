import re


# ==========================================
# Ruff
# ==========================================

def fix_e722(code_block: str) -> str:
    """
    Replace bare except with except Exception.
    """

    return code_block.replace(
        "except:",
        "except Exception:"
    )


# ==========================================
# Bandit
# ==========================================

def fix_b307(code_block: str) -> str:
    """
    Replace eval() with ast.literal_eval().
    """

    return code_block.replace(
        "eval(",
        "ast.literal_eval("
    )


# ==========================================
# Placeholder Fixers
# ==========================================

def fix_f401(code_block: str) -> str:
    """
    Remove an unused import.
    """

    return ""


def fix_f811(code_block: str) -> str:
    """
    Duplicate imports are handled by Import Manager.
    """

    return code_block


def fix_e402(code_block: str) -> str:
    """
    Import ordering handled elsewhere.
    """

    return code_block