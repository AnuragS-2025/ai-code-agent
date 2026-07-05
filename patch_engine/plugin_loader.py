import importlib
import inspect
import pkgutil

# Import the base package namespace and the abstraction contract
import patch_engine.plugins
from patch_engine.plugins.base_plugin import BaseRulePlugin


def load_plugins() -> list[BaseRulePlugin]:
    """
    Scans the patch_engine/plugins package directory dynamically, imports
    all detected modules in a deterministic order, and extracts initialized 
    valid rule plugin instances.
    
    Guarantees that broken modules do not crash the engine, skips abstract/base 
    contracts, and isolates discovery completely from registration steps.
    
    Returns:
        list[BaseRulePlugin]: A list of instantiated rule plugin objects implementing
                             the BaseRulePlugin interface.
    """
    discovered_instances: list[BaseRulePlugin] = []
    package = patch_engine.plugins

    # 1. Collect and sort all modules to guarantee deterministic order across different OS/environments
    modules_to_process = []
    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        if is_pkg:
            continue  # Skip nested packages to maintain a clean flat-plugin layout
        
        if module_name.endswith(".base_plugin"):
            continue  # Explicitly skip base contract definitions file
            
        modules_to_process.append(module_name)
    
    # Alphabetical sort ensures stability in unit testing
    modules_to_process.sort()

    # 2. Iterate through the sorted module paths
    for module_name in modules_to_process:
        try:
            # 3. Dynamically import the plugin module
            module = importlib.import_module(module_name)
            
            # 4. Inspect module attributes to locate concrete implementation classes
            for _, obj_class in inspect.getmembers(module, inspect.isclass):
                # Safeguard Filters:
                # - Must be defined directly within the current module (ignores external imports)
                # - Must be a subclass of BaseRulePlugin
                # - Must not be the BaseRulePlugin class itself
                # - Must not be an Abstract Base Class
                if (
                    obj_class.__module__ == module.__name__
                    and issubclass(obj_class, BaseRulePlugin) 
                    and obj_class is not BaseRulePlugin 
                    and not inspect.isabstract(obj_class)
                ):
                    try:
                        # 5. Initialize the plugin via its parameterless constructor
                        plugin_instance = obj_class()
                        discovered_instances.append(plugin_instance)
                    except Exception:
                        # Fail-silent execution wrapper: prevents one buggy constructor from killing the loader
                        # TODO: Log instantiation failure using 'exc' when logging system is integrated
                        pass
                        
        except Exception:
            # Catch file-level syntax errors or missing third-party imports gracefully
            # TODO: Log import failure using 'exc' when logging system is integrated
            pass

    return discovered_instances