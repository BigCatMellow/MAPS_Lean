PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS task_sequence (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    next_id INTEGER NOT NULL CHECK (next_id > 0)
);
INSERT OR IGNORE INTO task_sequence(singleton, next_id) VALUES (1, 1);

CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL DEFAULT 'default',
    title TEXT NOT NULL DEFAULT '',
    outcome TEXT NOT NULL DEFAULT '',
    task_type TEXT NOT NULL DEFAULT '',
    owner TEXT NOT NULL DEFAULT '',
    risk TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'NEEDS_SHAPING',
    agi_status TEXT NOT NULL DEFAULT 'UNCHECKED',
    decision_authority TEXT NOT NULL DEFAULT '',
    verification TEXT NOT NULL DEFAULT '',
    evidence_expected TEXT NOT NULL DEFAULT '',
    review_required TEXT NOT NULL DEFAULT '',
    escalation TEXT NOT NULL DEFAULT '',
    claimed_by TEXT,
    lease_expires_at TEXT,
    heartbeat_at TEXT,
    attempt INTEGER NOT NULL DEFAULT 0 CHECK (attempt >= 0),
    max_attempts INTEGER NOT NULL DEFAULT 3 CHECK (max_attempts > 0),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (status IN ('NEEDS_SHAPING','READY','ACTIVE','READY_FOR_REVIEW','CHANGES_REQUESTED','DONE','BLOCKED'))
);

CREATE TABLE IF NOT EXISTS task_inputs (
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    value TEXT NOT NULL,
    PRIMARY KEY(task_id, value)
);

CREATE TABLE IF NOT EXISTS task_sources (
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    value TEXT NOT NULL,
    PRIMARY KEY(task_id, value)
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    depends_on TEXT NOT NULL,
    PRIMARY KEY(task_id, depends_on)
);

CREATE TABLE IF NOT EXISTS task_output_paths (
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    PRIMARY KEY(task_id, path)
);

CREATE TABLE IF NOT EXISTS task_non_goals (
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    value TEXT NOT NULL,
    PRIMARY KEY(task_id, value)
);

CREATE TABLE IF NOT EXISTS task_acceptance_criteria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    criterion TEXT NOT NULL,
    UNIQUE(task_id, criterion)
);

CREATE TABLE IF NOT EXISTS task_stop_conditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    condition TEXT NOT NULL,
    UNIQUE(task_id, condition)
);

CREATE TABLE IF NOT EXISTS task_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    actor TEXT,
    summary TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_lease ON tasks(lease_expires_at);
CREATE INDEX IF NOT EXISTS idx_outputs_path ON task_output_paths(path);
CREATE INDEX IF NOT EXISTS idx_events_task ON task_events(task_id, id);

CREATE TABLE IF NOT EXISTS task_submissions (
    task_id TEXT PRIMARY KEY REFERENCES tasks(task_id) ON DELETE CASCADE,
    author_id TEXT NOT NULL,
    evidence TEXT NOT NULL,
    submission_count INTEGER NOT NULL DEFAULT 1 CHECK (submission_count > 0),
    first_submitted_at TEXT NOT NULL,
    submitted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    reviewer_id TEXT NOT NULL,
    verdict TEXT,
    summary TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    completed_at TEXT,
    CHECK (verdict IS NULL OR verdict IN ('APPROVED','CHANGES_REQUESTED','BLOCKED'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_reviews_one_open
    ON reviews(task_id)
    WHERE completed_at IS NULL;
