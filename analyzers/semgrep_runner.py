import json
import subprocess
from typing import AbstractSet

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)


def run_semgrep(
    project_path: str,
    exclude_dirs: AbstractSet[str],
    # 🎯 FIX 1: Changed 'auto' to 'p/python' to explicitly load ALL Python OWASP rules!
    config: str = "p/python" 
) -> dict:
    """
    Runs Semgrep and returns parsed JSON output.

    Args:
        project_path: File or directory to scan
        exclude_dirs: Directories to exclude
        config: Semgrep configuration (default: p/python)
    """
    logger.info("[✓] Running Semgrep...")

    command = [
        "semgrep",
        "scan",
        f"--config={config}",
        "--json",
        project_path
    ]

    core_exclusions = set(exclude_dirs)
    global_defaults = {"tests", "venv", ".venv", "node_modules", "frontend", ".ruff_cache", "logs"}
    final_exclusions = core_exclusions.union(global_defaults)

    for directory in final_exclusions:
        command.extend(["--exclude", directory])

    # 🎯 FIX 2: Bulletproof subprocess wrapper with 300 seconds timeout
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300  # Will not hang infinitely
        )
    except subprocess.TimeoutExpired:
        logger.error("❌ Semgrep execution timed out after 300 seconds.")
        return {}
    except Exception as e:
        logger.error(f"❌ Semgrep execution OS-level crash: {e}")
        return {}

    if result.returncode not in (0, 1):
        logger.error("❌ Semgrep execution failed with return code %d.", result.returncode)
        if result.stderr.strip():
            logger.error("Semgrep Stderr Context:\n%s", result.stderr)
        return {}

    logger.info("✔ Semgrep analysis completed.")

    if result.stderr.strip():
        logger.warning("Semgrep Operational Warnings:\n%s", result.stderr)

    if not result.stdout.strip():
        return {}

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        logger.exception("❌ Failed to parse Semgrep JSON output.")
        logger.debug("Raw unparsed stdout: %s", result.stdout)
        return {}