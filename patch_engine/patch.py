from dataclasses import dataclass


@dataclass(frozen=True)
class Patch:
    """Represents a pending code modification within the batch scheduling system.

    This immutable data class serves as the common data model used to
    stage and track structural code changes before they are permanently
    written to disk.
    """

    file: str
    rule: str
    start: int
    end: int
    original: str          # Added to allow rich debugging, structural diffs, and safe rollbacks
    replacement: str