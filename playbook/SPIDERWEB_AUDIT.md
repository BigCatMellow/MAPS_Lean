# Spiderweb Audit

Use this method to answer:

> **Is forward-relevant project information connected well enough that a fresh
> agent can find what caused it, what it relates to, and what happened next?**

Spiderweb is an **advisory information-integrity method**. It is not task truth,
policy authority, a knowledge graph, or an automatic organizer.

Related methods:

- [Information Lifecycle](INFORMATION_LIFECYCLE.md) — governs active,
  superseded, and historical information.
- [E/I](EMERGENCE.md) — captures insight → idea → experiment → promotion.
- [AGI Standard](AGI_STANDARD.md) — asks whether a fresh agent can safely use
  an artifact.
- [Roadmap Trajectory Check](ROADMAP_TRAJECTORY_CHECK.md) — asks whether the
  project is still moving in the right direction.
- [Tenth-Seat Review](TENTH_SEAT_REVIEW.md) — challenges unusually clean
  consequential consensus.

## 1. Model

```text
repository Markdown
        ↓
deterministic Spiderweb scan
        ↓
objective defects + relationship candidates
        ↓
bounded semantic reconciliation by a fresh agent
        ↓
CONNECTED | MISSING_LINK | STALE_DISPOSITION |
SUPERSEDED | INTENTIONALLY_STANDALONE | UNKNOWN
        ↓
smallest evidence-backed correction, if any
```

The deterministic scan may identify structure. It must not decide that two
artifacts are semantically related merely because their text is similar.

## 2. When to run

Run Spiderweb as a bounded check, not continuously:

- at a [roadmap trajectory check](ROADMAP_TRAJECTORY_CHECK.md) when several PRs
  or sessions have accumulated;
- before a major multi-session handoff or external Proof Phase;
- after a large migration/reconciliation arc;
- when a good idea, decision, review finding, or temporary workaround appears
  to have disappeared from current navigation;
- when old notes repeatedly look like unfinished work after later implementation.

Do not create a daemon, permanent scout agent, or background watcher.

## 3. Deterministic scanner

Default active scan:

```bash
python scripts/check_spiderweb.py
```

Machine-readable output:

```bash
python scripts/check_spiderweb.py --json
```

Reduce low-value thin-link noise:

```bash
python scripts/check_spiderweb.py --no-thin
```

Raw historical archaeology is opt-in:

```bash
python scripts/check_spiderweb.py --include-historical
```

The default scan excludes raw preservation/history surfaces:

- `legacy/`
- `migration/legacy-runtime-source/`
- `migration/legacy-knowledge-source/`
- `archive/`
- `work/context/`

Curated migration records such as `migration/FUTURE_IDEAS_BACKLOG.md`, the
promotion ledger, idea-recovery audit, and removal/audit documents remain in the
default scan because they still carry forward-relevant navigation/disposition.

Historical targets may still be recorded as outgoing historical relationships
from active files.

### Objective findings

- `BROKEN_LINK` — local Markdown target does not exist.
- `DUPLICATE_STABLE_ID` — the same declared stable ID appears in multiple
  scanned artifacts.

These are structural defects. The script can optionally return non-zero for
these only:

```bash
python scripts/check_spiderweb.py --fail-on-broken
```

This is **not** the default. Spiderweb begins advisory.

### Advisory relationship findings

- `ORPHAN_CANDIDATE` — no active inbound or outbound Markdown relationship.
- `THIN_CONNECTION` — only one active relationship.
- `HISTORICAL_ONLY` — no active relationship; outgoing links point only into
  historical material.
- `UNRECONCILED_CAPTURE` — an idea/insight still says `Not promoted` but has no
  later disposition/reconciliation section.
- `SUPERSEDED_WITHOUT_LINK` — a record says `SUPERSEDED` but does not point to
  replacement/context.
- `OVERDUE_PENDING_EXPERIMENT` — a pending experiment/result contains a
  structured end date before the requested `--as-of` date.

These findings are **questions, not conclusions**.

## 4. Spiderweb Reconciliation AGI

Use this instruction for the semantic pass over scanner findings.

