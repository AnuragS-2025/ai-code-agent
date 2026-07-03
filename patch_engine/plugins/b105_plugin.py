from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_b105


class B105Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "B105"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Hardcoded password"

    @property
    def fixer(self):
        return fix_b105