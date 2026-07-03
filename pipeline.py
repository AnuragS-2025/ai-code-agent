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

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)

# ==========================================
# Global Configuration & Safeguards
# ==========================================

# AI fallback rules.
# Currently empty because all supported rules have built-in fixers.
AI_FALLBACK_RULES = {
    # Future AI-only rules
}


def run_pipeline(target_files: list[str], max_iterations: int | None = None) -> dict:
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

        # Enhanced visual boundaries for Scan Iterations (Issue 2)
        logger.info("=" * 50)
        logger.info("SCAN ITERATION %d", iteration)
        logger.info("=" * 50)

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
            logger.info("✔ No remaining fixable issues.")
            break

        # Pick first issue (Now guaranteed to be the highest priority)
        issue = issues[0]

        # Readable logs using structured formatting
        logger.info(
            "Issue Found | Rule=%s File=%s Line=%s",
            issue["rule"],
            issue["file"],
            issue["line"],
        )
        logger.debug("Issue Details: %s", issue)

        # --------------------------------------
        # Extract precise block using updated AST Extractor
        # --------------------------------------
        block = extract_code_block(
            issue["file"],
            issue["line"],
        )

        code_block = block["code"]

        if not code_block.strip():
            logger.warning("⚠ Could not extract block for %s", issue["rule"])
            failed_issues.add(
                (
                    issue["rule"],
                    issue["message"],
                    issue["file"],
                )
            )
            continue

        # Heavy code blocks shifted to DEBUG level
        logger.debug("Extracted Block:\n%s", code_block)
        
        # --------------------------------------
        # Choose Fixer Strategy (Guard Routing)
        # --------------------------------------
        rule_meta = None
        rule_type = "block"  # Default fallback type

        if issue["rule"] in RULES:
            rule_meta = RULES[issue["rule"]]
            rule_type = rule_meta.get("type", "block")
            
            logger.info("⚡ Using built-in fixer for %s (Rule Type: %s)", issue["rule"], rule_type)
            
            if rule_type == "block":
                fixed_block = rule_meta["fixer"](code_block)
            else:
                fixed_block = ""

        # AI fallback rules are evaluated only if AI features are globally activated in the settings
        elif issue["rule"] in AI_FALLBACK_RULES and settings.ai_enabled:
            logger.info("🤖 Using AI fixer for %s", issue["rule"])
            rule_type = "block"
            fixed_block = generate_patch(
                f"{issue['rule']}: {issue['message']}",
                code_block,
            )

        else:
            logger.warning("⚠ Skipping unsupported rule: %s", issue["rule"])
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
            if fixed_block.strip():
                # Generated patch logs moved to DEBUG level
                logger.debug("Generated Patch:\n%s", fixed_block)
            else:
                logger.debug("Generated Patch: [Code block removed]")

            # Validate Patch
            valid, message = validate_patch(fixed_block)
            logger.info("Patch Validation Result: %s", message)

            if not valid:
                logger.error("❌ Validation failed.")
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
                logger.warning("⚠ Skipping %s (No changes generated)", issue["rule"])
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
        logger.info("Applying patch...")
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
            logger.info("✔ Fixed %s in %s. Re-running analyzers...", issue["rule"], issue["file"])

        else:
            logger.error("❌ Failed to apply patch for rule type '%s' (Check file bounds or structural state).", rule_type)
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
    logger.info("=" * 50)
    logger.info("SUMMARY")
    logger.info("=" * 50)

    logger.info("Iterations Run       : %d", iteration)
    logger.info("Issues Fixed         : %d", fixed_count)
    logger.info("Issues Skipped       : %d", len(failed_issues))

    if failed_issues:
        logger.info("Skipped / Unsupported:")
        for rule, message, file_path in sorted(failed_issues):
            logger.info("- %s in %s: %s", rule, file_path, message)

    return {
        "iterations": iteration,
        "fixed": fixed_count,
        "skipped": len(failed_issues),
    }