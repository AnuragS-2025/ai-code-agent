from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_f811


class F811Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "F811"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Remove duplicate import"

    @property
    def fixer(self):
        return fix_f811