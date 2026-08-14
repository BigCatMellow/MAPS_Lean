<!-- hpom: file: artifacts/tests/task-216-input-parity.md -->
<!-- hpom: project: ClearFront -->
<!-- hpom: state_owner: codex-lab-lilo -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-17 -->
<!-- hpom: verified_against: TASK-216; DEC-CF-007; post-TASK-215 app -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: NONE -->
<!-- hpom: superseded_by: NONE -->

# TASK-216 — input.js Extraction Parity Report

## Scope

TASK-216 completes the planned decomposition by moving only the
`initCardPeek` desktop-hover/touch-hold IIFE into `app/js/input.js`.
`input.js` publishes `CF.installInputModule()`; the inline host invokes it at
the IIFE's former position—after host action/overlay listeners and scrollbar
binding, before `showDeckSelect()`.

The host action buttons, modal listeners, scrollbar wiring, module installers,
shared mutable bindings, and bootstrap remain inline. No `ctx` key or shared
mutable binding was added.

## Mechanical extraction proof

- Pre-task `app/index.html` md5:
  `a2c9ebb1bc446c21d4cd93f2323f1267`.
- Extracted the old `initCardPeek` body and the new installer body, removed
  their four-space wrapper indentation, and compared them byte-for-byte.
- Result: **identical**, 69 body lines on each side, empty diff.
- Only integration changes are the new classic-script tag and replacement of
  the IIFE with `window.CF.installInputModule()` at the same ordering point.

## Focused input regression

Registered harness: `artifacts/tests/task216-input-check.mjs`. It opens the
editable app directly over `file://`, captures console messages and runtime
exceptions, and exits nonzero on any failed assertion.

| Assertion | Result |
|---|---|
| `CF.installInputModule` is published | PASS |
| `CF.ctx` remains exactly seven keys | PASS |
| Desktop mouseover creates visible non-touch preview | PASS |
| Desktop preview is noninteractive | PASS |
| Desktop mouseout removes preview | PASS |
| 350 ms touch hold creates `.card-peek.touch.show` | PASS |
| Touch hold creates backdrop | PASS |
| Touch end removes preview and backdrop | PASS |
| Console messages / runtime exceptions | 0 / 0 |

Headless Chromium does not reliably advertise `(hover: hover)`, so the harness
overrides only that media-query result before the second clean page load. The
production listener logic remains unchanged and the actual mouseover/mouseout
path is exercised.

## Broader parity

- Champion-select screenshots before and after extraction are byte-identical:
  md5 `fd85d1db8e3b326a58f9678384c6b198`.
- Reused the released TASK-214 seed-42 CDP harness against the current app:
  card play, attack, end turns, real blocker assignment, enemy combat/report,
  and AI-turn goals all passed; zero console messages/exceptions.
- Reused the fail-loud TASK-215 undo harness: 6/6 assertions passed, including
  ordinary undo restoration and TASK-213 replacement clearing undo; zero
  console messages/exceptions.

## Static and integrity checks

- `node --check` passes for `data.js`, `state.js`, `combat.js`, `render.js`,
  `input.js`, the focused harness, and the remaining inline host.
- `source/SHA256SUMS.txt` verifies all 11 preserved payloads.
- Preserved hashes:
  - source `Clearfront.html` sha256:
    `57e67f190b5a7f05418af1ad1884f8f99602ed6cc9731e02a9975086c0744fa6`
  - `baseline/index.html` sha256:
    `fa4dea9c0c5987b6c5e50f6e6707a36942f432edfb7951851367a70c5e4cfe9a`
  - `baseline/index.html` md5:
    `5124cac23a9bd326bb8dfd00a110af92`
- Post-task outputs:
  - `app/index.html` md5: `ccce9c802f7a2c47ddb35ba664961cfc`
  - `app/js/input.js` md5: `47c98e69bfb6b4b4facf1e6f054bc92f`
- Task graph, schema, and mirror validators pass.

## Acceptance criteria

1. Exact card-preview body moved behind installer at its former ordering point:
   **PASS**.
2. No `ctx`/shared-state growth; host integration wiring remains inline:
   **PASS**.
3. Direct `file://` hover/touch preview behavior with zero runtime errors:
   **PASS**.
4. Visual, seeded combat/blocking, and undo parity: **PASS**.
5. Syntax and preserved-source integrity: **PASS**.

Emergence capture considered: no new insight beyond the already established
plain-script installer and deterministic-browser parity patterns; no artifact
created.