> ### Goal
> Inspect each flagged artifact and enough current surrounding evidence to
> determine whether it is genuinely disconnected, already resolved elsewhere,
> intentionally standalone, superseded, or missing a durable relationship.
>
> ### Authority
> Spiderweb findings are advisory evidence only. Current code, canonical task
> state, approved decisions, `AGENTS.md`, and current project authority remain
> stronger sources. Do not change authority merely to make the graph cleaner.
>
> ### Required classifications
> For each investigated finding, choose exactly one:
>
> - `CONNECTED` — the current relationship is already sufficient; scanner
>   structure looked weak but no correction is needed.
> - `MISSING_LINK` — direct evidence proves a durable relationship is missing.
> - `STALE_DISPOSITION` — the historical observation remains valid as history,
>   but later reality changed what the record means now.
> - `SUPERSEDED` — a later artifact/decision/mechanism replaced this one.
> - `INTENTIONALLY_STANDALONE` — isolation is deliberate and safe.
> - `UNKNOWN` — evidence is insufficient; do not guess.
>
> ### For every proposed relationship
> Record:
>
> 1. source artifact;
> 2. target artifact;
> 3. relationship type;
> 4. direct evidence establishing the relationship;
> 5. whether the source's current disposition should change;
> 6. smallest correction required.
>
> ### Rules
> - Prefer one durable relative Markdown link over copied explanation.
> - Preserve the original observation; add current disposition rather than
>   rewriting history to pretend later evidence was known earlier.
> - Check current code/checklist/merged-PR history before calling an old
>   `future task` note unfinished.
> - Do not infer a relationship from topic similarity alone.
> - Do not infer supersession from dates alone.
> - Do not promote an idea automatically.
> - Do not create a task merely because an orphan exists.
> - Do not reopen a settled decision merely because a newer file discusses it.
> - Do not create links whose only purpose is raising graph degree.
> - Do not create manual duplicate backlinks when a reverse view can be derived.
> - If the evidence is ambiguous, use `UNKNOWN`.
>
> ### Completion
> The pass succeeds when each material candidate has an evidence-backed
> disposition and only the smallest useful links/status annotations are
> proposed. A dense graph is not the goal; **recoverable meaning is**.

## 5. Fresh-agent traversal test

After a meaningful reconciliation, give a fresh agent one node without chat
history and ask it to recover:

- what caused this artifact;
- what it supports or affects;
- whether it is active, deferred, rejected, superseded, or resolved;
- what evidence supports that disposition;
- what happened next;
- when it should be reconsidered, if applicable.

Repeat from a different artifact type, such as a PR review finding or decision.

Measure:

- material items missed;
- ghost gaps rediscovered as new;
- repository-wide searches required;
- historical files opened;
- unsupported relationships invented.

Spiderweb earns its place only if this becomes cheaper and more accurate.

## 6. Relationship quality, not link count

A link is useful when it carries project meaning.

Useful examples:

```text
IDEA → tested by EXPERIMENT
EXPERIMENT → informs DECISION
DECISION → implemented by TASK/PR
REVIEW FINDING → deferred until named trigger
HANDOFF → superseded by newer HANDOFF
REPAIR → frozen as REGRESSION CASE
PLAYBOOK → governed by AGENTS / used by task type
```

Bad examples:

```text
random note → another note because both mention recovery
idea → README merely to avoid orphan status
every file → central index with no meaningful relationship
```

Do not optimize graph density.

## 7. Storage rule

Spiderweb stores no new canonical graph.

```text
standard relative Markdown links
        ↓
scanner derives edges/backlinks/findings
        ↓
JSON/text report is disposable
```

The repository files remain the durable artifacts. Derived graph information
may be rebuilt at any time.

## 8. Relationship to other epistemic checks

```text
AGI          → can a fresh agent understand and execute this?
Spiderweb    → can a fresh agent find the surrounding meaning?
Review       → is the implementation/claim correct?
Tenth Seat   → what is the strongest credible case consensus is wrong?
Trajectory   → is the project still working on the right things?
```

These checks answer different questions. Do not merge their authority.

## 9. Minimal rule

> **Spiderweb finds structural isolation; evidence decides whether a connection
> belongs.**

The purpose is not to connect everything to everything. It is to prevent
important information from becoming unreachable or misleading as sessions,
implementations, and decisions accumulate.
