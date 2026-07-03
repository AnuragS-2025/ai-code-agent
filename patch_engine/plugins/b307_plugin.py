from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_b307


class B307Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "B307"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Replace eval()"

    @property
    def fixer(self):
        return fix_b307