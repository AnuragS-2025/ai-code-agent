def parse_semgrep(semgrep_data):
    """
    Converts Semgrep JSON output into a clean summary.
    """

    results = semgrep_data.get("results", [])

    if not results:
        return "No Semgrep findings."

    issues = {}

    for issue in results:

        rule = issue.get("check_id", "Unknown")

        message = issue.get("extra", {}).get("message", "")

        filename = issue.get("path", "")

        if rule not in issues:

            issues[rule] = {
                "message": message,
                "files": []
            }

        if filename not in issues[rule]["files"]:
            issues[rule]["files"].append(filename)

    summary = []

    for rule, data in issues.items():

        files = ", ".join(data["files"])

        summary.append(
            f"{rule}: {data['message']} (Files: {files})"
        )

    return "\n".join(summary)