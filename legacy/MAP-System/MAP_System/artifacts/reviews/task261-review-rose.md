# Review: TASK-261 Prototype query-global evidence selection and local capability verification

task_id: TASK-261
reviewer: claude-lab-rose
task_owner: codex-lab-kiri

## Verdict

APPROVED

**Disposition update (2026-07-21):** operator (bigboss) confirmed the
2026-07-19 Pi run was an exploratory capability probe and sanctioned it
retroactively; recorded durably via `DECISION_RECORDED` in `events.jsonl`
(2026-07-21T18:05:00-04:00, cites this review) and a rewrite of
`shared/current-state.md`'s Pi entry from "paused" to "exploratory-only."
The authority scope limit is unchanged and still binding: Pi still cannot
own tasks, reviews, handoffs, releases, routing, or capacity plans. This
run cleared that bar on its own merits — my verification below already
established Pi received zero task/routing/authority and the report itself
correctly rejected Pi as unviable — so this was exactly the sanctioned kind
of use. Unblocking and approving on that basis.

The finding that survives independent of the Pi question: this is the
second instance (with TASK-250) of a real decision/authorization existing
only in an ephemeral channel until a reviewer had to go looking for a
durable record that wasn't there. See the "Update (claude-lab-niko...)" note
below — worth a standing habit (e.g. always write a `DECISION_RECORDED`
event at the moment authorization is given, not after a reviewer asks).

---

*(Original review body below, preserved as written before the operator's
ruling.)*

The deterministic query-global evidence selector is well-built and well-verified.
But the task also ran a live Pi (`qwen2.5-coder:7b-16k`) helper session, and
`MAP_System/shared/current-state.md` carries a standing, explicit instruction
that is still current as of its last verification (2026-07-18, one day before
this task ran): *"Pi is paused as an operational helper... Do not retry
automatically; a new trial requires a separate operator authorization and
fresh visible instance."* I could not find evidence of a fresh operator
authorization for this specific run in `events/events.jsonl` or recent hcom
history. This is an operator-authority question, not something I can resolve
by reading code, so I'm not approving or rejecting — I'm routing it to the
operator per the review guide's BLOCKED definition ("review cannot complete
because required context... is missing").

## Acceptance Criteria

| Criterion | Result | Evidence |
|---|---|---|
| TASK-259 retriever and TASK-260 truth/results remain byte-for-byte unchanged; new selector is a separate disposable layer; TASK-260 is labeled development data. | PASS | `sha256sum` of `task_memory_fts.py` (`edd0b53a...`) and `task_memory_fts_holdout.py` (`65219824...`) match the values TASK-259/260 froze — unchanged. Report explicitly: "This is known-data development, not fresh evidence." |
| Deterministic query-global selector allocates ≤3 resolved sources across candidates, scores clause coverage/proof roles/non-redundancy/task linkage/temporal attribution without forcing role diversity. | PASS | `test_three_role_single_task_uses_three_source_budget`, `test_complementary_same_role_is_not_forced_out`, `test_compound_query_rewards_uncovered_task_and_clause` all pass. §"Deterministic Query-Global Selector" in the report matches the implementation's described scoring. |
| Focused tests cover 3-role single-task, compound cross-task, complementary same-role, unresolved/shared-source penalties, deterministic ordering, fixed-selector comparison. | PASS | All six named scenarios map 1:1 to the 7 passing tests (`test_current_shared_and_unresolved_are_penalized`, `test_deterministic_path_tie_break`, `test_fixed_selector_comparison_has_global_limit`, etc.). |
| Visible bounded local/Pi verifier receives one frozen TASK-260 packet at a time, no repo search/writes; report records decisions, false positives, context, latency, scope, viability. | PASS (resolved 2026-07-21) | The verifier ran as claimed (11 packets, one at a time, no repo access observed, report §"Visible Pi Capability-Verifier Run" is candid about its failures: 66.7% positive recall, 4 contract violations, 2 forced context compactions). Content was always satisfied; the open authorization question is now resolved — see updated Verdict above. |
| Report compares exact-source visibility against TASK-260's 15/20, documents tradeoffs/limitations, freezes a candidate for a later holdout, makes no integration/embedding claim. | PASS | §"Known-Data Comparison" table directly compares 15/20 vs 16/20. §"Candidate Freeze for a Fresh Holdout" freezes the selector (not Pi) with hash `1c33ed6c...`. No integration claim; explicit "no Pi verifier in the candidate path." |

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Modify Pi authority | NOT BROKEN (confirmed 2026-07-21) — the helper note and report are explicit that Pi received no task/routing/review/release/canonical-state authority, and the report's own conclusion excludes Pi from the frozen candidate. Operator confirmed retroactively that this was sanctioned exploratory use, not an authority grant; `shared/current-state.md`'s Pi entry now reads "exploratory-only" rather than "paused," and the authority ceiling (no task/review/routing/release/capacity-plan authority) remains explicitly unchanged. |
| Download models | NOT BROKEN — report states "already-installed" model, no download activity claimed or evident. |
| Add embeddings | NOT BROKEN — explicit no-embeddings statement in §Recommendation. |
| Integrate into startup, routing, UI, canonical authority, external services | NOT BROKEN — selector is a standalone script; database is disposable. |

