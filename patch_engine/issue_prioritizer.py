# patch_engine/issue_prioritizer.py

# Rule priority mapping: higher values mean higher fix priority.
# Categorized strictly by: Security > Correctness > Cleanup > Formatting
RULE_PRIORITIES = {
    # --- Security Issues ---
    "B307": 100,
    "no-eval": 90,
    "B105": 80,
    
    # --- Correctness Issues ---
    "E722": 70,
    "F811": 60,
    
    # --- Cleanup / Refactoring Issues ---
    "F401": 50,
    "E402": 40,
    
    # --- Formatting / Style Issues ---
    "E303": 30,
    "W291": 20,
    "W293": 10,
}

def prioritize_issues(issues: list[dict]) -> list[dict]:
    """
    Sorts the merged and filtered issue list based on rule priority weights.
    Unknown rules default to the lowest priority score.
    
    Args:
        issues (list[dict]): A list of detected rule issues.
        
    Returns:
        list[dict]: The sorted list of issues, prioritized highest to lowest.
    """
    def get_priority_score(issue: dict) -> int:
        rule = issue.get("rule")
        # Unknown rules default to 0 to ensure they sit at the bottom
        return RULE_PRIORITIES.get(rule, 0)

    # Sort descending so the highest priority rule sits at index 0
    return sorted(issues, key=get_priority_score, reverse=True)