# TASK-263 Claim-Evidence Retrieval Pilot — Development Report

Experiment evidence only (EXP-0006 / TASK-263). No production authority.

- Holdout: `MAP_System/artifacts/experiments/task-memory-claim-evidence-holdout-2026-07-19.json` (sha256 verified: 635aa5f0b41bdded...)
- Claim cards built: 1392 over 94 corpus tasks, 247 linked paths
- Task recall: 12/23 (0.5217)
- Exact-source accuracy: 17/41 (0.4146)
- Anchored-evidence accuracy: 7/41 (0.1707)
- Acceptable-substitute hits (a legitimate alternate source was actually retrieved): 1
- Source-hash drift since freeze: 5 drifted, 0 missing, of 29 checked  <-- anchors were frozen against different bytes
- Abstention (negatives correctly abstained): 2/5, false positives: 3
- Historical-version correctness: 2/3
- Median selection time: 8.5908 ms

Baselines to beat (recorded in the frozen holdout): exact-source 18/20, task recall 12/12.
