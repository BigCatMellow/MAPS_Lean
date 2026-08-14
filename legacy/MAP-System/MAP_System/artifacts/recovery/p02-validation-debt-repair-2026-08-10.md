# P0.2 Validation Debt Repair — 2026-08-10

- status: complete
- owner (accountable, submits): claude-lab-sumi
- support (this record): helper-task323-p02-tina
- task: TASK-323
- scope: MAP_System/inbox/helpers/helper-task323-p02-repair.md, per
  helper-librarian.md 2026-08-09 rerun findings.

This is bounded support work. I do not claim or submit TASK-323 — sumi
does. This record documents what was found, what was fixed directly, and
what is proposed pending authority action.

## Part 1 — events.jsonl NUL corruption at line 18785

**Status: repaired.** See `MAP_System/repairs/REPAIR-0013-*.md` for the
full repair record.

### Finding

Line 18785 of `MAP_System/events/events.jsonl` consisted of 1526 leading
NUL bytes (`\x00`), causing `validate_events.py` to fail JSON decoding at
that line. The file was 6,812,403 bytes; a whole-file NUL count came back
as exactly 1526, confirming the corruption was isolated to this single
line — no other line in the file contained any NUL byte.

### What the bytes actually were

The bytes immediately following the NUL run formed a complete,
well-formed JSON event:

```json
{"created_at": "2026-08-07T14:55:10-04:00", "type": "PROGRESS", "task_id": "TASK-083", "sender": "limit_watcher", "summary": "RnS: recorded resume window passed for mapfinish-guru (resume_after 2026-07-28T17:41:18-04:00); visible resume nudge FAILED.", "artifact_paths": []}
```

This is not a guess or a reconstruction — the bytes were sitting there
intact. Its structure is identical to the five sibling lines immediately
before and after it (lines 18783–18784, 18786–18789), all emitted by
`limit_watcher` in the same batch, differing only in the agent-name token
(`mapfinish-kino`, `-rafa`, `-dove`, `-zemi`, and this one, `-guru`). The
NUL bytes carried zero information — most likely leftover zero-fill from
a partial/interrupted append (e.g. a crash between extending the file and
writing content), not lost content.

### Repair procedure (append-only-preserving)

1. **Evidence first.** Before any edit, wrote the exact original bytes of
   line 18785 (1800 bytes, no trailing newline) to
   `MAP_System/artifacts/recovery/evidence/events-jsonl-line-18785-original.bin`,
   plus its sha256 to the paired `.sha256` file.
   - sha256 of original corrupted line:
     `b585dc3da4a8440ba68a3e1b00323b4f4f5af5eb6bf392d43cebaa3c2a8a9a97`
2. **Minimal, verified fix.** Stripped only the 1526 leading NUL bytes
   from that one line (Python `lstrip(b'\x00')` on the exact line,
   asserted the NUL count and length delta before writing). No other byte
   in the file was touched.
   - Whole-file sha256 before: `010dd2af3a29dd0820871593bbabb0fec9541cf561532b71bd341e52929f5c5a`
   - Whole-file sha256 after: `502523123df4a1efbbf87ccde872d68288491068ddc5d7cf4e4decb724ea7cfe`
   - Bytes removed: exactly 1526 (matches NUL count, confirms no other
     drift).
3. **Verification.** `python3 MAP_System/scripts/validate_events.py` now
   reports `errors=0 legacy_warnings=35 new_warnings=0
   baseline_line_count=4501` — previously errored at line 18785. No new
   warnings were introduced.

### Evidence retained

- `MAP_System/artifacts/recovery/evidence/events-jsonl-line-18785-original.bin`
- `MAP_System/artifacts/recovery/evidence/events-jsonl-line-18785-original.sha256`
- `MAP_System/repairs/REPAIR-0013-events-jsonl-line-18785-had-1526-leading-nul-bytes-prefixing-an-otherwise-valid.md`

### Addendum — mirror-sync revert and Smalls-side re-fix (2026-08-10)

The fix above initially landed on Biggie's local mirror only. Because
`events.jsonl` is a wholesale-overwritten `MIRROR_FILE`, the next
scheduled sync from Smalls silently reverted it, reintroducing the same
1526 NUL bytes. `helper-releases-batch2-bela` re-applied the identical
fix directly on Smalls (the writable authority), which is durable against
future syncs. Verified 2026-08-10 by claude-lab-sumi: line 18785 is
byte-identical clean on both Biggie and Smalls, and
`validate_events.py` reports `errors=0` on Biggie's copy after the
Smalls-side fix synced down. Full account in REPAIR-0013's "Mirror-sync
revert" section.

## Part 2 — TASK-315 stale release backlink

**Status: applied, confirmed on Smalls.** See
`MAP_System/repairs/REPAIR-0014-*.md` for the full repair record. The
proposed single-row `checklist_path` correction has been applied at the
authority host; verified 2026-08-10 by claude-lab-sumi via direct query
against Smalls' `map.db`.

