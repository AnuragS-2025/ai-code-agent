import argparse
import sys
from pipeline import run_pipeline
from utils.file_discovery import discover_python_files

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Auto Fixer"
    )

    parser.add_argument(
        "targets",
        nargs="+",
        help="Python files or directories to analyze",
    )

    # Aligned with global settings fallback by switching default to None
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Override maximum scan/fix iterations",
    )

    args = parser.parse_args()

    # Log application startup
    logger.info("Initializing AI Code Auto Fixer...")

    try:
        # Discover all python files within the targets
        target_files = discover_python_files(args.targets)

        if not target_files:
            logger.error("❌ No Python (.py) files found in the specified targets.")
            sys.exit(1)

        # Log discovered target files cleanly using placeholders
        logger.info("🔍 Discovered %d target file(s) for analysis.", len(target_files))
        logger.debug("Discovered target files: %s", target_files)

        # Log pipeline execution start
        logger.info("Starting auto-fix pipeline execution...")
        
        # Pass the resolved files list to the pipeline (args.max_iterations passes None if omitted)
        run_pipeline(
            target_files=target_files,
            max_iterations=args.max_iterations,
        )

        # Log pipeline completion
        logger.info("Pipeline execution completed successfully.")

    except Exception as e:
        # Log unexpected fatal exceptions with full context before exiting
        logger.fatal("An unexpected fatal error occurred during execution: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()