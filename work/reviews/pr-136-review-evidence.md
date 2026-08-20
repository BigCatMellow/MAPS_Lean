reviewer: pr136_reviewer
head_sha: a31ba99435093129c5f1a8495267153a05605fb1
independent: true
summary: APPROVED. Independently reviewed D1's docs-only design against its task contract, D0 audit, D2a file convention/templates, current installer, roadmap state, and PR head. The design preserves two explicit canonical roots, preview-first and confined target writes, current MAPS-side smoke semantics, and D2b/D2c/D3 boundaries; no implementation, target access, or status overclaim is present.

# Review: portable deployment D1 installer targeting design

- Task: `work/tasks/portable-deployment-d1-installer-targeting-design.md`
- Reviewed PR: #136, `portable-d1-installer-design`
- Reviewed code head: `a31ba99435093129c5f1a8495267153a05605fb1`
- Reviewer: `pr136_reviewer` (fresh independent reviewer)
- Verdict: `APPROVED`

## Acceptance criteria check

- `PASS` — `--target-repo <path>` parsing, separate canonical `MAPS_ROOT` / `TARGET_ROOT`, validation order, and refusals are specified.
- `PASS` — preview and apply semantics constrain target writes to missing `TARGET_ROOT/.maps/` content and prohibit MAPS task-state confusion or target source/dependency changes.
- `PASS` — `--run-smoke`, LangGraph, and hcom remain MAPS-side and optional; smoke success is not represented as target readiness.
- `PASS` — D1 consumes D0/D2a without defining D2b/D2c/D3 or changing installer/runtime code.
- `PASS` — checklist and Roadmap 06 show D1 `DONE`, D2a already `DONE`, and D2b/D2c/D3 `NOT STARTED`.

## Applicable review lenses

- `[x]` Functional / acceptance — directly inspected the task, design, cited D0/D2a evidence, templates, current installer behavior, and roadmap diff.
- `[x]` Authority / permission boundary — verified the design refuses implicit target selection, self-targeting, unsafe root ambiguity, target writes outside `.maps/`, target dependency/source/configuration changes, and target use of MAPS_Lean state.

## Evidence checked

- `git status --short --branch`: clean branch at `a31ba99435093129c5f1a8495267153a05605fb1`, matching the remote PR head.
- `git diff --check origin/main...HEAD`: passed.
- `git diff --name-only origin/main...HEAD`: limited to the D1 task/design and canonical roadmap/checklist paths.
- Targeted `rg` over Roadmap 06 and the capability checklist: D1 is `DONE`; D2b/D2c/D3 are `NOT STARTED`; 6.35 remains `IN PROGRESS`.
- Direct inspection of `scripts/install_maps.sh`, D0 audit, D2a design/templates, and the operator decision record: D1's stated boundaries are consistent with the inspected source evidence.
- `gh pr view 136`: PR is open against `main`, mergeable, and remote head is the reviewed SHA; test check passed before review evidence was added.

## Findings

- None.

## Reviewer limits

- No external target repository was available or accessed. This approves a design only; it does not establish an implemented installer, adapter, target initialization, or external pilot.
