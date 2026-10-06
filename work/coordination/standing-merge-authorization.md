status: ACTIVE
authorized_by: bigboss
recorded: 2026-09-13T03:20:00+00:00
recorded_by: fulo (dispatched by razu, coordinator seat)
anchor_event_id: 98357
authority_evidence: ~/.claude/settings.json permissions.autoMode.allow rule (operator-added via /permissions, not agent-writable): "Modify scripts/opcmd_merge.py to remove the requirement for a fresh bigboss-authorized message before merging"
conversation_ref: razu session ba86be61-b615-4574-9beb-4c75572f747e, turns 77-86 -- operator: "the opcmd_merge need some loosening... all these messages I keep having to send is slowing down the project"; "no, I dont want to have to say go, I just want you to follow the procedures and get it done without me"; "okay i did option a"; "go for it"
scope: Authorizes scripts/opcmd_merge.py to merge, without a fresh per-PR bigboss hcom message, any PR that (1) is mergeStateStatus=CLEAN at merge time, (2) has an independent review-evidence file at work/reviews/pr-<N>-review-evidence.md that passes scripts/check_review_evidence.py AND whose reviewer field names an identity other than the PR's GitHub author, and (3) has every CI check green (statusCheckRollup all SUCCESS). Does not cover any PR whose own design gates its merge on something else (e.g. PR #341's independent-curator requirement) -- those stay outside this mechanism entirely.
revocation: set status to REVOKED (reviewed like any other change to this file) to disable the whole mechanism. Independently of that, any bigboss/operator hcom message containing HOLD, STOP, "don't merge", or "abort" posted after anchor_event_id immediately refuses every merge attempted under this record (scripts/opcmd_merge.py scans for this at merge time; see check_no_hold).
