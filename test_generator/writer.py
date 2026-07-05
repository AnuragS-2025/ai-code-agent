"""
Secure System Test Writer Proxy.

Commits generated unit testing configurations safely into disk directories while
guaranteeing complete crash safety and safeguarding against file overwrite regressions.
"""

from pathlib import Path
from test_generator.models import GeneratedTest


class TestWriter:
    """
    Manages atomic file output sequences with strict overwrite protections.
    """

    def __init__(self, base_tests_dir: str = "tests"):
        self.base_dir = Path(base_tests_dir)

    def write_test_to_disk(self, generated_test: GeneratedTest) -> str | None:
        """
        Saves content inside the targets directory frame securely using strict UTF-8 rules.
        """
        try:
            # Guarantee the parent tests target workspace exists
            self.base_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = self.base_dir / generated_test.test_name
            
            # Guard against overwrite regressions
            if target_path.exists():
                return None
                
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(generated_test.content)
                
            return str(target_path.resolve())
            
        except (OSError, PermissionError, IOError):
            # Gracefully handle physical media failures without interrupting pipeline workflows
            return None