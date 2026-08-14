PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- TASK-307 security fix: server-side record of what transfer_rotation_claims()
-- actually changed, so restore_rotation_claims() can bind a restore to a real
-- prior transfer by opaque transfer_id instead of trusting caller-supplied
-- row JSON verbatim (the original damo-nivo design let any caller with
-- gateway access craft arbitrary old_row/replacement_row/task_rows and
-- overwrite unrelated agents/tasks). restored_at enforces single-use.
CREATE TABLE IF NOT EXISTS rotation_transfers (
    transfer_id       TEXT PRIMARY KEY,
    old_agent         TEXT NOT NULL,
    replacement_agent TEXT NOT NULL,
    snapshot_json     TEXT NOT NULL,
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    restored_at       TEXT
);

CREATE TABLE IF NOT EXISTS agents (
    agent_id        TEXT PRIMARY KEY,
    label           TEXT NOT NULL,
    agent_type      TEXT NOT NULL DEFAULT 'core',
    helper_tag      TEXT,
    status          TEXT NOT NULL DEFAULT 'available',
    reason          TEXT,
    resume_after    TEXT,
    last_heartbeat  TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id          TEXT PRIMARY KEY,
    project_id       TEXT NOT NULL,
    title            TEXT NOT NULL,
    description      TEXT NOT NULL DEFAULT '',
    task_type        TEXT NOT NULL,
    role             TEXT NOT NULL,
    status           TEXT NOT NULL DEFAULT 'BACKLOG',
    priority         INTEGER NOT NULL DEFAULT 3,
    required_agent   TEXT REFERENCES agents(agent_id),
    owner            TEXT REFERENCES agents(agent_id),
    claimed_by       TEXT REFERENCES agents(agent_id),
    lease_expires_at TEXT,
    heartbeat_at     TEXT,
    attempt          INTEGER NOT NULL DEFAULT 1,
    max_attempts     INTEGER NOT NULL DEFAULT 3,
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    decision_class   TEXT,
    risk_class       TEXT,
    risk_severity    TEXT,
    task_tier        TEXT,
    requires_operator_approval INTEGER NOT NULL DEFAULT 0,
    destructive_action        INTEGER,
    final_review              INTEGER,
    final_decision            INTEGER,
    broad_architecture        INTEGER,
    broad_rewrite             INTEGER,
    canonical_map_mutation    INTEGER,
    shell_required            INTEGER,
    trust_boundary_crossing   INTEGER
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id     TEXT NOT NULL REFERENCES tasks(task_id),
    depends_on  TEXT NOT NULL REFERENCES tasks(task_id),
    PRIMARY KEY (task_id, depends_on)
);

CREATE TABLE IF NOT EXISTS task_output_paths (
    task_id  TEXT NOT NULL REFERENCES tasks(task_id),
    path     TEXT NOT NULL,
    PRIMARY KEY (task_id, path)
);

CREATE TABLE IF NOT EXISTS task_acceptance_criteria (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id    TEXT NOT NULL REFERENCES tasks(task_id),
    criterion  TEXT NOT NULL,
    met        INTEGER NOT NULL DEFAULT 0,
    UNIQUE (task_id, criterion)
);

CREATE TABLE IF NOT EXISTS helpers (
    helper_id       TEXT PRIMARY KEY,
    owner_agent_id  TEXT NOT NULL REFERENCES agents(agent_id),
    task_id         TEXT REFERENCES tasks(task_id),
    scope           TEXT NOT NULL,
    note_path       TEXT,
    status          TEXT NOT NULL DEFAULT 'active',
    started_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    stopped_at      TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    message_id    TEXT PRIMARY KEY,
    message_type  TEXT NOT NULL,
    task_id       TEXT REFERENCES tasks(task_id),
    sender_id     TEXT NOT NULL REFERENCES agents(agent_id),
    recipient_id  TEXT REFERENCES agents(agent_id),
    subject       TEXT,
    body          TEXT NOT NULL,
    handoff_path  TEXT,
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id    TEXT PRIMARY KEY,
    task_id        TEXT REFERENCES tasks(task_id),
    artifact_type  TEXT NOT NULL,
    path           TEXT NOT NULL UNIQUE,
    title          TEXT,
    created_by     TEXT REFERENCES agents(agent_id),
    status         TEXT NOT NULL DEFAULT 'draft',
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    updated_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS artifact_versions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    artifact_id     TEXT NOT NULL REFERENCES artifacts(artifact_id),
    version         INTEGER NOT NULL DEFAULT 1,
    path            TEXT NOT NULL,
    created_by      TEXT REFERENCES agents(agent_id),
    change_summary  TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (artifact_id, version)
);

