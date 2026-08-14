# Insight Record

Insight ID: INS-0030
Project: MAP
Related task: TASK-262
Detected by: codex-lab-kiri
Date: 2026-07-19
Status: CLARIFIED

## Short description


- obs: Retrieval failures now cluster at claim-to-evidence alignment and temporal attribution, not task recall.

## Trigger


- src: TASK-260 through TASK-262 improved fresh-task recall to 12/12 and exact-source retrieval to 18/20, while the remaining misses involved exact proof location, non-Markdown code, negative boundaries, or historical source state.

## The synthesis


- synth: The retrieval bottleneck has moved from finding the right task to resolving which exact claim a source proves, where that proof lives inside the source, and what version of the source existed at the task watermark.

## Why it might matter


- why: Improving claim-to-evidence alignment can raise precision and temporal correctness without paying the token and dependency cost of broad semantic retrieval.

## Evidence


- ev: `artifacts/experiments/task-memory-evidence-verifier-development-2026-07-19.md` measured 16/20 exact-source selections after fresh-task recall had reached 12/12.
- ev: `artifacts/experiments/task-memory-capsule-development-2026-07-19.md` measured 18/20 exact-source selections with six structured capsules. Its remaining misses exposed source-type and evidence-location gaps rather than failure to recall the task.
- ev: The negative verifier trial correctly handled 3/3 explicit negatives but reduced positive-source accuracy, showing that positive proof and limitation language need separate treatment rather than one blended relevance score.

## Risk


- risk: Treating summaries or negative-boundary text as positive evidence can create confident but wrong source selections; current files can also drift after task completion.

## Scope


- [ ] current-task
- [x] adjacent
- [x] project
- [x] MAP-system

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [x] experiment
- [ ] escalate-human

## Notes

- note: This insight does not say lexical retrieval is exhausted. It says the next lexical improvement should operate below the whole-file level and above the raw token level: claims, sections, symbols, proof roles, and historical versions.
- note: No production or policy change is authorized by this record.
