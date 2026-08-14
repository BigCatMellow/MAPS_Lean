# Review Record: TASK-298

## Header

```
task_id:      TASK-298
reviewer:     claude-lab-mimi
review_date:  2026-07-30
task_owner:   codex-live
```

Reviewer (claude-lab-mimi) ≠ task owner (codex-live). Independence check passes.

Review basis: `MAP_System/artifacts/operations/cross-pc-convergence-2026-07-28.md`
(the 2026-07-28 evidence doc, written by the operation itself) plus
independent live re-verification performed today,
`2026-07-30`, by `rotation-replacement-kite-veni` running read-only checks
directly on Smalls/RUKI at my request — not a re-statement of the original
evidence, a fresh check against current reality. Given evidence can go stale
between submission and review (this session's own `INS-0058`), the two-day
gap made live re-verification necessary rather than optional.

---

## Verdict

```
APPROVED
```

Both required lenses (functional and security-framed) pass below.

---

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | RUKI divergent tracked/untracked/Git/MAP-database state archived with a manifest before replacement | PASS | Evidence doc lists 4 checksummed artifacts (`repository-all-refs.bundle`, `tracked-working-tree.patch`, `untracked-files.tar.gz`, `map-databases.tar.gz`) verified via `sha256sum -c` before activation. Not independently re-hashed today (the artifacts are outside the live tree, lower urgency than the live-system checks below), but their existence and the activation log's internal consistency are not in question. |
| 2 | KUDU transferred to staging; documented manifest proves program-file equivalence before activation | PASS | 2,146→2,148 file reconciliation, checksum dry-run showed no itemized differences (both pre- and post-install). |
| 3 | All RUKI agents quiescent before atomic swap; old repo preserved as timestamped backup; rollback recorded | PASS (backup independently reconfirmed live) | Rollback procedure is explicit and step-by-step. **Independently reconfirmed today**: veni verified `/home/home/Projects/MultiAgentProject.pre-kudu-20260728T202400Z` still exists, is a git repo at the expected pre-convergence HEAD, its 5 "modified" files all have mtimes at or before the 2026-07-28T20:24:00Z backup timestamp, and no process holds it open — i.e. it is genuinely untouched, not just claimed to be. |
| 4 | Installer regenerates RUKI launchers; focused Command Center/MAP health checks pass from the activated tree | PASS | Evidence doc's Verification section shows all 9 named checks (Git/Python/hcom/WezTerm/Codex/Claude/Gemini/Ollama/MAP venv) passing at convergence time. Not independently re-run today (would require live agent restarts on Smalls, out of proportion for a 2-day-old already-running system with no reported incidents since). |
| 5 | SSH uses dedicated ED25519 key, disables password/interactive auth, denies root login, restricted to home user from LAN | PASS — **independently reconfirmed live**, not trusted from the doc | Veni read the actual live config today: `/etc/ssh/sshd_config.d/90-map-peer.conf` shows `PermitRootLogin no`, `PasswordAuthentication no`, `KbdInteractiveAuthentication no`, `PubkeyAuthentication yes`, `AllowUsers home@192.168.1.*` — exact match to the claimed values, sourced from the actual override file (correctly distinguishing it from the base `sshd_config`'s commented-out defaults, which would have been a false-pass trap for a less careful check). |
| 6 | A separate functional review and security-framed review verify the convergence evidence before the backup is eligible for removal | PASS (this record) | See "Functional Assessment" and "Security Assessment" below — both lenses covered explicitly, per the same pattern used for TASK-306's equivalent criterion. |

---

## Functional Assessment

- Commit identity: veni confirmed live `/home/home/Projects/MultiAgentProject`
  HEAD is still `c70282616a7cb7640a5b3b207fc83e91ff9987d3`, exactly matching
  the activated commit. The ~30+ uncommitted working-tree changes veni
  observed are durable MAP state files (`emergence/`, `artifacts/`,
  `events.jsonl`, `agents/status.json`) consistent with two days of normal
  agent activity, not evidence of an unreviewed code change slipping in
  under the convergence's cover.
- Services: `map-rns-watcher.service` and `hcom-relay.service` both
  confirmed live-ACTIVE today (`systemctl --user is-active`, correctly using
  `--user` scope — veni caught that a scope-less check would have falsely
  reported both inactive, since they're user-scope units).
- The live `limit_watcher.py` process (pid 1117, running since Jul 29) was
  confirmed running from the **active** tree path, not the preserved
  backup — direct evidence that RUKI's real, current operation depends on
  the converged tree, not the old one, which is exactly what "convergence"
  is supposed to mean and is the kind of claim worth checking rather than
  assuming.

## Security Assessment

- SSH hardening matches exactly, verified against the live config file
  actually in effect (the override, not the commented-out base defaults) —
  see criterion 5 above. No root login, no password/interactive auth, no
  open `AllowUsers` scope.
- The evidence doc discloses a credential-exposure incident during setup (a
  remote setup agent exposed the account's sudo password in an
  hcom-visible command) and states the operator was notified and password
  rotation is still required. This is **already a known, tracked, open item**
  from before this review (referenced independently in this session's
  earlier orchestration handoff) — not a new finding, and not something
  this review is positioned to force, since the operator has separately
  indicated it's a "when convenient" item, not urgent. Recording it here
  again only for completeness of this specific task's security record.
- No new credential or secret exposure was found in anything reviewed for
  this task specifically.

---

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Deleting either preserved repository/backup path | NOT BROKEN — both explicitly preserved by rename, live-reconfirmed intact today. |
| MAP authority topology change (making Biggie writable, adding a second writer) | NOT BROKEN — this task converges the *program tree*, not database authority; Smalls remains sole writable `map.db`, untouched by this task. |
| Weakening SSH auth | NOT BROKEN — live-verified hardened, not weakened. |

---

## Files Reviewed

- `MAP_System/artifacts/operations/cross-pc-convergence-2026-07-28.md`
- Live (via `rotation-replacement-kite-veni`, read-only, 2026-07-30): backup
  path integrity/mtimes, `sshd_config.d/90-map-peer.conf`, active-tree HEAD,
  `map-rns-watcher.service`/`hcom-relay.service` status.

---

## Scope Check

| Changed file | In scope? |
|---|---|
| `MAP_System/artifacts/operations/cross-pc-convergence-2026-07-28.md` | YES — the task's sole registered output path, and the only file this task's record touches. |

---

## Risk Identification

| Risk | Severity | Recommended action |
|---|---|---|
| Home-account password exposure during setup, rotation still outstanding | MEDIUM | Already tracked outside this task (operator previously deferred it); no new action from this review. Not this task's acceptance criteria to fix. |
| Two independently-writable local SQLite copies still exist in principle (KUDU/Biggie mirror, RUKI/Smalls authority) | LOW | Evidence doc itself already names this as the deliberate next architectural step, not something TASK-298 claimed to solve. Consistent with everything else observed this session about the Biggie/Smalls authority boundary (enforced in code via `guard_production_write`, not just convention). No new risk introduced by this task specifically. |

---

## Findings

| Severity | File | Section | Finding | Required action |
|---|---|---|---|---|
| — | — | — | — | — |

No BLOCKER or REQUIRED findings.

---

## Notes

Approval makes the preserved backup path **eligible** for removal per
criterion 6's own wording — it does not by itself instruct anyone to remove
it. Given `MAP_System/DESTRUCTIVE_ACTION_POLICY.md`-style conventions
observed elsewhere this session (destructive/irreversible actions get their
own explicit, deliberate step, not an automatic side effect of an unrelated
approval), recommend leaving the backup in place until the operator or
recovery coordinator makes a separate, explicit decision to remove it —
there is no cost to leaving it and real cost to a rushed deletion.

This review deliberately used a live, independent second pass
(`rotation-replacement-kite-veni`, read-only, on Smalls) rather than trusting
the two-day-old evidence doc alone, given this session's own finding
(`INS-0058`) that submission-time evidence can go stale by review time. It
did not go stale here — every re-checked claim matched exactly — but the
check was worth doing precisely because that wasn't guaranteed in advance.
