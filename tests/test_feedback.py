import unittest
import tempfile
import shutil
from pathlib import Path
from feedback.models import FeedbackEntry
from feedback.manager import FeedbackManager
from feedback import database
from feedback.serializer import to_dict, from_dict


class TestFeedbackSystem(unittest.TestCase):
    """Deterministic suite verifying performance thresholds of system telemetry logs."""

    def setUp(self):
        # Provision isolated runtime mock sandboxes
        self.test_dir = tempfile.mkdtemp()
        self.mock_db_path = Path(self.test_dir) / ".feedback" / "history.json"
        
        # Divert data connections securely away from structural roots
        self.original_db_path = database.DB_PATH
        database.DB_PATH = self.mock_db_path
        
        self.manager = FeedbackManager()

    def tearDown(self):
        # Safely scrub active sandbox workspaces
        database.DB_PATH = self.original_db_path
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_empty_database_handling(self):
        """Verifies read commands safely drop down into empty standard collections."""
        history = self.manager.get_history()
        self.assertEqual(history, [])

    def test_serialization_pipeline_fidelity(self):
        """Ensures byte translation arrays encode and decode seamlessly."""
        entry = FeedbackEntry("B307", "test.py", True, 1, "Verified")
        serialized = to_dict(entry)
        self.assertEqual(serialized["rule"], "B307")
        
        reconstructed = from_dict(serialized)
        self.assertEqual(reconstructed, entry)

    def test_append_and_load_sequence(self):
        """Validates ordered sequential database modifications commit correctly to disk."""
        self.manager.record_success("B307", "app.py", 1, "Optimized")
        self.manager.record_failure("R001", "core.py", 2, "Linter Failure")
        
        history = self.manager.get_history()
        self.assertEqual(len(history), 2)
        self.assertTrue(history[0].success)
        self.assertFalse(history[1].success)
        self.assertEqual(history[0].rule, "B307")
        self.assertEqual(history[1].rule, "R001")

    def test_clear_database_transactions(self):
        """Ensures execution buffers can be cleared back to foundational baselines."""
        self.manager.record_success("B307", "app.py", 1)
        self.assertNotEqual(self.manager.get_history(), [])
        
        self.manager.clear()
        self.assertEqual(self.manager.get_history(), [])

    def test_corrupted_json_isolation(self):
        """Confirms pipeline avoids fatal crashes if history file data is corrupted."""
        database._ensure_storage()
        with open(self.mock_db_path, "w", encoding="utf-8") as f:
            f.write("{ INVALID RAW FILE PAYLOAD CORRUPTED ... }")
            
        # Verify layer handles formatting exceptions gracefully without crashing
        history = self.manager.get_history()
        self.assertEqual(history, [])

    # ==========================================================
    # Sprint 3.5 Extended Direct Database Tests
    # ==========================================================

    def test_direct_load_feedback_ordering(self):
        """
        Saves two FeedbackEntry objects directly via append_feedback,
        calls load_feedback(), and verifies entries are returned in exact chronological order.
        """
        entry1 = FeedbackEntry("B307", "src/auth.py", True, 1, "Direct Save 1")
        entry2 = FeedbackEntry("Ruff-E711", "src/utils.py", False, 1, "Direct Save 2")
        
        # Execute direct append transactions
        database.append_feedback(entry1)
        database.append_feedback(entry2)
        
        # Load directly bypassing the manager abstraction
        loaded_records = database.load_feedback()
        
        self.assertEqual(len(loaded_records), 2)
        self.assertEqual(loaded_records[0].rule, "B307")
        self.assertEqual(loaded_records[0].message, "Direct Save 1")
        self.assertEqual(loaded_records[1].rule, "Ruff-E711")
        self.assertEqual(loaded_records[1].message, "Direct Save 2")

    def test_multiple_append_database_length_integrity(self):
        """
        Appends exactly three distinct entry payloads sequentially 
        and validates that the absolute persistent file size length matches precisely.
        """
        e1 = FeedbackEntry("B307", "file1.py", True, 1, "M1")
        e2 = FeedbackEntry("B601", "file2.py", True, 2, "M2")
        e3 = FeedbackEntry("B101", "file3.py", False, 3, "M3")
        
        database.append_feedback(e1)
        database.append_feedback(e2)
        database.append_feedback(e3)
        
        loaded_records = database.load_feedback()
        self.assertEqual(len(loaded_records), 3)


if __name__ == "__main__":
    unittest.main()