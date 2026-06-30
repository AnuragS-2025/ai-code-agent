def parse_bandit(bandit_data):
    """
    Parse Bandit JSON output into structured issues.
    """

    if not bandit_data:
        return []

    results = bandit_data.get("results", [])

    if not results:
        return []

    issues = []

    for issue in results:

        issues.append(
            {
                "rule": issue.get("test_id", "Unknown"),
                "message": issue.get("issue_text", ""),
                "file": issue.get("filename", ""),
                "line": issue.get("line_number", 0),
                "column": issue.get("col_offset", 0),
                "severity": issue.get("issue_severity", ""),
                "confidence": issue.get("issue_confidence", ""),
            }
        )

    return issues