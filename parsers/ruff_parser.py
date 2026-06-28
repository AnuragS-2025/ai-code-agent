def parse_ruff(ruff_data):
    """
    Converts Ruff JSON output into a clean summary.
    """

    if not ruff_data:
        return "No quality issues found."

    issues = {}

    for issue in ruff_data:

        rule = issue.get("code", "Unknown")

        message = issue.get("message", "")

        filename = issue.get("filename", "")

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