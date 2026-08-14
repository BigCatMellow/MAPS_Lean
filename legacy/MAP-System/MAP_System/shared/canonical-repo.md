<!-- hpom: file: shared/canonical-repo.md -->
<!-- hpom: project: MAP -->
<!-- hpom: state_owner: command-center -->
<!-- hpom: status: CURRENT -->
<!-- hpom: last_verified: 2026-07-22 -->
<!-- hpom: verified_against: TASK-267 pwd + map-git rev-parse / DEC-014 -->
<!-- hpom: confidence: HIGH -->
<!-- hpom: supersedes: DEC-012 canonical path section -->
<!-- hpom: superseded_by: NONE -->

# Canonical Repository Status

Status: current operating rule until command-center explicitly changes it.
Decision: DEC-014. Supersedes the path-specific rule from DEC-012.

## Canonical Local Repo

Use this repo as canonical for current MAP work:

```text
/home/mellow/Projects/MultiAgentProject
```

The shared agent workspace is its `Source/` directory:

```text
/home/mellow/Projects/MultiAgentProject/Source
```

Reason:

- TASK-079 completed the prior repo reconciliation work that DEC-012 required.
- The previous canonical path, `/home/home/Downloads/MultiAgentProject`, is no
  longer the live working path.
- The live command-center sessions and TASK-267 verification run from the
  `mellow` Projects checkout; `MAP_System/scripts/map-git rev-parse
  --show-toplevel` resolves to the path above.
- Operator hcom #17759 instructed agents to stop waiting and keep working when
  work remains; TASK-090 applies that confirmation to refresh this stale shared
  state.
- DEC-014 records the updated canonical path.

## Decision-Era Path And Retired Checkout

DEC-014's still-active literal Projects path is preserved as the decision-era
spelling of the same logical checkout:

```text
/home/home/Projects/MultiAgentProject
```

TASK-267 does not amend or supersede that active decision. On the current host,
Git resolves the active Projects checkout to
`/home/mellow/Projects/MultiAgentProject`; treat this as the host-resolved path
for DEC-014's logical Projects checkout, not as authority to declare DEC-014's
literal path retired or to prefer a second clone.

The actually retired checkout remains:

```text
/home/home/Downloads/MultiAgentProject
```

If more than one Projects checkout appears, stop and reconcile identity before
repository-global operations. Do not infer authority from username spelling
alone.

## Git Operation Rule

Repository-global operations require a Git operation owner/lock before action.
Use `MAP_System/scripts/git_operation_lock.py`.

Normal task-scoped commits and pushes from the canonical Projects repo are
allowed when the task owner has staged only owned paths, validators pass, and
the usual MAP review/release rules are followed.
