"""Runner module for executing the Bandit security analysis tool as a sub-process.

Implements structural recursive tracking markers and explicit directory exclusion
strategies for virtual environments and configuration caches.
"""

import json
import os
import subprocess
from utils.logger import get_logger

logger = get_logger(__name__)


def run_bandit(target: str | list[str]) -> dict:
    """Execute Bandit structural audits over targeted resources with environment exclusions.

    Args:
        target (str | list[str]): Absolute directory route target string, module file,
                                  or explicit list tracking sequences.

    Returns:
        dict: Raw JSON document structure map holding vulnerability configurations.
    """
    logger.info("[✓] Running Bandit...")

    # Build command conditionally to handle directory recursion and avoid dependency noise
    if isinstance(target, str):
        if os.path.isdir(target):
            command = [
                "bandit",
                "-r",
                target,
                "-f",
                "json",
                "-x",
                "venv,.venv,__pycache__,.git,.ruff_cache"
            ]
        else:
            command = [
                "bandit",
                "-f",
                "json",
                target
            ]
    else:
        command = [
            "bandit",
            "-f",
            "json",
            *target
        ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    # Bandit operational status mapping codes: 0 (No concerns), 1 (Vulnerabilities found)
    if result.returncode not in (0, 1):
        logger.error("❌ Bandit execution failed with return code %d.", result.returncode)
        if result.stderr.strip():
            logger.error("Bandit Stderr Context:\n%s", result.stderr)
        return {}

    logger.info("✔ Bandit analysis completed.")

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)

    except json.JSONDecodeError:
        logger.exception("❌ Failed to decode Bandit JSON stdout output.")
        logger.debug("Raw unparsed stdout: %s", result.stdout)
        return {}