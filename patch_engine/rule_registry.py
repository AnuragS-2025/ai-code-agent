from patch_engine.rule_fixers import (
    fix_e722,
    fix_f401,
    fix_f811,
    fix_e402,
    fix_w291,
    fix_w293,
    fix_e303,
    fix_b307,
    # fix_b110,  # Removed temporarily until fully implemented
    fix_b105,
    fix_no_eval,
)

RULES = {

    # ==========================================
    # Ruff
    # ==========================================

    "E722": {
        "type": "block",
        "fixer": fix_e722,
        "description": "Replace bare except",
    },

    "F401": {
        "type": "block",
        "fixer": fix_f401,
        "description": "Remove unused import",
    },

    "F811": {
        "type": "block",
        "fixer": fix_f811,
        "description": "Remove duplicate import",
    },

    "E402": {
        "type": "file",
        "fixer": fix_e402,
        "description": "Move imports to top",
    },

    "W291": {
        "type": "block",
        "fixer": fix_w291,
        "description": "Remove trailing whitespaces",
    },

    "W293": {
        "type": "block",
        "fixer": fix_w293,
        "description": "Remove whitespace from blank lines",
    },

    "E303": {
        "type": "block",
        "fixer": fix_e303,
        "description": "Collapse excessive blank lines",
    },

    # ==========================================
    # Bandit
    # ==========================================

    "B307": {
        "type": "block",
        "fixer": fix_b307,
        "description": "Replace eval()",
    },

    # "B110": {
        # "type": "block",
        # "fixer": fix_b110,
        # "description": "Try Except Pass",
    # },

    "B105": {
        "type": "block",
        "fixer": fix_b105,
        "description": "Hardcoded password",
    },

    # ==========================================
    # Semgrep
    # ==========================================

    "no-eval": {
        "type": "block",
        "fixer": fix_no_eval,
        "description": "Replace eval()",
    },

}