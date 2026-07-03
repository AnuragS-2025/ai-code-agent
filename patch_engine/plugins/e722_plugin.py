from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_e722


class E722Plugin(BaseRulePlugin):
    """
    Plugin implementation for Ruff rule E722.

    Replaces bare 'except:' clauses with
    'except Exception:'.
    """

    @property
    def rule_id(self) -> str:
        return "E722"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Replace bare except"

    @property
    def fixer(self):
        return fix_e722