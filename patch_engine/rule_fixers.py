import re


# ==========================================
# Ruff Fixers
# ==========================================

def fix_e722(code_block: str) -> str:
    """
    Replace bare except with except Exception.
    """

    return code_block.replace(
        "except:",
        "except Exception:"
    )


def fix_f401(code_block: str) -> str:
    """
    Remove an unused import statement.
    """

    lines = code_block.splitlines()

    filtered = []

    for line in lines:

        stripped = line.strip()

        if stripped.startswith("import "):
            continue

        if stripped.startswith("from "):
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
    E402 is handled by the Import Manager.
    """

    return code_block


# ==========================================
# Bandit Fixers
# ==========================================

def fix_b307(code_block: str) -> str:
    """
    Replace eval() with ast.literal_eval().
    """

    return re.sub(
        r"\beval\s*\(",
        "ast.literal_eval(",
        code_block,
    )


def fix_b110(code_block: str) -> str:
    """
    Currently unsupported.
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
# Semgrep Fixers
# ==========================================

def fix_no_eval(code_block: str) -> str:
    """
    Same fix as Bandit B307.
    """

    return fix_b307(code_block)