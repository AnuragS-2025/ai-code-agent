import json
import subprocess
from typing import AbstractSet

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)


def run_semgrep(
    project_path: str,
    exclude_dirs: AbstractSet[str],
    config: str = "auto"
) -> dict:
    """
    Runs Semgrep and returns parsed JSON output.

    Args:
        project_path: File or directory to scan
        exclude_dirs: Directories to exclude
        config: Semgrep configuration (default: auto)
    """

    # Log analyzer start
    logger.info("[✓] Running Semgrep...")

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

    # Fixed Bug: Strict process-level failure checking & early exit
    if result.returncode not in (0, 1):
        logger.error("❌ Semgrep execution failed with return code %d.", result.returncode)
        if result.stderr.strip():
            logger.error("Semgrep Stderr Context:\n%s", result.stderr)
        return {}

    # Log analyzer completion (Executes ONLY on successful runs)
    logger.info("✔ Semgrep analysis completed.")

    # Semgrep occasionally prints operational/deprecation warnings on stderr even during successful scans
    if result.stderr.strip():
        logger.warning("Semgrep Operational Warnings:\n%s", result.stderr)

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)

    except json.JSONDecodeError:
        # Use logger.exception to automatically capture the full JSON decode stack trace
        logger.exception("❌ Failed to parse Semgrep JSON output.")
        logger.debug("Raw unparsed stdout: %s", result.stdout)
        return {}


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":
    # Internal test execution block logger integration
    logger.info("Running local isolated runner test...")
    
    findings = run_semgrep(
        "app.py",
        set(),
        config="semgrep_test_rule.yml"
    )

    logger.debug("Test Execution Findings Output:\n%s", json.dumps(findings, indent=4))