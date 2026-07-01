import argparse

from pipeline import run_pipeline   # or test_patch_pipeline


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Auto Fixer"
    )

    parser.add_argument(
        "target",
        help="Python file to analyze and fix",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum scan/fix iterations",
    )

    args = parser.parse_args()

    run_pipeline(
        target_file=args.target,
        max_iterations=args.max_iterations,
    )


if __name__ == "__main__":
    main()