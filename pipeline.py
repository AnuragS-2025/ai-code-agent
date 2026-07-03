import os
import time
from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep

from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep

from patch_engine.extractor import extract_code_block
from patch_engine.validator import validate_patch
from patch_engine.replacer import replace_code_block

from patch_engine.import_manager import update_imports
from patch_engine.file_fixers import cleanup_file
from patch_engine.rule_registry import RULES
from auto_fix_engine import generate_patch

# Phase 3 Intelligence Layer Imports
from config.settings import settings
from patch_engine.issue_prioritizer import prioritize_issues

# Centralized Models, Conflict Detector & Scheduler Imports
from patch_engine.conflict_detector import has_conflict
from patch_engine.patch import Patch
from patch_engine.scheduler import BatchScheduler

# Centralized logger initialization
from utils.logger import get_logger

logger = get_logger(__name__)

# ==========================================
# Global Configuration & Safeguards
# ==========================================

AI_FALLBACK_RULES = {
    # Future AI-only rules
}


# ==========================================
# Modular Lifecycle Helpers
# ==========================================

def _run_analyzers_and_filter(target_files: list[str], failed_issues: set) -> list[dict]:
    """Runs all enabled static analysis tools, aggregates issues, and normalizes file paths."""
    logger.info(">>> [START] Analyzer Rescan Sequence")
    
    # Normalize input target files to absolute structural paths
    normalized_targets = [os.path.normpath(os.path.abspath(f)) for f in target_files]
    
    ruff_issues = parse_ruff(run_ruff(normalized_targets)) if settings.ruff_enabled else []
    bandit_issues = parse_bandit(run_bandit(normalized_targets)) if settings.bandit_enabled else []
    
    semgrep_issues = []
    if settings.semgrep_enabled:
        semgrep_config = settings.semgrep_config_path
        for target_file in normalized_targets:
            file_issues = parse_semgrep(run_semgrep(target_file, set(), config=semgrep_config))
            semgrep_issues.extend(file_issues)

    raw_issues = ruff_issues + bandit_issues + semgrep_issues
    logger.info("<<< [END] Analyzer Rescan Sequence")
    
    # Normalize output paths across all engine diagnostics to eliminate duplicates
    processed_issues = []
    for issue in raw_issues:
        issue["file"] = os.path.normpath(os.path.abspath(issue["file"]))
        
        # Deduplicate using absolute key footprints against previous failure states
        if (issue["rule"], issue["message"], issue["file"]) not in failed_issues:
            processed_issues.append(issue)
            
    return processed_issues


