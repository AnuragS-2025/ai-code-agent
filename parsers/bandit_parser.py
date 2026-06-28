def parse_bandit(bandit_data):
    """
    Converts Bandit JSON output into a clean summary.
    """

    results = bandit_data.get("results", [])

    if not results:
        return "No security issues found."

    issues = {}

    for issue in results:

        rule = issue.get("test_id", "Unknown")

        description = issue.get("issue_text", "")

        severity = issue.get("issue_severity", "")

        filename = issue.get("filename", "")

        if rule not in issues:

            issues[rule] = {
                "description": description,
                "severity": severity,
                "files": []
            }

        if filename not in issues[rule]["files"]:
            issues[rule]["files"].append(filename)

    summary = []

    for rule, data in issues.items():

        files = ", ".join(data["files"])

        summary.append(
            f"{rule}: {data['description']} "
            f"(Severity: {data['severity']}, Files: {files})"
        )

    return "\n".join(summary)