from patch_engine.plugins.base_plugin import BaseRulePlugin
from patch_engine.rule_fixers import fix_e402


class E402Plugin(BaseRulePlugin):

    @property
    def rule_id(self) -> str:
        return "E402"

    @property
    def rule_type(self) -> str:
        return "file"

    @property
    def description(self) -> str:
        return "Move imports to top"

    @property
    def fixer(self):
        return fix_e402