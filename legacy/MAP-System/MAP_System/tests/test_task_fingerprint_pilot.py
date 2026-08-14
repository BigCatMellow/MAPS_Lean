#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from MAP_System.scripts import task_fingerprint_pilot as pilot


class TaskFingerprintPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = pilot.load_json(pilot.DEFAULT_SPEC)
        cls.index = pilot.build_index(cls.spec)

    def test_frozen_corpus_is_complete_and_sources_resolve(self) -> None:
        self.assertEqual(self.index["missing_task_ids"], [])
        self.assertEqual(self.index["corpus_count"], len(self.spec["corpus_task_ids"]))
        self.assertEqual(pilot.validate_expected_sources(self.spec), [])
        for fingerprint in self.index["fingerprints"]:
            self.assertTrue(fingerprint["source_refs"])
            task_ref = f"MAP_System/tasks/{fingerprint['task_id']}.json"
            self.assertIn(task_ref, fingerprint["source_refs"])
            self.assertTrue((pilot.REPO / task_ref).exists())

    def test_lexical_retrieval_meets_frozen_recall_gate(self) -> None:
        metrics = pilot.algorithm_metrics(self.spec, self.index)
        self.assertGreaterEqual(metrics["recall_at_6"], 0.8, metrics)
        self.assertEqual(metrics["critical_miss_count"], 0, metrics)

    def test_helper_packet_hides_truth_and_stays_within_per_query_budget(self) -> None:
        packet, estimates = pilot.render_helper_packet(self.spec, self.index)
        self.assertNotIn("expected_task_ids", packet)
        self.assertNotIn("expected_source_paths", packet)
        ceiling = self.spec["retrieval_contract"]["discovery_packet_max_estimated_tokens"]
        self.assertEqual(set(estimates), {query["id"] for query in self.spec["queries"]})
        self.assertTrue(all(value <= ceiling for value in estimates.values()), estimates)

    def test_generate_is_deterministic_for_frozen_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "first.json"
            second = Path(tmp) / "second.json"
            pilot.write_json(first, self.index)
            pilot.write_json(second, pilot.build_index(self.spec))
            self.assertEqual(json.loads(first.read_text()), json.loads(second.read_text()))

    def test_matching_concepts_outrank_unrelated_task(self) -> None:
        results = pilot.search_index(
            self.index,
            "Pi terminal acknowledgement did not create an hcom message event",
            limit=3,
        )
        returned = [result["task_id"] for result in results]
        self.assertIn("TASK-230", returned[:2])
        self.assertIn("TASK-229", returned)


if __name__ == "__main__":
    unittest.main()
