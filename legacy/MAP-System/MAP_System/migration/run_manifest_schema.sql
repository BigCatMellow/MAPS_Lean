-- TASK-281: bounded pilot schema for immutable run manifests.
--
-- Additive and separate from the core migration/schema.sql on purpose: this
-- is a pilot (see artifacts/experiments/task281-run-manifest-pilot.md), not
-- a production dispatch requirement, so it must not become load-bearing for
-- existing claim/submit/review flows until an independent review authorizes
-- wider adoption. Applied idempotently by scripts/run_manifest.py against
-- the live map.db; never merged into schema.sql by this task.
--
-- One row per dispatched attempt. Binds a task revision (content hash of
-- the task definition at manifest-creation time) to a unique run ID and
-- records the execution context as references + hashes, never copied
-- content, per TASK-277's "store references and hashes rather than copied
-- context" requirement.

-- TASK-283 added readable_scope and forbidden_scope (both additive columns,
-- see scripts/run_manifest.py's connect() for the ALTER TABLE migration
-- applied to databases created before these columns existed).
CREATE TABLE IF NOT EXISTS run_manifests (
    run_id           TEXT PRIMARY KEY,
    task_id          TEXT NOT NULL REFERENCES tasks(task_id),
    task_revision    TEXT NOT NULL,
    worker_id        TEXT NOT NULL REFERENCES agents(agent_id),
    session_id       TEXT,
    role_id          TEXT NOT NULL,
    role_source      TEXT NOT NULL,
    readable_scope   TEXT NOT NULL DEFAULT '[]',
    writable_scope   TEXT NOT NULL DEFAULT '[]',
    forbidden_scope  TEXT NOT NULL DEFAULT '[]',
    runtime_limits   TEXT NOT NULL DEFAULT '{}',
    base_revision    TEXT,
    created_by       TEXT NOT NULL REFERENCES agents(agent_id),
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Skills selected for this run. Normalized rather than JSON-packed into
-- run_manifests so staleness/inventory queries don't need to parse a blob.
CREATE TABLE IF NOT EXISTS run_manifest_skills (
    run_id  TEXT NOT NULL REFERENCES run_manifests(run_id),
    skill   TEXT NOT NULL,
    PRIMARY KEY (run_id, skill)
);

-- Context references supplied to the run: a repo-relative path plus the
-- sha256 of its content at manifest-creation time. No content column
-- exists on this table by design -- it must be structurally impossible for
-- a manifest to accidentally retain a full copy of source context.
CREATE TABLE IF NOT EXISTS run_manifest_context_refs (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id  TEXT NOT NULL REFERENCES run_manifests(run_id),
    path    TEXT NOT NULL,
    sha256  TEXT NOT NULL,
    UNIQUE (run_id, path)
);

CREATE INDEX IF NOT EXISTS idx_run_manifests_task_id ON run_manifests(task_id);
