-- TASK-282: structured, append-only, per-criterion submission claims and
-- reviewer verdicts.
--
-- Additive and separate from the core migration/schema.sql, same pattern as
-- TASK-281's run_manifest_schema.sql: applied idempotently by
-- scripts/submission_records.py against the live map.db, never merged into
-- schema.sql by this task.
--
-- Never a competing task authority: tasks.status (and the existing
-- SUBMITTED/CHANGES_REQUESTED/APPROVED lifecycle driven by
-- db/claims.py + scripts/map_task.py) remains the sole source of truth for
-- what state a task is in. These tables record structured claim/verdict
-- evidence *alongside* a submission; nothing here reads or writes
-- tasks.status, and no query in submission_records.py drives a lifecycle
-- transition.
--
-- Append-only by construction: a claim is tied to a specific
-- (task_id, submission_count) pair (submission_count comes from TASK-278's
-- task_submission_authorship) and is never updated or deleted. Rework and
-- resubmission produce new claim rows under the next submission_count
-- rather than mutating prior ones. A reviewer verdict likewise never
-- mutates or removes the claim it verifies -- rejecting one criterion adds
-- a verdict row, it does not rewrite the implementer's original claim.

CREATE TABLE IF NOT EXISTS submission_criterion_claims (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id           TEXT NOT NULL REFERENCES tasks(task_id),
    submission_count  INTEGER NOT NULL,
    criterion_id      INTEGER NOT NULL REFERENCES task_acceptance_criteria(id),
    claimed_status    TEXT NOT NULL CHECK (claimed_status IN ('complete', 'partial', 'blocked')),
    evidence_refs     TEXT NOT NULL DEFAULT '[]',
    task_revision     TEXT,
    run_id            TEXT,
    author_id         TEXT NOT NULL REFERENCES agents(agent_id),
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Reviewer-verified status, deliberately a separate table from claims so a
-- reviewer can reject one criterion without touching the implementer's
-- claim row. Multiple verdicts against the same claim are allowed (e.g. a
-- second review pass); callers treat the latest row per claim_id as
-- current and the full history as the audit trail.
CREATE TABLE IF NOT EXISTS submission_criterion_verdicts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id        INTEGER NOT NULL REFERENCES submission_criterion_claims(id),
    verified_status TEXT NOT NULL CHECK (verified_status IN ('confirmed', 'rejected')),
    reviewer_id     TEXT NOT NULL REFERENCES agents(agent_id),
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_submission_claims_task
    ON submission_criterion_claims(task_id, submission_count);
CREATE INDEX IF NOT EXISTS idx_submission_verdicts_claim
    ON submission_criterion_verdicts(claim_id);
