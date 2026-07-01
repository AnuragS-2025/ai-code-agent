def parse_semgrep(semgrep_data):
    """
    Parse Semgrep JSON output into structured issues.
    """

    if not semgrep_data:
        return []

    results = semgrep_data.get("results", [])

    if not results:
        return []

    issues = []

    for issue in results:

        issues.append(
            {
                "rule": issue.get("check_id", "Unknown"),
                "message": issue.get("extra", {}).get("message", ""),
                "file": issue.get("path", ""),
                "line": issue.get("start", {}).get("line", 0),
                "column": issue.get("start", {}).get("col", 0),
                "severity": issue.get("extra", {}).get("severity", ""),
            }
        )

    return issues