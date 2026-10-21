status: ACTIVE
authorized_by: bigboss
recorded: 2026-09-13T03:20:00+00:00
recorded_by: fulo (dispatched by razu, coordinator seat)
anchor_event_id: 98357
authority_evidence: ~/.claude/settings.json permissions.autoMode.allow rule (operator-added via /permissions, not agent-writable): "Modify scripts/opcmd_merge.py to remove the requirement for a fresh bigboss-authorized message before merging"
conversation_ref: razu session ba86be61-b615-4574-9beb-4c75572f747e, turns 77-86 -- operator: "the opcmd_merge need some loosening... all these messages I keep having to send is slowing down the project"; "no, I dont want to have to say go, I just want you to follow the procedures and get it done without me"; "okay i did option a"; "go for it"
scope: Authorizes scripts/opcmd_merge.py to attempt an immediate synchronous GitHub REST squash merge without a fresh per-PR hcom message only when the PR targets main, is non-draft and CLEAN, has exact-head independent review evidence and every CI check green, GitHub HOLD is OFF, and no special PR-specific gate remains. The REST merge must confirm success and fail rather than defer/queue; PR #341 and future explicit exclusions remain outside standing authority.
revocation: set status to REVOKED (reviewed like any other change to this file) to revoke standing authorization. Repository Actions variable MAPS_MERGE_HOLD=HOLD stops ALL merge modes; OFF permits otherwise eligible merges, and missing/unknown fails closed. A HOLD change applies to subsequent checks; cancel already-running workflow jobs. Legacy hcom HOLD scanning remains only for exceptional --authz calls; anchor_event_id is historical for standing mode.
github_native_route: .github/workflows/opcmd-merge.yml (manual dispatch, trusted main gate, exact SHA candidate, GitHub PR audit). Provision MAPS_MERGE_HOLD=OFF under repository Settings only after independent approval and merge of this implementation.
excluded_prs: 341