def _collect_patches(filtered_issues: list[dict], failed_issues: set, metrics: dict, affected_files: set) -> list[Patch]:
    """Processes filtered issues sequentially, extracts code blocks, and builds non-conflicting patches."""
    collected_patches = []
    
    # Line Drift Safeguard Set: Restrict execution to 1 structural patch per file per iteration
    files_touched_this_iteration = set()
    
    for issue in filtered_issues:
        target_file = issue["file"]
        
        # Dynamic check for structural collision safeguards
        if target_file in files_touched_this_iteration:
            logger.debug(
                "Line-Drift Prevention | Skipping rule %s for file %s. Retrained for next cycle rescan.",
                issue["rule"], target_file
            )
            continue

        logger.info("Processing Issue | Rule=%s File=%s Line=%s", issue["rule"], target_file, issue["line"])
        logger.debug("Issue Details: %s", issue)

        block = extract_code_block(target_file, issue["line"])
        code_block = block["code"]

        if not code_block.strip():
            logger.warning("⚠ Could not extract block structures for %s", issue["rule"])
            failed_issues.add((issue["rule"], issue["message"], target_file))
            metrics["failed_validation"] += 1
            continue

        logger.debug("Extracted Block:\n%s", code_block)
        
        rule_meta = None
        rule_type = "block"

        if issue["rule"] in RULES:
            rule_meta = RULES[issue["rule"]]
            rule_type = rule_meta.get("type", "block")
            logger.info("⚡ Using built-in fixer for %s (Rule Type: %s)", issue["rule"], rule_type)
            fixed_block = rule_meta["fixer"](code_block) if rule_type == "block" else ""
        elif issue["rule"] in AI_FALLBACK_RULES and settings.ai_enabled:
            logger.info("🤖 Using AI fallback auto-fixer for %s", issue["rule"])
            rule_type = "block"
            fixed_block = generate_patch(f"{issue['rule']}: {issue['message']}", code_block)
        else:
            logger.warning("⚠ Skipping unsupported rule: %s", issue["rule"])
            failed_issues.add((issue["rule"], issue["message"], target_file))
            metrics["unsupported_rules"] += 1
            continue

        if rule_type == "block":
            if fixed_block.strip():
                logger.debug("Generated Patch Payload:\n%s", fixed_block)
            else:
                logger.debug("Generated Patch Payload: [Block removed]")

            valid, message = validate_patch(fixed_block)
            logger.info("Patch Validation Result: %s", message)

            if not valid:
                logger.error("❌ Validation constraints failed.")
                failed_issues.add((issue["rule"], issue["message"], target_file))
                metrics["failed_validation"] += 1
                continue

            if code_block.strip() == fixed_block.strip():
                logger.warning("⚠ Skipping %s (No operational delta generated)", issue["rule"])
                failed_issues.add((issue["rule"], issue["message"], target_file))
                continue

            new_patch = Patch(
                file=target_file,
                rule=issue["rule"],
                start=block["start"],
                end=block["end"],
                original=code_block,
                replacement=fixed_block
            )

            # Strict cross-reference checker
            conflict_found = False
            for existing_patch in collected_patches:
                if has_conflict(existing_patch, new_patch):
                    logger.debug(
                        "Conflict | Rule=%s File=%s Range=%d-%d Reason=Skipped because another patch already targets the same structural region.",
                        new_patch.rule,
                        new_patch.file,
                        new_patch.start,
                        new_patch.end,
                    )
                    conflict_found = True
                    break

            if conflict_found:
                metrics["conflicts_skipped"] += 1
                continue

            collected_patches.append(new_patch)
            files_touched_this_iteration.add(target_file)
            metrics["patches_created"] += 1

        elif rule_type == "file" and rule_meta is not None:
            logger.info("Executing immediate file-level rule logic: %s", issue["rule"])
            rule_meta["fixer"](target_file)
            affected_files.add(target_file)
            files_touched_this_iteration.add(target_file)
            metrics["patches_applied"] += 1

    return collected_patches


def _apply_batch(collected_patches: list[Patch], filtered_issues: list[dict], failed_issues: set, metrics: dict, affected_files: set) -> None:
    """Commits verified code blocks down onto absolute storage addresses accurately."""
    if not collected_patches:
        return

    logger.info(">>> [START] Batch Application Phase: Committing %d patches to disk", len(collected_patches))

    for patch in collected_patches:
        success = replace_code_block(patch.file, patch.start, patch.end, patch.replacement)

        if success:
            metrics["patches_applied"] += 1
            affected_files.add(patch.file)
            logger.info("✔ Applied patch for rule %s inside file target: %s.", patch.rule, patch.file)
        else:
            logger.error("❌ Failed to commit patch coordinates for rule %s in %s.", patch.rule, patch.file)
            for issue in filtered_issues:
                if issue["rule"] == patch.rule and issue["file"] == patch.file:
                    failed_issues.add((issue["rule"], issue["message"], issue["file"]))

    logger.info("<<< [END] Batch Application Phase")


def _run_cleanup(affected_files: set) -> None:
    """Executes centralized high-resiliency auto-import generation and codebase linting updates."""
    if not affected_files:
        return

    logger.info(">>> [START] Single-Pass Post-Fix File Cleanup Loop")
    
    for affected_file in affected_files:
        try:
            with open(affected_file, "r", encoding="utf-8") as f:
                updated_content = f.read()
            
            update_imports(affected_file, updated_content)
            cleanup_file(affected_file)
            logger.info("✔ Post-fix operations successfully executed for file: %s", affected_file)
        except Exception:
            logger.exception("❌ Crash isolated running post-fix pipeline cleanup hooks on %s", affected_file)

    logger.info("<<< [END] Single-Pass Post-Fix File Cleanup Loop")


def _log_summary(iteration: int, metrics: dict, failed_count: int) -> None:
    """Prints a clear summary matrix inside system streams."""
    logger.info("=" * 50)
    logger.info("PIPELINE EXECUTION METRICS SUMMARY")
    logger.info("=" * 50)
    logger.info("Iterations Executed          : %d", iteration)
    # Metric successfully renamed to represent cumulative tracking correctly
    logger.info("Total Issues Processed       : %d", metrics["total_found"])
    logger.info("Issues Selected              : %d", metrics["issues_selected"])
    logger.info("Patches Created              : %d", metrics["patches_created"])
    logger.info("Patches Applied              : %d", metrics["patches_applied"])
    logger.info("Conflicts Skipped            : %d", metrics["conflicts_skipped"])
    logger.info("Validation Failed            : %d", metrics["failed_validation"])
    logger.info("Unsupported Rules            : %d", metrics["unsupported_rules"])
    logger.info("Files Modified               : %d", metrics["files_modified"])
    logger.info("Elapsed Time                 : %.2fs", metrics["elapsed_time"])
    logger.info("=" * 50)


# ==========================================
# Main Execution Entry Pipeline
# ==========================================

def run_pipeline(target_files: list[str], max_iterations: int | None = None) -> dict:
    """
    Runs the full auto-fix pipeline on a given list of target files using an optimized
    modular orchestration strategy.
    """
    start_time = time.perf_counter()

    if max_iterations is None:
        max_iterations = settings.max_iterations

    failed_issues = set()
    iteration = 0

    metrics = {
        "total_found": 0,
        "issues_selected": 0,
        "patches_created": 0,
        "patches_applied": 0,
        "conflicts_skipped": 0,
        "failed_validation": 0,
        "unsupported_rules": 0,
        "files_modified": 0,
        "elapsed_time": 0.0
    }

    scheduler = BatchScheduler()

    # ==========================================
    # Re-analysis Loop
    # ==========================================
    for iteration in range(1, max_iterations + 1):
        logger.info("=" * 50)
        logger.info("SCAN ITERATION %d", iteration)
        logger.info("=" * 50)

        # 1. Scanning and Normalization Phase
        discovered_issues = _run_analyzers_and_filter(target_files, failed_issues)
        metrics["total_found"] += len(discovered_issues)
        logger.info("Total issues discovered by static analysis engines: %d", len(discovered_issues))

        prioritized = prioritize_issues(discovered_issues)
        if not prioritized:
            logger.info("✔ No remaining fixable issues found.")
            break

        # 2. Scheduling & Filtering Phase
        filtered_issues = scheduler.build_batch(prioritized)
        metrics["issues_selected"] += len(filtered_issues)
        logger.info("Issues selected for batch execution configuration: %d", len(filtered_issues))

        if not filtered_issues:
            logger.info("✔ Scheduler returned an empty batch frame.")
            break

        affected_files = set()

        # 3. Code Extraction and Safe Tracking Collections Phase
        collected_patches = _collect_patches(filtered_issues, failed_issues, metrics, affected_files)
        logger.info("Collected patches compiled for execution batch window: %d", len(collected_patches))
        logger.info("Skipped conflicting structural patches within current loop: %d", metrics["conflicts_skipped"])

        if not collected_patches and not affected_files:
            logger.info("No valid patches or structural modifications were collected in this iteration.")
            break

        # 4. Atomic Block Apply Phase
        _apply_batch(collected_patches, filtered_issues, failed_issues, metrics, affected_files)

        # 5. Cleanups Phase
        _run_cleanup(affected_files)
        metrics["files_modified"] = len(affected_files)

        logger.info("Batch iteration processing block finalized.")

    metrics["elapsed_time"] = time.perf_counter() - start_time
    _log_summary(iteration, metrics, len(failed_issues))

    return {
        "iterations": iteration,
        "fixed": metrics["patches_applied"],
        "skipped": len(failed_issues),
    }