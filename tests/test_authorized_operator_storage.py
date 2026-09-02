"""SEC4 Half 3 — `AuthorizedOperatorStorageMixin` (the authorized-operator registry).

`work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`
Item B, with the session-17 operator answers.
"""

from __future__ import annotations

from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest

from runtime.state import TaskStore
from runtime.state.authorized_operator_storage import GENESIS_AUTHORIZER


class AuthorizedOperatorRegistryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "maps.db"
        self.store = TaskStore(self.db)

    def _genesis(self, operator_id="alice"):
        r = self.store.record_authorized_operator(
            operator_id, added_by=GENESIS_AUTHORIZER, decision_ref="d:genesis"
        )
        self.assertTrue(r.ok, r)
        return r

    # --- opt-in-by-data ---------------------------------------------------

    def test_empty_registry_is_inert(self):
        self.assertFalse(self.store.has_authorized_operator_registry())
        self.assertFalse(self.store.is_authorized_operator("anyone"))
        self.assertEqual(self.store.list_authorized_operators(), [])

    def test_genesis_flips_the_switch_and_authorizes(self):
        self._genesis("alice")
        self.assertTrue(self.store.has_authorized_operator_registry())
        self.assertTrue(self.store.is_authorized_operator("alice"))
        self.assertFalse(self.store.is_authorized_operator("bob"))

    # --- genesis rules --------------------------------------------------

    def test_first_add_must_be_genesis_sentinel(self):
        r = self.store.record_authorized_operator(
            "alice", added_by="alice", decision_ref="d:1"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "GENESIS_REQUIRED")
        self.assertFalse(self.store.has_authorized_operator_registry())

    def test_genesis_sentinel_rejected_once_seeded(self):
        self._genesis("alice")
        r = self.store.record_authorized_operator(
            "bob", added_by=GENESIS_AUTHORIZER, decision_ref="d:2"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "GENESIS_ALREADY_SEEDED")

    # --- authorizer must be authorized -------------------------------

    def test_authorized_operator_may_add_another(self):
        self._genesis("alice")
        r = self.store.record_authorized_operator(
            "bob", added_by="alice", decision_ref="d:2", display_name="Bob"
        )
        self.assertTrue(r.ok, r)
        self.assertTrue(self.store.is_authorized_operator("bob"))

    def test_unauthorized_authorizer_is_refused(self):
        self._genesis("alice")
        r = self.store.record_authorized_operator(
            "carol", added_by="eve", decision_ref="d:3"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "UNAUTHORIZED_AUTHORIZER")
        self.assertFalse(self.store.is_authorized_operator("carol"))

    def test_revoked_authorizer_cannot_add(self):
        self._genesis("alice")
        self.assertTrue(
            self.store.record_authorized_operator(
                "bob", added_by="alice", decision_ref="d:2"
            ).ok
        )
        self.assertTrue(
            self.store.revoke_authorized_operator(
                "bob", revoked_by="alice", decision_ref="d:rev"
            ).ok
        )
        r = self.store.record_authorized_operator(
            "carol", added_by="bob", decision_ref="d:4"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "UNAUTHORIZED_AUTHORIZER")

    # --- duplicates / missing ---------------------------------------

    def test_duplicate_add_is_refused(self):
        self._genesis("alice")
        self.assertTrue(
            self.store.record_authorized_operator(
                "bob", added_by="alice", decision_ref="d:2"
            ).ok
        )
        r = self.store.record_authorized_operator(
            "bob", added_by="alice", decision_ref="d:2b"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "OPERATOR_ALREADY_RECORDED")

    def test_unauthorized_revoker_is_refused(self):
        self._genesis("alice")
        self.assertTrue(
            self.store.record_authorized_operator(
                "bob", added_by="alice", decision_ref="d:2"
            ).ok
        )
        r = self.store.revoke_authorized_operator(
            "bob", revoked_by="eve", decision_ref="d:x"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "UNAUTHORIZED_AUTHORIZER")
        self.assertTrue(self.store.is_authorized_operator("bob"))

    def test_revoke_with_overlong_decision_ref_is_a_clean_failure(self):
        self._genesis("alice")
        self.assertTrue(
            self.store.record_authorized_operator(
                "bob", added_by="alice", decision_ref="d:2"
            ).ok
        )
        r = self.store.revoke_authorized_operator(
            "bob", revoked_by="alice", decision_ref="x" * 600
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "INVALID_REVOCATION")
        self.assertTrue(self.store.is_authorized_operator("bob"))

    def test_revoke_unknown_operator_is_typed(self):
        self._genesis("alice")
        r = self.store.revoke_authorized_operator(
            "ghost", revoked_by="alice", decision_ref="d:x"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "OPERATOR_NOT_RECORDED")

    def test_double_revoke_is_typed(self):
        self._genesis("alice")
        self.assertTrue(
            self.store.record_authorized_operator(
                "bob", added_by="alice", decision_ref="d:2"
            ).ok
        )
        self.assertTrue(
            self.store.revoke_authorized_operator(
                "bob", revoked_by="alice", decision_ref="d:r1"
            ).ok
        )
        r = self.store.revoke_authorized_operator(
            "bob", revoked_by="alice", decision_ref="d:r2"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "OPERATOR_ALREADY_REVOKED")

    # --- last-operator guard --------------------------------------

    def test_cannot_revoke_the_last_authorized_operator(self):
        self._genesis("alice")
        r = self.store.revoke_authorized_operator(
            "alice", revoked_by="alice", decision_ref="d:self"
        )
        self.assertFalse(r.ok)
        self.assertEqual(r.code, "CANNOT_REVOKE_LAST_OPERATOR")
        self.assertTrue(self.store.is_authorized_operator("alice"))

    def test_can_revoke_down_to_one(self):
        self._genesis("alice")
        self.assertTrue(
            self.store.record_authorized_operator(
                "bob", added_by="alice", decision_ref="d:2"
            ).ok
        )
        self.assertTrue(
            self.store.revoke_authorized_operator(
                "alice", revoked_by="bob", decision_ref="d:r"
            ).ok
        )
        self.assertFalse(self.store.is_authorized_operator("alice"))
        self.assertTrue(self.store.is_authorized_operator("bob"))
        # bob is now the last one
        self.assertEqual(
            self.store.revoke_authorized_operator(
                "bob", revoked_by="bob", decision_ref="d:r2"
            ).code,
            "CANNOT_REVOKE_LAST_OPERATOR",
        )

    # --- immutability --------------------------------------------

    def test_rows_are_trigger_locked(self):
        self._genesis("alice")
        with closing(sqlite3.connect(self.db)) as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE authorized_operators SET added_by='x'")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM authorized_operators")

    # --- validation ---------------------------------------------

    def test_blank_fields_are_typed_failures(self):
        self.assertEqual(
            self.store.record_authorized_operator(
                "  ", added_by=GENESIS_AUTHORIZER, decision_ref="d"
            ).code,
            "INVALID_OPERATOR_ID",
        )
        self.assertEqual(
            self.store.record_authorized_operator(
                "alice", added_by=GENESIS_AUTHORIZER, decision_ref="  "
            ).code,
            "INVALID_DECISION_REF",
        )

    def test_list_projects_composed_authorization(self):
        self._genesis("alice")
        self.store.record_authorized_operator(
            "bob", added_by="alice", decision_ref="d:2"
        )
        self.store.revoke_authorized_operator(
            "bob", revoked_by="alice", decision_ref="d:r"
        )
        by_id = {o["operator_id"]: o for o in self.store.list_authorized_operators()}
        self.assertTrue(by_id["alice"]["authorized"])
        self.assertFalse(by_id["bob"]["authorized"])
        self.assertEqual(by_id["bob"]["revoked_by"], "alice")

    def test_existing_store_tables_untouched(self):
        # a fresh store still creates every other table; a task round-trips.
        created = self.store.create_task(title="unrelated")
        self.assertTrue(created.ok, created)


if __name__ == "__main__":
    unittest.main()
