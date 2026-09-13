# Durable handoff register

This is the central discovery and lifecycle index for **durable handoff files** in
`work/handoffs/`. It is intentionally narrow: it answers whether a durable
handoff has been reviewed and where its work continued without making agents
scan the handoff directory.

It is **not** a second live PR/CI/review/ownership status database. Those mutable
facts remain on GitHub under the rules in
[`work/coordination/README.md`](../coordination/README.md). Detailed task truth
remains in the owning task/roadmap/spec/PR and the handoff itself.

## Handoff lifecycle

| Handoff status | Meaning | Required pointer |
| --- | --- | --- |
| `OPEN` | Handoff exists but no receiving agent/session has durably confirmed review. | Handoff path. |
| `ACKNOWLEDGED` | Receiving agent/session reviewed the handoff, but substantive successor work has not started. | Handoff path + review receipt. |
| `CONTINUED` | Successor work has started. | Durable continuation: task/work doc, issue, PR, commit, or repo path. |
| `CLOSED` | The handoff outcome was completed or absorbed into owning durable state. | Final result/evidence pointer. |
| `SUPERSEDED` | Another handoff replaced this one. | Replacement handoff/result pointer. |
| `UNTRIAGED` | Legacy handoff predating this register whose receiving history has not been reconciled. Do not use for new handoffs. | Existing handoff path. |

A workstream's operational state (`blocked`, `partial`, `ready`, etc.) is separate
from handoff lifecycle. A blocked workstream can still have an acknowledged or
continued handoff.

## Required receipt for durable handoff files

Every new forward-looking durable handoff must place this receipt near its top:

```text
Handoff ID: MAPS-HO-YYYYMMDD-<short-slug>
Handoff status: OPEN | ACKNOWLEDGED | CONTINUED | CLOSED | SUPERSEDED
Reviewed: NOT YET | YYYY-MM-DD by <agent/role/session>
Continued at: NOT YET | <durable repo path / issue / PR / commit / URL>
```

A chat title, hidden conversation, or vague statement that work continued
elsewhere is not a durable continuation pointer.

## Update protocol

1. **Create:** assign a stable handoff ID, set `Handoff status: OPEN`, add the
   receipt to the handoff, and add/update its row here in the same change.
2. **Receive:** after actually reading the handoff, the receiving agent/session
   records `Reviewed` and changes both the handoff and this register to
   `ACKNOWLEDGED` before claiming the handoff was handled. Acknowledgment does
   not itself claim that successor work was performed.
3. **Continue:** when substantive successor work begins, change both locations
   to `CONTINUED` and populate `Continued at` with the first durable continuation
   record. Do not copy mutable PR/CI facts into this register.
4. **Finish or replace:** use `CLOSED` with final evidence, or `SUPERSEDED` with
   the replacement pointer. Do not leave a completed handoff looking open.
5. **Reconcile:** if this register and the handoff receipt disagree, treat it as
   a coordination defect. Check the durable evidence, repair both, and do not
   claim the handoff is addressed until they agree.
6. **Legacy:** do not bulk-guess statuses for pre-register handoffs. When an
   older handoff becomes operationally relevant, review it, assign or confirm an
   ID, add its receipt, and register it before continuing. A legacy handoff that
   lives outside this repository (for example, an operator-home-directory session
   file) is recorded with its literal filename and an "outside repo" note instead
   of a relative link, since no repo-relative path resolves to it.

For a **GitHub-thread-only** handoff, keep its complete lifecycle receipt on the
same source issue/PR thread under the shared coordination headings rather than
creating a status-only repository commit. Record review acknowledgment and the
durable continuation pointer there. When the handoff reaches a terminal state,
record `CLOSED` with final-result evidence or `SUPERSEDED` with the replacement
pointer on that same source thread. Closing or merging the issue/PR does **not**
by itself establish handoff closure or supersession.

Agents checking a durable handoff should open this register first. Directory-wide
handoff search is a fallback for legacy recovery, not the normal start path.

## Register

Keep newest/recently changed handoffs first.

