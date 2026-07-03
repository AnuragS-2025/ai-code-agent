# patch_engine/plugins/base_plugin.py
from abc import ABC, abstractmethod
from typing import Callable, Literal, Dict, Any, Union


class BaseRulePlugin(ABC):
    """
    Abstract base class defining the common interface that every auto-fix rule plugin 
    must implement to safely integrate with the patch engine.
    """

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """
        Returns the unique identifier for the rule (e.g., 'B307', 'no-eval').
        """
        ...

    @property
    @abstractmethod
    def rule_type(self) -> Literal["block", "file"]:
        """
        Returns the targeting scope of the rule:
        - 'block': Modifies a specific code fragment or AST node.
        - 'file': Performs operations on the entire file context.
        """
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Returns a short summary describing what structural issue this rule resolves.
        """
        ...

    @property
    @abstractmethod
    def fixer(self) -> Union[Callable[[str], str], Callable[[str], None]]:
        """
        Returns the callable execution routine responsible for fixing the issue.
        
        - For 'block' type rules: The callable receives the extracted code string 
          and must return the transformed/repaired code block string: Callable[[str], str]
        - For 'file' type rules: The callable receives the target absolute file path string 
          and performs adjustments directly on the file system, returning nothing: Callable[[str], None]
        """
        ...

    @property
    def extra_metadata(self) -> Dict[str, Any]:
        """
        Extensible metadata mapping designed to future-proof the plugin API.
        
        Subclasses can optionally override this property to supply arbitrary internal engine 
        flags (e.g., severity, supported_analyzer, requires_ast, ai_allowed) without breaking 
        the foundational base contract or requiring modifications to the registry loader.
        
        Returns:
            Dict[str, Any]: A dictionary containing supplementary rule capabilities.
        """
        return {}