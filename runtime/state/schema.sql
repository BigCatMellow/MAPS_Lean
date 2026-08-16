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

CREATE TABLE IF NOT EXISTS task_policy (
    task_id TEXT PRIMARY KEY REFERENCES tasks(task_id) ON DELETE CASCADE,
    requires_operator_approval INTEGER NOT NULL DEFAULT 0 CHECK (requires_operator_approval IN (0,1)),
    destructive_action INTEGER NOT NULL DEFAULT 0 CHECK (destructive_action IN (0,1)),
    external_side_effect INTEGER NOT NULL DEFAULT 0 CHECK (external_side_effect IN (0,1)),
    security_sensitive INTEGER NOT NULL DEFAULT 0 CHECK (security_sensitive IN (0,1)),
    broad_architecture INTEGER NOT NULL DEFAULT 0 CHECK (broad_architecture IN (0,1)),
    paid_execution INTEGER NOT NULL DEFAULT 1 CHECK (paid_execution IN (0,1)),
    approved_by TEXT,
    approved_at TEXT,
    approval_note TEXT NOT NULL DEFAULT ''
);

-- Immutable execution binding. Full context is not copied; file references are
-- hashed separately. Task revision excludes lifecycle churn.
CREATE TABLE IF NOT EXISTS run_manifests (
    run_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    task_revision TEXT NOT NULL,
    worker_id TEXT NOT NULL,
    session_id TEXT,
    readable_scope TEXT NOT NULL DEFAULT '[]',
    writable_scope TEXT NOT NULL DEFAULT '[]',
    forbidden_scope TEXT NOT NULL DEFAULT '[]',
    runtime_limits TEXT NOT NULL DEFAULT '{}',
    base_revision TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_run_manifests_task ON run_manifests(task_id, created_at);

CREATE TABLE IF NOT EXISTS run_context_refs (
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    PRIMARY KEY(run_id, path)
);

-- Run bindings are append-only audit evidence. There is intentionally no
-- UPDATE/DELETE path, even for internal callers.
CREATE TRIGGER IF NOT EXISTS trg_run_manifests_no_update
BEFORE UPDATE ON run_manifests
BEGIN
    SELECT RAISE(ABORT, 'run manifests are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_manifests_no_delete
BEFORE DELETE ON run_manifests
BEGIN
    SELECT RAISE(ABORT, 'run manifests are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_context_no_update
BEFORE UPDATE ON run_context_refs
BEGIN
    SELECT RAISE(ABORT, 'run context refs are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_context_no_delete
BEFORE DELETE ON run_context_refs
BEGIN
    SELECT RAISE(ABORT, 'run context refs are immutable');
END;

-- Project/adapter-qualified provider/session identity is separate append-only
-- lineage. Project identity is copied from canonical task state at record time
-- only to preserve the provider namespace; it grants no task authority.
CREATE TABLE IF NOT EXISTS run_session_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    relation TEXT NOT NULL CHECK (relation IN ('ATTACH','REPLACE')),
    project_id TEXT NOT NULL CHECK (length(trim(project_id)) > 0),
    adapter_id TEXT NOT NULL CHECK (length(trim(adapter_id)) BETWEEN 1 AND 128),
    session_id TEXT NOT NULL CHECK (length(trim(session_id)) BETWEEN 1 AND 128),
    replaces_link_id INTEGER REFERENCES run_session_links(id),
    evidence_ref TEXT NOT NULL CHECK (length(trim(evidence_ref)) BETWEEN 1 AND 256),
    created_by TEXT NOT NULL CHECK (length(trim(created_by)) BETWEEN 1 AND 128),
    created_at TEXT NOT NULL,
    CHECK (
        (relation = 'ATTACH' AND replaces_link_id IS NULL)
        OR (relation = 'REPLACE' AND replaces_link_id IS NOT NULL)
    ),
    UNIQUE(project_id, adapter_id, session_id)
);
CREATE INDEX IF NOT EXISTS idx_run_session_links_run
    ON run_session_links(run_id, id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_run_session_one_attach
    ON run_session_links(run_id)
    WHERE relation = 'ATTACH';
CREATE UNIQUE INDEX IF NOT EXISTS idx_run_session_one_replacement
    ON run_session_links(replaces_link_id)
    WHERE replaces_link_id IS NOT NULL;

-- Every stored provider-context key must match canonical task state for the
-- owning immutable run. Direct SQL cannot invent a competing project identity.
CREATE TRIGGER IF NOT EXISTS trg_run_session_project_match
BEFORE INSERT ON run_session_links
WHEN NOT EXISTS (
    SELECT 1
    FROM run_manifests AS r
    JOIN tasks AS t ON t.task_id = r.task_id
    WHERE r.run_id = NEW.run_id
      AND trim(t.project_id) = trim(NEW.project_id)
)
BEGIN
    SELECT RAISE(ABORT, 'run session project must match canonical task project');
END;

-- Direct SQL must preserve the immutable manifest's only pre-existing session
-- fact. A bare manifest session may be adapter-qualified, never silently replaced.
CREATE TRIGGER IF NOT EXISTS trg_run_session_attach_manifest_match
BEFORE INSERT ON run_session_links
WHEN NEW.relation = 'ATTACH'
     AND EXISTS (
        SELECT 1
        FROM run_manifests
        WHERE run_id = NEW.run_id
          AND NULLIF(trim(session_id), '') IS NOT NULL
          AND trim(session_id) <> trim(NEW.session_id)
     )
BEGIN
    SELECT RAISE(ABORT, 'run session attach conflicts with immutable manifest session');
END;

-- Replacement lineage is local to one run. The self-FK alone cannot express
-- this cross-column invariant, so enforce it at the SQLite boundary too.
CREATE TRIGGER IF NOT EXISTS trg_run_session_replace_same_run
BEFORE INSERT ON run_session_links
WHEN NEW.relation = 'REPLACE'
     AND NOT EXISTS (
        SELECT 1
        FROM run_session_links
        WHERE id = NEW.replaces_link_id
          AND run_id = NEW.run_id
     )
BEGIN
    SELECT RAISE(ABORT, 'run session replacement predecessor must belong to the same run');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_session_links_no_update
BEFORE UPDATE ON run_session_links
BEGIN
    SELECT RAISE(ABORT, 'run session links are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_session_links_no_delete
BEFORE DELETE ON run_session_links
BEGIN
    SELECT RAISE(ABORT, 'run session links are immutable');
END;

-- Continuity is evidence that two worker/session identities share the same
-- inherited execution context. It disqualifies independent review; it grants
-- no ownership or task authority.
CREATE TABLE IF NOT EXISTS continuity_links (
    predecessor_id TEXT NOT NULL,
    replacement_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY(predecessor_id, replacement_id),
    CHECK(predecessor_id <> replacement_id)
);
CREATE INDEX IF NOT EXISTS idx_continuity_replacement ON continuity_links(replacement_id);

-- Optional structured evidence. Recording one criterion claim opts the current
-- submission into criterion-level verification; implementer claims and reviewer
-- verdicts are separate append-only audit records.
CREATE TABLE IF NOT EXISTS submission_criterion_claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    submission_count INTEGER NOT NULL CHECK (submission_count > 0),
    criterion_id INTEGER NOT NULL REFERENCES task_acceptance_criteria(id) ON DELETE CASCADE,
    claimed_status TEXT NOT NULL CHECK (claimed_status IN ('complete','partial','blocked')),
    evidence_refs TEXT NOT NULL DEFAULT '[]',
    task_revision TEXT NOT NULL,
    run_id TEXT REFERENCES run_manifests(run_id),
    author_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_criterion_claims_submission
    ON submission_criterion_claims(task_id, submission_count, criterion_id, id);

CREATE TABLE IF NOT EXISTS submission_criterion_verdicts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL REFERENCES submission_criterion_claims(id) ON DELETE CASCADE,
    verified_status TEXT NOT NULL CHECK (verified_status IN ('confirmed','rejected')),
    reviewer_id TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS trg_criterion_claims_no_update
BEFORE UPDATE ON submission_criterion_claims
BEGIN
    SELECT RAISE(ABORT, 'criterion claims are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_criterion_claims_no_delete
BEFORE DELETE ON submission_criterion_claims
BEGIN
    SELECT RAISE(ABORT, 'criterion claims are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_criterion_verdicts_no_update
BEFORE UPDATE ON submission_criterion_verdicts
BEGIN
    SELECT RAISE(ABORT, 'criterion verdicts are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_criterion_verdicts_no_delete
BEFORE DELETE ON submission_criterion_verdicts
BEGIN
    SELECT RAISE(ABORT, 'criterion verdicts are immutable');
END;

-- Post-completion outcome observations are later knowledge. They are append-only
-- evidence and never alter the original task/review lifecycle result.
CREATE TABLE IF NOT EXISTS task_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    run_id TEXT REFERENCES run_manifests(run_id),
    outcome_status TEXT NOT NULL CHECK (outcome_status IN ('SUCCESS','PARTIAL','FAILURE','UNKNOWN')),
    failure_class TEXT NOT NULL DEFAULT '',
    escaped_defect INTEGER NOT NULL DEFAULT 0 CHECK (escaped_defect IN (0,1)),
    rework_count INTEGER NOT NULL DEFAULT 0 CHECK (rework_count >= 0),
    operator_intervention_count INTEGER NOT NULL DEFAULT 0 CHECK (operator_intervention_count >= 0),
    actor_id TEXT NOT NULL DEFAULT '',
    actor_class TEXT NOT NULL CHECK (actor_class IN ('OPERATOR','CORE_AGENT','HELPER','SYSTEM','UNKNOWN')),
    source TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    task_revision TEXT NOT NULL,
    supersedes_outcome_id INTEGER REFERENCES task_outcomes(id),
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_task_outcomes_task ON task_outcomes(task_id, id);

CREATE TRIGGER IF NOT EXISTS trg_task_outcomes_no_update
BEFORE UPDATE ON task_outcomes
BEGIN
    SELECT RAISE(ABORT, 'task outcomes are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_task_outcomes_no_delete
BEFORE DELETE ON task_outcomes
BEGIN
    SELECT RAISE(ABORT, 'task outcomes are immutable');
END;
