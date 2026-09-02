# PR #252 review evidence — roadmap trajectory check #17

Independent verification review by maps-lean-nava (vame authored). Docs-only:
`work/notes/2026-09-02-roadmap-trajectory-check-17.md` +
`work/coordination/FRICTION_LOG.md`. Per `ROADMAP_TRAJECTORY_CHECK.md` +
`TENTH_SEAT_REVIEW.md` §7. One REQUEST_CHANGES round (an anchor-accounting gap),
fixed, then APPROVE. `head_sha` below is the rebased branch tip.

## Round 1 finding (fixed)

PR #251 (`6b8e703`) merged after the #252 branch was cut, was inside the
`6ea81b2..HEAD` window, but the note treated it as "in-flight for #18" — and
#18's mechanical anchor derivation (`<#252-squash>..HEAD`) would skip it. This
is the check-#11 anchor-accounting failure the playbook names.

## Delta verification — the fix

| Item | Result |
|---|---|
| #251 + #245 folded into #17's arc | DONE. #252 rebased; arc re-derived = 7 PRs (#242/#241/#243/#244/#246/#251/#245); the note acknowledges "just over the 3–6 window; the window matters more than the count". |
| #245 real re-verify | Confirmed independently: `/usr/bin/grep -rln "authorized_operators" runtime/` → `cli.py`, `authorized_operator_storage.py`, `schema.sql` (was 0 for #13–#16); `python3 -m unittest tests.test_authorized_operator_storage` → 18/18 OK; the `is_authorized_operator` gate on `maps skill approve` + `maps init` genesis present. Carried-check-1 row updated "In-flight → DONE — #245" (batch-item disposition, not a checklist status flip). |
| #251 re-verify | Design note only, no runtime change; recommends increment 2a, defers others, flags the fail-closed cutover as an operator decision. No status flip. |
| standing "grep → NOTHING" check | Correctly retired (carried check 4) — replaced with a slice-1-AND-slice-2 verification instruction for #18. |
| §6 anchor fix (the round-1 requirement) | DONE, stronger than a one-line handoff. §6 opens with a "READ THIS FIRST" block: **#18 anchors at `6ea81b2`, NOT #252's squash**, plus a 9-row table (#241–#251) each with a "#18 verifies" column and a "`git log 6ea81b2..HEAD`, check every line, re-confirm against merged code (rule 14), do not trust '#17 mentioned it' as reviewed" instruction. A deliberate over-anchor — a documented deviation from the PR #212 standing rule (anchor = previous trajectory squash), justified because #249 and #250 merged to `main` while #17 was in review and land before #252's squash. The "READ THIS FIRST" framing prevents a future reader from mis-applying the standard rule. |
| CONTINUE verdict | Unchanged, defensible — #16's REPRIORITIZE executed (batch answered, §3a slices landed); the #16 STOP-condition ("§3b batch STILL unanswered AND §3a exhausted") is not met. |
| Scoreboard 16/13/6, 10th consecutive | Re-confirmed. The trajectory PR's own diff = 2 files; zero `CAPABILITY_CHECKLIST.md` change by #252. |
| Tenth-Seat Trigger 2 "armed / did not fire" | Unchanged and sound — substantive findings present (operator batch answered = "changed picture"; blocker changed shape; merge-authority 3-incident pattern), pass not trending clean, no @soda pre-flag needed, no sub-agent dispatched, no minority-report file. |
| Carried checks 1–6 | All confirmed: operator batch answered per-item; no agent ran an enforced canonical-run pass (`.maps/` absent makes it impossible; grep clean); pid 3874 dead; friction entries 5/6 consumed with clean follow-up appends. |
| Merge-authority rule-20 recommendation (§1.5) | Unchanged — a real 3-incident pattern, correctly framed as an operator decision to adopt (not self-adopted). |
| smoke | `python3 -m runtime.smoke` → exit 0. |

## Non-blocking

- §6 has a duplicated "`python3 -m runtime.smoke` exit 0" line.

## Verdict: APPROVE

reviewer: maps-lean-nava
head_sha: 8bcc6c13f16e666a89bbcb780fe1c4ef1f4f8f31
independent: true
summary: APPROVE after a REQUEST_CHANGES round — trajectory check #17 (action CONTINUE, scoreboard 16/13/6 10th consecutive, Tenth-Seat Trigger 2 armed but did not fire, merge-authority rule-20 recommendation correctly framed as an operator decision); the round-1 gap (PR #251 merged inside the window but treated as in-flight, an anchor-accounting failure) is fixed with #245+#251 folded into the arc with real re-verification and a §6 "READ THIS FIRST" block explicitly anchoring check #18 at 6ea81b2 with a per-PR verify table for #241–#251; all carried checks confirmed, no checklist status flip by this PR.
