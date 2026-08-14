from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from MAP_System.scripts import map_authority_notify


def completed(returncode: int, *, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(
        args=["map-authority", "sync"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class AuthorityNotificationTests(unittest.TestCase):
    def test_first_failure_records_state_and_notifies(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(1, stderr="connection refused"),
                ),
                mock.patch.object(
                    map_authority_notify, "notify", return_value=True
                ) as notifier,
            ):
                result = map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=1000
                )
            self.assertEqual(result, 1)
            payload = json.loads(state.read_text())
            self.assertEqual(payload["status"], "failing")
            self.assertEqual(payload["consecutive_failures"], 1)
            self.assertTrue(payload["failure_notified"])
            self.assertEqual(payload["last_notification_epoch"], 1000)
            notifier.assert_called_once()

    def test_repeated_failure_is_rate_limited(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            state.write_text(
                json.dumps(
                    {
                        "status": "failing",
                        "consecutive_failures": 1,
                        "failure_notified": True,
                        "last_notification_epoch": 1000,
                    }
                )
            )
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(1, stderr="still unavailable"),
                ),
                mock.patch.object(map_authority_notify, "notify") as notifier,
            ):
                result = map_authority_notify.run_once(
                    Path("/bin/map-authority"),
                    state,
                    repeat_seconds=1800,
                    now_epoch=1200,
                )
            self.assertEqual(result, 1)
            self.assertEqual(json.loads(state.read_text())["consecutive_failures"], 2)
            notifier.assert_not_called()

    def test_notification_retries_when_desktop_was_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            state.write_text(
                json.dumps(
                    {
                        "status": "failing",
                        "consecutive_failures": 1,
                        "failure_notified": False,
                    }
                )
            )
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(1, stderr="still unavailable"),
                ),
                mock.patch.object(
                    map_authority_notify, "notify", return_value=True
                ) as notifier,
            ):
                map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=1200
                )
            notifier.assert_called_once()
            self.assertTrue(json.loads(state.read_text())["failure_notified"])

    def test_recovery_notifies_once_after_notified_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            state.write_text(
                json.dumps(
                    {
                        "status": "failing",
                        "consecutive_failures": 4,
                        "failure_notified": True,
                    }
                )
            )
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(0, stdout='{"ok":true}\n'),
                ),
                mock.patch.object(
                    map_authority_notify, "notify", return_value=True
                ) as notifier,
            ):
                result = map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=2000
                )
            self.assertEqual(result, 0)
            payload = json.loads(state.read_text())
            self.assertEqual(payload["status"], "healthy")
            self.assertEqual(payload["consecutive_failures"], 0)
            self.assertTrue(payload["recovery_notified"])
            notifier.assert_called_once()

    def test_success_without_prior_alert_does_not_notify(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(0),
                ),
                mock.patch.object(map_authority_notify, "notify") as notifier,
            ):
                self.assertEqual(
                    map_authority_notify.run_once(
                        Path("/bin/map-authority"), state, now_epoch=2000
                    ),
                    0,
                )
            notifier.assert_not_called()

    def test_recovery_notification_retries_when_desktop_was_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            state.write_text(
                json.dumps(
                    {
                        "status": "failing",
                        "consecutive_failures": 2,
                        "failure_notified": True,
                    }
                )
            )
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(0),
                ),
                mock.patch.object(
                    map_authority_notify, "notify", side_effect=[False, True]
                ) as notifier,
            ):
                map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=2000
                )
                first = json.loads(state.read_text())
                self.assertTrue(first["recovery_pending"])
                map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=2060
                )
            second = json.loads(state.read_text())
            self.assertFalse(second["recovery_pending"])
            self.assertTrue(second["recovery_notified"])
            self.assertEqual(notifier.call_count, 2)

    def test_success_records_authority_revision_from_sync(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(
                        0,
                        stdout=json.dumps(
                            {
                                "ok": True,
                                "authority_revision": "sha256:" + "a" * 64,
                                "authority_observed_at": "2026-07-30T01:00:00Z",
                            }
                        ),
                    ),
                ),
                mock.patch.object(map_authority_notify, "notify"),
            ):
                result = map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=2000
                )
            payload = json.loads(state.read_text())
        self.assertEqual(result, 0)
        self.assertEqual(payload["authority_revision"], "sha256:" + "a" * 64)
        self.assertEqual(
            payload["authority_observed_at"], "2026-07-30T01:00:00Z"
        )

    def test_failure_preserves_last_good_revision_and_success_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            state = Path(temp_name) / "health.json"
            state.write_text(
                json.dumps(
                    {
                        "status": "healthy",
                        "last_success_at": "2026-07-30T01:00:00Z",
                        "authority_revision": "sha256:" + "b" * 64,
                        "authority_observed_at": "2026-07-30T00:59:59Z",
                    }
                )
            )
            with (
                mock.patch.object(
                    map_authority_notify,
                    "run_sync",
                    return_value=completed(1, stderr="authority unavailable"),
                ),
                mock.patch.object(
                    map_authority_notify, "notify", return_value=False
                ),
            ):
                result = map_authority_notify.run_once(
                    Path("/bin/map-authority"), state, now_epoch=2000
                )
            payload = json.loads(state.read_text())
        self.assertEqual(result, 1)
        self.assertEqual(payload["last_success_at"], "2026-07-30T01:00:00Z")
        self.assertEqual(payload["authority_revision"], "sha256:" + "b" * 64)
        self.assertEqual(payload["status"], "failing")


if __name__ == "__main__":
    unittest.main()
