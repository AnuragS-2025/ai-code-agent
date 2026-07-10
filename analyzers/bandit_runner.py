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

    # Exclusions combined with strict absolute and wildcards patterns
    exclusions = "tests,*/tests/*,venv,*/venv/*,.venv,*/.venv/*,__pycache__,.git,.ruff_cache,node_modules,frontend"

    # Build command conditionally. 
    if isinstance(target, str):
        if os.path.isdir(target):
            command = [
                "bandit", "-r", target, "-f", "json", "-s", "B101", "-x", exclusions
            ]
        else:
            command = [
                "bandit", "-f", "json", "-s", "B101", "-x", exclusions, target
            ]
    else:
        # 🎯 FIX: Handled single directory wrapped inside a list target parameter
        if len(target) == 1 and os.path.isdir(target[0]):
            command = [
                "bandit", "-r", target[0], "-f", "json", "-s", "B101", "-x", exclusions
            ]
        else:
            command = [
                "bandit", "-f", "json", "-s", "B101", "-x", exclusions, *target
            ]

    # Bulletproof Try-Except shield against KeyboardInterrupt & OS crashes
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300
        )
        # =================================================================
        # REQUESTED DEBUG LOGS: Added immediately after execution
        # =================================================================
        logger.info("Bandit command: %s", " ".join(command))
        logger.info("Bandit return code: %s", result.returncode)
        logger.info("Bandit stdout:\n%s", result.stdout)
        
    except subprocess.TimeoutExpired:
        logger.error("❌ Bandit execution timed out after 300 seconds.")
        return {}
    except KeyboardInterrupt:
        logger.error("❌ Bandit execution was interrupted forcefully (KeyboardInterrupt).")
        return {}
    except Exception as e:
        logger.error(f"❌ Bandit OS-level crash sequence: {e}")
        return {}

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