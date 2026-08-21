from __future__ import annotations

import unittest

from runtime.no_progress import no_progress_advisory


def obs(activity: str, progress: str = "rev:1") -> dict[str, str]:
    return {"activity_key": activity, "progress_key": progress}


class NoProgressAdvisoryTests(unittest.TestCase):
    def test_repeated_equivalent_activity_without_progress_returns_advisory(self):
        result = no_progress_advisory(
            session_live=True,
            task_status="ACTIVE",
            observations=[
                obs("tool:pytest -k failing"),
                obs("tool:pytest -k failing"),
                obs("tool:pytest -k failing"),
            ],
        )

        self.assertEqual(result["state"], "NO_PROGRESS")
        self.assertEqual(result["advisory"], "HELPER_NO_PROGRESS")
        self.assertEqual(result["details"]["remediation"], "ADVISORY_ONLY")

    def test_non_live_or_ineligible_task_is_clear(self):
        non_live = no_progress_advisory(
            session_live=False,
            task_status="ACTIVE",
            observations=[obs("same"), obs("same"), obs("same")],
        )
        self.assertEqual(non_live["state"], "CLEAR")
        self.assertEqual(non_live["reason"], "SESSION_NOT_LIVE")

        done = no_progress_advisory(
            session_live=True,
            task_status="DONE",
            observations=[obs("same"), obs("same"), obs("same")],
        )
        self.assertEqual(done["state"], "CLEAR")
        self.assertEqual(done["reason"], "TASK_NOT_ELIGIBLE")

    def test_explicit_wait_and_progress_signals_are_clear(self):
        waiting = no_progress_advisory(
            session_live=True,
            task_status="ACTIVE",
            explicit_wait=True,
            observations=[obs("poll"), obs("poll"), obs("poll")],
        )
        self.assertEqual(waiting["state"], "CLEAR")
        self.assertEqual(waiting["reason"], "EXPLICIT_WAIT_ACTIVE")

        changed = no_progress_advisory(
            session_live=True,
            task_status="ACTIVE",
            output_changed=True,
            observations=[obs("compile"), obs("compile"), obs("compile")],
        )
        self.assertEqual(changed["state"], "CLEAR")
        self.assertEqual(changed["reason"], "PROGRESS_SIGNAL_CHANGED")
        self.assertEqual(changed["details"]["signals"], ["OUTPUT_CHANGED"])

    def test_threshold_activity_and_progress_variation_are_clear(self):
        short = no_progress_advisory(
            session_live=True,
            task_status="ACTIVE",
            observations=[obs("same"), obs("same")],
        )
        self.assertEqual(short["state"], "CLEAR")
        self.assertEqual(short["reason"], "OBSERVATION_THRESHOLD_NOT_MET")

        varied_activity = no_progress_advisory(
            session_live=True,
            task_status="ACTIVE",
            observations=[obs("a"), obs("b"), obs("a")],
        )
        self.assertEqual(varied_activity["state"], "CLEAR")
        self.assertEqual(varied_activity["reason"], "ACTIVITY_VARIED")

        progress_changed = no_progress_advisory(
            session_live=True,
            task_status="ACTIVE",
            observations=[obs("same", "rev:1"), obs("same", "rev:2"), obs("same", "rev:2")],
        )
        self.assertEqual(progress_changed["state"], "CLEAR")
        self.assertEqual(progress_changed["reason"], "PROGRESS_KEY_CHANGED")

    def test_invalid_threshold_is_unknown_not_no_progress(self):
        for threshold in (1, 2.5, "3", True):
            with self.subTest(threshold=threshold):
                result = no_progress_advisory(
                    session_live=True,
                    task_status="ACTIVE",
                    repeated_activity_threshold=threshold,  # type: ignore[arg-type]
                    observations=[obs("same"), obs("same"), obs("same")],
                )

                self.assertEqual(result["state"], "UNKNOWN")
                self.assertIsNone(result["advisory"])
                self.assertEqual(result["reason"], "INVALID_THRESHOLD")


if __name__ == "__main__":
    unittest.main()
