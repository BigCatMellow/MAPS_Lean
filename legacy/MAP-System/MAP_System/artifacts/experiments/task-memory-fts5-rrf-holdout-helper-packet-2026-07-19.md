# TASK-260 Combined Fresh Holdout Packets

Audit copy only. Evaluator receives one packet at a time.

# TASK-260 Fresh Holdout Packet — F1

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: The game still had to open directly from disk while its monolithic engine was split apart. How do the extracted state and combat layers share mutable bindings and call across files, and what evidence shows the combat slice preserved behavior? | The game still had to open directly from disk | its monolithic engine was split apart. How do the extracted state and combat layers share mutable bindings and call across files | what evidence shows the combat slice preserved behavior
- algorithm signal: candidate_set (coverage 42%; supporting channels 21)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

The game still had to open directly from disk while its monolithic engine was split apart. How do the extracted state and combat layers share mutable bindings and call across files, and what evidence shows the combat slice preserved behavior?

## Candidates

### 1. TASK-214 — ClearFront: extract js/combat.js (card play, combat, end-turn, AI)
- ClearFront / clearfront-ui / RELEASED
- scope: Second and highest-risk engine-layer decomposition slice (RISK-CF-0001), scoped precisely in DEC-CF-005 (Projects/ClearFront/shared/decisions.md) after inspecting post-TASK-212 app/index.html directly (not the pre-207 module map, which predates…
- linked evidence:
  - `Projects/ClearFront/app/js/combat.js` [implementation; current_shared; resolved] — Combat layer (DEC-CF-005). ctx contract state.js uses: ctx.state is the only mutable binding this symbols CF…
  - `Projects/ClearFront/app/js/state.js` [implementation; current_shared; resolved] — Mutable game state stays declared once in app/index.html's inline script (DEC-CF-004). symbols CF; build Decklist; apply…

### 2. TASK-212 — ClearFront: extract js/state.js (deck/side/game-state setup)
- ClearFront / clearfront-ui / RELEASED
- scope: First engine-layer decomposition slice per DEC-CF-004 (Projects/ClearFront/shared/decisions.md). Extract from app/index.html's remaining inline IIFE into Projects/ClearFront/app/js/state.js: buildDecklist, applyDeckIdentity, showDeckSelect, makeCard, shuffle, createSide, resetGame, sideOf, otherSide…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/task-212-state-parity.md` [test; current_unique; resolved] — TASK-212 — state.js Extraction Parity Report; What was done; The mutable-state sharing mechanism (binding for combat.js…
  - `Projects/ClearFront/app/js/state.js` [implementation; current_shared; resolved] — Mutable game state stays declared once in app/index.html's inline script (DEC-CF-004). symbols CF; build Decklist; apply…

### 3. TASK-216 — ClearFront: extract js/input.js (card preview gestures)
- ClearFront / clearfront-engine / RELEASED
- scope: Final decomposition slice per DEC-CF-007. Move only the self-contained initCardPeek hover/touch preview IIFE into app/js/input.js behind CF.installInputModule(), invoked at the same inline-host ordering point…
- linked evidence:
  - `Projects/ClearFront/shared/decisions.md` [decision; current_unique; resolved] — Decisions — ClearFront; DEC-CF-001 — Project bootstrap and decision paths; DEC-CF-002 — Module split mechanism: plain…
  - `Projects/ClearFront/app/js/input.js` [implementation; current_unique; resolved] — Card-preview gesture layer (DEC-CF-007). no ctx dependency: the behavior is a self-contained DOM-event closure. symbols CF…

### 4. TASK-220 — ClearFront: deterministic rule-engine test matrix (headless, below the DOM)
- ClearFront / clearfront-ui / RELEASED
- scope: Implements the audit's second P0 (rule-engine regression evidence too narrow for future gameplay changes) using the seam proven by INS-0026: data.js+state.js+combat.js load unmodified in…
- linked evidence:
  - `Projects/ClearFront/tests/engine/engine-host.mjs` [test; current_unique; resolved] — Headless engine host for ClearFront rule tests (TASK-220, INS-0026). // Loads the REAL, UNMODIFIED app/js/data.js +…
  - `Projects/ClearFront/tests/engine/run-rules.mjs` [test; current_unique; resolved] — ClearFront deterministic rule-matrix runner (TASK-220). usage: node tests/engine/run-rules.mjs [--verbose] symbols verbose; host; failed Cases; total Assertions…

### 5. TASK-215 — ClearFront: extract js/render.js (rendering + clash animation)
- ClearFront / clearfront-ui / RELEASED
- scope: Third engine-layer decomposition slice, scoped precisely in DEC-CF-006 (Projects/ClearFront/shared/decisions.md) by direct inspection of post-TASK-214 app/index.html. Extract these 28 functions verbatim into Projects/ClearFront/app/js/render.js, published via…
- linked evidence:
  - `Projects/ClearFront/app/js/state.js` [implementation; current_shared; resolved] — Mutable game state stays declared once in app/index.html's inline script (DEC-CF-004). symbols CF; build Decklist; apply…
  - `Projects/ClearFront/app/js/combat.js` [implementation; current_shared; resolved] — Combat layer (DEC-CF-005). ctx contract state.js uses: ctx.state is the only mutable binding this symbols CF…

### 6. TASK-207 — ClearFront: reproducible bundle extraction to editable baseline
- ClearFront / clearfront-delivery / RELEASED
- scope: Operator directive hcom #311 (2026-07-16): take over ClearFront trading card game via MAP. First step per Lilo's intake handoff (MAP_System/handoffs/HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md): the original Clearfront.html is…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/task-extraction-parity.md` [test; current_unique; resolved] — TASK-207 — Bundle Extraction Parity Report; Revision note (post-review); Second revision note (post-rereview); What was extracted…
  - `Projects/ClearFront/scripts/extract_bundle.py` [implementation; current_unique; resolved] — Reproducible extractor for the ClearFront self-extracting HTML bundle. symbols guess ext; extract script; safe asset path…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1563

---

# TASK-260 Fresh Holdout Packet — F2

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: Replacing a hand card reveals hidden information. What prevents an older Undo snapshot from restoring the pre-replacement hand, while keeping normal one-step Undo, and how is that behavior covered below the DOM? | Replacing a hand card reveals hidden information. What prevents an older Undo snapshot from restoring the pre-replacement hand | keeping normal one-step Undo | how is that behavior covered below the DOM
- algorithm signal: no_strong_match (coverage 19%; supporting channels 12)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

Replacing a hand card reveals hidden information. What prevents an older Undo snapshot from restoring the pre-replacement hand, while keeping normal one-step Undo, and how is that behavior covered below the DOM?

## Candidates

### 1. TASK-215 — ClearFront: extract js/render.js (rendering + clash animation)
- ClearFront / clearfront-ui / RELEASED
- scope: Third engine-layer decomposition slice, scoped precisely in DEC-CF-006 (Projects/ClearFront/shared/decisions.md) by direct inspection of post-TASK-214 app/index.html. Extract these 28 functions verbatim into Projects/ClearFront/app/js/render.js, published via…
- linked evidence:
  - `Projects/ClearFront/app/index.html` [implementation; current_shared; resolved] — Clearfront — Champion Prototype Clearfront Rules Cards Log New Latest New game started. Undo Swap 1…
  - `Projects/ClearFront/artifacts/tests/task215-undo-check.mjs` [test; current_unique; resolved] — localhost:${CDP_PORT}/json/new?${encodeURIComponent(target)}`, { method: 'PUT' }); This seed can deterministically have the enemy go first; wait until…

### 2. TASK-217 — ClearFront: add category artwork and detail-on-preview card faces
- ClearFront / clearfront-ui / RELEASED
- scope: Operator-requested presentation improvement after decomposition. Generate three original bitmap category artworks (Unit, Spell, Relic). Compact card faces show cost/name/art/category/stats while full rules text, keywords…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/task-217-card-art-preview.md` [test; current_unique; resolved] — TASK-217 — Category Artwork and Detail-on-Preview Evidence; Result; Image prompts; Design-review checklist Compact hand/board cards now…
  - `Projects/ClearFront/app/assets/card-relic.png` [implementation; current_unique; resolved] — implementation card relic png

### 3. TASK-213 — ClearFront: close replacement undo hidden-information exploit
- ClearFront / clearfront-engine / RELEASED
- scope: Implement approved PROMO-0010/INS-0025 in the editable app only: replacement must reveal its new card without leaving a reversible snapshot; preserve ordinary one-step undo for…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/task213-replacement-undo-regression.md` [test; current_unique; resolved] — TASK-213 Replacement Undo Regression Evidence; Scope and change; Headless Chromium interaction regression; Static and integrity checks…
  - `Projects/ClearFront/app/index.html` [implementation; current_shared; resolved] — Clearfront — Champion Prototype Clearfront Rules Cards Log New Latest New game started. Undo Swap 1…

### 4. TASK-216 — ClearFront: extract js/input.js (card preview gestures)
- ClearFront / clearfront-engine / RELEASED
- scope: Final decomposition slice per DEC-CF-007. Move only the self-contained initCardPeek hover/touch preview IIFE into app/js/input.js behind CF.installInputModule(), invoked at the same inline-host ordering point…
- linked evidence:
  - `Projects/ClearFront/app/js/input.js` [implementation; current_unique; resolved] — Card-preview gesture layer (DEC-CF-007). no ctx dependency: the behavior is a self-contained DOM-event closure. symbols CF…
  - `Projects/ClearFront/app/index.html` [implementation; current_shared; resolved] — Clearfront — Champion Prototype Clearfront Rules Cards Log New Latest New game started. Undo Swap 1…

### 5. TASK-214 — ClearFront: extract js/combat.js (card play, combat, end-turn, AI)
- ClearFront / clearfront-ui / RELEASED
- scope: Second and highest-risk engine-layer decomposition slice (RISK-CF-0001), scoped precisely in DEC-CF-005 (Projects/ClearFront/shared/decisions.md) after inspecting post-TASK-212 app/index.html directly (not the pre-207 module map, which predates…
- linked evidence:
  - `Projects/ClearFront/app/index.html` [implementation; current_shared; resolved] — Clearfront — Champion Prototype Clearfront Rules Cards Log New Latest New game started. Undo Swap 1…
  - `Projects/ClearFront/app/js/combat.js` [implementation; current_shared; resolved] — Combat layer (DEC-CF-005). ctx contract state.js uses: ctx.state is the only mutable binding this symbols CF…

### 6. TASK-220 — ClearFront: deterministic rule-engine test matrix (headless, below the DOM)
- ClearFront / clearfront-ui / RELEASED
- scope: Implements the audit's second P0 (rule-engine regression evidence too narrow for future gameplay changes) using the seam proven by INS-0026: data.js+state.js+combat.js load unmodified in…
- linked evidence:
  - `Projects/ClearFront/tests/engine/engine-host.mjs` [test; current_unique; resolved] — Headless engine host for ClearFront rule tests (TASK-220, INS-0026). // Loads the REAL, UNMODIFIED app/js/data.js +…
  - `Projects/ClearFront/tests/engine/rules.cases.mjs` [test; current_unique; resolved] — Table-driven rule cases for the ClearFront engine (TASK-220). // Each case: { id, domain, title, deviation?…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1469

---

# TASK-260 Fresh Holdout Packet — F3

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: How does the local session-limit supervisor detect quota exhaustion in a still-live agent, reject stale or replayed evidence, persist the reset window, throttle retries, and wake the agent only when due? | How does the local session-limit supervisor detect quota exhaustion in a still-live agent, reject stale | replayed evidence, persist the reset window, throttle retries, and wake the agent only when due
- algorithm signal: candidate_set (coverage 68%; supporting channels 12)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

How does the local session-limit supervisor detect quota exhaustion in a still-live agent, reject stale or replayed evidence, persist the reset window, throttle retries, and wake the agent only when due?

## Candidates

### 1. TASK-221 — RnS: persistent local session-limit supervisor
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Operator-directed hardening after the 2026-07-17 Claude limit incident: make the existing deterministic RnS watcher self-sufficient when every cloud agent is exhausted. Detect fresh session-limit/reset…
- linked evidence:
  - `MAP_System/tests/test_limit_watcher.py` [test; current_unique; resolved] — Tests for limit_watcher decision logic (TASK-080). symbols status; entry; test parse resume after; test fresh live…
  - `MAP_System/scripts/limit_watcher.py` [implementation; current_unique; resolved] — Rise & Shine (RnS) limit watcher: auto-resume agents after usage limits. symbols parse resume after; decide…

### 2. TASK-228 — Repair visible non-Pi local Ollama advisory lane
- MAP / command-center-ui / RELEASED
- scope: Implement the bounded repair evidenced by artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md. Do not download models and do not re-enable Pi. Reconcile health/allowlist/documentation with installed locally tested qwen3.5:4b; provide…
- linked evidence:
  - `MAP_System/templates/install/command-center-ui/app/server.py` [implementation; current_shared; resolved] — Local CommandCenterUI app server. symbols resolve workspace; read json; steward state; steward control; sentinel state; sentinel…
  - `MAP_System/tests/test_local_ollama_lane.py` [test; current_unique; resolved] — Focused no-model tests for the visible local Ollama advisory lane. symbols test health uses local host…

### 3. TASK-225 — Build visible local MAP Steward attention assistant
- MAP / command-center-ui / APPROVED
- scope: Build the operator-approved local Jarvis-style MAP Steward. Combine deterministic health/task/RnS/E-I/lesson signals into a read-only attention packet, optionally ask local Ollama qwen3.5:4b to summarize that…
- linked evidence:
  - `MAP_System/templates/install/command-center-ui/app/server.py` [implementation; current_shared; resolved] — Local CommandCenterUI app server. symbols resolve workspace; read json; steward state; steward control; sentinel state; sentinel…
  - `MAP_System/tests/test_map_steward.py` [test; current_unique; resolved] — symbols Map Steward Tests; test deterministic attention prioritizes rework review and ei; test model parser rejects…

### 4. TASK-224 — Pilot local E/I sentinel and bounded curator queue
- MAP / command-center-ui / APPROVED
- scope: Implement EXP-0002 from reopened IDEA-0013. Build a token-free deterministic sentinel that reads durable MAP signals and writes non-promoted E/I candidates to a review queue…
- linked evidence:
  - `MAP_System/scripts/emergence_sentinel.py` [implementation; current_unique; resolved] — Deterministic E/I signal scanner and non-promoting candidate queue. symbols stamp; load events; detect; dedup key; existing…
  - `MAP_System/tests/test_emergence_sentinel.py` [test; current_unique; resolved] — symbols Emergence Sentinel Tests; test detects repeated rework and blockers; test scan deduplicates and never promotes…

### 5. TASK-223 — Operational learning promotion loop for startup orientation
- MAP / emergence-and-learning / APPROVED
- scope: Implement IDEA-0022/PROMO-0011: convert incident-derived operational notes into selectively promoted, canonical, scope-matched startup guidance. Reuse E/I as the capture and promotion funnel; do not create…
- linked evidence:
  - `MAP_System/tests/test_operational_lessons.py` [test; current_unique; resolved] — symbols Operational Lesson Tests; test live store validates and routes fallback; test overdue lesson is marked…
  - `MAP_System/scripts/operational_lessons.py` [implementation; current_unique; resolved] — Validate and project promoted operational lessons into startup context. symbols parse time; load store; validate; relevant…

### 6. TASK-229 — Record Pi 7B-16K requalification result and preserve capacity boundary
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Record the operator-authorized visible Pi qwen2.5-coder:7b-16k no-write communication requalification. Preserve the observed failure (no exact hcom acknowledgement and malformed terminal delivery claim), keep Pi…
- linked evidence:
  - `MAP_System/notes/pi-agent-communication-guide.md` [guide; current_shared; resolved] — Pi Agent Communication Guide; Purpose; Operational pause; If an operator-authorized diagnostic is requested Pi is a…
  - `MAP_System/artifacts/experiments/pi-local-capability-trial-2026-07-18.md` [artifact; current_shared; resolved] — Pi Local Capability Trial — 2026-07-18; Purpose; Runtime facts; Trial A — 4B read-only lifecycle artifact…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1459

---

# TASK-260 Fresh Holdout Packet — F4

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: Which local Ollama model is allowed into the narrow advisory lane, and how are unapproved tags, remote hosts, hidden model work, and accidental Pi authority kept out? | Which local Ollama model is allowed into the narrow advisory lane | how are unapproved tags, remote hosts, hidden model work, and accidental Pi authority kept out
- algorithm signal: candidate_set (coverage 59%; supporting channels 18)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

Which local Ollama model is allowed into the narrow advisory lane, and how are unapproved tags, remote hosts, hidden model work, and accidental Pi authority kept out?

## Candidates

### 1. TASK-228 — Repair visible non-Pi local Ollama advisory lane
- MAP / command-center-ui / RELEASED
- scope: Implement the bounded repair evidenced by artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md. Do not download models and do not re-enable Pi. Reconcile health/allowlist/documentation with installed locally tested qwen3.5:4b; provide…
- linked evidence:
  - `MAP_System/tests/test_local_ollama_lane.py` [test; current_unique; resolved] — Focused no-model tests for the visible local Ollama advisory lane. symbols test health uses local host…
  - `MAP_System/scripts/local_runner.py` [implementation; current_unique; resolved] — Scoped Ollama helper runner with durable MAP records. symbols Local Runner Error; utc stamp; slug; read…

### 2. TASK-232 — Normalize the HPOM comparative research artifact
- MAP / emergence-and-learning / RELEASED
- scope: The only current full-suite failure is an advisory HPOM comparative research report placed under artifacts/research with an unrecognized filename and no Research System summary…
- linked evidence:
  - `MAP_System/artifacts/research/SUMMARY-HPOM-OPERATING-MODELS-2026-07-18.md` [research; current_unique; resolved] — Research Summary; Question; Answer; Confidence Which practices improve HPOM efficiency, accountability, learning, and human
  - `MAP_System/emergence/synthesis/SYN-0002-a-goal-first-evidence-budgeted-practice-loop-makes-map-coordinat.md` [test; current_unique; resolved] — Synthesis Note; Pieces being combined; Piece A; Piece B ownership, review, and release gates support recovery…

### 3. TASK-225 — Build visible local MAP Steward attention assistant
- MAP / command-center-ui / APPROVED
- scope: Build the operator-approved local Jarvis-style MAP Steward. Combine deterministic health/task/RnS/E-I/lesson signals into a read-only attention packet, optionally ask local Ollama qwen3.5:4b to summarize that…
- linked evidence:
  - `MAP_System/scripts/map_steward.py` [implementation; current_shared; resolved] — Read-only local MAP Steward attention packet and optional Ollama summary. symbols stamp; read json; collect; deterministic…
  - `MAP_System/templates/install/command-center-ui/app/server.py` [implementation; current_shared; resolved] — Local CommandCenterUI app server. symbols resolve workspace; read json; steward state; steward control; sentinel state; sentinel…

### 4. TASK-230 — Record Pi health-check terminal-versus-hcom result
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Record the operator-authorized minimal health check against fresh visible Pi vema using qwen2.5-coder:7b-16k. The model displayed the exact acknowledgement in its terminal, but hcom…
- linked evidence:
  - `MAP_System/artifacts/experiments/pi-local-capability-trial-2026-07-18.md` [artifact; current_shared; resolved] — Pi Local Capability Trial — 2026-07-18; Purpose; Runtime facts; Trial A — 4B read-only lifecycle artifact…
  - `MAP_System/notes/pi-agent-communication-guide.md` [guide; current_shared; resolved] — Pi Agent Communication Guide; Purpose; Operational pause; If an operator-authorized diagnostic is requested Pi is a…

### 5. TASK-229 — Record Pi 7B-16K requalification result and preserve capacity boundary
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Record the operator-authorized visible Pi qwen2.5-coder:7b-16k no-write communication requalification. Preserve the observed failure (no exact hcom acknowledgement and malformed terminal delivery claim), keep Pi…
- linked evidence:
  - `MAP_System/artifacts/experiments/pi-local-capability-trial-2026-07-18.md` [artifact; current_shared; resolved] — Pi Local Capability Trial — 2026-07-18; Purpose; Runtime facts; Trial A — 4B read-only lifecycle artifact…
  - `MAP_System/notes/local-model-helper-guide.md` [guide; current_shared; resolved] — Local Model Helper Guide; Status; Rule; Operating Pattern able to inspect and interact through a visible…

### 6. TASK-220 — ClearFront: deterministic rule-engine test matrix (headless, below the DOM)
- ClearFront / clearfront-ui / RELEASED
- scope: Implements the audit's second P0 (rule-engine regression evidence too narrow for future gameplay changes) using the seam proven by INS-0026: data.js+state.js+combat.js load unmodified in…
- linked evidence:
  - `Projects/ClearFront/tests/engine/engine-host.mjs` [test; current_unique; resolved] — Headless engine host for ClearFront rule tests (TASK-220, INS-0026). // Loads the REAL, UNMODIFIED app/js/data.js +…
  - `Projects/ClearFront/tests/engine/run-rules.mjs` [test; current_unique; resolved] — ClearFront deterministic rule-matrix runner (TASK-220). usage: node tests/engine/run-rules.mjs [--verbose] symbols verbose; host; failed Cases; total Assertions…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1455

---

# TASK-260 Fresh Holdout Packet — F5

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: Why could a visibly active manual helper disappear from capacity accounting, and what exact durable note metadata plus regression behavior makes that accounting reliable? | Why could a visibly active manual helper disappear from capacity accounting | what exact durable note metadata plus regression behavior makes that accounting reliable
- algorithm signal: candidate_set (coverage 50%; supporting channels 12)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

Why could a visibly active manual helper disappear from capacity accounting, and what exact durable note metadata plus regression behavior makes that accounting reliable?

## Candidates

### 1. TASK-231 — Make helper-note activity metadata explicit and testable
- MAP / map-runtime / RELEASED
- scope: A visible, active helper assignment was silently excluded from LangGraph helper capacity because its durable note used display-only status text rather than the runner-parsed…
- linked evidence:
  - `MAP_System/tests/test_runner_helper_notes.py` [test; current_unique; resolved] — Regression tests for durable helper-note capacity metadata. symbols test manual active note counts and terminal note…
  - `MAP_System/scripts/run_tests.sh` [implementation; current_shared; resolved] — !/bin/sh

### 2. TASK-229 — Record Pi 7B-16K requalification result and preserve capacity boundary
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Record the operator-authorized visible Pi qwen2.5-coder:7b-16k no-write communication requalification. Preserve the observed failure (no exact hcom acknowledgement and malformed terminal delivery claim), keep Pi…
- linked evidence:
  - `MAP_System/inbox/helpers/pi-requalification-communication-2026-07-18.md` [artifact; current_unique; resolved] — Pi Assignment — 7B-16K Communication Requalification; Required reads; Exact action and pass condition; Strict scope communication…
  - `MAP_System/notes/pi-agent-communication-guide.md` [guide; current_shared; resolved] — Pi Agent Communication Guide; Purpose; Operational pause; If an operator-authorized diagnostic is requested Pi is a…

### 3. TASK-230 — Record Pi health-check terminal-versus-hcom result
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Record the operator-authorized minimal health check against fresh visible Pi vema using qwen2.5-coder:7b-16k. The model displayed the exact acknowledgement in its terminal, but hcom…
- linked evidence:
  - `MAP_System/inbox/helpers/pi-healthcheck-vema-2026-07-18.md` [artifact; current_unique; resolved] — Pi Assignment — Minimal Hcom Health Check; Exact action; Boundaries; Outcome Send exactly one hcom inform…
  - `MAP_System/notes/pi-agent-communication-guide.md` [guide; current_shared; resolved] — Pi Agent Communication Guide; Purpose; Operational pause; If an operator-authorized diagnostic is requested Pi is a…

### 4. TASK-221 — RnS: persistent local session-limit supervisor
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Operator-directed hardening after the 2026-07-17 Claude limit incident: make the existing deterministic RnS watcher self-sufficient when every cloud agent is exhausted. Detect fresh session-limit/reset…
- linked evidence:
  - `MAP_System/scripts/limit_watcher.py` [implementation; current_unique; resolved] — Rise & Shine (RnS) limit watcher: auto-resume agents after usage limits. symbols parse resume after; decide…
  - `MAP_System/artifacts/tests/rns-persistent-supervisor.md` [test; current_unique; resolved] — TASK-221 — persistent local RnS supervisor evidence; Delivered behavior; Verification; Operator-friction closeout transcript tails for fresh…

### 5. TASK-228 — Repair visible non-Pi local Ollama advisory lane
- MAP / command-center-ui / RELEASED
- scope: Implement the bounded repair evidenced by artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md. Do not download models and do not re-enable Pi. Reconcile health/allowlist/documentation with installed locally tested qwen3.5:4b; provide…
- linked evidence:
  - `MAP_System/scripts/local_runner.py` [implementation; current_unique; resolved] — Scoped Ollama helper runner with durable MAP records. symbols Local Runner Error; utc stamp; slug; read…
  - `MAP_System/tests/test_local_runner.py` [test; current_unique; resolved] — Tests for scoped local Ollama helper runner. symbols fake health; test unknown model rejected; test output…

### 6. TASK-223 — Operational learning promotion loop for startup orientation
- MAP / emergence-and-learning / APPROVED
- scope: Implement IDEA-0022/PROMO-0011: convert incident-derived operational notes into selectively promoted, canonical, scope-matched startup guidance. Reuse E/I as the capture and promotion funnel; do not create…
- linked evidence:
  - `MAP_System/notes/operational-learning-guide.md` [guide; current_unique; resolved] — Operational Learning Guide; Lifecycle; Commands; Safety Operational learning converts an incident note into future behavior without
  - `MAP_System/notes/command-center-lab-restart-startup.md` [guide; current_unique; resolved] — AI Command Center Lab Restart And Startup Notes; Purpose; Current Implementation State; Startup Contract When the…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1401

---

# TASK-260 Fresh Holdout Packet — F6

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: How does the operator attention UI queue unanswered requests, approval gates, and terminal prompts one at a time, preserve explicit operator action, and reflow structured Issue, Options, Recommendation, and Needed text for readability?
- algorithm signal: candidate_set (coverage 70%; supporting channels 5)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

How does the operator attention UI queue unanswered requests, approval gates, and terminal prompts one at a time, preserve explicit operator action, and reflow structured Issue, Options, Recommendation, and Needed text for readability?

## Candidates

### 1. TASK-237 — Add operator reply popup queue to CommandCenterUI
- MAP / command-center-ui / APPROVED
- scope: Add a keyboard-accessible AIM-style overlay that presents only new unanswered operator-directed hcom requests, approval gates, and terminal prompts. Preserve existing attention inbox and reply_to…
- linked evidence:
  - `MAP_System/artifacts/tests/task237-attention-popup.md` [test; current_unique; resolved] — TASK-237 CommandCenterUI Attention Popup Verification; Delivered; Verification approval gates, and terminal prompts one at a time.
  - `MAP_System/templates/install/command-center-ui/src/chat.html` [implementation; current_shared; resolved] — AI Command Center Start lab Attention needed 0 In the room 0 Refresh usage MAP status…

### 2. TASK-239 — Create repeatable MAP practice-scenario runbook and queue
- MAP / map-improvement / RELEASED
- scope: Create planning-only groundwork for recurring, operator-visible MAP practice scenarios with Claude. Define a repeatable lifecycle exercise, bounded roles, evidence packet, measures, stop rules, independent…
- linked evidence:
  - `MAP_System/artifacts/planning/map-practice-scenario-queue-2026-07-18.md` [artifact; current_unique; resolved] — MAP Practice-Scenario Queue — 2026-07-18; Selection rule; First planned pairing when Claude is available; KICK-01 carry-forward…
  - `MAP_System/notes/practice-scenario-runbook.md` [guide; current_unique; resolved] — MAP Practice-Scenario Runbook; Objective; Admission checklist; Standard run Run small, complete lifecycle exercises with an available…

### 3. TASK-225 — Build visible local MAP Steward attention assistant
- MAP / command-center-ui / APPROVED
- scope: Build the operator-approved local Jarvis-style MAP Steward. Combine deterministic health/task/RnS/E-I/lesson signals into a read-only attention packet, optionally ask local Ollama qwen3.5:4b to summarize that…
- linked evidence:
  - `MAP_System/templates/install/command-center-ui/src/chat.html` [implementation; current_shared; resolved] — AI Command Center Start lab Attention needed 0 In the room 0 Refresh usage MAP status…
  - `MAP_System/tests/test_map_steward.py` [test; current_unique; resolved] — symbols Map Steward Tests; test deterministic attention prioritizes rework review and ei; test model parser rejects…

### 4. TASK-240 — Improve CommandCenterUI attention popup message formatting
- MAP / command-center-ui / RELEASED
- scope: Improve the operator attention popup readability by preserving authored line breaks and visually separating structured request fields such as Issue, Options, Recommendation, and Needed…
- linked evidence:
  - `MAP_System/tests/test_command_center_popup_formatting.py` [test; current_unique; resolved] — Contract checks for readable structured attention-popup text. symbols Command Center Popup Formatting Tests; test popup formats…
  - `MAP_System/templates/install/command-center-ui/src/chat.js` [implementation; current_shared; resolved] — event id -> {bubble, msg} event id -> message DOM node (for jump-to) symbols feed; input…

### 5. TASK-249 — Fix pre-dispatch is_destructive false positive on prohibition clauses
- MAP / map-runtime / APPROVED
- scope: evaluate_pre_dispatch flagged read-only tasks as core-destructive because is_destructive() substring-matched hard-stop phrases even inside a prohibition. TASK-235 (read-only manifest) was blocked at claim because its…
- linked evidence:
  - `MAP_System/scripts/pre_dispatch_policy.py` [implementation; current_unique; resolved] — Pre-dispatch policy checker for MAP task assignments. symbols utc now; normalize; upper value; as bool; list…
  - `MAP_System/tests/test_pre_dispatch_policy.py` [test; current_unique; resolved] — Tests for TASK-163 pre-dispatch policy checker and claim gate. symbols base task; core result; test core…

### 6. TASK-229 — Record Pi 7B-16K requalification result and preserve capacity boundary
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Record the operator-authorized visible Pi qwen2.5-coder:7b-16k no-write communication requalification. Preserve the observed failure (no exact hcom acknowledgement and malformed terminal delivery claim), keep Pi…
- linked evidence:
  - `MAP_System/inbox/helpers/pi-requalification-communication-2026-07-18.md` [artifact; current_unique; resolved] — Pi Assignment — 7B-16K Communication Requalification; Required reads; Exact action and pass condition; Strict scope communication…
  - `MAP_System/notes/pi-agent-communication-guide.md` [guide; current_shared; resolved] — Pi Agent Communication Guide; Purpose; Operational pause; If an operator-authorized diagnostic is requested Pi is a…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1429

---

# TASK-260 Fresh Holdout Packet — F7

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: A read-only task said not to restart services and was wrongly treated as destructive. How does pre-dispatch now distinguish a prohibition from a real destructive command without weakening the approval gate? | A read-only task said not to restart services and was wrongly treated as destructive | How does pre-dispatch now distinguish a prohibition from a real destructive command without weakening the approval gate
- algorithm signal: candidate_set (coverage 53%; supporting channels 11)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

A read-only task said not to restart services and was wrongly treated as destructive. How does pre-dispatch now distinguish a prohibition from a real destructive command without weakening the approval gate?

## Candidates

### 1. TASK-249 — Fix pre-dispatch is_destructive false positive on prohibition clauses
- MAP / map-runtime / APPROVED
- scope: evaluate_pre_dispatch flagged read-only tasks as core-destructive because is_destructive() substring-matched hard-stop phrases even inside a prohibition. TASK-235 (read-only manifest) was blocked at claim because its…
- linked evidence:
  - `MAP_System/tests/test_pre_dispatch_policy.py` [test; current_unique; resolved] — Tests for TASK-163 pre-dispatch policy checker and claim gate. symbols base task; core result; test core…
  - `MAP_System/scripts/pre_dispatch_policy.py` [implementation; current_unique; resolved] — Pre-dispatch policy checker for MAP task assignments. symbols utc now; normalize; upper value; as bool; list…

### 2. TASK-235 — Create a current CommandCenter deployment-source manifest and provenance check
- MAP / command-center-ui / APPROVED
- scope: Turn TASK-234 parity evidence into a durable, read-only deployment-source manifest and repeatable runtime-provenance check. Preserve historical records as provenance, but make the current configured…
- linked evidence:
  - `MAP_System/artifacts/audits/command-center-deployment-source-manifest-2026-07-18.md` [artifact; current_unique; resolved] — CommandCenter Deployment-Source Manifest and Provenance Check; 0. Guardrail and method; 1. Configured launch chain (AC1); 2…
  - `MAP_System/tasks/TASK-235.json` [task_scope; task_snapshot; resolved] — Create a current CommandCenter deployment-source manifest and provenance check Turn TASK-234 parity evidence into a durable…

### 3. TASK-228 — Repair visible non-Pi local Ollama advisory lane
- MAP / command-center-ui / RELEASED
- scope: Implement the bounded repair evidenced by artifacts/experiments/local-ollama-lane-inventory-2026-07-18.md. Do not download models and do not re-enable Pi. Reconcile health/allowlist/documentation with installed locally tested qwen3.5:4b; provide…
- linked evidence:
  - `MAP_System/scripts/local_assistant_health.py` [implementation; current_unique; resolved] — Read-only local assistant capability health check. symbols Command Result; run command; parse ollama models; check ollama…
  - `MAP_System/tests/test_local_ollama_lane.py` [test; current_unique; resolved] — Focused no-model tests for the visible local Ollama advisory lane. symbols test health uses local host…

### 4. TASK-223 — Operational learning promotion loop for startup orientation
- MAP / emergence-and-learning / APPROVED
- scope: Implement IDEA-0022/PROMO-0011: convert incident-derived operational notes into selectively promoted, canonical, scope-matched startup guidance. Reuse E/I as the capture and promotion funnel; do not create…
- linked evidence:
  - `MAP_System/notes/command-center-lab-restart-startup.md` [guide; current_unique; resolved] — AI Command Center Lab Restart And Startup Notes; Purpose; Current Implementation State; Startup Contract When the…
  - `MAP_System/notes/operational-learning-guide.md` [guide; current_unique; resolved] — Operational Learning Guide; Lifecycle; Commands; Safety Operational learning converts an incident note into future behavior without

### 5. TASK-225 — Build visible local MAP Steward attention assistant
- MAP / command-center-ui / APPROVED
- scope: Build the operator-approved local Jarvis-style MAP Steward. Combine deterministic health/task/RnS/E-I/lesson signals into a read-only attention packet, optionally ask local Ollama qwen3.5:4b to summarize that…
- linked evidence:
  - `MAP_System/tests/test_map_steward.py` [test; current_unique; resolved] — symbols Map Steward Tests; test deterministic attention prioritizes rework review and ei; test model parser rejects…
  - `MAP_System/templates/install/command-center-ui/app/server.py` [implementation; current_shared; resolved] — Local CommandCenterUI app server. symbols resolve workspace; read json; steward state; steward control; sentinel state; sentinel…

### 6. TASK-237 — Add operator reply popup queue to CommandCenterUI
- MAP / command-center-ui / APPROVED
- scope: Add a keyboard-accessible AIM-style overlay that presents only new unanswered operator-directed hcom requests, approval gates, and terminal prompts. Preserve existing attention inbox and reply_to…
- linked evidence:
  - `MAP_System/tests/test_command_center_attention_popup.py` [test; current_unique; resolved] — Static contract checks for the CommandCenterUI attention popup. symbols Command Center Attention Popup Tests; set Up…
  - `MAP_System/templates/install/command-center-ui/src/chat.html` [implementation; current_shared; resolved] — AI Command Center Start lab Attention needed 0 In the room 0 Refresh usage MAP status…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1472

---

# TASK-260 Fresh Holdout Packet — F8

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: How should a repeatable MAP practice run be admitted, measured, stopped, and independently reviewed, and what did the measured kickoff exercise reveal about handoff races and deployment-source uncertainty? | How should a repeatable MAP practice run be admitted, measured, stopped, and independently reviewed | what did the measured kickoff exercise reveal about handoff races and deployment-source uncertainty
- algorithm signal: candidate_set (coverage 37%; supporting channels 11)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

How should a repeatable MAP practice run be admitted, measured, stopped, and independently reviewed, and what did the measured kickoff exercise reveal about handoff races and deployment-source uncertainty?

## Candidates

### 1. TASK-233 — Run a measured MAP kickoff-alignment practice scenario
- MAP / map-improvement / RELEASED
- scope: Exercise MAP from a project kickoff through an implementation-ready brief without changing product code or policy. Use a realistic coordination-surface scenario, distinct visible participant…
- linked evidence:
  - `MAP_System/tasks/TASK-233.json` [task_scope; task_snapshot; resolved] — Run a measured MAP kickoff-alignment practice scenario Exercise MAP from a project kickoff through an implementation-ready…
  - `MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md` [artifact; current_unique; resolved] — MAP Kickoff-Alignment Practice Scenario; 0. Scenario purpose; 1. Shared project frame — v1 (frozen before participant…

### 2. TASK-239 — Create repeatable MAP practice-scenario runbook and queue
- MAP / map-improvement / RELEASED
- scope: Create planning-only groundwork for recurring, operator-visible MAP practice scenarios with Claude. Define a repeatable lifecycle exercise, bounded roles, evidence packet, measures, stop rules, independent…
- linked evidence:
  - `MAP_System/notes/practice-scenario-runbook.md` [guide; current_unique; resolved] — MAP Practice-Scenario Runbook; Objective; Admission checklist; Standard run Run small, complete lifecycle exercises with an available…
  - `MAP_System/artifacts/planning/map-practice-scenario-queue-2026-07-18.md` [artifact; current_unique; resolved] — MAP Practice-Scenario Queue — 2026-07-18; Selection rule; First planned pairing when Claude is available; KICK-01 carry-forward…

### 3. TASK-235 — Create a current CommandCenter deployment-source manifest and provenance check
- MAP / command-center-ui / APPROVED
- scope: Turn TASK-234 parity evidence into a durable, read-only deployment-source manifest and repeatable runtime-provenance check. Preserve historical records as provenance, but make the current configured…
- linked evidence:
  - `MAP_System/tasks/TASK-235.json` [task_scope; task_snapshot; resolved] — Create a current CommandCenter deployment-source manifest and provenance check Turn TASK-234 parity evidence into a durable…
  - `MAP_System/artifacts/audits/command-center-deployment-source-manifest-2026-07-18.md` [artifact; current_unique; resolved] — CommandCenter Deployment-Source Manifest and Provenance Check; 0. Guardrail and method; 1. Configured launch chain (AC1); 2…

### 4. TASK-234 — Audit CommandCenter deployment-source parity before coordination-card implementation
- MAP / command-center-ui / RELEASED
- scope: Run the read-only, evidence-bounded deployment-source parity audit recommended by KICK-01. Establish which checkout or installer template actually updates the operator Command Center, identify any…
- linked evidence:
  - `MAP_System/tasks/TASK-234.json` [task_scope; task_snapshot; resolved] — Audit CommandCenter deployment-source parity before coordination-card implementation Run the read-only, evidence-bounded deployment-source parity audit recommended by…
  - `MAP_System/artifacts/experiments/command-center-deployment-source-parity-audit-2026-07-18.md` [test; current_unique; resolved] — CommandCenter Deployment-Source Parity Audit; Purpose and guardrail; Method and evidence boundary; Candidate source and launch-path evidence…

### 5. TASK-207 — ClearFront: reproducible bundle extraction to editable baseline
- ClearFront / clearfront-delivery / RELEASED
- scope: Operator directive hcom #311 (2026-07-16): take over ClearFront trading card game via MAP. First step per Lilo's intake handoff (MAP_System/handoffs/HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md): the original Clearfront.html is…
- linked evidence:
  - `Projects/ClearFront/source/SHA256SUMS.txt` [artifact; current_unique; resolved] — 57e67f190b5a7f05418af1ad1884f8f99602ed6cc9731e02a9975086c0744fa6 ./Clearfront.html.dup
  - `Projects/ClearFront/scripts/extract_bundle.py` [implementation; current_unique; resolved] — Reproducible extractor for the ClearFront self-extracting HTML bundle. symbols guess ext; extract script; safe asset path…

### 6. TASK-224 — Pilot local E/I sentinel and bounded curator queue
- MAP / command-center-ui / APPROVED
- scope: Implement EXP-0002 from reopened IDEA-0013. Build a token-free deterministic sentinel that reads durable MAP signals and writes non-promoted E/I candidates to a review queue…
- linked evidence:
  - `MAP_System/agents/emergence-sentinel-state.json` [artifact; current_unique; resolved] — fields schema_version; status; last_run; last_success; last_error; candidates_new; candidates_total; runtime_ms; stop_requested
  - `MAP_System/tests/test_emergence_sentinel.py` [test; current_unique; resolved] — symbols Emergence Sentinel Tests; test detects repeated rework and blockers; test scan deduplicates and never promotes…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1507

---

# TASK-260 Fresh Holdout Packet — N1

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: Where was real-time online multiplayer synchronization with reconnect support implemented for ClearFront?
- algorithm signal: candidate_set (coverage 22%; supporting channels 3)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

Where was real-time online multiplayer synchronization with reconnect support implemented for ClearFront?

## Candidates

### 1. TASK-222 — Research efficient multi-agent delivery from ClearFront evidence
- ClearFront / clearfront-delivery / APPROVED
- scope: Operator-directed comparative study of how ClearFront was handled, focused on process rather than another product/code audit. Use the project task/event/artifact/hcom record as empirical evidence…
- linked evidence:
  - `MAP_System/tasks/TASK-222.json` [task_scope; task_snapshot; resolved] — Research efficient multi-agent delivery from ClearFront evidence Operator-directed comparative study of how ClearFront was handled, focused…
  - `MAP_System/artifacts/research/SUMMARY-clearfront-delivery-systems-comparative-study-2026-07-17.md` [research; current_unique; resolved] — Research Summary; Question; Answer; Executive answer Did MAP's multi-agent handling of ClearFront improve outcomes enough to…

### 2. TASK-226 — Discovery Agent pilot on completed ClearFront phase
- ClearFront / clearfront-delivery / APPROVED
- scope: Execute EXP-0003 using the operator-provided seven-pass, non-forcing Discovery Agent method. A new visible Codex helper performs proposal-only discovery over the completed ClearFront decomposition phase…
- linked evidence:
  - `MAP_System/artifacts/experiments/clearfront-discovery-agent-pilot-2026-07-17.md` [artifact; current_unique; resolved] — ClearFront Discovery Agent Pilot — Independent Output; Findings; Pass coverage and method note
  - `MAP_System/artifacts/experiments/clearfront-discovery-agent-adjudication-2026-07-17.md` [artifact; current_unique; resolved] — ClearFront Discovery Agent Pilot — Coordinator Adjudication; Verdict; Finding adjudication; Metrics **ADOPT WITH REFINEMENT.** The visible…

### 3. TASK-220 — ClearFront: deterministic rule-engine test matrix (headless, below the DOM)
- ClearFront / clearfront-ui / RELEASED
- scope: Implements the audit's second P0 (rule-engine regression evidence too narrow for future gameplay changes) using the seam proven by INS-0026: data.js+state.js+combat.js load unmodified in…
- linked evidence:
  - `Projects/ClearFront/tests/engine/engine-host.mjs` [test; current_unique; resolved] — Headless engine host for ClearFront rule tests (TASK-220, INS-0026). // Loads the REAL, UNMODIFIED app/js/data.js +…
  - `Projects/ClearFront/tests/engine/run-rules.mjs` [test; current_unique; resolved] — ClearFront deterministic rule-matrix runner (TASK-220). usage: node tests/engine/run-rules.mjs [--verbose] symbols verbose; host; failed Cases; total Assertions…

### 4. TASK-207 — ClearFront: reproducible bundle extraction to editable baseline
- ClearFront / clearfront-delivery / RELEASED
- scope: Operator directive hcom #311 (2026-07-16): take over ClearFront trading card game via MAP. First step per Lilo's intake handoff (MAP_System/handoffs/HANDOFF-CLEARFRONT-intake-codex-lab-lilo-to-claude-lab-gome.md): the original Clearfront.html is…
- linked evidence:
  - `Projects/ClearFront/scripts/extract_bundle.py` [implementation; current_unique; resolved] — Reproducible extractor for the ClearFront self-extracting HTML bundle. symbols guess ext; extract script; safe asset path…
  - `Projects/ClearFront/artifacts/tests/task-extraction-parity.md` [test; current_unique; resolved] — TASK-207 — Bundle Extraction Parity Report; Revision note (post-review); Second revision note (post-rereview); What was extracted…

### 5. TASK-208 — ClearFront: extract CSS+data module, establish multi-file skeleton
- ClearFront / clearfront-ui / RELEASED
- scope: Follow-on to TASK-207 (baseline extraction, APPROVED-pending-review). Per DEC-CF-002/DEC-CF-003 (Projects/ClearFront/shared/decisions.md) and the module map (Projects/ClearFront/artifacts/planning/clearfront-module-map-2026-07-16.md): split Projects/ClearFront/baseline/index.html into a directly-editable multi-file skeleton, starting with the…
- linked evidence:
  - `Projects/ClearFront/app/styles/clearfront.css` [implementation; current_shared; resolved] — 0b1020; 151c2f;
  - `Projects/ClearFront/artifacts/tests/task-208-skeleton-parity.md` [test; current_unique; resolved] — TASK-208 — Multi-File Skeleton Parity Report; What was done; Acceptance criteria checks; Visual parity (headless Chromium…

### 6. TASK-233 — Run a measured MAP kickoff-alignment practice scenario
- MAP / map-improvement / RELEASED
- scope: Exercise MAP from a project kickoff through an implementation-ready brief without changing product code or policy. Use a realistic coordination-surface scenario, distinct visible participant…
- linked evidence:
  - `MAP_System/artifacts/experiments/map-kickoff-alignment-scenario-2026-07-18.md` [artifact; current_unique; resolved] — MAP Kickoff-Alignment Practice Scenario; 0. Scenario purpose; 1. Shared project frame — v1 (frozen before participant…
  - `MAP_System/tasks/TASK-233.json` [task_scope; task_snapshot; resolved] — Run a measured MAP kickoff-alignment practice scenario Exercise MAP from a project kickoff through an implementation-ready…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1439

---

# TASK-260 Fresh Holdout Packet — N2

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: What implementation encrypts raw hcom transcripts at rest and automatically deletes each agent's transcript after a configurable retention period?
- algorithm signal: candidate_set (coverage 27%; supporting channels 3)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

What implementation encrypts raw hcom transcripts at rest and automatically deletes each agent's transcript after a configurable retention period?

## Candidates

### 1. TASK-226 — Discovery Agent pilot on completed ClearFront phase
- ClearFront / clearfront-delivery / APPROVED
- scope: Execute EXP-0003 using the operator-provided seven-pass, non-forcing Discovery Agent method. A new visible Codex helper performs proposal-only discovery over the completed ClearFront decomposition phase…
- linked evidence:
  - `MAP_System/artifacts/experiments/clearfront-discovery-agent-pilot-2026-07-17.md` [artifact; current_unique; resolved] — ClearFront Discovery Agent Pilot — Independent Output; Findings; Pass coverage and method note
  - `MAP_System/artifacts/experiments/clearfront-discovery-agent-adjudication-2026-07-17.md` [artifact; current_unique; resolved] — ClearFront Discovery Agent Pilot — Coordinator Adjudication; Verdict; Finding adjudication; Metrics **ADOPT WITH REFINEMENT.** The visible…

### 2. TASK-208 — ClearFront: extract CSS+data module, establish multi-file skeleton
- ClearFront / clearfront-ui / RELEASED
- scope: Follow-on to TASK-207 (baseline extraction, APPROVED-pending-review). Per DEC-CF-002/DEC-CF-003 (Projects/ClearFront/shared/decisions.md) and the module map (Projects/ClearFront/artifacts/planning/clearfront-module-map-2026-07-16.md): split Projects/ClearFront/baseline/index.html into a directly-editable multi-file skeleton, starting with the…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/screenshots/task208-app-after-champion-click.png` [test; current_unique; resolved] — test task208 app after champion click png
  - `Projects/ClearFront/app/index.html` [implementation; current_shared; resolved] — Clearfront — Champion Prototype Clearfront Rules Cards Log New Latest New game started. Undo Swap 1…

### 3. TASK-221 — RnS: persistent local session-limit supervisor
- MAP / agent-liveness-and-helpers / RELEASED
- scope: Operator-directed hardening after the 2026-07-17 Claude limit incident: make the existing deterministic RnS watcher self-sufficient when every cloud agent is exhausted. Detect fresh session-limit/reset…
- linked evidence:
  - `MAP_System/scripts/limit_watcher.py` [implementation; current_unique; resolved] — Rise & Shine (RnS) limit watcher: auto-resume agents after usage limits. symbols parse resume after; decide…
  - `MAP_System/tests/test_limit_watcher.py` [test; current_unique; resolved] — Tests for limit_watcher decision logic (TASK-080). symbols status; entry; test parse resume after; test fresh live…

### 4. TASK-223 — Operational learning promotion loop for startup orientation
- MAP / emergence-and-learning / APPROVED
- scope: Implement IDEA-0022/PROMO-0011: convert incident-derived operational notes into selectively promoted, canonical, scope-matched startup guidance. Reuse E/I as the capture and promotion funnel; do not create…
- linked evidence:
  - `MAP_System/scripts/operational_lessons.py` [implementation; current_unique; resolved] — Validate and project promoted operational lessons into startup context. symbols parse time; load store; validate; relevant…
  - `MAP_System/tests/test_operational_lessons.py` [test; current_unique; resolved] — symbols Operational Lesson Tests; test live store validates and routes fallback; test overdue lesson is marked…

### 5. TASK-235 — Create a current CommandCenter deployment-source manifest and provenance check
- MAP / command-center-ui / APPROVED
- scope: Turn TASK-234 parity evidence into a durable, read-only deployment-source manifest and repeatable runtime-provenance check. Preserve historical records as provenance, but make the current configured…
- linked evidence:
  - `MAP_System/tasks/TASK-235.json` [task_scope; task_snapshot; resolved] — Create a current CommandCenter deployment-source manifest and provenance check Turn TASK-234 parity evidence into a durable…
  - `MAP_System/artifacts/audits/command-center-deployment-source-manifest-2026-07-18.md` [artifact; current_unique; resolved] — CommandCenter Deployment-Source Manifest and Provenance Check; 0. Guardrail and method; 1. Configured launch chain (AC1); 2…

### 6. TASK-224 — Pilot local E/I sentinel and bounded curator queue
- MAP / command-center-ui / APPROVED
- scope: Implement EXP-0002 from reopened IDEA-0013. Build a token-free deterministic sentinel that reads durable MAP signals and writes non-promoted E/I candidates to a review queue…
- linked evidence:
  - `MAP_System/scripts/emergence_sentinel.py` [implementation; current_unique; resolved] — Deterministic E/I signal scanner and non-promoting candidate queue. symbols stamp; load events; detect; dedup key; existing…
  - `MAP_System/tests/test_emergence_sentinel.py` [test; current_unique; resolved] — symbols Emergence Sentinel Tests; test detects repeated rework and blockers; test scan deduplicates and never promotes…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1407

---

# TASK-260 Fresh Holdout Packet — N3

Generated retrieval aid; not authority. Use only this packet.
- corpus: 43 completed task records with linked source documents
- query parts: Where was a one-click automatic rollback mechanism implemented and tested for a failed CommandCenterUI deployment?
- algorithm signal: candidate_set (coverage 20%; supporting channels 4)
- watermark: 2026-07-19T19:27:55Z
- no strong match is a valid answer

## Query

Where was a one-click automatic rollback mechanism implemented and tested for a failed CommandCenterUI deployment?

## Candidates

### 1. TASK-235 — Create a current CommandCenter deployment-source manifest and provenance check
- MAP / command-center-ui / APPROVED
- scope: Turn TASK-234 parity evidence into a durable, read-only deployment-source manifest and repeatable runtime-provenance check. Preserve historical records as provenance, but make the current configured…
- linked evidence:
  - `MAP_System/tasks/TASK-235.json` [task_scope; task_snapshot; resolved] — Create a current CommandCenter deployment-source manifest and provenance check Turn TASK-234 parity evidence into a durable…
  - `MAP_System/artifacts/audits/command-center-deployment-source-manifest-2026-07-18.md` [artifact; current_unique; resolved] — CommandCenter Deployment-Source Manifest and Provenance Check; 0. Guardrail and method; 1. Configured launch chain (AC1); 2…

### 2. TASK-234 — Audit CommandCenter deployment-source parity before coordination-card implementation
- MAP / command-center-ui / RELEASED
- scope: Run the read-only, evidence-bounded deployment-source parity audit recommended by KICK-01. Establish which checkout or installer template actually updates the operator Command Center, identify any…
- linked evidence:
  - `MAP_System/artifacts/experiments/command-center-deployment-source-parity-audit-2026-07-18.md` [test; current_unique; resolved] — CommandCenter Deployment-Source Parity Audit; Purpose and guardrail; Method and evidence boundary; Candidate source and launch-path evidence…
  - `MAP_System/tasks/TASK-234.json` [task_scope; task_snapshot; resolved] — Audit CommandCenter deployment-source parity before coordination-card implementation Run the read-only, evidence-bounded deployment-source parity audit recommended by…

### 3. TASK-208 — ClearFront: extract CSS+data module, establish multi-file skeleton
- ClearFront / clearfront-ui / RELEASED
- scope: Follow-on to TASK-207 (baseline extraction, APPROVED-pending-review). Per DEC-CF-002/DEC-CF-003 (Projects/ClearFront/shared/decisions.md) and the module map (Projects/ClearFront/artifacts/planning/clearfront-module-map-2026-07-16.md): split Projects/ClearFront/baseline/index.html into a directly-editable multi-file skeleton, starting with the…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/screenshots/task208-app-after-champion-click.png` [test; current_unique; resolved] — test task208 app after champion click png
  - `Projects/ClearFront/app/index.html` [implementation; current_shared; resolved] — Clearfront — Champion Prototype Clearfront Rules Cards Log New Latest New game started. Undo Swap 1…

### 4. TASK-237 — Add operator reply popup queue to CommandCenterUI
- MAP / command-center-ui / APPROVED
- scope: Add a keyboard-accessible AIM-style overlay that presents only new unanswered operator-directed hcom requests, approval gates, and terminal prompts. Preserve existing attention inbox and reply_to…
- linked evidence:
  - `MAP_System/artifacts/tests/task237-attention-popup.md` [test; current_unique; resolved] — TASK-237 CommandCenterUI Attention Popup Verification; Delivered; Verification approval gates, and terminal prompts one at a time.
  - `MAP_System/templates/install/command-center-ui/src/chat.html` [implementation; current_shared; resolved] — AI Command Center Start lab Attention needed 0 In the room 0 Refresh usage MAP status…

### 5. TASK-217 — ClearFront: add category artwork and detail-on-preview card faces
- ClearFront / clearfront-ui / RELEASED
- scope: Operator-requested presentation improvement after decomposition. Generate three original bitmap category artworks (Unit, Spell, Relic). Compact card faces show cost/name/art/category/stats while full rules text, keywords…
- linked evidence:
  - `Projects/ClearFront/artifacts/tests/task-217-card-art-preview.md` [test; current_unique; resolved] — TASK-217 — Category Artwork and Detail-on-Preview Evidence; Result; Image prompts; Design-review checklist Compact hand/board cards now…
  - `Projects/ClearFront/app/assets/card-relic.png` [implementation; current_unique; resolved] — implementation card relic png

### 6. TASK-223 — Operational learning promotion loop for startup orientation
- MAP / emergence-and-learning / APPROVED
- scope: Implement IDEA-0022/PROMO-0011: convert incident-derived operational notes into selectively promoted, canonical, scope-matched startup guidance. Reuse E/I as the capture and promotion funnel; do not create…
- linked evidence:
  - `MAP_System/scripts/operational_lessons.py` [implementation; current_unique; resolved] — Validate and project promoted operational lessons into startup context. symbols parse time; load store; validate; relevant…
  - `MAP_System/tests/test_operational_lessons.py` [test; current_unique; resolved] — symbols Operational Lesson Tests; test live store validates and routes fallback; test overdue lesson is marked…

## Required response

Return one line: `query ID | up to two TASK IDs or NO MATCH | up to
three source paths | confidence high/medium/low | concise reasoning`.
State ambiguity and whether anything outside this packet was accessed.
- estimated packet tokens: 1411

---
