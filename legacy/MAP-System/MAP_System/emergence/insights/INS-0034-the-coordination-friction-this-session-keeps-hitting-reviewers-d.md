# Insight Record

Insight ID: INS-0034
Project: MAP
Related task: NONE
Detected by: claude-lab-lure
Date: 2026-07-19
Status: OPEN

## Short description


- obs: The coordination friction this session keeps hitting (reviewers dropping mid-review, stranded/duplicate reviews, RnS nudging live sessions, unexplained waits) IS the problem the operator triage design addresses. The triage half of that design is under-built vs the E/I retrieval half, so the next coordination investment should be the explainable wait/incident envelope, not more retrieval tuning.

## Trigger


- src: Reviewing conversation_notes.md (E/I + Triage design) against Codex TASK-255..262: the chain thoroughly built and stress-tested the E/I RETRIEVAL half but left the TRIAGE half (task-state model, explainable wait/incident envelope, graduated authority) conceptual. Meanwhile this session repeatedly hit the exact triage failures the design names: lilo and hana dropping mid-review (stranded review requests hcom #5600/#6035/#8567), near-duplicate reviews, RnS nudging live sessions.

## The synthesis


- synth: The coordination friction this session keeps hitting (reviewers dropping mid-review, stranded/duplicate reviews, RnS nudging live sessions, unexplained waits) IS the problem the operator triage design addresses. The triage half of that design is under-built vs the E/I retrieval half, so the next coordination investment should be the explainable wait/incident envelope, not more retrieval tuning.

## Why it might matter


- why: This is the cross-task connection E/I exists to surface: a designed-but-unbuilt capability directly addresses a currently-recurring, operator-visible friction, and it rebalances priority. Codex holdouts show task retrieval already works (100 percent task recall) while exact-evidence recall lags (about 75 percent), so more retrieval tuning has diminishing returns; the triage envelope is unbuilt and would remove active coordination cost. This is the same problem as G2 (liveness truth) in the MAP improvement kickoff.

## Evidence


- ev: conversation_notes.md sections 2-3 (triage state model plus explainable wait envelope); Codex TASK-255 intake note ([[artifacts/planning/conversation-notes-ei-triage-intake-2026-07-19]]); TASK-260/261 holdout reports (task recall 100 percent, exact-source recall 75 percent); this session stranded-review re-routes (lilo twice, then hana) and RnS false-positive informs; [[emergence/promotions/PROMO-0012-idea-0024]] review was itself stranded twice by this friction.

## Risk


- risk: Acting without promotion could bypass HPOM governance.

## Scope


- scope: Only the files and artifacts named in this record.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note:
