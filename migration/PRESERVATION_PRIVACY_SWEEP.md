# Preservation Privacy / Secret Sweep

Status: `PASS — CURRENT PRESERVATION SET`
Date: 2026-08-14
Scope: current repository contents plus the two curated preservation snapshots:

```text
migration/legacy-runtime-source/
migration/legacy-knowledge-source/
```

Purpose: check that the material retained before eventual `legacy/` removal did
not accidentally preserve credentials, private machine state, live databases,
transcripts, inbox/message stores, logs, screenshots, or other obvious runtime
artifacts that should not survive as migration reference.

## Important limitation

This is a **current-tree preservation sweep**, not a forensic secret scan of all
historical Git objects, reflogs, deleted blobs, forks, local clones, hcom state,
or external services.

A clean result means the current tracked preservation set did not expose the
checked secret patterns/artifact classes. It does not prove that a secret could
never have existed in repository history.

If legacy history is later rewritten, published more broadly, or evidence
suggests a credential was ever committed, use a dedicated Git-history secret
scanner and rotate the affected credential rather than relying on this report.

## Text / credential pattern sweep

Repository code search returned no current indexed matches for the following
high-signal patterns/classes:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
sk-
Bearer 
api_key
token=
password
ghp_
github_pat_
AKIA
AIza
xoxb-
BEGIN PRIVATE KEY
hf_
```

Machine-private absolute path checks also returned no indexed matches for:

```text
/home/
C:\Users\
```

These are pattern checks, not claims that every occurrence of words such as
`token`, `key`, or `password` would necessarily be a secret.

## Preservation snapshot structure sweep

The recursive trees for both curated snapshots were checked for artifact/file
classes that commonly contain live or sensitive state.

No preservation-snapshot paths were found for:

```text
.env
*.pem
*.key
id_rsa
*.db
*.db-wal
*.db-shm
*.sqlite*
*.jsonl
*.log
settings.json
status.json
state.json
*.png
*.jpg
```

No copied live `map.db`, giant legacy `events.jsonl`, hcom transcript tree,
inbox store, or message-store artifact was identified in either snapshot.

Session-related material in `legacy-knowledge-source` is source/design/test
material for session replay and continuity behavior, not copied live session
transcripts/state.

## What was intentionally preserved

The snapshots retain code, tests, documentation, migration references, and
selected measured evidence needed to understand/prove behavior. They
intentionally exclude the large historical task/event corpus, live SQLite
state, hcom message/session history, UI screenshots, and fixed-roster runtime
state.

## Result

```text
Obvious current credential pattern found: NO
Private-key/config artifact found: NO
Live SQLite/runtime DB artifact found: NO
SQLite WAL/SHM sidecar found: NO
Transcript/inbox/message-store artifact found: NO
Log/JSONL historical dump found: NO
Screenshot/image artifact found: NO
Machine-private absolute home path found: NO

CURRENT PRESERVATION PRIVACY SWEEP: PASS
```

## Remaining deletion gates

This PASS closes the privacy/secret gate for the **current curated preservation
set**. It does not authorize `legacy/` deletion by itself.

Still required:

1. deferred independent review of the runtime PR stack;
2. merge the reviewed runtime to `main`;
3. final active-reference/dependency sweep after merge; and
4. explicit operator approval for the legacy-removal change.
