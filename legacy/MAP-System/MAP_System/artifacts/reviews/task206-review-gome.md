<!-- hpom: file: artifacts/reviews/task206-review-gome.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: claude-lab-gome -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-206 independent review, rereview after rework -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# Review Record: TASK-206

## Header

```text
task_id:      TASK-206
reviewer:     claude-lab-gome
review_date:  2026-07-17
task_owner:   codex-lab-hana
```

Reviewer (`claude-lab-gome`) != task owner (`codex-lab-hana`). Independence passes. Reviewer made no implementation contribution to this task.

## Verdict

```text
APPROVED
```

Rework resolved the finding below. Verdict history: first pass
CHANGES_REQUESTED (template/installed launcher mismatch); rework kept
the `dashboard` feature intentionally and added it to the canonical
template with the `__LOCAL_BIN__` placeholder, closing the gap.

## Forbidden Changes Check

| Forbidden change | Status |
|---|---|
| Edit files outside `output_paths` | NOT BROKEN — only the 4 registered files (2 templates, 2 installed launchers) plus the task record were touched. |
| Reintroduce a self-identifying `--name` on operator read/control calls | NOT BROKEN — `grep -n -- "--name"` confirms only the unrelated `hcom list --names` flag remains, both before and after rework. |
| Break `--from command-center` external attribution | NOT BROKEN — unchanged by the rework. |
| Change task scope (bundle in unrelated functionality beyond the disclosed `dashboard` reconciliation) | NOT BROKEN — the rework's only change is adding the already-installed `dashboard` command to the template; no other functional change. |

## Rereview (after rework)

- `diff` between each installed launcher and its template with
  `__PROJECT_DIR__`/`__LOCAL_BIN__` substituted back to the real
  installed values: **empty for both files** (`ai` and
  `ai-command-center-monitor`), i.e. the two are now structurally
  identical modulo only the placeholder substitution, independently
  reproduced rather than trusting the submitted claim.
- `ai dashboard` command and its help line now present in both the
  template (with `__LOCAL_BIN__/hcom-dashboard`) and the installed copy
  (with the resolved path); target binary `/home/mellow/.local/bin/hcom-dashboard`
  confirmed to exist.
- Re-ran all original live checks: `sh -n` passes on all 4 files, `ai
  status` exits 0 with clean output, `ai-command-center-monitor feed`
  (bounded) renders cleanly, `grep -n -- "--name"` still shows only the
  legitimate `hcom list --names` flag — no `--name` regression
  introduced by the rework.
- `validate_task_mirrors.py`, `validate_task_graph.py`,
  `validate_task_schema.py`, `validate_events.py --fail-on-new`: all
  pass (events: 0 errors, 0 new warnings).

## Acceptance Criteria Check

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | `ai` wrapper runs hcom control commands without an agent `--name`; `ai status` completes without an instance-name error | PASS | `grep -n -- "--name"` on both scripts returns zero matches (the one `--names` hit in `ai` is `hcom list --names`, a distinct, legitimate hcom flag — "just names, one per line" — confirmed via `hcom list --help`, unrelated to the bug). Ran `ai status` live: exit 0, clean `hcom list -v` output, no instance-name error. |
| 2 | Monitor queries hcom events without an agent `--name` and does not suppress an instance-name error | PASS | `print_hcom()` calls `"$HCOM" events --last 12 2>/dev/null \|\| true` with no `--name`. Ran `ai-command-center-monitor feed` live (bounded via `timeout 3`): renders hcom events, MAP events, and agent status cleanly, no error suppressed by the `\|\| true` (there was nothing to suppress — command succeeded). |
| 3 | Operator messages retain external attribution via `--from command-center`, while repository templates and installed launchers match | PASS | Attribution: `send_msg()` uses `exec "$HCOM" send $targets --intent inform --from "$OPERATOR_NAME" -- "$*"` with `OPERATOR_NAME` defaulting to `command-center`. Template/installed match: confirmed empty diff after rework (see Rereview). |

## Independent Verification

- `grep -n -- "--name"` on `MAP_System/templates/install/bin/ai` and
  `ai-command-center-monitor`: only the legitimate `hcom list --names`
  plural flag, no self-identifying `--name <agent>` anywhere.
- Live `ai status`: exit 0, correct output, no instance-name error.
- Live `ai-command-center-monitor feed` (bounded with `timeout 3`):
  clean render of hcom events, MAP events log tail, no error.
- `sh -n` shell syntax check: passes on all 4 files (2 repo templates,
  2 installed launchers).
- `diff` between repo templates and installed launchers: the
  `__PROJECT_DIR__`/`__LOCAL_BIN__` placeholder substitution is expected
  and correct templating behavior, not a defect. However, the installed
  `/home/mellow/.local/bin/ai` also contains an `ai dashboard` command
  (`exec /home/mellow/.local/bin/hcom-dashboard`) and its `usage()` help
  line, **absent from the repository template** — a real structural
  difference beyond placeholder substitution.

## Finding (RESOLVED)

| Severity | File | Section | Finding | Resolution |
|---|---|---|---|---|
| REQUIRED (RESOLVED) | `MAP_System/templates/install/bin/ai` vs `/home/mellow/.local/bin/ai` | `usage()` / `cmd` case statement | The installed launcher had an `ai dashboard` command (and its help-text line) that did not exist in the repository template — introduced during this task's own edit session per file mtimes, contradicting acceptance criterion 3. | `dashboard` confirmed intentional; added to the canonical template using the `__LOCAL_BIN__` placeholder pattern already used elsewhere in the file. Independently reproduced: normalized diff between template and installed copy is now empty for both `ai` and `ai-command-center-monitor`. |

## Assessment

The actual bug this task set out to fix — invalid hyphenated hcom
`--name` values breaking operator commands — is fixed correctly and
verified working end-to-end, live, not just by reading the diff. The
approach taken (omit `--name` entirely from operator-side calls, since
the wrapper isn't itself a persistent named agent) differs from the
task description's suggested approach ("underscore-safe base names")
but satisfies the literal, outcome-based acceptance criteria, which is
what should be graded. The one blocking issue is unrelated to the core
fix's correctness — it's a scope-discipline gap (an unrelated feature
addition leaked into the installed copy during this edit, not
back-propagated to the template) that the task's own stated acceptance
criteria explicitly catches.

## Files Reviewed

- `MAP_System/templates/install/bin/ai`
- `MAP_System/templates/install/bin/ai-command-center-monitor`
- `/home/mellow/.local/bin/ai`
- `/home/mellow/.local/bin/ai-command-center-monitor`
- `MAP_System/tasks/TASK-206.json`
