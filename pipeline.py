import os
import time
from typing import Optional, TYPE_CHECKING

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

# New Context Layer Imports
from project_index.index import ProjectIndexer
from context_engine.context import ContextEngine

# Telemetry System Import with static typing safety
if TYPE_CHECKING:
    from feedback.manager import FeedbackManager
else:
    try:
        from feedback.manager import FeedbackManager
    except ImportError:
        FeedbackManager = None

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
# Telemetry Integration Wrappers
# ==========================================

def _record_feedback_safe(
    feedback_manager: Optional["FeedbackManager"], 
    rule_id: str, 
    target_file: str, 
    iteration: int, 
    success: bool, 
    message: str
) -> None:
    """Helper method to safely execute feedback submission under strict exception isolation."""
    if feedback_manager is None:
        return
    try:
        if success:
            feedback_manager.record_success(
                rule=rule_id,
                file=target_file,
                iteration=iteration,
                message=message
            )
        else:
            feedback_manager.record_failure(
                rule=rule_id,
                file=target_file,
                iteration=iteration,
                message=message
            )
    except Exception as e:
        logger.warning("Telemetry Failure | Isolated error recording feedback engine metrics: %s", str(e))


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


def _collect_patches(
    filtered_issues: list[dict], 
    failed_issues: set, 
    metrics: dict, 
    affected_files: set,
    iteration: int,
    feedback_manager: Optional["FeedbackManager"] = None,
    context_engine: ContextEngine = None
) -> list[Patch]:
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

        # Context Resolution Loop Hook
        context = None
        if context_engine is not None:
            try:
                context = context_engine.get_context(target_file)
                metrics["context_lookup_count"] += 1
                
                # Dynamic diagnostic tracking safely handling attribute structures
                module_name = getattr(context, "module", "Unknown")
                imports_count = len(getattr(context, "imports", []))
                exports_count = len(getattr(context, "exports", []))
                related_count = len(getattr(context, "related_modules", []))
                
                logger.info(
                    "Context Resolved | Module: %s | Imports: %d | Exports: %d | Related Modules: %d",
                    module_name, imports_count, exports_count, related_count
                )
            except Exception as e:
                metrics["context_lookup_failures"] += 1
                logger.error("Failed to resolve context for file %s: %s", target_file, str(e))

        block = extract_code_block(target_file, issue["line"])
        code_block = block["code"]

        if not code_block.strip():
            msg = "Could not extract block structures (empty string extracted)."
            logger.warning("⚠ %s for %s", msg, issue["rule"])
            failed_issues.add((issue["rule"], issue["message"], target_file))
            metrics["failed_validation"] += 1
            _record_feedback_safe(feedback_manager, issue["rule"], target_file, iteration, False, msg)
            continue

        logger.debug("Extracted Block:\n%s", code_block)
        
        rule_meta = None
        rule_type = "block"

        if issue["rule"] in RULES:
            rule_meta = RULES[issue["rule"]]
            rule_type = rule_meta.get("type", "block")
            logger.info("⚡ Using built-in fixer for %s (Rule Type: %s)", issue["rule"], rule_type)
            
            if rule_type == "block":
                fixer_fn = rule_meta["fixer"]
                try:
                    fixed_block = fixer_fn(code_block, context=None)
                except TypeError:
                    fixed_block = fixer_fn(code_block)
            else:
                fixed_block = ""
                
        elif issue["rule"] in AI_FALLBACK_RULES and settings.ai_enabled:
            logger.info("🤖 Using AI fallback auto-fixer for %s", issue["rule"])
            rule_type = "block"
            
            # AI Context API Hooks setup block
            logger.info("AI Context Placeholder Prepared")
            
            fixed_block = generate_patch(f"{issue['rule']}: {issue['message']}", code_block)
        else:
            # Do not record feedback telemetry for completely unsupported rules as per constraints
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
                _record_feedback_safe(feedback_manager, issue["rule"], target_file, iteration, False, f"Syntax validation failed: {message}")
                continue

            if code_block.strip() == fixed_block.strip():
                msg = "Skipping rule execution (No operational delta generated by fixer)."
                logger.warning("⚠ %s: %s", msg, issue["rule"])
                failed_issues.add((issue["rule"], issue["message"], target_file))
                _record_feedback_safe(feedback_manager, issue["rule"], target_file, iteration, False, msg)
                continue

            # FIXED: Added back 'original=code_block' to guarantee full positional contract alignment with your Patch schema
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
            try:
                rule_meta["fixer"](target_file)
                affected_files.add(target_file)
                files_touched_this_iteration.add(target_file)
                metrics["patches_applied"] += 1
                _record_feedback_safe(feedback_manager, issue["rule"], target_file, iteration, True, "File-level patch applied successfully.")
            except Exception as e:
                failed_issues.add((issue["rule"], issue["message"], target_file))
                _record_feedback_safe(feedback_manager, issue["rule"], target_file, iteration, False, f"File-level patch application crashed: {str(e)}")

    return collected_patches


