import json
import subprocess


def run_bandit(python_files):
    """
    Runs Bandit and returns parsed JSON output.
    """

    print("[✓] Running Bandit...\n")

    result = subprocess.run(
        [
            "bandit",
            "-f",
            "json",
            *python_files
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    print("✔ Bandit analysis completed.\n")

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}