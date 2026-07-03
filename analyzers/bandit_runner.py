import json
import subprocess

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)


def run_bandit(python_files: list[str]) -> dict:
    """
    Runs Bandit and returns parsed JSON output.
    """

    # Log analyzer start
    logger.info("[✓] Running Bandit...")

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

    # Bandit process-level failure checking (Log analyzer failures)
    # Bandit standard target return codes are: 0 (No issues), 1 (Issues found)
    if result.returncode not in (0, 1):
        logger.error("❌ Bandit execution failed with return code %d.", result.returncode)
        if result.stderr.strip():
            logger.error("Bandit Stderr Context:\n%s", result.stderr)
        return {}

    # Log analyzer completion (Moved after process boundary verification)
    logger.info("✔ Bandit analysis completed.")

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)
        
    except json.JSONDecodeError:
        # Use logger.exception to automatically capture the full JSON decode stack trace
        logger.exception("❌ Failed to decode Bandit JSON stdout output.")
        logger.debug("Raw unparsed stdout: %s", result.stdout)
        return {}