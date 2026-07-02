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

# Phase 3 Intelligence Layer Imports
from patch_engine.issue_prioritizer import prioritize_issues
from config.settings import settings

# ==========================================
# Global Configuration & Safeguards
# ==========================================

# AI fallback rules.
# Currently empty because all supported rules have built-in fixers.
AI_FALLBACK_RULES = {
    # Future AI-only rules
}


def run_pipeline(target_files: list[str], max_iterations: int = None) -> dict:
    """
    Runs the full auto-fix pipeline on a given list of target files.
    Returns a summary dictionary of the execution.
    """
    # Use explicit parameter override if provided; otherwise, fall back to global settings
    if max_iterations is None:
        max_iterations = settings.max_iterations

    fixed_count = 0
    failed_issues = set()
    iteration = 0

    # ==========================================
    # Re-analysis Loop
    # ==========================================
    for iteration in range(1, max_iterations + 1):

        print("\n" + "=" * 60)
        print(f"SCAN ITERATION {iteration}")
        print("=" * 60)

        # --------------------------------------
        # Run Analyzers (Controlled via clean property toggles)
        # --------------------------------------
        ruff_issues = []
        if settings.ruff_enabled:
            ruff_issues = parse_ruff(run_ruff(target_files))

        bandit_issues = []
        if settings.bandit_enabled:
            bandit_issues = parse_bandit(run_bandit(target_files))
        
        semgrep_issues = []
        if settings.semgrep_enabled:
            semgrep_config = settings.semgrep_config_path
            for target_file in target_files:
                file_issues = parse_semgrep(
                    run_semgrep(
                        target_file,
                        set(),
                        config=semgrep_config,
                    )
                )
                semgrep_issues.extend(file_issues)

        # Merge Issues
        issues = ruff_issues + bandit_issues + semgrep_issues

        # Remove previously failed or unsupported issues
        issues = [
            issue
            for issue in issues
            if (
                issue["rule"],
                issue["message"],
                issue["file"],
            ) not in failed_issues
        ]

        # --------------------------------------
        # Prioritize Issues (Deterministic Reordering)
        # --------------------------------------
        issues = prioritize_issues(issues)

        if not issues:
            print("\n✔ No remaining fixable issues.")
            break

        # Pick first issue (Now guaranteed to be the highest priority)
        issue = issues[0]

        print("\n" + "=" * 60)
        print("ISSUE FOUND")
        print("=" * 60)
        print(issue)

        # --------------------------------------
        # Extract precise block using updated AST Extractor
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
        rule_meta = None
        rule_type = "block"  # Default fallback type

        if issue["rule"] in RULES:
            rule_meta = RULES[issue["rule"]]
            rule_type = rule_meta.get("type", "block")
            
            print(f"⚡ Using built-in fixer for {issue['rule']}")
            print(f"Rule Type : {rule_type}")
            
            if rule_type == "block":
                fixed_block = rule_meta["fixer"](code_block)
            else:
                fixed_block = ""

        # AI fallback rules are evaluated only if AI features are globally activated in the settings
        elif issue["rule"] in AI_FALLBACK_RULES and settings.ai_enabled:
            print(f"🤖 Using AI fixer for {issue['rule']}")
            rule_type = "block"
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
        # Validate Generated Patch (Only for block level fixes)
        # --------------------------------------
        if rule_type == "block":
            print("\n" + "=" * 60)
            print("GENERATED PATCH")
            print("=" * 60)

            if fixed_block.strip():
                print(fixed_block)
            else:
                print("[Code block removed]")

            # Validate Patch
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

            # Skip unchanged patch
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
        # Dispatch Logic Using Line Coordinate Ranges
        # --------------------------------------
        print("\nApplying patch...\n")
        success = False

        if rule_type == "block":
            # Passing coordinates metadata rather than raw old text search
            success = replace_code_block(
                issue["file"],
                block["start"],
                block["end"],
                fixed_block,
            )
        elif rule_type == "file" and rule_meta is not None:
            rule_meta["fixer"](issue["file"])
            success = True
        else:
            success = False

        # --------------------------------------
        # Post-Fix & Cleanup Flow
        # --------------------------------------
        if success:
            if rule_type == "block":
                update_imports(issue["file"], fixed_block)
            
            cleanup_file(issue["file"])

            fixed_count += 1
            print(f"✔ Fixed {issue['rule']} in {issue['file']}")
            print("Re-running analyzers...")
            print("-" * 60)

        else:
            print(f"❌ Failed to apply patch for rule type '{rule_type}' (Check file bounds or structural state).")
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

    return {
        "iterations": iteration,
        "fixed": fixed_count,
        "skipped": len(failed_issues),
    }