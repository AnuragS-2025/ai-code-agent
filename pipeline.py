# pipeline.py
from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep

from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep

from patch_engine.extractor import extract_code_block
from patch_engine.validator import validate_patch
from patch_engine.replacer import replace_code_block

from patch_engine.import_manager import (
    update_imports,
)

from patch_engine.file_fixers import cleanup_file
from patch_engine.rule_registry import RULES
from auto_fix_engine import generate_patch

# ==========================================
# Global Configuration & Safeguards
# ==========================================

# Explicitly allowed rules for AI to fix (defined at module level to avoid re-allocation)
AI_FALLBACK_RULES = {
    "no-eval",
}


def run_pipeline(target_files: list[str], max_iterations: int = 20) -> dict:
    """
    Runs the full auto-fix pipeline on a given list of target files.
    Returns a summary dictionary of the execution.
    """
    fixed_count = 0
    failed_issues = set()
    iteration = 0  # Safe initialization to prevent UnboundLocalError in summary

    # ==========================================
    # Re-analysis Loop
    # ==========================================
    for iteration in range(1, max_iterations + 1):

        print("\n" + "=" * 60)
        print(f"SCAN ITERATION {iteration}")
        print("=" * 60)

        # --------------------------------------
        # Run Ruff (Handles multiple files smoothly)
        # --------------------------------------
        ruff_issues = parse_ruff(
            run_ruff(target_files)
        )

        # --------------------------------------
        # Run Bandit (Handles multiple files smoothly)
        # --------------------------------------
        bandit_issues = parse_bandit(
            run_bandit(target_files)
        )

        # --------------------------------------
        # Run Semgrep (Runs iteratively for each target file in the scope)
        # --------------------------------------
        semgrep_issues = []
        for target_file in target_files:
            file_issues = parse_semgrep(
                run_semgrep(
                    target_file,
                    set(),
                    config="semgrep_test_rule.yml",
                )
            )
            semgrep_issues.extend(file_issues)

        # --------------------------------------
        # Merge Issues
        # --------------------------------------
        issues = (
            ruff_issues +
            bandit_issues +
            semgrep_issues
        )

        # --------------------------------------
        # Remove previously failed or unsupported issues
        # --------------------------------------
        issues = [
            issue
            for issue in issues
            if (
                issue["rule"],
                issue["message"],
                issue["file"],
            ) not in failed_issues
        ]

        if not issues:
            print("\n✔ No remaining fixable issues.")
            break

        # --------------------------------------
        # Pick first issue
        # --------------------------------------
        issue = issues[0]

        print("\n" + "=" * 60)
        print("ISSUE FOUND")
        print("=" * 60)
        print(issue)

        # --------------------------------------
        # Extract code block
        # --------------------------------------
        block = extract_code_block(
            issue["file"],
            issue["line"],
        )

        code_block = block["code"]

        if not code_block.strip():
            print(f"⚠ Could not extract block for {issue['rule']}")
            failed_issues.add(
                (
                    issue["rule"],
                    issue["message"],
                    issue["file"],
                )
            )
            continue

        print("\n" + "=" * 60)
        print("EXTRACTED BLOCK")
        print("=" * 60)
        print(code_block)
        
        # --------------------------------------
        # Choose Fixer Strategy (Guard Routing)
        # --------------------------------------
        if issue["rule"] in RULES:
            rule = RULES[issue["rule"]]
            print(f"⚡ Using built-in fixer for {issue['rule']}")
            print(f"Rule Type : {rule['type']}")
            fixed_block = rule["fixer"](code_block)

        elif issue["rule"] in AI_FALLBACK_RULES:
            print(f"🤖 Using AI fixer for {issue['rule']}")
            fixed_block = generate_patch(
                f"{issue['rule']}: {issue['message']}",
                code_block,
            )

        else:
            print(f"⚠ Skipping unsupported rule: {issue['rule']}")
            failed_issues.add(
                (
                    issue["rule"],
                    issue["message"],
                    issue["file"],
                )
            )
            continue

        # --------------------------------------
        # Generated Patch
        # --------------------------------------
        print("\n" + "=" * 60)
        print("GENERATED PATCH")
        print("=" * 60)

        if fixed_block.strip():
            print(fixed_block)
        else:
            print("[Code block removed]")

        # --------------------------------------
        # Validate Patch
        # --------------------------------------
        valid, message = validate_patch(fixed_block)

        print("\n" + "=" * 60)
        print("PATCH VALIDATION")
        print("=" * 60)
        print(message)

        if not valid:
            print("❌ Validation failed.")
            failed_issues.add(
                (
                    issue["rule"],
                    issue["message"],
                    issue["file"],
                )
            )
            continue

        # --------------------------------------
        # Skip unchanged patch
        # --------------------------------------
        if code_block.strip() == fixed_block.strip():
            print(f"⚠ Skipping {issue['rule']} (No changes generated)")
            failed_issues.add(
                (
                    issue["rule"],
                    issue["message"],
                    issue["file"],
                )
            )
            continue

        # --------------------------------------
        # Apply Patch
        # --------------------------------------
        print("\nApplying patch...\n")

        success = replace_code_block(
            issue["file"],
            code_block,
            fixed_block,
        )

        if success:
            # Update Imports & Cleanup File
            update_imports(issue["file"], fixed_block)
            cleanup_file(issue["file"])

            fixed_count += 1
            print(f"✔ Fixed {issue['rule']} in {issue['file']}")
            print("Re-running analyzers...")
            print("-" * 60)

        else:
            print("❌ Failed to replace code block.")
            failed_issues.add(
                (
                    issue["rule"],
                    issue["message"],
                    issue["file"],
                )
            )

    # ==========================================
    # Summary Logs
    # ==========================================
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"Iterations Run      : {iteration}")
    print(f"Issues Fixed        : {fixed_count}")
    print(f"Issues Skipped      : {len(failed_issues)}")

    if failed_issues:
        print("\nSkipped / Unsupported:")
        for rule, message, file_path in sorted(failed_issues):
            print(f"- {rule} in {file_path}: {message}")

    # Pure return structure for clean testing/reporting integration
    return {
        "iterations": iteration,
        "fixed": fixed_count,
        "skipped": len(failed_issues),
    }