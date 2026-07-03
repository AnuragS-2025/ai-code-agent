from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_w291


class W291Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "W291"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Remove trailing whitespaces"

    @property
    def fixer(self):
        return fix_w291