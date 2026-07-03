# patch_engine/conflict_detector.py

from patch_engine.patch import Patch


def has_conflict(existing_patch: Patch, new_patch: Patch) -> bool:
    """Detects structural conflicts between two pending Patch objects.

    A conflict occurs if both patches target the same file and their
    intended line ranges overlap mathematically. This function does not perform
    scheduling or file modifications.

    Args:
        existing_patch: The patch already staged in the system.
        new_patch: The incoming patch to validate.

    Returns:
        True if there is a line range overlap on the same file, False otherwise.
    """
    if existing_patch.file != new_patch.file:
        return False

    # Check for mathematical overlap between the two line intervals
    return max(existing_patch.start, new_patch.start) <= min(
        existing_patch.end, new_patch.end
    )