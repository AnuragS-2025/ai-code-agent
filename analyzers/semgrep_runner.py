import json
import subprocess


def run_semgrep(project_path, exclude_dirs):
    """
    Runs Semgrep and returns parsed JSON output.
    """

    print("[✓] Running Semgrep...\n")

    command = [
        "semgrep",
        "scan",
        "--config=auto",
        "--json",
        project_path
    ]

    for directory in exclude_dirs:
        command.extend(["--exclude", directory])

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    print("✔ Semgrep analysis completed.\n")

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}