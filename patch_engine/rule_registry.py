from patch_engine.rule_fixers import (
    fix_e722,
    fix_b307,
    fix_f401,
    fix_f811,
    fix_e402,
)


RULE_FIXERS = {
    "E722": fix_e722,
    "B307": fix_b307,
    "F401": fix_f401,
    "F811": fix_f811,
    "E402": fix_e402,
}