# Portable Deployment operator decisions (roadmap 06)

Roadmap `06-portable-deployment.md` (#128) closed its Mission meeting with
five open questions the roadmap explicitly could not resolve itself, plus an
unpicked pilot target. The operator has now made all five calls, and named
the first pilot target. This note is the record; the roadmap itself is
updated in the same PR to point back here and to rescope `D2`/`D3` onto the
now-resolved architecture.

## Operator decisions (recorded 2026-08-19)

1. **V1 discipline: lightweight file-convention only, not a full SQLite
   task-truth port.** Task/review/roadmap discipline in the target project
   is Markdown files + a status-field convention + git — no database, no
   atomic claim/lease guarantees. Reasoning: the SQLite path buys mechanical
   enforcement but requires porting and running real `runtime/state/` code
   inside a repo MAPS doesn't own; nothing has yet demonstrated that
   contention risk is real for a single-project v1. Upgrade to SQLite only
   if a real pilot actually proves contention the file-convention path can't
   handle.

2. **Distribution model: sibling-clone + lightweight adapter.** MAPS_Lean
   stays a separate clone next to the target project; a small adapter living
   in the target project's own tooling calls out to it as needed. No
   packaged/pip-installable distribution for v1. Reasoning: this is the
   cheapest distribution shape consistent with decision 1 — there's no
   Python runtime code that needs to run inside the target project, so
   there's nothing to package or vendor yet.

3. **Review-evidence enforcement: best-effort discipline, not a hard CI
   gate, for v1.** If the target project happens to run GitHub Actions, the
   `scripts/check_review_evidence.py` pattern may optionally be offered and
   documented, but v1 success does not require it. Reasoning: not every
   target project uses GitHub, or CI at all — making the gate mandatory
   would make the CI system, not the discipline, the actual scope
   constraint on which projects v1 can target.

4. **V1 scope: stack-agnostic, not Python-only.** Reasoning: decision 1
   already means the thing being ported is Markdown files + git
   conventions — no MAPS Python runtime code needs to execute inside the
   target project for v1, so restricting the pilot to Python-stack projects
   would be an arbitrary constraint left over from the SQLite-port framing,
   not a real one.

5. **Target-project MAPS state: committed inside the external repo itself.**
   Task/review/roadmap files live under a clearly-named directory in the
   target project's own tree (e.g. `.maps/`), visible to that project's own
   contributors — not hidden in a separate MAPS-owned location that
   references the target repo by path. Reasoning: an indirection that
   contributors of the target project can't see invites exactly the kind of
   confusion/drift roadmap 06's Definition of DONE is trying to rule out;
   visibility in-tree is the cheaper failure mode to detect and fix.

**First pilot target: Chain Shovel.** A real, currently-active game dev
project (unrelated to MAPS_Lean) with a known, bounded bug — an ES-module-
split + logger issue — already identified. Chosen over a synthetic/throwaway
repo because roadmap 06's Definition of DONE explicitly requires a real,
observable pilot with an inspectable merged PR and review-evidence artifact;
a bounded, already-diagnosed bug gives genuine end-to-end proof without
open-ended risk. Note: actually running the D2/D3 pilot against Chain Shovel
is separate future work — not part of the decision-recording or rescoping
done in this PR, and this session has no access to Chain Shovel's repo.

## What this unblocks

All five decisions together resolve the architecture fork that was blocking
everything past `D0`/`D1`. Roadmap 06's "First wave selected" and Phase 1 are
updated in this same PR to reflect concrete next design phases (`D2a`–`D2c`)
that were previously just "D2 — implement the operator-chosen v1 discipline"
placeholder text. Those phases are still design/planning only, per roadmap
06's own "not doing... building or shipping any runtime code" boundary — this
note and the roadmap update do not authorize implementation.
