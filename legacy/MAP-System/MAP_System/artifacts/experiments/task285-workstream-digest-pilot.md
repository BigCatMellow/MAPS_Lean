# TASK-285 Evidence-Linked Workstream Digest Pilot

- task_id: TASK-285
- generated_at: 2026-07-27T18:25:16+00:00
- workstream_id: map-task-lifecycle-integrity
- mode: offline_disposable_projection
- canonical: false
- production_routing_enabled: false
- frozen_evaluation_sha256: `f94aef8b207a37cff9cd90a583351672b713a4be48121c42e1eb04f56c1816d9`

## Eligibility

The predeclared threshold is 5 related tasks whose task JSON,
read-only SQLite status, and task-graph status all agree on `RELEASED`. This
single bounded workstream has 5
verified released tasks and eligibility is
`true`.

## Evidence Boundary

This digest is a retrieval projection, never task, decision, or project truth.
Every retained fact links to hashed raw evidence, and
`raw_evidence_required: true`. Missing, stale, anchor-missing, or contradictory
evidence is surfaced in `evidence_issues`; unsupported claims are withheld.

## Digest

```json
{
  "canonical": false,
  "decisions": [
    {
      "backlinks": [
        {
          "anchor": "DEC-003: One Owner Per Active Task",
          "expected_sha256": null,
          "kind": "decision",
          "path": "MAP_System/shared/decisions.md",
          "sha256": "ec783566927247606a0e94c3b1d19752070111f5ed263dc5d2096206f24721b7",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "decision",
      "id": "decision-one-owner",
      "statement": "One accountable owner is required for each active task."
    },
    {
      "backlinks": [
        {
          "anchor": "DEC-009: SQLite Is The Task Claiming Coordinator",
          "expected_sha256": null,
          "kind": "decision",
          "path": "MAP_System/shared/decisions.md",
          "sha256": "ec783566927247606a0e94c3b1d19752070111f5ed263dc5d2096206f24721b7",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "decision",
      "id": "decision-sqlite-claim-authority",
      "statement": "SQLite is the canonical coordinator for atomic task claims."
    }
  ],
  "eligibility": {
    "declared_related_tasks": [
      "TASK-143",
      "TASK-199",
      "TASK-266",
      "TASK-270",
      "TASK-273"
    ],
    "eligible": true,
    "minimum_related_released_tasks": 5,
    "verified_released_tasks": 5
  },
  "evidence_issues": [
    {
      "kind": "missing_submission_evidence",
      "path": "MAP_System/events/events.jsonl",
      "task_id": "TASK-199"
    }
  ],
  "key_files": {
    "backlinks": [
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/db/claims.py",
        "sha256": "95b4b18225a7262d5e69c72195ca717eced430ae43e9784b8a5646c9cddc23e4",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/scripts/map_task.py",
        "sha256": "43239c76f34922e7ca489892e26162b38cc217dbdea4020c70a8de3a77bd71ef",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/scripts/validate_task_mirrors.py",
        "sha256": "0b263ffc045c68c49a8a3f0c2eefd19d6c90b26211e777eee344e5fcf0f611c0",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/notes/review-guide.md",
        "sha256": "87cc8f7c9bd44cfbc660a53e29ca754091276ccbb6210a6c48318fdbb9cb0e31",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/tests/test_recover_orphan.py",
        "sha256": "c8c260752bca7164d827f30a597ddb71dc31d428a6b683e8cf44c69e57e072ce",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/tests/test_reassign_owner.py",
        "sha256": "0883c42756ed5a7dccde48841e71f357a3bb64a11b2632c7bd02f287aee5a0b4",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/tests/test_review_claims.py",
        "sha256": "76dea89461cf5b4ed32db8f4f3510491649bb76ee446912fa0b715dd00f23122",
        "source_type": "file",
        "state": "available"
      },
      {
        "anchor": null,
        "expected_sha256": null,
        "kind": "key_file",
        "path": "MAP_System/tests/test_validate_task_mirrors.py",
        "sha256": "42885fa74f285d5fc62ba1d91d0f8ae426f22a7c4226852a3b9a88a24b4129e1",
        "source_type": "file",
        "state": "available"
      }
    ],
    "id": "key-files",
    "statement": "Files repeatedly changed or relied on by this workstream."
  },
  "mode": "offline_disposable_projection",
  "open_risks": [
    {
      "backlinks": [
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "open_risk",
          "path": "MAP_System/tasks/TASK-274.json",
          "sha256": "3882d4522487103e64ac0924c7dd121dd7c3cc8a774e2cdb970f10535d167b38",
          "source_type": "file",
          "state": "available"
        }
      ],
      "id": "risk-submission-authorship",
      "statement": "Durable submission authorship and author-keyed review separation remain unfinished.",
      "status": {
        "sqlite": "APPROVED",
        "task_graph": "APPROVED",
        "task_json": "APPROVED"
      },
      "task_id": "TASK-274"
    }
  ],
  "production_routing_enabled": false,
  "raw_evidence_required": true,
  "repeated_failures": [
    {
      "backlinks": [
        {
          "anchor": "manual SQLite/file sync drift",
          "expected_sha256": null,
          "kind": "repeated_failure",
          "path": "MAP_System/tasks/TASK-143.json",
          "sha256": "0007fd1d4f8bdb0895f44b8b9f853cc8358e04a1675aacdb74fd238f8d77f470",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "repeated_failure",
      "id": "failure-mirror-drift",
      "statement": "Manual SQLite, task-file, and task-graph synchronization drift required a reconciliation gate."
    },
    {
      "backlinks": [
        {
          "anchor": "duplicated review effort",
          "expected_sha256": null,
          "kind": "repeated_failure",
          "path": "MAP_System/tasks/TASK-199.json",
          "sha256": "c9ab095c76dd11b43faca198dfe71ebbd37570ebd78c1ef559265a55f5b84bdd",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "repeated_failure",
      "id": "failure-duplicate-review-work",
      "statement": "Independent reviewers duplicated full reviews before atomic review claiming existed."
    },
    {
      "backlinks": [
        {
          "anchor": "structurally unreachable",
          "expected_sha256": null,
          "kind": "repeated_failure",
          "path": "MAP_System/tasks/TASK-266.json",
          "sha256": "4390802e45402fa86718d4b5ab3368ffa72792b9bbbe050e0d8c5367da1cbfb1",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "repeated_failure",
      "id": "failure-orphaned-task",
      "statement": "An IN_PROGRESS task with no claimant or lease was structurally unreachable by sanctioned recovery paths."
    },
    {
      "backlinks": [
        {
          "anchor": "false negative",
          "expected_sha256": null,
          "kind": "repeated_failure",
          "path": "MAP_System/tasks/TASK-270.json",
          "sha256": "a1754e431f5abbef421ed70ad7ca8adf64370387106b5f3c936330c0b15695a8",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "repeated_failure",
      "id": "failure-reviewer-false-negative",
      "statement": "An unregistered reviewer was falsely told an open review was already claimed."
    },
    {
      "backlinks": [
        {
          "anchor": "permanent and unfixable",
          "expected_sha256": null,
          "kind": "repeated_failure",
          "path": "MAP_System/tasks/TASK-273.json",
          "sha256": "1955e5f22b43535292701063e5cc17ea85d854962eb331064205946b7ae44ee2",
          "source_type": "file",
          "state": "available"
        }
      ],
      "category": "repeated_failure",
      "id": "failure-stale-owner",
      "statement": "Owner identity became permanent and unsanctioned to repair after agents disappeared."
    }
  ],
  "schema_version": 1,
  "tasks": [
    {
      "backlinks": [
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "released_task",
          "path": "MAP_System/tasks/TASK-143.json",
          "sha256": "0007fd1d4f8bdb0895f44b8b9f853cc8358e04a1675aacdb74fd238f8d77f470",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": "jsonl_line:689",
          "event_sha256": "6fb6f2759434654560a030ea05e9d3dbe1514e9805a455dbd8b27449ad242aa1",
          "kind": "submission",
          "path": "MAP_System/events/events.jsonl",
          "sha256": "81d7da8cab43a92a91277f9796b055c8fe5e5d961e881b6c9a2ae938a335744a",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task143-review-magi.md",
          "sha256": "baa6d9402bdda73b3291b3866fbc96ffc95dec710f85597b7694fae68a7c3e43",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/artifacts/reports/task-143-systems-use-note.md",
          "sha256": "9db277bc284a560f070a8cc063f04811c5bb0a898430cef403aa0986ed88a391",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/map_task.py",
          "sha256": "43239c76f34922e7ca489892e26162b38cc217dbdea4020c70a8de3a77bd71ef",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/release_task.py",
          "sha256": "f945fda6164726a9f709638b271f5d033f206b1587045baa10f03f912b518f44",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/run_tests.sh",
          "sha256": "e95ebcd945b393d26e6ebe2bb318708a8ce6221308abc149c3626abe14ff546c",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/validate_task_mirrors.py",
          "sha256": "0b263ffc045c68c49a8a3f0c2eefd19d6c90b26211e777eee344e5fcf0f611c0",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/shared/current-state.md",
          "sha256": "68ed1155d1961e1e909f31a5df2297adde169c78be0384d77bc934ff0b3cb1f8",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/shared/improvement-backlog.md",
          "sha256": "37d0f614b76ef18450b5c1fc8f66537d0411c8db9a11c6ed7bb330fa7aae979b",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tasks",
          "sha256": "2e63590c12f64729ac8331522e50d6a40725a5f3db34823149e5b469f6258642",
          "source_type": "directory_manifest",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_release_gate.py",
          "sha256": "80dd8badc28b67144c1fb302a5228d1ee5f47285f5d875aca0a60b2f16af4f5f",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_review_gate.py",
          "sha256": "f3d090e351ebf1c503bf586d4ecafc0e64379cded73cf5e70c22ca94c47a45ae",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_validate_task_mirrors.py",
          "sha256": "42885fa74f285d5fc62ba1d91d0f8ae426f22a7c4226852a3b9a88a24b4129e1",
          "source_type": "file",
          "state": "available"
        }
      ],
      "lifecycle": {
        "contradictory": false,
        "missing_sources": [],
        "released": true,
        "statuses": {
          "sqlite": "RELEASED",
          "task_graph": "RELEASED",
          "task_json": "RELEASED"
        }
      },
      "task_id": "TASK-143",
      "title": "Add task-state mirror reconciliation gate"
    },
    {
      "backlinks": [
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "released_task",
          "path": "MAP_System/tasks/TASK-199.json",
          "sha256": "c9ab095c76dd11b43faca198dfe71ebbd37570ebd78c1ef559265a55f5b84bdd",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task199-review-mira.md",
          "sha256": "f73c28e4b2d71892f260d5f1690e7aa0e327f5b0e0a4126a64c308b218e845c8",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/db/claims.py",
          "sha256": "95b4b18225a7262d5e69c72195ca717eced430ae43e9784b8a5646c9cddc23e4",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/migration/schema.sql",
          "sha256": "299b329b3597d8c5c7cc75935fbd64f8d59fb3fd2f76580acac5990205a3afa9",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/notes/review-guide.md",
          "sha256": "87cc8f7c9bd44cfbc660a53e29ca754091276ccbb6210a6c48318fdbb9cb0e31",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/run_tests.sh",
          "sha256": "e95ebcd945b393d26e6ebe2bb318708a8ce6221308abc149c3626abe14ff546c",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_review_claims.py",
          "sha256": "76dea89461cf5b4ed32db8f4f3510491649bb76ee446912fa0b715dd00f23122",
          "source_type": "file",
          "state": "available"
        }
      ],
      "lifecycle": {
        "contradictory": false,
        "missing_sources": [],
        "released": true,
        "statuses": {
          "sqlite": "RELEASED",
          "task_graph": "RELEASED",
          "task_json": "RELEASED"
        }
      },
      "task_id": "TASK-199",
      "title": "Atomic review claiming (claim_review in db/claims.py)"
    },
    {
      "backlinks": [
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "released_task",
          "path": "MAP_System/tasks/TASK-266.json",
          "sha256": "4390802e45402fa86718d4b5ab3368ffa72792b9bbbe050e0d8c5367da1cbfb1",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": "jsonl_line:2292",
          "event_sha256": "cfc3943a30b240c44b8511b2f5364878db7027bdf3511e64718645ebc1a46be1",
          "kind": "submission",
          "path": "MAP_System/events/events.jsonl",
          "sha256": "81d7da8cab43a92a91277f9796b055c8fe5e5d961e881b6c9a2ae938a335744a",
          "state": "available"
        },
        {
          "anchor": "jsonl_line:2310",
          "event_sha256": "5180f6ea8c2b65f8a800a994cf4a64f0edbb252df0ec23ce32c828dbbb73e318",
          "kind": "submission",
          "path": "MAP_System/events/events.jsonl",
          "sha256": "81d7da8cab43a92a91277f9796b055c8fe5e5d961e881b6c9a2ae938a335744a",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task266-final-review-lime.md",
          "sha256": "5619594b80b7655e08197b3882035ec946c942ec03416847b1e89ddc0f2fdd0b",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task266-review-lime.md",
          "sha256": "11932f3671ce879c6a1b518dd05bbd02c0cb8921af7f444c420f912bf4970c03",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/db/claims.py",
          "sha256": "95b4b18225a7262d5e69c72195ca717eced430ae43e9784b8a5646c9cddc23e4",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/map_task.py",
          "sha256": "43239c76f34922e7ca489892e26162b38cc217dbdea4020c70a8de3a77bd71ef",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/run_tests.sh",
          "sha256": "e95ebcd945b393d26e6ebe2bb318708a8ce6221308abc149c3626abe14ff546c",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_recover_orphan.py",
          "sha256": "c8c260752bca7164d827f30a597ddb71dc31d428a6b683e8cf44c69e57e072ce",
          "source_type": "file",
          "state": "available"
        }
      ],
      "lifecycle": {
        "contradictory": false,
        "missing_sources": [],
        "released": true,
        "statuses": {
          "sqlite": "RELEASED",
          "task_graph": "RELEASED",
          "task_json": "RELEASED"
        }
      },
      "task_id": "TASK-266",
      "title": "Add a sanctioned recovery path for orphaned IN_PROGRESS tasks with no claimant"
    },
    {
      "backlinks": [
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "released_task",
          "path": "MAP_System/tasks/TASK-270.json",
          "sha256": "a1754e431f5abbef421ed70ad7ca8adf64370387106b5f3c936330c0b15695a8",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": "jsonl_line:2373",
          "event_sha256": "12bd8bfd3f9eb7f68fda40ec2630793f566804750de576e370395add356fcc1a",
          "kind": "submission",
          "path": "MAP_System/events/events.jsonl",
          "sha256": "81d7da8cab43a92a91277f9796b055c8fe5e5d961e881b6c9a2ae938a335744a",
          "state": "available"
        },
        {
          "anchor": "jsonl_line:2381",
          "event_sha256": "e47febdefd3c1516303ad92a394cbf031c5fbf01ec41cdcb83400d9e474b5c83",
          "kind": "submission",
          "path": "MAP_System/events/events.jsonl",
          "sha256": "81d7da8cab43a92a91277f9796b055c8fe5e5d961e881b6c9a2ae938a335744a",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task270-rereview-lime.md",
          "sha256": "db3c1e5f4e7524c377aed55c946f6fa2f24d12680ba92cdf0c72e41230eebcfd",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task270-review-lime.md",
          "sha256": "32d04fa89cdf35fcb9055d4b02da7e8d0e94bb0a2b505e8fdc832f9825f7aca5",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/db/claims.py",
          "sha256": "95b4b18225a7262d5e69c72195ca717eced430ae43e9784b8a5646c9cddc23e4",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/notes/review-guide.md",
          "sha256": "87cc8f7c9bd44cfbc660a53e29ca754091276ccbb6210a6c48318fdbb9cb0e31",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_review_claims.py",
          "sha256": "76dea89461cf5b4ed32db8f4f3510491649bb76ee446912fa0b715dd00f23122",
          "source_type": "file",
          "state": "available"
        }
      ],
      "lifecycle": {
        "contradictory": false,
        "missing_sources": [],
        "released": true,
        "statuses": {
          "sqlite": "RELEASED",
          "task_graph": "RELEASED",
          "task_json": "RELEASED"
        }
      },
      "task_id": "TASK-270",
      "title": "claim_review must not report an unregistered reviewer as already-claimed"
    },
    {
      "backlinks": [
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "released_task",
          "path": "MAP_System/tasks/TASK-273.json",
          "sha256": "1955e5f22b43535292701063e5cc17ea85d854962eb331064205946b7ae44ee2",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": "jsonl_line:2510",
          "event_sha256": "acd47f1ed01bb8fc168d426619820e3eb4bcf5ddda9de095d819791a9818904a",
          "kind": "submission",
          "path": "MAP_System/events/events.jsonl",
          "sha256": "81d7da8cab43a92a91277f9796b055c8fe5e5d961e881b6c9a2ae938a335744a",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "review",
          "path": "MAP_System/artifacts/reviews/task273-review-deli.md",
          "sha256": "dbcaf4d9293042f2248e31c4cc3c2190960d189b738928ad74adccc95ae2009e",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/db/claims.py",
          "sha256": "95b4b18225a7262d5e69c72195ca717eced430ae43e9784b8a5646c9cddc23e4",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/map_task.py",
          "sha256": "43239c76f34922e7ca489892e26162b38cc217dbdea4020c70a8de3a77bd71ef",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/scripts/run_tests.sh",
          "sha256": "e95ebcd945b393d26e6ebe2bb318708a8ce6221308abc149c3626abe14ff546c",
          "source_type": "file",
          "state": "available"
        },
        {
          "anchor": null,
          "expected_sha256": null,
          "kind": "primary",
          "path": "MAP_System/tests/test_reassign_owner.py",
          "sha256": "0883c42756ed5a7dccde48841e71f357a3bb64a11b2632c7bd02f287aee5a0b4",
          "source_type": "file",
          "state": "available"
        }
      ],
      "lifecycle": {
        "contradictory": false,
        "missing_sources": [],
        "released": true,
        "statuses": {
          "sqlite": "RELEASED",
          "task_graph": "RELEASED",
          "task_json": "RELEASED"
        }
      },
      "task_id": "TASK-273",
      "title": "Add a sanctioned owner-reassignment verb for tasks whose owner agent no longer exists"
    }
  ],
  "withheld_claims": [],
  "workstream_id": "map-task-lifecycle-integrity"
}
```

