import unittest
from unittest.mock import patch, MagicMock
from git_automation.models import GitStatus, GitOperationResult
from git_automation.manager import GitAutomationManager
from git_automation import git


class TestGitAutomationSuite(unittest.TestCase):
    """Deterministic validation test array for Git subprocess wrapper verification."""

    def setUp(self):
        self.manager = GitAutomationManager()

    @patch("subprocess.run")
    def test_run_command_execution_failure(self, mock_run):
        """Ensures that OS errors or missing bin issues return graceful error result entities."""
        mock_run.side_effect = OSError("System binary not found")
        res = git.run_git_command(["status"])
        
        self.assertFalse(res.success)
        self.assertIn("Subprocess system runtime failure", res.message)

    @patch("subprocess.run")
    def test_clean_repository_evaluation(self, mock_run):
        """Verifies true state is derived when git status yields zero modifications."""
        # Setup mock returns for branch lookup and porcelain status
        mock_branch = MagicMock(returncode=0, stdout="main", stderr="")
        mock_status = MagicMock(returncode=0, stdout="", stderr="")
        mock_run.side_effect = [mock_branch, mock_status]

        status = self.manager.status()
        self.assertTrue(status.clean)
        self.assertEqual(status.branch, "main")
        self.assertEqual(len(status.modified_files), 0)

    @patch("subprocess.run")
    def test_dirty_repository_evaluation(self, mock_run):
        """Ensures unstaged modified files are accurately cataloged into list structures."""
        mock_branch = MagicMock(returncode=0, stdout="feature-fix\n", stderr="")
        mock_status = MagicMock(returncode=0, stdout=" M src/auth.py\n?? tests/new.py\n", stderr="")
        mock_run.side_effect = [mock_branch, mock_status]

        status = self.manager.status()
        self.assertFalse(status.clean)
        self.assertEqual(status.branch, "feature-fix")
        self.assertIn("src/auth.py", status.modified_files)
        self.assertIn("tests/new.py", status.modified_files)

    @patch("subprocess.run")
    def test_current_branch_lookup(self, mock_run):
        """Validates that current_branch extracts branch strings cleanly without newline noise."""
        mock_run.return_value = MagicMock(returncode=0, stdout="patch-v1\n", stderr="")
        branch = self.manager.current_branch()
        self.assertEqual(branch, "patch-v1")

    @patch("subprocess.run")
    def test_git_diff_retrieval(self, mock_run):
        """Checks that active diff strings are returned natively as plaintext."""
        expected_diff = "--- a/auth.py\n+++ b/auth.py\n@@ -1,1 +1,2 @@"
        mock_run.return_value = MagicMock(returncode=0, stdout=expected_diff, stderr="")
        
        diff_output = self.manager.diff()
        self.assertEqual(diff_output, expected_diff)

    @patch("subprocess.run")
    def test_stage_files_success_case(self, mock_run):
        """Verifies success metrics when staging valid existing files."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        res = self.manager.stage(["src/core.py"])
        
        self.assertTrue(res.success)
        self.assertIn("completed successfully", res.message)

    @patch("subprocess.run")
    def test_stage_files_failure_case(self, mock_run):
        """Validates error profile encapsulation when a stage action hits access rejections."""
        mock_run.return_value = MagicMock(returncode=128, stdout="", stderr="fatal: pathspec matched no files")
        res = self.manager.stage(["missing.py"])
        
        self.assertFalse(res.success)
        self.assertIn("Command failed with exit code 128", res.message)
        self.assertEqual(res.output, "fatal: pathspec matched no files")

    @patch("subprocess.run")
    def test_commit_success_case(self, mock_run):
        """Ensures standard commit execution yields true values on code 0."""
        mock_run.return_value = MagicMock(returncode=0, stdout="[main 1a2b3c4] Fixed issue", stderr="")
        res = self.manager.commit("feat: auto fix")
        
        self.assertTrue(res.success)
        self.assertIn("[main 1a2b3c4]", res.output)

    @patch("subprocess.run")
    def test_commit_failure_case(self, mock_run):
        """Checks that empty messages or pre-commit hook aborts are handled safely."""
        res = self.manager.commit("  ")
        self.assertFalse(res.success)
        self.assertIn("message payload is empty", res.message)

    @patch("subprocess.run")
    def test_manager_has_uncommitted_changes_facade(self, mock_run):
        """Validates high-level facade accurately matches the boolean calculation of clean indices."""
        mock_branch = MagicMock(returncode=0, stdout="main", stderr="")
        mock_status = MagicMock(returncode=0, stdout=" M updated.py", stderr="")
        mock_run.side_effect = [mock_branch, mock_status]
        
        self.assertTrue(self.manager.has_uncommitted_changes())


if __name__ == "__main__":
    unittest.main()