from patch_engine.plugin_loader import load_plugins

# ==============================================================================
# Legacy Manual Registrations
# ==============================================================================
# Kept empty as all core rules have been fully migrated to the plugin architecture.
# New rules should be implemented as plugins rather than added here.
MANUAL_RULES = {}


# ==============================================================================
# Dynamic Rule Aggregation Layer
# ==============================================================================

def _initialize_rules() -> dict:
    """
    Assembles the master RULES dictionary by merging manual definitions with 
    dynamically discovered plugins. Plugins supersede manual definitions.
    """
    # 1. Initialize with a shallow copy of the manual configurations (currently empty)
    aggregated_rules = dict(MANUAL_RULES)
    
    # 2. Discover and evaluate runtime plugins
    discovered_plugins = load_plugins()
    
    # 3. Layer plugins over manual configurations to build the final registry
    for plugin in discovered_plugins:
        aggregated_rules[plugin.rule_id] = {
            "type": plugin.rule_type,
            "fixer": plugin.fixer,
            "description": plugin.description,
        }
        
    return aggregated_rules


# Public API consumed downstream by the pipeline.
# Preserves schema integrity and ensures backwards compatibility.
RULES = _initialize_rules()