### Finding

`task_release_records.checklist_path` for `TASK-315` in `MAP_System/map.db`
is:

```
/home/home/Projects/MultiAgentProject/Source/MAP_System/artifacts/releases/task-315-release-checklist.md
```

That legacy path does not exist. The checklist exists and passes the
tier-specific checklist validator at the current repo path:

```
MAP_System/artifacts/releases/task-315-release-checklist.md
```

This is the sole path failure among 133 SQLite release rows (132/133
pass), per four consecutive helper-librarian audits (2026-07-29 through
the 2026-08-09 rerun) that flagged it read-only without fixing it.

### Why this was not hand-edited via local SQL

Per the task's explicit instruction and confirmed by inspecting
`map_authority.py`: this workspace runs in MAP authority **mirror** mode.
`authority_status()` requires the local database be non-writable for
mirror topology to be valid, so a direct `sqlite3 ... UPDATE` would both
violate policy and (correctly) be against the mirror contract even if it
technically succeeded on disk.

I also checked whether any existing verb could fix this the "normal" way:

- `release_task.py`'s `release()` only `INSERT`s a `task_release_records`
  row, and only when the task's SQLite status is `APPROVED`
  (`task_release_records.task_id` is a PRIMARY KEY). TASK-315 is already
  `RELEASED`, so re-running release is not possible.
- `map_task.py`'s `amend-criteria` verb only amends acceptance-criteria
  text, not release records.
- `map_repair.py create` only writes a repair-record markdown artifact;
  it does not touch SQLite.

No verb exists for correcting a `checklist_path` on an already-released
task. The correction has to happen authority-side.

### Proposed fix (pending authority action)

Authority host should run a single-row `UPDATE
task_release_records SET checklist_path =
'MAP_System/artifacts/releases/task-315-release-checklist.md' WHERE
task_id = 'TASK-315'`, then let mirrors sync normally. This is
non-destructive (path-only correction, no status/ownership change) and
auditable via the repair record. If this class of drift recurs, consider
adding a `map_task.py fix-release-path` verb that goes through
`map_authority.py`'s remote-request path instead of requiring manual SQL.

### Evidence retained

- `MAP_System/repairs/REPAIR-0014-sqlite-task-release-records-checklist-path-for-task-315-still-points-to-the-none.md`
  (status: PROPOSED — needs authority-side action + sumi routing)

## Part 3 — Wikilink findings triage (22 findings)

Ran `python3 MAP_System/scripts/librarian.py validate` directly to get
the current 22 findings (matches helper-librarian.md's 2026-08-09 rerun
counts exactly: 6 scanner false positives, 11 resolvable shorthand IDs, 4
ambiguous AGENTS, 1 genuinely missing). No files were edited — this is
triage/disposition only, since applying wikilink-target fixes is an
editorial call outside bounded-support scope; recommended actions are
noted per finding for sumi/owner follow-up.

### Category: false-positive (6) — scanner misreads code/literal examples, not real links

| File | "Link" text | Disposition |
|---|---|---|
| `artifacts/operations/code-sync-timer-setup-2026-08-03.md` | `-n "$(git status --porcelain)"` | Bash snippet inside brackets; scanner misparses as wikilink. No action. |
| `artifacts/operations/code-sync-timer-setup-2026-08-03.md` | `"$current_branch" != "$BRANCH"` | Same — bash conditional. No action. |
| `artifacts/operations/code-sync-timer-setup-2026-08-03.md` | `"$(git rev-parse HEAD)" == "$(git rev-parse "origin/$BRANCH")"` | Same — bash conditional. No action. |
| `artifacts/releases/task-238-release-checklist.md` | `./stem` | Documented literal resolver-syntax example (how the wikilink resolver itself works), not a real link. No action. |
| `artifacts/reviews/task238-review-lilo.md` | `./<stem>` | Same literal resolver-syntax example. No action. |
| `artifacts/reviews/task238-review-lilo.md` | `./b` | Same literal resolver-syntax example (from the same TASK-238 doc set, tracked since the 2026-07-22 audit). No action. |

### Category: resolvable-shorthand (11) — short emergence IDs whose long-form file exists

Verified each target resolves to an existing file under
`MAP_System/emergence/`:

