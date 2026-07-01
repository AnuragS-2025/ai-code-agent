import json
import subprocess


def run_semgrep(
    project_path,
    exclude_dirs,
    config="auto"
):
    """
    Runs Semgrep and returns parsed JSON output.

    Args:
        project_path: File or directory to scan
        exclude_dirs: Directories to exclude
        config: Semgrep configuration (default: auto)
    """

    print("[✓] Running Semgrep...\n")

    command = [
        "semgrep",
        "scan",
        f"--config={config}",
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

    # Print Semgrep warnings/errors if any
    if result.stderr.strip():
        print(result.stderr)

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)

    except json.JSONDecodeError:
        print("❌ Failed to parse Semgrep JSON output.")
        return {}


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    findings = run_semgrep(
        "app.py",
        set(),
        config="semgrep_test_rule.yml"
    )

    print(json.dumps(findings, indent=4))