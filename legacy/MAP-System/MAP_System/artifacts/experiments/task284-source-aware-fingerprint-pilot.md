# TASK-284 Source-Aware Fingerprint Pilot

- task_id: TASK-284
- status: completed_offline_pilot
- generated_at: 2026-07-26T19:31:58+00:00
- holdout: TASK-258-source-holdout-subset-frozen-2026-07-19
- frozen_holdout_sha256: `73ce9fbaf346c906cfadb208c1b6f3bff15a83afb6c4830961191089868404b4`

## Boundary

This is a rebuildable retrieval projection, not canonical MAP truth. Every
returned task has raw source backlinks and `raw_evidence_required: true`.
Missing source state is preserved rather than inferred away. Release eligibility
is checked against task JSON, read-only canonical SQLite, and the task-graph
mirror. When any source identifies a release candidate, missing or
non-`RELEASED` status in any other source is recorded as a structured
contradiction and excluded from searchable candidates. The pilot does not
modify startup, runner routing, Command Center behavior, or task authority.

## Predeclared thresholds

- Promotion is prohibited in this task regardless of score.
- A future proposal requires task recall >= 0.90, primary-source recall >= 0.80,
  negative abstention accuracy == 1.00, and a separate independent review.
- Failure of any threshold, a missing/contradictory primary source, or inability
  to preserve backlinks means retain the projection as an experiment only.

## Frozen Evaluation

| Metric | Result |
|---|---:|
| released task records indexed | 144 |
| contradictory release records excluded | 0 |
| task recall | 33.33% |
| primary-source recall | 33.33% |
| negative abstention accuracy | 0.00% |
| raw context bytes | 12755816 |
| fingerprint context bytes | 986663 |
| context-byte reduction | 92.26% |

Only the holdout queries and expectations are frozen. The evidence corpus and
both byte counts are point-in-time measurements from this report generation;
they may change as canonical source files evolve while the holdout hash remains
stable.

## Results by Frozen Query

```json
[
  {
    "abstained": false,
    "expected_sources": [
      "MAP_System/scripts/validate_research_artifacts.py",
      "MAP_System/tests/test_validate_research_artifacts.py"
    ],
    "expected_tasks": [
      "TASK-104"
    ],
    "id": "S1",
    "returned_primary_sources": [
      "MAP_System/CHANGE_CONTROL_SYSTEM.md",
      "MAP_System/RESEARCH_SYSTEM.md",
      "MAP_System/db/claims.py",
      "MAP_System/notes/review-guide.md",
      "MAP_System/notes/task-authoring-guide.md",
      "MAP_System/research/README.md",
      "MAP_System/templates/README.md",
      "MAP_System/templates/RETROSPECTIVE_TEMPLATE.md",
      "MAP_System/tests/test_review_claims.py"
    ],
    "returned_tasks": [
      "TASK-103",
      "TASK-118",
      "TASK-270"
    ]
  },
  {
    "abstained": false,
    "expected_sources": [
      "MAP_System/graph/runner.py",
      "MAP_System/tests/test_runner_task_classification.py"
    ],
    "expected_tasks": [
      "TASK-116"
    ],
    "id": "S2",
    "returned_primary_sources": [
      "MAP_System/artifacts/tests/release-gate-test.md",
      "MAP_System/emergence/ideas/IDEA-0005-add-a-release-path-smoke-checklist-for-user-facing-packages.md",
      "MAP_System/emergence/insights/INS-0016-validator-coverage-must-include-live-command-surfaces-not-only-d.md",
      "MAP_System/emergence/promotions/PROMO-0001-task-052-emergence-cli.md",
      "MAP_System/notes/system-improvement-implementation-plan.md",
      "MAP_System/templates/release-checklist.md",
      "MAP_System/tests/test_release_gate.py"
    ],
    "returned_tasks": [
      "TASK-038",
      "TASK-181",
      "TASK-227"
    ]
  },
  {
    "abstained": false,
    "expected_sources": [
      "MAP_System/scripts/validate_task_mirrors.py",
      "MAP_System/tests/test_validate_task_mirrors.py"
    ],
    "expected_tasks": [
      "TASK-143"
    ],
    "id": "S5",
    "returned_primary_sources": [
      "MAP_System/migration/export_to_files.py",
      "MAP_System/scripts/map_task.py",
      "MAP_System/scripts/run_tests.sh",
      "MAP_System/scripts/validate_layer1.py",
      "MAP_System/scripts/validate_task_graph.py",
      "MAP_System/scripts/validate_task_mirrors.py",
      "MAP_System/tests/test_validate_task_graph_shared_outputs.py",
      "MAP_System/tests/test_validate_task_mirrors.py",
      "MAP_System/workflow/runtime_policy.yaml"
    ],
    "returned_tasks": [
      "TASK-101",
      "TASK-143",
      "TASK-201"
    ]
  },
  {
    "abstained": false,
    "expected_sources": [],
    "expected_tasks": [],
    "id": "S9",
    "returned_primary_sources": [
      "MAP_System/artifacts/README.md",
      "MAP_System/artifacts/command-center-ui/README.md",
      "MAP_System/artifacts/planning/emergence-local-librarian-report.md",
      "MAP_System/artifacts/releases/README.md",
      "MAP_System/emergence/synthesis/SYN-0001-two-readers-one-truth.md",
      "MAP_System/emergence/templates/INSIGHT_TEMPLATE.md",
      "MAP_System/emergence/templates/PROMOTION_RECORD_TEMPLATE.md",
      "MAP_System/scripts/local_runner.py",
      "MAP_System/scripts/map_emergence.py"
    ],
    "returned_tasks": [
      "TASK-121",
      "TASK-180",
      "TASK-181"
    ]
  }
]
```

## TASK-256 Comparison

TASK-256 reported 100% task recall@6 but 68.75% primary-source recall on its
curated 16-source experiment. This stricter source-aware pilot reports task
and primary-source recall separately, includes a genuine negative query that
exposed a false positive (zero abstention accuracy), and returns primary-source
backlinks rather than treating a task hit as proof. Its scores are not
comparable as a production claim because the frozen holdout and corpus differ.

## Decision

Do not promote or enable default production routing. Treat this report and the
script as an offline measurement harness until repeated independent holdouts
meet the thresholds and a separate task authorizes integration.
