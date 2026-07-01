from patch_engine.rule_fixers import (
    fix_e722,
    fix_f401,
    fix_f811,
    fix_e402,
    fix_b307,
    fix_b110,
    fix_b105,
    fix_no_eval,
)

RULE_FIXERS = {
    "E722": fix_e722,
    "F401": fix_f401,
    "F811": fix_f811,
    "E402": fix_e402,
    "B307": fix_b307,
    "B110": fix_b110,
    "B105": fix_b105,
    "no-eval": fix_no_eval,
}