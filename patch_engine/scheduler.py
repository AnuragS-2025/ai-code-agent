# patch_engine/scheduler.py


class BatchScheduler:
    """Manages the initial staging phase of the batch scheduling system.

    This scheduler acts as the first stage in the patch pipeline, currently
    responsible for removing duplicate analyzer issues while preserving their
    deterministic execution order. It does not perform conflict detection,
    AST extraction, or file modifications.
    """

    def build_batch(self, issues: list[dict]) -> list[dict]:
        """Filters out duplicate analyzer issues from the provided list.

        Duplicates are identified by identical (rule, message, file, line)
        combinations. The original order of the unique issues is strictly
        preserved.

        Args:
            issues: A list of dictionaries representing prioritized analyzer issues.

        Returns:
            A new list of unique issues with their relative ordering intact.
        """
        seen = set()
        unique_issues = []

        for issue in issues:
            # Extract the unique fingerprint for the issue
            fingerprint = (
                issue.get("rule"),
                issue.get("message"),
                issue.get("file"),
                issue.get("line"),
            )

            if fingerprint not in seen:
                seen.add(fingerprint)
                unique_issues.append(issue)

        return unique_issues