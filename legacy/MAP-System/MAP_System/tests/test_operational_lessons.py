import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from MAP_System.scripts.operational_lessons import load_store, orientation, validate


class OperationalLessonTests(unittest.TestCase):
    def test_live_store_validates_and_routes_fallback(self):
        data = load_store(Path("MAP_System/agents/operational-lessons.json"))
        self.assertEqual([], validate(data))
        packet = orientation(data, {"review-routing"}, datetime.now(timezone.utc))
        ids = {x["lesson_id"] for x in packet["active_lessons"]}
        self.assertIn("OPLESSON-0001", ids)
        self.assertIn("OPLESSON-0002", ids)
        fallback = next(x for x in packet["active_lessons"] if x["lesson_id"] == "OPLESSON-0001")
        self.assertIn("visible wezterm-tab", fallback["summary"])

    def test_overdue_lesson_is_marked_review_due(self):
        data = load_store(Path("MAP_System/agents/operational-lessons.json"))
        data["lessons"][0]["review_after"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        packet = orientation(data, {"review-routing"}, datetime.now(timezone.utc))
        fallback = next(x for x in packet["active_lessons"] if x["lesson_id"] == "OPLESSON-0001")
        self.assertTrue(fallback["review_due"])

    def test_retired_lessons_are_not_projected(self):
        data = load_store(Path("MAP_System/agents/operational-lessons.json"))
        data["lessons"][0]["status"] = "retired"
        packet = orientation(data, {"review-routing"}, datetime.now(timezone.utc))
        self.assertNotIn("OPLESSON-0001", {x["lesson_id"] for x in packet["active_lessons"]})

    def test_superseded_lessons_are_not_projected(self):
        data = load_store(Path("MAP_System/agents/operational-lessons.json"))
        data["lessons"][0]["status"] = "superseded"
        data["lessons"][0]["superseded_by"] = "OPLESSON-0002"
        packet = orientation(data, {"review-routing"}, datetime.now(timezone.utc))
        self.assertNotIn("OPLESSON-0001", {x["lesson_id"] for x in packet["active_lessons"]})

    def test_missing_source_and_conflict_fail_validation(self):
        data = load_store(Path("MAP_System/agents/operational-lessons.json"))
        duplicate = dict(data["lessons"][0])
        duplicate["lesson_id"] = "OPLESSON-9999"
        duplicate["source_paths"] = ["missing.md"]
        data["lessons"].append(duplicate)
        errors = validate(data)
        self.assertTrue(any("missing source" in x for x in errors))
        self.assertTrue(any("active title conflicts" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
