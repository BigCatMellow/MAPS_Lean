# Insight Record

Insight ID: INS-0061
Project: MAP
Related task: TASK-294
Detected by: claude-lab-luzo
Date: 2026-08-04
Status: RAW

## Short description


- obs: emergence_sentinel.py's repeated_rework signal records evidence_refs line numbers that do not match the actual CHANGES_REQUESTED events they claim to cite

## Trigger


- src: CAND-C2944006C52D8A50 claimed TASK-294 had CHANGES_REQUESTED events at events.jsonl lines 5270 and 9636. Reading those lines directly showed unrelated TASK-083 PROGRESS entries (RnS resume-window messages), not CHANGES_REQUESTED events at all. Same for CAND-CAF97DE6F92ACD3A (TASK-310, claimed lines 9570/9587/9609, also unrelated TASK-083 PROGRESS entries). Searching events.jsonl directly found the real CHANGES_REQUESTED events at completely different line numbers (5326, 9692 for TASK-294; 9626, 9643, 9665 for TASK-310).

## The synthesis


- synth: The repeated_rework signal_type's underlying count (N changes-requested events for a task) appears correct -- both tasks genuinely had repeated rework -- but the evidence_refs line numbers recorded alongside it do not correspond to that count's source events. A curator trusting evidence_refs without independently re-searching the file would investigate the wrong events entirely, potentially reaching a false conclusion about what caused the rework.

## Why it might matter


- why: This is the second distinct evidence-integrity bug found in emergence_sentinel.py this quarter (see [[emergence/insights/INS-0050-emergence-sentinel-py-s-repeated-blocker-signal-miscounts-operat]] for the repeated_blocker task-id misattribution bug). Unlike [[emergence/insights/INS-0050-emergence-sentinel-py-s-repeated-blocker-signal-miscounts-operat]] (wrong task attributed to real events), this is worse: the events themselves are wrong, not just their attribution -- undermines the specific guarantee curation depends on (evidence_refs point at real, checkable evidence).

## Evidence


- ev: MAP_System/events/events.jsonl: candidates' claimed lines (5270, 9636, 9570, 9587, 9609) vs actual CHANGES_REQUESTED lines found by direct search (5326, 9692, 9626, 9643, 9665), 2026-08-04.

## Risk


- risk: Acting without promotion could bypass HPOM governance. Separately: continuing to trust unverified evidence_refs from this scanner risks future curation decisions being made against the wrong evidence.

## Scope


- scope: Any future repeated_rework candidate from this scanner -- its evidence_refs need independent verification (re-search events.jsonl by task_id+type) before being relied on, until the underlying line-indexing bug is found and fixed.

## Recommended next action

- [ ] ignore
- [ ] park
- [ ] task
- [ ] idea
- [ ] experiment
- [ ] escalate-human

## Notes

- note: CAND-C2944006C52D8A50 and CAND-CAF97DE6F92ACD3A (the candidates that
  surfaced this) were already correctly curated by codex-lab-vumo on
  2026-08-01, three days before this insight was written -- that curation
  sat uncommitted on Smalls and never reached Biggie, so this session's scan
  re-created and re-curated them independently, overwriting vumo's better,
  more substantive resolutions (TASK-294 -> INS-0060, TASK-310 -> merged
  into INS-0058/059) with a less-informed one citing this insight instead.
  Corrected: vumo's original curation has been restored as authoritative for
  those two candidates. This insight stands on its own merit (the
  evidence_refs bug is real and independent of that mistake) but is not
  itself the resolution for either candidate.