## Files Reviewed

- `MAP_System/artifacts/experiments/task-memory-evidence-verifier-development-2026-07-19.md` (full)
- `MAP_System/inbox/helpers/helper-index-local-verifier-2026-07-19.md`
- `MAP_System/scripts/task_memory_packet_selector.py`, `MAP_System/tests/test_task_memory_packet_selector.py`
- `MAP_System/shared/current-state.md` (Pi pause language)
- `MAP_System/events/events.jsonl` (searched for authorization evidence around 2026-07-19)

## Verification

- `python -m py_compile MAP_System/scripts/task_memory_packet_selector.py MAP_System/tests/test_task_memory_packet_selector.py` — passes.
- `python -m unittest MAP_System.tests.test_task_memory_packet_selector -v` — 7/7 passed.
- `python -m unittest MAP_System.tests.test_task_memory_packet_selector MAP_System.tests.test_task_memory_fts MAP_System.tests.test_task_memory_fts_holdout` — 21/21 passed, exactly matching the report's "21 focused and adjacent tests passed" claim.
- `sha256sum` confirms the selector matches its frozen hash and the carried-forward retriever/harness are byte-for-byte unchanged.
- Searched `MAP_System/events/events.jsonl` and recent hcom event history for Pi-trial authorization near TASK-261's execution window (2026-07-19 ~18:30–19:00 EDT / 22:36–22:39 UTC per the report) — found no authorization record. This is not proof none exists (hcom history predating this session is only partially searchable from here), which is exactly why this is BLOCKED rather than a finding I'm confident enough to make a REQUIRED/reject call on unilaterally.

## Notes

The engineering substance here is genuinely good and, on its own, would be an
easy APPROVED: the selector is deterministic, disposable, well-tested, and
the report is honest that Pi failed as a verifier (66.7% positive recall,
contract violations, context blowup) and correctly excludes it from the
frozen candidate. My hold is narrowly about process compliance, not quality.

Routing to @bigboss via hcom (intent=request): please confirm whether the
`helper-index-local-verifier-bero` Pi session (qwen2.5-coder:7b-16k,
2026-07-19) had a fresh operator authorization per the standing pause note in
`shared/current-state.md`. If yes, this task should be approved as-is (I'll
need only a pointer to that authorization to close this out). If no, this
still doesn't need rework — the finding is about the process gap for future
tasks, not the artifact's technical content — but it should be logged
somewhere durable (e.g. `shared/decisions.md` or an update to the Pi pause
note) so the next task author doesn't repeat it silently.

**Update (claude-lab-niko, independent confirmation):** niko re-ran the same
search across `events.jsonl` for 2026-07-18..20 and found nothing
authorization-shaped for Pi/qwen in that window either. Important framing
niko added: this may not mean no authorization was given — it may have been
given verbally/in chat and simply never written down as a durable record,
the way `shared/decisions.md` or an explicit PROGRESS event would. Contrast:
when claude-lab-lure needed to clear TASK-235's `REQUIRE_CORE_DESTRUCTIVE_APPROVAL`
gate on 2026-07-18, it wrote an explicit PROGRESS event naming the operator,
evidence, and date — that pattern is what's missing here. Combined with
TASK-250 (lure's APPROVED verdict reached the same way — a real decision
that existed but was never durably recorded, so the runner kept re-routing
it), this is now two instances of the same underlying failure mode: verdicts
and authorizations happening in ephemeral channels instead of durable state.
Worth a `shared/decisions.md` entry or a note in `notes/` about durably
recording operator authorizations at the point they're given, independent of
how TASK-261 itself resolves.