| Handoff ID | Handoff status | Handoff | Reviewed | Continued at |
| --- | --- | --- | --- | --- |
| `MAPS-HO-20260913-session43` | `CONTINUED` | `MAPS_Lean_Handoff_2026-09-13-session43.md` (outside repo, `/home/home/`) | 2026-09-13 by bobo | This session (bobo, hcom name), post-self-clear resume of session 43. |
| `LEGACY-MAPS-20260912-session42` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-12-session42.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260910-hore-backup-seat` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-10-hore-backup-seat.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260910-opcmd-gule-romi` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-10-opcmd-gule-romi.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260910-session40` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-10-session40.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260910-session41` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-10-session41.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260909-session39` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-09-session39.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260908-session38` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-08-session38.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260907-session35` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-07-session35.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260907-session36` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-07-session36.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260907-session37` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-07-session37.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260906-session33` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-06-session33.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260906-session34` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-06-session34.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260905-opcmd-gule` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-05-opcmd-gule.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260905-session32` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-05-session32.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-dec003-b-exercise` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-dec003-b-exercise.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-sana-reviewer` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-sana-reviewer.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-session27` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-session27.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-session28` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-session28.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-session29` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-session29.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-session30` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-session30.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260904-session31` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-04-session31.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260903-session24` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-03-session24.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260903-session25` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-03-session25.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260903-session26` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-03-session26.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session19-gela` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session19-gela.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session19` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session19.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session20` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session20.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session21-luve` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session21-luve.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session21-nava` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session21-nava.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session21` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session21.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session22` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session22.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260902-session23-rafa` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-02-session23-rafa.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260901-session14` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-01-session14.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260901-session15` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-01-session15.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260901-session16` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-01-session16.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260901-session17` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-01-session17.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260901-session18` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-09-01-session18.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260831-session10` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-31-session10.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260831-session11` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-31-session11.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260831-session12` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-31-session12.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260831-session13` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-31-session13.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260830-session8` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-30-session8.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260830-session9` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-30-session9.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260824-session7` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-24-session7.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260821` | `UNTRIAGED` | [`2026-08-21-roadmap-progress-and-handoff.md`](2026-08-21-roadmap-progress-and-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260820-session-portable-and-roadmap-progress` | `UNTRIAGED` | [`2026-08-20-session-portable-and-roadmap-progress.md`](2026-08-20-session-portable-and-roadmap-progress.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260819-session2` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-19-session2.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260819-session5` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-19-session5.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260819-session6` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-19-session6.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-task-001-onboarding-handoff` | `UNTRIAGED` | [`TASK-001-onboarding-handoff.md`](TASK-001-onboarding-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-task-002-question-led-onboarding-handoff` | `UNTRIAGED` | [`TASK-002-question-led-onboarding-handoff.md`](TASK-002-question-led-onboarding-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-task-005-linked-route-selection-handoff` | `UNTRIAGED` | [`TASK-005-linked-route-selection-handoff.md`](TASK-005-linked-route-selection-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-task-006-incident-triage-handoff` | `UNTRIAGED` | [`TASK-006-incident-triage-handoff.md`](TASK-006-incident-triage-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-task-007-repair-record-link-handoff` | `UNTRIAGED` | [`TASK-007-repair-record-link-handoff.md`](TASK-007-repair-record-link-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-task-008-returning-agent-handoff` | `UNTRIAGED` | [`TASK-008-returning-agent-handoff.md`](TASK-008-returning-agent-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-session2` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-18-session2.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-session3` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-18-session3.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-session4` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-18-session4.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260818-handoff` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-18.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260817-session2` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-17-session2.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260817-handoff` | `UNTRIAGED` | `MAPS_Lean_Handoff_2026-08-17.md` (outside repo — operator home dir, not tracked in git) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |
| `LEGACY-MAPS-20260813-lean-navigation-and-simulation-tuning` | `UNTRIAGED` | [`2026-08-13-lean-navigation-and-simulation-tuning.md`](2026-08-13-lean-navigation-and-simulation-tuning.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |

This register begins on 2026-09-10. Unlisted older handoffs are not implicitly
`OPEN`, `CLOSED`, or otherwise resolved; they remain legacy records until
deliberately triaged.
