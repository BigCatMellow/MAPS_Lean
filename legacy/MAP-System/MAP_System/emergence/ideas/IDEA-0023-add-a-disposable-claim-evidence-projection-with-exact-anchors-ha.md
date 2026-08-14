# Idea Card

Idea ID: IDEA-0023
Project: MAP
Source insight or synthesis: SYN-0003
Owner: codex-lab-kiri
Date: 2026-07-19
Status: CANDIDATE

## Idea


- idea: Add a disposable claim-evidence projection with exact anchors, hashes, watermarks, and a separate boundary channel.

## Problem or opportunity


- gap: Whole-file retrieval finds relevant documents but does not reliably identify the exact claim, section, code symbol, negative boundary, or historical version that answers a question.

## Why now


- now: The capsule pilot reached 18/20 exact sources and fresh-task recall is already 12/12, making the residual failure modes visible enough for a targeted experiment.

## Expected benefit


- gain: Potentially improve exact-source and abstention performance while keeping packets compact and avoiding an embedding service or full knowledge graph.

## Cost


- cost: Requires claim labels, section or symbol extraction, source hashes and watermarks, separate boundary handling, and a better independently authored evaluation set.

## Reversibility

- [x] yes — the pilot is a disposable, read-only projection over existing sources
- [ ] no
- [ ] partial:

## Smallest safe experiment


- test: For a bounded completed-task holdout, freeze independently authored questions and acceptable evidence sets before treatment; then create disposable claim cards pointing to exact Markdown sections or code symbols, include proof role and source hash, store negative boundaries separately, and rerun the frozen questions plus hard negatives.

## Decision needed

- [x] task-DRI — only if the proposed experiment is admitted
- [x] review-DRI — freeze labels and evaluate without treatment leakage
- [ ] state-steward
- [ ] project-DRI
- [ ] human-owner

## Recommendation

- [ ] park
- [ ] reject
- [x] test — proposal recorded as `EXP-0006`; not yet approved or running
- [ ] promote-task

## Constraints

- Claim cards are retrieval aids, never task or policy authority.
- Positive proof and negative boundaries are stored and scored separately.
- A hash detects changed content; retained historical content is needed to answer historical-state questions.
- Semantic expansion, learned reranking, embeddings, and a full knowledge graph remain outside the first experiment.
