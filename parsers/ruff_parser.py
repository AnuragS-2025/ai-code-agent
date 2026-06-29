def parse_ruff(ruff_data):
    """
    Parse Ruff JSON output into structured issues.
    """

    if not ruff_data:
        return []

    issues = []

    for issue in ruff_data:

        issues.append(
            {
                "rule": issue.get("code", "Unknown"),
                "message": issue.get("message", ""),
                "file": issue.get("filename", ""),
                "line": issue.get("location", {}).get("row", 0),
                "column": issue.get("location", {}).get("column", 0),
            }
        )

    return issues