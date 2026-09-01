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

CREATE TABLE IF NOT EXISTS task_environment (
    task_id TEXT PRIMARY KEY REFERENCES tasks(task_id) ON DELETE CASCADE,
    spec_ref TEXT NOT NULL,
    max_age_seconds INTEGER NOT NULL CHECK (max_age_seconds > 0),
    required_for_routing INTEGER NOT NULL DEFAULT 0 CHECK (required_for_routing IN (0,1)),
    allow_older_task_revision INTEGER NOT NULL DEFAULT 0 CHECK (allow_older_task_revision IN (0,1))
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

CREATE TABLE IF NOT EXISTS run_worktree_bindings (
    run_id TEXT PRIMARY KEY REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    repo_root TEXT NOT NULL,
    git_common_dir TEXT NOT NULL,
    git_dir TEXT NOT NULL,
    worktree_private_dir TEXT NOT NULL DEFAULT '',
    head_revision TEXT NOT NULL,
    bound_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS run_context_refs (
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    PRIMARY KEY(run_id, path)
);

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

CREATE TRIGGER IF NOT EXISTS trg_run_worktree_bindings_no_update
BEFORE UPDATE ON run_worktree_bindings
BEGIN
    SELECT RAISE(ABORT, 'run worktree bindings are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_worktree_bindings_no_delete
BEFORE DELETE ON run_worktree_bindings
BEGIN
    SELECT RAISE(ABORT, 'run worktree bindings are immutable');
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

-- Exact submission-attempt/run attribution is append-only and optional. The
-- mutable task_submissions row remains the source for the current submission.
CREATE TABLE IF NOT EXISTS submission_run_links (
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    submission_count INTEGER NOT NULL CHECK (submission_count > 0),
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    linked_at TEXT NOT NULL,
    PRIMARY KEY(task_id, submission_count)
);
CREATE INDEX IF NOT EXISTS idx_submission_run_links_run
    ON submission_run_links(run_id, task_id, submission_count);

CREATE TRIGGER IF NOT EXISTS trg_submission_run_same_task
BEFORE INSERT ON submission_run_links
WHEN NOT EXISTS (
    SELECT 1
    FROM run_manifests
    WHERE run_id = NEW.run_id AND task_id = NEW.task_id
)
BEGIN
    SELECT RAISE(ABORT, 'submission run must belong to the same task');
END;

CREATE TRIGGER IF NOT EXISTS trg_submission_run_attempt_exists
BEFORE INSERT ON submission_run_links
WHEN NOT EXISTS (
    SELECT 1
    FROM task_submissions
    WHERE task_id = NEW.task_id
      AND submission_count >= NEW.submission_count
)
BEGIN
    SELECT RAISE(ABORT, 'submission attempt does not exist');
END;

CREATE TRIGGER IF NOT EXISTS trg_submission_run_links_no_update
BEFORE UPDATE ON submission_run_links
BEGIN
    SELECT RAISE(ABORT, 'submission run links are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_submission_run_links_no_delete
BEFORE DELETE ON submission_run_links
BEGIN
    SELECT RAISE(ABORT, 'submission run links are immutable');
END;

-- Project/adapter-qualified provider/session identity is separate append-only
-- lineage. Project identity is copied from canonical task state at record time
-- only to preserve the provider namespace; it grants no task authority.
CREATE TABLE IF NOT EXISTS run_session_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    relation TEXT NOT NULL CHECK (relation IN ('ATTACH','REPLACE')),
    project_id TEXT NOT NULL CHECK (length(project_id) > 0),
    adapter_id TEXT NOT NULL CHECK (
        length(adapter_id) BETWEEN 1 AND 128
        AND adapter_id GLOB '[A-Za-z0-9]*'
        AND adapter_id NOT GLOB '*[^A-Za-z0-9_.:@-]*'
    ),
    session_id TEXT NOT NULL CHECK (
        length(session_id) BETWEEN 1 AND 128
        AND session_id GLOB '[A-Za-z0-9]*'
        AND session_id NOT GLOB '*[^A-Za-z0-9_.:@-]*'
    ),
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

-- Every stored provider-context key must exactly match canonical task state for
-- the owning immutable run. Direct SQL cannot invent a trim-equivalent project.
CREATE TRIGGER IF NOT EXISTS trg_run_session_project_match
BEFORE INSERT ON run_session_links
WHEN NOT EXISTS (
    SELECT 1
    FROM run_manifests AS r
    JOIN tasks AS t ON t.task_id = r.task_id
    WHERE r.run_id = NEW.run_id
      AND t.project_id = NEW.project_id
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

-- Helper invocation lineage records only relationship identity. HelperResult JSON
-- remains the source for helper status, summary, and output paths. A session parent
-- is already project-scoped by accepted A1; requiring the same immutable run keeps
-- the helper relation inside that canonical project context without copying a
-- second project authority into this table.
CREATE TABLE IF NOT EXISTS run_helper_links (
    helper_run_id TEXT PRIMARY KEY CHECK (length(trim(helper_run_id)) BETWEEN 1 AND 128),
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    invoker_worker_id TEXT NOT NULL CHECK (length(trim(invoker_worker_id)) BETWEEN 1 AND 128),
    parent_session_link_id INTEGER REFERENCES run_session_links(id),
    parent_helper_run_id TEXT REFERENCES run_helper_links(helper_run_id),
    evidence_ref TEXT NOT NULL CHECK (length(trim(evidence_ref)) BETWEEN 1 AND 256),
    created_by TEXT NOT NULL CHECK (length(trim(created_by)) BETWEEN 1 AND 128),
    created_at TEXT NOT NULL,
    CHECK (parent_session_link_id IS NULL OR parent_helper_run_id IS NULL),
    CHECK (parent_helper_run_id IS NULL OR parent_helper_run_id <> helper_run_id)
);
CREATE INDEX IF NOT EXISTS idx_run_helper_links_run
    ON run_helper_links(run_id, created_at, helper_run_id);

CREATE TRIGGER IF NOT EXISTS trg_run_helper_parent_session_same_run
BEFORE INSERT ON run_helper_links
WHEN NEW.parent_session_link_id IS NOT NULL
     AND NOT EXISTS (
        SELECT 1 FROM run_session_links
        WHERE id = NEW.parent_session_link_id AND run_id = NEW.run_id
     )
BEGIN
    SELECT RAISE(ABORT, 'helper parent session must belong to the same run');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_helper_parent_helper_same_run
BEFORE INSERT ON run_helper_links
WHEN NEW.parent_helper_run_id IS NOT NULL
     AND NOT EXISTS (
        SELECT 1 FROM run_helper_links
        WHERE helper_run_id = NEW.parent_helper_run_id AND run_id = NEW.run_id
     )
BEGIN
    SELECT RAISE(ABORT, 'helper parent helper must belong to the same run');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_helper_links_no_update
BEFORE UPDATE ON run_helper_links
BEGIN
    SELECT RAISE(ABORT, 'run helper links are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_helper_links_no_delete
BEFORE DELETE ON run_helper_links
BEGIN
    SELECT RAISE(ABORT, 'run helper links are immutable');
END;

-- Recovery lineage relates immutable runs. RecoveryStore continues to own the
-- mutable incident state/attempt/backoff/error record referenced by recovery_ref.
-- Same-task enforcement also keeps predecessor/replacement inside the canonical
-- project owned by that task; no project field is duplicated here.
CREATE TABLE IF NOT EXISTS run_recovery_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    predecessor_run_id TEXT NOT NULL UNIQUE REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    replacement_run_id TEXT NOT NULL UNIQUE REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    recovery_ref TEXT NOT NULL CHECK (length(trim(recovery_ref)) BETWEEN 1 AND 256),
    evidence_ref TEXT NOT NULL CHECK (length(trim(evidence_ref)) BETWEEN 1 AND 256),
    created_by TEXT NOT NULL CHECK (length(trim(created_by)) BETWEEN 1 AND 128),
    created_at TEXT NOT NULL,
    CHECK (predecessor_run_id <> replacement_run_id)
);
CREATE INDEX IF NOT EXISTS idx_run_recovery_replacement
    ON run_recovery_links(replacement_run_id);

CREATE TRIGGER IF NOT EXISTS trg_run_recovery_same_task
BEFORE INSERT ON run_recovery_links
WHEN NOT EXISTS (
    SELECT 1
    FROM run_manifests predecessor
    JOIN run_manifests replacement
      ON predecessor.task_id = replacement.task_id
    WHERE predecessor.run_id = NEW.predecessor_run_id
      AND replacement.run_id = NEW.replacement_run_id
)
BEGIN
    SELECT RAISE(ABORT, 'recovery runs must belong to the same task');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_recovery_chronological
BEFORE INSERT ON run_recovery_links
WHEN (
    SELECT julianday(replacement.created_at) < julianday(predecessor.created_at)
    FROM run_manifests predecessor, run_manifests replacement
    WHERE predecessor.run_id = NEW.predecessor_run_id
      AND replacement.run_id = NEW.replacement_run_id
)
BEGIN
    SELECT RAISE(ABORT, 'replacement run cannot predate predecessor run');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_recovery_no_cycle
BEFORE INSERT ON run_recovery_links
WHEN EXISTS (
    WITH RECURSIVE descendants(run_id) AS (
        SELECT replacement_run_id
        FROM run_recovery_links
        WHERE predecessor_run_id = NEW.replacement_run_id
        UNION ALL
        SELECT links.replacement_run_id
        FROM run_recovery_links links
        JOIN descendants
          ON links.predecessor_run_id = descendants.run_id
    )
    SELECT 1
    FROM descendants
    WHERE run_id = NEW.predecessor_run_id
)
BEGIN
    SELECT RAISE(ABORT, 'recovery lineage cannot contain a cycle');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_recovery_links_no_update
BEFORE UPDATE ON run_recovery_links
BEGIN
    SELECT RAISE(ABORT, 'run recovery links are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_recovery_links_no_delete
BEFORE DELETE ON run_recovery_links
BEGIN
    SELECT RAISE(ABORT, 'run recovery links are immutable');
END;

-- Environment observations are append-only evidence attached to an immutable
-- run. They never alter the run contract, task lifecycle, ownership, or policy.
CREATE TABLE IF NOT EXISTS run_environment_evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES run_manifests(run_id) ON DELETE CASCADE,
    spec_ref TEXT NOT NULL,
    environment_spec_hash TEXT NOT NULL,
    fingerprint_sha256 TEXT NOT NULL,
    compatibility_state TEXT NOT NULL CHECK (
        compatibility_state IN (
            'COMPATIBLE','COMPATIBLE_WITH_WARNINGS','DRIFTED','INCOMPATIBLE','UNKNOWN'
        )
    ),
    reference_fingerprint_sha256 TEXT,
    spec_snapshot TEXT NOT NULL,
    fingerprint_snapshot TEXT NOT NULL,
    compatibility_snapshot TEXT NOT NULL,
    recorded_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_run_environment_evidence_run
    ON run_environment_evidence(run_id, id);

CREATE TRIGGER IF NOT EXISTS trg_run_environment_evidence_no_update
BEFORE UPDATE ON run_environment_evidence
BEGIN
    SELECT RAISE(ABORT, 'run environment evidence is immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_run_environment_evidence_no_delete
BEFORE DELETE ON run_environment_evidence
BEGIN
    SELECT RAISE(ABORT, 'run environment evidence is immutable');
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

-- Immutable subject/evidence binding for a claimed review. This identifies the
-- exact submission/task/run/artifact subject under review; it grants no review
-- authority and does not alter the task lifecycle by itself.
CREATE TABLE IF NOT EXISTS review_subjects (
    review_id INTEGER PRIMARY KEY REFERENCES reviews(id) ON DELETE CASCADE,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    submission_count INTEGER NOT NULL CHECK (submission_count > 0),
    task_revision TEXT NOT NULL,
    run_id TEXT REFERENCES run_manifests(run_id),
    artifact_refs TEXT NOT NULL DEFAULT '[]',
    freshness_mode TEXT NOT NULL CHECK (
        freshness_mode IN ('REVISION_BOUND','REDERIVED_AT_REVIEW','NON_CONSEQUENTIAL')
    ),
    bound_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_review_subjects_task
    ON review_subjects(task_id, review_id);

CREATE TRIGGER IF NOT EXISTS trg_review_subjects_no_update
BEFORE UPDATE ON review_subjects
BEGIN
    SELECT RAISE(ABORT, 'review subjects are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_review_subjects_no_delete
BEFORE DELETE ON review_subjects
BEGIN
    SELECT RAISE(ABORT, 'review subjects are immutable');
END;

-- Operational-learning candidate lessons (Storage-0 only). Records only
-- CANDIDATE-status lesson snapshots produced by runtime/operational_learning.py
-- validation; there is no promotion/retirement mechanism yet, enforced here at
-- the schema level (status is restricted to 'CANDIDATE') as well as by the
-- Python layer. promotion/retirement/superseded_by columns exist for future
-- schema stability but are always NULL while this constraint holds, since
-- validate_lesson_record() rejects a CANDIDATE record carrying promotion or
-- retirement data.
CREATE TABLE IF NOT EXISTS operational_lessons (
    lesson_id TEXT PRIMARY KEY CHECK (length(trim(lesson_id)) BETWEEN 1 AND 128),
    lesson_version INTEGER NOT NULL CHECK (lesson_version = 1),
    status TEXT NOT NULL CHECK (status = 'CANDIDATE'),
    claim TEXT NOT NULL CHECK (length(trim(claim)) > 0),
    source_kind TEXT NOT NULL CHECK (
        source_kind IN (
            'TASK_OUTCOME','INCIDENT','OPERATOR_OBSERVATION',
            'NON_TASK_OBSERVATION','RESEARCH'
        )
    ),
    source_refs TEXT NOT NULL CHECK (json_valid(source_refs) AND json_array_length(source_refs) > 0),
    applicability TEXT NOT NULL CHECK (json_valid(applicability)),
    created_by TEXT NOT NULL CHECK (length(trim(created_by)) BETWEEN 1 AND 128),
    created_at TEXT NOT NULL,
    promotion TEXT CHECK (promotion IS NULL OR json_valid(promotion)),
    retirement TEXT CHECK (retirement IS NULL OR json_valid(retirement)),
    superseded_by TEXT REFERENCES operational_lessons(lesson_id),
    CHECK (superseded_by IS NULL OR superseded_by <> lesson_id)
);
CREATE INDEX IF NOT EXISTS idx_operational_lessons_status_created
    ON operational_lessons(status, created_at);

CREATE TRIGGER IF NOT EXISTS trg_operational_lessons_no_update
BEFORE UPDATE ON operational_lessons
BEGIN
    SELECT RAISE(ABORT, 'operational lesson candidates are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_lessons_no_delete
BEFORE DELETE ON operational_lessons
BEGIN
    SELECT RAISE(ABORT, 'operational lesson candidates are immutable');
END;

-- Operational-learning promotion/retirement decisions (Authority-1). The
-- base operational_lessons row above never changes -- status stays
-- CHECK-locked to 'CANDIDATE' and the row is immutable, per Storage-0. A
-- lesson's effective status (CANDIDATE / ACTIVE / RETIRED) is derived by
-- composing the base row with the rows below, never by mutating a status
-- column. Every row here is one explicit, operator-authored decision
-- (decision_ref + actor required); there is no automatic/evidence-gated
-- promotion path (operator decision recorded 2026-08-17, Option A).
CREATE TABLE IF NOT EXISTS operational_lesson_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    lesson_id TEXT NOT NULL REFERENCES operational_lessons(lesson_id),
    decision_kind TEXT NOT NULL CHECK (decision_kind IN ('PROMOTE', 'RETIRE')),
    decision_payload TEXT NOT NULL CHECK (json_valid(decision_payload)),
    decided_by TEXT NOT NULL CHECK (length(trim(decided_by)) BETWEEN 1 AND 128),
    decided_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_operational_lesson_decisions_lesson
    ON operational_lesson_decisions(lesson_id, created_at);

CREATE TRIGGER IF NOT EXISTS trg_operational_lesson_decisions_no_update
BEFORE UPDATE ON operational_lesson_decisions
BEGIN
    SELECT RAISE(ABORT, 'operational lesson decisions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_lesson_decisions_no_delete
BEFORE DELETE ON operational_lesson_decisions
BEGIN
    SELECT RAISE(ABORT, 'operational lesson decisions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_lesson_decisions_no_reretire
BEFORE INSERT ON operational_lesson_decisions
WHEN EXISTS (
    SELECT 1 FROM operational_lesson_decisions
    WHERE lesson_id = NEW.lesson_id AND decision_kind = 'RETIRE'
)
BEGIN
    SELECT RAISE(ABORT, 'operational lesson is already retired; retirement is terminal');
END;

CREATE TRIGGER IF NOT EXISTS trg_operational_lesson_decisions_no_repromote
BEFORE INSERT ON operational_lesson_decisions
WHEN NEW.decision_kind = 'PROMOTE' AND EXISTS (
    SELECT 1 FROM operational_lesson_decisions
    WHERE lesson_id = NEW.lesson_id AND decision_kind = 'PROMOTE'
)
BEGIN
    SELECT RAISE(ABORT, 'operational lesson is already promoted');
END;

-- Skill lifecycle subjects (SEC4 / roadmap 6.10, Half 1 -- durable storage
-- only). One immutable identity row per content-addressed Skill revision.
-- `catalog_key` is exactly SkillCatalogEntry.catalog_key
-- ("<source_id>:<skill_id>@sha256:<content_sha256>"), so any edit to a
-- Skill's contents yields a *different* catalog_key and therefore a new
-- subject that starts over at VALIDATED/QUARANTINED -- re-approval is
-- structural, not the product of any reconciliation job.
--
-- Deliberately absent: SKILL.md bodies, resource contents, procedure text.
-- References and hashes only (roadmap 6.3). `gate_report` is the findings /
-- verdict summary produced by SkillGateReport.to_dict(), not Skill content.
--
-- These tables live in the existing TaskStore database on purpose: this is
-- not a second authority store (roadmap 7.2), it is the same canonical
-- SQLite file that already holds operational_lessons, whose
-- immutable-base-row + append-only-decisions + composed-state pattern this
-- reuses verbatim.
CREATE TABLE IF NOT EXISTS skill_lifecycle_subjects (
    catalog_key TEXT PRIMARY KEY CHECK (length(trim(catalog_key)) BETWEEN 1 AND 512),
    source_id TEXT NOT NULL CHECK (length(trim(source_id)) BETWEEN 1 AND 128),
    source_kind TEXT NOT NULL CHECK (source_kind IN ('BUNDLED','LOCAL','THIRD_PARTY')),
    source_ref TEXT,
    declared_revision TEXT,
    skill_id TEXT NOT NULL CHECK (length(trim(skill_id)) BETWEEN 1 AND 128),
    skill_name TEXT NOT NULL CHECK (length(trim(skill_name)) BETWEEN 1 AND 256),
    content_sha256 TEXT NOT NULL CHECK (length(content_sha256) = 64),
    initial_state TEXT NOT NULL CHECK (initial_state IN ('VALIDATED','QUARANTINED')),
    gate_disposition TEXT NOT NULL CHECK (
        gate_disposition IN ('CLEAR','REVIEW_REQUIRED','QUARANTINE')
    ),
    gate_report TEXT NOT NULL CHECK (json_valid(gate_report)),
    first_seen_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_skill_lifecycle_subjects_identity
    ON skill_lifecycle_subjects(source_id, skill_id, first_seen_at);

CREATE TRIGGER IF NOT EXISTS trg_skill_lifecycle_subjects_no_update
BEFORE UPDATE ON skill_lifecycle_subjects
BEGIN
    SELECT RAISE(ABORT, 'skill lifecycle subjects are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_skill_lifecycle_subjects_no_delete
BEFORE DELETE ON skill_lifecycle_subjects
BEGIN
    SELECT RAISE(ABORT, 'skill lifecycle subjects are immutable');
END;

-- Append-only Skill lifecycle decisions. One row per transition after the
-- initial gate verdict recorded on the subject row. A Skill's effective
-- lifecycle state is *composed* by replaying these rows through the pure
-- validator in runtime/skills/lifecycle.py; it is never stored in a mutable
-- column, so the transition history can never be lost and no write can land
-- a Skill in APPROVED without a decision row behind it.
--
-- The actor CHECK below duplicates, at the schema level, the requirement the
-- pure module already enforces for the two "-> APPROVED" edges. It is
-- defense in depth against a direct-SQL write, not the primary check.
CREATE TABLE IF NOT EXISTS skill_lifecycle_decisions (
    decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    catalog_key TEXT NOT NULL REFERENCES skill_lifecycle_subjects(catalog_key),
    from_state TEXT NOT NULL CHECK (
        from_state IN (
            'DISCOVERED','VALIDATED','QUARANTINED','APPROVED','ACTIVE',
            'SUPERSEDED','RETIRED'
        )
    ),
    to_state TEXT NOT NULL CHECK (
        to_state IN (
            'DISCOVERED','VALIDATED','QUARANTINED','APPROVED','ACTIVE',
            'SUPERSEDED','RETIRED'
        )
    ),
    decision_ref TEXT NOT NULL CHECK (length(trim(decision_ref)) BETWEEN 1 AND 512),
    decided_by TEXT CHECK (decided_by IS NULL OR length(trim(decided_by)) BETWEEN 1 AND 128),
    decided_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CHECK (from_state <> to_state),
    CHECK (NOT (to_state = 'APPROVED' AND (decided_by IS NULL OR length(trim(decided_by)) = 0)))
);
CREATE INDEX IF NOT EXISTS idx_skill_lifecycle_decisions_subject
    ON skill_lifecycle_decisions(catalog_key, decision_id);

CREATE TRIGGER IF NOT EXISTS trg_skill_lifecycle_decisions_no_update
BEFORE UPDATE ON skill_lifecycle_decisions
BEGIN
    SELECT RAISE(ABORT, 'skill lifecycle decisions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_skill_lifecycle_decisions_no_delete
BEFORE DELETE ON skill_lifecycle_decisions
BEGIN
    SELECT RAISE(ABORT, 'skill lifecycle decisions are immutable');
END;

CREATE TRIGGER IF NOT EXISTS trg_skill_lifecycle_decisions_no_post_terminal
BEFORE INSERT ON skill_lifecycle_decisions
WHEN EXISTS (
    SELECT 1 FROM skill_lifecycle_decisions
    WHERE catalog_key = NEW.catalog_key AND to_state IN ('SUPERSEDED','RETIRED')
)
BEGIN
    SELECT RAISE(ABORT, 'skill lifecycle state is terminal; no further decisions');
END;

-- Operator-visible release check (6.21 `maps flow release-check`). Append-only
-- evidence assembled BEFORE the review verdict for an
-- OPERATOR_VISIBLE_RELEASE_CHECK task: the artifact-identity aggregate (from
-- `evaluate_acquisition_evidence`), the release-path-smoke aggregate (from
-- `evaluate_benchmark_results`), the composite state, and the full summary
-- snapshot. The flow records no verdict; `composite_state = 'BLOCKED'` is
-- advisory input to `maps flow review-record`, not an approval gate (that is a
-- later hardening slice). Re-running the check appends a new row; the latest by
-- id is current.
CREATE TABLE IF NOT EXISTS release_checks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    review_id INTEGER NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
    subject_run_id TEXT,
    artifact_identity_state TEXT NOT NULL CHECK (
        artifact_identity_state IN ('PASS','FAIL','UNKNOWN','NOT_APPLICABLE')
    ),
    artifact_identity_report_ref TEXT,
    release_smoke_state TEXT NOT NULL CHECK (
        release_smoke_state IN ('COMPLETE','FAIL','INCOMPLETE','NOT_APPLICABLE')
    ),
    release_smoke_report_ref TEXT,
    input_evidence_refs TEXT NOT NULL DEFAULT '[]',
    composite_state TEXT NOT NULL CHECK (
        composite_state IN ('READY_FOR_OPERATOR_VERDICT','BLOCKED')
    ),
    summary_snapshot TEXT NOT NULL,
    operator_ack_ref TEXT,
    recorded_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_release_checks_task
    ON release_checks(task_id, review_id, id);

CREATE TRIGGER IF NOT EXISTS trg_release_checks_no_update
BEFORE UPDATE ON release_checks
BEGIN
    SELECT RAISE(ABORT, 'release checks are immutable; re-run to append a new one');
END;

CREATE TRIGGER IF NOT EXISTS trg_release_checks_no_delete
BEFORE DELETE ON release_checks
BEGIN
    SELECT RAISE(ABORT, 'release checks are immutable');
END;
