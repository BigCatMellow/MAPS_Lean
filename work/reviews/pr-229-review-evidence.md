# PR #229 review evidence — context_builder: correct `memory_trust_gate_note` after #225 capability DENY

reviewer: maps-lean-nava
head_sha: 45fdb0e17ecd27ec5ea152d88e8cf87b2d16e955
independent: true
summary: APPROVE — pure prose fix: the reworded `memory_trust_gate_note` now scopes "passes admit_memory_evidence()" to items that reach the trust gate and names the pre-trust-gate `SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE` DENY explicitly; the only non-string change is a new regression test; no behaviour change (the reason code was already in `_reasons` since #225); luve's STOP-condition analysis (no double-count, capability-DENY'd Skills absent from `memory_like`) is correct; folding into the existing tally is defensible; no checklist status flip; targeted modules + smoke green. Verification-only is right — there is no logic to mutation-test. NB: head_sha rebound by coordinator to the post-rebase commit (branch predated #228/#230; rebase clean).

## Criteria

| # | Criterion | Result |
|---|-----------|--------|
| 1 | Reworded note is now accurate | PASS. New text scopes the `admit_memory_evidence()` claim to "every memory-like item **that reaches the trust gate**" and adds an explicit clause: "One DENY is decided earlier and outside the trust gate: SEC4 capability-manifest slice 2 (#225) drops a matched Skill whose declared capabilities fall outside the task_policy envelope, reason SKILL_CAPABILITY_OUTSIDE_TASK_ENVELOPE — a capabilities_within_envelope() intersection, not a MemoryTrustClass decision. It is recorded in the same tally … but is distinguishable by its reason code." Matches the merged `_select_skills` path (capability DENY at ~L399-406 → `continue` before `admit_memory_evidence`, records into the shared `tally`). The over-claim #228 §2 identified is gone. |
| 2 | NO behaviour change | PASS. `git diff HEAD~1..HEAD -- runtime/context_builder.py` filtered to lines outside the `"memory_trust_gate_note": ( … )` string literal → empty. The only edits are the string body + a new test method. `capabilities_within_envelope`, the `_select_skills` hook, `_AdmissionTally`, the coverage counters untouched; the reason was already populated by #225. |
| 3 | luve's STOP-condition check right — tally reuse is not a correctness problem | PASS. No double-count: each matched Skill takes exactly one `continue` (capability DENY, or trust-gate DENY, or `selected.append`) — mutually exclusive. No classification-flag effect: a capability-DENY'd Skill hits `continue` before `selected.append(item)`, so it is not in the returned list, not in `memory_like = [*guidance, *withheld_guidance, *skills]`, and cannot affect `memory_trust_classification_present`. It is correctly counted in `memory_trust_gate_denied` / `_reasons`. Verified against merged code. |
| 4 | Folding into the existing tally rather than a new counter is defensible | PASS. #228's note recommended a separate `skill_capability_gate_*` counter as "cleaner" but also presented the reword as valid. The reason code already makes the two paths distinguishable in `memory_trust_gate_reasons`; the note now documents the dual-path semantics explicitly. The smaller change for the same information — a reasonable judgment call, fully resolves the accuracy defect. |
| 5 | NO checklist status flip | PASS. `git show HEAD --stat` = 2 files: `runtime/context_builder.py`, `tests/test_skill_capability_manifest.py`. `CAPABILITY_CHECKLIST.md` not touched. |
| 6 | test_context_builder + test_flow_start + test_skill_capability_manifest green + smoke 0 | PASS. `test_skill_capability_manifest` + `test_flow_start` 44/44; `test_context_builder` 26/26 (incl. the new `test_coverage_note_acknowledges_the_pre_trust_gate_capability_deny` asserting the note lacks the old over-claim, contains the reason code + `capabilities_within_envelope` + "outside the trust gate", and the structured counts still work). `runtime.smoke` → `"ok": true`, exit 0. |
| — | Verification-only (no min-5) is right | CONFIRMED. String literal + a string-content assertion; no branching logic introduced. `capabilities_within_envelope` and the `_select_skills` hook were mutation-tested 8/8 in the #225 review and are unchanged here. |

## Non-blocking

- The new test is a string-content assertion (`assertNotIn` / `assertIn` on the note) — brittle to future rewordings, but appropriate as a regression guard for a doc-accuracy fix and consistent with the (otherwise untested) coverage-note strings.

## Verdict

APPROVE.
