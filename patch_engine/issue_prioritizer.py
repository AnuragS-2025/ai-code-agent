# patch_engine/issue_prioritizer.py
from config.settings import settings

def prioritize_issues(issues: list[dict]) -> list[dict]:
    """
    Sorts the merged and filtered issue list based on rule priority weights
    loaded from the configuration system. Unknown rules default to the lowest priority score.
    
    Args:
        issues (list[dict]): A list of detected rule issues.
        
    Returns:
        list[dict]: The sorted list of issues, prioritized highest to lowest.
    """
    # Load the priority mapping dynamically from the config module
    rule_priorities = settings.rule_priorities

    def get_priority_score(issue: dict) -> int:
        rule = issue.get("rule")
        # Unknown rules default to 0 to ensure they sit at the bottom
        return rule_priorities.get(rule, 0)

    # Sort descending so the highest priority rule sits at index 0
    return sorted(issues, key=get_priority_score, reverse=True)