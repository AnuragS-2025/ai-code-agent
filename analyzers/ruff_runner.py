import json
import subprocess


def run_ruff(python_files):
    """
    Runs Ruff and returns parsed JSON output.
    """

    print("[✓] Running Ruff...\n")

    result = subprocess.run(
        [
            "ruff",
            "check",
            "--output-format=json",
            *python_files
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    print("✔ Ruff analysis completed.\n")

    if not result.stdout.strip():
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return []