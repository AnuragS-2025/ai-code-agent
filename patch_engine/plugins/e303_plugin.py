from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_e303


class E303Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "E303"

    @property
    def rule_type(self) -> str:
        return "block"

    @property
    def description(self) -> str:
        return "Collapse excessive blank lines"

    @property
    def fixer(self):
        return fix_e303