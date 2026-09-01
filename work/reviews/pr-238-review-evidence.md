# PR #238 review evidence — SEC4 capability granularity design note (design only)

reviewer: maps-lean-nava
head_sha: 1247f2c441304995f5b0faa58a76d26943d15f45
independent: true
summary: APPROVE — verification-only review of a design-only note; all six of luve's claims verified independently against merged code; §2(A) is a strict tightening of a gate-reconciliation rule (#223's "technical security mapping = reviewer scrutiny, not operator sign-off" category) affecting zero Skills in the repo, and its one forward-looking escalation point is explicitly flagged in §5, not glossed; §2(B) is vocabulary+parsing only with zero enforcement and no new permission (a path-scoped write claim is strictly narrower than the baseline-permitted bare token). No operator-only decision is hidden as reviewer judgment.

## Claim-by-claim verification (against merged code, re-checked at review HEAD)

| luve's claim | Verified? |
|---|---|
| 1. `network-read` / `network-general` are already two distinct tokens | TRUE. `work/roadmaps/agent-harness-capabilities/04-agentic-security.md` §5.1 lists both. `runtime/skills/format.py::_CAPABILITY_TOKENS` contains both. No missing token. |
| 2. Real gap is at the gate-reconciliation alias set | TRUE. `runtime/skills/gate.py`: `_DETECTOR_CAPABILITY["SCRIPT_NETWORK_ACCESS"] = "network-general"`; `_SATISFYING_TOKENS["network-general"] = frozenset({"network-general", "network-read"})`. `_declared_covers` returns True if `declared & _SATISFYING_TOKENS.get(capability, {capability})` is non-empty — so a Skill declaring only `network-read` clears a detected `SCRIPT_NETWORK_ACCESS`. The detector regex matches mutating verbs (`requests.post`, `requests.delete`) and a bare `https://` identically to read verbs — it genuinely cannot distinguish read from write. |
| 3. Fix A = drop `network-read` from that alias set, `gate.py` only, a strict narrowing | TRUE. Removing an entry from `_SATISFYING_TOKENS["network-general"]` can only shrink the set of declared-token combinations `_declared_covers` accepts for a network detection. `capability_policy.py` untouched (`network-read` stays in `_BASELINE`, `_required_flags` still returns `()` for it). Strict narrowing at the gate layer, policy layer unchanged. |
| 4. Fix B = additive `filesystem-write:<path>` token, vocab+parsing only, path enforcement DEFERRED | TRUE and the note is honest. §2(B) and §4 explicitly defer matching `filesystem-write:<path>` against `task["output_paths"]` to "a distinct, reviewable slice." `capabilities_within_envelope` today reads only `task.get("policy")`; `_required_flags` for the new prefix returns `()` — identical to bare `filesystem-write`. No enforcement ships. |
| 5. Zero live manifests; `register_skill_catalog` idempotent by `catalog_key` so gate-tightening never re-assesses recorded subjects | TRUE. `.claude/skills/` = one Skill (`pilot`), no `capabilities` sidecar; `/usr/bin/grep -rln "network-read\|network-general\|filesystem-write" .claude/` → nothing. `register_skill_catalog`: `if store.get_skill_lifecycle_subject(entry.catalog_key) is not None: continue` then `assess_skill(entry.descriptor)` — `_SATISFYING_TOKENS` runs only for a `catalog_key` with no subject row yet. An already-recorded VALIDATED/APPROVED/ACTIVE Skill is never re-assessed by a later gate-logic change. |
| 6. OPERATOR DECISION: NONE required | CONCUR — see judgment below. |

## Criterion 6 — is §2(A) genuinely reviewer judgment, or a hidden operator call? (the dispatch's central question)

It is genuinely reviewer judgment, and the note does not hide anything.

- §2(B) is not an authority question at all. Parsing a narrower form (`filesystem-write:output/`) of a token already baseline-permitted, with zero enforcement wired, grants no new permission.
- §2(A) is a strict tightening of a technical security-mapping rule. It makes the Skill gate stricter (a `network-read`-only declaration can no longer dodge a real detected network access), never looser. Rule 9's escalation trigger is an unknown that could raise risk / reduce security / expand authority — a tightening does the opposite. PR #223's own independent review established that the `capability_policy.py` capability→`task_policy` mapping is "reviewer scrutiny, not operator sign-off"; the `_SATISFYING_TOKENS` reconciliation rule is the same category one layer over. It changes behavior for zero Skills in this repo and cannot retroactively demote a recorded subject.
- The note flags — without resolving or hiding — the one forward-looking scenario a future reviewer might escalate: §5 says removing `network-read` from the alias set "will make some future category of third-party Skill harder to pass gate review without also carrying `external_side_effect`," and that whether that warrants operator awareness "is a reviewer's call to escalate at implementation time, not a block on writing or approving this design note." Correct treatment of a "someone may want to raise this later" point. No `THIRD_PARTY` Skills today; the third-party trust-root question is already separately batched for the operator (SEC4 Half 3).

No rule-9 / rule-11 violation: the note neither guesses across an authority boundary nor treats a capability as permission.

## Other checks

- No schema involvement anywhere — the whole chain is a sidecar text file, a `tuple[str,...]` descriptor field, and a pure dict-based check.
- `secret-use:<name>` via `_SECRET_USE_PREFIX` → `security_sensitive` precedent verified in `capability_policy.py`; the proposed `filesystem-write:` prefix branch mirrors it exactly.
- STOP conditions (§7) — none triggered. The §6 Resume prompt correctly tells the implementer to re-run the "zero manifests" check at their HEAD before implementing.
- Diff = 1 file (`work/notes/2026-09-01-sec4-capability-granularity-design.md`); no runtime/tests/checklist change.

## Verdict

APPROVE.
