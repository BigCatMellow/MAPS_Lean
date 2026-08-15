# Review packet: Outcome feedback

- Status: `QUEUED`
- PR: `#19`
- Task record: `work/tasks/outcome-feedback.md`
- CI evidence: Runtime stack tests run `31886288275` passed with the outcome
  implementation and focused tests present.

## Review scope

Inspect the current PR revision, especially:

- `runtime/state/schema.sql`
- `runtime/state/outcomes.py`
- `runtime/state/store.py`
- `runtime/state/observability.py`
- `runtime/cli.py`
- `tests/test_outcomes.py`
- `runtime/README.md`

## Intended behavior

- only `DONE` tasks accept post-completion outcome observations;
- observations are append-only SQLite evidence with no update/delete path;
- recording an outcome does not reopen a task or change task/review/policy
  authority;
- actor identity/class, source provenance, task revision, optional run binding,
  failure class, escaped-defect/rework/operator-intervention metrics, and time
  are explicit;
- later corrections supersede by reference instead of overwriting history;
- run IDs and superseded outcome IDs cannot cross task boundaries;
- diagnostic source/notes use the best-effort secret-safety boundary;
- CLI can record/list outcomes and trace includes them.

## Review questions

1. Is `DONE` the correct first boundary for accepting outcomes?
2. Can any outcome field accidentally become task authority or routing policy?
3. Are append-only triggers and cross-task validation sufficient for historical
   integrity?
4. Is actor provenance explicit enough without forcing fake identities?
5. Are source/notes clearly diagnostic metadata rather than a new evidence
   warehouse?
6. Does supersession preserve old observations without creating ambiguity about
   history?

## Intentionally deferred

- no eval corpus builder yet;
- no automated harness/configuration changes from outcome data;
- no dashboard or scoring model;
- no outcome-triggered task reopening.
