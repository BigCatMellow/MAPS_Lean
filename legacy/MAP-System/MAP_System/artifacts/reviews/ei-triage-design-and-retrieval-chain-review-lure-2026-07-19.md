# Cross-Model Review — E/I + Triage design and Codex retrieval chain

reviewer: claude-lab-lure
date: 2026-07-19
scope: operator design doc `conversation_notes.md` (E/I + Triage) and Codex's
  TASK-255 intake + TASK-256..262 retrieval experiment chain.
type: design-fidelity + findings review (NOT a full evidence-reproduction of the
  measured recall numbers — those were run under Codex's blinded holdout harness
  and are taken as reported; see limits).

## Verdict

The design is sound and Codex's execution is faithful, rigorous, and correctly
restrained (no integration, no embeddings-yet, negative results preserved).
Two substantive gaps to surface to the operator: (1) the Triage half is
under-built relative to the E/I retrieval half; (2) the measured
evidence-recall shortfall is the design's own predicted "compression erases
detail" weakness, now confirmed — it is the real adoption blocker.

## What the design asks for

Two systems sharing records but operating differently: E/I (long-range
cross-task synthesis over a hierarchical memory: full archive -> task
fingerprint -> workstream digest -> insight ledger, searched-not-loaded) and
Triage (live operational awareness: explicit task-state model, explainable
wait/incident envelope, graduated authority observe->recommend->intervene->
escalate). Stated central risk: compression can erase the detail a future
connection depends on.

## Codex fidelity assessment

- TASK-255 intake: CORRECT reframing as a "missing middle layer," properly
  bounded (subordinate to map.db/decisions/artifacts; external citations not
  independently validated; no authority created). Faithful to intent.
- TASK-256..262: built and stress-tested the E/I RETRIEVAL half — task
  fingerprints -> FTS5/BM25 + RRF -> blinded frozen holdouts with temporal-leak
  controls. Discipline is exemplary and matches MAP's own experiment norms.
- KEY RESULT: the chain empirically CONFIRMED the design's central worry.
  Task-label recall reached 100%, but exact-EVIDENCE recall lagged (37.5%->60%
  ->75% across runs). "Find the right task" is solved; "find the load-bearing
  evidence" is not. Codex correctly ruled it NOT safe to integrate and correctly
  deferred embeddings (first-stage recall already saturated).

## Gaps to surface

1. **Triage half under-built.** The design weights E/I and Triage as co-equal;
   the chain invested almost entirely in retrieval. The explainable
   wait/incident envelope, the WAITING_ON_* state model, and graduated authority
   remain conceptual (captured in the intake note, not implemented or tested).
   Given retrieval's task-recall is already saturated, the higher-marginal-value
   next step is the triage envelope, not more retrieval tuning. See INS-0034.
2. **Evidence-recall is the adoption blocker, and it is dangerous for E/I
   specifically.** E/I draws connections; if it retrieves the right task but the
   wrong/missing evidence, it will synthesize from summaries lacking the
   load-bearing detail — the exact failure the design warns about. Any future
   adoption gate must hold on evidence recall, not task recall.
3. **Untested design safeguard:** the doc's "deliberate randomness / sample old
   non-similar records" guard against missing remote connections was not
   exercised (lexical-only chain). Future work if/when synthesis breadth matters.

## Coordination-process note

This substantial body of Codex work (a design + 8 experiment tasks) had no
cross-model review until now because the reviewing core agent (me) treated the
chain as background informs while focused on another workstream. That is itself
a coordination gap: large autonomous chains should get at least a lightweight
independent review checkpoint, not only per-task self-verification.

## Limits

Design-fidelity + findings review only. The recall/precision figures are read
from Codex's holdout reports, not independently reproduced. A deeper pass would
re-run the frozen holdout harness against the reported numbers.