## Frozen Evaluation

| Metric | Result |
|---|---:|
| required-fact retention | 100.00% |
| source traceability | 100.00% |
| stale/missing/contradiction detection | 100.00% |
| raw evidence tokens (estimate) | 442011 |
| digest tokens (estimate) | 1608 |
| context-token reduction | 99.64% |
| raw evidence bytes | 1433409 |
| digest bytes | 5650 |
| context-byte reduction | 99.61% |

The frozen evaluation fixes required fact IDs, lifecycle threshold, related
task IDs, and four evidence-health probes. Token counts are a deterministic
word/symbol-boundary estimate (`estimate_tokens`), not a specific model's
BPE tokenizer -- no tokenizer library is available in this project's venv,
and the metric name/report say "estimate" rather than overclaiming an exact
count. Byte counts are retained as an additional diagnostic. Raw evidence
bytes/tokens remain a point-in-time measurement because source files
continue to evolve.

## Refresh, Invalidation, Review, And Rollback

- Refresh by calling `build_digest(prior_manifest=extract_manifest(prior_digest))`
  (or the CLI's `--prior-report`) so a changed backlink hash is compared
  against the prior build and surfaced as `state: stale` in `evidence_issues`,
  withholding the affected claim rather than silently reporting it available.
  A plain rebuild with no prior manifest cannot detect staleness by itself --
  it only proves the *current* content is internally consistent.
- Refresh when any backlink hash or lifecycle status changes, a related task is
  released, or new submission/review/decision evidence appears.
- Invalidate when fewer than 5 related tasks remain
  three-way `RELEASED`, any lifecycle source contradicts another, a required
  backlink is missing/stale, or a claim anchor disappears.
- Require independent review of claims, links, evidence-health findings, and
  frozen metrics before any production proposal.
- Roll back by deleting or rebuilding this disposable report. No task state,
  decision, source evidence, startup context, runner route, or Command Center
  behavior depends on it.

## Decision

Retain as an offline experiment. Do not enable production routing or substitute
this digest for opening canonical evidence.
