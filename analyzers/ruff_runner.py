import json
import subprocess

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)


def run_ruff(python_files: list[str]) -> list[dict]:
    """
    Runs Ruff and returns parsed JSON output.
    """

    # Log analyzer start
    logger.info("[✓] Running Ruff...")

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

    # Ruff error handling (Log analyzer failures)
    if result.returncode not in (0, 1):
        logger.error("❌ Ruff execution failed with return code %d.", result.returncode)
        if result.stderr.strip():
            logger.error("Ruff Stderr Context:\n%s", result.stderr)
        return []

    # Log analyzer completion moved after returncode verification
    logger.info("✔ Ruff analysis completed.")

    if not result.stdout.strip():
        return []

    try:
        return json.loads(result.stdout)

    except json.JSONDecodeError:
        # Use logger.exception to automatically capture the JSON decode stack trace
        logger.exception("❌ Failed to decode Ruff JSON stdout output.")
        logger.debug("Raw unparsed stdout: %s", result.stdout)
        return []