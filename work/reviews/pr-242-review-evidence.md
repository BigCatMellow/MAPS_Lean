# PR #242 review evidence — SEC4 capability granularity §6 impl (code)

Independent review by maps-lean-vame (luve authored). Impl re-derived against
design note §6, MUST-NOT walked line-by-line, an independent 8-mutation set run
(luve's own 6/6 not trusted).

## Diff scope — CLEAN

`git diff --stat` (against the pre-#242 base) = exactly 6 files, all in §6's
MAY-change list: `runtime/skills/gate.py` (+11/-6), `runtime/skills/format.py`
(+16/-1), `runtime/skills/capability_policy.py` (+14/-2),
`tests/test_skill_capability_manifest.py`, `tests/test_skills_format.py`,
`work/roadmaps/CAPABILITY_CHECKLIST.md` (SEC4 row, +1 evidence clause). No extra
file.

## Impl matches §6 exactly

1. `gate.py` — `_SATISFYING_TOKENS["network-general"]` = `frozenset({"network-general"})`
   (dropped `"network-read"`); comment rewritten to explain the read/write
   detector limitation and that `network-read` stays a valid baseline
   declaration.
2. `format.py` — `_FILESYSTEM_WRITE_PATH_RE = re.compile(r"^filesystem-write:(?!/)(?!.*\.\.)[A-Za-z0-9_.\-/]+$")`,
   added as a 3rd alternative in `_parse_capability_manifest`'s token branch
   (alongside `_CAPABILITY_TOKENS` / `_SECRET_USE_RE`).
3. `capability_policy.py` — `_FILESYSTEM_WRITE_PREFIX = "filesystem-write:"`;
   `_required_flags` gains `if token.startswith(_FILESYSTEM_WRITE_PREFIX): return ()`
   after `_BASELINE`, before `_SECRET_USE_PREFIX`. Baseline, no flag — mirrors
   the `_SECRET_USE_PREFIX` shape.

## MUST-NOT walk — all HELD

- schema/table change — no `.sql` in the diff.
- manifest written into `task_policy` — `capability_policy.py` only reads
  `policy`; `_required_flags` returns flag names, never writes.
- a `HookRegistry` guard reads it — no guard/registry code touched.
- `filesystem-write:<path>` enforced vs `task["output_paths"]` (§4) —
  `_required_flags` returns `()`, no path comparison; `capabilities_within_envelope`
  unchanged; `output_paths` not referenced in the diff.
- `_DETECTOR_CAPABILITY` / detector regexes changed — dict unchanged (only the
  comment + the `_SATISFYING_TOKENS` set itself); `_NETWORK_ACCESS_RE` /
  `_DESTRUCTIVE_RE` not in the diff.
- bare `filesystem-write` / `network-general` meaning changed — `_BASELINE`
  still has bare `filesystem-write`; `_REQUIRES["network-general"]` still
  `("external_side_effect",)`; `network-general` still satisfies its own
  detected finding.
- recorded lifecycle subject re-assessed — no catalog/lifecycle/
  `register_skill_catalog` code touched.
- checklist status flip — SEC4 row reads `IN PROGRESS` on both sides; only
  evidence prose expanded.

## Acceptance 1–6

1. network-read-only + network-touching script → `UNDECLARED_CAPABILITY` BLOCK,
   `disposition == QUARANTINE` — PASS.
2. same Skill declaring `network-general` → `DECLARED_CAPABILITY_USE` INFO,
   `disposition == CLEAR`, no `UNDECLARED_CAPABILITY` — PASS (unchanged).
3. `filesystem-write:output/` + `a/b.txt` parse; `filesystem-write:`,
   `filesystem-write:../etc`, `filesystem-write:/abs` → `declared_capabilities
   == ()` (MALFORMED) — PASS.
4. `capabilities_within_envelope(["filesystem-write:x/"], policy)` == bare
   `filesystem-write`, `== (True, ())` for `policy in ({}, None, {destructive_action,
   external_side_effect})` — PASS.
5. checklist +1 clause, no flip — PASS.
6. ≥5 mutations killed — PASS (independent 8/8 below).

## The 2 updated existing tests — both encoded the bug, not a valid invariant

- `test_network_read_declaration_satisfies_generic_network_detection` →
  `..._no_longer_covers_a_detected_generic_access` (split into 3): the old
  `assertNotIn("UNDECLARED_CAPABILITY")` for a `network-read`-only Skill with a
  `requests.get` script asserted the over-permissive alias itself — the exact
  escape hatch §6 removes. The flip to `assertIn("UNDECLARED_CAPABILITY")` +
  `QUARANTINE` is correct; the "network-read with no network content is still
  clean" case is now a separate explicit test, so coverage grew. Legitimate.
- `test_declared_capability_skill_survives_into_plan_metadata`: the old fixture
  (`network-read` + `requests.get`) was "correctly declared" only under the old
  rule; under §6 it is now under-declared and would be QUARANTINED. Swapped to a
  genuinely correctly-declared Skill (`rm -rf ./scratch` + `filesystem-write\nshell`
  → `DESTRUCTIVE_OPERATION` covered by baseline `filesystem-write`). The test's
  purpose (a correctly-declared Skill survives into the plan;
  `memory_trust_gate_denied == 0`) is preserved. Legitimate — not a silenced
  check.

Non-blocking: after the fix no test exercises "a `network-general` Skill on an
`external_side_effect` task surfaces into the plan" end-to-end. The
`_REQUIRES["network-general"]` path is still covered by
`CapabilityIntersectionPlanTests` (analog) and the gate side by acceptance-2 —
a small e2e gap, not a regression. Regex cosmetic edges (lone `.` accepted,
`..foo` over-rejected) are harmless for a parse-only slice; flag for the §4
enforcement slice.

## Independent mutation set — 8/8 KILLED, no survivors

| # | Mutation | Result |
|---|----------|--------|
| M1 | `_SATISFYING_TOKENS["network-general"]` → re-add `"network-read"` (revert) | killed |
| M2 | `_SATISFYING_TOKENS["network-general"]` → `frozenset()` | killed |
| M3 | regex: drop `(?!/)` absolute-guard | killed |
| M4 | regex: drop `(?!.*\.\.)` traversal-guard | killed |
| M5 | regex: `+` → `*` (allow empty suffix) | killed |
| M6 | drop the `or _FILESYSTEM_WRITE_PATH_RE.match(line)` parser alternative | killed |
| M7 | `_required_flags` prefix branch → `return ("external_side_effect",)` | killed |
| M8 | drop the `filesystem-write:` prefix branch entirely | killed |

Oracle: `tests.test_skill_capability_manifest tests.test_skills_format
tests.test_skills_quality_gate`. Each mutation restored; `git diff --stat HEAD`
clean after the run.

## Verification (foreground)

```
python3 -m unittest tests.test_skill_capability_manifest tests.test_skills_format
  tests.test_skills_quality_gate tests.test_skills_quality_gate_metadata  -> 78 OK
python3 -m unittest tests.test_context_builder tests.test_skills_catalog     -> 50 OK
python3 -m runtime.smoke  -> exit 0
```

reviewer: maps-lean-vame
head_sha: d539e955fac7a24bac6c13f072649e6c8964e595
independent: true
summary: APPROVE — independent review of the SEC4 §6 capability-granularity impl; diff scope is exactly §6's MAY-change files, the full MUST-NOT list holds (no schema, no task_policy write, no output_paths enforcement, detectors untouched, bare-token meanings unchanged, no status flip), Acceptance 1-6 all pass, the 2 updated existing tests each encoded the over-permissive alias bug rather than a valid invariant (coverage grew), and an independent 8-mutation set killed 8/8 with no survivors; 78+50 tests + smoke green.
