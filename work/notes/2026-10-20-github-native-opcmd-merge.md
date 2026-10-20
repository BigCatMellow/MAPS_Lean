# GitHub-native standing merge gate — candidate

- Record role: `DESIGN / SECURITY-SENSITIVE IMPLEMENTATION`
- Status: `CANDIDATE / INDEPENDENT REVIEW REQUIRED / NOT YET ACTIVE`
- Authority: existing standing authorization; no new merge permission; emergency HOLD controlled by human operator
- Parent: [OPCMD](../../scripts/opcmd_merge.py), [standing authorization](../coordination/standing-merge-authorization.md)

## Implementation and boundary

Routine standing mode no longer depends on hcom event availability. The **repository Actions variable** `MAPS_MERGE_HOLD` acts as a global emergency stop for BOTH legacy per-PR and standing modes. Only exact `OFF` permits further checks. Missing, denied, unrecognized or `HOLD` fails closed. Local `gh` reads the live variable; the trusted GitHub Actions workflow receives the `vars` context from GitHub.

Manual `workflow_dispatch` resolves the live PR SHA and checks out trusted merge code and verification policy from protected `main`, separately from the PR's immutable candidate SHA. The candidate is inspected as data and never supplies executed authorization code. The reviewed-head verifier supports an explicit candidate repository root. Current PR head must match the candidate tree before a final `--match-head-commit` merge. The standing path forbids `--admin` and deferred `--auto`. The existing ledger prints to the Actions log, with a final PR audit comment.

## Deployment / emergency stop

1. Independently review this security-sensitive change and verify CI. **Do not self-approve or merge this PR through direct GitHub merge.** The existing mandatory hcom-backed OPCMD merge route applies until this update itself is legitimately merged.
2. After accepted merge, set the GitHub repository Settings → Secrets and variables → Actions variable `MAPS_MERGE_HOLD=HOLD`. Switch to `OFF` explicitly to enable eligible merges; absent variable deliberately blocks.
3. In Actions, manually run `OPCMD merge (standing authorization)` with a PR number. Workflow uses its GitHub token with minimal PR/content/issue write permissions; branch protection and any PR-specific design gates remain in force.
4. Emergency stop: set `MAPS_MERGE_HOLD=HOLD` and **cancel any already-running merge workflow**. GitHub evaluates the variable into each workflow run, so a change is not a synchronous interrupt to a job already executing.
5. For local use authenticate `gh`, check out the exact PR head, and run the gate. Exceptional `--authz` remains supported but cannot bypass the GitHub HOLD.

## Independent reviewer targets / limits

- Verify `check_review_evidence.py` is executed from trusted checkout against candidate as data, with no candidate Python imported or executed.
- Check all fail-closed paths, no stale checkout, no review identity substitution, no `--admin`/auto under standing, no bypass of special PR-specific holds, no implicit scope expansion.
- Check `workflow_dispatch` token/variable permissions and `gh` behavior empirically after acceptance. This branch cannot exercise production dispatch before merge.
- Current GitHub variable is sampled when the job begins. Cancel in-progress jobs when HOLD changes. Repository settings access and current branch protection remain authority boundaries.
- Unit tests exercise normal and negative checks; GitHub CI and truly independent security review remain required. No test has approved a live merge.

Known standing-authority exclusion: `excluded_prs: 341` in the canonical authorization record. PR #341's benchmark-specific design gates cannot be satisfied by routine green CI; update exclusion only after a separately reviewed owner disposition. Standing mode allows only the inert `--delete-branch` passthrough, so user-supplied flags cannot override the expected head or GitHub protection.
