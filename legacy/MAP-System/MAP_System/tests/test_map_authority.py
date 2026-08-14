from __future__ import annotations

import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tarfile
import tempfile
import time
import unittest
from unittest import mock

from MAP_System.db import authority
from MAP_System.graph import runner as graph_runner
from MAP_System.scripts import map_authority


def archive_bytes(files: dict[str, bytes], manifest: dict | None = None) -> bytes:
    manifest = manifest or {
        name: {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
        for name, data in files.items()
    }
    members = {**files, "manifest.json": (json.dumps(manifest) + "\n").encode()}
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, data in members.items():
            info = tarfile.TarInfo(name)
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


class RequestValidationTests(unittest.TestCase):
    def test_request_round_trip_preserves_shell_shaped_argument_as_data(self) -> None:
        shaped = "$(touch /tmp/never-run); `id`; a b"
        encoded = map_authority.encode_request("task", ["show", shaped])
        self.assertEqual(
            map_authority.decode_request(encoded),
            {"operation": "task", "args": ["show", shaped]},
        )

    def test_rejects_unknown_operation(self) -> None:
        encoded = base64.urlsafe_b64encode(
            b'{"version":1,"operation":"shell","args":["id"]}'
        ).decode()
        with self.assertRaisesRegex(map_authority.AuthorityError, "not allowlisted"):
            map_authority.decode_request(encoded)

    def test_rejects_invalid_base64(self) -> None:
        with self.assertRaisesRegex(map_authority.AuthorityError, "base64"):
            map_authority.decode_request("%%%")

    def test_rejects_oversized_request(self) -> None:
        with self.assertRaisesRegex(map_authority.AuthorityError, "oversized"):
            map_authority.decode_request("A" * (map_authority.MAX_REQUEST_BYTES * 2 + 1))

    def test_rejects_nul_and_too_many_arguments(self) -> None:
        with self.assertRaisesRegex(map_authority.AuthorityError, "NUL"):
            map_authority.encode_request("task", ["show", "bad\x00value"])
        with self.assertRaisesRegex(map_authority.AuthorityError, "too many"):
            map_authority.decode_request(
                map_authority.encode_request(
                    "task", ["show"] * (map_authority.MAX_ARGUMENTS + 1)
                )
            )

    def test_task_dispatch_rejects_unknown_verbs_and_path_overrides(self) -> None:
        with mock.patch.object(
            map_authority, "load_authority_config", return_value={"mode": "authority"}
        ):
            with self.assertRaisesRegex(map_authority.AuthorityError, "verb"):
                map_authority.dispatch_authority("task", ["shell", "id"])
            for arguments in (
                ["show", "TASK-1", "--db", "/tmp/alternate.db"],
                ["show", "TASK-1", "--db=/tmp/alternate.db"],
            ):
                with self.assertRaisesRegex(map_authority.AuthorityError, "canonical"):
                    map_authority.dispatch_authority("task", arguments)

    def test_remote_request_uses_argv_without_a_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            key = Path(temp_name) / "key"
            key.touch()
            completed = subprocess.CompletedProcess(
                args=[], returncode=0, stdout='{"version":1,"ok":true}', stderr=""
            )
            config = {
                "mode": "mirror",
                "authority_host": "192.0.2.1",
                "authority_user": "home",
                "authority_key": str(key),
            }
            with mock.patch.object(
                map_authority.subprocess, "run", return_value=completed
            ) as run:
                response = map_authority.remote_request(
                    config, "task", ["show", "$(touch /tmp/never-run)"]
                )
            self.assertTrue(response["ok"])
            positional, keywords = run.call_args
            self.assertIsInstance(positional[0], list)
            self.assertNotIn("shell", keywords)

    def test_remote_request_surfaces_remote_error_from_stdout_on_nonzero_exit(
        self,
    ) -> None:
        """The gateway prints its structured error to stdout and exits 1 on
        ok=False; the client must surface that message, not just the (empty)
        stderr."""
        with tempfile.TemporaryDirectory() as temp_name:
            key = Path(temp_name) / "key"
            key.touch()
            completed = subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout='{"version":1,"ok":false,"error":"old or replacement agent is absent from SQLite"}',
                stderr="",
            )
            config = {
                "mode": "mirror",
                "authority_host": "192.0.2.1",
                "authority_user": "home",
                "authority_key": str(key),
            }
            with mock.patch.object(
                map_authority.subprocess, "run", return_value=completed
            ):
                with self.assertRaisesRegex(
                    map_authority.AuthorityError,
                    "old or replacement agent is absent from SQLite",
                ):
                    map_authority.remote_request(config, "rotation-transfer", ["a", "b"])

    def test_route_embeds_authority_contract(self) -> None:
        with (
            mock.patch.object(
                map_authority,
                "load_authority_config",
                return_value={"mode": "authority"},
            ),
            mock.patch.object(
                map_authority,
                "run_checked",
                return_value={
                    "version": 1,
                    "ok": True,
                    "returncode": 0,
                    "stdout": '{"next_route":"review"}',
                    "stderr": "",
                },
            ),
            mock.patch.object(
                map_authority,
                "authority_status",
                return_value={"freshness": "AUTHORITATIVE"},
            ),
        ):
            routed = map_authority.dispatch_authority("route", [])
        payload = json.loads(routed["stdout"])
        self.assertEqual(payload["next_route"], "review")
        self.assertEqual(payload["authority"]["freshness"], "AUTHORITATIVE")


