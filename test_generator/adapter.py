from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class AdaptedModuleInfo:
    """Immutable representation of module info tailored for TestGenerator."""

    file_path: str
    module_name: str
    functions: List[str] = field(default_factory=list)
    classes: Dict[str, List[str]] = field(default_factory=dict)


def adapt_module_info(project_module: Any) -> AdaptedModuleInfo:
    """Adapts a ProjectIndex.ModuleInfo object into an AdaptedModuleInfo instance.

    Mapping rules:
    - file_path: Extracted from project_module.path
    - module_name: Stem of the file path
    - functions: Kept as-is from project_module.functions
    - classes: Converted from a list of strings to a dict with empty list values
    """
    path_str = project_module.path
    module_name = Path(path_str).stem

    # Transform list[str] into dict[str, list[str]] as required
    adapted_classes = {
        class_name: [] for class_name in project_module.classes
    }

    return AdaptedModuleInfo(
        file_path=path_str,
        module_name=module_name,
        functions=project_module.functions,
        classes=adapted_classes,
    )