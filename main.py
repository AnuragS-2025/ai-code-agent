# main.py
import argparse
import sys
from pipeline import run_pipeline
from utils.file_discovery import discover_python_files


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Auto Fixer"
    )

    # Changed from 'target' to 'targets' with nargs="+"
    parser.add_argument(
        "targets",
        nargs="+",
        help="Python files or directories to analyze",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum scan/fix iterations",
    )

    args = parser.parse_args()

    # Discover all python files within the targets
    target_files = discover_python_files(args.targets)

    if not target_files:
        print("❌ No Python (.py) files found in the specified targets.")
        sys.exit(1)

    print(f"🔍 Found {len(target_files)} file(s) to analyze: {target_files}")

    # Pass the resolved files list to the pipeline
    run_pipeline(
        target_files=target_files,
        max_iterations=args.max_iterations,
    )


if __name__ == "__main__":
    main()