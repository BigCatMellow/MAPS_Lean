# PR #253 review evidence — operator decision batch 2026-09-02

Independent verification-only review by maps-lean-nava (vame authored).
Docs-only, 1 file (`work/notes/OPERATOR_DECISION_BATCH_2026-09-02.md`); no
runtime, no `CAPABILITY_CHECKLIST.md` change.

## Item-by-item verification (faithful / recommendation sound / classification)

| # | Source | Faithful? | Recommendation sound? | Blocking classification |
|---|--------|-----------|----------------------|-------------------------|
| **1** release-check 3b approval gate | `2026-09-02-release-check-3b-approval-gate-scoping.md` §1 (#249, reviewed by nava) | Yes — the drafted callout is copied verbatim: hard-block `record_review` APPROVED for `OPERATOR_VISIBLE_RELEASE_CHECK`, `operator_ack_ref` as the recorded override (no `--force`), no-row → `RELEASE_CHECK_REQUIRED`. Cites #234 §6 "authority-model change" (rule 11). | YES — sound. Enforcing a recorded BLOCKED with an explicit ack escape hatch closes the name↔enforcement gap; ~8-line check, no schema, no CLI. | No (correct) — 3a advisory shipped in #244; 3a stands if NO. |
| **2** merge-authority / merge-prep rule | `2026-09-02-roadmap-trajectory-check-17.md` §1.5 (#252, reviewed by nava) | Yes — (a) named fallback merge-prep order (longest peer rebases + binds evidence, does not merge), (b) `gh pr merge` stays operator-only, (c) claim-rebase-in-channel. "Process rule only, no daemon (rule 13)." 3-incident pattern. | adopt (a)(b)(c) — sound, rule-20 territory. Operator call because (a)/(b) touch the authority model. | No (correct) — prevents recurrence, no code unblock. |
| **3** SEC4 H3 2c empty-registry semantics | `2026-09-01-sec4-half3-slice2-scoping.md` §2c (#251, `6b8e703`) | Yes — the three options match §2c exactly: keep fail-open (= today), hard cutover (breaks every `maps skill`/CI call until a genesis row), `--enforce-operator-identity` flag default-off. | keep fail-open + flag as a later slice; never the hard cutover (a foot-gun with no migration path). Sound. | No (correct) — slice 1 + #251 scoping both stand under fail-open. |
| **4** 6.9/S6 path to DONE | `2026-09-02-6.9-s6-promotion-gate-step.md` §5 (#250, authored by nava) | Yes — (a) reviewed `_select_skills` quality PR closing the three 0.00 gaps, EXP-B as acceptance; (b) explicit §17.3 operator sign-off. Matches #250 §5 near-verbatim. | pursue (a), (b) as fallback — sound. | No (correct) — (b) surfaced so a stalled (a) has an exit. |
| **5** Ask #1 enforced pass — target + timing | `OPERATOR_ASK_2026-08-31-session13.md` Ask #1 (#243, as corrected by nava's #243 review) + `2026-09-02-roadmap-trajectory-check-17.md` §2.3 (both reviewed by nava) | Yes — carries the corrected `.maps/` precondition exactly: target `~/Projects/MAPS_Lean`, `.maps/` absent → coordinator establishes the control-plane DB + `--harness-project-id` per `docs/CONTROL_PLANE_SETUP.md` first, then operator "go"; expected `LEASE_EXPIRED`, remediate per §5; no impl/review agent runs the pass autonomously. | confirm target; authorise the coordinator to stand up the control plane; operator gives the final "go" — sound. | Partial (correct) — the control-plane setup is dispatchable coordinator work now with no operator input; only the pass itself needs the operator's go. Unblocks 7 rows. Highest leverage in the batch. |
| **6** infra carry-overs | `OPERATOR_ASK_2026-08-31-session13.md` Infra #2/#3 + session-15 worktree audit + this session's merge-prep friction | Yes — (1) ~70 classifier-blocked `git worktree remove`/`git branch -D` (grown from 44; includes pid-3874's 4 locks), (2) 5 stale remote branches (audit rows 24/33/39/47/48), (3) a scoped `git push --force-with-lease` allow rule for throwaway rebase branches — (3) is new relative to #243 but session-sourced from observed force-push friction. | add the 3 scoped Bash rules (low-risk, repo-local, audited) OR one operator cleanup pass — sound. | No (correct) — friction that compounds on every merge/worktree lifecycle. |

## Non-blocking notes

- Item 4 states "gela is scoping (a) now" — a dispatch-state claim not verified;
  tangential to the operator decision itself. (Since landed as #254.)
- Item 4's "(b) fallback only if (a) needs semantic retrieval, a separate
  EVIDENCE-GATED roadmap item" — an accurate elaboration (semantic retrieval =
  §6.33, EVIDENCE-GATED), not a misstatement.
- The Resume prompt is clean: present all 6 together, accept 1–4 as a block,
  per-item for 5–6, record answers under a dated "OPERATOR ANSWERED" heading
  (matching the #243 doc), then dispatch. "Do not resolve any item yourself" —
  correct.

## Verdict: APPROVE

reviewer: maps-lean-nava
head_sha: e449422c60beec72fdf56555c71c409c5515a26f
independent: true
summary: APPROVE — all 6 items in the operator decision batch are faithfully stated against their merged source notes (verified line-by-line, including three nava reviewed — #249/#250/#252 — and #251 §2c / #243 read directly), each recommended answer is sound, and each blocking-vs-dispatchable classification is correct (notably item 5 "Partial" — the control-plane setup is dispatchable coordinator work now, only the enforced pass needs the operator's go); docs-only, 1 file, no runtime, no status flip; the batch structure matches the #243 precedent.