CREATE TABLE IF NOT EXISTS reviews (
    review_id     TEXT PRIMARY KEY,
    task_id       TEXT NOT NULL REFERENCES tasks(task_id),
    artifact_id   TEXT REFERENCES artifacts(artifact_id),
    reviewer_id   TEXT NOT NULL REFERENCES agents(agent_id),
    verdict       TEXT,
    summary       TEXT,
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    completed_at  TEXT
);

-- TASK-278: the author of the current submission is lifecycle state, not task
-- ownership.  Keep it separately so owner reassignment and review artifacts
-- cannot rewrite or invent the identity used by no-self-review gates.
CREATE TABLE IF NOT EXISTS task_submission_authorship (
    task_id           TEXT PRIMARY KEY REFERENCES tasks(task_id),
    author_id         TEXT NOT NULL REFERENCES agents(agent_id),
    submission_count  INTEGER NOT NULL DEFAULT 1 CHECK (submission_count > 0),
    first_submitted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    submitted_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- TASK-199 (IDEA-0017): at most one open (uncompleted) review claim per task
-- at a time, so independent reviewers can't both start full review work on
-- the same SUBMITTED task before either finalizes.
CREATE UNIQUE INDEX IF NOT EXISTS idx_reviews_open_claim
    ON reviews(task_id)
    WHERE completed_at IS NULL;

CREATE TABLE IF NOT EXISTS task_release_records (
    task_id         TEXT PRIMARY KEY REFERENCES tasks(task_id),
    checklist_path  TEXT NOT NULL,
    released_by     TEXT NOT NULL REFERENCES agents(agent_id),
    summary         TEXT NOT NULL DEFAULT '',
    release_tier    TEXT NOT NULL DEFAULT 'full',
    tier_reason     TEXT NOT NULL DEFAULT '',
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS review_findings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id    TEXT NOT NULL REFERENCES reviews(review_id),
    severity     TEXT NOT NULL,
    area         TEXT,
    description  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decisions (
    decision_id  TEXT PRIMARY KEY,
    title        TEXT NOT NULL,
    body         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',
    proposed_by  TEXT REFERENCES agents(agent_id),
    task_id      TEXT REFERENCES tasks(task_id),
    created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    resolved_at  TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type      TEXT NOT NULL,
    task_id         TEXT REFERENCES tasks(task_id),
    sender_id       TEXT REFERENCES agents(agent_id),
    summary         TEXT NOT NULL,
    artifact_paths  TEXT,
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE (created_at, event_type, task_id, sender_id, summary)
);

CREATE TABLE IF NOT EXISTS approval_gates (
    gate_id              TEXT PRIMARY KEY,
    name                 TEXT NOT NULL,
    required_after_task  TEXT REFERENCES tasks(task_id),
    status               TEXT NOT NULL DEFAULT 'pending',
    approved_by          TEXT,
    approved_at          TEXT,
    created_at           TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS approval_gate_resume_tasks (
    gate_id  TEXT NOT NULL REFERENCES approval_gates(gate_id),
    task_id  TEXT NOT NULL REFERENCES tasks(task_id),
    PRIMARY KEY (gate_id, task_id)
);

CREATE INDEX IF NOT EXISTS idx_tasks_status        ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_owner         ON tasks(owner);
CREATE INDEX IF NOT EXISTS idx_tasks_lease_expires ON tasks(lease_expires_at);
CREATE INDEX IF NOT EXISTS idx_events_task_id      ON events(task_id);
CREATE INDEX IF NOT EXISTS idx_events_created_at   ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_recipient  ON messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_task_id   ON artifacts(task_id);
CREATE INDEX IF NOT EXISTS idx_helpers_status      ON helpers(status);
