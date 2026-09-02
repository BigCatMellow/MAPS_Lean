# PR #245 review evidence — SEC4 Half 3 slice 1: authorized-operator registry

Independent review by maps-lean-luve (vame authored). Two rounds: round 1 at
`8d4decf` (full review, two REQUEST_CHANGES items), then a delta pass covering
the fix commit + the coordinator's rebase-conflict resolution. `head_sha` below
is the final rebased branch tip.

## Round 1 (at `8d4decf`) — full review

The schema (append-only `authorized_operators` / `authorized_operator_revocations`
with house-pattern no-update/no-delete triggers, all CHECKs, the revocations FK +
index), the `AuthorizedOperatorStorageMixin` (composed "authorized as of now" =
row ∧ no revocation, genesis-sentinel rule, authorized-adds-authorized,
cannot-revoke-the-last-operator), and the CLI (`maps init --operator` genesis,
`maps operator add|revoke|list`, and the `maps skill approve` opt-in-by-data
identity check — CLI-side per design Q B3, `approve`-only, inert while the
registry is empty) are all correct and faithful to
`work/notes/2026-08-31-sec4-operator-lifecycle-transitions-and-identity-design.md`
Item B / Q B5 + the session-17 operator answers (#243).
`record_skill_lifecycle_transition` and `runtime/skills/lifecycle.py` are
untouched (the store stays a faithful recorder; the check is CLI-side).
CAPABILITY_CHECKLIST SEC4 + 6.10 rows stay IN PROGRESS — evidence text updated,
no status flip.

Two REQUEST_CHANGES items:
1. **M6** — `revoke_authorized_operator`'s `UNAUTHORIZED_AUTHORIZER` guard had no
   test (every revoke test used an authorized `revoked_by`).
2. The `revoke` INSERT lacked the `sqlite3.IntegrityError` guard that
   `record_authorized_operator`'s INSERT has — a pathological over-length
   `--decision-ref` on `maps operator revoke` raised an uncaught traceback
   instead of a clean `MutationResult`.

## Delta pass — fix commit + rebase-conflict resolution

### (a) Fix commit — both round-1 findings addressed

`runtime/state/authorized_operator_storage.py` +19/-6,
`tests/test_authorized_operator_storage.py` +28:
- `revoke_authorized_operator`: revocation INSERT now wrapped
  `try / except sqlite3.IntegrityError as exc: conn.rollback(); return
  MutationResult(False, "INVALID_REVOCATION", str(exc))` — same guard shape as
  `record_authorized_operator`'s insert, distinct code.
- docstring line: a revoked operator cannot be re-authorized in slice 1
  (rotation out of scope, design Q B5).
- `test_unauthorized_revoker_is_refused` — `revoke_authorized_operator("bob",
  revoked_by="eve")` → `UNAUTHORIZED_AUTHORIZER`, `bob` stays authorized.
- `test_revoke_with_overlong_decision_ref_is_a_clean_failure` — 600-char
  `decision_ref` → `INVALID_REVOCATION`, `bob` stays authorized.

Mutation re-check on the rebased tip:

| Mutation | Result |
|---|---|
| M6 — `revoke_*` `UNAUTHORIZED_AUTHORIZER` guard → `if False:` | KILLED (was the round-1 survivor) |
| swallow the `INVALID_REVOCATION` `except` (`… as exc: pass`) → falls through to `commit()` | KILLED |

Nothing else of substance in the fix commit.

### (b) Rebase-conflict resolution (onto current main)

3 additive conflicts resolved keep-both:
- **`runtime/state/schema.sql`** — keeps BOTH #244's `release_checks` table
  (+ triggers) AND #245's `authorized_operators` /
  `authorized_operator_revocations` tables (+ all 4 immutability triggers,
  CHECKs, FK, revocations index).
  `python3 -c "import sqlite3; sqlite3.connect(':memory:').executescript(open('runtime/state/schema.sql').read())"`
  → OK (both table sets + all triggers load clean).
- **`runtime/cli.py`** — keeps BOTH the `flow release-check` subparser
  (+ `from runtime.flow_release_check import flow_release_check` + dispatch) AND
  the `operator` subparser (+ `_dispatch_operator` + `maps init --operator`
  genesis + the `maps skill approve` `has_authorized_operator_registry()` /
  `UNAUTHORIZED_ACTOR` check).
- **`runtime/state/store.py`** — `AuthorizedOperatorStorageMixin` in the
  `TaskStore` MRO (auto-merged with #244's `ReleaseCheckMixin`).
- **`work/roadmaps/CAPABILITY_CHECKLIST.md`** — only SEC4 + 6.10 rows change vs
  main; both `IN PROGRESS` → `IN PROGRESS` (verified `-`/`+`), Half-3-slice-1
  evidence text added; the 6.9 row keeps #246's already-merged EXP-B text
  unchanged. No status flip on any row.

## Verification (foreground)

```
python3 -m unittest tests.test_authorized_operator_storage tests.test_cli_skill tests.test_flow_release_check
  → Ran 64 tests — OK
python3 -m runtime.smoke  → {"ok": true}, exit 0
python3 -c "import sqlite3; sqlite3.connect(':memory:').executescript(open('runtime/state/schema.sql').read())"
  → OK
```

## Verdict: APPROVE

The fix commit addresses both round-1 REQUEST_CHANGES items (M6 and the revoke
`IntegrityError` asymmetry) and is mutation-confirmed; the coordinator's 3-file
conflict resolution is clean additive keep-both, the schema loads, both CLI
surfaces are present, and no checklist status cell flipped.

reviewer: maps-lean-luve
head_sha: 01c89d555db6e8e0e289a3daff00c447797027d5
independent: true
summary: APPROVE — independent review of the SEC4 Half 3 slice 1 authorized-operator registry (schema + AuthorizedOperatorStorageMixin + maps operator/init/skill-approve CLI), faithful to the SEC4 operator-lifecycle design Item B / Q B5 + the #243 operator answers; two round-1 REQUEST_CHANGES items (untested revoke UNAUTHORIZED_AUTHORIZER guard, missing revoke IntegrityError guard) are addressed in the fix commit and mutation-confirmed KILLED on the rebased tip; the coordinator's 3-file additive keep-both conflict resolution is verified clean (schema loads with both release_checks and authorized_operators, both CLI subparsers present, no checklist status flip); 64 targeted tests + smoke green.
