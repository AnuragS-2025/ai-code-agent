from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_w293


class W293Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "W293"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Remove whitespace from blank lines"

    @property
    def fixer(self):
        return fix_w293