def _apply_batch(
    collected_patches: list[Patch], 
    filtered_issues: list[dict], 
    failed_issues: set, 
    metrics: dict, 
    affected_files: set,
    iteration: int,
    feedback_manager: Optional["FeedbackManager"] = None
) -> None:
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
            _record_feedback_safe(feedback_manager, patch.rule, patch.file, iteration, True, "Patch applied successfully and written to disk.")
        else:
            logger.error("❌ Failed to commit patch coordinates for rule %s in %s.", patch.rule, patch.file)
            msg = "Failed to apply patch modifications to disk structural blocks."
            _record_feedback_safe(feedback_manager, patch.rule, patch.file, iteration, False, msg)
            for issue in filtered_issues:
                if issue["rule"] == patch.rule and issue["file"] == patch.file:
                    failed_issues.add((issue["rule"], issue["message"], issue["file"]))

    logger.info("<<< [END] Batch Application Phase")


def _run_cleanup(affected_files: set) -> None:
    """Executes centralized high-resiliency auto-import generation and codebase linter updates."""
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
    logger.info("Total Issues Processed       : %d", metrics["total_found"])
    logger.info("Issues Selected              : %d", metrics["issues_selected"])
    logger.info("Patches Created              : %d", metrics["patches_created"])
    logger.info("Patches Applied              : %d", metrics["patches_applied"])
    logger.info("Conflicts Skipped            : %d", metrics["conflicts_skipped"])
    logger.info("Validation Failed            : %d", metrics["failed_validation"])
    logger.info("Unsupported Rules            : %d", metrics["unsupported_rules"])
    logger.info("Files Modified               : %d", metrics["files_modified"])
    logger.info("Project Index Build Time     : %.4fs", metrics["project_index_build_time"])
    logger.info("Context Engine Build Time    : %.4fs", metrics["context_engine_build_time"])
    logger.info("Context Lookups Executed     : %d", metrics["context_lookup_count"])
    logger.info("Context Lookup Failures      : %d", metrics["context_lookup_failures"])
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

    # Instantiating exactly one FeedbackManager instance for backward-compatible pipeline execution
    feedback_manager = FeedbackManager() if FeedbackManager is not None else None

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
        "project_index_build_time": 0.0,
        "context_engine_build_time": 0.0,
        "context_lookup_count": 0,
        "context_lookup_failures": 0,
        "elapsed_time": 0.0
    }

    # Ensure project_root is absolute and normalized for path matching
    project_root = os.path.normpath(os.path.abspath(os.getcwd()))
    if target_files:
        absolute_targets = [os.path.normpath(os.path.abspath(f)) for f in target_files]
        common_root = os.path.commonpath(absolute_targets)
        if common_root and os.path.exists(common_root):
            project_root = common_root if os.path.isdir(common_root) else os.path.dirname(common_root)

    # Initialize Project Index
    logger.info("Building Project Index...")
    index_start = time.perf_counter()
    project_indexer = ProjectIndexer()
    project_indexer.build(project_root)
    metrics["project_index_build_time"] = time.perf_counter() - index_start
    logger.info("Project Index created successfully.")

    # Initialize Context Engine
    logger.info("Building Context Engine...")
    engine_start = time.perf_counter()
    context_engine = ContextEngine()
    
    # Fallback lookup to support both public .index property and internal _index dictionary safely
    raw_index_data = getattr(project_indexer, "index", getattr(project_indexer, "_index", None))
    context_engine.build(raw_index_data)
    
    metrics["context_engine_build_time"] = time.perf_counter() - engine_start
    logger.info("Context Engine ready.")

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
        collected_patches = _collect_patches(
            filtered_issues, 
            failed_issues, 
            metrics, 
            affected_files, 
            iteration=iteration,
            feedback_manager=feedback_manager,
            context_engine=context_engine
        )
        logger.info("Collected patches compiled for execution batch window: %d", len(collected_patches))
        logger.info("Skipped conflicting structural patches within current loop: %d", metrics["conflicts_skipped"])

        if not collected_patches and not affected_files:
            logger.info("No valid patches or structural modifications were collected in this iteration.")
            break

        # 4. Atomic Block Apply Phase
        _apply_batch(
            collected_patches, 
            filtered_issues, 
            failed_issues, 
            metrics, 
            affected_files, 
            iteration=iteration, 
            feedback_manager=feedback_manager
        )

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