class GuardTests(unittest.TestCase):
    def test_mirror_guard_blocks_only_production_database(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            temp = Path(temp_name)
            production = temp / "map.db"
            fixture = temp / "fixture.db"
            config = temp / "authority.json"
            config.write_text('{"mode":"mirror","authority_host":"ruki"}\n')
            with (
                mock.patch.object(authority, "PRODUCTION_DB", production),
                mock.patch.dict(os.environ, {"MAP_AUTHORITY_CONFIG": str(config)}),
            ):
                with self.assertRaises(authority.RemoteAuthorityRequired):
                    authority.guard_production_write(production)
                authority.guard_production_write(fixture)

    def test_invalid_configuration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            config = Path(temp_name) / "authority.json"
            config.write_text("{invalid")
            with mock.patch.dict(os.environ, {"MAP_AUTHORITY_CONFIG": str(config)}):
                with self.assertRaises(authority.RemoteAuthorityRequired):
                    authority.load_authority_config()

    def test_installer_rejects_unsupported_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            home = Path(temp_name)
            config_dir = home / ".config"
            config_dir.mkdir()
            (config_dir / "map-authority.json").write_text('{"mode":"mirorr"}\n')
            completed = subprocess.run(
                [
                    str(map_authority.REPO / "install-map-system.sh"),
                    "--dry-run",
                    "--skip-apt",
                    "--skip-hcom",
                    "--skip-wezterm",
                    "--skip-desktop",
                    "--skip-venv",
                ],
                cwd=map_authority.REPO,
                env={**os.environ, "HOME": str(home)},
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Unsupported MAP authority mode", completed.stderr)
            self.assertNotIn(
                "configure MAP Command Center user services", completed.stdout
            )


class WriterServiceTests(unittest.TestCase):
    """TASK-316: map-rns-watcher.service should only disqualify a sync around
    an actual write to a mirrored file, not merely while the always-on
    service is running, while any other active local writer service must
    still block unconditionally (the original TASK-310 protection)."""

    @staticmethod
    def _systemctl_stub(active_units):
        def run(cmd, **kwargs):
            unit = cmd[-1]
            returncode = 0 if unit in active_units else 3
            return subprocess.CompletedProcess(cmd, returncode, stdout="", stderr="")

        return run

    def test_quiet_rns_watcher_does_not_block_sync(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            events = Path(temp_name) / "events.jsonl"
            events.write_text("old\n")
            old = time.time() - 3600
            os.utime(events, (old, old))
            with (
                mock.patch.object(
                    map_authority, "RNS_WATCHER_MIRRORED_WRITE_TARGETS", (events,)
                ),
                mock.patch.object(
                    map_authority.shutil, "which", return_value="/usr/bin/systemctl"
                ),
                mock.patch.object(
                    map_authority.subprocess,
                    "run",
                    side_effect=self._systemctl_stub({"map-rns-watcher.service"}),
                ),
            ):
                self.assertEqual(map_authority.active_local_writer_services(), [])

    def test_recent_rns_watcher_write_still_blocks_sync(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            events = Path(temp_name) / "events.jsonl"
            events.write_text("fresh\n")
            with (
                mock.patch.object(
                    map_authority, "RNS_WATCHER_MIRRORED_WRITE_TARGETS", (events,)
                ),
                mock.patch.object(
                    map_authority.shutil, "which", return_value="/usr/bin/systemctl"
                ),
                mock.patch.object(
                    map_authority.subprocess,
                    "run",
                    side_effect=self._systemctl_stub({"map-rns-watcher.service"}),
                ),
            ):
                self.assertEqual(
                    map_authority.active_local_writer_services(),
                    ["map-rns-watcher.service"],
                )

    def test_genuine_second_authority_writer_still_blocks_unconditionally(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            events = Path(temp_name) / "events.jsonl"
            with (
                mock.patch.object(
                    map_authority, "RNS_WATCHER_MIRRORED_WRITE_TARGETS", (events,)
                ),
                mock.patch.object(
                    map_authority.shutil, "which", return_value="/usr/bin/systemctl"
                ),
                mock.patch.object(
                    map_authority.subprocess,
                    "run",
                    side_effect=self._systemctl_stub(
                        {"map-command-center-maintenance.service"}
                    ),
                ),
            ):
                self.assertEqual(
                    map_authority.active_local_writer_services(),
                    ["map-command-center-maintenance.service"],
                )

    def test_recently_written_missing_file_is_not_recent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            missing = Path(temp_name) / "never-written.jsonl"
            self.assertFalse(
                map_authority._recently_written((missing,), quiet_seconds=15)
            )

    def test_recently_written_fails_closed_on_stat_error(self) -> None:
        path = mock.MagicMock(spec=Path)
        path.stat.side_effect = PermissionError("denied")
        self.assertTrue(map_authority._recently_written((path,), quiet_seconds=15))

    @staticmethod
    def _write_cgroup_events(root: Path, unit: str, populated: str) -> None:
        events = (
            root
            / "user.slice"
            / "user-1000.slice"
            / "user@1000.service"
            / "app.slice"
            / unit
            / "cgroup.events"
        )
        events.parent.mkdir(parents=True)
        events.write_text(f"populated {populated}\nfrozen 0\n")

    def test_user_bus_failure_falls_back_to_quiet_cgroup_service(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            self._write_cgroup_events(root, map_authority.RNS_WATCHER_SERVICE, "1")
            events = root / "events.jsonl"
            events.write_text("old\n")
            old = time.time() - 3600
            os.utime(events, (old, old))
            bus_error = subprocess.CompletedProcess(
                ["systemctl"], 1, stdout="", stderr="Failed to connect to bus: No data available\n"
            )
            with (
                mock.patch.object(map_authority, "CGROUP_ROOT", root),
                mock.patch.object(
                    map_authority, "RNS_WATCHER_MIRRORED_WRITE_TARGETS", (events,)
                ),
                mock.patch.object(map_authority.shutil, "which", return_value="/usr/bin/systemctl"),
                mock.patch.object(map_authority.subprocess, "run", return_value=bus_error),
                mock.patch.object(map_authority.os, "getuid", return_value=1000),
            ):
                self.assertEqual(map_authority.active_local_writer_services(), [])

    def test_writer_probe_reports_cgroup_fallback_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            self._write_cgroup_events(root, map_authority.RNS_WATCHER_SERVICE, "0")
            bus_error = subprocess.CompletedProcess(
                ["systemctl"],
                1,
                stdout="",
                stderr="Failed to connect to bus: No data available\n",
            )
            with (
                mock.patch.object(map_authority, "CGROUP_ROOT", root),
                mock.patch.object(
                    map_authority.shutil, "which", return_value="/usr/bin/systemctl"
                ),
                mock.patch.object(
                    map_authority.subprocess, "run", return_value=bus_error
                ),
                mock.patch.object(map_authority.os, "getuid", return_value=1000),
            ):
                services, source = map_authority._probe_active_local_writer_services()

        self.assertEqual(services, [])
        self.assertEqual(source, "cgroup_v2_fallback")

    def test_writer_probe_reports_systemctl_source(self) -> None:
        with (
            mock.patch.object(
                map_authority.shutil, "which", return_value="/usr/bin/systemctl"
            ),
            mock.patch.object(
                map_authority.subprocess,
                "run",
                side_effect=self._systemctl_stub(set()),
            ),
        ):
            services, source = map_authority._probe_active_local_writer_services()

        self.assertEqual(services, [])
        self.assertEqual(source, "systemctl")

    def test_user_bus_failure_keeps_recent_watcher_collision_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            self._write_cgroup_events(root, map_authority.RNS_WATCHER_SERVICE, "1")
            events = root / "events.jsonl"
            events.write_text("fresh\n")
            bus_error = subprocess.CompletedProcess(
                ["systemctl"], 1, stdout="", stderr="Failed to connect to bus: No data available\n"
            )
            with (
                mock.patch.object(map_authority, "CGROUP_ROOT", root),
                mock.patch.object(
                    map_authority, "RNS_WATCHER_MIRRORED_WRITE_TARGETS", (events,)
                ),
                mock.patch.object(map_authority.shutil, "which", return_value="/usr/bin/systemctl"),
                mock.patch.object(map_authority.subprocess, "run", return_value=bus_error),
                mock.patch.object(map_authority.os, "getuid", return_value=1000),
            ):
                self.assertEqual(
                    map_authority.active_local_writer_services(),
                    [map_authority.RNS_WATCHER_SERVICE],
                )

    def test_user_bus_failure_keeps_genuine_writer_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            self._write_cgroup_events(
                root, "map-command-center-maintenance.service", "1"
            )
            bus_error = subprocess.CompletedProcess(
                ["systemctl"], 1, stdout="", stderr="Failed to connect to bus: No data available\n"
            )
            with (
                mock.patch.object(map_authority, "CGROUP_ROOT", root),
                mock.patch.object(map_authority.shutil, "which", return_value="/usr/bin/systemctl"),
                mock.patch.object(map_authority.subprocess, "run", return_value=bus_error),
                mock.patch.object(map_authority.os, "getuid", return_value=1000),
            ):
                self.assertEqual(
                    map_authority.active_local_writer_services(),
                    ["map-command-center-maintenance.service"],
                )

    def test_user_bus_failure_fails_closed_on_invalid_cgroup_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            self._write_cgroup_events(root, map_authority.RNS_WATCHER_SERVICE, "maybe")
            bus_error = subprocess.CompletedProcess(
                ["systemctl"], 1, stdout="", stderr="Failed to connect to bus: No data available\n"
            )
            with (
                mock.patch.object(map_authority, "CGROUP_ROOT", root),
                mock.patch.object(map_authority.shutil, "which", return_value="/usr/bin/systemctl"),
                mock.patch.object(map_authority.subprocess, "run", return_value=bus_error),
                mock.patch.object(map_authority.os, "getuid", return_value=1000),
            ):
                with self.assertRaisesRegex(map_authority.AuthorityError, "invalid"):
                    map_authority.active_local_writer_services()

    def test_user_bus_failure_fails_closed_on_uid_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "cgroup.controllers").write_text("cpu memory\n")
            self._write_cgroup_events(root, map_authority.RNS_WATCHER_SERVICE, "0")
            bus_error = subprocess.CompletedProcess(
                ["systemctl"], 1, stdout="", stderr="Failed to connect to bus: No data available\n"
            )
            with (
                mock.patch.object(map_authority, "CGROUP_ROOT", root),
                mock.patch.object(map_authority.shutil, "which", return_value="/usr/bin/systemctl"),
                mock.patch.object(map_authority.subprocess, "run", return_value=bus_error),
                mock.patch.object(map_authority.os, "getuid", return_value=2000),
            ):
                with self.assertRaisesRegex(
                    map_authority.AuthorityError, "not found for uid 2000"
                ):
                    map_authority.active_local_writer_services()

    def test_non_bus_systemctl_error_does_not_use_cgroup_fallback(self) -> None:
        denied = subprocess.CompletedProcess(
            ["systemctl"], 1, stdout="", stderr="permission denied\n"
        )
        with (
            mock.patch.object(map_authority.shutil, "which", return_value="/usr/bin/systemctl"),
            mock.patch.object(map_authority.subprocess, "run", return_value=denied),
            mock.patch.object(
                map_authority, "_active_writer_services_from_cgroup_v2"
            ) as fallback,
        ):
            with self.assertRaisesRegex(map_authority.AuthorityError, "permission denied"):
                map_authority.active_local_writer_services()
        fallback.assert_not_called()


class SnapshotTests(unittest.TestCase):
    def test_valid_snapshot_round_trip(self) -> None:
        files = {
            "map.db": b"sqlite bytes",
            "tasks/TASK-1.json": b'{"task_id":"TASK-1"}\n',
        }
        self.assertEqual(map_authority.validate_snapshot(archive_bytes(files)), files)

    def test_rejects_path_traversal_and_links(self) -> None:
        bad = archive_bytes({"../map.db": b"x", "map.db": b"db"})
        with self.assertRaisesRegex(map_authority.AuthorityError, "unsafe"):
            map_authority.validate_snapshot(bad)

        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            link = tarfile.TarInfo("map.db")
            link.type = tarfile.SYMTYPE
            link.linkname = "/etc/passwd"
            archive.addfile(link)
            manifest = b"{}\n"
            info = tarfile.TarInfo("manifest.json")
            info.size = len(manifest)
            archive.addfile(info, io.BytesIO(manifest))
        with self.assertRaisesRegex(map_authority.AuthorityError, "unsafe"):
            map_authority.validate_snapshot(buffer.getvalue())

    def test_rejects_checksum_mismatch(self) -> None:
        files = {"map.db": b"actual"}
        manifest = {"map.db": {"sha256": "0" * 64, "size": 6}}
        with self.assertRaisesRegex(map_authority.AuthorityError, "checksum"):
            map_authority.validate_snapshot(archive_bytes(files, manifest))

    def test_reported_revision_mismatch_is_rejected_before_install(self) -> None:
        archive = archive_bytes({"map.db": b"validated"})
        response = {
            "ok": True,
            "archive_b64": base64.b64encode(archive).decode(),
            "sha256": hashlib.sha256(archive).hexdigest(),
            "authority_revision": "sha256:" + "0" * 64,
        }
        with (
            mock.patch.object(
                map_authority, "remote_request", return_value=response
            ),
            mock.patch.object(map_authority, "install_snapshot") as install,
        ):
            with self.assertRaisesRegex(
                map_authority.AuthorityError, "revision"
            ):
                map_authority.sync_mirror({"mode": "mirror"})
        install.assert_not_called()

    def test_install_replaces_database_last_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            lock = root / ".locks" / "sync.lock"
            db.write_bytes(b"old")
            files = {
                "map.db": b"new",
                "tasks/TASK-1.json": b"task",
                "workflow/task_graph.json": b"graph",
            }
            with (
                mock.patch.object(map_authority, "ROOT", root),
                mock.patch.object(map_authority, "DB_PATH", db),
                mock.patch.object(map_authority, "DEFAULT_LOCK", lock),
                mock.patch.object(
                    map_authority, "active_local_writer_services", return_value=[]
                ),
            ):
                map_authority.install_snapshot(files)
            self.assertEqual(db.read_bytes(), b"new")
            self.assertEqual(db.stat().st_mode & 0o777, 0o444)
            self.assertEqual((root / "tasks/TASK-1.json").read_bytes(), b"task")

    def test_install_refuses_while_a_local_writer_is_active(self) -> None:
        with mock.patch.object(
            map_authority,
            "active_local_writer_services",
            return_value=["map-rns-watcher.service"],
        ):
            with self.assertRaisesRegex(map_authority.AuthorityError, "disabled"):
                map_authority.install_snapshot({"map.db": b"x"})

    def test_install_aborts_when_watcher_writes_between_probe_and_replace(self) -> None:
        """TASK-316 follow-up (zinu review, TOCTOU finding): the initial
        active_local_writer_services() probe runs before staging even
        starts, so a watcher write can land after it passes but before the
        real events.jsonl replace. install_snapshot must re-check
        immediately before that specific replace and abort/roll back
        instead of silently clobbering the write."""
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            lock = root / ".locks" / "sync.lock"
            db.write_bytes(b"old")
            existing_graph = root / "workflow" / "task_graph.json"
            existing_graph.parent.mkdir(parents=True)
            existing_graph.write_bytes(b"old graph")
            events_target = root / "events" / "events.jsonl"
            files = {
                "map.db": b"new",
                "events/events.jsonl": b"new events",
                "workflow/task_graph.json": b"new graph",
            }
            with (
                mock.patch.object(map_authority, "ROOT", root),
                mock.patch.object(map_authority, "DB_PATH", db),
                mock.patch.object(map_authority, "DEFAULT_LOCK", lock),
                mock.patch.object(
                    map_authority, "active_local_writer_services", return_value=[]
                ),
                mock.patch.object(
                    map_authority,
                    "RNS_WATCHER_MIRRORED_WRITE_TARGETS",
                    (events_target,),
                ),
                mock.patch.object(
                    map_authority, "_recently_written", return_value=True
                ),
            ):
                with self.assertRaisesRegex(
                    map_authority.AuthorityError, "events.jsonl"
                ):
                    map_authority.install_snapshot(files)
            self.assertEqual(db.read_bytes(), b"old")
            self.assertEqual(existing_graph.read_bytes(), b"old graph")
            self.assertFalse(events_target.exists())

    def test_failed_database_swap_restores_old_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            wal = root / "map.db-wal"
            shm = root / "map.db-shm"
            lock = root / ".locks" / "sync.lock"
            db.write_bytes(b"old database")
            wal.write_bytes(b"old wal")
            shm.write_bytes(b"old shm")
            real_replace = os.replace
            injected = False

            def fail_database_swap(source: str | Path, destination: str | Path) -> None:
                nonlocal injected
                source_path = Path(source)
                if (
                    not injected
                    and
                    Path(destination) == db
                    and source_path.name.startswith(".map.db.")
                ):
                    injected = True
                    raise OSError("injected database swap failure")
                real_replace(source, destination)

            with (
                mock.patch.object(map_authority, "ROOT", root),
                mock.patch.object(map_authority, "DB_PATH", db),
                mock.patch.object(map_authority, "DEFAULT_LOCK", lock),
                mock.patch.object(
                    map_authority, "active_local_writer_services", return_value=[]
                ),
                mock.patch.object(map_authority.os, "replace", side_effect=fail_database_swap),
            ):
                with self.assertRaisesRegex(OSError, "injected"):
                    map_authority.install_snapshot({"map.db": b"new database"})

            self.assertEqual(db.read_bytes(), b"old database")
            self.assertEqual(wal.read_bytes(), b"old wal")
            self.assertEqual(shm.read_bytes(), b"old shm")

    def test_failed_mirror_swap_rolls_back_earlier_mirrors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            task = root / "tasks" / "TASK-1.json"
            graph = root / "workflow" / "task_graph.json"
            lock = root / ".locks" / "sync.lock"
            task.parent.mkdir()
            graph.parent.mkdir()
            db.write_bytes(b"old database")
            task.write_bytes(b"old task")
            graph.write_bytes(b"old graph")
            real_replace = os.replace
            injected = False

            def fail_graph_swap(source: str | Path, destination: str | Path) -> None:
                nonlocal injected
                source_path = Path(source)
                if (
                    not injected
                    and
                    Path(destination) == graph
                    and source_path.name.startswith(".task_graph.json.")
                ):
                    injected = True
                    raise OSError("injected mirror swap failure")
                real_replace(source, destination)

            with (
                mock.patch.object(map_authority, "ROOT", root),
                mock.patch.object(map_authority, "DB_PATH", db),
                mock.patch.object(map_authority, "DEFAULT_LOCK", lock),
                mock.patch.object(
                    map_authority, "active_local_writer_services", return_value=[]
                ),
                mock.patch.object(map_authority.os, "replace", side_effect=fail_graph_swap),
            ):
                with self.assertRaisesRegex(OSError, "injected"):
                    map_authority.install_snapshot(
                        {
                            "map.db": b"new database",
                            "tasks/TASK-1.json": b"new task",
                            "workflow/task_graph.json": b"new graph",
                        }
                    )

            self.assertEqual(db.read_bytes(), b"old database")
            self.assertEqual(task.read_bytes(), b"old task")
            self.assertEqual(graph.read_bytes(), b"old graph")


class AuthorityFreshnessTests(unittest.TestCase):
    NOW = datetime(2026, 7, 30, 2, 0, tzinfo=timezone.utc)

    def mirror_status(
        self,
        root: Path,
        state: dict,
        *,
        database_writable: bool = False,
        writer_services: list[str] | None = None,
        now: datetime | None = None,
    ) -> dict:
        db = root / "map.db"
        health = root / "health.json"
        health.write_text(json.dumps(state))
        return map_authority.authority_status(
            {"mode": "mirror", "authority_host": "ruki"},
            now=now or self.NOW,
            health_path=health,
            db_path=db,
            writer_services=[] if writer_services is None else writer_services,
            database_writable=database_writable,
            freshness_threshold_seconds=180,
        )

    def test_fresh_mirror_requires_matching_installed_revision(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            db.write_bytes(b"consistent mirror")
            revision = map_authority.file_revision(db)
            status = self.mirror_status(
                root,
                {
                    "status": "healthy",
                    "last_success_at": "2026-07-30T01:59:00Z",
                    "authority_revision": revision,
                    "authority_observed_at": "2026-07-30T01:58:59Z",
                },
            )
        self.assertEqual(status["freshness"], "FRESH")
        self.assertEqual(status["freshness_age_seconds"], 60)
        self.assertTrue(status["topology_valid"])

    def test_failed_sync_with_last_good_snapshot_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            db.write_bytes(b"last good")
            status = self.mirror_status(
                root,
                {
                    "status": "failing",
                    "last_success_at": "2026-07-30T01:59:30Z",
                    "authority_revision": map_authority.file_revision(db),
                    "last_error": "connection refused",
                },
            )
        self.assertEqual(status["freshness"], "STALE")
        self.assertEqual(status["last_error"], "connection refused")

    def test_sync_age_beyond_threshold_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            db.write_bytes(b"aged mirror")
            status = self.mirror_status(
                root,
                {
                    "status": "healthy",
                    "last_success_at": "2026-07-30T01:56:59Z",
                    "authority_revision": map_authority.file_revision(db),
                },
            )
        self.assertEqual(status["freshness"], "STALE")
        self.assertEqual(status["freshness_age_seconds"], 181)

    def test_active_writer_service_invalidates_mirror_topology(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            db.write_bytes(b"writer collision")
            status = self.mirror_status(
                root,
                {
                    "status": "healthy",
                    "last_success_at": "2026-07-30T01:59:00Z",
                    "authority_revision": map_authority.file_revision(db),
                },
                writer_services=["map-rns-watcher.service"],
            )
        self.assertEqual(status["freshness"], "INVALID")
        self.assertFalse(status["topology_valid"])
        self.assertEqual(
            status["local_writer_services"], ["map-rns-watcher.service"]
        )

    def test_unavailable_service_manager_invalidates_mirror_topology(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            health = root / "health.json"
            db.write_bytes(b"unproven topology")
            health.write_text(
                json.dumps(
                    {
                        "status": "healthy",
                        "last_success_at": "2026-07-30T01:59:00Z",
                        "authority_revision": map_authority.file_revision(db),
                    }
                )
            )
            with mock.patch.object(map_authority.shutil, "which", return_value=None):
                status = map_authority.authority_status(
                    {"mode": "mirror", "authority_host": "ruki"},
                    now=self.NOW,
                    health_path=health,
                    db_path=db,
                    database_writable=False,
                    freshness_threshold_seconds=180,
                )
        self.assertEqual(status["freshness"], "INVALID")
        self.assertFalse(status["topology_valid"])
        self.assertIn("systemctl was not found", status["last_error"])
        self.assertEqual(status["writer_service_probe_source"], "unavailable")

    def test_status_surfaces_cgroup_writer_probe_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            health = root / "health.json"
            db.write_bytes(b"fallback-audited mirror")
            health.write_text(
                json.dumps(
                    {
                        "status": "healthy",
                        "last_success_at": "2026-07-30T01:59:00Z",
                        "authority_revision": map_authority.file_revision(db),
                    }
                )
            )
            with mock.patch.object(
                map_authority,
                "_probe_active_local_writer_services",
                return_value=([], "cgroup_v2_fallback"),
            ):
                status = map_authority.authority_status(
                    {"mode": "mirror", "authority_host": "ruki"},
                    now=self.NOW,
                    health_path=health,
                    db_path=db,
                    database_writable=False,
                    freshness_threshold_seconds=180,
                )

        self.assertTrue(status["topology_valid"])
        self.assertEqual(
            status["writer_service_probe_source"], "cgroup_v2_fallback"
        )

    def test_missing_success_record_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "map.db").write_bytes(b"unproven")
            status = self.mirror_status(root, {"status": "unknown"})
        self.assertEqual(status["freshness"], "UNAVAILABLE")

    def test_writable_mirror_and_future_clock_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            db.write_bytes(b"mirror")
            state = {
                "status": "healthy",
                "last_success_at": "2026-07-30T02:10:00Z",
                "authority_revision": map_authority.file_revision(db),
            }
            writable = self.mirror_status(root, state, database_writable=True)
            future = self.mirror_status(root, state, database_writable=False)
        self.assertEqual(writable["freshness"], "INVALID")
        self.assertFalse(writable["topology_valid"])
        self.assertEqual(future["freshness"], "INVALID")
        self.assertIn("future", future["last_error"])

    def test_revision_mismatch_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            (root / "map.db").write_bytes(b"unexpected")
            status = self.mirror_status(
                root,
                {
                    "status": "healthy",
                    "last_success_at": "2026-07-30T01:59:00Z",
                    "authority_revision": "sha256:" + "0" * 64,
                },
            )
        self.assertEqual(status["freshness"], "INVALID")
        self.assertIn("does not match", status["last_error"])

    def test_authority_revision_uses_online_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            db = root / "map.db"
            with sqlite3.connect(db) as conn:
                conn.execute("CREATE TABLE evidence (value TEXT)")
                conn.execute("INSERT INTO evidence VALUES ('canonical')")
            status = map_authority.authority_status(
                {"mode": "authority"},
                now=self.NOW,
                db_path=db,
                writer_services=[],
                database_writable=True,
            )
        self.assertEqual(status["freshness"], "AUTHORITATIVE")
        self.assertRegex(status["authority_revision"], r"^sha256:[0-9a-f]{64}$")
        self.assertIsNone(status["authority_host"])


class FreshnessGateTests(unittest.TestCase):
    """TASK-310: every route consumer must fail closed on a non-fresh mirror."""

    def routed(self, **overrides: object) -> dict:
        base = {
            "next_route": "review",
            "recommended_action": "Send submitted tasks to an independent reviewer.",
            "ready_tasks": ["TASK-999"],
        }
        base.update(overrides)
        return base

    def test_fresh_authority_leaves_recommendation_untouched(self) -> None:
        gated = map_authority.apply_freshness_gate(
            self.routed(), {"freshness": "FRESH", "last_error": ""}
        )
        self.assertEqual(gated["next_route"], "review")
        self.assertNotIn("stale_authority_next_route", gated)
        self.assertNotIn("stale_authority_recommended_action", gated)

    def test_authoritative_mode_leaves_recommendation_untouched(self) -> None:
        gated = map_authority.apply_freshness_gate(
            self.routed(), {"freshness": "AUTHORITATIVE", "last_error": ""}
        )
        self.assertEqual(gated["next_route"], "review")

    def test_stale_mirror_overrides_recommendation_but_preserves_it(self) -> None:
        gated = map_authority.apply_freshness_gate(
            self.routed(),
            {"freshness": "STALE", "last_error": "sync age exceeds threshold"},
        )
        self.assertEqual(gated["next_route"], "STALE_AUTHORITY")
        self.assertIn("sync age exceeds threshold", gated["recommended_action"])
        self.assertEqual(gated["stale_authority_next_route"], "review")
        self.assertEqual(
            gated["stale_authority_recommended_action"],
            "Send submitted tasks to an independent reviewer.",
        )
        # Underlying task data stays inspectable -- only the recommendation is gated.
        self.assertEqual(gated["ready_tasks"], ["TASK-999"])

    def test_unavailable_and_invalid_also_gate(self) -> None:
        for freshness in ("UNAVAILABLE", "INVALID"):
            with self.subTest(freshness=freshness):
                gated = map_authority.apply_freshness_gate(
                    self.routed(), {"freshness": freshness, "last_error": ""}
                )
                self.assertEqual(gated["next_route"], "STALE_AUTHORITY")
                self.assertIn(freshness, gated["recommended_action"])

    def test_missing_last_error_still_produces_a_readable_message(self) -> None:
        gated = map_authority.apply_freshness_gate(
            self.routed(), {"freshness": "UNAVAILABLE", "last_error": None}
        )
        self.assertIn("no fresh sync recorded", gated["recommended_action"])

    def test_direct_runner_and_wrapped_route_share_non_fresh_gate(self) -> None:
        state = self.routed()
        authority_payload = {
            "freshness": "STALE",
            "last_error": "sync age exceeds threshold",
        }
        wrapped = map_authority.apply_freshness_gate(
            graph_runner.summarize(state), dict(authority_payload)
        )
        with (
            mock.patch.object(
                graph_runner, "load_authority_config", return_value={"mode": "mirror"}
            ),
            mock.patch.object(
                graph_runner, "authority_status", return_value=dict(authority_payload)
            ),
        ):
            direct = graph_runner.summarize_with_authority(state)
        self.assertEqual(direct["next_route"], "STALE_AUTHORITY")
        self.assertEqual(direct["next_route"], wrapped["next_route"])
        self.assertEqual(direct["authority"], wrapped["authority"])

    def test_gate_always_attaches_the_authority_object(self) -> None:
        authority = {"freshness": "FRESH", "authority_revision": "sha256:" + "a" * 64}
        gated = map_authority.apply_freshness_gate(self.routed(), authority)
        self.assertIs(gated["authority"], authority)


if __name__ == "__main__":
    unittest.main()