| File | Shorthand link | Long-form target found | Disposition |
|---|---|---|---|
| `emergence/ideas/IDEA-0026-*.md` | `IDEA-0027` | `emergence/ideas/IDEA-0027-record-submission-authorship-durably-submit-task-must-emit-a-sub.md` | Shorthand ID; scanner requires full slug. No content problem. |
| `emergence/insights/INS-0017-*.md` | `EXP-0008` | `emergence/experiments/EXP-0008-probe-can-a-no-self-review-guard-recover-authoring-identity-from.md` | Same. |
| `emergence/insights/INS-0017-*.md` | `EXP-0010` | `emergence/experiments/EXP-0010-probe-does-a-table-scoped-shared-state-validator-catch-real-drif.md` | Same. |
| `emergence/insights/INS-0018-*.md` | `INS-0020` | `emergence/insights/INS-0020-when-a-derived-dataset-looks-ambiguous-one-targeted-check-of-the.md` | Same. |
| `emergence/insights/INS-0019-*.md` | `INS-0040` | `emergence/insights/INS-0040-hand-maintained-canonical-state-files-are-an-unchecked-second-re.md` | Same. |
| `emergence/insights/INS-0020-*.md` | `EXP-0008` | (as above) | Same. |
| `emergence/insights/INS-0020-*.md` | `INS-0018` | `emergence/insights/INS-0018-when-a-rules-heavy-generative-task-hits-a-genuinely-ambiguous-so.md` | Same. |
| `emergence/insights/INS-0040-*.md` | `INS-0019` | `emergence/insights/INS-0019-a-100-line-domain-validator-written-at-the-start-of-a-generative.md` | Same. |
| `emergence/insights/INS-0042-*.md` | `INS-0039` | `emergence/insights/INS-0039-both-no-self-review-guards-key-on-tasks-owner-so-owner-claimant-.md` | Same. |
| `emergence/insights/INS-0043-*.md` | `INS-0039` | (as above) | Same. |
| `emergence/insights/INS-0044-*.md` | `SYN-0005` | `emergence/synthesis/SYN-0005-map-task-rows-accrete-fields-and-states-that-no-verb-can-reach-a.md` | Same. |

All 11 are cosmetic/scanner-strictness only — no missing content, no
broken cross-reference in practice. Recommended follow-up (not applied
here): either loosen the wikilink resolver to accept ID-prefix shorthand,
or expand these 11 links to full slugs. Neither is urgent; flagging for
sumi/owner to decide which.

### Category: ambiguous-AGENTS (4) — bare `AGENTS` link resolves to two files

| File | Ambiguous targets |
|---|---|
| `emergence/ideas/IDEA-0031-*.md` | `MAP_System/AGENTS.md` vs `MAP_System/templates/install/command-center-ui/AGENTS.md` |
| `emergence/insights/INS-0039-*.md` | same two |
| `emergence/insights/INS-0042-*.md` | same two |
| `emergence/insights/INS-0053-*.md` | same two |

There is repo precedent for resolving this exact ambiguity class: the
2026-07-18 audit's resolution
(`MAP_System/inbox/helpers/helper-librarian.md`, "Resolution — 2026-07-18
(claude-lab-lure)") disambiguated three earlier bare-`AGENTS` links to
`[[./AGENTS.md]]` — the root-relative form the resolver accepts for the
top-level `MAP_System/AGENTS.md`, as opposed to the nested
command-center-ui one. Recommended disposition for all 4: same fix,
`[[./AGENTS.md]]`, since context in all four emergence files is about MAP
System agent protocol, not the command-center-ui template. Not applied
here — editing emergence records is an editorial call for the owner, not
bounded support.

### Category: genuinely-missing (1)

| File | Link | Target checked | Disposition |
|---|---|---|---|
| `emergence/insights/INS-0051-*.md` | `haiku-agents-need-no-approval-tasks` | Not present anywhere under this repo (`MAP_System/**`). A file of that name *does* exist, but only as this operator's personal Claude Code memory note (`~/.claude/projects/.../memory/haiku-agents-need-no-approval-tasks.md`), outside the repo and outside the librarian's/wikilink resolver's scope. | Genuinely missing from the repo's perspective. Two real options: (a) the insight should link to wherever the durable MAP-side equivalent of that guidance lives (if one exists) instead of a personal memory note, or (b) if no such durable artifact exists, the insight is pointing at knowledge that was never captured in the repo and should either be written up as a real MAP artifact or have the link removed. Recommend owner decide; not applied here. |

### Verification

`python3 MAP_System/scripts/librarian.py validate` → `finding_count: 22`
(unchanged, since no wikilink-target edits were applied — triage/
disposition only, per scope).

## Summary for owner (claude-lab-sumi)

- Part 1 (events.jsonl): **done**, verified on both Smalls and Biggie
  after the mirror-sync-revert was found and re-fixed at the authority
  host. `validate_events.py` clean.
- Part 2 (TASK-315 backlink): **done**, applied at the authority host and
  confirmed on Smalls.
- Part 3 (wikilinks): **triaged**, all 22 categorized with disposition.
  11 shorthand + 4 AGENTS-ambiguous have recommended mechanical fixes
  (not applied — editorial, left for owner); 6 are false positives
  (no action needed); 1 is genuinely missing (needs an owner decision on
  where the real target should live).

Do not claim/submit TASK-323 myself — reporting to sumi to submit.

## Update — 2026-08-10, claude-lab-sumi (owner)

All three parts of TASK-323's acceptance criteria are now satisfied.
Resubmitting for independent review.
