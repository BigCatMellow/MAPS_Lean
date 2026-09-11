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
   ID, add its receipt, and register it before continuing.

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
| `LEGACY-MAPS-20260821` | `UNTRIAGED` | [`2026-08-21-roadmap-progress-and-handoff.md`](2026-08-21-roadmap-progress-and-handoff.md) | Pre-register receiving history not reconciled under this rule. | Not yet registered; recover mutable state from live GitHub before acting. |

This register begins on 2026-09-10. Unlisted older handoffs are not implicitly
`OPEN`, `CLOSED`, or otherwise resolved; they remain legacy records until
deliberately triaged.
